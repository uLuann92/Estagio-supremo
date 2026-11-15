---
name: clipe-roteiro
description: "Planeja o clipe inteiro compasso a compasso: curva de energia, quadro de mangá, movimento pretendido, tratamento da letra e efeitos. Use em /clipe-roteiro, após a clipe-paineis."
---

# clipe-roteiro

Planeja o clipe inteiro compasso a compasso: curva de energia por seção, qual quadro do mangá entra em cada corte, como a câmera e as camadas vão se mover (em palavras), como a letra aparece e onde entram os efeitos e transições. Não recorta camadas nem anima nada: propõe, compara com o segundo olhar, ajusta com o usuário e grava.

- **Lê:** `_CLAUDE/projeto.json` (blocos `briefing`, `musica`, `paineis`, `perfil`), mapa da música e letra alinhada em `_CLAUDE/musica/`, índice de quadros e miniaturas em `_CLAUDE/paineis/`, perfil em `edicao/perfis/<perfil>/`
- **Escreve:** bloco `roteiro` em `_CLAUDE/projeto.json` (ids estáveis `rt001`, `rt002`…), `_CLAUDE/roteiro/curva.md`, `_CLAUDE/roteiro/roteiro.md`, folhas de contato por seção em `_CLAUDE/roteiro/folhas/`
- **Próximo passo:** `/clipe-animar`

Se `clipe-paineis` (ou `clipe-musica`) não estiver `concluido`, pare e sugira terminá-la.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-roteiro-clipe.md` e `.claude/skills/fluxo-de-edicao/guias/etapa-paineis.md` (§2 e §5). Decisões criativas são tendência, não regra:

- **Curva antes dos detalhes:** monte uma tabela curta por seção (arco emocional em uma frase, ritmo de corte, presença da letra, dose de efeito). Escalada até o fim: o último refrão é maior que o primeiro; o maior momento do clipe é um só. Depois de trecho forte, dê respiro.
- **Ritmo por seção (tendência; números vêm do perfil):** intro lenta (2–4 compassos/quadro); verso 1–2 compassos (meio nas rimas fortes); pré-refrão acelerando (1 → 1/2 → 1 tempo) até o acento; entrada do refrão com quadro-herói cravado na batida; refrão por tempo ou a cada 2 tempos; pausa da música com corte seco, congelamento ou preto; ponte mais lenta e emotiva. Rajadas (2–4 frames) só em subida, terminando no acento, poucas vezes. Refrão que volta pode repetir a estrutura de cortes com quadros novos.
- **Casar quadro e letra:** literal nas palavras-chave (golpe, nome, lugar com ápice na palavra); clima do verso no resto (não legendar cada linha). Respeite quem canta e dê prioridade aos quadros pedidos no briefing.
- **Proporção e movimento pretendido:** em vídeo 16:9 (1920×1080), quadro alto ou largo pede viagem de câmera (ex.: dos pés ao rosto, do rosto ao punho). Anote em palavras o movimento de cada quadro (aproximação lenta, paralaxe, viagem, ou os 5 tempos do golpe: espera → antecipação → impacto no acento → reação com chicote/tremida/linhas/brilho → assentamento) e se exige fundo limpo completo.
- **Letra no plano:** defina por seção quanto aparece e o tratamento (bloco com destaque, palavra a palavra, palavra gigante). Refrão tem tratamento fixo e reconhecível; versos variam. Posicione longe de rostos e áreas de interesse apontadas no índice. Escolha 3 a 6 frases de efeito no clipe todo para a letra ser protagonista (o quadro recua).
- **Efeitos e transições em palavras:** um protagonista por momento (se a letra brilha, efeito mínimo no quadro, e vice-versa). Anote repertório por seção, efeitos nos acentos marcados e transições entre seções (mergulho de saída, clarão, corte seco no silêncio).
- **O que falta (assets):** nunca troque quadro que falta por algo genérico em silêncio. Liste quadros ausentes (perguntando ao usuário em que capítulo estão), fontes, texturas ou partículas.

## Perfil
Leia em `edicao/perfis/<perfil>/` antes de propor:
- Ritmo de corte e identidade: compassos por quadro em cada seção, uso de rajadas e estrutura de refrão.
- Letra: quanto aparece, tratamentos preferidos e estilo das frases de efeito.
- Efeitos e mangá animado: dose de efeito por seção, uso de acento de cor e tratamento dos balões (no padrão, balões saem para dar lugar à letra).

## Scripts
Na primeira vez que a etapa rodar num vídeo real, escreva os scripts que faltam em `edicao/scripts/`, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar |
|---|---|---|
| `python edicao/scripts/estado.py <projeto> ...` | Lê e atualiza `_CLAUDE/projeto.json` | Nunca perder itens já aprovados ao regravar o bloco `roteiro`; manter ids estáveis (`rt017` para o compasso/corte 17). |
| `python edicao/scripts/folha_roteiro.py` (escrever no 1º vídeo) | Monta folha de contato das miniaturas dos quadros escolhidos, na ordem do roteiro, rotuladas com `rtNNN`, compasso, tempo, id do quadro (`v..c..p..q..`) e trecho da letra | Não esticar proporção original do quadro; numerar legível; destacar onde falta quadro; nunca sobrescrever folha anterior (`folha_refrão1_v1.jpg`, `v2.jpg`). |

## Passo a passo
1. Confira status e pendências: `python edicao/scripts/estado.py <pasta do projeto> status`. Verifique se `clipe-musica` e `clipe-paineis` estão `concluido`.
2. Leia o briefing, o mapa da música (BPM, compassos, seções, acentos, letra alinhada), o índice de quadros (`_CLAUDE/paineis/`) e os arquivos do perfil.
3. Escreva a **curva de energia** por seção em `_CLAUDE/roteiro/curva.md` e liste desde já qualquer quadro ou asset que falte no índice.
4. Mostre a curva de energia e a lista de faltas ao usuário no chat e **espere o "sim"** antes de detalhar os compassos.
5. Aprovada a curva, rascunhe o roteiro do **primeiro refrão** (compasso, tempo, id do quadro, movimento pretendido, letra, efeito) e rode o **Segundo olhar** (parecer independente) antes de mostrar ao usuário.
6. Compare os dois pensamentos, ajuste o rascunho, gere a folha de contato do primeiro refrão e mostre ao usuário (roteiro + resumo da comparação + folha).
7. Aprovado o primeiro refrão, planeje as demais seções (usando crítica leve no segundo olhar se necessário), gere as folhas de contato em `_CLAUDE/roteiro/folhas/` e grave tudo em `_CLAUDE/roteiro/roteiro.md` e no bloco `roteiro` de `_CLAUDE/projeto.json`. **Primeira vez de todas:** valide o formato da tabela e da folha de contato do 1º refrão com o usuário, anote no arquivo de validação e só então siga para o resto do clipe.

## Segundo olhar
- **Quando:** (1) logo após rascunhar o primeiro refrão, antes de mostrar ao usuário; (2) opcionalmente, após rascunhar o restante do roteiro.
- **Uso:** (1) **parecer independente** com o modelo capaz (`gemini-4-argon`); (2) **crítica** com o modelo leve (`gemini-flash-latest`). Chame via `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py perguntar ...`.
- **O que mandar:** no parecer independente do 1º refrão, envie a música (`Musica/`), o mapa da música, a letra, o índice de quadros (`_CLAUDE/paineis/`) e o resumo do perfil — **sem** o rascunho do Claude. Na crítica do restante, envie o roteiro completo + mapa + índice. Respeite o aviso de teto (~R$ 15 no vídeo).
- **Pergunta-base:** para o 1º refrão: *"Com base no mapa da música, no áudio, na letra, no índice de quadros e neste perfil, proponha o roteiro compasso a compasso para o primeiro refrão (tempos exatos onde sente os acentos, id do quadro em cada corte, movimento de câmera/camadas, tratamento da letra e efeito)."*
- **O que conferir na resposta:** se os ids de quadros citados existem no índice, se a proporção de cada quadro permite o movimento sugerido e se os tempos batem com a grade de compassos. Guarde o retorno em `_CLAUDE/segundo-olhar/` e apresente o resumo dos dois pensamentos ao usuário.
Seguir o protocolo da seção 6 de `.claude/skills/clipe/regras-comuns.md`.

## Resumo no chat
Curto: a curva aprovada, o resumo do roteiro por seção (destacando onde os dois pensamentos concordaram ou divergiram no refrão), os quadros/assets que faltam e os caminhos de `_CLAUDE/roteiro/roteiro.md` e das folhas em `_CLAUDE/roteiro/folhas/`. Marque a etapa como `aguardando_aprovacao`.

## Revisão
O usuário devolve por id ou compasso (`rt017 troca pelo quadro q08`, `compasso 25 mais calmo`, `risca o flash do rt033`). Ajuste **só** o que foi citado, preservando no `_CLAUDE/projeto.json` os compassos já aprovados. Gere nova versão da folha de contato sem sobrescrever a anterior e anote aprendizados de gosto/ritmo em `_CLAUDE/aprendizados.md`.

## Aprovação
Marque `clipe-roteiro` como `concluido` em `_CLAUDE/projeto.json`, diga quantos aprendizados ficaram anotados em `_CLAUDE/aprendizados.md` e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Nunca animar ou recortar camadas nesta etapa; aqui mudar é barato.
- Nunca inventar número de capítulo nem substituir silenciosamente um quadro pedido que falta no índice.
- Falar com o usuário em português, de forma curta.
