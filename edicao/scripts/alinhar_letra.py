#!/usr/bin/env python3
"""Alinhamento forçado da letra: o texto é a letra escrita; o áudio (de preferência a voz isolada) só dá o tempo.

  alinhar_letra.py <voz.wav> --linhas letra_linhas.json --saida letra_por_palavra.json [--modelo small] [--idioma pt]

`letra_linhas.json`: lista de {"n", "secao", "texto"} (uma linha da letra por item).
Saída: lista de {"palavra", "inicio", "fim", "linha", "secao", "prob"}, mais um relatório das linhas suspeitas.

Precisa de: torch e stable-ts (que baixa o modelo Whisper na primeira vez).
"""
import argparse
import json
import re
import sys

import stable_whisper


def limpar(texto):
    """Tira o que não é cantado como palavra: barras de cadência, parênteses de ad-lib ficam (são cantados)."""
    t = texto.replace("/", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio")
    p.add_argument("--linhas", required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--modelo", default="small")
    p.add_argument("--idioma", default="pt")
    a = p.parse_args()

    linhas = json.load(open(a.linhas, encoding="utf-8"))
    texto = "\n".join(limpar(x["texto"]) for x in linhas)
    modelo = stable_whisper.load_model(a.modelo, device="cpu")
    r = modelo.align(a.audio, texto, language=a.idioma, original_split=True, vad=False, suppress_silence=True)
    segs = r.segments
    if len(segs) != len(linhas):
        print(f"AVISO: {len(linhas)} linhas na letra, {len(segs)} segmentos alinhados; a numeração pode escorregar.",
              file=sys.stderr)
    palavras, suspeitas = [], []
    for i, s in enumerate(segs):
        ln = linhas[min(i, len(linhas) - 1)]
        ws = [w for w in s.words if w.word.strip()]
        for w in ws:
            palavras.append({"palavra": w.word.strip(), "inicio": round(float(w.start), 3), "fim": round(float(w.end), 3),
                             "linha": ln["n"], "secao": ln.get("secao", ""),
                             "prob": round(float(getattr(w, "probability", 0) or 0), 3)})
        if ws:
            dur = ws[-1].end - ws[0].start
            prob = sum(float(getattr(w, "probability", 0) or 0) for w in ws) / len(ws)
            curtas = sum(1 for w in ws if w.end - w.start < 0.04)
            motivo = []
            if prob < 0.35:
                motivo.append(f"confiança baixa ({prob:.2f})")
            if curtas > len(ws) / 2:
                motivo.append("palavras espremidas")
            if dur / len(ws) > 2.5:
                motivo.append("linha esticada demais")
            if motivo:
                suspeitas.append({"linha": ln["n"], "inicio": round(float(ws[0].start), 2), "texto": ln["texto"][:50],
                                  "motivo": ", ".join(motivo)})
    # o tempo tem de crescer
    for x, y in zip(palavras, palavras[1:]):
        if y["inicio"] < x["inicio"] - 0.01:
            suspeitas.append({"linha": y["linha"], "inicio": y["inicio"], "texto": y["palavra"], "motivo": "tempo voltou"})
    json.dump(palavras, open(a.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(suspeitas, open(a.saida.replace(".json", "_suspeitas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(palavras)} palavras em {len(segs)} linhas -> {a.saida}")
    print(f"{len(suspeitas)} linha(s) suspeita(s) para conferir no karaokê.")


if __name__ == "__main__":
    main()
