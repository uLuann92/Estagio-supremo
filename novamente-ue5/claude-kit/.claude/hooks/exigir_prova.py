"""
exigir_prova.py - gancho "Stop" do Claude Code para o NOVAMENTE.

Depois de mexer em qualquer coisa que muda a imagem (asset, mapa, material, shader, código, config),
o Claude não consegue encerrar a vez sem uma rodada de revisão nova e aprovada:
  - Saved/Review/<data-hora>/ mais nova que a última mudança, com fotos das câmeras Rev_* na
    qualidade 4 e numa qualidade menor (Scripts/capture_review.py);
  - fidelidade.json na mesma pasta (Scripts/fidelidade.py), quando existe Referencias/pares.json;
  - PARECER.md do subagente revisor-visual com a linha "VEREDITO: APROVADO".
Se o parecer reprovou, o gancho devolve os defeitos e o Claude continua corrigindo.

Duas saídas honestas, que o autor lê na resposta:
  "PENDENTE:"          o que falta e de quem depende (download, aprovação do autor, máquina);
  "SEM EFEITO VISUAL:" a mudança não altera a imagem, e por quê.

Também confere o selo das referências e do juiz (fidelidade.py). Se um deles mudou, bloqueia.
Só o autor sela de novo, depois de trocar uma referência de propósito:
  python .claude/hooks/exigir_prova.py --selar

Para o Claude ver o que falta antes de tentar encerrar:
  python .claude/hooks/exigir_prova.py --checar

Variáveis: NOV_MAX_BLOQUEIOS (padrão 8) limita os bloqueios seguidos numa mesma vez.
"""

import datetime
import glob
import hashlib
import json
import os
import re
import sys
import tempfile
import time

# Script Python do editor só muda a imagem quando roda, e aí mexe em .uasset/.umap, que já contam.
VISUAL_EXT = {".uasset", ".umap", ".hlsl", ".usf", ".ush", ".cpp", ".h", ".ini"}
SKIP_DIRS = {"saved", "intermediate", "binaries", "deriveddatacache", ".git", ".vs", ".vscode", ".idea",
             ".claude", "node_modules", "__pycache__", "referencias", "modelos"}
ESCAPES = ("PENDENTE:", "SEM EFEITO VISUAL:")
MAX_BLOCKS = int(os.environ.get("NOV_MAX_BLOQUEIOS", "8"))
SEAL_NAME = "selo.json"
VERDICT = re.compile(r"VEREDITO:\s*\**\s*(APROVADO|REPROVADO)", re.IGNORECASE)


def project_dir(data):
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def session_start(data):
    """Primeiro horário gravado na conversa; sem ele, a criação do arquivo da conversa."""
    path = data.get("transcript_path") or ""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    stamp = json.loads(line).get("timestamp")
                except ValueError:
                    continue
                if stamp:
                    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
    except (OSError, ValueError):
        pass
    try:
        return os.path.getctime(path)
    except OSError:
        return time.time() - 6 * 3600


def newest_change(root):
    """(mtime, caminho) da mudança visual mais nova no projeto, ou (0, None)."""
    best = (0.0, None)
    for here, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS]
        rel_here = os.path.relpath(here, root).replace("\\", "/")
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext not in VISUAL_EXT:
                continue
            if ext == ".ini" and not rel_here.lower().startswith("config"):
                continue
            path = os.path.join(here, name)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            if mtime > best[0]:
                best = (mtime, path)
    return best


def latest_review(root):
    dirs = [d for d in glob.glob(os.path.join(root, "Saved", "Review", "*")) if os.path.isdir(d)]
    return max(dirs, key=os.path.basename) if dirs else None


def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sealed_files(root):
    files = [os.path.join(root, "Scripts", "fidelidade.py")]
    ref = os.path.join(root, "Referencias")
    if os.path.isdir(ref):
        for name in sorted(os.listdir(ref)):
            path = os.path.join(ref, name)
            if os.path.isfile(path):
                files.append(path)
    return [f for f in files if os.path.isfile(f)]


def seal(root):
    out = {os.path.relpath(p, root).replace("\\", "/"): sha256(p) for p in sealed_files(root)}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SEAL_NAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    for name in out:
        print("selado: " + name)
    print("selo gravado em " + path)


def seal_problems(root):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SEAL_NAME)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        sealed = json.load(f)
    bad = []
    for name, digest in sealed.items():
        full = os.path.join(root, name)
        if not os.path.isfile(full):
            bad.append(name + " sumiu")
        elif sha256(full) != digest:
            bad.append(name + " foi alterado")
    if not bad:
        return []
    return ["As referências e o juiz são do autor e estão selados: " + "; ".join(bad) + ". "
            "Desfaça a alteração (git checkout ou cópia original). Se foi o autor que trocou de propósito, "
            "peça para ele rodar: python .claude/hooks/exigir_prova.py --selar"]


def parecer_excerpt(text, limit=25):
    """As linhas de defeitos do parecer, para voltarem ao Claude junto com o bloqueio."""
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if re.match(r"#+\s*(o que )?corrigir", line.strip(), re.IGNORECASE):
            start = i
            break
    picked = [l for l in lines[start:] if l.strip()][:limit]
    return "\n".join(picked)


def review_problems(root, last_change):
    review = latest_review(root)
    if not review:
        return ["Nenhuma rodada em Saved/Review. Rode a skill /revisao-aaa (fotos, fidelidade.py, revisor-visual)."]
    name = os.path.basename(review)
    revisao = os.path.join(review, "REVISAO.md")
    parecer = os.path.join(review, "PARECER.md")
    fid = os.path.join(review, "fidelidade.json")
    problems = []

    if mtime(revisao) < last_change:
        return ["A última rodada (%s) é anterior à sua última mudança. Fotografe de novo com /revisao-aaa." % name]

    shots = [os.path.basename(p) for p in glob.glob(os.path.join(review, "*.png"))]
    if not any(re.search(r"_q4\.png$", s) for s in shots):
        problems.append("Faltam fotos na qualidade 4 (cinematográfica) em %s. Coloque câmeras Rev_* no mapa." % name)
    if not any(re.search(r"_q[0-3]\.png$", s) for s in shots):
        problems.append("Faltam fotos numa qualidade menor (NOV_TIERS=4,1) em %s: o estilo precisa se sustentar em PC fraco." % name)

    fid_ok = None
    if os.path.isfile(os.path.join(root, "Referencias", "pares.json")):
        if not os.path.isfile(fid):
            problems.append("Falta fidelidade.json em %s. Rode: python Scripts/fidelidade.py --pares Referencias/pares.json --dir \"%s\""
                            % (name, review))
        else:
            try:
                with open(fid, encoding="utf-8") as f:
                    fid_ok = bool(json.load(f).get("passou"))
            except (OSError, ValueError):
                problems.append("fidelidade.json ilegível em %s. Rode o fidelidade.py de novo." % name)

    if not os.path.isfile(parecer):
        problems.append("Falta PARECER.md em %s. Chame o subagente revisor-visual para julgar a rodada." % name)
        return problems
    if mtime(parecer) < max(mtime(revisao), mtime(fid)):
        problems.append("O PARECER.md é anterior às fotos ou à medição. Chame o revisor-visual de novo.")
        return problems

    with open(parecer, encoding="utf-8", errors="replace") as f:
        text = f.read()
    verdict = VERDICT.search(text)
    if not verdict:
        problems.append("O PARECER.md não tem a linha \"VEREDITO: APROVADO\" ou \"VEREDITO: REPROVADO\".")
    elif verdict.group(1).upper() == "REPROVADO":
        problems.append("O revisor-visual REPROVOU a rodada %s. Corrija e fotografe de novo. Defeitos:\n%s"
                        % (name, parecer_excerpt(text)))
    elif fid_ok is False:
        problems.append("O parecer aprova, mas o fidelidade.json reprovou. Número vence opinião: corrija até a medição passar.")
    return problems


def state_path(session_id):
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "sem-sessao")
    return os.path.join(tempfile.gettempdir(), "novamente_prova_%s.json" % safe)


def bump_counter(data):
    path = state_path(data.get("session_id"))
    count = 0
    if data.get("stop_hook_active"):
        try:
            with open(path, encoding="utf-8") as f:
                count = int(json.load(f).get("bloqueios", 0))
        except (OSError, ValueError):
            count = 0
    count += 1
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"bloqueios": count}, f)
    except OSError:
        pass
    return count


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=True))
    sys.stdout.flush()


def run_hook():
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError:
        data = {}
    root = project_dir(data)
    problems = seal_problems(root)

    last_change, last_path = newest_change(root)
    touched = last_path is not None and last_change > session_start(data)
    message = data.get("last_assistant_message") or ""
    escaped = any(e in message for e in ESCAPES)

    if touched and not escaped:
        problems += review_problems(root, last_change)
    if not problems:
        return

    count = bump_counter(data)
    if count > MAX_BLOCKS:
        emit({"systemMessage": "exigir_prova: %d bloqueios seguidos; liberei para não girar sem fim. "
                               "Pendências: %s" % (MAX_BLOCKS, " | ".join(p.splitlines()[0] for p in problems))})
        return

    changed = ""
    if touched and not escaped:
        changed = "Última mudança visual: %s.\n" % os.path.relpath(last_path, root)
    reason = ("Sem prova visual aprovada, a vez não termina (NOVAMENTE AAA+).\n" + changed + "\n".join("- " + p for p in problems) +
              "\n\nSe o que falta depende do autor ou de algo fora do seu alcance, encerre com uma linha começando por "
              "\"PENDENTE:\" dizendo o que falta e de quem depende. Se a mudança não altera a imagem, comece com "
              "\"SEM EFEITO VISUAL:\" e explique. Nunca diga que terminou sem a prova.")
    emit({"decision": "block", "reason": reason})


def run_check():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    last_change, last_path = newest_change(root)
    problems = seal_problems(root)
    if last_path:
        print("Última mudança visual: %s (%s)" % (os.path.relpath(last_path, root),
                                                 datetime.datetime.fromtimestamp(last_change).strftime("%Y-%m-%d %H:%M:%S")))
        problems += review_problems(root, last_change)
    if problems:
        print("FALTA PROVA:")
        for p in problems:
            print("- " + p)
        sys.exit(1)
    print("OK: a rodada mais nova cobre a última mudança e foi aprovada.")


def main():
    if "--selar" in sys.argv:
        seal(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    elif "--checar" in sys.argv:
        run_check()
    else:
        run_hook()


if __name__ == "__main__":
    main()
