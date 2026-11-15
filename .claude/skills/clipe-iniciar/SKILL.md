---
name: clipe-iniciar
description: "Abre o projeto de um clipe musical, cria a estrutura de pastas e organiza o briefing. Use em /clipe-iniciar, no início de um vídeo novo."
---

# clipe-iniciar

Abre o projeto do clipe, prepara a estrutura de pastas e organiza o briefing com o usuário. Não analisa áudio, páginas de mangá nem outros arquivos brutos: apenas registra as informações iniciais, o estado do projeto e confere o que falta para começar.

- **Lê:** pastas existentes em `projetos/`, lista de perfis em `edicao/perfis/`, relato do usuário no chat
- **Escreve:** estrutura da pasta `projetos/AAAA-MM-DD_Nome/`, estado inicial em `_CLAUDE/projeto.json`, caderno em `_CLAUDE/aprendizados.md`, briefing em `Docs/briefing.md`
- **Próximo passo:** `/clipe-musica`

Esta é a primeira etapa do fluxo (não há etapa anterior).

## Ofício
Destilado de `.claude/skills/fluxo-de-edicao/guias/etapa-iniciar-preparar.md` e `.claude/skills/fluxo-de-edicao/guias/clipe-musical.md` (consulte-os para detalhes):

- **Conferência da pasta:** verifique se já existe uma pasta de projeto em `projetos/AAAA-MM-DD_Nome/` ou se uma nova deve ser criada. O padrão exige as subpastas `Musica/`, `Paginas/`, `Docs/`, `Renders/` e `_CLAUDE/` (incluindo `_CLAUDE/segundo-olhar/`). Se faltar alguma subpasta, pergunte se pode criar vazia. Se já houver `_CLAUDE/projeto.json`, não sobrescreva nada: mostre o status atual e pergunte se é apenas para atualizar o briefing.
- **Formato e ferramentas fixadas no estado:** registre no `projeto.json` as configurações-padrão do fluxo: 16:9, 1920×1080, 24 fps e a versão do HyperFrames (`0.9.45`).
- **Briefing sem formulário:** peça numa mensagem curta: *"Me conta, do jeito que vier, sobre o que é esse clipe (música, personagem/obra, de onde vêm as páginas do mangá) e qualquer ideia ou direcionamento que você já tenha."*
- **Organizar sem inventar (tendência, não regra na estrutura):** preserve as palavras e a intenção do usuário; nunca invente tom, público ou ideia não dita. Use seções claras em `Docs/briefing.md` (ex.: Sobre o clipe e personagem, Música e letra, Origem das páginas e direitos, Direcionamentos gerais, Observações por etapa: música, painéis, roteiro, animação, letra, efeitos, som). Omita as seções vazias.
- **Direitos e material:** páginas de mangá, músicas e fontes têm dono. Explique uma vez com clareza e registre no briefing a origem das páginas (volumes digitais, capítulos, se têm balões ou marcas d'água), quem produziu a música/instrumental (ex.: Suno, produtor, se há faixas separadas de voz e instrumental) e quantas vozes cantam.

## Perfil
Verifique as pastas disponíveis em `edicao/perfis/`.
- Se houver apenas `edicao/perfis/padrao/`, defina `padrao` no estado do vídeo (`_CLAUDE/projeto.json`).
- Se houver mais de um perfil, pergunte ao usuário qual usar e anote no estado.
- Caso o perfil escolhido ainda seja apenas o esqueleto (sem referências medidas), avise o usuário que convém medir os canais de referência antes das etapas criativas.

## Scripts
| Script | O que faz | Armadilhas a evitar |
|---|---|---|
| `python edicao/scripts/estado.py <pasta> ...` | Cria e atualiza `_CLAUDE/projeto.json`, controla status das etapas e fixa parâmetros (24 fps, 1920×1080, versão `0.9.45` do HyperFrames). | Nunca sobrescrever um `projeto.json` já existente ao iniciar; gravar JSON válido com caminhos relativos e todas as 9 etapas (`clipe-iniciar` a `clipe-finalizar`). |

Na primeira vez que a etapa rodar num vídeo real, se `edicao/scripts/estado.py` ainda não existir, escreva-o e teste-o em `edicao/scripts/`, anotando aqui os subcomandos exatos (`init`, `status`, `set-etapa`, etc.). Nos próximos vídeos, reaproveite.

## Passo a passo
1. Verifique se o usuário já indicou uma pasta em `projetos/AAAA-MM-DD_Nome/`. Se o projeto já existir e tiver `_CLAUDE/projeto.json`, rode `python edicao/scripts/estado.py <pasta do projeto> status`, mostre o resumo e pergunte se deseja apenas atualizar o briefing.
2. Para projeto novo, confirme o nome e crie (após aval do usuário, se necessário) `projetos/AAAA-MM-DD_Nome/` com `Musica/`, `Paginas/`, `Docs/`, `Renders/`, `_CLAUDE/` e `_CLAUDE/segundo-olhar/`.
3. Inicialize `_CLAUDE/projeto.json` via `python edicao/scripts/estado.py <pasta do projeto> ...` (com perfil `padrao`, 1920×1080, 24 fps, HyperFrames `0.9.45`) e crie `_CLAUDE/aprendizados.md` se não existir.
4. Peça o briefing ao usuário em uma mensagem curta e aberta, incluindo pergunta sobre a origem da música, letra e páginas do mangá.
5. Ao receber a resposta, organize e salve em `Docs/briefing.md` sem acrescentar ideias próprias. Mostre o texto organizado no chat e pergunte de volta só se algo estiver realmente ambíguo.
6. Liste os arquivos que já estão em `Musica/`, `Docs/` e `Paginas/` e aponte claramente o que falta para a próxima etapa (`/clipe-musica`: mixagem final em WAV ou MP3 em `Musica/`, faixas separadas se houver, e a letra escrita na versão final em `Docs/` ou `Musica/`).

## Resumo no chat
Curto: confirme a pasta criada/aberta, mostre o conteúdo salvo em `Docs/briefing.md`, liste o que já está nas pastas e o que falta colocar antes de `/clipe-musica`. Marque a etapa `clipe-iniciar` como `aguardando_aprovacao` usando `python edicao/scripts/estado.py <pasta do projeto> ...`.

## Revisão
O usuário responde no chat dizendo o que mudar, tirar ou acrescentar no briefing ou nos dados do projeto. Ajuste apenas o que foi citado em `Docs/briefing.md` ou `_CLAUDE/projeto.json`, mostre a versão atualizada e anote aprendizados relevantes em `_CLAUDE/aprendizados.md`.

## Aprovação
Quando o usuário aprovar o briefing, marque `clipe-iniciar` como `concluido` no estado (`python edicao/scripts/estado.py <pasta do projeto> ...`), diga quantos aprendizados foram anotados em `_CLAUDE/aprendizados.md` e sugira rodar `/clear` e depois `/clipe` (ou `/clipe-musica` quando os arquivos de áudio e letra estiverem na pasta).

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto trazidos pelo usuário.
- Nunca sobrescrever `_CLAUDE/projeto.json` ou `Docs/briefing.md` existentes sem mostrar o estado atual e confirmar.
- Não inventar informações, tom ou direcionamentos que o usuário não disse no briefing.
- Falar com o usuário em português, de forma curta e direta.
