#!/usr/bin/env python3
"""Segundo olhar: pergunta ao Google Gemini, com ou sem mídia (vídeo, áudio, imagem).

Só usa a biblioteca padrão do Python (nada para instalar).
A chave fica na variável de ambiente GEMINI_API_KEY. Nunca em arquivo, nunca no chat.

Uso:
  gemini.py testar
  gemini.py modelos
  gemini.py perguntar --pergunta "..." [--midia clipe.mp4 ...] [--saida resposta.md]
  gemini.py perguntar --arquivo-pergunta pergunta.md --midia ref01.mp4 --fps 12 --inicio 10 --fim 25
  gemini.py apagar            (apaga do Google os arquivos enviados por este script)

Como usar bem (1 fps por padrão, tempos aproximados, o que conferir): guias/segundo-olhar.md
"""
import argparse
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("GEMINI_API_BASE", "https://generativelanguage.googleapis.com").rstrip("/")
MODELO_PADRAO = os.environ.get("GEMINI_MODELO", "gemini-flash-latest")
CACHE = os.environ.get(
    "GEMINI_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "fluxo-de-edicao", "gemini-envios.json")
)
LIMITE_EMBUTIDO = 15 * 1024 * 1024  # acima disso, o arquivo vai pela Files API
TIPOS = {
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".mkv": "video/x-matroska", ".webm": "video/webm",
    ".avi": "video/x-msvideo", ".mpg": "video/mpeg", ".mpeg": "video/mpeg", ".wmv": "video/x-ms-wmv",
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".flac": "audio/flac", ".ogg": "audio/ogg",
    ".m4a": "audio/mp4", ".aac": "audio/aac",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
    ".pdf": "application/pdf", ".txt": "text/plain", ".md": "text/plain", ".json": "text/plain",
    ".srt": "text/plain", ".csv": "text/plain",
}


class Erro(Exception):
    pass


def chave():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        raise Erro(
            "Falta a chave. Crie uma no Google AI Studio e guarde na variável de ambiente GEMINI_API_KEY "
            "(a própria pessoa faz isso; a chave nunca é colada no chat). Depois, abra o terminal de novo."
        )
    return k.strip()


def chamar(metodo, url, corpo=None, cabecalhos=None, bruto=False, espera=600):
    """Uma chamada HTTP. Devolve (json | bytes, cabeçalhos). Tenta de novo em erro passageiro."""
    cab = {"x-goog-api-key": chave()}
    cab.update(cabecalhos or {})
    dados = corpo
    if corpo is not None and not hasattr(corpo, "read") and not isinstance(corpo, (bytes, bytearray)):
        dados = json.dumps(corpo).encode("utf-8")
        cab.setdefault("Content-Type", "application/json")
    reenviavel = not hasattr(dados, "read")
    for tentativa in range(4):
        req = urllib.request.Request(url, data=dados, method=metodo, headers=cab)
        try:
            with urllib.request.urlopen(req, timeout=espera) as r:
                conteudo = r.read()
                return (conteudo if bruto else json.loads(conteudo or b"{}")), r.headers
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", "replace")
            try:
                msg = json.loads(texto)["error"]["message"]
            except Exception:
                msg = texto[:500]
            if e.code in (429, 500, 502, 503, 504) and reenviavel and tentativa < 3:
                time.sleep(4 * 2 ** tentativa)
                continue
            dica = ""
            if e.code == 429:
                dica = " (limite de uso atingido: espere, use um modelo mais leve ou confira o plano)"
            elif e.code in (401, 403):
                dica = " (chave inválida ou sem acesso a este modelo)"
            elif e.code == 404:
                dica = " (modelo ou arquivo não existe: rode 'gemini.py modelos')"
            raise Erro(f"Gemini respondeu {e.code}: {msg}{dica}")
        except urllib.error.URLError as e:
            if reenviavel and tentativa < 3:
                time.sleep(4 * 2 ** tentativa)
                continue
            raise Erro(f"Sem conexão com o Gemini: {e.reason}")
    raise Erro("O Gemini não respondeu depois de várias tentativas.")


def tipo_de(caminho):
    ext = os.path.splitext(caminho)[1].lower()
    return TIPOS.get(ext) or mimetypes.guess_type(caminho)[0] or "application/octet-stream"


# ---------- envio de arquivos (Files API), com cache para não enviar duas vezes ----------

def ler_cache():
    try:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def gravar_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f, indent=1)


def marca(caminho):
    st = os.stat(caminho)
    base = f"{os.path.abspath(caminho)}|{st.st_size}|{int(st.st_mtime)}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def esperar_ativo(nome, aviso):
    for _ in range(240):
        info, _ = chamar("GET", f"{BASE}/v1beta/{nome}")
        estado = info.get("state", "ACTIVE")
        if estado == "ACTIVE":
            return info
        if estado == "FAILED":
            raise Erro(f"O Google não conseguiu processar {aviso}. Tente converter para MP4 (H.264) ou WAV.")
        time.sleep(3)
    raise Erro(f"O processamento de {aviso} demorou demais.")


def enviar(caminho):
    """Envia o arquivo e devolve {name, uri, mimeType}. Reaproveita o envio se ainda existir no Google."""
    cache = ler_cache()
    m = marca(caminho)
    antigo = cache.get(m)
    if antigo and time.time() - antigo.get("quando", 0) < 40 * 3600:
        try:
            info, _ = chamar("GET", f"{BASE}/v1beta/{antigo['name']}")
            if info.get("state", "ACTIVE") == "ACTIVE":
                return antigo
        except Erro:
            pass
    tamanho = os.path.getsize(caminho)
    tipo = tipo_de(caminho)
    nome_curto = os.path.basename(caminho)
    print(f"  enviando {nome_curto} ({tamanho / 1e6:.1f} MB)…", file=sys.stderr)
    _, cab = chamar(
        "POST", f"{BASE}/upload/v1beta/files",
        corpo={"file": {"display_name": nome_curto[:100]}},
        cabecalhos={
            "X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(tamanho),
            "X-Goog-Upload-Header-Content-Type": tipo,
        },
    )
    destino = cab.get("x-goog-upload-url")
    if not destino:
        raise Erro("O Google não devolveu o endereço de envio.")
    with open(caminho, "rb") as f:
        resp, _ = chamar(
            "POST", destino, corpo=f, espera=3600,
            cabecalhos={
                "Content-Length": str(tamanho), "Content-Type": tipo,
                "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize",
            },
        )
    arq = resp.get("file", resp)
    if arq.get("state") not in (None, "ACTIVE"):
        arq = esperar_ativo(arq["name"], nome_curto)
    item = {"name": arq["name"], "uri": arq["uri"], "mimeType": arq.get("mimeType", tipo),
            "quando": time.time(), "arquivo": os.path.abspath(caminho)}
    cache[m] = item
    gravar_cache(cache)
    return item


def parte_de_midia(caminho, a):
    if not os.path.isfile(caminho):
        raise Erro(f"Arquivo não encontrado: {caminho}")
    tipo = tipo_de(caminho)
    if tipo == "text/plain":
        with open(caminho, encoding="utf-8", errors="replace") as f:
            return {"text": f"--- {os.path.basename(caminho)} ---\n{f.read()}"}
    if os.path.getsize(caminho) <= LIMITE_EMBUTIDO and not tipo.startswith("video/"):
        import base64
        with open(caminho, "rb") as f:
            parte = {"inlineData": {"mimeType": tipo, "data": base64.b64encode(f.read()).decode("ascii")}}
    else:
        env = enviar(caminho)
        parte = {"fileData": {"mimeType": env["mimeType"], "fileUri": env["uri"]}}
    if tipo.startswith("video/"):
        meta = {}
        if a.fps:
            meta["fps"] = a.fps
        if a.inicio is not None:
            meta["startOffset"] = f"{a.inicio:g}s"
        if a.fim is not None:
            meta["endOffset"] = f"{a.fim:g}s"
        if meta:
            parte["videoMetadata"] = meta
    return parte


# ---------- comandos ----------

def cmd_modelos(a):
    url = f"{BASE}/v1beta/models?pageSize=200"
    linhas = []
    while True:
        r, _ = chamar("GET", url)
        for m in r.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                nome = m["name"].split("/", 1)[-1]
                linhas.append(f"{nome:42} entrada {m.get('inputTokenLimit', '?'):>9}  {m.get('displayName', '')}")
        prox = r.get("nextPageToken")
        if not prox:
            break
        url = f"{BASE}/v1beta/models?pageSize=200&pageToken={urllib.parse.quote(prox)}"
    print("\n".join(sorted(linhas)) or "Nenhum modelo disponível para esta chave.")
    print(f"\nModelo padrão deste script: {MODELO_PADRAO} (mude com --modelo ou com a variável GEMINI_MODELO).")


def perguntar(a, texto):
    partes = [parte_de_midia(c, a) for c in (a.midia or [])]
    partes.append({"text": texto})
    corpo = {"contents": [{"role": "user", "parts": partes}], "generationConfig": {}}
    if a.sistema:
        with open(a.sistema, encoding="utf-8") as f:
            corpo["systemInstruction"] = {"parts": [{"text": f.read()}]}
    if a.baixa:
        corpo["generationConfig"]["mediaResolution"] = "MEDIA_RESOLUTION_LOW"
    if a.json:
        corpo["generationConfig"]["responseMimeType"] = "application/json"
    if a.temperatura is not None:
        corpo["generationConfig"]["temperature"] = a.temperatura
    modelo = urllib.parse.quote(a.modelo, safe="")
    r, _ = chamar("POST", f"{BASE}/v1beta/models/{modelo}:generateContent", corpo=corpo, espera=900)
    cands = r.get("candidates") or []
    if not cands:
        motivo = (r.get("promptFeedback") or {}).get("blockReason", "sem motivo informado")
        raise Erro(f"O Gemini não respondeu (bloqueio: {motivo}).")
    resposta = "".join(p.get("text", "") for p in (cands[0].get("content") or {}).get("parts", [])
                       if not p.get("thought"))
    fim = cands[0].get("finishReason", "")
    if not resposta.strip():
        raise Erro(f"Resposta vazia (motivo: {fim or 'desconhecido'}).")
    uso = r.get("usageMetadata", {})
    return resposta, uso, fim


def cmd_perguntar(a):
    if a.arquivo_pergunta:
        with open(a.arquivo_pergunta, encoding="utf-8") as f:
            texto = f.read()
        if a.pergunta:
            texto += "\n\n" + a.pergunta
    elif a.pergunta:
        texto = a.pergunta
    else:
        raise Erro("Diga a pergunta com --pergunta ou --arquivo-pergunta.")
    resposta, uso, fim = perguntar(a, texto)
    if a.saida:
        os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
        with open(a.saida, "w", encoding="utf-8") as f:
            f.write(resposta)
        print(f"Resposta gravada em {a.saida}")
    else:
        print(resposta)
    print(f"[{a.modelo} · entrada {uso.get('promptTokenCount', '?')} tokens · "
          f"saída {uso.get('candidatesTokenCount', '?')} tokens]", file=sys.stderr)
    if fim == "MAX_TOKENS":
        print("Aviso: a resposta foi cortada no limite de tamanho. Peça menos coisa por vez.", file=sys.stderr)


def cmd_testar(a):
    a.midia, a.sistema, a.baixa, a.json, a.temperatura = [], None, False, False, None
    resposta, _, _ = perguntar(a, "Responda só com a palavra: funcionando")
    print(f"Chave e modelo ({a.modelo}) funcionando. Resposta: {resposta.strip()[:80]}")


def cmd_apagar(a):
    cache = ler_cache()
    n = 0
    for item in cache.values():
        try:
            chamar("DELETE", f"{BASE}/v1beta/{item['name']}")
            n += 1
        except Erro:
            pass  # já tinha expirado
    gravar_cache({})
    print(f"{n} arquivo(s) apagado(s) do Google. (O que sobrar some sozinho em cerca de 48 h.)")


def main():
    p = argparse.ArgumentParser(description="Segundo olhar com o Google Gemini.")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("testar", help="confere a chave e o modelo com uma pergunta mínima")
    t.add_argument("--modelo", default=MODELO_PADRAO)
    t.set_defaults(f=cmd_testar)

    m = sub.add_parser("modelos", help="lista os modelos que a chave pode usar")
    m.set_defaults(f=cmd_modelos)

    q = sub.add_parser("perguntar", help="faz uma pergunta, com ou sem mídia")
    q.add_argument("--pergunta", help="o texto da pergunta")
    q.add_argument("--arquivo-pergunta", help="arquivo de texto com a pergunta (melhor para perguntas longas)")
    q.add_argument("--midia", nargs="*", help="vídeos, áudios, imagens ou textos para o Gemini examinar")
    q.add_argument("--fps", type=float, help="quadros por segundo que o Gemini olha (padrão dele: 1; máximo: 24)")
    q.add_argument("--inicio", type=float, help="olhar o vídeo só a partir deste segundo")
    q.add_argument("--fim", type=float, help="olhar o vídeo só até este segundo")
    q.add_argument("--baixa", action="store_true", help="resolução baixa por quadro (gasta menos; ruim para ler texto)")
    q.add_argument("--json", action="store_true", help="pede a resposta em JSON")
    q.add_argument("--sistema", help="arquivo com a instrução de papel (ex.: 'você é um editor crítico')")
    q.add_argument("--temperatura", type=float)
    q.add_argument("--modelo", default=MODELO_PADRAO)
    q.add_argument("--saida", help="grava a resposta neste arquivo em vez de mostrar")
    q.set_defaults(f=cmd_perguntar)

    d = sub.add_parser("apagar", help="apaga do Google os arquivos enviados")
    d.set_defaults(f=cmd_apagar)

    a = p.parse_args()
    if getattr(a, "fps", None) is not None and not (0 < a.fps <= 24):
        p.error("--fps precisa ficar entre 0 e 24")
    try:
        a.f(a)
    except Erro as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
