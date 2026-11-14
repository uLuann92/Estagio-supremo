#!/usr/bin/env python3
"""Segundo olhar: pergunta ao Google Gemini, com ou sem mídia (vídeo, áudio, imagem).

Só usa a biblioteca padrão do Python (nada para instalar).
A chave fica na variável de ambiente GEMINI_API_KEY. Nunca em arquivo, nunca no chat.

Uso:
  gemini.py testar
  gemini.py modelos
  gemini.py perguntar --pergunta "..." [--midia clipe.mp4 ...] [--saida resposta.md]
  gemini.py perguntar --arquivo-pergunta pergunta.md --midia ref01.mp4 --fps 12 --inicio 10 --fim 25
  gemini.py perguntar --pergunta "..." --youtube https://www.youtube.com/watch?v=... --inicio 30 --fim 90
  gemini.py imagem --pedido "Remova o personagem e complete o fundo" --midia quadro.png --saida fundo.png
  gemini.py apagar            (apaga do Google os arquivos enviados por este script)

Se o modelo pedido estiver sobrecarregado ou sem cota, o script tenta sozinho os outros
modelos "flash" que a chave alcança, do mais novo para o mais antigo, e diz qual respondeu.

Como usar bem (1 fps por padrão, tempos aproximados, o que conferir): guias/segundo-olhar.md
"""
import argparse
import hashlib
import json
import mimetypes
import os
import re
import socket
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
    def __init__(self, msg, codigo=None):
        super().__init__(msg)
        self.codigo = codigo


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
            raise Erro(f"Gemini respondeu {e.code}: {msg[:400]}{dica}", e.code)
        except (socket.timeout, TimeoutError):
            raise Erro("O Gemini não respondeu a tempo.", "tempo")
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


def meta_de_video(a):
    meta = {}
    if getattr(a, "fps", None):
        meta["fps"] = a.fps
    if getattr(a, "inicio", None) is not None:
        meta["startOffset"] = f"{a.inicio:g}s"
    if getattr(a, "fim", None) is not None:
        meta["endOffset"] = f"{a.fim:g}s"
    return meta


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
        meta = meta_de_video(a)
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


def reservas(ja):
    """Outros modelos 'flash' estáveis que a chave alcança, do mais novo para o mais antigo."""
    try:
        r, _ = chamar("GET", f"{BASE}/v1beta/models?pageSize=200", espera=30)
    except Erro:
        return []
    achados = []
    for m in r.get("models", []):
        nome = m["name"].split("/", 1)[-1]
        v = re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-flash", nome)
        if v and "generateContent" in m.get("supportedGenerationMethods", []) and nome not in ja:
            achados.append((float(v.group(1)), nome))
    return [n for _, n in sorted(achados, reverse=True)]


def gerar(modelo, corpo, espera):
    """Uma pergunta a um modelo, por streaming (falha rápido se o modelo estiver sobrecarregado)."""
    url = f"{BASE}/v1beta/models/{urllib.parse.quote(modelo, safe='')}:streamGenerateContent?alt=sse"
    req = urllib.request.Request(
        url, data=json.dumps(corpo).encode("utf-8"), method="POST",
        headers={"x-goog-api-key": chave(), "Content-Type": "application/json"},
    )
    texto, uso, fim, versao, bloqueio = [], {}, "", modelo, None
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            for bruto in r:
                linha = bruto.decode("utf-8", "replace").strip()
                if not linha.startswith("data:"):
                    continue
                try:
                    obj = json.loads(linha[5:])
                except ValueError:
                    continue
                if "error" in obj:
                    raise Erro(f"Gemini: {obj['error'].get('message', '')[:400]}", obj["error"].get("code"))
                uso = obj.get("usageMetadata") or uso
                versao = obj.get("modelVersion") or versao
                bloqueio = (obj.get("promptFeedback") or {}).get("blockReason") or bloqueio
                for c in obj.get("candidates") or []:
                    fim = c.get("finishReason") or fim
                    for p in (c.get("content") or {}).get("parts", []):
                        if p.get("text") and not p.get("thought"):
                            texto.append(p["text"])
    except urllib.error.HTTPError as e:
        cru = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(cru)["error"]["message"]
        except Exception:
            msg = cru[:400]
        raise Erro(f"Gemini respondeu {e.code}: {msg[:400]}", e.code)
    except (socket.timeout, TimeoutError):
        raise Erro("O Gemini não respondeu a tempo.", "tempo")
    except urllib.error.URLError as e:
        raise Erro(f"Sem conexão com o Gemini: {e.reason}", "rede")
    resposta = "".join(texto)
    if not resposta.strip():
        if bloqueio:
            raise Erro(f"O Gemini não respondeu (bloqueio: {bloqueio}).")
        raise Erro(f"Resposta vazia (motivo: {fim or 'desconhecido'}).", "vazia")
    return resposta, uso, fim, versao


def perguntar(a, texto):
    partes = [parte_de_midia(c, a) for c in (a.midia or [])]
    for link in (getattr(a, "youtube", None) or []):
        parte = {"fileData": {"fileUri": link}}
        meta = meta_de_video(a)
        if meta:
            parte["videoMetadata"] = meta
        partes.append(parte)
    partes.append({"text": texto})
    corpo = {"contents": [{"role": "user", "parts": partes}], "generationConfig": {}}
    if a.sistema:
        with open(a.sistema, encoding="utf-8") as f:
            corpo["systemInstruction"] = {"parts": [{"text": f.read()}]}
    if a.baixa:
        corpo["generationConfig"]["mediaResolution"] = "MEDIA_RESOLUTION_LOW"
    elif getattr(a, "alta", False):
        corpo["generationConfig"]["mediaResolution"] = "MEDIA_RESOLUTION_HIGH"
    if a.json:
        corpo["generationConfig"]["responseMimeType"] = "application/json"
    if a.temperatura is not None:
        corpo["generationConfig"]["temperature"] = a.temperatura
    fila = [m.strip() for m in a.modelo.split(",") if m.strip()]
    bom = ler_cache().get("_ultimo_bom") or {}
    if a.modelo == MODELO_PADRAO and bom.get("modelo") and time.time() - bom.get("quando", 0) < 3600:
        # o modelo padrão falhou há pouco e outro respondeu: começa por ele, para não esperar de novo
        fila = [bom["modelo"]] + [m for m in fila if m != bom["modelo"]]
    tentados, ultimo, procurou = [], None, False
    while fila:
        modelo = fila.pop(0)
        tentados.append(modelo)
        for tentativa in range(2):
            try:
                resposta, uso, fim, versao = gerar(modelo, corpo, a.espera)
                if len(tentados) > 1:
                    print(f"  (respondeu: {modelo}; antes falharam: {', '.join(tentados[:-1])})", file=sys.stderr)
                    c = ler_cache()
                    c["_ultimo_bom"] = {"modelo": modelo, "quando": time.time()}
                    gravar_cache(c)
                return resposta, uso, fim, versao
            except Erro as e:
                ultimo = e
                if e.codigo in (500, 502, 503, 504, "rede") and tentativa == 0:
                    time.sleep(5)
                    continue
                break
        # passa para outro modelo só quando o problema é do modelo (sobrecarga, cota, sumiu)
        if ultimo.codigo not in (429, 404, 500, 502, 503, 504, "tempo", "vazia"):
            raise ultimo
        print(f"  {modelo}: {str(ultimo)[:110]}", file=sys.stderr)
        if not fila and not procurou:
            procurou = True
            fila = reservas(tentados)
    raise Erro(f"Nenhum modelo respondeu ({', '.join(tentados)}). Último erro: {ultimo}")


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
    resposta, uso, fim, versao = perguntar(a, texto)
    if a.saida:
        os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
        with open(a.saida, "w", encoding="utf-8") as f:
            f.write(resposta)
        print(f"Resposta gravada em {a.saida}")
    else:
        print(resposta)
    print(f"[{versao} · entrada {uso.get('promptTokenCount', '?')} tokens · "
          f"saída {uso.get('candidatesTokenCount', '?')} tokens]", file=sys.stderr)
    if fim == "MAX_TOKENS":
        print("Aviso: a resposta foi cortada no limite de tamanho. Peça menos coisa por vez.", file=sys.stderr)


def modelos_de_imagem():
    """Modelos que editam/geram imagem e que a chave alcança; os 'flash' primeiro, do mais novo ao mais antigo."""
    r, _ = chamar("GET", f"{BASE}/v1beta/models?pageSize=200", espera=30)
    achados = []
    for m in r.get("models", []):
        nome = m["name"].split("/", 1)[-1]
        v = re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-(flash|pro)-image", nome)
        if v and "generateContent" in m.get("supportedGenerationMethods", []):
            achados.append((v.group(2) == "flash", float(v.group(1)), nome))
    return [n for _, _, n in sorted(achados, reverse=True)]


def cmd_imagem(a):
    """Edita ou cria uma imagem. Precisa de plano pago: no gratuito, os modelos de imagem têm cota zero."""
    import base64
    partes = []
    for c in (a.midia or []):
        if not os.path.isfile(c):
            raise Erro(f"Arquivo não encontrado: {c}")
        with open(c, "rb") as f:
            partes.append({"inlineData": {"mimeType": tipo_de(c), "data": base64.b64encode(f.read()).decode("ascii")}})
    partes.append({"text": a.pedido})
    corpo = {"contents": [{"role": "user", "parts": partes}]}
    fila = [m.strip() for m in (a.modelo or "").split(",") if m.strip()] or modelos_de_imagem()
    if not fila:
        raise Erro("Nenhum modelo de imagem disponível para esta chave.")
    ultimo = None
    for modelo in fila:
        try:
            r, _ = chamar("POST", f"{BASE}/v1beta/models/{urllib.parse.quote(modelo, safe='')}:generateContent",
                          corpo=corpo, espera=a.espera)
        except Erro as e:
            ultimo = e
            print(f"  {modelo}: {str(e)[:110]}", file=sys.stderr)
            continue
        achou, falas = None, []
        for c in r.get("candidates") or []:
            for p in (c.get("content") or {}).get("parts", []):
                if p.get("inlineData", {}).get("data"):
                    achou = achou or p["inlineData"]
                elif p.get("text") and not p.get("thought"):
                    falas.append(p["text"])
        if not achou:
            ultimo = Erro(f"{modelo} não devolveu imagem. {' '.join(falas)[:200]}")
            print(f"  {ultimo}", file=sys.stderr)
            continue
        # o modelo escolhe o formato (muitas vezes JPEG): a extensão do arquivo acompanha o que veio
        ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(achou.get("mimeType"), "")
        saida = a.saida
        if ext and os.path.splitext(saida)[1].lower() not in ((ext, ".jpeg") if ext == ".jpg" else (ext,)):
            saida = os.path.splitext(saida)[0] + ext
        os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
        with open(saida, "wb") as f:
            f.write(base64.b64decode(achou["data"]))
        uso = r.get("usageMetadata", {})
        print(f"Imagem gravada em {saida}")
        print(f"[{modelo} · entrada {uso.get('promptTokenCount', '?')} tokens · "
              f"saída {uso.get('candidatesTokenCount', '?')} tokens]", file=sys.stderr)
        return
    raise Erro(f"Nenhum modelo de imagem respondeu. Último erro: {ultimo}")


def cmd_testar(a):
    a.alta = False
    a.midia, a.youtube, a.sistema, a.baixa, a.json, a.temperatura, a.espera = [], [], None, False, False, None, 40
    resposta, _, _, versao = perguntar(a, "Responda só com a palavra: funcionando")
    print(f"Chave funcionando. Quem respondeu: {versao}. Resposta: {resposta.strip()[:80]}")


def cmd_apagar(a):
    cache = ler_cache()
    n = 0
    for item in cache.values():
        if "name" not in item:
            continue
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
    q.add_argument("--youtube", nargs="*", help="links de vídeos públicos do YouTube (o Gemini assiste direto, sem baixar)")
    q.add_argument("--espera", type=int, default=600, help="segundos de espera por resposta, por tentativa")
    q.add_argument("--fps", type=float, help="quadros por segundo que o Gemini olha (padrão dele: 1; máximo: 24)")
    q.add_argument("--inicio", type=float, help="olhar o vídeo só a partir deste segundo")
    q.add_argument("--fim", type=float, help="olhar o vídeo só até este segundo")
    q.add_argument("--baixa", action="store_true", help="resolução baixa por quadro (gasta menos; ruim para ler texto)")
    q.add_argument("--alta", action="store_true",
                   help="resolução alta por quadro (gasta ~4x; para detalhe fino num trecho curto: tremida, texto pequeno)")
    q.add_argument("--json", action="store_true", help="pede a resposta em JSON")
    q.add_argument("--sistema", help="arquivo com a instrução de papel (ex.: 'você é um editor crítico')")
    q.add_argument("--temperatura", type=float)
    q.add_argument("--modelo", default=MODELO_PADRAO, help="um modelo, ou vários separados por vírgula (ordem de tentativa)")
    q.add_argument("--saida", help="grava a resposta neste arquivo em vez de mostrar")
    q.set_defaults(f=cmd_perguntar)

    g = sub.add_parser("imagem", help="edita ou cria uma imagem (plano pago)")
    g.add_argument("--pedido", required=True, help="o que fazer com a imagem, em uma instrução clara")
    g.add_argument("--midia", nargs="*", help="imagem(ns) de entrada")
    g.add_argument("--saida", required=True, help="arquivo de saída (.png)")
    g.add_argument("--modelo", default=os.environ.get("GEMINI_MODELO_IMAGEM", ""),
                   help="modelo de imagem; vazio = o mais novo que a chave alcança")
    g.add_argument("--espera", type=int, default=300)
    g.set_defaults(f=cmd_imagem)

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
