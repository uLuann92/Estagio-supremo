# Etapas: painéis (o catálogo de quadros de mangá) e animar painéis

Para o clipe em que a imagem não vem de vídeo pronto, e sim de **quadros de mangá animados** (o "mangá animado" dos edits de rap geek): o quadro parado é separado em camadas e ganha câmera, profundidade, impacto, tremida, linhas de velocidade, brilho e cor.

No fluxo do clipe musical (`clipe-musical.md`), estas duas etapas ficam no lugar de **cenas** e **montagem**:
- **painéis** (antes do roteiro): cataloga os quadros disponíveis;
- **animar painéis** (depois do roteiro): constrói e renderiza a animação de cada quadro escolhido, já com a duração e os acentos da música. Cada quadro animado vira uma "cena" da montagem.

As curvas e os cuidados gerais são os do `oficio-motion.md`; a ferramenta, a do `hyperframes.md`; a dose de efeito, a do `etapa-efeitos.md`. Aqui fica o que é próprio de quadro de mangá. Existe um exemplo que roda em `../exemplos/painel-animado/` (ver §9).

## 1. De onde vêm as páginas
- **A pessoa aponta a pasta** com as páginas (os volumes digitais dela, capítulos oficiais, arte própria ou encomendada). O fluxo **não baixa mangá de site de scan**: é material pirata, e o risco de bloqueio do vídeo é dela. Vale tudo o que está em `clipe-musical.md` §3.
- **O Claude ajuda a achar o que procurar:** a partir da letra, ele diz que cena da obra casa com cada verso ("a luta do capítulo X; o close do personagem Y") e a pessoa confirma o capítulo. Na dúvida sobre o capítulo, pergunte: não invente número.
- **Qualidade:** página em alta resolução (ao menos ~1600 px de altura por quadro útil depois do zoom). Página pequena pode ser ampliada com um ampliador próprio para desenho (ex.: Real-ESRGAN/Real-CUGAN no modelo de anime; pesquise). Ampliar não inventa traço: confira o resultado num quadro.
- **Tradução:** balões na língua errada são limpos e refeitos (§4), ou o balão fica fora do enquadramento.

## 2. Fatiar e catalogar
- `painel.py fatiar pagina.png --saida paineis/` separa a página em quadros pela calha branca, na ordem de leitura do mangá (direita → esquerda), e gera uma **folha numerada** para conferir. Quadro sangrado (sem moldura), quadros que se invadem e página dupla não saem certos: recorte à mão ou junte as duas páginas antes.
- **Análise de cada quadro** (o Gemini é bom nisso, e funciona no plano gratuito): elementos da frente para o fundo, cada um com caixa, profundidade, o que deveria se mover e as partes móveis; mais o tipo de plano, a emoção, a intensidade, a direção da ação e **o ponto de impacto**. Pergunta-base no `segundo-olhar.md` §9. As caixas dele são aproximadas: servem para apontar, não para recortar.
- **O índice** tem uma linha por quadro: id (`v03c021p07q04`), personagem, ação, emoção, intensidade, plano, direção, impacto, proporção (largo, alto, quadrado) e restrições (balão grande, quadro pequeno demais, traço muito fino).
- **Proporção importa:** um quadro alto num vídeo deitado só aparece em parte. Em vez de brigar, use: a câmera **viaja** pelo quadro (dos pés ao rosto, do rosto ao punho). O índice guarda a proporção para o roteiro escolher sabendo.

## 3. Separar em camadas
É o passo que mais pesa na qualidade, e o que menos se automatiza bem.
- **Quantas:** o mínimo que serve. Quase sempre 2–4: fundo, personagem, o elemento do golpe (punho, espada, energia), balão ou onomatopeia. Cada camada a mais é mais um recorte para errar.
- **A máscara do personagem** (branco = a camada), por ordem de qualidade:
  1. **Modelo de segmentação guiado pela caixa** que o Gemini apontou (ex.: SAM), ou um removedor de fundo treinado em anime (ex.: `rembg` com o modelo `isnet-anime`). Pesquise o estado atual e **teste num quadro real** da obra: em mangá preto e branco, com retícula e linhas de velocidade atravessando o personagem, os modelos erram mais do que em imagem colorida.
  2. **Retoque à mão:** a pessoa corrige a máscara num editor de imagem (5 minutos por quadro-herói valem a pena).
  3. `painel.py mascaras` transforma a resposta do Gemini em máscaras; sem máscara na resposta, ele tenta a silhueta fechada pelo traço dentro da caixa. Serve para balão e formas fechadas; **não** serve para personagem sobre fundo com retícula.
- **Sempre conferir a máscara por cima do quadro** (uma folha com a máscara em vermelho) antes de seguir.
- `painel.py camadas quadro.png --mascara frente.png meio.png --saida camadas/` recorta cada camada (da frente para trás), fecha o buraco no fundo e grava o `camadas.json` com a posição de cada uma.
- **O fundo atrás do personagem é remendo.** O preenchimento automático serve para movimento pequeno. O script avisa quando o buraco passa de ~35% do quadro. Para movimento grande, o fundo precisa ser refeito de verdade: por um modelo de imagem que edita (os do Gemini existem, mas **não têm cota no plano gratuito**; com plano pago, é o melhor caminho para "tire o personagem e complete o fundo"), ou à mão.
- **Três regras do remendo** (cada uma apareceu no teste):
  - uma camada **nunca some nem encolhe** abaixo do tamanho original: atrás dela só há remendo. Ela pode pular, crescer e voltar;
  - o deslocamento de uma camada fica **dentro da folga** do recorte (alguns pixels a poucas dezenas). Passou disso, o remendo aparece na borda;
  - o que precisa **entrar** em cena (um balão que estoura, um golpe que surge) pede fundo limpo de verdade naquele lugar.

## 4. Limpar e colorir (opcional; do perfil)
- **Balões e onomatopeias:** ficam (como parte do desenho, animados), saem (limpos com preenchimento) ou são refeitos em tipografia animada. Decisão do perfil; a letra da música costuma substituir os balões.
- **Cor:** o gênero usa muito o preto e branco com **um acento de cor** (o brilho do golpe, os olhos, a aura) em modo de mistura, por camada. Colorir o quadro inteiro é outro trabalho (modelo de imagem ou à mão) e muda o custo: combine antes.
- **Retícula:** ampliar ou reduzir muito gera ondas (moiré). Confira num quadro do render, no zoom mais aberto e no mais fechado.

## 5. O repertório de movimento
| Movimento | Como é | Casa com |
|---|---|---|
| **Aproximação lenta** | escala linear contínua, numa propriedade só dela (2–8% no trecho) | dá vida a qualquer quadro; fica por baixo de tudo |
| **Paralaxe** | as camadas da frente deslizam contra a câmera, proporcional à profundidade (frente ~10–16%, meio ~5%) | sensação de espaço; viagens de câmera |
| **Viagem pelo quadro** | a câmera vai de um ponto de interesse a outro (rosto → punho) | quadros altos ou largos; contar a ação dentro do quadro |
| **Antecipação** | o personagem recua e a câmera abre um pouco, 6–10 frames antes do golpe (`power2.out`) | prepara o impacto; sem ela, o golpe não pesa |
| **Quadro de impacto** | 1–3 frames em negativo, alto contraste ou preto e branco chapado, no frame do acento. **Tudo congela neles** (a parada do golpe) | o ápice do golpe |
| **Chicote de câmera** | salto para o ponto de impacto e assentamento em `expo.out` (0,4–0,6 s), com zoom chegando maior e cedendo | logo depois do quadro de impacto |
| **Tremida** | deslocamento + um pouco de giro e de escala, com sorteio de semente fixa, decaindo em 8–12 frames | depois do impacto; precisa ser **medida** (§8) |
| **Linhas de velocidade** | desenhadas por código, a partir do ponto de impacto, redesenhadas a cada 2 frames | golpe, corrida, susto |
| **Brilho e aura** | degradê colorido em modo de mistura, atrás do elemento do golpe; pulsa no acento | energia, poder |
| **Pulo de camada** | a camada cresce 15–40% e volta com mola (`back.out`) | balão, onomatopeia, o elemento do golpe |
| **Deformação** | malha ou deslocamento em cabelo, capa, fumaça, fogo; respiração leve no tronco | quadro calmo que precisa de vida; pede máscara boa |
| **Partículas** | poeira, faíscas, detritos, na direção do golpe | preenche o pós-impacto |
| **Mergulho de saída** | zoom acelerando (`expo.in`) até um clarão; o próximo quadro chega freando | emenda dois quadros |
| **Passagem entre quadros** | a câmera desliza de um quadro ao vizinho da mesma página, ou os quadros entram como recortes | sequência de ação da mesma página |

- **Quadro a quadro, como no anime:** tremida e linhas redesenhadas a cada 2 frames ficam mais "desenhadas" que suaves demais. É gosto: vai no perfil.
- **Um golpe tem cinco tempos:** espera → antecipação → impacto (quadros parados) → reação (chicote, tremida, linhas, brilho) → assentamento. Faltando um, o impacto não convence.
- **O acento da música é o frame do quadro de impacto.** A antecipação termina nele; a reação começa nele.

## 6. Câmera sobre um quadro
- **O quadro nunca mostra a borda.** O zoom mínimo é o que cobre a tela com margem (moldura do quadro + folga da tremida); o foco da câmera é limitado ao que cabe naquele zoom. Um ponto de interesse colado na borda (um punho no canto) não vai ao centro: ele fica no terço. Planeje com isso.
- **A câmera é uma transformação só** sobre o "mundo" (o quadro inteiro), com origem no foco. Camadas, paralaxe e tremida são calculados **num lugar só**, a partir de um objeto de estado animado. Vários tweens soltos em elementos diferentes brigam e saem diferentes no render (`hyperframes.md`, armadilhas).
- **Resolução:** zoom máximo × largura do vídeo ≤ largura do quadro original, ou o traço borra. Num mergulho rápido, borrar passa; num close parado, não.
- **Quando a cena treme, a letra fica firme** (e vice-versa): a letra é outra camada, fora do mundo.

## 7. Construir e renderizar
- **Um projeto por quadro animado** (ou por sequência da mesma página), com a duração em compassos e os tempos dos acentos vindos da grade da etapa de música. Os tempos entram como dados no topo do código, nunca espalhados.
- **Peças-base desde o primeiro quadro bom:** a câmera com limite, a tremida com semente, as linhas de velocidade, o quadro de impacto, o brilho. O próximo quadro reaproveita e só muda os dados (pontos de interesse, profundidades, tempos).
- **Ciclo:** `check` → `snapshot` nos tempos-chave (antes, antecipação, cada frame de impacto, reação, abertura, saída) → **olhar a folha** → render → medir (§8).
- **Formato:** cena cheia, na taxa de quadros do projeto. A letra e os efeitos de seção entram depois, por cima.

## 8. Conferir (medir, e só então perguntar)
- **A tremida existe?** Um script mede o deslocamento global quadro a quadro (correlação de fase). Tremida de verdade aparece como deslocamentos de **sinal alternado**, decaindo. Deslocamento sempre para o mesmo lado é só a câmera assentando.
- **O remendo aparece?** Olhe os frames de maior deslocamento de cada camada (antecipação, pulo).
- **A borda aparece?** Olhe o zoom mais aberto e o pico da tremida.
- **Segundo olhar:** peça a crítica do trecho com fps alto, dizendo o que foi planejado e proibindo avaliar o desenho. No teste desta skill, ele acertou o que faltava na primeira versão (a tremida não se lia) e sugeriu coisas úteis (parada do golpe, desfoque de movimento no chicote). Na segunda, **repetiu que não havia tremida nem antecipação quando a medida mostrava as duas**. É por isso que a regra é: a impressão dele diz onde medir; a medida decide.

## 9. O exemplo que roda
`exemplos/painel-animado/`: um quadro de teste (desenho próprio, simples de propósito) em 4 camadas, com aproximação lenta, antecipação, quadro de impacto, chicote, tremida com semente, linhas de velocidade, brilho de cor, pulo de camada e mergulho de saída, sincronizado em 140 BPM. Passou no `check` e renderizou no HyperFrames 0.9.45.
- Serve de **ponto de partida das peças-base**, não de estilo. O estilo vem das referências da pessoa.
- Para rodar: crie um projeto com `hyperframes init`, troque o `index.html` e a pasta `assets/` pelos do exemplo, `check`, `snapshot`, `render`.

## 10. Revisão
- Por quadro e por tempo: "o q07 precisa de mais peso", "a câmera do q12 chega tarde", "menos brilho".
- "Sem peso" ou "parado" pede rever os cinco tempos do golpe (§5), não aumentar tudo.
- Máscara ruim não se conserta na animação: volta ao §3.
- O que ficar bom vira item do catálogo do perfil (`catalogo.md`) e peça-base.
