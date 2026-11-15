---
name: clipe-animar
description: "Separa em camadas e anima no HyperFrames cada quadro de mangá escolhido no roteiro, no tempo da música. Use em /clipe-animar, após a clipe-roteiro."
---

# clipe-animar

Separa cada quadro escolhido no roteiro em camadas (fundo limpo pelo Gemini + máscaras por diferença) e constrói a animação em código no HyperFrames, sincronizada com os compassos e acentos da música. Entrega cada cena renderizada em MP4 (1920×1080, 24 fps) e um vídeo do trecho montado com a música para revisão. Não coloca a letra da música, os efeitos de seção nem os efeitos sonoros. Pode rodar por trecho (ex.: só o refrão 1).

- **Lê:** `_CLAUDE/projeto.json` (versão do HyperFrames, perfil, música, painéis, roteiro), `_CLAUDE/musica/` (grade de batidas e acentos), `_CLAUDE/paineis/` (quadros recortados e análises JSON), `_CLAUDE/roteiro/` (plano com tempos, quadros e movimentos), `edicao/perfis/<perfil>/`
- **Escreve:** bloco `animar` no `_CLAUDE/projeto.json`, camadas e projetos HyperFrames em `_CLAUDE/animar/`, eventos para som em `_CLAUDE/animar/eventos-som.json`, entregas em `Renders/cenas/` e `Renders/previas/`
- **Próximo passo:** `/clipe-letra`

Se `roteiro` não estiver `concluido` no estado, pare e sugira rodar `/clipe-roteiro`.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-paineis.md` (§3 a §10) e `.claude/skills/fluxo-de-edicao/guias/hyperframes.md`. Decisões criativas são tendência, não regra; sincronia e limites técnicos são regras firmes.
- **Camadas mínimas (2–4):** fundo, personagem, elemento do golpe, eventual onomatopeia. Balões saem (a letra ocupará o lugar). Elemento ligado ao corpo fica na mesma camada; se o punho precisa pular no impacto, use uma cópia por cima.
- **Fundo limpo primeiro:** peça ao `gemini-3.1-flash-image` para remover personagem, golpe e balões continuando o fundo original sem redesenhar o resto. Gere máscaras por diferença (`painel.py mascaras --limpo`) e recorte (`painel.py camadas --fundo-limpo`). Sempre confira a folha de máscara em vermelho e o aviso de diferença fora do buraco.
- **Cinco tempos do golpe:** espera → antecipação (6–10 frames antes, `power2.out`) → impacto (1–3 frames parados em alto contraste/negativo cravados no acento da música) → reação (chicote em `expo.out`, tremida com semente fixa decaindo quase linear por 8–14 frames, linhas de velocidade, brilho de cor) → assentamento.
- **Câmera única e estado central:** calcule câmera, paralaxe e tremida num único `onUpdate` a partir de um objeto de estado animado (parta de `.claude/skills/fluxo-de-edicao/exemplos/painel-animado/`). Nunca mostre a borda do quadro (limite foco e zoom mínimo com folga para a tremida). Zoom máximo × 1920 ≤ largura do quadro original em closes parados.
- **HyperFrames:** use a versão fixa do vídeo (`npx --yes hyperframes@<versão>`). Duração da raiz `(N - 0.5) / 24`. CSS embutido no `index.html`, GSAP local se sem rede, `data-motion-blur="on"` com `data-motion-blur-tier="filter"`, `lazy: false` em todo tween. Anote golpes, chegadas e chicotes em `_CLAUDE/animar/eventos-som.json`.

## Perfil
Leia em `edicao/perfis/<perfil>/`:
- `estilo.md` ou equivalente: cadência de redesenho (ex.: 2 em 2 frames para tremida e linhas), intensidade de câmera, paralaxe e paleta de acento de cor sobre o preto e branco.
- `catalogo.md`: peças-base de código e movimentos já aprovados em vídeos anteriores para reaproveitar.

## Scripts
Na primeira vez que a etapa rodar num vídeo, escreva os scripts que faltam em `edicao/scripts/`, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar |
|---|---|---|
| `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py imagem` | Gera `fundo_limpo` tirando personagem/balões (`--midia`, `--saida`, `--pedido`). | Modelo devolver tamanho diferente ou redesenhar fora do buraco; se a diferença externa vier alta, pedir de novo mais duro; vigiar o teto de ~R$ 15 do vídeo. |
| `python .claude/skills/fluxo-de-edicao/ferramentas/painel.py` | `mascaras` (com `--json` e `--limpo`) e `camadas` (com `--mascara` e `--fundo-limpo`). | Cortar membro ligado em linha reta; esquecer de olhar a folha de conferência da máscara; usar fundo remendado em camada que encolhe ou anda longe. |
| `python edicao/scripts/medir_cena.py` *(escrever na 1ª vez)* | Rastreia detalhe fixo por casamento de padrão para medir tremida, checa bordas vazias, moiré e confirma frames/fps do MP4. | Confundir assentamento (anda para um lado só) ou linhas de velocidade com tremida real (precisa ir e voltar ≥ 8 frames, amplitude inicial ≥ 1,5% da largura). |
| `python edicao/scripts/montar_trecho.py` *(escrever na 1ª vez)* | Concatena as cenas renderizadas do trecho com a faixa de música correspondente em `Renders/previas/`. | Deslizamento de sincronia por arredondamento de frames; sobrescrever prévia anterior (usar `_v01`, `_v02`). |

## Passo a passo
1. Confira status e pendências (`python edicao/scripts/estado.py <pasta> status`) e defina com o usuário qual trecho animar (recomendado começar pelo primeiro refrão).
2. Para cada quadro do trecho, gere o fundo limpo com `gemini.py imagem`, extraia máscaras e camadas com `painel.py`, e inspecione a folha da máscara e as camadas recortadas.
3. Crie o projeto da cena em `_CLAUDE/animar/<id_cena>/` a partir de `.claude/skills/fluxo-de-edicao/exemplos/painel-animado/`. Configure no topo do código os tamanhos, posições do `camadas.json`, pontos de interesse, profundidades e tempos exatos dos acentos vindos da música.
4. Rode `npx --yes hyperframes@<versão> check` até zerar erros, tire `snapshot --at <tempos-chave>` (antes, antecipação, frames de impacto, reação, abertura, saída) e **olhe os quadros** (enquadramento, remendo, moiré).
5. Renderize em 1920×1080 a 24 fps (`npx --yes hyperframes@<versão> render --fps 24`), salve em `Renders/cenas/<id_cena>_v01.mp4` e rode `medir_cena.py` para comprovar a tremida e ausência de borda.
6. Monte a prévia do trecho com a música em `Renders/previas/<trecho>_v01.mp4`. **Primeira vez de todas:** faça de 1 quadro curto primeiro, peça para o usuário conferir, anote no arquivo de validação e só então siga para o resto do trecho.

## Segundo olhar
- **Quando:** após montar o render do primeiro refrão (ou trecho-chave), antes de mostrar ao usuário.
- **Uso:** crítica com o modelo capaz (`gemini-4-argon`) via `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py perguntar`.
- **O que mandar:** o vídeo do trecho (`Renders/previas/<trecho>_v01.mp4`) em 24 fps, o recorte do roteiro daquele trecho e o resumo do perfil.
- **Pergunta-base:** "Avalie o enquadramento, a entrada e saída de elementos, a leitura do impacto (antecipação, parada, chicote, paralaxe) e a sincronia com a música neste trecho. Proibido avaliar o traço do mangá. Aponte problemas com o tempo exato."
- **O que conferir na resposta:** extraia e olhe um quadro de todo tempo citado. **Ignore** reclamações de "falta de tremida" se `medir_cena.py` provou que há vai-e-vem ≥ 8 frames (o modelo não enxerga tremida rápida; avise o usuário se houver discordância).
Seguir o protocolo da seção 6 das regras comuns.

## Resumo no chat
Curto: quais quadros/trecho foram animados, o que as medidas e o segundo olhar apontaram, o que precisa da atenção do usuário e o caminho em `Renders/previas/`. Marque a etapa (ou o trecho) como `aguardando_aprovacao`.

## Revisão
O usuário devolve por quadro ou tempo ("c04 precisa de mais peso", "câmera da c07 chega tarde", "apareceu recorte no braço"). Ajuste só as cenas citadas: se for "sem peso", revise os 5 tempos do golpe; se for recorte ruim, volte às máscaras (§3 do guia). Gere `_v02` sem sobrescrever `_v01` e anote aprendizados em `_CLAUDE/aprendizados.md` e peças boas no `catalogo.md`.

## Aprovação
Quando todos os trechos do roteiro estiverem aprovados, marque `animar` como `concluido` no estado, diga quantos aprendizados ficaram anotados e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto, nem sobrescrever renders já entregues (`_v01`, `_v02`).
- Falar com o usuário em português, de forma curta.
