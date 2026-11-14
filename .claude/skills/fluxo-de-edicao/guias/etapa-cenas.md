# Etapas: cenas (o catálogo) e montagem (as cenas na grade)

Duas etapas do clipe musical que usam o mesmo material. O **catálogo** vem antes do roteiro: é o que torna possível escolher. A **montagem** vem depois do roteiro: executa o que foi aprovado.

## Parte A. Cenas: o catálogo do material bruto

O Claude não assiste a horas de episódio. Ele escolhe por um **índice**: cada cena com um número, o que acontece nela e algumas medidas.

### 1. Inventário e alertas
- `ffprobe` em cada arquivo: duração, taxa de quadros, resolução, proporção, codec.
- **Alertas:** taxa diferente da do projeto; taxa variável (gravação de tela, gameplay); barras pretas queimadas; **legenda, logo de emissora ou marca d'água queimados na imagem** (a cena vira "só com recorte" ou "evitar"); resolução baixa demais para o zoom que os efeitos pedem.

### 2. Dividir em cenas
- Um detector de cenas (ex.: PySceneDetect) separa cada plano. Anime tem cortes secos e também fusões e clarões: confira a divisão numa amostra e ajuste a sensibilidade.
- Cada cena ganha um id estável (`c0001`…), o arquivo, o início e o fim no tempo do arquivo de origem.

### 3. Medir cada cena (script)
- **Movimento:** quanto e para onde (fluxo óptico: parado, deriva lenta, ação rápida; direção dominante).
- **O ápice:** o frame em que o movimento muda de repente (o soco acerta, a explosão abre). É ele que casa com a batida.
- **Brilho e cor dominante**, para ordenar por clima e para a continuidade de cor.
- **Rostos** e a área de interesse (onde a letra não pode ficar).
- **Quadros repetidos:** anime é desenhado a cada 2 ou 3 quadros. Cena assim, se for desacelerada, engasga.

### 4. Descrever cada cena
O que os números não dizem: quem aparece, a ação, a emoção, o tipo de plano (close, médio, aberto), a intensidade (1–5).
- **Com o segundo olhar:** o Gemini assiste ao material em blocos e devolve a lista em JSON (`segundo-olhar.md` §9). É muito mais barato que o Claude abrir quadros de cada cena. O Claude casa a lista dele com os cortes medidos pelo script (os tempos dele são aproximados) e confere uma amostra de cada bloco.
- **Sem o segundo olhar:** folhas de contato (3 quadros por cena, numeradas) que o Claude lê em lotes, só do material que a pessoa indicar como promissor. Peça a ela os episódios e os momentos que tem em mente: ela conhece a obra.

### 5. O índice
Uma linha por cena: id, duração, quem, ação, emoção, intensidade, plano, movimento e direção, ápice, restrições. O Claude busca por texto ("close nos olhos", "golpe para a direita, intensidade 5"). Uma folha de contato por episódio fica guardada para conferência.
- Marque as **cenas-herói** (as melhores) com a pessoa. Elas são reservadas para o refrão e o ápice.

## Parte B. Montagem: as cenas na grade

Executa o roteiro aprovado (`etapa-roteiro-clipe.md`): cada compasso com a cena escolhida, cortada e encaixada. Sem letra e sem efeito ainda. É o primeiro corte que a pessoa assiste com a música.

### 1. Corte na grade
- Todo corte cai num ponto da grade (compasso, tempo ou subdivisão), em frames inteiros, calculado pelo script a partir da grade da etapa de música.
- **Na dúvida, o corte vem 1 frame adiantado.** O olho perdoa imagem adiantada; atrasada parece erro.
- **Nem toda batida é corte.** O ritmo dos cortes segue a energia do roteiro. Corte em toda batida, do começo ao fim, cansa em trinta segundos.
- **Duração mínima** de um plano para dar para ver: ~8–10 frames. Menos que isso, só em rajada intencional (ver roteiro).

### 2. O ápice na batida
- O que casa com o acento é o **ápice da cena**, não o início dela. O script posiciona a cena para o frame do ápice cair no frame do acento, e o corte de entrada fica onde der (num ponto da grade antes).
- Se o trecho antes do ápice for curto ou longo demais para a grade, ajuste a velocidade daquele pedaço (até ~±25% passa despercebido) em vez de mover o ápice.

### 3. Velocidade
- **Acelerar** quase sempre funciona. **Desacelerar** cena desenhada a cada 2–3 quadros engasga: prefira congelar o quadro no ápice, ou desacelerar só cenas de movimento contínuo. Interpolação de quadros em anime costuma borrar o traço; teste antes de confiar.
- **Rampa de velocidade** (rápido → lento no ápice → rápido) com o ponto lento no acento. A curva é do `oficio-motion.md`; a entrega no programa depende do que o formato carrega (ver §5).

### 4. Continuidade
- **Direção do movimento:** cenas seguidas andando para o mesmo lado emendam; direções opostas batem. Use o choque de propósito, num acento.
- **Variar o plano:** close → aberto → médio. Três closes seguidos parecem o mesmo plano.
- **Cor e brilho:** salto grande entre cenas vizinhas vira marcador para a finalização (ou o corte ganha um flash, na etapa de efeitos).
- **Não repetir cena** no mesmo clipe, salvo repetição intencional (o refrão que volta com a mesma imagem-marca).
- **Recorte:** material com barras, legenda queimada ou outra proporção é recortado com a área de interesse no quadro. Em vídeo vertical, o recorte segue o assunto.

### 5. Entrega e revisão
- Conforme `entrega-no-editor.md`: as cenas em V1 (e V2 quando houver sobreposição de imagem), a música em A1, **inteira e intocada**. Marcadores na linha do tempo com as seções e os compassos numerados, para a pessoa apontar ("no compasso 33…").
- **Velocidade no XML:** mudança de velocidade constante costuma atravessar; rampa, nem sempre. Faça o teste curto com uma cena acelerada e uma com rampa. O que não atravessar vira trecho pré-renderizado (versionado) ou marcador para a pessoa fazer à mão.
- **Sem programa:** um rascunho em resolução baixa, com o número do compasso e o id da cena queimados no canto, para a revisão.
- **Revisão por compasso ou por cena:** "troca a cena do compasso 17", "c0412 começa antes", "o refrão 2 está fraco". Pedido de troca: ofereça 2–3 alternativas do índice numa folha de contato.
- **Segundo olhar:** crítica do rascunho por seção, com fps alto, perguntando só de sincronia e variedade.
- **Depois de aprovada, a montagem trava.** Letra e efeitos se apoiam nos cortes dela.
