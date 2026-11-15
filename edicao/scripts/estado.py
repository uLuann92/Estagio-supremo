#!/usr/bin/env python3
"""Gerenciador de estado do projeto de clipe musical (_CLAUDE/projeto.json)."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

ETAPAS = [
    "iniciar",
    "musica",
    "paineis",
    "roteiro",
    "animar",
    "letra",
    "efeitos",
    "sfx",
    "finalizar",
]

STATUS_VALIDOS = {
    "pendente",
    "em_andamento",
    "aguardando_aprovacao",
    "aguardando_usuario",
    "concluido",
    "nao_precisa",
}

SIMBOLOS_STATUS = {
    "concluido": "[x]",
    "em_andamento": "[~]",
    "aguardando_aprovacao": "[?]",
    "aguardando_usuario": "[?]",
    "pendente": "[ ]",
    "nao_precisa": "[-]",
}

CHAVES_SISTEMA = {
    "projeto",
    "nome",
    "perfil",
    "criado_em",
    "video",
    "ferramentas",
    "etapas",
    "pendencias",
    "atualizado",
}

MAPA_BLOCO_ETAPA = {
    "musica": "musica",
    "cenas": "paineis",
    "paineis": "paineis",
    "roteiro": "roteiro",
    "montagem": "animar",
    "animar": "animar",
    "letra": "letra",
    "efeitos": "efeitos",
    "sfx": "sfx",
    "finalizar": "finalizar",
}


def erro(mensagem: str) -> None:
    """Imprime mensagem de erro em português e encerra com código 1."""
    print(f"Erro: {mensagem}", file=sys.stderr)
    sys.exit(1)


def agora_iso() -> str:
    """Retorna a data e hora atual em formato ISO 8601 (UTC, precisão de segundos)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def caminho_projeto_json(pasta: Path) -> Path:
    """Retorna o caminho para _CLAUDE/projeto.json dentro da pasta do projeto."""
    return pasta / "_CLAUDE" / "projeto.json"


def carregar_estado(pasta: Path) -> dict:
    """Carrega e retorna o dicionário de estado do projeto ou encerra com erro."""
    if not pasta.exists() or not pasta.is_dir():
        erro(f"Pasta do projeto não encontrada: '{pasta}'.")
    arq = caminho_projeto_json(pasta)
    if not arq.exists():
        erro(f"Arquivo de estado não encontrado em '{arq}'. Use o comando 'iniciar' primeiro.")
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        erro(f"JSON inválido em '{arq}': {exc}")
    return {}


def salvar_estado(pasta: Path, estado: dict) -> None:
    """Grava o dicionário de estado em _CLAUDE/projeto.json de forma atômica."""
    arq = caminho_projeto_json(pasta)
    arq.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(estado, ensure_ascii=False, indent=2) + "\n"
    fd, temp_path = tempfile.mkstemp(
        dir=str(arq.parent), prefix=".projeto_", suffix=".tmp", text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(conteudo)
        os.replace(temp_path, arq)
    except Exception as exc:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        erro(f"Falha ao gravar estado em '{arq}': {exc}")


def registrar_atualizacao(estado: dict, chave: str) -> None:
    """Atualiza o timestamp ISO de uma etapa ou bloco no dicionário 'atualizado'."""
    estado.setdefault("atualizado", {})
    ts = agora_iso()
    estado["atualizado"][chave] = ts
    etapa_correspondente = MAPA_BLOCO_ETAPA.get(chave)
    if etapa_correspondente:
        estado["atualizado"][etapa_correspondente] = ts


def comando_iniciar(pasta: Path, args: argparse.Namespace) -> None:
    """Cria a estrutura de pastas, aprendizados.md e o projeto.json inicial."""
    if not args.nome:
        erro("O comando 'iniciar' exige a opção --nome \"<nome>\".")
    arq = caminho_projeto_json(pasta)
    if arq.exists():
        erro(f"O projeto já existe em '{arq}'. Não foi sobrescrito.")

    subpastas = [
        "Musica",
        "Paginas",
        "Docs",
        "Renders",
        "_CLAUDE",
        "_CLAUDE/segundo-olhar",
    ]
    for sub in subpastas:
        (pasta / sub).mkdir(parents=True, exist_ok=True)

    aprendizados = pasta / "_CLAUDE" / "aprendizados.md"
    if not aprendizados.exists():
        aprendizados.write_text(
            "# Aprendizados e preferências\n\n"
            "Formato de cada item: `- [ ] <etapa> · <pedido> · <dd/mm>`\n",
            encoding="utf-8",
        )

    ts = agora_iso()
    estado = {
        "projeto": pasta.resolve().name,
        "nome": args.nome,
        "perfil": args.perfil,
        "criado_em": ts,
        "video": {
            "fps": args.fps,
            "largura": args.largura,
            "altura": args.altura,
        },
        "ferramentas": {
            "hyperframes": "0.9.45",
        },
        "etapas": {etapa: "pendente" for etapa in ETAPAS},
        "pendencias": [],
        "atualizado": {"iniciar": ts},
    }
    salvar_estado(pasta, estado)
    print(f"Projeto '{args.nome}' ({estado['projeto']}) iniciado em '{pasta}'.")


def calcular_alertas(estado: dict) -> list[str]:
    """Verifica se alguma etapa anterior foi atualizada após etapa posterior concluída/aguardando."""
    etapas = estado.get("etapas", {})
    atualizado = estado.get("atualizado", {})
    alertas = []
    for i, ant in enumerate(ETAPAS):
        ts_ant = atualizado.get(ant)
        if not ts_ant:
            continue
        for post in ETAPAS[i + 1 :]:
            st_post = etapas.get(post, "pendente")
            if st_post not in ("concluido", "aguardando_aprovacao"):
                continue
            ts_post = atualizado.get(post)
            if ts_post and ts_ant > ts_post:
                alertas.append(
                    f"{ant} mudou depois de {post}: {post} pode estar desatualizada"
                )
    return alertas


def contar_aprendizados_abertos(pasta: Path) -> int:
    """Conta quantas linhas começam com '- [ ]' em _CLAUDE/aprendizados.md."""
    arq = pasta / "_CLAUDE" / "aprendizados.md"
    if not arq.exists():
        return 0
    linhas = arq.read_text(encoding="utf-8").splitlines()
    return sum(1 for linha in linhas if linha.startswith("- [ ]"))


def resumir_bloco_uma_linha(valor: object) -> str:
    """Gera um resumo conciso de uma linha para um bloco de dados."""
    if isinstance(valor, list):
        return f"{len(valor)} item(ns)"
    if isinstance(valor, dict):
        partes = []
        for k, v in valor.items():
            if isinstance(v, list):
                partes.append(f"{k}: {len(v)} item(ns)")
            elif isinstance(v, dict):
                partes.append(f"{k}: {len(v)} chave(s)")
            else:
                partes.append(f"{k}={v}")
        return ", ".join(partes[:6]) + ("..." if len(partes) > 6 else "")
    return str(valor)


def comando_status(pasta: Path, estado: dict) -> None:
    """Imprime o resumo completo do status do projeto."""
    nome = estado.get("nome", estado.get("projeto", "?"))
    perfil = estado.get("perfil", "padrao")
    video = estado.get("video", {})
    info_video = f"{video.get('largura', '?')}x{video.get('altura', '?')} @ {video.get('fps', '?')}fps"
    print(f"Projeto: {nome} ({estado.get('projeto', '')}) | Perfil: {perfil} | Vídeo: {info_video}")

    etapas = estado.get("etapas", {})
    print("\nEtapas:")
    proxima = None
    for etapa in ETAPAS:
        st = etapas.get(etapa, "pendente")
        simbolo = SIMBOLOS_STATUS.get(st, "[?]" if st.startswith("aguardando_") else "[ ]")
        print(f"  {simbolo} {etapa}: {st}")
        if proxima is None and st not in ("concluido", "nao_precisa"):
            proxima = etapa

    print(f"\nPróxima etapa: {proxima if proxima else 'nenhuma (fluxo concluído)'}")

    pendencias = [p for p in estado.get("pendencias", []) if not p.get("resolvida")]
    if pendencias:
        print(f"\nPendências abertas ({len(pendencias)}):")
        for p in pendencias:
            print(f"  - [{p.get('id')}] ({p.get('etapa')}): {p.get('texto')}")
    else:
        print("\nPendências abertas: 0")

    alertas = calcular_alertas(estado)
    if alertas:
        print(f"\nAlertas ({len(alertas)}):")
        for alerta in alertas:
            print(f"  ! {alerta}")
    else:
        print("\nAlertas: nenhum")

    qtd_aprendizados = contar_aprendizados_abertos(pasta)
    print(f"Aprendizados abertos: {qtd_aprendizados}")

    blocos_extras = [k for k in estado.keys() if k not in CHAVES_SISTEMA]
    if blocos_extras:
        print("\nBlocos de dados:")
        for chave in blocos_extras:
            print(f"  - {chave}: {resumir_bloco_uma_linha(estado[chave])}")


def buscar_item_recursivo(dados: object, alvo_id: str) -> object:
    """Procura recursivamente um dicionário com campo 'id' igual a alvo_id."""
    if isinstance(dados, dict):
        if str(dados.get("id", "")) == alvo_id:
            return dados
        for v in dados.values():
            achado = buscar_item_recursivo(v, alvo_id)
            if achado is not None:
                return achado
    elif isinstance(dados, list):
        for elem in dados:
            achado = buscar_item_recursivo(elem, alvo_id)
            if achado is not None:
                return achado
    return None


def resumir_lista_amostra(lista: list) -> str:
    """Retorna a contagem e até os 5 primeiros identificadores ou textos de uma lista."""
    amostra = []
    for item in lista[:5]:
        if isinstance(item, dict):
            ident = (
                item.get("id")
                or item.get("nome")
                or item.get("secao")
                or item.get("texto")
                or item.get("cena")
                or str(item)
            )
            amostra.append(str(ident))
        else:
            amostra.append(str(item))
    sufixo = f" [{', '.join(amostra)}{', ...' if len(lista) > 5 else ''}]" if amostra else ""
    return f"{len(lista)} item(ns){sufixo}"


def comando_bloco(estado: dict, nome_bloco: str, como_json: bool, item_id: str | None) -> None:
    """Exibe um bloco do estado (resumo, JSON completo ou item específico)."""
    if nome_bloco not in estado:
        erro(f"Bloco '{nome_bloco}' não encontrado no estado do projeto.")
    bloco = estado[nome_bloco]

    if item_id is not None:
        achado = buscar_item_recursivo(bloco, item_id)
        if achado is None:
            erro(f"Item com id '{item_id}' não encontrado no bloco '{nome_bloco}'.")
        print(json.dumps(achado, ensure_ascii=False, indent=2))
        return

    if como_json:
        print(json.dumps(bloco, ensure_ascii=False, indent=2))
        return

    print(f"Bloco '{nome_bloco}':")
    if isinstance(bloco, list):
        print(f"  Lista: {resumir_lista_amostra(bloco)}")
    elif isinstance(bloco, dict):
        if not bloco:
            print("  (vazio)")
        for k, v in bloco.items():
            if isinstance(v, list):
                print(f"  {k}: {resumir_lista_amostra(v)}")
            elif isinstance(v, dict):
                chaves_sub = ", ".join(list(v.keys())[:8])
                print(f"  {k}: dicionário ({len(v)} chave(s): {chaves_sub})")
            else:
                print(f"  {k}: {v}")
    else:
        print(f"  {bloco}")


def interpretar_valor(texto: str) -> object:
    """Tenta converter o texto como JSON; se falhar, retorna a própria string."""
    try:
        return json.loads(texto)
    except Exception:
        return texto


def aplicar_set(estado: dict, caminho: str, valor_str: str) -> None:
    """Aplica um valor em um caminho separado por pontos no estado."""
    partes = [p for p in caminho.split(".") if p]
    if not partes:
        erro("Caminho inválido para --set.")
    valor = interpretar_valor(valor_str)
    atual = estado
    for parte in partes[:-1]:
        if parte not in atual or not isinstance(atual[parte], dict):
            atual[parte] = {}
        atual = atual[parte]
    atual[partes[-1]] = valor
    registrar_atualizacao(estado, partes[0])
    print(f"Definido {caminho} = {json.dumps(valor, ensure_ascii=False)}")


def aplicar_etapa(estado: dict, expressao: str) -> None:
    """Valida e altera o status de uma etapa no formato <etapa>=<status>."""
    if "=" not in expressao:
        erro(f"Formato inválido em --etapa '{expressao}'. Use <etapa>=<status>.")
    etapa, status = expressao.split("=", 1)
    etapa = etapa.strip()
    status = status.strip()
    if etapa not in ETAPAS:
        erro(f"Etapa inválida: '{etapa}'. Etapas válidas: {', '.join(ETAPAS)}.")
    if status not in STATUS_VALIDOS:
        erro(
            f"Status inválido: '{status}'. Status válidos: {', '.join(sorted(STATUS_VALIDOS))}."
        )
    estado.setdefault("etapas", {})[etapa] = status
    registrar_atualizacao(estado, etapa)
    print(f"Etapa '{etapa}' atualizada para '{status}'.")


def aplicar_pendencia(estado: dict, etapa: str, texto: str) -> None:
    """Adiciona uma nova pendência numerada ao estado do projeto."""
    if etapa not in ETAPAS:
        erro(f"Etapa inválida para pendência: '{etapa}'. Etapas válidas: {', '.join(ETAPAS)}.")
    pendencias = estado.setdefault("pendencias", [])
    maior_num = 0
    for p in pendencias:
        pid = str(p.get("id", ""))
        if pid.startswith("p") and pid[1:].isdigit():
            maior_num = max(maior_num, int(pid[1:]))
    novo_id = f"p{maior_num + 1:02d}"
    item = {
        "id": novo_id,
        "etapa": etapa,
        "texto": texto,
        "criada_em": agora_iso(),
        "resolvida": False,
    }
    pendencias.append(item)
    print(f"Pendência '{novo_id}' adicionada na etapa '{etapa}'.")


def aplicar_resolver(estado: dict, id_pendencia: str) -> None:
    """Marca uma pendência existente como resolvida com a data atual."""
    for p in estado.get("pendencias", []):
        if p.get("id") == id_pendencia:
            p["resolvida"] = agora_iso()
            print(f"Pendência '{id_pendencia}' marcada como resolvida.")
            return
    erro(f"Pendência com id '{id_pendencia}' não encontrada.")


def aplicar_gravar_bloco(estado: dict, bloco: str, caminho_arq: str) -> None:
    """Substitui um bloco inteiro pelo conteúdo de um arquivo JSON externo."""
    arq = Path(caminho_arq)
    if not arq.exists():
        erro(f"Arquivo JSON não encontrado: '{arq}'.")
    try:
        conteudo = json.loads(arq.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        erro(f"Arquivo '{arq}' não contém JSON válido: {exc}")
    estado[bloco] = conteudo
    registrar_atualizacao(estado, bloco)
    print(f"Bloco '{bloco}' gravado a partir de '{arq}'.")


def construir_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Gerencia o estado (_CLAUDE/projeto.json) de um clipe musical."
    )
    parser.add_argument("pasta", help="Caminho da pasta do projeto")
    parser.add_argument(
        "comando",
        nargs="?",
        default=None,
        help="Comando ('iniciar', 'status') ou nome de um bloco (ex.: 'musica', 'roteiro')",
    )

    parser.add_argument("--nome", help="Nome do projeto (usado com 'iniciar')")
    parser.add_argument(
        "--perfil", default="padrao", help="Perfil de estilo (padrão: padrao)"
    )
    parser.add_argument(
        "--fps", type=float, default=24, help="Taxa de quadros (padrão: 24)"
    )
    parser.add_argument(
        "--largura", type=int, default=1920, help="Largura do vídeo (padrão: 1920)"
    )
    parser.add_argument(
        "--altura", type=int, default=1080, help="Altura do vídeo (padrão: 1080)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="como_json",
        help="Imprime o bloco inteiro em formato JSON",
    )
    parser.add_argument(
        "--item",
         metavar="ID",
        help="Busca e imprime recursivamente o item com este 'id' dentro do bloco",
    )

    parser.add_argument(
        "--set",
        nargs=2,
        metavar=("CAMINHO", "VALOR"),
        action="append",
        dest="sets",
        help="Define um valor em um caminho com pontos (ex.: --set musica.bpm 140)",
    )
    parser.add_argument(
        "--etapa",
        metavar="ETAPA=STATUS",
        action="append",
        dest="etapas",
        help="Atualiza o status de uma etapa (ex.: --etapa musica=concluido)",
    )
    parser.add_argument(
        "--pendencia",
        nargs=2,
        metavar=("ETAPA", "TEXTO"),
        action="append",
        dest="pendencias",
        help="Registra uma nova pendência em uma etapa",
    )
    parser.add_argument(
        "--resolver",
        metavar="ID",
        action="append",
        dest="resolucoes",
        help="Marca uma pendência como resolvida pelo id (ex.: --resolver p01)",
    )
    parser.add_argument(
        "--gravar-bloco",
        nargs=2,
        metavar=("BLOCO", "ARQUIVO_JSON"),
        action="append",
        dest="blocos_gravar",
        help="Substitui um bloco pelo conteúdo de um arquivo JSON",
    )
    return parser


def main() -> None:
    """Ponto de entrada principal do script de estado."""
    parser = construir_parser()
    args = parser.parse_args()
    pasta = Path(args.pasta)

    if args.comando == "iniciar":
        if args.fps == int(args.fps):
            args.fps = int(args.fps)
        comando_iniciar(pasta, args)
        return

    tem_mutacao = any(
        [
            args.sets,
            args.etapas,
            args.pendencias,
            args.resolucoes,
            args.blocos_gravar,
        ]
    )

    if not args.comando and not tem_mutacao:
        erro("Informe um comando ('iniciar', 'status', <bloco>) ou uma opção de alteração.")

    estado = carregar_estado(pasta)

    if tem_mutacao:
        for caminho, valor in args.sets or []:
            aplicar_set(estado, caminho, valor)
        for expr in args.etapas or []:
            aplicar_etapa(estado, expr)
        for etapa, texto in args.pendencias or []:
            aplicar_pendencia(estado, etapa, texto)
        for pid in args.resolucoes or []:
            aplicar_resolver(estado, pid)
        for bloco, arq in args.blocos_gravar or []:
            aplicar_gravar_bloco(estado, bloco, arq)
        salvar_estado(pasta, estado)

    if args.comando == "status":
        comando_status(pasta, estado)
    elif args.comando is not None:
        comando_bloco(estado, args.comando, args.como_json, args.item)


if __name__ == "__main__":
    main()
