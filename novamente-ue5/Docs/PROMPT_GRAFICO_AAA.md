# NOVAMENTE · Salto gráfico para nível AAA (Unreal Engine 5.8)

Mande junto com este prompt: o render 3D do Luan criança (é o alvo de qualidade), a capa v1 a v3, as fotos do estado atual do jogo e a Bíblia do Abismo.

## 1. Seu papel

Você é o diretor de arte técnico deste projeto. A tarefa agora não é criar sistemas novos. É fazer a imagem na tela sair de "blockout com luz" e chegar em "jogo de estúdio grande". Continue do jeito que já trabalha: uma decisão por ADR (a próxima é a ADR-032), uma etapa por vez, número em todo ajuste e foto como prova.

## 2. Correções de rota (antes de qualquer outra coisa)

- **O "sol baixo o dia todo" da ADR-029 está errado para Manaus.** Veio de um prompt genérico. Manaus fica a 3° do Equador:
  - o sol nasce perto das 6h e se põe perto das 18h o ano inteiro;
  - ao meio-dia fica quase a pino, com sombra curta e dura;
  - a hora dourada dura uns 30 minutos;
  - na maior parte do dia o céu é branco-azulado de umidade;
  - chove forte de repente, principalmente à tarde.

  Troque a regra fixa por luz por cena (seção 6, fase E). O dourado vira exceção de fim de tarde, não padrão.

- **Ghost of Tsushima é só o método visual.** Luz, vento, partículas, céu, silhueta, paleta por lugar e peso da animação. Nada de japonês no conteúdo.
- **O tom é realismo sujo.** A cor pode ser forte, mas tudo tem idade, umidade, barro, poeira e uso. Nada fica limpo nem novo.

## 3. Regras de arquitetura (não negociáveis)

Estas regras existem para nenhuma IA desviar NOVAMENTE para fórmulas genéricas. Qualquer exceção precisa de ADR com o motivo e da aprovação do autor.

- **Zero assets orientais.**
  - Nada de pacotes "oriental", "japanese", "asian village", "samurai", "shrine", "torii", "bamboo forest", "feudal" ou parecidos. Nem como provisório.
  - Do Ghost of Tsushima vem só o método (direção de arte, luz, vento, física, peso). O conteúdo é Manaus.
- **Mixamo está descartado.** Não serve para o rigor físico de MMA: não tem transferência de peso nem contato firme no solo, e o pé desliza.
  - O pipeline de animação é captura de movimento (Rokoko, Move.ai ou estúdio) refinada no Control Rig e aplicada em MetaHumans.
  - Para testar lógica antes da captura, use as animações do Game Animation Sample.
- **A base de movimento é o Game Animation Sample (Motion Matching), não o Lyra.** O Lyra traz rede e sistemas de tiro multiplayer que só poluem um jogo de luta para um jogador.
- **O combate é mão e pé, estilo UFC.** Não existe espada nem sistema de troca de armas. A fonte do combate é o plugin NovamenteCombat (C++):
  - preparação, janela ativa e recuperação de cada golpe;
  - esquiva e Visão do Caos;
  - Motion Warping para o golpe chegar no alvo certo;
  - diretor de combate (queda, nocaute, hit-stop, fichas de ataque em grupo);
  - travamento de alvo e câmera de combate.
- **GAS só com ADR.**
  - Para os tempos exatos de um golpe, janelas curtas de esquiva e acerto preciso, o componente próprio em C++ é mais rápido e confiável.
  - O Gameplay Ability System entra quando o mundo aberto exigir sistemas paralelos de RPG (fôlego, buffs da Sombra, ferimentos, itens). Aí migram só os atributos e efeitos; o golpe continua no plugin.
- **Linguagens.**

  | Linguagem | Para quê |
  |---|---|
  | C++ | Sistemas e desempenho |
  | Blueprint | Montar personagens, AnimBP e ajustes de designer |
  | Python | Ferramentas do editor: montar cenário, criar materiais, fotos de revisão |
  | HLSL | Nós Custom de material e pós-processamento |

  Nada de lógica pesada em Blueprint no Tick.
- **Mundo aberto com World Partition.**
  - O Mutirão é carregado em células, com HLOD para o longe.
  - Data Layers para dia, noite e chuva. Level Instances para os quarteirões do kit modular.
  - PCG para espalhar capim, lixo e detalhe.
  - Sem tela de carregamento dentro do bairro.
- **Calibração antes de efeito.**
  - Exposição e albedo com números, materiais em camadas (reboco descascando, asfalto úmido, barro, poças), vento constante na vegetação e na roupa.
  - Ligar Nanite e Lumen não resolve nada se o material parecer plástico.

## 4. Diagnóstico: por que hoje parece argila (prompt negativo)

As fotos atuais mostram exatamente o que não queremos:

1. **Paredes.** São caixas lisas de uma cor só: sem textura, sem relevo, sem chanfro nas quinas, sem desgaste. Não há sujeira na base, escorrido de chuva, limo nem pintura descascada. Portas e janelas são retângulos chapados, sem batente, sem profundidade, sem grade.
2. **Chão.** Uma cor marrom lisa, sem textura, sem repetição disfarçada, sem rachadura, sem sarjeta, sem poça. O capim são cartões soltos que não se misturam ao chão.
3. **Árvore.** Esfera em cima de cilindro. Vegetação primitiva não pode aparecer em nenhuma foto de revisão.
4. **Céu.** Estourado em branco perto do horizonte (exposição errada) e sem nuvem.
5. **Luz.**
   - O mesmo sol baixo em todo lugar.
   - Nada encosta no chão: sem oclusão de contato, sem sombra de contato.
   - Rebatimento de cor fraco, sombras todas iguais.
6. **Personagem.**
   - É um manequim com pele de plástico: sem poro, sem variação de brilho, sem pele translúcida, olho sem vida.
   - O cabelo é uma touca e a camiseta não tem dobra nem tecido. A bermuda é uma mancha preta.
   - As proporções estão erradas: braço comprido demais, cabeça pequena, ombro e pescoço sem forma. Fica parado duro, como um boneco de testes.
7. **Vazio.** Não há nada que dê escala e vida: fios, postes, grades, portões, caixas-d'água, lixo, gente, bicho.
8. **Sem umidade.** Manaus é úmida. A imagem atual parece deserto de maquete.

Tudo isso vira lista de proibições. Nenhuma foto final pode ter um desses itens.

## 5. O alvo

**O nível mínimo de close é o render 3D do Luan criança:**
- luz dura entrando por um cobogó de concreto, com feixes volumétricos e poeira suspensa;
- reboco áspero e manchado, sombra funda com cor;
- pele com poro, brilho e translucidez;
- camiseta de algodão gasto com a gola canelada amarela e azul;
- cabelo em fios e profundidade de campo curta.

A primeira prova de que o pipeline funciona é recriar essa cena dentro da Unreal, com o Luan em MetaHuman, e deixar as duas imagens lado a lado.

**Da capa vem a atmosfera.** Noite azul e fria, luz quente de poste, contraste alto. Os olhos amarelos da Sombra podem ter qualquer cor de ambiente em volta.

**Do Ghost of Tsushima vem o método:**
- vento em tudo (vegetação, roupa, cabelo, partículas);
- céu com nuvem que conta a hora e o clima;
- silhuetas fortes;
- uma cor dominante e uma de contraste por lugar;
- enquadramento limpo.

**Manaus, Zona Norte, Mutirão e Novo Aleixo, 2017:**
- **Casas:** construídas pelo próprio morador em camadas. Tijolo baiano e bloco de concreto aparentes, reboco pela metade, vergalhão saindo da laje esperando o próximo andar.
- **Telhado e fachada:** telha de fibrocimento, caixa-d'água azul, grade e portão de ferro, muro pintado com cor desbotada e pichação.
- **Rua:**
  - poste de concreto com emaranhado de fios e "gato";
  - calçada quebrada com meio-fio, sarjeta com capim e lixo;
  - barro vermelho e amarelo onde não tem asfalto;
  - asfalto remendado;
  - igarapé poluído no fundo.
- **Vida:** mercadinho, placa de açaí, moto e mototáxi, varal, pipa no céu, cachorro vira-lata, criança de chinelo.

## 6. Ordem de trabalho (substitui os passos 4 a 8 anteriores)

O aspecto de estúdio grande vem primeiro de material, detalhe de geometria e luz calibrada. Partícula, paleta e pós-processamento em cima de argila só decoram argila. Por isso a ordem muda.

### Fase A · Base física: exposição, sol, céu

- **Fazer.**
  - Corrigir a ADR-029 (ADR-032).
  - SkyAtmosphere com névoa de umidade: mais espalhamento Mie.
  - Volumetric Clouds com cúmulos equatoriais.
  - Sky Light com captura em tempo real.
  - Luz direcional com ângulo de fonte de 0,53° (disco do sol) e Contact Shadows ligado.
  - Lumen para luz global e reflexos. Sombras virtuais.
  - Exposição automática por histograma, com limites por cena.
- **Números (EV100 alvo):** meio-dia de sol 14 a 15; nublado 12 a 13; fim de tarde 11 a 12; interior com janela 7 a 9; rua à noite com poste 3 a 5.
  - Sol limpo ao meio-dia perto de 100.000 lux.
  - Céu sem pixel estourado fora do disco do sol e de reflexos.
- **Prova.** Fotos das câmeras de revisão (seção 7) nas horas 7h, 12h, 17h45 e 21h. Visualização de HDR sem céu clipado.

### Fase B · Kit modular do Mutirão (geometria)

- **Fazer.**
  - Trocar as caixas por um kit modular com medidas reais: parede de tijolo e de bloco, reboco, laje com vergalhão, beiral, telha de fibrocimento, janela basculante com grade, portão, muro, calçada com meio-fio, sarjeta, poste com fios, caixa-d'água.
  - Todas as quinas com chanfro de 0,5 a 2 cm.
  - Nada perfeitamente reto: paredes com 1 a 3 cm de torto, porque a casa foi feita pelo morador.
  - Nanite em toda malha estática. Deslocamento do Nanite no chão e nas paredes onde valer.
- **Números.**

  | Elemento | Medida |
  |---|---|
  | Pé-direito | 2,6 a 2,8 m |
  | Porta | 0,8 × 2,1 m |
  | Janela basculante | 1,0 × 1,0 m, a 1,1 m do chão |
  | Muro | 2,0 a 2,5 m |
  | Calçada | 1,2 a 2,0 m |
  | Meio-fio | 15 cm |
  | Rua | 6 a 7 m |
  | Poste | 9 a 11 m, com fios a 7 ou 8 m |

- **Prova.** Plano geral da rua e close de 1 m numa esquina de muro. Mostrar a luz batendo no chanfro.

### Fase C · Materiais em camadas (a maior parte do salto)

- **Fazer.** Um material mestre em camadas:
  1. base (reboco, tijolo, concreto, asfalto, barro);
  2. tinta desbotada e descascando;
  3. sujeira de barro vermelho de 0 a 40 cm do chão;
  4. escorrido preto de chuva debaixo de laje e janela;
  5. limo e mofo verde-escuro nos cantos úmidos.

  Máscaras por pintura de vértice, por posição no mundo e por decals (pichação, mancha, rachadura, cartaz). Folhas de acabamento (trim sheets) para batentes, grades e beirais. Variação em escala grande para quebrar a repetição e mistura por distância. Um parâmetro global de umidade (coleção de parâmetros) que molha todos os materiais junto com a chuva.

- **Números.**
  - Albedo em sRGB: nunca abaixo de 30 nem acima de 240. Asfalto 50 a 70; concreto 110 a 150; reboco claro 170 a 210.
  - Metálico só 0 ou 1.
  - Rugosidade nunca uniforme: pelo menos ±0,15 de variação dentro de uma superfície. Molhado entre 0,05 e 0,2.
  - Densidade de textura: 10,24 px/cm perto da câmera e 5,12 px/cm no fundo. Conferir no modo de visualização de precisão de escala de textura.
- **Fontes.** Megascans e Fab (concreto, reboco, tijolo, asfalto, terra, barro vermelho), Substance 3D Painter e Designer.
- **Prova.** Mesmas câmeras, antes e depois. Visualização "só luz" e "só cor base" lado a lado, para provar que o albedo está calibrado e que a luz não está escondendo a falta de material.

### Fase D · Vegetação de verdade e vento

- **Fazer.**
  - Apagar as primitivas. Usar vegetação real: mangueira, jambeiro, castanholeira, açaizeiro, bananeira, ipê, capim-colonião e braquiária na sarjeta e no terreno baldio, mato alto no lote vazio.
  - Espalhar com PCG, mantendo a sua boa ideia da distribuição copiada do Street View.
  - Vento das árvores integrado ao vento global da ADR-030.
- **Prova.** Plano geral com árvore em primeiro plano, e close do capim encostando no chão sem cartão visível.

### Fase E · Luz por hora e clima

Predefinições de cena:

| Cena | Como é |
|---|---|
| Meio-dia seco | Sol a pino, sombra curta, calor tremendo sobre o asfalto |
| Tarde de chuva | Céu cinza-chumbo, chuva em Niagara, poças com respingo, escorrido nas paredes, tudo molhado pelo parâmetro de umidade |
| Fim de tarde | O único momento dourado, uns 30 minutos |
| Noite de poste | Sódio laranja perto de 2000 K e LED branco de 4000 K nos postes novos, luz azul de TV pelas janelas, fios recortados no céu |

Neblina volumétrica para feixes de luz em interiores e na chuva.

**Prova.** As quatro predefinições nas mesmas câmeras.

### Fase F · Personagens

- **Fazer.**
  - Apagar o manequim de todas as fotos.
  - Luan criança em MetaHuman a partir do render: Mesh to MetaHuman sobre uma escultura ou um escaneamento que siga a referência.
    - Proporção de criança (cabeça maior, ombro estreito).
    - Pele parda clara, quase branca. Cabelo escuro em fios (groom), com cílios e penugem.
    - Pele com perfil de translucidez e textura de qualidade alta.
  - Roupa feita em Marvelous Designer ou com Chaos Cloth: dobra real e trama do algodão no normal map.
    - A camiseta branca é pijama e pode virar a farda, com a gola canelada amarela e azul.
  - Suor e sujeira por parâmetro.
  - Depois, o Luan adulto, a Emma, o Mateus e o Felipe, sempre com a Bíblia e a capa.
- **Prova.** Recriar a cena do render (interior com cobogó, feixes e poeira) e comparar lado a lado. O autor aprova o rosto antes de seguir.

### Fase G · Animação

- **Fazer.**
  - Locomoção com Motion Matching (Game Animation Sample) redirecionada para o esqueleto do MetaHuman.
  - IK de pé sem deslizar, virar no lugar, parado respirando.
  - Olhar seguindo o que importa, mão na parede ao encostar.
  - Rosto com MetaHuman Animator nas falas.
  - Nada de braço duro caído ao lado do corpo.
  - Golpes de MMA por captura, ligados ao NovMoveSet do plugin, com janela de Motion Warping chamada `Strike`.
  - Luta de rua em grupo com o travamento de alvo (soft-lock, trava, troca no analógico) e a câmera de combate do plugin.
- **Prova.** Vídeo de 30 s andando, correndo, parando e virando na rua. Nenhum pé deslizando.

### Fase H · Partículas e rua viva (seus antigos passos 4 e 5)

- **Partículas.**
  - Areia e barro vermelho no vento forte.
  - Calor tremendo sobre o asfalto ao meio-dia.
  - Poeira nos feixes de luz.
  - Chuva com respingo.
  - Mosquitos e insetos em volta dos postes à noite.
- **Rua viva.**
  - Lixo, sacos (inclusive o saco que rasga), o cocô de cachorro que você pediu.
  - Cachorros animados, moto passando.
  - Pipa no céu, varal com roupa no vento.
- **Prova.** Plano geral da rua nas quatro predefinições.

### Fase I · Cor por lugar e pós-processamento (seu antigo passo 6)

Só depois de a luz e o material estarem certos:
- uma cor dominante e uma de contraste por lugar;
- LUTs de gradação para os estados da Cromatologia;
- desfoque de fundo;
- grão leve.

**Proibido usar pós-processamento para esconder falta de material, textura ou luz.**

### Fase J · Desempenho

- 60 qps a 1440p com TSR numa placa média (RTX 3060 ou equivalente).
- Cache de PSO ligado, sem travadas de shader.
- Número de `stat unit` e `stat gpu` ao fim de cada fase.
- Medir com Unreal Insights antes de otimizar.

## 7. Câmeras de revisão

Coloque no mapa seis câmeras fixas, com as tags Rev_01 a Rev_06:

| Câmera | O que mostra |
|---|---|
| Rev_01 | Plano geral da rua do Mutirão |
| Rev_02 | Close de 1 m numa esquina de muro |
| Rev_03 | Chão com sarjeta e calçada |
| Rev_04 | Luan de corpo inteiro |
| Rev_05 | Rosto do Luan a 0,5 m |
| Rev_06 | O interior com cobogó que recria o render |

A cada etapa, faça as fotos (HighResShot 1920×1080) das seis câmeras, antes e depois, lado a lado com a referência. Liste com honestidade o que ainda está pior que a referência.

## 8. Regras de trabalho

- **Etapas.** Uma fase por vez, na ordem. Não avance com o portão da fase anterior reprovado.
- **Registro.** Uma ADR por decisão, com número, motivo e foto.
- **Prova.** Nunca diga que terminou sem as fotos das seis câmeras.
- **Proibido nas fotos finais:**
  - primitiva;
  - rugosidade uniforme;
  - céu branco estourado;
  - objeto flutuando sem contato com o chão;
  - manequim;
  - elemento japonês;
  - bloom, vinheta ou gradação usados como maquiagem.
- **Downloads.** Quando precisar de algo do Fab ou dos Megascans, entregue uma lista exata para o autor baixar: nome do pacote, para que serve, tamanho. Depois integre você.
- **Canon.** Onde a Bíblia não define (rosto adulto, cor de uma casa, figurino), proponha 3 opções em foto antes de escolher.
- **Limites.** Diga cedo o que não dá para fazer só com IA:
  - rosto muito fiel exige escultura ou escaneamento e um artista de personagem;
  - golpe e movimento com peso real exigem captura de movimento;
  - fotos do Mutirão de verdade o autor tira no local, ou vêm do Street View.

## 9. Sua primeira resposta

1. As fotos das seis câmeras como o jogo está hoje, com o diagnóstico da seção 4 conferido item por item.
2. A confirmação das regras de arquitetura da seção 3, com o que no projeto atual as contraria (pacote, animação, sistema) e como sai.
3. A ADR-032 (luz de Manaus no lugar do sol baixo fixo) e o plano da Fase A com os números.
4. A lista de downloads da Fase A até a Fase D para o autor.

Depois execute a Fase A e mostre a prova antes de seguir.
