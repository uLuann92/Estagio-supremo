"""
build_largo.py - monta o blockout do Largo de São Sebastião (Manaus, 2017, noite de chuva) para a luta.

Escala real em centímetros. O centro do octógono fica na origem, a lona a 90 cm do chão.
O Teatro Amazonas fica no eixo -X, de frente para o octógono; a câmera de transmissão fica do lado +X
e vê a fachada rosa e a cúpula de azulejos atrás dos lutadores.

Tudo que este script cria recebe a tag NovBuild: rodar de novo apaga e recria só isso.
O que um artista colocar à mão no mapa fica.

Rodar depois de setup_novamente.py:
  Editor: Tools > Execute Python Script... > este arquivo
  Linha de comando:
    UnrealEditor-Cmd.exe "C:/caminho/Novamente.uproject" -run=pythonscript -script="C:/caminho/novamente-ue5/Scripts/build_largo.py"

O que é blockout (troque na fase de arte, ver Docs/ROADMAP):
  fachada, cúpula, igreja e monumento são caixas e esferas; a chuva é Niagara (não dá para gerar por script);
  o público entra com Mass Crowd ou MetaHumans; os postes são cilindros com a luz certa.
"""

import math
import os

import unreal

ROOT = "/Game/Novamente"
MAP = ROOT + "/Maps/L_Largo"
TAG = "NovBuild"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

CUBE = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
CYLINDER = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
SPHERE = unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
PLANE = unreal.load_asset("/Engine/BasicShapes/Plane.Plane")

RING_RADIUS = 460.0   # grade
MAT_HEIGHT = 90.0     # lona
THEATER_X = -3600.0   # fachada


def log(msg):
    unreal.log("[Novamente] " + msg)


def V(x, y, z):
    return unreal.Vector(x, y, z)


def R(pitch=0.0, yaw=0.0, roll=0.0):
    return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)


def load_or_create(path, cls, factory):
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    package, name = path.rsplit("/", 1)
    eal.make_directory(package)
    return asset_tools.create_asset(name, package, cls, factory)


# ---------------------------------------------------------------------------
# Materiais do blockout
# ---------------------------------------------------------------------------

def base_material():
    path = ROOT + "/Materials/M_Blockout"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    mat = load_or_create(path, unreal.Material, unreal.MaterialFactoryNew())
    color = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -500, -100)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(0.5, 0.5, 0.5, 1.0))
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -500, 100)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.6)
    metal = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -500, 200)
    metal.set_editor_property("parameter_name", "Metallic")
    metal.set_editor_property("default_value", 0.0)
    mel.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    return mat


def instance(name, color, roughness=0.6, metallic=0.0):
    path = ROOT + "/Materials/Blockout/MI_" + name
    mi = load_or_create(path, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, base_material())
    mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    mel.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    mel.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    eal.save_loaded_asset(mi)
    return mi


def custom_material(name, code, inputs, output_type, target, extra=None):
    """Material com um nó Custom. inputs: lista de (nome, fábrica_do_nó)."""
    path = ROOT + "/Materials/" + name
    mat = load_or_create(path, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    if extra:
        extra(mat)
    custom = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -300, 0)
    # Sem comentários: o compilador de shader quer ASCII puro.
    code = "\n".join(l for l in code.splitlines() if l.strip() and not l.strip().startswith("//"))
    custom.set_editor_property("code", code)
    custom.set_editor_property("output_type", output_type)
    pins = []
    for input_name, _ in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", input_name)
        pins.append(ci)
    custom.set_editor_property("inputs", pins)
    y = -200
    for input_name, make in inputs:
        node = make(mat, -700, y)
        mel.connect_material_expressions(node, "", custom, input_name)
        y += 120
    mel.connect_material_property(custom, "", target)
    return mat, custom


def node(cls, **props):
    def make(mat, x, y):
        n = mel.create_material_expression(mat, cls, x, y)
        for k, v in props.items():
            n.set_editor_property(k, v)
        return n
    return make


def constant(mat, prop, value, x=-300, y=300):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, x, y)
    n.set_editor_property("r", value)
    mel.connect_material_property(n, "", prop)


PAVEMENT_HLSL = """
// Pedra portuguesa do Largo: faixas pretas e brancas em ondas (o Encontro das Águas), pedras de ~7 cm, rejunte.
float2 p = WorldPos.xy;
float wave = sin((p.y + 260.0 * sin(p.x / 900.0) + 90.0 * sin(p.x / 310.0 + 1.3)) / 160.0 * 3.14159265);
float band = smoothstep(-0.04, 0.04, wave);
float2 cell = floor(p / 7.0);
float2 f = frac(p / 7.0);
float h = frac(sin(dot(cell, float2(127.1, 311.7))) * 43758.5453);
float grout = smoothstep(0.0, 0.09, min(min(f.x, f.y), min(1.0 - f.x, 1.0 - f.y)));
float3 black = float3(0.03, 0.03, 0.033) * (0.8 + 0.4 * h);
float3 white = float3(0.60, 0.58, 0.54) * (0.85 + 0.25 * h);
float3 col = lerp(black, white, band);
return lerp(float3(0.045, 0.04, 0.035), col, grout);
"""

DOME_HLSL = """
// Cúpula do Teatro Amazonas: azulejos verde, amarelo e azul em ziguezague, cerâmica com variação.
float3 d = normalize(WorldPos - ObjectPos);
float lon = atan2(d.y, d.x);
float lat = asin(clamp(d.z, -1.0, 1.0));
float2 uv = float2(lon * 36.0 / 6.2831853, lat * 18.0 / 1.5707963);
float zig = frac(uv.y * 0.5 + abs(frac(uv.x * 0.5) - 0.5));
float3 green = float3(0.02, 0.16, 0.05);
float3 yellow = float3(0.62, 0.42, 0.03);
float3 blue = float3(0.02, 0.05, 0.24);
float3 col = zig < 0.34 ? green : (zig < 0.67 ? yellow : blue);
float2 t = uv * 5.0;
float h = frac(sin(dot(floor(t), float2(12.9898, 78.233))) * 43758.5453);
float2 ft = frac(t);
float grout = smoothstep(0.0, 0.08, min(min(ft.x, ft.y), min(1.0 - ft.x, 1.0 - ft.y)));
col *= 0.78 + 0.44 * h;
return lerp(float3(0.5, 0.48, 0.44) * 0.3, col, grout);
"""

CHAINLINK_HLSL = """
// Grade do octógono: arame em losango.
float2 q = UV * Tiles;
float2 r = float2(q.x + q.y, q.x - q.y);
float2 e = min(frac(r), 1.0 - frac(r));
return 1.0 - smoothstep(0.035, 0.075, min(e.x, e.y));
"""


def make_materials():
    mats = {
        "pink": instance("TeatroRosa", (0.74, 0.34, 0.32), 0.55),
        "trim": instance("TeatroBranco", (0.78, 0.76, 0.70), 0.5),
        "church": instance("IgrejaCal", (0.66, 0.66, 0.63), 0.65),
        "dark": instance("Escuro", (0.025, 0.025, 0.03), 0.45),
        "canvas": instance("Lona", (0.52, 0.52, 0.49), 0.32),
        "iron": instance("FerroPreto", (0.02, 0.022, 0.02), 0.35, 1.0),
        "bronze": instance("Bronze", (0.32, 0.2, 0.09), 0.4, 1.0),
        "asphalt": instance("AsfaltoMolhado", (0.02, 0.02, 0.022), 0.15),
        "tree": instance("Mangueira", (0.02, 0.05, 0.02), 0.8),
    }

    WP = node(unreal.MaterialExpressionWorldPosition)
    pavement, _ = custom_material("M_PedraPortuguesa", PAVEMENT_HLSL, [("WorldPos", WP)],
                                  unreal.CustomMaterialOutputType.CMOT_FLOAT3, unreal.MaterialProperty.MP_BASE_COLOR,
                                  extra=lambda m: constant(m, unreal.MaterialProperty.MP_ROUGHNESS, 0.2))
    mel.recompile_material(pavement)
    eal.save_loaded_asset(pavement)
    mats["pavement"] = pavement

    dome, _ = custom_material("M_CupulaAzulejos", DOME_HLSL,
                              [("WorldPos", WP), ("ObjectPos", node(unreal.MaterialExpressionObjectPositionWS))],
                              unreal.CustomMaterialOutputType.CMOT_FLOAT3, unreal.MaterialProperty.MP_BASE_COLOR,
                              extra=lambda m: constant(m, unreal.MaterialProperty.MP_ROUGHNESS, 0.18))
    mel.recompile_material(dome)
    eal.save_loaded_asset(dome)
    mats["dome"] = dome

    def chain_extra(m):
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        m.set_editor_property("two_sided", True)
        n = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -300, -250)
        n.set_editor_property("constant", unreal.LinearColor(0.05, 0.05, 0.055, 1.0))
        mel.connect_material_property(n, "", unreal.MaterialProperty.MP_BASE_COLOR)
        constant(m, unreal.MaterialProperty.MP_METALLIC, 1.0, -300, 250)
        constant(m, unreal.MaterialProperty.MP_ROUGHNESS, 0.35, -300, 350)

    chain, _ = custom_material("M_Alambrado", CHAINLINK_HLSL,
                               [("UV", node(unreal.MaterialExpressionTextureCoordinate)),
                                ("Tiles", node(unreal.MaterialExpressionConstant2Vector, r=58.0, g=30.0))],
                               unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.MaterialProperty.MP_OPACITY_MASK,
                               extra=chain_extra)
    mel.recompile_material(chain)
    eal.save_loaded_asset(chain)
    mats["chain"] = chain

    eyes = ROOT + "/Materials/M_SombraEyes"
    mats["eyes"] = unreal.load_asset(eyes) if eal.does_asset_exist(eyes) else None
    return mats


# ---------------------------------------------------------------------------
# Atores
# ---------------------------------------------------------------------------

def tag(actor, folder, label, extra_tags=()):
    actor.set_actor_label(label)
    actor.set_folder_path(folder)
    actor.set_editor_property("tags", [unreal.Name(TAG)] + [unreal.Name(t) for t in extra_tags])
    return actor


def mesh(folder, label, static_mesh, material, location, scale, rotation=None, shadows=True):
    actor = eas.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation or R())
    comp = actor.static_mesh_component
    comp.set_static_mesh(static_mesh)
    if material:
        comp.set_material(0, material)
    comp.set_cast_shadow(shadows)
    actor.set_actor_scale3d(scale)
    return tag(actor, folder, label)


def box(folder, label, material, center, size, yaw=0.0):
    """Caixa pelo centro e tamanho em cm (o cubo da engine tem 100 cm e pivô no centro)."""
    return mesh(folder, label, CUBE, material, center, V(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0), R(yaw=yaw))


def cylinder(folder, label, material, base, diameter, height):
    return mesh(folder, label, CYLINDER, material, V(base.x, base.y, base.z + height / 2.0),
                V(diameter / 100.0, diameter / 100.0, height / 100.0))


def marker(label, location, tag_name):
    actor = eas.spawn_actor_from_class(unreal.TargetPoint, location, R())
    return tag(actor, "Novamente/Marcadores", label, [tag_name])


def light(cls, folder, label, location, rotation, intensity, color, radius=None, temperature=None, shadows=True, units=None):
    actor = eas.spawn_actor_from_class(cls, location, rotation)
    comp = actor.get_component_by_class(unreal.LightComponent)
    if units is not None:
        comp.set_editor_property("intensity_units", units)
    comp.set_intensity(intensity)
    comp.set_light_color(unreal.LinearColor(color[0], color[1], color[2], 1.0))
    if temperature:
        comp.set_editor_property("use_temperature", True)
        comp.set_editor_property("temperature", temperature)
    if radius:
        comp.set_editor_property("attenuation_radius", radius)
    comp.set_cast_shadows(shadows)
    return tag(actor, folder, label), comp


def clear_previous():
    removed = 0
    for actor in eas.get_all_level_actors():
        if unreal.Name(TAG) in actor.get_editor_property("tags"):
            eas.destroy_actor(actor)
            removed += 1
    if removed:
        log("removidos %d atores de um build anterior" % removed)


def open_or_create_map():
    if eal.does_asset_exist(MAP):
        les.load_level(MAP)
    else:
        les.new_level(MAP)
    log("mapa " + MAP)


# ---------------------------------------------------------------------------
# Largo
# ---------------------------------------------------------------------------

def build_octagon(m):
    f = "Novamente/Octogono"
    # Plataforma e lona.
    mesh(f, "Plataforma", CYLINDER, m["dark"], V(0, 0, MAT_HEIGHT / 2.0 - 1.0), V(10.6, 10.6, (MAT_HEIGHT - 2.0) / 100.0))
    mesh(f, "Lona", CYLINDER, m["canvas"], V(0, 0, MAT_HEIGHT - 1.0), V(9.3, 9.3, 0.02))
    # Grade: 8 painéis, 8 postes, almofadas no topo.
    side = 2.0 * RING_RADIUS * math.sin(math.pi / 8.0)
    apothem = RING_RADIUS * math.cos(math.pi / 8.0)
    for i in range(8):
        a = (i + 0.5) * math.pi / 4.0
        cx, cy = math.cos(a) * apothem, math.sin(a) * apothem
        yaw = math.degrees(a) + 90.0
        box(f, "Grade_%d" % i, m["chain"], V(cx, cy, MAT_HEIGHT + 95.0), (side, 3.0, 180.0), yaw)
        box(f, "Almofada_%d" % i, m["dark"], V(cx, cy, MAT_HEIGHT + 190.0), (side, 14.0, 12.0), yaw)
        pa = i * math.pi / 4.0
        cylinder(f, "Poste_%d" % i, m["iron"], V(math.cos(pa) * RING_RADIUS, math.sin(pa) * RING_RADIUS, MAT_HEIGHT), 12.0, 196.0)
    marker("NovRingCenter", V(0, 0, MAT_HEIGHT), "NovRingCenter")

    # Treliça com refletores (luz fria de evento, sombras fortes, como a capa).
    for i, a in enumerate([45, 135, 225, 315]):
        r = math.radians(a)
        pos = V(math.cos(r) * 620.0, math.sin(r) * 620.0, 950.0)
        look = unreal.MathLibrary.find_look_at_rotation(pos, V(0, 0, MAT_HEIGHT + 60.0))
        cylinder(f, "Torre_%d" % i, m["iron"], V(pos.x * 1.08, pos.y * 1.08, 0), 18.0, 980.0)
        actor, comp = light(unreal.SpotLight, f, "Refletor_%d" % i, pos, look, 30000.0, (1, 1, 1),
                            radius=2600.0, temperature=5600.0, units=unreal.LightUnits.CANDELAS)
        comp.set_editor_property("outer_cone_angle", 38.0)
        comp.set_editor_property("inner_cone_angle", 18.0)
        comp.set_editor_property("source_radius", 25.0)


def build_square(m):
    f = "Novamente/Largo"
    mesh(f, "PedraPortuguesa", PLANE, m["pavement"], V(-1400, 0, 0), V(110.0, 110.0, 1.0), shadows=False)
    mesh(f, "RuaAsfalto", PLANE, m["asphalt"], V(-1400, 0, -2), V(220.0, 220.0, 1.0), shadows=False)

    # Monumento à Abertura dos Portos (bronze sobre pedestal), de lado para não tapar a fachada.
    cylinder(f, "Monumento_Base", m["trim"], V(-1500, -2100, 0), 600.0, 180.0)
    cylinder(f, "Monumento_Coluna", m["bronze"], V(-1500, -2100, 180), 160.0, 900.0)
    mesh(f, "Monumento_Topo", SPHERE, m["bronze"], V(-1500, -2100, 1160), V(2.0, 2.0, 2.4))

    # Postes coloniais de ferro com luz de sódio (laranja), a luz de rua de Manaus.
    for i in range(12):
        a = math.radians(i * 30.0 + 15.0)
        x, y = -1400 + math.cos(a) * 3300.0, math.sin(a) * 3000.0
        cylinder(f, "Poste_%02d" % i, m["iron"], V(x, y, 0), 16.0, 420.0)
        light(unreal.PointLight, f, "Luz_%02d" % i, V(x, y, 440.0), R(), 900.0, (1.0, 0.62, 0.3),
              radius=1800.0, temperature=2100.0, shadows=(i % 3 == 0), units=unreal.LightUnits.CANDELAS)

    # Mangueiras e oitizeiros escuros na borda (a cidade é verde e úmida).
    for i in range(10):
        a = math.radians(i * 36.0)
        x, y = -1400 + math.cos(a) * 4300.0, math.sin(a) * 3900.0
        if x < THEATER_X + 600:
            continue
        cylinder(f, "Arvore_Tronco_%d" % i, m["dark"], V(x, y, 0), 60.0, 500.0)
        mesh(f, "Arvore_Copa_%d" % i, SPHERE, m["tree"], V(x, y, 850.0), V(9.0, 9.0, 7.0))


def build_theater(m):
    f = "Novamente/TeatroAmazonas"
    depth, width, height = 3000.0, 4400.0, 1500.0
    cx = THEATER_X - depth / 2.0
    box(f, "Corpo", m["pink"], V(cx, 0, height / 2.0), (depth, width, height))
    box(f, "Cornija", m["trim"], V(THEATER_X - 10, 0, height + 40.0), (60.0, width + 80.0, 80.0))
    # Pórtico com colunas, balcão e escadaria.
    box(f, "Portico", m["pink"], V(THEATER_X + 300.0, 0, 650.0), (600.0, 2400.0, 1300.0))
    box(f, "Balcao", m["trim"], V(THEATER_X + 620.0, 0, 620.0), (80.0, 2500.0, 40.0))
    # Escadaria: degraus empilhados, o mais baixo avança mais na praça.
    for k in range(6):
        depth, rise = (6 - k) * 45.0, (k + 1) * 24.0
        box(f, "Degrau_%d" % k, m["trim"], V(THEATER_X + 600.0 + depth / 2.0, 0, rise / 2.0), (depth, 3000.0 - k * 60.0, rise))
    for i in range(8):
        y = -1050.0 + i * 300.0
        cylinder(f, "Coluna_%d" % i, m["trim"], V(THEATER_X + 640.0, y, 144.0), 90.0, 1056.0)
    # Cúpula de azulejos sobre o tambor.
    dome_center = V(cx - 400.0, 0, height + 700.0)
    cylinder(f, "Tambor", m["trim"], V(dome_center.x, 0, height), 1500.0, 500.0)
    mesh(f, "Cupula", SPHERE, m["dome"], dome_center, V(15.0, 15.0, 13.0))
    cylinder(f, "Lanterna", m["trim"], V(dome_center.x, 0, dome_center.z + 620.0), 180.0, 360.0)
    marker("NovDomeFocus", dome_center, "NovDomeFocus")
    # Luz de fachada quente vinda de baixo (a fachada rosa acesa à noite).
    for i, y in enumerate([-1600.0, 0.0, 1600.0]):
        pos = V(THEATER_X + 1400.0, y, 60.0)
        look = unreal.MathLibrary.find_look_at_rotation(pos, V(THEATER_X, y * 0.8, 900.0))
        actor, comp = light(unreal.SpotLight, f, "Fachada_%d" % i, pos, look, 60000.0, (1.0, 0.8, 0.6),
                            radius=4000.0, temperature=3000.0, shadows=True, units=unreal.LightUnits.CANDELAS)
        comp.set_editor_property("outer_cone_angle", 30.0)


def build_church(m):
    f = "Novamente/IgrejaSaoSebastiao"
    box(f, "Nave", m["church"], V(-900, 3600, 600), (2600, 1400, 1200), 90.0)
    box(f, "Torre", m["church"], V(400, 3600, 1300), (500, 500, 2600))
    mesh(f, "Pinaculo", SPHERE, m["trim"], V(400, 3600, 2700), V(2.5, 2.5, 3.5))


def build_atmosphere(m):
    f = "Novamente/Atmosfera"
    # Lua fraca e fria atrás das nuvens.
    actor, moon = light(unreal.DirectionalLight, f, "Lua", V(0, 0, 3000), R(pitch=-38.0, yaw=35.0), 0.35,
                        (0.55, 0.66, 1.0), shadows=True)
    # Céu: captura em tempo real, horizonte escuro e úmido.
    sky = eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 500), R())
    comp = sky.get_component_by_class(unreal.SkyLightComponent)
    comp.set_editor_property("real_time_capture", True)
    comp.set_editor_property("lower_hemisphere_is_black", True)
    comp.set_intensity(0.6)
    tag(sky, f, "Ceu")
    atmo = eas.spawn_actor_from_class(unreal.SkyAtmosphere, V(0, 0, 0), R())
    tag(atmo, f, "Atmosfera")
    # Neblina volumétrica: a chuva segura a luz dos refletores e dos postes.
    fog = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, V(0, 0, 0), R())
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    fc.set_editor_property("fog_density", 0.035)
    fc.set_editor_property("fog_height_falloff", 0.12)
    for name in ("fog_inscattering_luminance", "fog_inscattering_color"):
        try:
            fc.set_editor_property(name, unreal.LinearColor(0.012, 0.018, 0.035, 1.0))
            break
        except Exception:
            pass
    fc.set_editor_property("volumetric_fog", True)
    fc.set_editor_property("volumetric_fog_scattering_distribution", 0.35)
    fc.set_editor_property("volumetric_fog_extinction_scale", 1.4)
    tag(fog, f, "NeblinaChuva")

    # Olhos da Sombra no céu, atrás do teatro (o material lê SombraEyes da coleção).
    # auditar_humanos: permitido (olhos da Sombra no céu: efeito num plano, não é pessoa; formas básicas só no blockout do cenário)
    if m.get("eyes"):
        mesh(f, "OlhosDaSombra", PLANE, m["eyes"], V(THEATER_X - 9000.0, 0, 4600.0), V(78.0, 24.0, 1.0),
             R(yaw=90.0, roll=90.0), shadows=False)

    # Pós-processamento global.
    pp_actor = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 0), R())
    pp_actor.set_editor_property("unbound", True)
    s = pp_actor.get_editor_property("settings")

    def setp(name, value):
        try:
            s.set_editor_property("override_" + name, True)
            s.set_editor_property(name, value)
        except Exception as e:  # nomes mudam entre versões da engine
            unreal.log_warning("[Novamente] pós-processamento: %s não aplicado (%s)" % (name, e))

    setp("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
    setp("auto_exposure_min_brightness", -2.0)
    setp("auto_exposure_max_brightness", 4.0)
    setp("auto_exposure_bias", 0.3)
    setp("bloom_intensity", 0.6)
    setp("motion_blur_amount", 0.35)
    setp("vignette_intensity", 0.0)          # a vinheta é do M_PP_Novamente
    setp("scene_fringe_intensity", 0.0)      # a aberração também
    setp("film_grain_intensity", 0.0)
    setp("color_saturation", unreal.Vector4(0.92, 0.94, 1.0, 1.0))
    setp("color_gamma_shadows", unreal.Vector4(0.96, 1.0, 1.06, 1.0))     # sombras frias
    setp("color_gain_highlights", unreal.Vector4(1.06, 1.0, 0.94, 1.0))   # luzes quentes
    setp("lumen_final_gather_quality", 2.0)
    setp("lumen_scene_lighting_quality", 2.0)
    pp_mat = ROOT + "/Materials/M_PP_Novamente"
    if eal.does_asset_exist(pp_mat):
        blend = unreal.WeightedBlendable()
        blend.set_editor_property("weight", 1.0)
        blend.set_editor_property("object", unreal.load_asset(pp_mat))
        blendables = unreal.WeightedBlendables()
        blendables.set_editor_property("array", [blend])
        s.set_editor_property("weighted_blendables", blendables)
    pp_actor.set_editor_property("settings", s)
    tag(pp_actor, f, "PosProcesso")


def build_gameplay():
    f = "Novamente/Luta"
    cam = eas.spawn_actor_from_class(unreal.NovFightCamera, V(800, 0, 250), R())
    tag(cam, f, "CameraTransmissao")
    world = ues.get_editor_world()
    try:
        settings = world.get_world_settings()
    except Exception:
        settings = unreal.GameplayStatics.get_actor_of_class(world, unreal.WorldSettings)
    settings.set_editor_property("default_game_mode", unreal.NovFightGameMode.static_class())
    log("GameMode do mapa: NovFightGameMode")


def main():
    open_or_create_map()
    clear_previous()
    m = make_materials()
    build_octagon(m)
    build_square(m)
    build_theater(m)
    build_church(m)
    build_atmosphere(m)
    build_gameplay()
    les.save_current_level()
    log("Largo montado e salvo. Aperte Play. Depois rode Scripts/capture_review.py para as fotos de revisão.")


main()
