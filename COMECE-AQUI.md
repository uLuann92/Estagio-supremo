# Oficina de clipes (rap geek com mangá animado)

Este repositório é a oficina: as skills, os scripts e os projetos de vídeo ficam aqui. Funciona numa sessão do Claude Code na nuvem aberta neste repositório, ou no seu computador.

## Para fazer um vídeo
1. Abra o Claude Code neste repositório e digite `/clipe`.
2. Ele abre a etapa certa. No primeiro vídeo, começa por `/clipe-iniciar` e pede:
   - **a música** (WAV ou MP3; se tiver voz e instrumental separados, melhor);
   - **a letra escrita**, na versão final;
   - **as páginas do mangá**, em boa resolução (seus volumes digitais ou capítulos oficiais);
   - **links do YouTube** de 3 a 5 vídeos no estilo que você quer.
3. Uma etapa por vez: você aprova e ele segue.

## As etapas
`/clipe-iniciar` → `/clipe-musica` → `/clipe-paineis` → `/clipe-roteiro` → `/clipe-animar` → `/clipe-letra` → `/clipe-efeitos` → `/clipe-sfx` → `/clipe-finalizar`

## Onde está cada coisa
| Pasta | O que tem |
|---|---|
| `.claude/skills/clipe*/` | as skills do dia a dia |
| `.claude/skills/fluxo-de-edicao/` | a skill que monta e muda o fluxo, os guias e as ferramentas (`gemini.py`, `painel.py`) |
| `edicao/` | decisões (`montagem.md`), scripts (`estado.py`, `musica.py`), perfil de estilo, sons |
| `projetos/` | um vídeo por pasta |
| `config-claude/` | o protocolo global e a ponte do Gemini, para instalar no seu computador |

## O que precisa existir
- A variável de ambiente `GEMINI_API_KEY` (segundo olhar, análise dos quadros e fundo limpo). Na nuvem: nas configurações do ambiente. No computador: `config-claude/LEIA.md`.
- Sem ela o fluxo roda, mas sem o Gemini: o recorte dos quadros passa a pedir retoque à mão.

## Atenção: mídia não vai para o GitHub
Música, páginas de mangá e renders ficam fora do repositório (`.gitignore`): são grandes e têm dono. Numa sessão na nuvem, isso quer dizer que **eles somem quando a sessão é encerrada**; o que fica salvo é o estado do projeto, o roteiro e os códigos das animações. Para um vídeo inteiro, o caminho mais seguro é rodar no seu computador, ou baixar cada render assim que sair.

## Mudar o fluxo
As escolhas atuais são padrões (`edicao/montagem.md`). Para mudar, digite `/fluxo-de-edicao`.
