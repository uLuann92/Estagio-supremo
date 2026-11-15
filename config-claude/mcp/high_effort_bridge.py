"""Ponte MCP Claude Code <-> Gemini (duplo pensamento e trabalho pesado direto no disco).

Precisa de: pip install mcp google-genai
A chave vem da variável de ambiente GEMINI_API_KEY (nunca escrita em arquivo).

Variáveis opcionais:
  BRAIN_MODEL_ID   modelo(s) preferido(s), separados por vírgula. Padrão: gemini-4-carbon,gemini-pro-latest,gemini-flash-latest
                   (o gemini-4-argon só entra quando a chamada passa model_id="gemini-4-argon", para tarefa mecânica)
  BRAIN_BASE_URL   endereço alternativo da API (proxy/roteador)
  BRAIN_ROOTS      pastas onde a ponte pode gravar, separadas por ; ou : (padrão: a pasta de trabalho atual)
"""
import ast
import glob
import json
import os
import re
import shutil
import time

from google import genai
from google.genai import types
try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Gemini-DualBrain")

API_KEY = os.environ.get("GEMINI_API_KEY")
CUSTOM_BASE_URL = os.environ.get("BRAIN_BASE_URL")
DEFAULT_MODEL = "gemini-4-carbon"
MODELOS = [m.strip() for m in os.environ.get(
    "BRAIN_MODEL_ID", f"{DEFAULT_MODEL},gemini-pro-latest,gemini-flash-latest").split(",") if m.strip()]

_client = None
ACTIVE_CACHES = {}

MIDIA = {".mp4", ".mkv", ".mov", ".webm", ".mp3", ".wav", ".flac", ".m4a", ".png", ".jpg", ".jpeg", ".webp", ".pdf"}
# nunca saem do computador, mesmo que alguém peça
SEGREDOS = re.compile(r"(^|[\\/])(\.env(\..*)?|.*\.pem|.*\.key|id_rsa.*|id_ed25519.*|credentials.*|.*\.p12|.*\.pfx|"
                      r"\.npmrc|\.netrc|secrets?\..*)$", re.I)
LIMITE_TEXTO = 1_500_000  # caracteres por arquivo de texto


def client():
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError("Falta a variável de ambiente GEMINI_API_KEY.")
        # v1beta: é onde a API aceita instrução de sistema, busca do Google e nível de raciocínio juntos
        opts = {"base_url": CUSTOM_BASE_URL} if CUSTOM_BASE_URL else {"api_version": "v1beta"}
        _client = genai.Client(api_key=API_KEY, http_options=opts)
    return _client


def fila_de_modelos(pedido: str = ""):
    return ([pedido] if pedido else []) + [m for m in MODELOS if m != pedido]


def gerar(contents, config_kwargs, model_id="", effort_level="HIGH", espera=300, fila=None):
    """Tenta cada modelo da fila, com raciocínio alto por padrão.
    Passa para o próximo modelo em sobrecarga, falta de cota ou modelo inexistente."""
    ultimo, erros = None, []
    for modelo in (fila or fila_de_modelos(model_id)):
        cfg = dict(config_kwargs)
        cfg["http_options"] = types.HttpOptions(timeout=int(espera * 1000))  # sem limite, uma chamada pode ficar presa
        t = thinking(effort_level) if effort_level else None
        if t is not None and "thinking_config" not in cfg:
            cfg["thinking_config"] = t
        for tentativa in range(3):
            try:
                r = client().models.generate_content(
                    model=modelo, contents=contents, config=types.GenerateContentConfig(**cfg))
                if not (r.text or "").strip():
                    raise RuntimeError("resposta vazia")
                return modelo, r
            except Exception as e:  # noqa: BLE001 - a SDK levanta tipos diferentes por versão
                ultimo = e
                codigo = getattr(e, "code", None) or getattr(e, "status_code", None)
                if "thinking" in str(e).lower() and "thinking_config" in cfg:
                    cfg.pop("thinking_config")  # este modelo não aceita o nível pedido: segue sem
                    continue
                if codigo in (500, 502, 503, 504) and tentativa == 0:
                    time.sleep(4)
                    continue
                erros.append(f"{modelo}: {str(e)[:160]}")
                break
    raise RuntimeError("Nenhum modelo respondeu. " + " | ".join(erros or [str(ultimo)]))


def thinking(effort_level: str):
    try:
        return types.ThinkingConfig(include_thoughts=False, thinking_level=effort_level.upper())
    except Exception:  # noqa: BLE001
        return None


def expandir(padroes):
    achados = []
    for p in padroes:
        p = os.path.expanduser(p)
        itens = sorted(glob.glob(p, recursive=True)) or ([p] if os.path.exists(p) else [])
        for c in itens:
            if os.path.isdir(c):
                for raiz, pastas, nomes in os.walk(c):
                    pastas[:] = [d for d in pastas if d not in (".git", "node_modules", "__pycache__", ".venv", "dist", "build")]
                    achados += [os.path.join(raiz, n) for n in sorted(nomes)]
            elif os.path.isfile(c):
                achados.append(c)
    vistos, unicos = set(), []
    for c in achados:
        r = os.path.realpath(c)
        if r not in vistos:
            vistos.add(r)
            unicos.append(c)
    return unicos


def montar_partes(caminhos):
    """Lê os arquivos do disco. Devolve (partes para o Gemini, relatório de uma linha por arquivo)."""
    partes, relato = [], []
    for c in caminhos:
        if SEGREDOS.search(c):
            relato.append(f"RECUSADO (parece segredo): {c}")
            continue
        ext = os.path.splitext(c)[1].lower()
        if ext in MIDIA:
            f = client().files.upload(file=c)
            while f.state.name == "PROCESSING":
                time.sleep(2)
                f = client().files.get(name=f.name)
            if f.state.name != "ACTIVE":
                relato.append(f"FALHOU no processamento: {c}")
                continue
            partes.append(f)
            relato.append(f"mídia: {c}")
        else:
            try:
                with open(c, "r", encoding="utf-8", errors="replace") as fh:
                    texto = fh.read(LIMITE_TEXTO + 1)
            except OSError as e:
                relato.append(f"ILEGÍVEL: {c} ({e})")
                continue
            cortado = len(texto) > LIMITE_TEXTO
            numerado = "\n".join(f"{i + 1:>5}| {l}" for i, l in enumerate(texto[:LIMITE_TEXTO].split("\n")))
            partes.append(f"--- ARQUIVO: {c} (linhas numeradas à esquerda; os números não fazem parte do arquivo) ---\n{numerado}")
            relato.append(f"texto: {c} ({texto.count(chr(10)) + 1} linhas{', CORTADO' if cortado else ''})")
    return partes, relato


def pode_gravar(caminho: str) -> bool:
    raizes = [r for r in re.split(r"[;:](?![\\/])", os.environ.get("BRAIN_ROOTS", "")) if r] or [os.getcwd()]
    alvo = os.path.realpath(caminho)
    return any(os.path.commonpath([alvo, os.path.realpath(os.path.expanduser(r))]) == os.path.realpath(os.path.expanduser(r))
               for r in raizes if os.path.splitdrive(alvo)[0] == os.path.splitdrive(os.path.realpath(os.path.expanduser(r)))[0])


def assinaturas(caminho: str, codigo: str):
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".py":
        try:
            arv = ast.parse(codigo)
        except SyntaxError as e:
            return [], f"ERRO DE SINTAXE na linha {e.lineno}: {e.msg}"
        sai = []
        for n in ast.walk(arv):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sai.append(f"L{n.lineno}: def {n.name}({ast.unparse(n.args)})")
            elif isinstance(n, ast.ClassDef):
                sai.append(f"L{n.lineno}: class {n.name}")
        return sorted(sai, key=lambda s: int(s[1:s.index(':')])), "sintaxe Python ok"
    if ext == ".json":
        try:
            json.loads(codigo)
            return [], "JSON válido"
        except ValueError as e:
            return [], f"JSON INVÁLIDO: {e}"
    padrao = re.compile(
        r"^\s*(export\s+(default\s+)?)?(async\s+)?(function\s+\w+\s*\([^)]*\)|class\s+\w+|const\s+\w+\s*=\s*(async\s*)?\([^)]*\)\s*=>|"
        r"(void|float|vec[234]|mat[234]|int|bool)\s+\w+\s*\([^)]*\)|fn\s+\w+\s*\([^)]*\)|func\s+\w+\s*\([^)]*\))", re.M)
    sai = []
    for m in padrao.finditer(codigo):
        linha = codigo.count("\n", 0, m.start()) + 1
        sai.append(f"L{linha}: {m.group(0).strip()[:110]}")
    return sai, "sintaxe não conferida (rode o verificador da linguagem)"


@mcp.tool()
def check_active_models() -> str:
    """Lista os modelos que a chave alcança. Estar na lista não garante cota: teste com uma pergunta curta."""
    nomes = [m.name.replace("models/", "") for m in client().models.list()]
    return "Fila configurada: " + ", ".join(MODELOS) + "\nModelos na chave:\n" + "\n".join(f"- {n}" for n in nomes)


@mcp.tool()
def cache_heavy_context(cache_name: str, file_paths: list[str], model_id: str = "", ttl_minutes: int = 60) -> str:
    """Sobe vídeos, áudios e código para o cache de contexto do Gemini, para várias perguntas sobre o mesmo material.
    O cache vive só enquanto este servidor estiver rodando e até o prazo (ttl). Nem todo modelo aceita cache."""
    partes, relato = montar_partes(expandir(file_paths))
    if not partes:
        return "Nada para colocar no cache.\n" + "\n".join(relato)
    ultimo = None
    for modelo in fila_de_modelos(model_id):
        try:
            cache = client().caches.create(model=modelo, config=types.CreateCachedContentConfig(
                contents=partes, ttl=f"{ttl_minutes * 60}s",
                system_instruction="Você analisa mídia e código para um editor de vídeo e desenvolvedor. "
                                   "Tempos que você citar são aproximados; diga quando não tiver certeza."))
            ACTIVE_CACHES[cache_name] = (cache.name, modelo)
            return f"Cache '{cache_name}' ativo no modelo {modelo}.\n" + "\n".join(relato)
        except Exception as e:  # noqa: BLE001
            ultimo = e
    return f"Não consegui criar o cache: {ultimo}"


@mcp.tool()
def dual_think_high_effort(prompt: str, cache_name: str = "", model_id: str = "", effort_level: str = "HIGH") -> str:
    """Segundo pensamento do Gemini sobre um plano, um bug ou uma decisão. A resposta é opinião a conferir, não ordem."""
    cfg = {"temperature": 0.2}
    if cache_name in ACTIVE_CACHES:
        cfg["cached_content"], model_id = ACTIVE_CACHES[cache_name]
    modelo, r = gerar(prompt, cfg, model_id, effort_level)
    return f"[Modelo: {modelo}]\n\n{r.text}"


@mcp.tool()
def gemini_direct_file_worker(task_prompt: str, input_files: list[str] | None = None, output_file: str = "",
                              model_id: str = "", overwrite: bool = False) -> str:
    """Trabalho pesado direto no disco: o Gemini lê os arquivos locais e grava o resultado, sem passar pelo Claude.

    task_prompt: instrução detalhada do que criar, refatorar, resumir ou localizar.
    input_files: arquivos, pastas ou padrões (glob) lidos direto do disco por este script (texto, vídeo, áudio, imagem).
    output_file: se dado, o conteúdo gerado é gravado aqui e só volta um resumo curto com as assinaturas.
                 Se o arquivo já existir, exige overwrite=True e guarda uma cópia .bak.
                 Sem output_file, volta a resposta do Gemini (resumo, análise, localização do bug).
    """
    caminhos = expandir(input_files or [])
    partes, relato = montar_partes(caminhos)
    faltando = [p for p in (input_files or []) if not expandir([p])]
    if faltando:
        return "Arquivo(s) não encontrado(s): " + ", ".join(faltando)

    if not output_file:
        instr = ("Responda em português, direto. Quando apontar código, cite arquivo e número de linha. "
                 "No máximo ~60 linhas, salvo se a tarefa pedir mais.\n\nTAREFA:\n" + task_prompt)
        modelo, r = gerar(partes + [instr], {"temperature": 0.2}, model_id)
        return f"[Modelo: {modelo}]\nLidos: {len(relato)} arquivo(s)\n" + "\n".join(relato[:20]) + f"\n\n{r.text}"

    destino = os.path.abspath(os.path.expanduser(output_file))
    if SEGREDOS.search(destino) or not pode_gravar(destino):
        return f"RECUSADO: {destino} está fora das pastas permitidas (BRAIN_ROOTS ou a pasta de trabalho) ou parece arquivo de segredo."
    if os.path.exists(destino) and not overwrite:
        return f"RECUSADO: {destino} já existe. Passe overwrite=True para substituir (fica uma cópia .bak)."

    instr = (
        "Você vai escrever UM arquivo completo, pronto para uso, sem trechos omitidos nem '...'.\n"
        f"Caminho do arquivo: {destino}\n\n"
        "Formato OBRIGATÓRIO da resposta, nesta ordem:\n"
        "<<<ARQUIVO>>>\n(o conteúdo integral do arquivo, sem cercas de markdown)\n<<<FIM>>>\n"
        "<<<RESUMO>>>\n(até 10 linhas em português: o que foi feito, decisões tomadas, dependências, o que NÃO foi feito "
        "ou ficou incerto, e o que o revisor deve conferir primeiro)\n<<<FIM>>>\n\n"
        "TAREFA:\n" + task_prompt)
    modelo, r = gerar(partes + [instr], {"temperature": 0.2, "max_output_tokens": 65000}, model_id)
    texto = r.text or ""
    fim = ""
    try:
        fim = str(r.candidates[0].finish_reason)
    except Exception:  # noqa: BLE001
        pass
    m = re.search(r"<<<ARQUIVO>>>\r?\n(.*?)\r?\n?<<<FIM>>>", texto, re.S)
    if not m or "MAX_TOKENS" in fim:
        return (f"[Modelo: {modelo}] NADA FOI GRAVADO: a resposta veio "
                f"{'cortada no limite de tamanho' if 'MAX_TOKENS' in fim else 'fora do formato'}. "
                "Divida a tarefa em arquivos menores.\nInício da resposta:\n" + texto[:600])
    codigo = m.group(1)
    codigo = re.sub(r"\A```[\w+-]*\r?\n", "", codigo)
    codigo = re.sub(r"\r?\n```\s*\Z", "", codigo)
    if not codigo.endswith("\n"):
        codigo += "\n"
    s = re.search(r"<<<RESUMO>>>\r?\n(.*?)(\r?\n<<<FIM>>>|\Z)", texto, re.S)
    resumo = "\n".join((s.group(1).strip() if s else "(o modelo não mandou resumo)").split("\n")[:10])

    copia = ""
    if os.path.exists(destino):
        copia = destino + ".bak"
        shutil.copy2(destino, copia)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(codigo)
    sigs, sintaxe = assinaturas(destino, codigo)
    alerta = ""
    if re.search(r"^\s*(#|//)\s*\.\.\.|resto do (código|arquivo)|rest of (the )?(code|file)|TODO: implement", codigo, re.I | re.M):
        alerta = "\nALERTA: o arquivo parece ter trechos omitidos ou por implementar. Confira antes de usar."
    return (f"[Modelo: {modelo}] Gravado: {destino} ({codigo.count(chr(10))} linhas)"
            + (f" · cópia do anterior: {copia}" if copia else "")
            + f"\nLidos: {len(relato)} arquivo(s). Conferência: {sintaxe}{alerta}\n\nRESUMO:\n{resumo}\n\nASSINATURAS:\n"
            + ("\n".join(sigs[:40]) if sigs else "(nenhuma detectada)")
            + "\n\nNÃO REVISADO: audite com git diff ou lendo os trechos críticos, e rode o código antes de confiar.")


PESQUISADOR = """Você é um pesquisador especialista em animes, mangás, manhwas, jogos e engenharia. Use a busca na web.

Quando o pedido for sobre um personagem, uma obra ou uma luta, entregue um dossiê em Markdown com:
1. Lista cronológica dos eventos relevantes.
2. Poderes e técnicas, com os nomes exatos (original e tradução usual em português).
3. Citações marcantes: no máximo uma frase curta por cena, em paráfrase ou com poucas palavras entre aspas, com a fonte.
4. Episódios do anime onde cada cena acontece, com o número exato e a minutagem aproximada.
5. Capítulos do mangá/manhwa onde ficam os quadros mais icônicos, com o número exato (e o volume, se achar).
6. Tags correspondentes no Sakugabooru (nome da obra, do personagem e dos animadores, no formato de tag do site).

Regras de honestidade (valem mais que a completude):
- Número de episódio, capítulo, volume ou minutagem só entra se uma fonte encontrada na busca o sustenta. Sem fonte, escreva "não confirmado". Nunca complete de memória sem avisar.
- Quando as fontes divergem, mostre as duas versões.
- Separe o que é do mangá do que é só do anime ou de filme.

Formato: comece SEMPRE com a seção "## Resumo executivo" (até 12 linhas, com os números mais úteis). Depois, o dossiê completo. Responda em português do Brasil."""


def fontes_da_busca(r):
    """Títulos e endereços das páginas que a busca usou, sem repetição."""
    vistos, fontes = set(), []
    try:
        meta = r.candidates[0].grounding_metadata
        for ch in (meta.grounding_chunks or []) if meta else []:
            web = getattr(ch, "web", None)
            if web and web.uri and web.uri not in vistos:
                vistos.add(web.uri)
                fontes.append((web.title or "fonte", web.uri))
    except Exception:  # noqa: BLE001
        pass
    return fontes


@mcp.tool()
def carbon_web_research(query: str, save_report_to: str = "", model_id: str = "") -> str:
    """Pesquisa na web com o Gemini (busca do Google ligada) e monta um dossiê: eventos, técnicas, episódios,
    capítulos e tags do Sakugabooru de um personagem, obra ou luta; ou pesquisa técnica de engenharia e jogos.

    query: o que pesquisar, com o máximo de contexto (obra, personagem, cena, o que se quer achar).
    save_report_to: se dado, grava o dossiê completo em Markdown neste caminho (com as fontes no fim) e
                    devolve só o resumo executivo. Não sobrescreve: se o arquivo existir, grava _v02, _v03…
    """
    cfg = {"temperature": 0.2, "system_instruction": PESQUISADOR,
           "tools": [types.Tool(google_search=types.GoogleSearch())]}
    # Medido: carbon + busca + raciocínio alto pode passar de 3 min numa pergunta curta. Ordem das tentativas:
    # carbon em raciocínio alto (até 8 min) -> carbon no nível padrão dele (até 5 min) -> a fila de reserva.
    principal = model_id or DEFAULT_MODEL
    nivel = "HIGH"
    try:
        modelo, r = gerar(query, cfg, effort_level="HIGH", espera=480, fila=[principal])
    except Exception:  # noqa: BLE001
        try:
            nivel = "padrão do modelo (o nível alto estourou o tempo)"
            modelo, r = gerar(query, cfg, effort_level="", espera=300, fila=[principal])
        except Exception:  # noqa: BLE001
            nivel = "padrão (reserva: o modelo principal não respondeu)"
            modelo, r = gerar(query, cfg, model_id, effort_level="", espera=300)
    texto = (r.text or "").strip()
    fontes = fontes_da_busca(r)
    bloco = "\n\n## Fontes consultadas\n" + ("\n".join(f"- [{t}]({u})" for t, u in fontes) if fontes else
                                            "- (a busca não devolveu a lista de fontes: trate os números como não conferidos)")
    aviso = "" if fontes else "\nATENÇÃO: sem lista de fontes; confira os números antes de usar."
    if not save_report_to:
        return f"[Modelo: {modelo} · raciocínio: {nivel} · {len(fontes)} fonte(s)]{aviso}\n\n{texto}{bloco}"
    destino = os.path.abspath(os.path.expanduser(save_report_to))
    if SEGREDOS.search(destino) or not pode_gravar(destino):
        return f"RECUSADO: {destino} está fora das pastas permitidas (BRAIN_ROOTS ou a pasta de trabalho)."
    base, ext = os.path.splitext(destino)
    n = 2
    while os.path.exists(destino):
        destino = f"{base}_v{n:02d}{ext or '.md'}"
        n += 1
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"<!-- pesquisa: {query[:300]} · modelo: {modelo} -->\n\n{texto}{bloco}\n")
    m = re.search(r"##\s*Resumo executivo\s*\n(.*?)(\n##\s|\Z)", texto, re.S | re.I)
    resumo = "\n".join((m.group(1).strip() if m else texto[:900]).split("\n")[:14])
    return (f"[Modelo: {modelo} · raciocínio: {nivel}] Dossiê gravado: {destino} ({texto.count(chr(10)) + 1} linhas, {len(fontes)} fonte(s)){aviso}"
            f"\n\nRESUMO EXECUTIVO:\n{resumo}\n\nNÃO CONFERIDO: números de capítulo e episódio vêm da busca; "
            "confira os que forem usados.")


if __name__ == "__main__":
    mcp.run()
