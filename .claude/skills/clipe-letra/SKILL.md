---
name: clipe-letra
description: "Constrói e renderiza a tipografia animada da letra por seção, sincronizada por palavra com a voz sobre os quadros animados. Use em /clipe-letra, após a clipe-animar."
---

# clipe-letra

Constrói e renderiza a letra animada no HyperFrames com fundo transparente, sincronizada pelo arquivo de alinhamento, e entrega prévias por seção compostas sobre as cenas animadas. Não mexe nas animações dos quadros, não altera o alinhamento (a menos que uma linha esteja fora de tempo, voltando pontualmente à etapa de música) e não aplica efeitos de seção nem sons.

- **Lê:** `_CLAUDE/projeto.json` (versão do HyperFrames, fps, resolução, perfil), alinhamento da letra e grade de batidas (`_CLAUDE/musica/`), letra escrita aprovada, roteiro e posições seguras (`_CLAUDE/roteiro/`), cenas renderizadas (`_CLAUDE/animar/`) e perfil (`edicao/perfis/<nome>/estilo-letra.md`)
- **Escreve:** bloco `letra` no estado, composições HyperFrames e eventos em `_CLAUDE/letra/`, sobreposições transparentes e prévias compostas com música em `_CLAUDE/entregas/letra/`
- **Próximo passo:** `/clipe-efeitos`

Se a etapa `clipe-animar` não estiver `concluido`, pare e sugira terminá-la.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-letra.md`, `.claude/skills/fluxo-de-edicao/guias/hyperframes.md` e `.claude/skills/fluxo-de-edicao/guias/oficio-motion.md`. As decisões criativas abaixo são tendência, não regra; sincronia, grafia e contagem de frames são regras firmes.

- **Ler antes de enfeitar:** máximo ~2 linhas e ~6–7 palavras na tela por vez. Quebre a linha na respiração ou virada de compasso, nunca separando artigo/preposição da palavra seguinte ou nome composto. Tempo mínimo na tela: ~0,25–0,3 s por palavra (nunca menos de ~0,6 s no bloco). Tamanho mínimo: 28 px em 1080p, dentro da área segura (80%) e longe dos rostos das cenas.
- **Formas por seção (4–8 compassos):** *bloco com destaque* (verso rápido), *palavra a palavra* com recentralização (verso lento/cadenciado), *palavra gigante* (frase de efeito/grito), *empilhado* (enumeração), *dobra/fundo* (respostas, menor e de lado). O refrão tem uma forma só, reconhecível, que volta igual ou maior. Vozes diferentes têm cor ou posição constante no clipe inteiro.
- **Sincronia:** a palavra entra no começo do som dela (arquivo de alinhamento), nunca digitada à mão. Entrada curta (3–6 frames); na dúvida, 1 frame adiantada. O bloco troca na virada da linha/corte. Palavra esticada ganha movimento contínuo durante sua duração.
- **Ênfase e contraste:** no máximo uma palavra-chave com punch por linha. Reação leve à batida com parcimônia; se a cena já treme, a letra fica firme. Garanta leitura sobre o quadro mais claro e o mais confuso da cena (contorno, sombra ou placa). Saída rápida (~0,15–0,25 s) ou no corte.
- **Construção no HyperFrames:** uma composição por seção (ou 8–16 compassos), fundo transparente (MOV ProRes 4444), duração da raiz `(N - 0.5) / fps` para cravar `N` frames. CSS embutido no `index.html`, `data-motion-blur="on"` com `data-motion-blur-tier="filter"`, `fromTo` com `immediateRender: false` e `lazy: false`, medição de texto dentro de `document.fonts.ready`. Transforme a primeira forma boa de cada tipo em peça-base reaproveitável.

## Perfil
Antes de começar, leia `edicao/perfis/<nome>/estilo-letra.md` (o nome do perfil está em `_CLAUDE/projeto.json`). Ele decide: fontes titulares e de apoio, cores por voz e de destaque, uso de caixa alta, espessura de contorno/sombra/placa e intensidade de movimento da tipografia.

## Scripts
Na primeira vez que esta etapa rodar num vídeo real, escreva os scripts que faltam em `edicao/scripts/`, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar (dos guias) |
|---|---|---|
| `edicao/scripts/conferir_grafia.py` | Compara todo o texto das composições da letra com a letra escrita aprovada e checa suporte a acentos/cedilha (`ã, õ, ç, é, í, ô`) na fonte. | Não deixar passar troca silenciosa de glifo pelo navegador nem divergência com a grafia oficial. |
| `edicao/scripts/compor_previa_letra.py` | Compõe a sobreposição MOV ProRes 4444 da seção sobre os renders de `_CLAUDE/animar/` com o trecho da música em MP4 (`_v01`, `_v02`…), e gera PNGs de conferência sobre o fundo real. | Confira resolução, 24 fps e total exato de frames; para inspecionar um quadro com `-ss`, extraia o frame do MOV para PNG antes de compor sobre a cena (compor direto do MOV com `-ss` no FFmpeg sai vazio). Nunca sobrescrever entrega anterior. |

## Passo a passo
1. Veja o status e pendências: `python edicao/scripts/estado.py <pasta do projeto> status`.
2. Leia o roteiro, o alinhamento, a letra aprovada e `estilo-letra.md`. Verifique a versão fixada do HyperFrames no estado (`npx --yes hyperframes@<versão> --help`).
3. **Primeira vez de todas (ou primeira seção do vídeo):** construa uma seção curta (ou peça-base do verso e do refrão), rode `conferir_grafia.py`, faça `check` e `snapshot`, renderize o MOV transparente e componha a prévia sobre a cena com música. Entregue ao usuário para validar leitura e estilo antes de produzir o restante das seções.
4. Para cada seção do roteiro:
   - Monte o projeto HyperFrames em `_CLAUDE/letra/<secao>/` lendo as palavras e tempos diretamente do JSON/arquivo de alinhamento (GSAP local em `assets/` se sem rede).
   - Rode `conferir_grafia.py` e `npx --yes hyperframes@<versão> check`.
   - Gere `snapshot` no primeiro som de 3–4 palavras espalhadas e no quadro mais cheio; componha sobre o quadro real mais claro/confuso da cena e olhe (palavra certa acesa? cabe na área segura? longe do rosto? última letra de texto com gradiente inteira?).
   - Renderize em MOV ProRes 4444 transparente e gere a prévia composta em `_CLAUDE/entregas/letra/<secao>_v01.mp4`.
5. Anote em `_CLAUDE/letra/eventos-letra.json` todas as palavras gigantes e frases de efeito (tempo, tipo livre, força, duração e descrição) para guiar `clipe-efeitos` e `clipe-sfx`.

## Segundo olhar
O `montagem.md` liga o segundo olhar no render do refrão e no vídeo final; nesta etapa, use apenas se precisar destravar dúvida de leitura e sincronia num trecho rápido (respeitando o teto de ~R$ 15 no vídeo).
- **Quando:** após compor a prévia do primeiro refrão ou do verso mais rápido, antes de mostrar ao usuário.
- **Uso:** crítica com o modelo leve (`gemini-flash-latest`) via `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py perguntar`.
- **O que mandar:** prévia composta de 20–30 s (cenas + letra + música) com fps alto e o trecho correspondente de `estilo-letra.md`.
- **Pergunta-base:** "Assista com som. Avalie apenas leitura e sincronia da letra: 1) alguma linha passa rápido demais para ler ou cobre rostos? 2) alguma palavra acende visivelmente atrasada ou adiantada em relação à voz? Cite os tempos exatos."
- **O que conferir na resposta:** todo tempo citado, extraindo o quadro correspondente da prévia e comparando com o arquivo de alinhamento.
Seguir o protocolo da seção 6 das regras comuns.

## Resumo no chat
Curto: seções renderizadas, peças-base criadas, qualquer ajuste de posição para fugir de rostos e os caminhos dos vídeos em `_CLAUDE/entregas/letra/`. Marque a etapa como `aguardando_aprovacao` com `estado.py`.

## Revisão
O usuário devolve pelo chat por linha, palavra ou compasso ("compasso 21 atrasado", "palavra 'imortal' maior", "refrão com outra cor").
- Se uma linha única estiver fora de tempo, corrija o tempo dela no arquivo de alinhamento (etapa de música) e re-renderize a seção sem digitar tempos à mão no código.
- Se o feedback for geral ("sem graça", "amador"), refaça a forma da seção em vez de só retocar.
- Gere nova versão (`_v02`, `_v03`…) só das seções afetadas e anote os aprendizados em `_CLAUDE/aprendizados.md`.

## Aprovação
Marque `concluido` no estado, diga quantos aprendizados ficaram anotados em `_CLAUDE/aprendizados.md` e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Nunca digitar tempos de palavras à mão no código da animação nem alterar a grafia aprovada da letra.
- Nunca sobrescrever um render já entregue (`_v01`, `_v02`…).
- Falar com o usuário em português, de forma curta.
