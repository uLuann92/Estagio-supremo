# NOVAMENTE · Prompt de Personagens: corpos, templates e o rosto do Luan

## Como usar (para o autor)

- Este prompt é separado do Prompt AAA+. Abra uma sessão só para ele.
- Mande o texto inteiro como primeira mensagem, com as imagens anexadas: o render do Luan (a prancha das quatro vistas e o close) e a capa.
- Antes, no projeto:
  1. rode `python claude-kit/instalar.py <pasta do .uproject>`, que copia os scripts de medida;
  2. tire as fichas do rosto:
     ```
     python Scripts/medidas_rosto.py --ficha Referencias/luan_crianca_close.jpg --out Referencias/ficha_luan_close.json
     python Scripts/medidas_rosto.py --ficha Referencias/luan_crianca_frente.jpg --out Referencias/ficha_luan_frente.json
     python Scripts/medidas_rosto.py --ficha Referencias/luan_crianca_34.jpg --out Referencias/ficha_luan_34.json
     ```
  3. sele: `python .claude/hooks/exigir_prova.py --selar`.

---

## 1. O escopo: três coisas e só isso

1. **Corpos padrão proporcionais, completos da cabeça ao pé:** mulher adulta, homem adulto e garoto de 13 a 14 anos, magros.
2. **Uma biblioteca de templates** para montar qualquer personagem por partes:
   - rosto por região, cabelo, sobrancelha e pelos;
   - braços, pernas, barriga, cintura, ombros, peito, costas e postura;
   - mãos, pés, pele, olhos e dentes;
   - roupa em camadas sobrepostas e textura de tecido.
3. **O rosto do Luan refeito 100%** com as medidas do rosto original.

Fora do escopo: cenário, luz de cena, combate, animação de jogo, efeitos, interface e som. As exceções são a sala de lookdev, o provador e a animação de teste de roupa, que servem para medir. Se aparecer algo de fora, anote numa linha "fora do escopo" no fim da resposta e não faça.

## 2. Seu papel

Você é o supervisor de personagens de um estúdio AAA. Reúne o anatomista, o escultor técnico, o groomer (cabelo e pelos), o figurinista e o lookdev. Número vence gosto, e a referência vence tudo.

## 3. As referências

### 3.1 O Luan aos 13–14 anos: o render (a única referência de rosto)

Quatro vistas (frente, costas, perfil, três quartos) e um close, na mesma sala e com a mesma luz.

- **Rosto.**
  - Garoto magro de 13 a 14 anos. Rosto oval, bochecha ainda cheia, queixo pequeno e arredondado, mandíbula suave.
  - Sobrancelhas escuras, quase retas, de espessura média.
  - Olhos amendoados e grandes, com dobra na pálpebra de cima. Íris avelã (castanho com fundo esverdeado) com anel escuro na borda. Leve olheira.
  - Nariz reto com ponte baixa a média, ponta arredondada e narinas pequenas.
  - Lábio de cima fino com o arco marcado; lábio de baixo mais cheio e rosado.
  - Orelhas médias e um pouco salientes, translúcidas contra a luz.
  - Pele parda clara, quase branca, com fundo quente, rosado nas bochechas e no nariz, pintinhas discretas.
- **Expressão da referência.** Espanto: boca entreaberta mostrando os dentes de cima, sobrancelha levantada, olho aberto.
- **Cabelo.** Castanho muito escuro, curto na nuca e nas laterais, mais longo em cima (4 a 6 cm), penteado para a frente, franja curta e irregular, redemoinho no alto, fios soltos contra a luz.
- **Corpo e roupa.**
  - Pescoço fino, ombros estreitos.
  - A farda: camiseta branca de algodão velho, já creme, de manga curta. Malha com bolinhas. Gola canelada creme com listra amarela entre dois filetes azuis, e um filete na costura do ombro.

### 3.2 A capa: referência secundária

Serve só para o que a capa diz sobre os personagens que os templates vão montar depois. Não é fonte de medida.
- O Luan adulto: cabelo preto ondulado e desgrenhado, barba e bigode ralos, olheira funda, magro.
- A garota ruiva: cabelo ruivo longo e ondulado, pele clara.
- O Mateus: camisa amarela 10, cabelo escuro cacheado, pele parda.

### 3.3 A ficha de medidas do rosto do Luan (tirada do render)

Medida com `Scripts/medidas_rosto.py`: 478 pontos do MediaPipe, alinhados pela linha das pupilas.
- **Unidade:** a distância entre os cantos externos dos olhos. Os centímetros são estimativa, com 6,0 cm entre as pupilas (13 a 14 anos).
- **Duas imagens:** o close é a ficha principal. A vista de frente é outra imagem do mesmo rosto e confere a primeira. Entre as duas, o erro médio é de 0,9% e nenhuma medida passa de 1,8%. Esse é o ruído da medição; a tolerância de 3% fica acima dele.

**Identidade** (osso, olho, nariz, larguras; valem sempre):

| Medida | Close | Frente | cm (close) | O que é |
|---|---|---|---|---|
| dist_pupilas | 0,7058 | 0,7021 | 6,00 | centro a centro das pupilas |
| largura_olho (dir / esq) | 0,3086 / 0,3094 | 0,3102 / 0,3150 | 2,62 / 2,63 | canto a canto de cada olho |
| distancia_entre_olhos | 0,3833 | 0,3764 | 3,26 | entre os cantos internos |
| largura_iris | 0,1511 | 0,1517 | 1,28 | diâmetro da íris |
| largura_testa | 1,3446 | 1,3383 | 11,43 | testa, na altura das entradas |
| largura_temporas | 1,5183 | 1,5176 | 12,91 | têmporas, na linha dos olhos |
| largura_macas | 1,4792 | 1,4793 | 12,58 | maior largura do rosto |
| largura_mandibula | 1,0866 | 1,0839 | 9,24 | ângulo da mandíbula |
| largura_mandibula_baixa | 0,9456 | 0,9433 | 8,04 | entre o ângulo e o queixo |
| largura_queixo | 0,2728 | 0,2745 | 2,32 | queixo |
| largura_ponte_nariz | 0,1664 | 0,1642 | 1,41 | ponte entre os olhos |
| largura_nariz | 0,4371 | 0,4408 | 3,72 | asas do nariz |
| largura_sobrancelha (dir / esq) | 0,4768 / 0,4560 | 0,4740 / 0,4537 | 4,05 / 3,88 | ponta de fora à de dentro |
| entre_sobrancelhas | 0,3499 | 0,3466 | 2,97 | vão entre as sobrancelhas |
| testa_ate_glabela | 0,3109 | 0,3165 | 2,64 | alto da testa medida ao meio das sobrancelhas |
| glabela_ate_base_nariz | 0,7401 | 0,7324 | 6,29 | terço médio |
| comprimento_nariz | 0,5272 | 0,5230 | 4,48 | raiz à base do nariz |
| raiz_ate_ponta_nariz | 0,4460 | 0,4420 | 3,79 | raiz à ponta |
| pupilas_ate_base_nariz | 0,4675 | 0,4599 | 3,97 | linha das pupilas à base do nariz |
| filtro | 0,1631 | 0,1612 | 1,39 | base do nariz ao lábio de cima |
| inclinacao_olhos | 3,6° | 4,0° | | canto externo acima do interno |
| angulo_mandibula_frontal | 143,4° | 143,7° | | ângulo da mandíbula visto de frente |
| quintos | 4,79 | 4,73 | | largura do rosto ÷ largura do olho |
| mandibula_por_macas | 0,735 | 0,733 | | mandíbula ÷ maçãs |
| nariz_por_entre_olhos | 1,14 | 1,17 | | nariz ÷ distância entre os olhos |

**Expressão** (só contam quando a expressão da referência é repetida no rig):

| Medida | Close | cm | O que é |
|---|---|---|---|
| largura_boca | 0,4684 | 3,98 | canto a canto |
| arco_do_cupido | 0,1545 | 1,31 | picos do lábio de cima |
| labio_superior / labio_inferior | 0,0762 / 0,1235 | 0,65 / 1,05 | altura de cada lábio |
| abertura_boca | 0,1433 | 1,22 | entre os lábios |
| labio_ate_queixo | 0,2729 | 2,32 | lábio de baixo à ponta do queixo |
| base_nariz_ate_queixo | 0,7790 | 6,62 | terço inferior |
| altura_rosto_visivel | 1,8299 | 15,56 | alto da testa medida ao queixo |
| abertura_olho (dir / esq) | 0,1217 / 0,1206 | 1,03 / 1,03 | pálpebra a pálpebra |
| sobrancelha_ate_olho (dir / esq) | 0,2537 / 0,2441 | 2,16 / 2,08 | pico da sobrancelha à pálpebra |
| inclinacao_sobrancelhas | 3,0° | | da ponta de dentro ao pico |

**Assimetria natural** (mantenha; rosto perfeitamente simétrico não é o Luan):
- olhos 0,3%;
- boca 1,1%;
- maçãs 6,5%, que é em boa parte o leve giro da cabeça na foto.

**Cores na luz da referência** (as partes iluminadas; só se comparam na sala de lookdev com a mesma luz):

| Região | Cor iluminada | Lab |
|---|---|---|
| Pele das bochechas | | 40,9 · 15,4 · 22,6 |
| Pele do rosto | #9D6C4C | 50,2 · 16 · 26 |
| Cabelo | #866747 | 45,9 · 8 · 23 |
| Sobrancelhas | #371E10 | 14,1 · 11 · 14 |
| Íris | #342010 a #3C2715 | 14 a 18 · 7 a 8 · 14 a 16 |
| Lábios | #6E3B28 | 31 · 21 · 21 |
| Camiseta (farda) | #978167 | 55,3 · 4 · 17 |

Orelha, perfil e nuca não aparecem nos 478 pontos. Confira por sobreposição (seção 6).

## 4. Fator 1: corpos padrão proporcionais

Os números estão em `Scripts/corpos_padrao.json`, e as ferramentas leem o mesmo arquivo:
- `medir_corpo.py` mede a malha;
- `medir_esqueleto.py` mede os ossos dentro da Unreal.

Eles são o ponto de partida anatômico:
- segmentos pelas proporções clássicas de Drillis e Contini;
- magreza do garoto pela curva de crescimento da OMS;
- adultos perto da média do Norte do Brasil.

O autor pode mudar qualquer número.

| Medida | Garoto 13–14 | Mulher | Homem | Onde se mede |
|---|---|---|---|---|
| Altura | 158 cm | 160 cm | 170 cm | em pé, descalço |
| Peso (IMC) | 40 kg (16) | 50 kg (19,5) | 58 kg (20,1) | referência de magreza |
| Altura em cabeças | 7,1 | 7,4 | 7,4 | altura ÷ altura da cabeça |
| Cabeça (alto ao queixo) | 22,3 cm | 21,6 cm | 23 cm | malha |
| Entrepernas (do chão) | 75 cm | 74,4 cm | 79,9 cm | malha |
| Largura de ombros | 36,5 cm | 37,5 cm | 42,5 cm | malha |
| Largura do quadril | 27,5 cm | 34 cm | 32 cm | malha |
| Pescoço (volta) | 29 cm | 30 cm | 35 cm | malha |
| Peito / busto (volta) | 71 cm | 82 cm | 87 cm | malha |
| Cintura (volta) | 61 cm | 64 cm | 73 cm | malha |
| Quadril (volta) | 75 cm | 90 cm | 89 cm | malha |
| Coxa (volta) | 40 cm | 51 cm | 49 cm | malha |
| Panturrilha (volta) | 28 cm | 32 cm | 34 cm | malha |
| Braço (volta) | 20 cm | 24 cm | 26,5 cm | à mão |
| Punho (volta) | 14 cm | 14,5 cm | 16,5 cm | à mão |
| Ombro a ombro (ossos) | 30 cm | 30,4 cm | 34,9 cm | esqueleto |
| Quadril a quadril (ossos) | 15 cm | 17,6 cm | 17 cm | esqueleto |
| Braço (ombro ao cotovelo) | 29,4 cm | 29,8 cm | 31,6 cm | esqueleto |
| Antebraço (cotovelo ao punho) | 23,1 cm | 23,4 cm | 24,8 cm | esqueleto |
| Mão (punho à ponta do dedo) | 17,1 cm | 17,3 cm | 18,4 cm | à mão |
| Coxa (quadril ao joelho) | 38,7 cm | 39,2 cm | 41,7 cm | esqueleto |
| Perna (joelho ao tornozelo) | 38,9 cm | 39,4 cm | 41,8 cm | esqueleto |
| Pé | 24 cm | 24,3 cm | 25,8 cm | à mão |
| Altura do ombro (osso) | 129,2 cm | 130,9 cm | 139,1 cm | esqueleto |
| Altura do quadril (osso) | 83,7 cm | 84,8 cm | 90,1 cm | esqueleto |

| Cabeça | Garoto | Mulher | Homem |
|---|---|---|---|
| Distância entre pupilas | 6 cm | 6,2 cm | 6,4 cm |
| Largura da cabeça | 14,8 cm | 14,6 cm | 15,3 cm |
| Comprimento da cabeça (frente a trás) | 18,8 cm | 18,5 cm | 19,5 cm |
| Largura do rosto nas maçãs | 12,6 cm | 13 cm | 13,8 cm |

**Tolerâncias:**
- altura, 1%;
- cabeças, ±0,2;
- entrepernas e alturas de osso, 2%;
- larguras e voltas, 4%;
- segmentos, 3%;
- simetria esquerda e direita, 1%.

Outra altura (por exemplo, o Luan adulto com 1,63 m) usa as mesmas proporções: `--altura 163`.

**Conferências rápidas de proporção:**
- a envergadura dos braços é quase igual à altura;
- o pé tem quase o comprimento do antebraço;
- a mão tem quase a altura do rosto (do queixo à linha do cabelo);
- o cotovelo fica perto da cintura, e o punho perto do entrepernas.

**O que faz o garoto parecer ter 13 a 14 anos:**
- a cabeça é maior em relação ao corpo (7,1 cabeças contra 7,4);
- os ombros ainda são estreitos;
- braços e pernas são longos e finos, e joelho e cotovelo parecem grandes;
- mãos e pés já estão quase do tamanho de adulto (o desengonçado do estirão);
- clavícula e escápulas aparecem, com pouca definição muscular;
- o pescoço é fino e a postura, levemente curvada;
- no rosto, a bochecha ainda é cheia, e nariz e mandíbula começam a crescer.

**Variantes de corpo** (sobre o magro; o garoto tem só magro e médio):

| Variante | Ombros | Pescoço | Peito | Cintura | Quadril | Coxa | Panturrilha | Braço |
|---|---|---|---|---|---|---|---|---|
| Médio | = | +4% | +6% | +12% | +6% | +8% | +5% | +8% |
| Forte | +6% | +10% | +12% | +4% | +5% | +12% | +10% | +22% |
| Acima do peso | +3% | +8% | +14% | +28% | +14% | +16% | +10% | +14% |

**Como fazer na Unreal:**
- **Base:** o MetaHuman, com o corpo paramétrico. Entre as medidas por número onde a sua versão tiver o campo; senão, ajuste até a fita métrica bater.
- **Se o paramétrico não chegar no garoto:** faça um corpo sob medida no esqueleto do MetaHuman. Ajuste a escala dos ossos pelo retarget e esculpa na topologia do corpo do MetaHuman. O rig continua o padrão; é isso que faz roupa, Motion Matching e templates funcionarem em todos.
- **Como medir:**
  1. Exporte corpo e cabeça (FBX para OBJ; o comando está no cabeçalho do `medir_corpo.py`) e rode `python Scripts/medir_corpo.py personagem.obj --padrao garoto_13_14`.
  2. Na Unreal, rode o `medir_esqueleto.py` com `NOV_CORPO`, `NOV_CABECA` e `NOV_PADRAO`.
  3. Os dois precisam dizer "DENTRO DO PADRÃO".

## 5. Fator 2: a biblioteca de templates

**Princípio:** nenhum personagem nasce do zero. Todo personagem é:
- um corpo padrão;
- a variante;
- a altura;
- um template por região;
- as misturas entre eles.

Todos os templates usam a topologia e o esqueleto do MetaHuman, então qualquer combinação funciona e a roupa veste.

**Receita de personagem.** Um Data Asset por personagem lista:
- corpo padrão, variante e altura;
- os pesos de mistura das regiões do rosto;
- cabelo, sobrancelha e pelos;
- pele, olhos e dentes;
- as camadas de roupa com os tecidos.

Mudou um template, todos os personagens que o usam mudam. Nome dos templates: `T_<Regiao>_<Nome>` (ex.: `T_Nariz_Adunco`, `T_Barriga_Pochete`).

**Pastas:**
```
/Game/Novamente/Personagens/
  Base/        Corpo_Garoto13, Corpo_Feminino, Corpo_Masculino (+ variantes)
  Templates/   Rosto/ Cabelo/ Sobrancelha/ Pelos/ Corpo/ Pele/ Olhos/ Dentes/ Maos_Pes/
  Roupa/       Camadas/ Tecidos/ Acessorios/
  Receitas/    Luan_13, ... (uma por personagem)
  Provador/    L_Provador (mapa), ROM de teste, câmeras de medição
```

**Mínimos da biblioteca:**

| Categoria | Templates (mínimo) | Como |
|---|---|---|
| Rosto: formato | oval, redondo, quadrado, alongado, triangular, coração, losango | Mistura por região no MetaHuman |
| Rosto: olhos | amendoado, redondo, caído, inclinado para cima; pálpebra com dobra, encapuzada, sem dobra | Mistura por região |
| Rosto: nariz | reto, adunco, arrebitado, base larga, fino, ponta redonda | Mistura por região |
| Rosto: boca | fina, média, cheia; arco marcado ou reto | Mistura por região |
| Rosto: queixo e mandíbula | pequeno, largo, projetado, recuado, com covinha; mandíbula estreita, média, quadrada | Mistura por região |
| Rosto: maçãs, testa, orelhas | maçã alta, baixa, plana; testa alta, baixa, inclinada; orelha colada, de abano, lóbulo solto, lóbulo preso | Mistura por região |
| Rostos de base | 8 ou mais, cobrindo a gente de Manaus: traço indígena e caboclo, negro, branco, pardo, sem caricatura | Presets do MetaHuman |
| Pele | 10 tons (claro ao retinto, subtom quente, neutro e oliva); sardas, pintas, mancha de sol, espinha de adolescente, cicatriz, olheira, barba por fazer, estria, calo, marca de chinelo no pé | Texturas e máscaras do MetaHuman |
| Olhos | castanho-escuro, castanho, avelã, mel, verde; esclera cansada | Material de olho do MetaHuman |
| Dentes | alinhados, um pouco tortos, incisivo para trás, aparelho fixo; cor natural, nunca branco puro | Malha e material de dentes |
| Cabelo | liso fino, liso grosso preto, ondulado, cacheado, crespo; cortes de Manaus 2017: disfarçado com risca de navalha, na régua, topete, platinado, máquina zero, franja curta (a do Luan), black, tranças nagô, rabo de cavalo, coque, liso de chapinha, longo ondulado ruivo | Groom em fios, cards nos LODs de longe |
| Sobrancelha | reta, arqueada, grossa, fina, falhada, com risquinho, unida | Groom |
| Pelos | buço de adolescente; barba rala, cheia, cavanhaque, por fazer; pelos de braço e perna (adultos) | Groom |
| Braços | fino, médio, forte, gordinho; veia de trabalhador; cotovelo marcado | Morph na topologia do MetaHuman |
| Pernas | fina, média, grossa; joelho para dentro ou para fora; panturrilha alta ou baixa | Morph |
| Barriga | chapada magra (costela aparece ao levantar os braços), normal, pochete, barriga de cerveja (adulto) | Morph |
| Cintura e quadril | definida, reta, larga | Morph e variantes |
| Ombros e peito | caído, reto, largo, estreito; clavícula marcada; esterno aparente; busto P, M, G | Morph |
| Costas e postura | reta, curvada de cansaço (o Luan), lordose | Morph e pose base |
| Mãos e pés | dedo longo ou curto; unha roída, suja; nó do dedo machucado (lutador); pé chato, cavo; calcanhar rachado | Morph e texturas |

Cada template de corpo é um morph de 0 a 1 com os corretivos das articulações. Conferir: a fita métrica continua dentro do padrão com o template em 0, e na variante declarada com o template em 1.

### 5.1 Roupa em camadas (sobreposição)

| Camada | Peças |
|---|---|
| 0 · Pele | o corpo |
| 1 · Íntima | cueca, calcinha, sutiã, top |
| 2 · Base | camiseta, regata, a farda, camisa de time; bermuda tactel, short, jeans, legging |
| 3 · Meio | camisa aberta, moletom |
| 4 · Fora | jaqueta, capa de chuva |
| 5 · Acessórios | boné, corrente, relógio, mochila, cinto |
| Pés | meia, chinelo de dedo, tênis |

- **Modelagem:** cada camada é feita no Marvelous Designer por cima da anterior, simulada em sequência, para cada corpo padrão e variante. Quando a sua versão tiver o ajuste automático de roupa ao corpo do MetaHuman, use.
- **Folga entre camadas** (espessura mais folga):

  | Peça | Folga |
  |---|---|
  | Malha | 1 a 2 mm |
  | Camisa | 2 a 3 mm |
  | Moletom | 4 a 6 mm |
  | Jaqueta | 6 a 10 mm |

- **Nada atravessa:**
  - o corpo escondido por baixo da roupa é mascarado por peça;
  - a roupa de dentro vai por pele com mapa de ruga;
  - só a de fora é simulada com Chaos Cloth.
- **Camisa por dentro e por fora** são duas variantes da mesma peça.
- **Teste:** no `L_Provador`, uma animação de teste de movimento:
  - levantar os braços, agachar, girar o tronco;
  - chute alto, guarda, soco;
  - sentar, correr.

  Zero atravessamento em todos os quadros, nos três corpos e nas variantes.

### 5.2 Tecidos

Shading model Cloth, com fuzz. Três níveis de detalhe:
- dobra grande da simulação;
- ruga do mapa;
- trama em escala real, num normal de detalhe repetido.

Parâmetros de desgaste (bolinha, costura desbotada, gola lasseada, amarelado de suor na gola e na axila, barro, rasgo), de suor e de molhado. Na chuva de Manaus, o tecido molhado escurece de 20% a 40%, perde de 0,2 a 0,3 de rugosidade e gruda no corpo.

| Tecido | Onde | Trama (escala real) | Rugosidade | Cor |
|---|---|---|---|---|
| Malha de algodão | camiseta, a farda | laçadas de ~1 mm (8 a 10 por cm), bloco de 2 × 2 cm | 0,8 a 0,95 | branco gasto 200 a 225 sRGB, nunca 255 |
| Ribana 1×1 | gola canelada, punho | cordões de 1,5 a 2 mm | 0,8 a 0,9 | listras tiradas da referência |
| Jeans (sarja 3×1) | calça, bermuda | diagonal de 2 a 3 mm | 0,75 a 0,9 | índigo desbotando em costura, joelho, bolso |
| Tactel | bermuda de praia | liso, brilho leve | 0,45 a 0,6 | cores fortes desbotadas |
| Poliéster de camisa de time | camisa 10 | malha furadinha de 0,5 a 1 mm | 0,4 a 0,55 | estampa sublimada |
| Moletom | blusa de frio | liso por fora, felpa por dentro | 0,9 a 1 | |
| Lycra, suplex | legging, bermuda de luta | liso esticado, brilho | 0,35 a 0,5 | |
| Atadura de algodão | mão enfaixada | trama aberta de ~1 mm | 0,9 a 1 | branco sujo, manchas |
| Couro sintético | jaqueta, cinto | poro e rachadura | 0,35 a 0,6 | |
| Lona e borracha | tênis, chinelo | trama de lona; borracha lisa | 0,6 a 0,8 | |

## 6. Fator 3: o rosto do Luan, 100% pelas medidas

1. **Fichas.** Use as três fichas da referência (close, frente, três quartos) em `Referencias/`. São do autor e estão seladas.
2. **Câmeras.**
   - As câmeras `Rev_05_Rosto_Close`, `_Frente`, `_34` e `_Perfil` repetem a lente, a distância e a altura de cada referência.
   - A distância focal sai do FaceBuilder, que a estima ao encaixar a malha na foto.
   - O `medidas_rosto.py` reprova se o ângulo da cabeça não bate.
3. **Ponto de partida por medida.**
   - Fotografe cada rosto de base da biblioteca na câmera do close e rode `medidas_rosto.py --comparar` contra a ficha.
   - Ordene pelo erro médio de identidade e comece da mistura por região dos três melhores.
4. **Cabeça com a identidade.**
   - Opção A: FaceBuilder a partir das quatro vistas.
   - Opção B: escultura sobre a cabeça do MetaHuman, com as quatro vistas como pranchas na mesma lente.
   - Sobreponha cada vista a 50% de transparência. O contorno do perfil, da nuca e das orelhas fica a no máximo 2 pixels numa imagem de 1024.
5. **Mesh to MetaHuman.** Depois da conversão, meça de novo. Nada que a conversão mudou fica sem correção.
6. **Corrigir pela tabela.**
   - Rode `medidas_rosto.py --comparar Referencias/ficha_luan_close.json --shot <foto>` e corrija a pior medida de identidade primeiro, uma região por vez.
   - Anote o número antes e depois.
   - Nunca "corrija" mexendo na câmera.
7. **A expressão.** Coloque no rig facial a expressão da referência (boca entreaberta com abertura de 0,14 unidade, sobrancelha levantada, olhar) e rode com `--com-expressao`. Tudo dentro de 6%.
8. **As cores.** Na sala de lookdev que recria a luz do render, rode com `--com-cor`:
   - pele das bochechas até Delta E 5;
   - cabelo, sobrancelha, íris, lábio e camiseta até Delta E 6.
9. **As três vistas.** Close, frente e três quartos passam, cada uma contra a própria ficha. Perfil, costas e orelhas passam pela sobreposição do passo 4.
10. **Juiz e autor.**
    - Com os números passando, o revisor-visual julga (`/revisao-aaa`).
    - Depois, o autor vê as cinco comparações lado a lado.
    - O rosto só vira "o Luan" com o sim do autor.

**Metas:**
- cada medida de identidade até 3%;
- média até 2%;
- ângulos até 2°;
- expressão até 6%;
- cores até Delta E 5 e 6.

## 7. Portões

| Portão | Entrega | Prova |
|---|---|---|
| C1 · Corpo do garoto | O corpo do Luan aos 13–14 anos | `medir_corpo.py` e `medir_esqueleto.py` DENTRO DO PADRÃO; giro de 360° no provador com a roupa de medição; parecer aprovado |
| C2 · Rosto do Luan | A seção 6 inteira | As três fichas passando com identidade, expressão e cor; sobreposição de perfil e orelhas; parecer aprovado; sim do autor |
| C3 · Corpos adultos | Mulher e homem, com as variantes | As duas ferramentas DENTRO DO PADRÃO em cada corpo e variante |
| C4 · Biblioteca | Os mínimos da seção 5, roupa em camadas e tecidos | Teste de montagem: 6 personagens sorteados das receitas, todos dentro das medidas, sem atravessamento no teste de movimento, parecer aprovado |

Registre cada rodada em `Docs/REVISOES.md`, com as tabelas das ferramentas.

## 8. Regras

- Só os três fatores.
- Nunca diga "pronto" sem as tabelas das ferramentas dizendo PASSOU ou DENTRO DO PADRÃO, e sem o parecer.
- Não mexa em referência, ficha, `corpos_padrao.json` nem tolerância sem o autor. Proponha a mudança com o motivo.
- Template antes de sob medida. Tudo na topologia e no esqueleto do MetaHuman.
- **Personagem menor de idade:**
  - o garoto é sempre revisado vestido, no mínimo com regata e bermuda de medição;
  - nada de nudez nem pose que não seja de medição ou de jogo;
  - a medida do corpo é tirada da malha, por número.
- **Adultos:** revisados com roupa neutra justa (regata e bermuda de malha cinza).
- Nada oriental. Nada de Mixamo.
- **Diga cedo o que precisa de gente ou licença:**
  - escultor ou FaceBuilder para o rosto exato;
  - Marvelous Designer para a roupa;
  - fotos de gente de Manaus para os rostos de base (com autorização).

## 9. Sua primeira resposta

1. **As ferramentas funcionando.** Mostre:
   - as três fichas da referência (`medidas_rosto.py`);
   - a fita métrica do corpo atual do Luan (`medir_corpo.py`);
   - o esqueleto dele (`medir_esqueleto.py`), com o que está fora do padrão.
2. **O plano na ordem C1, C2, C3, C4.** Diga o que você faz e o que o autor fornece (licenças, escultor, fotos).
3. **A lista de downloads e licenças.**
4. **Decisões para o autor:**
   - a altura do Luan aos 13–14 anos (o padrão é 1,58 m; o canon adulto é 1,63 m);
   - a cor da íris, que segue a referência (avelã) salvo decisão contrária.

Depois execute o C1 e o C2 até as tabelas passarem e o parecer aprovar, ou até um "PENDENTE:" honesto.
