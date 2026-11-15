#!/usr/bin/env python3
"""Grade de batidas para música cujo andamento varia um pouco (comum em faixas geradas por IA).

O `musica.py grade` ajusta UMA grade constante. Quando o resíduo dele vem alto e o andamento medido por trecho
muda (ex.: 135 -> 137 BPM), use este: ele acha um trecho firme, trava a grade ali e segue a batida para a
frente e para trás, corrigindo período e fase aos poucos. Onde a batida some (intro, ponte), ele segue no embalo.

Saída no mesmo formato do `musica.py grade` (serve para `musica.py clique` e `mapa`).

  grade_variavel.py <audio> --saida batidas.json [--bpm 135] [--fps 24] [--por-compasso 4] [--fase N]
                    [--ancora S]   (um tempo, em segundos, que é com certeza o tempo 1 de um compasso)
"""
import argparse
import json
import subprocess
import sys

import librosa
import numpy as np

SR, HOP = 22050, 64
DT = HOP / SR


def ler(caminho):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", caminho, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit(f"ERRO: não consegui ler o áudio: {r.stderr.decode()[:200]}")
    return np.frombuffer(r.stdout, np.float32)


def envelopes(y):
    """Envelope de ataque (todas as faixas) e envelope do grave, com passo de ~2,9 ms."""
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=HOP))
    f = librosa.fft_frequencies(sr=SR, n_fft=1024)

    def ataque(mask):
        e = np.log1p(S[mask].sum(0))
        d = np.maximum(np.diff(e, prepend=e[0]), 0)
        return np.convolve(d, np.ones(3) / 3, mode="same")
    return ataque(f > 0), ataque(f < 150)


def amostra(env, tempos):
    return np.interp(np.asarray(tempos) / DT, np.arange(len(env)), env, left=0, right=0)


def melhor_global(env, t0, t1, bpm_min, bpm_max):
    """Período e fase que mais batem com o envelope entre t0 e t1."""
    melhor = (-1, None, None)
    for bpm in np.arange(bpm_min, bpm_max, 0.05):
        per = 60 / bpm
        n = int((t1 - t0) / per) - 1
        k = np.arange(n)
        for fase in np.arange(0, per, 0.002):
            s = amostra(env, t0 + fase + k * per).mean()
            if s > melhor[0]:
                melhor = (s, per, t0 + fase)
    return melhor[1], melhor[2], melhor[0]


def seguir(env, t_ini, per_ini, limite, sentido, janela=16, passo=4):
    """Segue a batida a partir de t_ini no sentido dado (+1 ou -1). Devolve [(tempo, firme)]."""
    base = float(np.median(env)) + 1e-9
    t, per, saida = t_ini, per_ini, []
    k = np.arange(janela)
    while (t < limite) if sentido > 0 else (t > limite):
        melhor = (-1, per, 0.0)
        for fp in np.arange(0.988, 1.0121, 0.002):
            p2 = per * fp
            for d in np.arange(-0.030, 0.0301, 0.002):
                s = amostra(env, t + d + sentido * k * p2).mean()
                if s > melhor[0]:
                    melhor = (s, p2, d)
        parado = amostra(env, t + sentido * k * per).mean()
        firme = melhor[0] > 6 * base and melhor[0] > 1.15 * parado
        if firme:  # corrige com freio, para não pular atrás de um ataque solto
            per = 0.6 * per + 0.4 * melhor[1]
            t = t + 0.6 * melhor[2]
        elif melhor[0] > 6 * base:
            firme = True  # a grade atual já bate bem: mantém
        for j in range(passo):
            saida.append((t + sentido * j * per, firme))
        t = t + sentido * passo * per
    return saida


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio")
    p.add_argument("--saida", required=True)
    p.add_argument("--bpm", type=float, help="andamento aproximado (padrão: procura entre 60 e 180)")
    p.add_argument("--fps", type=float, default=24)
    p.add_argument("--por-compasso", type=int, default=4)
    p.add_argument("--fase", type=int, help="índice (0..N-1) da batida que é o tempo 1; ignora a estimativa")
    p.add_argument("--ancora", type=float, help="um instante (s) que é com certeza um tempo 1 de compasso")
    a = p.parse_args()

    y = ler(a.audio)
    dur = len(y) / SR
    env, grave = envelopes(y)

    # 1. o trecho de 24 s mais "batido" da música (maior energia de ataque) vira o ponto de partida
    n = int(24 / DT)
    soma = np.convolve(env, np.ones(n), mode="valid")
    ini = float(np.argmax(soma) * DT)
    lo, hi = (a.bpm * 0.96, a.bpm * 1.04) if a.bpm else (60, 180)
    per0, t0, _ = melhor_global(env, ini, ini + 24, lo, hi)

    # 2. segue para a frente e para trás
    frente = seguir(env, t0, per0, dur, +1)
    tras = seguir(env, t0, per0, 0.0, -1)[1:]
    todos = sorted(tras + frente)
    todos = [(t, f) for t, f in todos if 0 <= t <= dur]
    tempos = np.array([t for t, _ in todos])
    firmes = np.array([f for _, f in todos])

    # 3. tempo 1 do compasso
    m = a.por_compasso
    if a.ancora is not None:
        fase = int(np.argmin(np.abs(tempos - a.ancora))) % m
        confianca, origem = None, f"âncora em {a.ancora:.2f}s"
    elif a.fase is not None:
        fase, confianca, origem = a.fase % m, None, "informada"
    else:
        forca = [max(amostra(grave, tempos[i] + d) for d in np.arange(-0.04, 0.041, 0.005)) for i in range(len(tempos))]
        somas = [float(np.sum([forca[i] for i in range(f, len(tempos), m) if firmes[i]])) for f in range(m)]
        ordem = np.argsort(somas)[::-1]
        fase = int(ordem[0])
        confianca = round(somas[ordem[0]] / (somas[ordem[1]] + 1e-9), 2)
        origem = "estimada pelo grave"

    # 4. resíduo: distância de cada batida firme ao pico de ataque mais próximo (±1/4 de batida)
    res = []
    for i, t in enumerate(tempos):
        if not firmes[i]:
            continue
        q = 60 / 135 / 4 if i == 0 else (tempos[i] - tempos[i - 1]) / 4
        d = np.arange(-q, q, 0.001)
        v = amostra(env, t + d)
        if v.max() > 4 * np.median(env):
            res.append(d[int(np.argmax(v))] * 1000)
    res = np.array(res) if res else np.array([0.0])

    batidas = []
    for i, t in enumerate(tempos):
        rel = i - fase
        batidas.append({"i": i, "t": round(float(t), 4), "frame": int(round(float(t) * a.fps)),
                        "compasso": (rel // m + 1) if rel >= 0 else 0, "tempo": rel % m + 1,
                        "firme": bool(firmes[i])})
    difs = np.diff(tempos)
    # andamento por trecho de 30 s, para o relatório
    trechos = []
    for s in range(0, int(dur), 30):
        sel = (tempos[:-1] >= s) & (tempos[:-1] < s + 30)
        if sel.sum() > 4:
            trechos.append({"de": s, "bpm": round(float(60 / np.median(difs[sel])), 2),
                            "firme": round(float(firmes[:-1][sel].mean()), 2)})
    saida = {"audio": a.audio, "duracao": round(dur, 3), "fps": a.fps, "bpm": round(float(60 / np.median(difs)), 4),
             "periodo": round(float(np.median(difs)), 5), "offset": round(float(tempos[0]), 4),
             "por_compasso": m, "fase": fase, "fase_estimada": origem.startswith("estimada"), "fase_confianca": confianca,
             "leitura": "auto", "grade": "variavel", "residuo_ms": round(float(np.std(res)), 2),
             "residuo_mediano_ms": round(float(np.median(res)), 2), "trechos": trechos,
             "parte_firme": round(float(firmes.mean()), 2), "batidas": batidas}
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f"Ponto de partida: {ini:.1f}s a {60 / per0:.2f} BPM")
    print(f"Grade variável: {len(batidas)} batidas, {batidas[-1]['compasso']} compassos; "
          f"{firmes.mean() * 100:.0f}% travada na batida, o resto no embalo")
    print("Andamento por 30 s: " + " ".join(f"{t['de']}s:{t['bpm']:.1f}" for t in trechos))
    print(f"Resíduo nas batidas firmes: desvio {saida['residuo_ms']} ms, mediana {saida['residuo_mediano_ms']} ms")
    print(f"Tempo 1 do compasso: fase {fase} ({origem}" + (f", confiança {confianca}" if confianca else "") + ")")
    if confianca is not None and confianca < 1.15:
        print("AVISO: primeiro tempo do compasso incerto: confirme no teste do clique (--fase ou --ancora).")


if __name__ == "__main__":
    main()
