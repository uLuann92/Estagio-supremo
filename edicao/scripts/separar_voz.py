#!/usr/bin/env python3
"""Separa a voz do instrumental com o Demucs (CPU serve; ~1 a 2x a duração da música).

  separar_voz.py <audio> --saida <pasta>      grava voz.wav e instrumental.wav (44,1 kHz, estéreo, 16 bits)

Precisa de: torch, demucs e ffmpeg. A leitura e a gravação não usam torchaudio (evita problema de versão).
"""
import argparse, os, subprocess, sys, wave
import numpy as np
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio"); p.add_argument("--saida", required=True); p.add_argument("--modelo", default="htdemucs")
    a = p.parse_args()
    modelo = get_model(a.modelo); modelo.eval()
    sr = modelo.samplerate
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit(f"ERRO ao ler o áudio: {r.stderr.decode()[:200]}")
    x = torch.from_numpy(np.frombuffer(r.stdout, np.float32).reshape(-1, 2).T.copy())
    ref = x.mean(0); x = (x - ref.mean()) / (ref.std() + 1e-8)
    with torch.no_grad():
        fontes = apply_model(modelo, x[None], device="cpu", shifts=0, split=True, overlap=0.25, progress=False)[0]
    fontes = fontes * (ref.std() + 1e-8) + ref.mean()
    nomes = modelo.sources
    voz = fontes[nomes.index("vocals")]
    resto = sum(fontes[i] for i, n in enumerate(nomes) if n != "vocals")
    os.makedirs(a.saida, exist_ok=True)
    for nome, t in (("voz", voz), ("instrumental", resto)):
        y = (t.clamp(-1, 1).T.numpy() * 32767).astype(np.int16)
        with wave.open(os.path.join(a.saida, nome + ".wav"), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(y.tobytes())
    print(f"Gravados voz.wav e instrumental.wav em {a.saida} ({x.shape[1] / sr:.1f} s)")


if __name__ == "__main__":
    main()
