"""
auditar_humanos.py - acha gente feita por código ou por primitiva no projeto, sem abrir a Unreal.

No NOVAMENTE, todo humano é MetaHuman (ou personagem profissional com o rig do MetaHuman). Este script
procura o que não pode existir:

1. Código que monta malha na mão (ProceduralMesh, DynamicMesh, Geometry Script de caixa e esfera,
   MeshDescription feita à mão) em arquivo que fala de gente (cabeça, rosto, cabelo, olho, braço,
   personagem, NPC...).
2. Asset de personagem (.uasset com movimento de personagem ou malha esquelética) que usa as formas
   básicas da engine (/Engine/BasicShapes: cubo, esfera, cilindro, cone, plano) ou malha procedural.
3. Asset de personagem que não referencia MetaHuman nenhum (aviso: pode vir da receita em tempo de jogo).

Exceção declarada: um arquivo de código com a linha "auditar_humanos: permitido (motivo)" não reprova, mas
aparece no relatório como EXCEÇÃO com o motivo. Só o autor aprova exceção (com ADR); efeito como os olhos da
Sombra no céu é exceção legítima, gente não é.

Uso:
  python Scripts/auditar_humanos.py                        (na pasta do .uproject)
  python Scripts/auditar_humanos.py C:/Projetos/Novamente --json Saved/Review/<data>/auditoria_humanos.json

Saída: lista de achados com arquivo, linha e motivo; código 0 (limpo) ou 1 (achou gente de primitiva).
"""

import argparse
import json
import os
import re
import sys

CODE_EXT = {".cpp", ".h", ".hpp", ".inl", ".py", ".cs"}
SKIP_DIRS = {"intermediate", "binaries", "saved", "deriveddatacache", ".git", ".vs", ".claude", "__pycache__", "node_modules"}
HEAD_BYTES = 4 * 1024 * 1024  # a tabela de nomes do .uasset fica no começo do arquivo

PROCEDURAL = re.compile(
    r"UProceduralMeshComponent|ProceduralMeshComponent|CreateMeshSection|UDynamicMeshComponent|DynamicMeshComponent"
    r"|FDynamicMesh3|AppendBox|AppendSphere|AppendCapsule|AppendCylinder|AppendCone|AppendSimpleSweptPolygon"
    r"|FMeshDescriptionBuilder|MeshDescriptionBuilder|BuildFromMeshDescriptions"
    r"|/Engine/BasicShapes/|BasicShapes\.(Cube|Sphere|Cylinder|Cone|Plane)")
HUMAN = re.compile(
    r"\b(humano|humanos|pessoa|pessoas|personagem|personagens|npc|npcs|rosto|cabeca|cabeça|cabelo|olho|olhos|nariz"
    r"|boca|orelha|orelhas|sobrancelha|torso|tronco|braco|braço|bracos|braços|perna|pernas|mao|mão|maos|mãos"
    r"|head|face|hair|eye|eyes|nose|mouth|ears?|arm|arms|leg|legs|hand|hands|torso|body|character|pawn)\b",
    re.IGNORECASE)
CHAR_MARKERS = (b"CharacterMovementComponent", b"SkeletalMeshComponent", b"MetaHumanCharacter")
PRIMITIVE_MARKERS = (b"/Engine/BasicShapes/", b"ProceduralMeshComponent", b"DynamicMeshComponent")
METAHUMAN_MARKERS = (b"/Game/MetaHumans/", b"MetaHumanCharacter", b"metahuman_base_skel", b"MetaHuman")


def walk(root, exts):
    for here, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS]
        for name in files:
            if os.path.splitext(name)[1].lower() in exts:
                yield os.path.join(here, name)


def audit_code(root):
    found = []
    for path in walk(root, CODE_EXT):
        if os.path.basename(path) == os.path.basename(__file__):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError:
            continue
        hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if PROCEDURAL.search(l)]
        if not hits:
            continue
        humans = sorted({m.group(0).lower() for l in lines for m in HUMAN.finditer(l)})
        if not humans:
            continue
        allowed = [l.split("auditar_humanos: permitido", 1)[1].strip(" :-()#/") for l in lines if "auditar_humanos: permitido" in l]
        found.append({
            "arquivo": os.path.relpath(path, root).replace("\\", "/"),
            "tipo": "codigo",
            "motivo": ("EXCEÇÃO declarada: %s" % (allowed[0] or "sem motivo escrito")) if allowed else
                      "monta malha por código num arquivo que fala de gente (%s)" % ", ".join(humans[:8]),
            "linhas": [{"linha": n, "texto": t[:160]} for n, t in hits[:10]],
            "grave": not allowed,
            "excecao": bool(allowed),
        })
    return found


def audit_assets(root):
    found, chars, with_mh = [], 0, 0
    content = os.path.join(root, "Content")
    if not os.path.isdir(content):
        return found, chars, with_mh
    for path in walk(content, {".uasset"}):
        try:
            with open(path, "rb") as f:
                head = f.read(HEAD_BYTES)
        except OSError:
            continue
        rel = os.path.relpath(path, root).replace("\\", "/")
        in_mh_folder = "/metahumans/" in ("/" + rel.lower())
        is_char = any(m in head for m in CHAR_MARKERS)
        if not is_char or in_mh_folder:
            continue
        chars += 1
        prims = [m.decode() for m in PRIMITIVE_MARKERS if m in head]
        shapes = sorted({s.decode() for s in re.findall(rb"/Engine/BasicShapes/(\w+)", head)})
        has_mh = any(m in head for m in METAHUMAN_MARKERS)
        with_mh += 1 if has_mh else 0
        if prims:
            found.append({"arquivo": rel, "tipo": "asset", "grave": True,
                          "motivo": "personagem usa %s%s" % (", ".join(prims), (" (" + ", ".join(shapes) + ")") if shapes else "")})
        elif not has_mh:
            found.append({"arquivo": rel, "tipo": "asset", "grave": False,
                          "motivo": "personagem sem referência a MetaHuman (confira se a receita aplica um em tempo de jogo)"})
    return found, chars, with_mh


def main():
    ap = argparse.ArgumentParser(description="Acha gente feita por código ou primitiva no projeto.")
    ap.add_argument("projeto", nargs="?", default=os.getcwd(), help="pasta do .uproject (padrão: a atual)")
    ap.add_argument("--json", help="salva o resultado em JSON")
    args = ap.parse_args()
    root = os.path.abspath(args.projeto)

    code = audit_code(root)
    assets, chars, with_mh = audit_assets(root)
    found = code + assets
    grave = [f for f in found if f["grave"]]

    print("AUDITORIA DE HUMANOS · %s" % root)
    print("  assets de personagem: %d · com referência a MetaHuman: %d" % (chars, with_mh))
    for f in found:
        tag = "PROIBIDO" if f["grave"] else ("EXCEÇÃO " if f.get("excecao") else "aviso   ")
        print("  %s %s: %s" % (tag, f["arquivo"], f["motivo"]))
        for l in f.get("linhas", [])[:5]:
            print("      linha %d: %s" % (l["linha"], l["texto"]))
    ok = not grave
    print("== %s ==" % ("LIMPO: nenhuma pessoa feita de primitiva ou de código" if ok else "REPROVADO: %d achado(s) proibido(s)" % len(grave)))
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"passou": ok, "personagens": chars, "com_metahuman": with_mh, "achados": found}, fh, ensure_ascii=False, indent=2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
