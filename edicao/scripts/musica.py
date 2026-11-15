#!/usr/bin/env python3
"""Ferramentas da etapa de música: grade de batidas, áudio de clique e mapa por compasso."""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from typing import Any, Dict, List, Optional, Tuple

import librosa
import numpy as np


def erro(mensagem: str) -> None:
    """Exibe uma mensagem de erro em português no stderr e encerra com código 1."""
    print(f"Erro: {mensagem}", file=sys.stderr)
    sys.exit(1)


def segundos_para_frame(t: float, fps: float) -> int:
    """Converte um instante em segundos para o frame inteiro mais próximo sem acumular arredondamento."""
    return int(round(float(t) * float(fps)))


def formatar_tempo(segundos: float) -> str:
    """Formata um tempo em segundos como mm:ss.cc (minutos, segundos e centésimos)."""
    total_centesimos = max(0, int(round(segundos * 100)))
    minutos = total_centesimos // 6000
    resto = total_centesimos % 6000
    segs = resto // 100
    cent = resto % 100
    return f"{minutos:02d}:{segs:02d}.{cent:02d}"


def ler_audio_ffmpeg(caminho: str, sr: int) -> np.ndarray:
    """Decodifica um arquivo de áudio via ffmpeg em PCM float32 mono na taxa especificada."""
    if not os.path.isfile(caminho):
        erro(f"Arquivo de áudio não encontrado: {caminho}")
    if shutil.which("ffmpeg") is None:
        erro("O programa 'ffmpeg' não foi encontrado no PATH.")

    cmd = [
        "ffmpeg",
        "-nostdin",
        "-v",
        "error",
        "-i",
        caminho,
        "-f",
        "f32le",
        "-ac",
        "1",
        "-ar",
        str(sr),
        "pipe:1",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        detalhe = proc.stderr.decode("utf-8", errors="replace").strip()
        erro(f"Falha ao decodificar '{caminho}' com ffmpeg: {detalhe}")

    amostras = np.frombuffer(proc.stdout, dtype=np.float32).copy()
    if amostras.size == 0:
        erro(f"O áudio '{caminho}' não contém amostras válidas.")
    return amostras


def gravar_wav_16bits(caminho: str, amostras: np.ndarray, sr: int) -> None:
    """Grava um array numpy mono (float em [-1, 1]) em um arquivo WAV PCM de 16 bits."""
    pasta = os.path.dirname(os.path.abspath(caminho))
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)

    limitado = np.clip(amostras, -1.0, 1.0)
    pcm16 = (limitado * 32767.0).astype(np.int16)

    try:
        with wave.open(caminho, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm16.tobytes())
    except Exception as exc:
        erro(f"Não foi possível gravar o arquivo WAV '{caminho}': {exc}")


def carregar_json(caminho: str, descricao: str) -> Any:
    """Carrega um arquivo JSON do disco ou encerra com erro amigável."""
    if not os.path.isfile(caminho):
        erro(f"Arquivo de {descricao} não encontrado: {caminho}")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        erro(f"Falha ao ler {descricao} em '{caminho}': {exc}")


def salvar_json(caminho: str, dados: Any) -> None:
    """Salva um dicionário ou lista como JSON UTF-8 indentado."""
    pasta = os.path.dirname(os.path.abspath(caminho))
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except Exception as exc:
        erro(f"Falha ao salvar JSON em '{caminho}': {exc}")


def ajustar_grade_robusta(tempos_batidas: np.ndarray) -> Tuple[float, float, np.ndarray]:
    """Ajusta reta robusta (período e offset) aos tempos detectados descartando outliers > 2,5 desvios."""
    if tempos_batidas.size < 4:
        erro("Poucas batidas detectadas para ajustar uma grade confiável (mínimo: 4).")

    indices = np.arange(tempos_batidas.size, dtype=np.float64)
    periodo1, offset1 = np.polyfit(indices, tempos_batidas, 1)
    residuos1 = tempos_batidas - (offset1 + indices * periodo1)
    desvio1 = float(np.std(residuos1))

    if desvio1 > 1e-9:
        mascara = np.abs(residuos1) <= (2.5 * desvio1)
        if np.count_nonzero(mascara) >= 4:
            periodo2, offset2 = np.polyfit(indices[mascara], tempos_batidas[mascara], 1)
        else:
            periodo2, offset2 = periodo1, offset1
    else:
        periodo2, offset2 = periodo1, offset1

    if periodo2 <= 0:
        erro("O período calculado para a grade é inválido (não positivo).")

    residuos_finais = tempos_batidas - (offset2 + indices * periodo2)
    return float(periodo2), float(offset2), residuos_finais


def calcular_envelope_alta_resolucao(y: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
    """Calcula envelope de ataque em alta resolução (janela=256, hop=32) com diferença positiva do log RMS suavizada."""
    frame_length = 256
    hop_length = 32
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length, center=True)[0]
    log_rms = np.log(1e-6 + rms.astype(np.float64))
    diff_pos = np.maximum(0.0, np.diff(log_rms, prepend=log_rms[0]))
    kernel = np.ones(3, dtype=np.float64) / 3.0
    env = np.convolve(diff_pos, kernel, mode="same")
    tempos_env = np.arange(env.size, dtype=np.float64) * (float(hop_length) / float(sr))
    return tempos_env, env


def refinar_offset_alta_resolucao(
    tempos_env: np.ndarray,
    env: np.ndarray,
    offset_inicial: float,
    periodo: float,
    duracao: float,
) -> Tuple[float, float]:
    """Busca d em [-0.060, +0.060] s (passo 0,5 ms) que maximiza a soma do envelope interpolado nas batidas."""
    total_est = int(math.floor((duracao - offset_inicial) / periodo)) + 1
    indices = np.arange(max(1, total_est), dtype=np.float64)
    tempos_base = offset_inicial + indices * periodo
    tempos_base = tempos_base[(tempos_base >= 0.0) & (tempos_base <= duracao)]

    deslocamentos = np.linspace(-0.060, 0.060, 241)
    melhor_d = 0.0
    maior_soma = -1.0

    for d in deslocamentos:
        t_cand = tempos_base + d
        validos = t_cand[(t_cand >= 0.0) & (t_cand <= duracao)]
        if validos.size == 0:
            continue
        soma = float(np.sum(np.interp(validos, tempos_env, env)))
        if soma > maior_soma:
            maior_soma = soma
            melhor_d = float(d)

    novo_offset = offset_inicial + melhor_d
    while novo_offset - periodo >= 0.0:
        novo_offset -= periodo
    if novo_offset < 0.0:
        passos = math.ceil(-novo_offset / periodo)
        novo_offset += passos * periodo

    return float(novo_offset), float(melhor_d * 1000.0)


def medir_residuo_e_deriva(
    tempos_env: np.ndarray,
    env: np.ndarray,
    tempos_grade: np.ndarray,
    periodo: float,
) -> Tuple[float, float]:
    """Calcula desvio padrão (ms) e deriva (ms) usando o pico do envelope de alta resolução em ±periodo/4 de cada batida."""
    meia_janela = 0.25 * periodo
    erros_ms_lista: List[float] = []

    for tg in tempos_grade:
        i0 = int(np.searchsorted(tempos_env, tg - meia_janela, side="left"))
        i1 = int(np.searchsorted(tempos_env, tg + meia_janela, side="right"))
        if i1 <= i0:
            continue
        fatia = env[i0:i1]
        if fatia.size == 0 or float(np.max(fatia)) <= 0.0:
            continue
        idx_pico = i0 + int(np.argmax(fatia))
        t_pico = float(tempos_env[idx_pico])
        erros_ms_lista.append((t_pico - float(tg)) * 1000.0)

    if not erros_ms_lista:
        return 0.0, 0.0

    erros_ms = np.array(erros_ms_lista, dtype=np.float64)
    residuo_ms = float(np.std(erros_ms))
    n = erros_ms.size
    quarto = max(1, n // 4)
    media_inicio = float(np.mean(erros_ms[:quarto]))
    media_fim = float(np.mean(erros_ms[-quarto:]))
    deriva_ms = media_fim - media_inicio
    return residuo_ms, deriva_ms


def estimar_fase_compasso_grave(
    y: np.ndarray,
    sr: int,
    tempos_grade: np.ndarray,
    por_compasso: int,
) -> Tuple[int, float]:
    """Escolhe a fase (0..por_compasso-1) que maximiza o envelope grave (<150 Hz) em ±40 ms de cada batida e calcula confiança."""
    n_fft = 2048
    hop_grave = 128
    stft = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_grave)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    mascara_grave = freqs < 150.0
    energia_grave = np.sum(stft[mascara_grave, :], axis=0)
    env_grave = np.maximum(0.0, np.diff(energia_grave, prepend=energia_grave[0]))
    tempos_grave = np.arange(env_grave.size, dtype=np.float64) * (float(hop_grave) / float(sr))

    janela_s = 0.040
    somas: List[float] = []
    for f in range(por_compasso):
        batidas_fase = tempos_grade[f::por_compasso]
        soma_f = 0.0
        for tb in batidas_fase:
            i0 = int(np.searchsorted(tempos_grave, tb - janela_s, side="left"))
            i1 = int(np.searchsorted(tempos_grave, tb + janela_s, side="right"))
            if i1 > i0:
                soma_f += float(np.max(env_grave[i0:i1]))
        somas.append(soma_f)

    if not somas:
        return 0, 1.0

    melhor_fase = int(np.argmax(somas))
    ordenadas = sorted(somas, reverse=True)
    maior = ordenadas[0]
    segunda = ordenadas[1] if len(ordenadas) > 1 else 0.0
    if segunda > 1e-12:
        confianca = maior / segunda
    else:
        confianca = 99.99 if maior > 0.0 else 1.0
    return melhor_fase, round(float(confianca), 2)


def cmd_grade(args: argparse.Namespace) -> None:
    """Executa o subcomando 'grade': detecta batidas, ajusta grade constante e grava o JSON."""
    if args.fps <= 0:
        erro("O valor de --fps deve ser maior que zero.")
    if args.por_compasso < 1:
        erro("O valor de --por-compasso deve ser pelo menos 1.")

    sr = 22050
    hop_length = 512
    y = ler_audio_ffmpeg(args.audio, sr)
    duracao = float(y.size) / float(sr)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

    kwargs_beat: Dict[str, Any] = {
        "onset_envelope": onset_env,
        "sr": sr,
        "hop_length": hop_length,
        "units": "frames",
    }
    if args.bpm is not None:
        if args.bpm <= 0:
            erro("O --bpm informado deve ser positivo.")
        kwargs_beat["start_bpm"] = float(args.bpm)
        kwargs_beat["tightness"] = 400.0

    _, beat_frames = librosa.beat.beat_track(**kwargs_beat)
    tempos_detectados = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)

    periodo_base, offset_base, _ = ajustar_grade_robusta(tempos_detectados)

    while offset_base - periodo_base >= 0.0:
        offset_base -= periodo_base
    if offset_base < 0.0:
        passos = math.ceil(-offset_base / periodo_base)
        offset_base += passos * periodo_base

    leitura = args.leitura
    if leitura == "metade":
        periodo = periodo_base * 2.0
    elif leitura == "dobro":
        periodo = periodo_base / 2.0
    else:
        periodo = periodo_base

    offset_pre = offset_base
    while offset_pre - periodo >= 0.0:
        offset_pre -= periodo

    tempos_env_hr, env_hr = calcular_envelope_alta_resolucao(y, sr)
    offset, refino_offset_ms = refinar_offset_alta_resolucao(
        tempos_env_hr, env_hr, offset_pre, periodo, duracao
    )

    bpm_final = 60.0 / periodo

    total_batidas = int(math.floor((duracao - offset) / periodo)) + 1
    if total_batidas < 1:
        erro("Nenhuma batida cabe na duração do áudio com o período calculado.")

    indices = np.arange(total_batidas, dtype=np.int64)
    tempos_grade = offset + indices.astype(np.float64) * periodo
    mascara_validos = tempos_grade <= duracao + 1e-9
    indices = indices[mascara_validos]
    tempos_grade = tempos_grade[mascara_validos]

    residuo_ms, deriva_ms = medir_residuo_e_deriva(tempos_env_hr, env_hr, tempos_grade, periodo)

    fase_est, fase_confianca = estimar_fase_compasso_grave(y, sr, tempos_grade, args.por_compasso)
    if args.fase is not None:
        if not (0 <= args.fase < args.por_compasso):
            erro(f"--fase deve estar entre 0 e {args.por_compasso - 1}.")
        fase = int(args.fase)
        fase_estimada = False
    else:
        fase = fase_est
        fase_estimada = True

    lista_batidas: List[Dict[str, Any]] = []
    for i_val, t_val in zip(indices.tolist(), tempos_grade.tolist()):
        if i_val < fase:
            compasso = 0
            tempo_no_compasso = ((i_val - fase) % args.por_compasso) + 1
        else:
            compasso = ((i_val - fase) // args.por_compasso) + 1
            tempo_no_compasso = ((i_val - fase) % args.por_compasso) + 1

        lista_batidas.append(
            {
                "i": int(i_val),
                "t": round(float(t_val), 4),
                "frame": segundos_para_frame(t_val, args.fps),
                "compasso": int(compasso),
                "tempo": int(tempo_no_compasso),
            }
        )

    dados_saida = {
        "audio": args.audio,
        "duracao": round(duracao, 4),
        "fps": args.fps,
        "bpm": round(bpm_final, 4),
        "periodo": round(periodo, 6),
        "offset": round(offset, 4),
        "refino_offset_ms": round(refino_offset_ms, 2),
        "por_compasso": int(args.por_compasso),
        "fase": int(fase),
        "fase_estimada": bool(fase_estimada),
        "fase_confianca": round(fase_confianca, 2),
        "leitura": leitura,
        "residuo_ms": round(residuo_ms, 2),
        "deriva_ms": round(deriva_ms, 2),
        "batidas": lista_batidas,
    }

    salvar_json(args.saida, dados_saida)

    compassos_totais = max((b["compasso"] for b in lista_batidas), default=0)
    aviso_estabilidade = (
        "AVISO: a música pode mudar de andamento ou a detecção falhou: confira no teste do clique"
        if (residuo_ms > 25.0 or abs(deriva_ms) > 30.0)
        else "OK: grade estável dentro dos limites de resíduo e deriva."
    )

    origem_fase = "estimada pelo grave" if fase_estimada else "fixada por parâmetro"
    print(f"Áudio: {args.audio} | Duração: {duracao:.2f}s | FPS: {args.fps}")
    print(
        f"Andamento: {bpm_final:.2f} BPM (leitura: {leitura}) | Período: {periodo:.4f}s | "
        f"Offset: {offset:.4f}s (refino: {refino_offset_ms:+.2f} ms)"
    )
    print(
        f"Grade: {len(lista_batidas)} batidas, {compassos_totais} compassos ({args.por_compasso}/4), "
        f"fase {fase} ({origem_fase}, confiança: {fase_confianca:.2f})"
    )
    if fase_estimada and fase_confianca < 1.15:
        print("AVISO: primeiro tempo do compasso incerto: confirme no teste do clique (use --fase)")
    print(f"Precisão: resíduo = {residuo_ms:.2f} ms | deriva = {deriva_ms:+.2f} ms")
    print(f"Diagnóstico: {aviso_estabilidade} -> Salvo em {args.saida}")


def gerar_sinal_clique(sr: int, freq: float, amplitude: float, duracao_s: float = 0.030) -> np.ndarray:
    """Sintetiza um pulso senoidal curto com decaimento exponencial para marcação de batida."""
    n = int(round(duracao_s * sr))
    t = np.arange(n, dtype=np.float32) / float(sr)
    envelope = np.exp(-t / 0.008).astype(np.float32)
    return (amplitude * np.sin(2.0 * math.pi * freq * t) * envelope).astype(np.float32)


def cmd_clique(args: argparse.Namespace) -> None:
    """Executa o subcomando 'clique': mistura cliques nas batidas ao áudio original e salva WAV."""
    sr = 44100
    dados_grade = carregar_json(args.batidas, "batidas")
    batidas = dados_grade.get("batidas", [])
    if not batidas:
        erro("O arquivo de batidas não contém nenhuma batida.")

    audio = ler_audio_ffmpeg(args.audio, sr)
    duracao_total = audio.size / float(sr)

    inicio_s = float(args.inicio) if args.inicio is not None else 0.0
    fim_s = float(args.fim) if args.fim is not None else duracao_total
    if inicio_s < 0 or fim_s <= inicio_s:
        erro("Intervalo [inicio, fim] inválido.")

    mix = audio * 0.65
    clique_forte = gerar_sinal_clique(sr, freq=2000.0, amplitude=0.85, duracao_s=0.030)
    clique_comum = gerar_sinal_clique(sr, freq=1000.0, amplitude=0.45, duracao_s=0.030)

    for b in batidas:
        t_batida = float(b["t"])
        idx_ini = int(round(t_batida * sr))
        if idx_ini < 0 or idx_ini >= mix.size:
            continue
        sinal = clique_forte if int(b.get("tempo", 0)) == 1 else clique_comum
        idx_fim = min(mix.size, idx_ini + sinal.size)
        mix[idx_ini:idx_fim] += sinal[: idx_fim - idx_ini]

    amostra_ini = max(0, int(round(inicio_s * sr)))
    amostra_fim = min(mix.size, int(round(fim_s * sr)))
    trecho = mix[amostra_ini:amostra_fim]
    if trecho.size == 0:
        erro("O recorte solicitado resultou em áudio vazio.")

    pico = float(np.max(np.abs(trecho)))
    if pico > 0.98:
        trecho = trecho * (0.98 / pico)

    gravar_wav_16bits(args.saida, trecho, sr)
    print(
        f"Teste do clique gravado em '{args.saida}' "
        f"({(amostra_fim - amostra_ini) / sr:.2f}s, {len(batidas)} batidas na grade)."
    )


def agrupar_compassos(
    batidas: List[Dict[str, Any]], duracao_audio: float, periodo: float
) -> List[Dict[str, Any]]:
    """Agrupa a lista de batidas por número de compasso com tempo de início, fim e frame inicial."""
    por_num: Dict[int, List[Dict[str, Any]]] = {}
    for b in batidas:
        c = int(b["compasso"])
        por_num.setdefault(c, []).append(b)

    numeros = sorted(por_num.keys())
    compassos: List[Dict[str, Any]] = []
    for pos, c in enumerate(numeros):
        grupo = por_num[c]
        t_ini = float(grupo[0]["t"])
        frame_ini = int(grupo[0]["frame"])
        if pos + 1 < len(numeros):
            t_fim = float(por_num[numeros[pos + 1]][0]["t"])
        else:
            t_fim = min(duracao_audio, float(grupo[-1]["t"]) + periodo)
        compassos.append(
            {
                "compasso": c,
                "t_ini": t_ini,
                "t_fim": max(t_ini, t_fim),
                "frame": frame_ini,
            }
        )
    return compassos


def calcular_energias_quintis(y: np.ndarray, sr: int, compassos: List[Dict[str, Any]]) -> List[int]:
    """Calcula o RMS de cada compasso no áudio e converte para escala de 1 a 5 pelos quintis."""
    rms_vals: List[float] = []
    for comp in compassos:
        i0 = max(0, int(round(comp["t_ini"] * sr)))
        i1 = min(y.size, int(round(comp["t_fim"] * sr)))
        if i1 <= i0:
            rms_vals.append(0.0)
        else:
            bloco = y[i0:i1]
            rms_vals.append(float(np.sqrt(np.mean(bloco * bloco))))

    arr = np.array(rms_vals, dtype=np.float64)
    if arr.size == 0:
        return []
    q20, q40, q60, q80 = np.percentile(arr, [20, 40, 60, 80])
    notas: List[int] = []
    for v in rms_vals:
        if v <= q20:
            notas.append(1)
        elif v <= q40:
            notas.append(2)
        elif v <= q60:
            notas.append(3)
        elif v <= q80:
            notas.append(4)
        else:
            notas.append(5)
    return notas


def montar_letra_por_compasso(
    compassos: List[Dict[str, Any]], palavras: List[Dict[str, Any]]
) -> Dict[int, str]:
    """Associa cada palavra ao compasso onde ela começa e formata o texto com indicação de voz."""
    textos: Dict[int, List[str]] = {c["compasso"]: [] for c in compassos}
    vozes_atuais: Dict[int, Optional[str]] = {c["compasso"]: None for c in compassos}

    palavras_ord = sorted(palavras, key=lambda p: float(p.get("inicio", 0.0)))
    for p in palavras_ord:
        texto = str(p.get("palavra", "")).strip()
        if not texto:
            continue
        t_ini = float(p.get("inicio", 0.0))
        voz = p.get("voz")

        alvo = compassos[-1]["compasso"] if compassos else 0
        for c in compassos:
            if c["t_ini"] - 1e-6 <= t_ini < c["t_fim"] - 1e-6:
                alvo = c["compasso"]
                break
            if t_ini < c["t_ini"]:
                alvo = c["compasso"]
                break

        if voz and voz != vozes_atuais.get(alvo):
            textos[alvo].append(f"[{voz}:] {texto}")
            vozes_atuais[alvo] = str(voz)
        else:
            textos[alvo].append(texto)

    return {k: " ".join(v).replace("|", "/") for k, v in textos.items()}


def cmd_mapa(args: argparse.Namespace) -> None:
    """Executa o subcomando 'mapa': gera a tabela Markdown com seção, energia e letra por compasso."""
    dados_grade = carregar_json(args.batidas, "batidas")
    batidas = dados_grade.get("batidas", [])
    if not batidas:
        erro("O arquivo de batidas está vazio.")

    sr = 22050
    y = ler_audio_ffmpeg(args.audio, sr)
    duracao = float(dados_grade.get("duracao", y.size / float(sr)))
    periodo = float(dados_grade.get("periodo", 60.0 / float(dados_grade.get("bpm", 120.0))))
    fps = float(dados_grade.get("fps", 24))
    bpm = float(dados_grade.get("bpm", 120.0))
    offset = float(dados_grade.get("offset", 0.0))

    compassos = agrupar_compassos(batidas, duracao, periodo)
    energias = calcular_energias_quintis(y, sr, compassos)

    palavras: List[Dict[str, Any]] = []
    if args.letra:
        bruto_letra = carregar_json(args.letra, "letra por palavra")
        palavras = bruto_letra if isinstance(bruto_letra, list) else bruto_letra.get("palavras", [])
    letras_comp = montar_letra_por_compasso(compassos, palavras) if palavras else {}

    secoes: List[Dict[str, Any]] = []
    if args.secoes:
        bruto_sec = carregar_json(args.secoes, "seções")
        secoes = bruto_sec if isinstance(bruto_sec, list) else bruto_sec.get("secoes", [])

    def nome_secao(num_comp: int) -> str:
        """Retorna o nome da seção correspondente ao número do compasso ou '-'."""
        for s in secoes:
            if int(s["compasso_ini"]) <= num_comp <= int(s["compasso_fim"]):
                return str(s["nome"])
        return "-"

    linhas_md = [
        "# Mapa da Música",
        "",
        f"- **BPM:** {bpm:.4f}",
        f"- **Offset:** {offset:.4f} s",
        f"- **FPS:** {fps:g}",
        f"- **Compassos:** {len(compassos)}",
        f"- **Duração:** {duracao:.2f} s ({formatar_tempo(duracao)})",
        "",
        "| compasso | mm:ss.cc | frame | seção | energia | letra |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    energias_por_secao: Dict[str, List[int]] = {}
    for comp, nota in zip(compassos, energias):
        c_num = comp["compasso"]
        sec = nome_secao(c_num)
        letra_txt = letras_comp.get(c_num, "")
        frame_c = segundos_para_frame(comp["t_ini"], fps)
        linhas_md.append(
            f"| {c_num} | {formatar_tempo(comp['t_ini'])} | {frame_c} | {sec} | {nota} | {letra_txt} |"
        )
        if sec != "-":
            energias_por_secao.setdefault(sec, []).append(nota)

    pasta = os.path.dirname(os.path.abspath(args.saida))
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)
    with open(args.saida, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md) + "\n")

    print(f"Mapa gerado em '{args.saida}' com {len(compassos)} compassos.")
    if energias_por_secao:
        resumo_sec = ", ".join(
            f"{nome}: {np.mean(vals):.2f}" for nome, vals in energias_por_secao.items()
        )
        print(f"Energia média por seção (1–5): {resumo_sec}")


def construir_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o parser de linha de comando com os subcomandos grade, clique e mapa."""
    parser = argparse.ArgumentParser(
        prog="musica.py",
        description="Prepara a grade de batidas, o teste do clique e o mapa por compasso da música.",
    )
    sub = parser.add_subparsers(dest="subcomando", required=True)

    p_grade = sub.add_parser("grade", help="Detecta batidas e ajusta grade de andamento constante.")
    p_grade.add_argument("audio", help="Caminho do arquivo de áudio.")
    p_grade.add_argument("--saida", required=True, help="Caminho do arquivo batidas.json de saída.")
    p_grade.add_argument("--fps", type=float, default=24.0, help="Taxa de quadros do vídeo (padrão: 24).")
    p_grade.add_argument("--por-compasso", type=int, default=4, help="Tempos por compasso (padrão: 4).")
    p_grade.add_argument("--bpm", type=float, default=None, help="BPM aproximado inicial (opcional).")
    p_grade.add_argument(
        "--leitura",
        choices=["auto", "metade", "dobro"],
        default="auto",
        help="Ajusta leitura de andamento em metade ou dobro (padrão: auto).",
    )
    p_grade.add_argument("--fase", type=int, default=None, help="Índice da primeira batida forte (0..N-1).")
    p_grade.set_defaults(func=cmd_grade)

    p_clique = sub.add_parser("clique", help="Gera áudio WAV com clique nas batidas para conferência.")
    p_clique.add_argument("audio", help="Caminho do arquivo de áudio.")
    p_clique.add_argument("--batidas", required=True, help="Caminho do batidas.json gerado na grade.")
    p_clique.add_argument("--saida", required=True, help="Caminho do arquivo WAV de saída.")
    p_clique.add_argument("--inicio", type=float, default=None, help="Início do recorte em segundos.")
    p_clique.add_argument("--fim", type=float, default=None, help="Fim do recorte em segundos.")
    p_clique.set_defaults(func=cmd_clique)

    p_mapa = sub.add_parser("mapa", help="Gera o mapa Markdown por compasso com energia, seção e letra.")
    p_mapa.add_argument("--batidas", required=True, help="Caminho do arquivo batidas.json.")
    p_mapa.add_argument("--audio", required=True, help="Caminho do arquivo de áudio.")
    p_mapa.add_argument("--saida", required=True, help="Caminho do arquivo mapa.md de saída.")
    p_mapa.add_argument("--letra", default=None, help="JSON opcional de palavras alinhadas.")
    p_mapa.add_argument("--secoes", default=None, help="JSON opcional de seções em compassos.")
    p_mapa.set_defaults(func=cmd_mapa)

    return parser


def main() -> None:
    """Ponto de entrada principal do script."""
    parser = construir_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
