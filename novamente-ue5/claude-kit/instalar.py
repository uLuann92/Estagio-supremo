"""
instalar.py - instala o kit AAA+ do NOVAMENTE num projeto Unreal (a pasta do .uproject).

Uso:
  python novamente-ue5/claude-kit/instalar.py "C:/Projetos/Novamente"

Copia para o projeto:
  .claude/hooks/exigir_prova.py      gancho que não deixa a vez terminar sem prova visual aprovada
  .claude/agents/revisor-visual.md   o juiz que escreve o PARECER.md
  .claude/skills/revisao-aaa/        a rodada: fotos, medição, juiz
  .claude/rules/aaa-plus.md          as regras que ficam carregadas em toda sessão
  .claude/settings.json              o gancho, o esforço e as travas (junta com o que já existir)
  Scripts/capture_review.py, fidelidade.py, preparar_referencias.py
  Scripts/medidas_rosto.py, medir_corpo.py, medir_esqueleto.py, corpos_padrao.json, auditar_humanos.py
  Referencias/pares.json             só se ainda não existir
  Docs/PROMPT_AAA_PLUS.md, Docs/PROMPT_PERSONAGENS.md, Docs/PROMPT_HUMANOS.md, Docs/PROMPT_LUAN.md

No fim, sela as referências e os scripts de medida. Rode de novo sempre que atualizar o kit.
"""

import json
import os
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(KIT)


def copy(src, dst, overwrite=True):
    if os.path.exists(dst) and not overwrite:
        print("mantido  " + dst)
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print("copiado  " + dst)


def merge_settings(dst):
    with open(os.path.join(KIT, ".claude", "settings.json"), encoding="utf-8") as f:
        kit = json.load(f)
    cur = {}
    if os.path.exists(dst):
        with open(dst, encoding="utf-8") as f:
            cur = json.load(f)
    cur.setdefault("effortLevel", kit["effortLevel"])
    deny = cur.setdefault("permissions", {}).setdefault("deny", [])
    for rule in kit["permissions"]["deny"]:
        if rule not in deny:
            deny.append(rule)
    stops = cur.setdefault("hooks", {}).setdefault("Stop", [])
    ours = kit["hooks"]["Stop"][0]
    if not any("exigir_prova.py" in h.get("command", "") for group in stops for h in group.get("hooks", [])):
        stops.append(ours)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("ajustado " + dst)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = os.path.abspath(sys.argv[1])
    if not any(n.endswith(".uproject") for n in os.listdir(proj)):
        print("aviso: não achei .uproject em " + proj + " (continuando)")

    for sub in ("hooks/exigir_prova.py", "agents/revisor-visual.md", "skills/revisao-aaa/SKILL.md", "rules/aaa-plus.md"):
        copy(os.path.join(KIT, ".claude", sub), os.path.join(proj, ".claude", sub))
    merge_settings(os.path.join(proj, ".claude", "settings.json"))

    for name in ("capture_review.py", "fidelidade.py", "preparar_referencias.py",
                 "medidas_rosto.py", "medir_corpo.py", "medir_esqueleto.py", "corpos_padrao.json", "auditar_humanos.py"):
        copy(os.path.join(REPO, "Scripts", name), os.path.join(proj, "Scripts", name))
    copy(os.path.join(KIT, "Referencias", "pares.json"), os.path.join(proj, "Referencias", "pares.json"), overwrite=False)
    for doc in ("PROMPT_AAA_PLUS.md", "PROMPT_PERSONAGENS.md", "PROMPT_HUMANOS.md", "PROMPT_LUAN.md"):
        copy(os.path.join(REPO, "Docs", doc), os.path.join(proj, "Docs", doc))

    env = dict(os.environ, CLAUDE_PROJECT_DIR=proj)
    subprocess.call([sys.executable, os.path.join(proj, ".claude", "hooks", "exigir_prova.py"), "--selar"], env=env)

    refs = [n for n in os.listdir(os.path.join(proj, "Referencias")) if n.lower().endswith((".jpg", ".jpeg", ".png"))]
    print("\nPronto. Referências encontradas: %d." % len(refs))
    if len(refs) < 5:
        print("Coloque em Referencias/ as imagens do autor (veja o README do kit) e sele de novo:")
        print('  cd "%s" && python .claude/hooks/exigir_prova.py --selar' % proj)
    print("Depois: pip install mediapipe opencv-python numpy")


if __name__ == "__main__":
    main()
