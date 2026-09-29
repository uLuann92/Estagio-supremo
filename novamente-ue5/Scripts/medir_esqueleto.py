"""
medir_esqueleto.py - mede o esqueleto do personagem dentro da Unreal e compara com os corpos padrão.

Coloca o corpo (e a cabeça) numa cena vazia, lê a posição dos ossos na pose de referência e mede os segmentos
entre articulações: ombro a ombro, quadril a quadril, braço, antebraço, coxa, perna, altura do ombro e do quadril,
e a simetria entre esquerda e direita. Compara com Scripts/corpos_padrao.json na altura do personagem.

Rodar no editor (Tools > Execute Python Script) ou por linha de comando:
  set NOV_CORPO=/Game/MetaHumans/Luan/Body/m_srt_unw_body
  set NOV_CABECA=/Game/MetaHumans/Luan/Face/Luan_FaceMesh
  set NOV_PADRAO=garoto_13_14
  set NOV_ALTURA=158
  "%UE%\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe" "%PROJ%" -run=pythonscript -script="%CD%\\Scripts\\medir_esqueleto.py"

Nomes de osso: os do esqueleto do MetaHuman (upperarm_l, lowerarm_l, hand_l, thigh_l, calf_l, foot_l...).
Grava Saved/Review/esqueleto_<padrão>_<data-hora>.json e escreve a tabela no log.
"""

import datetime
import json
import os

import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
BODY = os.environ.get("NOV_CORPO", "")
HEAD = os.environ.get("NOV_CABECA", "")
STD = os.environ.get("NOV_PADRAO", "garoto_13_14")
HEIGHT = float(os.environ.get("NOV_ALTURA", "0") or 0)
MIRROR = [("upperarm_l", "lowerarm_l"), ("lowerarm_l", "hand_l"), ("thigh_l", "calf_l"), ("calf_l", "foot_l")]

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def log(msg):
    unreal.log("[Novamente] " + msg)


def spawn(path):
    mesh = unreal.load_asset(path)
    if mesh is None:
        raise RuntimeError("não achei o asset " + path)
    actor = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
    comp = actor.get_editor_property("skeletal_mesh_component")
    setter = getattr(comp, "set_skeletal_mesh_asset", None) or getattr(comp, "set_skeletal_mesh")
    setter(mesh)
    return actor, comp, mesh


def bounds_z(mesh):
    b = mesh.get_bounds()
    origin, ext = b.origin, b.box_extent
    return origin.z - ext.z, origin.z + ext.z


def dist(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2) ** 0.5


def main():
    if not BODY:
        unreal.log_error("[Novamente] defina NOV_CORPO com o caminho do corpo (ex.: /Game/MetaHumans/Luan/Body/...)")
        return
    with open(os.path.join(HERE, "corpos_padrao.json"), encoding="utf-8") as f:
        data = json.load(f)
    std = data["corpos"][STD]
    tol = data["tolerancia"]

    spawned = []
    try:
        actor, comp, mesh = spawn(BODY)
        spawned.append(actor)
        lo, hi = bounds_z(mesh)
        if HEAD:
            hactor, _, hmesh = spawn(HEAD)
            spawned.append(hactor)
            hlo, hhi = bounds_z(hmesh)
            lo, hi = min(lo, hlo), max(hi, hhi)
        height = hi - lo
        target_h = HEIGHT or std["altura"]
        k = target_h / std["altura"]

        def bone(name):
            if comp.get_bone_index(name) < 0:
                raise KeyError(name)
            return comp.get_socket_location(name)

        rows, ok_all = [], True
        err_h = abs(height - target_h) / target_h
        ok_h = err_h <= tol["altura"]
        ok_all &= ok_h
        rows.append({"medida": "altura", "alvo": round(target_h, 1), "medido": round(height, 1), "erro_pct": round(err_h * 100, 1), "passou": ok_h})
        for name, spec in std["medidas"].items():
            pair = spec.get("osso")
            if not pair:
                continue
            try:
                if len(pair) == 1:
                    got = bone(pair[0]).z - lo
                else:
                    got = dist(bone(pair[0]), bone(pair[1]))
            except KeyError as missing:
                rows.append({"medida": name, "alvo": round(spec["cm"] * k, 1), "medido": None, "erro_pct": None, "passou": False,
                             "nota": "osso %s não existe neste esqueleto" % missing})
                ok_all = False
                continue
            target = spec["cm"] * k
            err = abs(got - target) / target
            ok = err <= tol[spec["tipo"]]
            ok_all &= ok
            rows.append({"medida": name, "alvo": round(target, 1), "medido": round(got, 1), "erro_pct": round(err * 100, 1), "passou": ok})

        for a, b in MIRROR:
            try:
                left = dist(bone(a), bone(b))
                right = dist(bone(a[:-1] + "r"), bone(b[:-1] + "r"))
            except KeyError:
                continue
            diff = abs(left - right) / max(left, 1e-6)
            ok = diff <= 0.01
            ok_all &= ok
            rows.append({"medida": "simetria %s-%s" % (a[:-2], b[:-2]), "alvo": 0.0, "medido": round(diff * 100, 2), "erro_pct": round(diff * 100, 2), "passou": ok})

        try:
            tip = bone("middle_03_l")
            prev = bone("middle_02_l")
            tip = unreal.Vector(tip.x + (tip.x - prev.x) * 0.8, tip.y + (tip.y - prev.y) * 0.8, tip.z + (tip.z - prev.z) * 0.8)
            rows.append({"medida": "mao (aproximada)", "alvo": round(std["medidas"]["mao"]["cm"] * k, 1),
                         "medido": round(dist(bone("hand_l"), tip), 1), "erro_pct": None, "passou": True, "info": True,
                         "nota": "só informativo: a ponta do dedo não é osso; confira à mão"})
        except KeyError:
            pass
    finally:
        for a in spawned:
            eas.destroy_actor(a)

    log("ESQUELETO · %s · padrão %s · altura alvo %.1f cm" % (BODY, STD, target_h))
    for r in rows:
        got = "—" if r["medido"] is None else "%.1f" % r["medido"]
        err = "" if r.get("erro_pct") is None else "%.1f%%" % r["erro_pct"]
        log("  %-28s alvo %6.1f  medido %6s  %6s  %s %s" % (r["medida"], r["alvo"], got, err, "info" if r.get("info") else ("ok" if r["passou"] else "FORA"), r.get("nota", "")))
    log("== %s ==" % ("DENTRO DO PADRÃO" if ok_all else "FORA DO PADRÃO"))

    out_dir = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), "Review")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "esqueleto_%s_%s.json" % (STD, datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"corpo": BODY, "cabeca": HEAD, "padrao": STD, "altura_alvo": target_h, "linhas": rows, "passou": ok_all},
                  f, ensure_ascii=False, indent=2)
    log("resultado em " + path)


main()
