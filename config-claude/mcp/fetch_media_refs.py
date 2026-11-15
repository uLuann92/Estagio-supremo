#!/usr/bin/env python3
""" Utilitário de linha de comando para buscar material de referência de estudo
de animação e metadados de obras (Sakugabooru, MangaDex e Jikan/MyAnimeList).

REGRA FIXA: este script NÃO baixa páginas de capítulos de mangá (nem pelo
endpoint at-home do MangaDex nem por qualquer outro site). Do MangaDex ele só
usa dados (títulos, numeração de capítulos) e capas. Os cortes do Sakugabooru
são referência de estudo de animação, com crédito guardado; usar esse material
num vídeo publicado é decisão e responsabilidade do usuário.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "media-refs/1.0"
TIMEOUT_SEGUNDOS = 30
INTERVALO_SITE_SEGUNDOS = 1.0
ESPERA_RETRY_SEGUNDOS = 5.0
TAMANHO_BLOCO_BYTES = 256 * 1024

TIPOS_TAG_SAKUGA = {
    0: "geral",
    1: "artista",
    3: "copyright/obra",
    4: "personagem",
}

_ULTIMO_PEDIDO_POR_SITE = {}


class _ArgumentParserPortugues(argparse.ArgumentParser):
    """Analisador de argumentos que relata erros em português e sai com código 1."""

    def error(self, message):
        """Imprime o uso, exibe mensagem de erro em português e encerra com código 1."""
        self.print_usage(sys.stderr)
        print(f"Erro nos argumentos: {message}", file=sys.stderr)
        sys.exit(1)


def _erro(mensagem):
    """Exibe mensagem de erro clara na saída de erro e encerra com código 1."""
    print(f"Erro: {mensagem}", file=sys.stderr)
    sys.exit(1)


def _agora_iso():
    """Retorna o horário atual em UTC no formato ISO 8601."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _chave_site(url):
    """Extrai o domínio base da URL para aplicar espera entre pedidos ao mesmo site."""
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    partes = [p for p in host.split(".") if p]
    if len(partes) >= 2:
        return ".".join(partes[-2:])
    return host


def _aguardar_intervalo_site(url):
    """Aguarda até completar 1 segundo desde o último pedido feito ao mesmo site."""
    site = _chave_site(url)
    ultimo = _ULTIMO_PEDIDO_POR_SITE.get(site)
    if ultimo is not None:
        restante = INTERVALO_SITE_SEGUNDOS - (time.monotonic() - ultimo)
        if restante > 0:
            time.sleep(restante)
    _ULTIMO_PEDIDO_POR_SITE[site] = time.monotonic()


def _marcar_fim_pedido(url):
    """Registra o instante de conclusão de um pedido HTTP para controle de intervalo."""
    _ULTIMO_PEDIDO_POR_SITE[_chave_site(url)] = time.monotonic()


def _abrir_url(url, aceitar_json=False):
    """Abre uma URL com User-Agent, timeout de 30 s e uma nova tentativa em 429/5xx."""
    cabecalhos = {"User-Agent": USER_AGENT}
    if aceitar_json:
        cabecalhos["Accept"] = "application/json"

    for tentativa in range(2):
        _aguardar_intervalo_site(url)
        requisicao = urllib.request.Request(url, headers=cabecalhos, method="GET")
        try:
            resposta = urllib.request.urlopen(requisicao, timeout=TIMEOUT_SEGUNDOS)
            _marcar_fim_pedido(url)
            return resposta
        except urllib.error.HTTPError as exc:
            _marcar_fim_pedido(url)
            repetivel = exc.code == 429 or 500 <= exc.code <= 599
            if repetivel and tentativa == 0:
                print(
                    f"Aviso: HTTP {exc.code} ao acessar {url}. "
                    f"Aguardando {ESPERA_RETRY_SEGUNDOS:g} s para tentar novamente...",
                    file=sys.stderr,
                )
                time.sleep(ESPERA_RETRY_SEGUNDOS)
                continue
            _erro(f"Falha HTTP {exc.code} ({exc.reason}) ao acessar {url}")
        except urllib.error.URLError as exc:
            _marcar_fim_pedido(url)
            _erro(f"Falha de conexão ao acessar {url}: {exc.reason}")
        except TimeoutError:
            _marcar_fim_pedido(url)
            _erro(f"Tempo limite de {TIMEOUT_SEGUNDOS} s excedido ao acessar {url}")

    _erro(f"Não foi possível concluir o pedido para {url}")


def pedir_json(url):
    """Realiza um pedido HTTP GET e retorna a estrutura JSON decodificada."""
    try:
        with _abrir_url(url, aceitar_json=True) as resposta:
            corpo = resposta.read()
        _marcar_fim_pedido(url)
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        _erro(f"Erro ao ler resposta de {url}: {exc}")

    try:
        texto = corpo.decode("utf-8")
        return json.loads(texto)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _erro(f"Resposta JSON inválida recebida de {url}: {exc}")


def baixar(url, destino, max_mb=None):
    """Baixa um arquivo em blocos de 256 KB sem sobrescrever arquivos já existentes."""
    if os.path.exists(destino):
        print(f"Aviso: arquivo já existe, pulando: {destino}")
        return False

    pasta_destino = os.path.dirname(os.path.abspath(destino))
    try:
        os.makedirs(pasta_destino, exist_ok=True)
    except OSError as exc:
        _erro(f"Não foi possível criar o diretório '{pasta_destino}': {exc}")

    limite_bytes = int(max_mb * 1024 * 1024) if max_mb is not None else None
    caminho_parcial = f"{destino}.part"
    concluido = False

    try:
        with _abrir_url(url) as resposta:
            tamanho_cabecalho = resposta.headers.get("Content-Length")
            if limite_bytes is not None and tamanho_cabecalho and tamanho_cabecalho.isdigit():
                bytes_remotos = int(tamanho_cabecalho)
                if bytes_remotos > limite_bytes:
                    mb_remoto = bytes_remotos / (1024 * 1024)
                    print(
                        f"Aviso: arquivo remoto ({mb_remoto:.2f} MB) passa do limite "
                        f"de {max_mb:g} MB; pulando: {url}"
                    )
                    _marcar_fim_pedido(url)
                    return False

            bytes_lidos = 0
            with open(caminho_parcial, "wb") as arquivo_saida:
                while True:
                    bloco = resposta.read(TAMANHO_BLOCO_BYTES)
                    if not bloco:
                        break
                    bytes_lidos += len(bloco)
                    if limite_bytes is not None and bytes_lidos > limite_bytes:
                        print(
                            f"Aviso: download ultrapassou {max_mb:g} MB; "
                            f"interrompendo e pulando: {url}"
                        )
                        _marcar_fim_pedido(url)
                        return False
                    arquivo_saida.write(bloco)

        _marcar_fim_pedido(url)

        if os.path.exists(destino):
            print(f"Aviso: arquivo já existe, pulando: {destino}")
            return False

        os.replace(caminho_parcial, destino)
        concluido = True
        return True
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        _erro(f"Falha ao baixar '{url}' para '{destino}': {exc}")
    finally:
        if not concluido and os.path.exists(caminho_parcial):
            try:
                os.remove(caminho_parcial)
            except OSError:
                pass


def registrar_credito(pasta, item):
    """Acrescenta um registro em creditos.json na pasta informada sem duplicar id_unico."""
    if not isinstance(item, dict) or not item.get("id_unico"):
        _erro("Registro de crédito inválido: campo 'id_unico' ausente.")

    try:
        os.makedirs(pasta, exist_ok=True)
    except OSError as exc:
        _erro(f"Não foi possível criar a pasta '{pasta}': {exc}")

    caminho_creditos = os.path.join(pasta, "creditos.json")
    lista_creditos = []

    if os.path.exists(caminho_creditos):
        try:
            with open(caminho_creditos, "r", encoding="utf-8") as arq:
                conteudo = arq.read().strip()
                if conteudo:
                    lista_creditos = json.loads(conteudo)
        except (OSError, json.JSONDecodeError) as exc:
            _erro(f"Não foi possível ler '{caminho_creditos}': {exc}")

        if not isinstance(lista_creditos, list):
            _erro(f"Conteúdo inválido em '{caminho_creditos}': esperava-se uma lista JSON.")

    id_novo = item["id_unico"]
    for registro in lista_creditos:
        if isinstance(registro, dict) and registro.get("id_unico") == id_novo:
            return

    lista_creditos.append(item)
    caminho_temp = f"{caminho_creditos}.tmp"
    try:
        with open(caminho_temp, "w", encoding="utf-8") as arq:
            json.dump(lista_creditos, arq, ensure_ascii=False, indent=2)
            arq.write("\n")
        os.replace(caminho_temp, caminho_creditos)
    except OSError as exc:
        if os.path.exists(caminho_temp):
            try:
                os.remove(caminho_temp)
            except OSError:
                pass
        _erro(f"Não foi possível gravar '{caminho_creditos}': {exc}")


def _sanitizar_segmento(valor):
    """Substitui caracteres inseguros para formação de nomes de arquivo locais."""
    limpo = re.sub(r"[^a-zA-Z0-9._-]", "_", str(valor).strip())
    return limpo or "indefinido"


def _normalizar_url_sakuga(url_arquivo):
    """Garante esquema e domínio completos em URLs retornadas pelo Sakugabooru."""
    if not url_arquivo:
        return ""
    if url_arquivo.startswith("//"):
        return f"https:{url_arquivo}"
    if url_arquivo.startswith("/"):
        return f"https://www.sakugabooru.com{url_arquivo}"
    return url_arquivo


def _extrair_extensao(url_ou_nome, padrao="bin"):
    """Extrai e limpa a extensão de arquivo a partir de uma URL ou nome de arquivo."""
    caminho = urllib.parse.urlsplit(url_ou_nome).path
    ext = os.path.splitext(caminho)[1].lstrip(".").lower()
    ext = re.sub(r"[^a-z0-9]", "", ext)
    return ext or padrao


def _extrair_titulo_mangadex(atributos):
    """Obtém o título do mangá priorizando pt-br, en ou o primeiro idioma disponível."""
    titulos = atributos.get("title") or {}
    alt_titulos = atributos.get("altTitles") or []

    for idioma in ("pt-br", "en"):
        if isinstance(titulos, dict) and titulos.get(idioma):
            return titulos[idioma]
        for alt in alt_titulos:
            if isinstance(alt, dict) and alt.get(idioma):
                return alt[idioma]

    if isinstance(titulos, dict):
        for valor in titulos.values():
            if valor:
                return valor

    for alt in alt_titulos:
        if isinstance(alt, dict):
            for valor in alt.values():
                if valor:
                    return valor

    return "(sem título)"


def _chave_ordem_numerica(texto):
    """Produz chave de ordenação numérica crescente mantendo valores não numéricos ao final."""
    texto_str = str(texto)
    try:
        return (0, float(texto_str), texto_str)
    except ValueError:
        return (1, 0.0, texto_str)


def cmd_sakuga(args):
    """Busca posts de estudo no Sakugabooru, exibe metadados e baixa os cortes."""
    tags_limpas = " ".join((args.tags or "").split())
    if not tags_limpas:
        _erro("Informe ao menos uma tag em --tags.")
    if args.limite <= 0:
        _erro("O valor de --limite deve ser maior que zero.")
    if args.tamanho_max_mb <= 0:
        _erro("O valor de --tamanho-max-mb deve ser maior que zero.")

    limite = args.limite
    if limite > 20:
        print(f"Aviso: o limite máximo é 20 (informado: {limite}); reduzindo para 20.")
        limite = 20

    tags_codificadas = urllib.parse.quote_plus(tags_limpas)
    url = f"https://www.sakugabooru.com/post.json?tags={tags_codificadas}&limit={limite}"
    posts = pedir_json(url)

    if not isinstance(posts, list):
        _erro("Formato inesperado na resposta de posts do Sakugabooru.")
    if not posts:
        print("Nenhum post encontrado no Sakugabooru para as tags informadas.")
        return

    for post in posts:
        if not isinstance(post, dict):
            continue
        post_id = post.get("id")
        tags_brutas = post.get("tags") or ""
        lista_tags = tags_brutas.split() if isinstance(tags_brutas, str) else [str(t) for t in tags_brutas]
        tags_resumo = " ".join(lista_tags[:12])
        origem = post.get("source") or "(sem fonte)"
        autor = post.get("author") or ""
        tamanho_bytes = post.get("file_size") or 0
        tamanho_mb = tamanho_bytes / (1024 * 1024) if isinstance(tamanho_bytes, (int, float)) else 0.0
        pagina = f"https://www.sakugabooru.com/post/show/{post_id}"

        print(f"[{post_id}] {tamanho_mb:.2f} MB | Fonte: {origem}")
        print(f"  Tags (até 12): {tags_resumo}")
        print(f"  Página: {pagina}")

        if args.so_listar:
            continue

        if tamanho_bytes and tamanho_mb > args.tamanho_max_mb:
            print(
                f"  Aviso: post {post_id} ({tamanho_mb:.2f} MB) excede "
                f"--tamanho-max-mb ({args.tamanho_max_mb:g} MB); pulando download."
            )
            continue

        file_url = _normalizar_url_sakuga(post.get("file_url"))
        if not file_url:
            print(f"  Aviso: post {post_id} não possui URL de arquivo disponível; pulando.")
            continue

        ext = _extrair_extensao(file_url, padrao=str(post.get("file_ext") or "mp4"))
        nome_arquivo = f"sakuga_{_sanitizar_segmento(post_id)}.{ext}"
        destino = os.path.join(args.saida, nome_arquivo)

        if baixar(file_url, destino, max_mb=args.tamanho_max_mb):
            print(f"  Salvo em: {destino}")
            registrar_credito(
                args.saida,
                {
                    "id_unico": f"sakugabooru:{post_id}",
                    "arquivo": nome_arquivo,
                    "site": "sakugabooru.com",
                    "pagina": pagina,
                    "tags": " ".join(lista_tags),
                    "autor": autor,
                    "origem": post.get("source") or "",
                    "baixado_em": _agora_iso(),
                },
            )


def cmd_sakuga_tags(args):
    """Consulta tags existentes no Sakugabooru ordenadas por número de posts."""
    trecho = (args.busca or "").strip()
    if not trecho:
        _erro("Informe um trecho de busca em --busca.")
    if args.limite <= 0:
        _erro("O valor de --limite deve ser maior que zero.")

    busca_codificada = urllib.parse.quote_plus(trecho)
    url = (
        f"https://www.sakugabooru.com/tag.json?name={busca_codificada}"
        f"&limit={args.limite}&order=count"
    )
    tags = pedir_json(url)

    if not isinstance(tags, list):
        _erro("Formato inesperado na resposta de tags do Sakugabooru.")
    if not tags:
        print("Nenhuma tag encontrada para o trecho informado.")
        return

    for item in tags:
        if not isinstance(item, dict):
            continue
        nome = item.get("name") or "(sem nome)"
        codigo_tipo = item.get("type")
        nome_tipo = TIPOS_TAG_SAKUGA.get(codigo_tipo, f"outro ({codigo_tipo})")
        contagem = item.get("count", 0)
        print(f"{nome} | tipo: {nome_tipo} | posts: {contagem}")


def cmd_mangadex(args):
    """Busca obras no MangaDex exibindo identificador, título, ano, status e autor."""
    busca = (args.busca or "").strip()
    if not busca:
        _erro("Informe um título para busca em --busca.")
    if args.limite <= 0:
        _erro("O valor de --limite deve ser maior que zero.")

    limite = args.limite
    if limite > 100:
        print(f"Aviso: limite máximo da busca MangaDex é 100; reduzindo de {limite} para 100.")
        limite = 100

    titulo_codificado = urllib.parse.quote_plus(busca)
    url = (
        f"https://api.mangadex.org/manga?title={titulo_codificado}"
        f"&limit={limite}&includes[]=author&includes[]=cover_art"
    )
    resposta = pedir_json(url)
    lista = resposta.get("data") if isinstance(resposta, dict) else None

    if not isinstance(lista, list):
        _erro("Formato inesperado na resposta de busca do MangaDex.")
    if not lista:
        print("Nenhum mangá encontrado no MangaDex para o título informado.")
        return

    for item in lista:
        if not isinstance(item, dict):
            continue
        manga_id = item.get("id") or "N/D"
        atributos = item.get("attributes") or {}
        titulo = _extrair_titulo_mangadex(atributos)
        ano = atributos.get("year") or "N/D"
        status = atributos.get("status") or "N/D"

        autores = []
        for rel in item.get("relationships") or []:
            if isinstance(rel, dict) and rel.get("type") == "author":
                nome_autor = (rel.get("attributes") or {}).get("name")
                if nome_autor and nome_autor not in autores:
                    autores.append(nome_autor)
        texto_autor = ", ".join(autores) if autores else "N/D"

        print(f"{manga_id} | {titulo} | Ano: {ano} | Status: {status} | Autor: {texto_autor}")


def cmd_mangadex_capitulos(args):
    """Lista somente a numeração de volumes e capítulos disponíveis no MangaDex."""
    manga_id = (args.manga_id or "").strip()
    if not manga_id:
        _erro("Informe o identificador <manga_id>.")
    if args.de is not None and args.ate is not None and args.de > args.ate:
        _erro("O valor de --de não pode ser maior que --ate.")

    id_codificado = urllib.parse.quote(manga_id, safe="")
    idioma_codificado = urllib.parse.quote_plus((args.idioma or "").strip())
    url = (
        f"https://api.mangadex.org/manga/{id_codificado}/aggregate"
        f"?translatedLanguage[]={idioma_codificado}"
    )
    resposta = pedir_json(url)
    volumes_brutos = resposta.get("volumes") if isinstance(resposta, dict) else None

    if isinstance(volumes_brutos, dict):
        iter_volumes = list(volumes_brutos.values())
    elif isinstance(volumes_brutos, list):
        iter_volumes = volumes_brutos
    else:
        _erro("Formato inesperado na agregação de capítulos do MangaDex.")

    if not iter_volumes:
        print(f"Nenhum capítulo catalogado para o idioma '{args.idioma}'.")
        return

    volumes_ordenados = sorted(
        (v for v in iter_volumes if isinstance(v, dict)),
        key=lambda v: _chave_ordem_numerica(v.get("volume") or "none"),
    )

    exibiu_algum = False
    for vol_obj in volumes_ordenados:
        vol_id = str(vol_obj.get("volume") or "none")
        caps_brutos = vol_obj.get("chapters") or {}
        if isinstance(caps_brutos, dict):
            iter_caps = list(caps_brutos.values())
        elif isinstance(caps_brutos, list):
            iter_caps = caps_brutos
        else:
            continue

        numeros_filtrados = []
        for cap_obj in iter_caps:
            cap_str = str(cap_obj.get("chapter") if isinstance(cap_obj, dict) else cap_obj)
            if args.de is not None or args.ate is not None:
                try:
                    cap_num = float(cap_str)
                except ValueError:
                    continue
                if args.de is not None and cap_num < args.de:
                    continue
                if args.ate is not None and cap_num > args.ate:
                    continue
            if cap_str not in numeros_filtrados:
                numeros_filtrados.append(cap_str)

        if not numeros_filtrados:
            continue

        numeros_filtrados.sort(key=_chave_ordem_numerica)
        rotulo_vol = "Sem volume" if vol_id.lower() == "none" else f"Volume {vol_id}"
        print(f"{rotulo_vol}: {', '.join(numeros_filtrados)}")
        exibiu_algum = True

    if not exibiu_algum:
        print("Nenhum capítulo encontrado dentro dos critérios informados.")


def cmd_mangadex_capas(args):
    """Baixa capas de volumes de um mangá no MangaDex e registra os respectivos créditos."""
    manga_id = (args.manga_id or "").strip()
    if not manga_id:
        _erro("Informe o identificador <manga_id>.")
    if args.limite <= 0:
        _erro("O valor de --limite deve ser maior que zero.")

    limite = args.limite
    if limite > 100:
        print(f"Aviso: limite máximo de capas por consulta é 100; reduzindo de {limite} para 100.")
        limite = 100

    id_codificado = urllib.parse.quote(manga_id, safe="")
    url = (
        f"https://api.mangadex.org/cover?manga[]={id_codificado}"
        f"&limit={limite}&order[volume]=asc"
    )
    resposta = pedir_json(url)
    capas = resposta.get("data") if isinstance(resposta, dict) else None

    if not isinstance(capas, list):
        _erro("Formato inesperado na resposta de capas do MangaDex.")
    if not capas:
        print("Nenhuma capa encontrada para o mangá informado.")
        return

    id_seguro = _sanitizar_segmento(manga_id)
    pagina_obra = f"https://mangadex.org/title/{manga_id}"

    for item in capas:
        if not isinstance(item, dict):
            continue
        cover_id = item.get("id") or ""
        atributos = item.get("attributes") or {}
        file_name = atributos.get("fileName") or ""
        if not file_name:
            print(f"Aviso: capa {cover_id} sem nome de arquivo; pulando.")
            continue

        volume = atributos.get("volume")
        rotulo_vol = _sanitizar_segmento(volume if volume not in (None, "") else "none")
        ext = _extrair_extensao(file_name, padrao="jpg")
        nome_local = f"capa_{id_seguro}_v{rotulo_vol}.{ext}"
        destino = os.path.join(args.saida, nome_local)
        url_imagem = (
            f"https://uploads.mangadex.org/covers/{id_codificado}/"
            f"{urllib.parse.quote(file_name)}"
        )

        autor_capa = ""
        for rel in item.get("relationships") or []:
            if isinstance(rel, dict) and rel.get("type") in ("author", "artist", "user"):
                rel_attrs = rel.get("attributes") or {}
                nome_rel = rel_attrs.get("name") or rel_attrs.get("username")
                if nome_rel:
                    autor_capa = nome_rel
                    break

        descricao = (atributos.get("description") or "").strip()
        titulo_credito = f"Capa volume {volume if volume not in (None, '') else 'N/D'} ({manga_id})"
        if descricao:
            titulo_credito = f"{titulo_credito} - {descricao}"

        print(f"Baixando capa volume {volume if volume not in (None, '') else 'N/D'}: {nome_local}")
        if baixar(url_imagem, destino):
            print(f"  Salvo em: {destino}")
            registrar_credito(
                args.saida,
                {
                    "id_unico": f"mangadex_cover:{cover_id or nome_local}",
                    "arquivo": nome_local,
                    "site": "mangadex.org",
                    "pagina": pagina_obra,
                    "titulo": titulo_credito,
                    "autor": autor_capa,
                    "origem": url_imagem,
                    "baixado_em": _agora_iso(),
                },
            )


def cmd_jikan(args):
    """Consulta metadados de animes ou mangás na API Jikan v4 (MyAnimeList)."""
    busca = (args.busca or "").strip()
    if not busca:
        _erro("Informe um título para busca em --busca.")
    if args.limite <= 0:
        _erro("O valor de --limite deve ser maior que zero.")

    limite = args.limite
    if limite > 25:
        print(f"Aviso: limite máximo da busca Jikan v4 é 25; reduzindo de {limite} para 25.")
        limite = 25

    busca_codificada = urllib.parse.quote_plus(busca)
    url = f"https://api.jikan.moe/v4/{args.tipo}?q={busca_codificada}&limit={limite}"
    resposta = pedir_json(url)
    itens = resposta.get("data") if isinstance(resposta, dict) else None

    if not isinstance(itens, list):
        _erro("Formato inesperado na resposta da API Jikan.")
    if not itens:
        print(f"Nenhum resultado encontrado para '{busca}' ({args.tipo}).")
        return

    for item in itens:
        if not isinstance(item, dict):
            continue
        mal_id = item.get("mal_id", "N/D")
        titulo = item.get("title") or item.get("title_english") or "(sem título)"
        tipo_item = item.get("type") or "N/D"

        ano = item.get("year")
        if not ano:
            ano = (((item.get("aired") or {}).get("prop") or {}).get("from") or {}).get("year")
        if not ano:
            ano = (((item.get("published") or {}).get("prop") or {}).get("from") or {}).get("year")
        ano_str = str(ano) if ano else "N/D"

        nota = item.get("score")
        nota_str = f"{nota:.2f}" if isinstance(nota, (int, float)) else "N/D"

        if args.tipo == "anime":
            episodios = item.get("episodes")
            contagem_str = f"Episódios: {episodios if episodios is not None else 'N/D'}"
        else:
            capitulos = item.get("chapters")
            volumes = item.get("volumes")
            cap_txt = capitulos if capitulos is not None else "N/D"
            vol_txt = volumes if volumes is not None else "N/D"
            contagem_str = f"Capítulos: {cap_txt} | Volumes: {vol_txt}"

        print(
            f"[{mal_id}] {titulo} | Tipo: {tipo_item} | Ano: {ano_str} | "
            f"{contagem_str} | Nota: {nota_str}"
        )


def cmd_jikan_episodios(args):
    """Lista número e título dos episódios de um anime na API Jikan v4 com info de paginação."""
    if args.mal_id <= 0:
        _erro("O identificador <mal_id> deve ser um inteiro positivo.")
    if args.pagina <= 0:
        _erro("O número de --pagina deve ser maior ou igual a 1.")

    url = f"https://api.jikan.moe/v4/anime/{args.mal_id}/episodes?page={args.pagina}"
    resposta = pedir_json(url)
    episodios = resposta.get("data") if isinstance(resposta, dict) else None

    if not isinstance(episodios, list):
        _erro("Formato inesperado na resposta de episódios da API Jikan.")
    if not episodios:
        print(f"Nenhum episódio encontrado na página {args.pagina} para mal_id={args.mal_id}.")
        return

    for ep in episodios:
        if not isinstance(ep, dict):
            continue
        numero = ep.get("mal_id") if ep.get("mal_id") is not None else ep.get("episode", "?")
        titulo = (
            ep.get("title")
            or ep.get("title_romanji")
            or ep.get("title_japanese")
            or "(sem título)"
        )
        print(f"Episódio {numero}: {titulo}")

    paginacao = resposta.get("pagination") or {}
    tem_proxima = bool(paginacao.get("has_next_page"))
    ultima_pagina = paginacao.get("last_visible_page") or args.pagina

    if tem_proxima:
        print(
            f"Há mais páginas disponíveis (página {args.pagina} de {ultima_pagina}; "
            f"use --pagina {args.pagina + 1})."
        )
    else:
        print(f"Não há mais páginas (página {args.pagina} de {ultima_pagina}).")


def _construir_parser():
    """Cria e configura o parser principal e todos os subcomandos da CLI."""
    parser = _ArgumentParserPortugues(
        prog="fetch_media_refs.py",
        description=(
            "Busca material de referência para estudo de animação e metadados de obras "
            "(não baixa páginas de capítulos de mangá)."
        ),
    )
    subparsers = parser.add_subparsers(dest="subcomando", metavar="<subcomando>")
    subparsers.required = True

    p_sakuga = subparsers.add_parser(
        "sakuga",
        help="Busca e baixa cortes de estudo no Sakugabooru.",
    )
    p_sakuga.add_argument("--tags", required=True, help="Tags separadas por espaço.")
    p_sakuga.add_argument("--limite", type=int, default=5, help="Quantidade de posts (máx. 20).")
    p_sakuga.add_argument(
        "--saida",
        default="./referencias/sakuga",
        help="Pasta de saída (padrão: ./referencias/sakuga).",
    )
    p_sakuga.add_argument(
        "--so-listar",
        action="store_true",
        help="Apenas lista os posts encontrados sem baixar arquivos.",
    )
    p_sakuga.add_argument(
        "--tamanho-max-mb",
        type=float,
        default=40.0,
        help="Tamanho máximo por arquivo em MB (padrão: 40).",
    )
    p_sakuga.set_defaults(func=cmd_sakuga)

    p_sakuga_tags = subparsers.add_parser(
        "sakuga-tags",
        help="Busca a grafia exata de tags no Sakugabooru.",
    )
    p_sakuga_tags.add_argument("--busca", required=True, help="Trecho do nome da tag.")
    p_sakuga_tags.add_argument(
        "--limite",
        type=int,
        default=15,
        help="Quantidade máxima de tags listadas (padrão: 15).",
    )
    p_sakuga_tags.set_defaults(func=cmd_sakuga_tags)

    p_mangadex = subparsers.add_parser(
        "mangadex",
        help="Busca metadados de mangás no MangaDex.",
    )
    p_mangadex.add_argument("--busca", required=True, help="Título da obra para busca.")
    p_mangadex.add_argument(
        "--limite",
        type=int,
        default=5,
        help="Quantidade máxima de resultados (padrão: 5).",
    )
    p_mangadex.set_defaults(func=cmd_mangadex)

    p_md_caps = subparsers.add_parser(
        "mangadex-capitulos",
        help="Lista apenas os números de volumes e capítulos existentes no MangaDex.",
    )
    p_md_caps.add_argument("manga_id", help="UUID do mangá no MangaDex.")
    p_md_caps.add_argument(
        "--idioma",
        default="pt-br",
        help="Código de idioma traduzido (padrão: pt-br).",
    )
    p_md_caps.add_argument("--de", type=float, default=None, help="Capítulo inicial do filtro.")
    p_md_caps.add_argument("--ate", type=float, default=None, help="Capítulo final do filtro.")
    p_md_caps.set_defaults(func=cmd_mangadex_capitulos)

    p_md_capas = subparsers.add_parser(
        "mangadex-capas",
        help="Baixa capas de volumes de um mangá no MangaDex.",
    )
    p_md_capas.add_argument("manga_id", help="UUID do mangá no MangaDex.")
    p_md_capas.add_argument(
        "--saida",
        default="./referencias/capas",
        help="Pasta de saída das capas (padrão: ./referencias/capas).",
    )
    p_md_capas.add_argument(
        "--limite",
        type=int,
        default=10,
        help="Quantidade máxima de capas (padrão: 10).",
    )
    p_md_capas.set_defaults(func=cmd_mangadex_capas)

    p_jikan = subparsers.add_parser(
        "jikan",
        help="Busca animes ou mangás na API Jikan (MyAnimeList).",
    )
    p_jikan.add_argument(
        "--tipo",
        required=True,
        choices=["anime", "manga"],
        help="Tipo da obra: anime ou manga.",
    )
    p_jikan.add_argument("--busca", required=True, help="Título para busca.")
    p_jikan.add_argument(
        "--limite",
        type=int,
        default=5,
        help="Quantidade máxima de resultados (padrão: 5).",
    )
    p_jikan.set_defaults(func=cmd_jikan)

    p_jikan_eps = subparsers.add_parser(
        "jikan-episodios",
        help="Lista número e título dos episódios de um anime via Jikan.",
    )
    p_jikan_eps.add_argument("mal_id", type=int, help="ID numérico do anime no MyAnimeList.")
    p_jikan_eps.add_argument(
        "--pagina",
        type=int,
        default=1,
        help="Página da listagem de episódios (padrão: 1).",
    )
    p_jikan_eps.set_defaults(func=cmd_jikan_episodios)

    return parser


def main():
    """Executa a interface de linha de comando e trata interrupções do usuário."""
    parser = _construir_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        _erro("Operação interrompida pelo usuário.")


if __name__ == "__main__":
    main()
