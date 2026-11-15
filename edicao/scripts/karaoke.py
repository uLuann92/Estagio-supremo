#!/usr/bin/env python3
"""Teste do karaokê: vídeo simples, em resolução baixa, com cada palavra acendendo no tempo alinhado.

  karaoke.py --audio <musica> --palavras letra_por_palavra.json --batidas batidas.json --saida karaoke.mp4
             [--inicio S] [--fim S] [--suspeitas letra_por_palavra_suspeitas.json]

No canto de cima: o tempo, o número do compasso, o tempo do compasso e a seção. Linha suspeita aparece em laranja.
Precisa de ffmpeg com libass.
"""
import argparse, json, os, subprocess, sys, tempfile


def ts(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True); p.add_argument("--palavras", required=True)
    p.add_argument("--batidas", required=True); p.add_argument("--saida", required=True)
    p.add_argument("--inicio", type=float, default=0.0); p.add_argument("--fim", type=float)
    p.add_argument("--suspeitas")
    a = p.parse_args()
    palavras = json.load(open(a.palavras, encoding="utf-8"))
    grade = json.load(open(a.batidas, encoding="utf-8"))
    fim = a.fim or grade["duracao"]
    susp = set()
    if a.suspeitas and os.path.exists(a.suspeitas):
        susp = {x["linha"] for x in json.load(open(a.suspeitas, encoding="utf-8"))}
    linhas = {}
    for w in palavras:
        linhas.setdefault(w["linha"], []).append(w)
    cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Letra,DejaVu Sans,26,&H0000FFFF,&H00808080,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,5,30,30,20,1
Style: Susp,DejaVu Sans,26,&H0000A5FF,&H00808080,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,5,30,30,20,1
Style: Topo,DejaVu Sans Mono,16,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,7,12,12,10,1
Style: Batida,DejaVu Sans Mono,30,&H0000FF00,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1,0,9,12,12,6,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    ordem = sorted(linhas)
    for i, n in enumerate(ordem):
        ws = linhas[n]
        ini, ult = ws[0]["inicio"], ws[-1]["fim"]
        prox = linhas[ordem[i + 1]][0]["inicio"] if i + 1 < len(ordem) else ult + 2
        mostra_ini = max(ini - 0.6, linhas[ordem[i - 1]][-1]["fim"] if i else 0)
        mostra_fim = min(max(ult + 0.4, ini + 0.8), max(prox, ult))
        if mostra_fim < a.inicio or mostra_ini > fim:
            continue
        txt = "{\\k%d}" % max(0, round((ini - mostra_ini) * 100))
        for j, w in enumerate(ws):
            ate = ws[j + 1]["inicio"] if j + 1 < len(ws) else w["fim"]
            txt += "{\\k%d}%s " % (max(1, round((ate - w["inicio"]) * 100)), w["palavra"].replace("{", "(").replace("}", ")"))
        estilo = "Susp" if n in susp else "Letra"
        ev.append(f"Dialogue: 1,{ts(mostra_ini - a.inicio)},{ts(mostra_fim - a.inicio)},{estilo},,0,0,0,,{txt.strip()}")
        sec = ws[0].get("secao", "")
        ev.append(f"Dialogue: 0,{ts(mostra_ini - a.inicio)},{ts(mostra_fim - a.inicio)},Topo,,0,0,0,,"
                  f"{{\\an1}}linha {n} · {sec}" + (" · SUSPEITA" if n in susp else ""))
    bs = grade["batidas"]
    for i, b in enumerate(bs):
        t1 = bs[i + 1]["t"] if i + 1 < len(bs) else b["t"] + 0.4
        if t1 < a.inicio or b["t"] > fim:
            continue
        ev.append(f"Dialogue: 0,{ts(b['t'] - a.inicio)},{ts(t1 - a.inicio)},Topo,,0,0,0,,"
                  f"compasso {b['compasso']} · tempo {b['tempo']}")
        cor = "&H0000FF00&" if b["tempo"] == 1 else "&H00606060&"
        ev.append(f"Dialogue: 0,{ts(b['t'] - a.inicio)},{ts(min(t1, b['t'] + 0.12) - a.inicio)},Batida,,0,0,0,,{{\\c{cor}}}●")
    with tempfile.TemporaryDirectory() as d:
        ass = os.path.join(d, "k.ass")
        open(ass, "w", encoding="utf-8").write(cab + "\n".join(ev) + "\n")
        dur = fim - a.inicio
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x101014:s=640x360:r=24:d={dur:.3f}",
               "-ss", f"{a.inicio:.3f}", "-t", f"{dur:.3f}", "-i", a.audio,
               "-vf", f"ass={ass}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-shortest", a.saida]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("ERRO no ffmpeg: " + r.stderr[-400:])
    print(f"Karaokê gravado em {a.saida} ({dur:.0f} s)")


if __name__ == "__main__":
    main()
