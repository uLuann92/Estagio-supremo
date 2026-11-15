---
name: clipe-paineis
description: "Fatia as páginas do mangá em quadros, analisa o conteúdo de cada um e monta o catálogo de quadros. Use em /clipe-paineis, após a clipe-musica."
---

# clipe-paineis

Fatia as páginas de mangá apontadas pelo usuário em quadros numerados, analisa cada quadro e monta o índice para o roteiro. Não baixa mangá da internet, não separa camadas e não anima (isso é da `/clipe-animar`).

- **Lê:** `_CLAUDE/projeto.json` (bloco `musica`, perfil), páginas em `Paginas/`, letra alinhada em `_CLAUDE/musica/`, perfil em `edicao/perfis/<perfil>/`
- **Escreve:** bloco `paineis` em `_CLAUDE/projeto.json`, quadros e análises em `_CLAUDE/paineis/`, folhas numeradas e índice em `_CLAUDE/paineis/catalogo.md` (e `.json`), logs em `_CLAUDE/segundo-olhar/`
- **Próximo passo:** `/clipe-roteiro`

Se a etapa `musica` não estiver `concluido`, pare e sugira terminá-la com `/clipe-musica`.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-paineis.md` (§1 e §2) para detalhes. Princípios desta etapa (decisões criativas são tendência, não regra):
- **Origem das páginas:** o usuário coloca as páginas em `Paginas/`. Nunca baixe de site de scan. Se faltar página para cobrir um verso, sugira pela letra que cena da obra procurar ("a luta do capítulo X; o close do personagem Y") e peça ao usuário para confirmar o capítulo; nunca invente número de capítulo.
- **Qualidade:** confira se cada quadro útil terá ao menos ~1600 px de altura após o zoom. Se a página for pequena, sugira ampliar com modelo próprio para desenho (ex.: Real-ESRGAN/Real-CUGAN no modelo de anime; pesquisar na hora) e conferir num quadro antes de seguir.
- **Fatiar:** separe pela calha branca na ordem de leitura do mangá (direita → esquerda) e gere folha numerada por página. Quadros sangrados, quadros que se invadem e páginas duplas não saem certos no corte automático: junte páginas duplas antes ou ajuste o recorte.
- **ID e índice:** cada quadro ganha ID padronizado (ex.: `v03c021p07q04` ou `p01q01`) e uma linha no índice com: id, personagem, ação, emoção, intensidade (1–5), plano, direção da ação, ponto de impacto, proporção (`largo`, `alto`, `quadrado`), resolução útil e restrições (balão grande, quadro pequeno demais, traço muito fino).
- **Proporção no 16:9 (1920×1080):** quadro alto em vídeo deitado só aparece em parte; anote a proporção e os pontos de interesse para que o roteiro planeje viagem de câmera (ex.: dos pés ao rosto).
- **Balões:** pelo fluxo, balões saem na animação para dar lugar à letra; anote no índice quando um balão cobrir área importante do desenho.

## Perfil
Leia `edicao/perfis/<nome do perfil>/` (nome em `_CLAUDE/projeto.json`):
- `estilo.md` e `catalogo.md` (se já preenchidos): preferências de enquadramento, tipos de plano e tratamento de balões/onomatopeias para destacar no índice os quadros mais adequados.

## Scripts
Na primeira vez que a etapa rodar num vídeo, escreva os scripts que faltam em `edicao/scripts/`, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar |
|---|---|---|
| `python .claude/skills/fluxo-de-edicao/ferramentas/painel.py fatiar <pagina.png> --saida <pasta>` | Separa a página em quadros pela calha branca (direita → esquerda) e gera a folha numerada | Quadros sangrados, que se invadem ou página dupla falham no automático: conferir sempre a folha numerada; juntar página dupla antes ou recortar à mão |
| `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py perguntar` | Analisa cada quadro em JSON (elementos, caixas, plano, emoção, impacto) | Caixas (`box_2d`) são aproximadas (servem para apontar, não para recortar); vigiar cota e teto de gasto (~R$ 15 no vídeo) |
| `python edicao/scripts/catalogo_paineis.py` *(escrever no 1º vídeo)* | Mede dimensões/proporção de cada quadro recortado, junta com o JSON do Gemini e gera `_CLAUDE/paineis/catalogo.json` e `catalogo.md` | Não sobrescrever correções manuais de recorte ou de descrição feitas na revisão; alertar quadros abaixo de ~1600 px úteis |

## Passo a passo
1. Veja status e pendências: `python edicao/scripts/estado.py <pasta do projeto> status`.
2. Liste as imagens em `Paginas/`. Se a pasta estiver vazia ou faltar cena para versos da letra, ajude o usuário a identificar quais capítulos procurar sem inventar números.
3. **Primeira vez de todas:** rode `painel.py fatiar` em 1 ou 2 páginas de teste, gere a folha numerada e a análise desses quadros, peça ao usuário para conferir se a numeração e os recortes funcionam, anote na validação e só então processe o lote inteiro.
4. Fatie todas as páginas para `_CLAUDE/paineis/<id_pagina>/`. Inspecione as folhas numeradas geradas: onde houver página dupla, quadro sangrado ou invasão de calha que cortou errado, refaça o recorte daquele quadro antes de catalogar.
5. Meça resolução e classifique a proporção (`largo`, `alto`, `quadrado`) de cada quadro. Marque restrições de baixa resolução (<1600 px de altura útil).
6. Rode o **Segundo olhar** (abaixo) para descrever os quadros e consolidar o índice em `_CLAUDE/paineis/catalogo.json` e `_CLAUDE/paineis/catalogo.md`.

## Segundo olhar
Consulte `.claude/skills/fluxo-de-edicao/guias/segundo-olhar.md`.
- **Quando:** após ter os quadros fatiados e conferidos, para catalogar o conteúdo visual em lote.
- **Uso:** `olhar` com o modelo leve (`gemini-flash-latest`), usando `--json`. Se não houver `GEMINI_API_KEY`, faça a leitura diretamente olhando as folhas numeradas e os quadros principais.
- **O que mandar:** imagem de cada quadro recortado (`--midia <quadro.png>`). Confirme a permissão de envio externo se ainda não constar autorizada para o projeto.
- **Pergunta-base:** `"Você é um diretor de animação de mangá. Analise este quadro para separá-lo em camadas e animá-lo. Responda só com um JSON: lista de elementos, da frente para o fundo, cada um com label, box_2d ([y0, x0, y1, x1] em milésimos), profundidade (1–5), movimento (uma frase) e partes_moveis. No máximo 6 elementos, sem a moldura. Depois: plano, emocao, intensidade (1–5), direcao_da_acao e ponto_de_impacto ([y, x])."`
- **O que conferir na resposta:** confira uma amostra dos JSONs contra as folhas numeradas (se não trocou personagem, direção da ação ou ponto de impacto). Lembre que `box_2d` é aproximada. Guarde pergunta e respostas em `_CLAUDE/segundo-olhar/paineis_analise_NN.md`.
Seguir o protocolo da seção 6 das regras comuns.

## Resumo no chat
Curto: quantas páginas fatiadas e quantos quadros catalogados, quais páginas tiveram recorte especial (dupla/sangrada) ou baixa resolução que precisam da atenção do usuário, e os caminhos das folhas numeradas e de `_CLAUDE/paineis/catalogo.md`. Marque a etapa como `aguardando_aprovacao` com `estado.py`.

## Revisão
O usuário devolve pelo ID do quadro ou da página (ex.: "`p03q02` cortou o braço", "junta `p04` e `p05` como página dupla", "`p01q04` é o personagem X, não Y"). Ajuste apenas os recortes ou linhas do catálogo citados, gere nova versão sem apagar o histórico e anote aprendizados em `_CLAUDE/aprendizados.md`.

## Aprovação
Marque `paineis` como `concluido` via `python edicao/scripts/estado.py <pasta do projeto> ...`, diga quantos aprendizados ficaram anotados e sugira `/clear` e `/clipe` (ou `/clipe-roteiro`).

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos originais em `Paginas/` nem outros arquivos do projeto.
- Nunca baixar páginas de mangá de sites de scan.
- Falar com o usuário em português, de forma curta.
