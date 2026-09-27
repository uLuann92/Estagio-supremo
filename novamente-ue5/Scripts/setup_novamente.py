"""
setup_novamente.py - prepara o projeto Unreal para o plugin NovamenteCombat.

Cria (ou atualiza, sem apagar o que já existe):
  /Game/Novamente/Materials/MPC_Novamente     parâmetros de tela da Sombra e das Leis
  /Game/Novamente/Materials/M_PP_Novamente    pós-processamento (código em Shaders/PP_Novamente_Custom.hlsl)
  /Game/Novamente/Materials/M_SombraEyes      olhos da Sombra no céu (Shaders/M_SombraEyes_Custom.hlsl)
  /Game/Novamente/Materials/MF_NovamenteFerimentos  hematomas e corte no rosto (Shaders/Bruises_Custom.hlsl)
  /Game/Novamente/Audio/SM_Muffle             1ª Lei: mundo abafado depois de golpe forte
e ajusta Config/*.ini (Enhanced Input, Lumen, sombras virtuais, TSR, cache de PSO).

Como rodar:
  Editor: Tools > Execute Python Script... > este arquivo
  Linha de comando:
    UnrealEditor-Cmd.exe "C:/caminho/Novamente.uproject" -run=pythonscript -script="C:/caminho/novamente-ue5/Scripts/setup_novamente.py"

Pode rodar quantas vezes quiser.
"""

import os
import re

import unreal

ROOT = "/Game/Novamente"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

MPC_SCALARS = {
    "Sombra": 0.0,
    "SombraPresence": 0.0,
    "SombraEyes": 0.0,
    "Tunnel": 0.0,
    "Pulse": 0.0,
    "Flash": 0.0,
    "Desat": 0.0,
    "Caos": 0.0,
    "Chroma": 0.0015,
    "Lightning": 0.0,
    "Crowd": 0.0,
}
MPC_VECTORS = {
    "SombraColor": unreal.LinearColor(0.47, 1.0, 0.03, 1.0),
}

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary


def log(msg):
    unreal.log("[Novamente] " + msg)


def warn(msg):
    unreal.log_warning("[Novamente] " + msg)


def load_or_create(path, cls, factory):
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    package, name = path.rsplit("/", 1)
    eal.make_directory(package)
    asset = asset_tools.create_asset(name, package, cls, factory)
    log("criado " + path)
    return asset


def read_hlsl(relative):
    """Lê o HLSL do repositório e tira os comentários (o compilador de shader quer ASCII puro)."""
    with open(os.path.join(REPO, relative), "r", encoding="utf-8-sig") as f:
        code = f.read()
    code = re.sub(r"//[^\n]*", "", code)
    code = "\n".join(line.rstrip() for line in code.splitlines() if line.strip())
    bad = [c for c in code if ord(c) > 127]
    if bad:
        raise ValueError("%s tem caracteres fora do ASCII no código: %r" % (relative, "".join(sorted(set(bad)))))
    return code


# ---------------------------------------------------------------------------
# Material Parameter Collection
# ---------------------------------------------------------------------------

def setup_mpc():
    mpc = load_or_create(ROOT + "/Materials/MPC_Novamente", unreal.MaterialParameterCollection,
                         unreal.MaterialParameterCollectionFactoryNew())
    scalars = list(mpc.get_editor_property("scalar_parameters"))
    vectors = list(mpc.get_editor_property("vector_parameters"))
    have_s = {str(p.get_editor_property("parameter_name")) for p in scalars}
    have_v = {str(p.get_editor_property("parameter_name")) for p in vectors}

    # Só acrescenta o que falta: reescrever mudaria os IDs e quebraria materiais que já usam a coleção.
    for name, value in MPC_SCALARS.items():
        if name not in have_s:
            p = unreal.CollectionScalarParameter()
            p.set_editor_property("parameter_name", name)
            p.set_editor_property("default_value", value)
            scalars.append(p)
            log("MPC: +" + name)
    for name, value in MPC_VECTORS.items():
        if name not in have_v:
            p = unreal.CollectionVectorParameter()
            p.set_editor_property("parameter_name", name)
            p.set_editor_property("default_value", value)
            vectors.append(p)
            log("MPC: +" + name)

    mpc.set_editor_property("scalar_parameters", scalars)
    mpc.set_editor_property("vector_parameters", vectors)
    eal.save_loaded_asset(mpc)
    return mpc


# ---------------------------------------------------------------------------
# Materiais com nó Custom
# ---------------------------------------------------------------------------

def make_custom(material, code, input_names, x=-300, y=0):
    custom = mel.create_material_expression(material, unreal.MaterialExpressionCustom, x, y)
    custom.set_editor_property("code", code)
    custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    custom.set_editor_property("description", "Novamente")
    inputs = []
    for name in input_names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", name)
        inputs.append(ci)
    custom.set_editor_property("inputs", inputs)
    return custom


def collection_param(material, mpc, name, x, y, rgb=False):
    node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, x, y)
    node.set_editor_property("collection", mpc)
    node.set_editor_property("parameter_name", name)
    if not rgb:
        return node
    mask = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, x + 180, y)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", True)
    mask.set_editor_property("a", False)
    mel.connect_material_expressions(node, "", mask, "")
    return mask


def scalar_param(material, name, value, x, y):
    node = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, x, y)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", value)
    return node


def setup_post_process(mpc):
    path = ROOT + "/Materials/M_PP_Novamente"
    mat = load_or_create(path, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    mat.set_editor_property("blendable_location", unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
    mel.delete_all_material_expressions(mat)

    names = ["SceneColor", "Time", "ViewSize", "Sombra", "SombraPresence", "SombraColor", "Tunnel", "Pulse",
             "Flash", "Desat", "Caos", "Chroma", "Grain", "Vignette"]
    custom = make_custom(mat, read_hlsl("Shaders/PP_Novamente_Custom.hlsl"), names)

    y = -700
    scene = mel.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, -800, y)
    scene.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
    mel.connect_material_expressions(scene, "Color", custom, "SceneColor")
    y += 110
    mel.connect_material_expressions(mel.create_material_expression(mat, unreal.MaterialExpressionTime, -800, y), "", custom, "Time")
    y += 80
    mel.connect_material_expressions(mel.create_material_expression(mat, unreal.MaterialExpressionViewSize, -800, y), "", custom, "ViewSize")
    for name in ["Sombra", "SombraPresence", "SombraColor", "Tunnel", "Pulse", "Flash", "Desat", "Caos", "Chroma"]:
        y += 80
        node = collection_param(mat, mpc, name, -1000, y, rgb=(name == "SombraColor"))
        mel.connect_material_expressions(node, "", custom, name)
    y += 80
    mel.connect_material_expressions(scalar_param(mat, "Grain", 0.045, -800, y), "", custom, "Grain")
    y += 80
    mel.connect_material_expressions(scalar_param(mat, "Vignette", 0.42, -800, y), "", custom, "Vignette")

    mel.connect_material_property(custom, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    log("pós-processamento pronto: " + path)
    return mat


def setup_eyes(mpc):
    path = ROOT + "/Materials/M_SombraEyes"
    mat = load_or_create(path, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property("two_sided", True)
    try:
        mat.set_editor_property("use_emissive_for_dynamic_area_lighting", False)
    except Exception:
        pass
    mel.delete_all_material_expressions(mat)
    custom = make_custom(mat, read_hlsl("Shaders/M_SombraEyes_Custom.hlsl"), ["UV", "Time", "Eyes"])
    mel.connect_material_expressions(mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -700, -100), "", custom, "UV")
    mel.connect_material_expressions(mel.create_material_expression(mat, unreal.MaterialExpressionTime, -700, 0), "", custom, "Time")
    mel.connect_material_expressions(collection_param(mat, mpc, "SombraEyes", -900, 100), "", custom, "Eyes")
    mel.connect_material_property(custom, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    log("olhos da Sombra prontos: " + path)
    return mat


def setup_wounds_function():
    """MF_NovamenteFerimentos: hematomas e corte lidos dos parâmetros que o NovFighterCharacter escreve no rosto."""
    path = ROOT + "/Materials/MF_NovamenteFerimentos"
    func = load_or_create(path, unreal.MaterialFunction, unreal.MaterialFunctionFactoryNew())
    mel.delete_all_material_expressions_in_function(func)
    make = lambda cls, x, y: mel.create_material_expression_in_function(func, cls, x, y)

    uv_in = make(unreal.MaterialExpressionFunctionInput, -1200, -600)
    uv_in.set_editor_property("input_name", "UV")
    uv_in.set_editor_property("input_type", unreal.FunctionInputType.FUNCTION_INPUT_VECTOR2)

    names = ["UV"] + ["B%d" % i for i in range(8)] + ["A%d" % i for i in range(8)] + ["Cut"]
    custom = make(unreal.MaterialExpressionCustom, -300, 0)
    custom.set_editor_property("code", read_hlsl("Shaders/Bruises_Custom.hlsl"))
    custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    pins = []
    for name in names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", name)
        pins.append(ci)
    custom.set_editor_property("inputs", pins)
    mel.connect_material_expressions(uv_in, "", custom, "UV")

    y = -500
    for i in range(8):
        b = make(unreal.MaterialExpressionVectorParameter, -900, y)
        b.set_editor_property("parameter_name", "Bruise%d" % i)
        b.set_editor_property("default_value", unreal.LinearColor(0, 0, 0, 0))
        # Precisa dos 4 canais (u, v, raio, intensidade): saída RGBA; sem ela, junta RGB + A.
        if not mel.connect_material_expressions(b, "RGBA", custom, "B%d" % i):
            joined = make(unreal.MaterialExpressionAppendVector, -800, y)
            mel.connect_material_expressions(b, "", joined, "A")
            mel.connect_material_expressions(b, "A", joined, "B")
            mel.connect_material_expressions(joined, "", custom, "B%d" % i)
        a = make(unreal.MaterialExpressionScalarParameter, -700, y)
        a.set_editor_property("parameter_name", "BruiseAge%d" % i)
        mel.connect_material_expressions(a, "", custom, "A%d" % i)
        y += 110
    cut = make(unreal.MaterialExpressionScalarParameter, -700, y)
    cut.set_editor_property("parameter_name", "Cut")
    mel.connect_material_expressions(cut, "", custom, "Cut")

    out = make(unreal.MaterialExpressionFunctionOutput, 100, 0)
    out.set_editor_property("output_name", "Hematomas")
    mel.connect_material_expressions(custom, "", out, "")
    sweat = make(unreal.MaterialExpressionScalarParameter, -300, 300)
    sweat.set_editor_property("parameter_name", "Sweat")
    sweat_out = make(unreal.MaterialExpressionFunctionOutput, 100, 300)
    sweat_out.set_editor_property("output_name", "Suor")
    mel.connect_material_expressions(sweat, "", sweat_out, "")

    mel.update_material_function(func)
    eal.save_loaded_asset(func)
    log("função de ferimentos pronta: " + path)


# ---------------------------------------------------------------------------
# Som
# ---------------------------------------------------------------------------

def setup_muffle():
    path = ROOT + "/Audio/SM_Muffle"
    try:
        mix = load_or_create(path, unreal.SoundMix, unreal.SoundMixFactory())
        master = unreal.load_asset("/Engine/EngineSounds/Master")
        adjuster = unreal.SoundClassAdjuster()
        adjuster.set_editor_property("sound_class_object", master)
        adjuster.set_editor_property("volume_adjuster", 0.75)
        adjuster.set_editor_property("low_pass_filter_frequency", 900.0)
        adjuster.set_editor_property("apply_to_children", True)
        mix.set_editor_property("sound_class_effects", [adjuster])
        mix.set_editor_property("fade_in_time", 0.08)
        mix.set_editor_property("fade_out_time", 1.2)
        eal.save_loaded_asset(mix)
        return path + "." + path.rsplit("/", 1)[1]
    except Exception as e:  # nomes de propriedade mudam entre versões
        warn("não consegui montar SM_Muffle automaticamente (%s). Crie à mão: Sound Mix com filtro passa-baixa ~900 Hz na classe Master." % e)
        return None


# ---------------------------------------------------------------------------
# Config/*.ini
# ---------------------------------------------------------------------------

def config_path(name):
    return os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_config_dir()), name)


def set_ini(file_name, section, values):
    """Define chaves numa seção do .ini sem mexer no resto do arquivo."""
    path = config_path(file_name)
    text = open(path, "r", encoding="utf-8").read() if os.path.exists(path) else ""
    header = "[" + section + "]"
    changed = []
    if header not in text:
        text = (text.rstrip("\n") + "\n\n" if text.strip() else "") + header + "\n"
    start = text.index(header) + len(header)
    nxt = text.find("\n[", start)
    end = len(text) if nxt < 0 else nxt
    body = text[start:end]
    for key, value in values.items():
        line = "%s=%s" % (key, value)
        pattern = re.compile(r"^" + re.escape(key) + r"=.*$", re.M)
        if pattern.search(body):
            new_body = pattern.sub(line, body)
            if new_body != body:
                changed.append(line)
            body = new_body
        else:
            body = body.rstrip("\n") + "\n" + line + "\n"
            changed.append(line)
    text = text[:start] + body + text[end:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    for line in changed:
        log("%s [%s] %s" % (file_name, section, line))


def setup_config(muffle_path):
    set_ini("DefaultInput.ini", "/Script/Engine.InputSettings", {
        "DefaultPlayerInputClass": "/Script/EnhancedInput.EnhancedPlayerInput",
        "DefaultInputComponentClass": "/Script/EnhancedInput.EnhancedInputComponent",
    })
    set_ini("DefaultEngine.ini", "/Script/Engine.RendererSettings", {
        "r.DynamicGlobalIlluminationMethod": "1",   # Lumen
        "r.ReflectionMethod": "1",                  # Lumen
        "r.Shadow.Virtual.Enable": "1",             # sombras virtuais
        "r.GenerateMeshDistanceFields": "True",
        "r.AntiAliasingMethod": "4",                # TSR
        "r.SkinCache.CompileShaders": "True",       # MetaHuman exige
        "r.Nanite.ProjectEnabled": "True",
        "r.CustomDepth": "3",
    })
    set_ini("DefaultEngine.ini", "SystemSettings", {
        "r.PSOPrecaching": "1",                     # evita travadas na primeira vez que um efeito aparece
        "r.ShaderPipelineCache.Enabled": "1",
    })
    settings = {"ScreenParameters": ROOT + "/Materials/MPC_Novamente.MPC_Novamente"}
    if muffle_path:
        settings["MuffleMix"] = muffle_path
    set_ini("DefaultGame.ini", "/Script/NovamenteCombat.NovamenteSettings", settings)


def main():
    for folder in ["Materials", "Audio", "Maps", "Characters", "Animations", "FX", "UI"]:
        eal.make_directory(ROOT + "/" + folder)
    mpc = setup_mpc()
    setup_post_process(mpc)
    setup_eyes(mpc)
    setup_wounds_function()
    muffle = setup_muffle()
    setup_config(muffle)
    log("pronto. Reinicie o editor para as mudanças de Config valerem. Depois rode Scripts/build_largo.py.")


main()
