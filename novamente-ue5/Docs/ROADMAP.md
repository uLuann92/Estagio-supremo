# Roadmap do vertical slice: Luta no Largo

Meta: uma luta de três rounds no Largo de São Sebastião que aguente comparação lado a lado com um jogo de estúdio grande, rodando a 60 quadros por segundo numa placa de vídeo intermediária.

Escala honesta: Ghost of Tsushima foi feito por uma equipe de mais de cem pessoas durante cerca de seis anos. Um slice (uma arena, dois personagens principais, um sistema de luta) nesse nível visual é possível com equipe pequena, MetaHuman, bibliotecas do Fab e captura de movimento terceirizada. Um jogo inteiro nesse nível não é possível só com IA e uma pessoa.

## Portões de revisão

Cada portão só fecha com a prova. A prova vem das fotos de `Scripts/capture_review.py` (sempre os mesmos ângulos) comparadas com as referências e com a rodada anterior, registrada em `Docs/REVISOES.md`.

| Portão | O que precisa estar pronto | Prova | Quem faz |
|---|---|---|---|
| **R0 · Compila** | Plugin compila sem erro e sem aviso novo. Play abre a abertura, a câmera desce, a luta roda com cápsulas, o HUD mostra barras, relógio e legendas. O save grava e lê os hematomas. | Log de compilação limpo; `luta_00` a `luta_11`; log do Play sem erro. | Claude no PC |
| **R1 · Parece Manaus** | Blockout substituído por arte: fachada rosa com frisos brancos, cúpula de azulejos verde, amarelo e azul, pedra portuguesa em ondas pretas e brancas, Igreja de São Sebastião, monumento em bronze, mangueiras, postes coloniais, prédios em volta. | `editor_04`, `editor_05`, `editor_06` ao lado de fotos reais do Largo. Nenhum elemento japonês. | Artista de cenário (ou kits do Fab) + Claude nos materiais e na montagem |
| **R2 · Luz e clima** | Noite de chuva: luz de sódio laranja nos postes, refletores frios no octógono, neblina volumétrica segurando a luz, chão molhado com reflexo, relâmpago, vento nas árvores, respingos, vapor saindo dos corpos. | `editor_01`, `editor_04`, `editor_06`; histograma sem preto esmagado nem branco estourado. | Artista de luz + Claude (Niagara, materiais, pós) |
| **R3 · Rostos** | Luan e Igor em MetaHuman parecendo com a capa e o render: poros, suor, olhos úmidos, cabelo em fios (groom), rugas de cansaço. | `editor_02`, `editor_03` lado a lado com a capa v1 a v3 e o render 3D. Aprovação do autor. | Artista de personagem (Mesh to MetaHuman) + autor aprova |
| **R4 · Corpo e roupa** | Proporções de lutador real, bandagens, luvas de MMA, bermudas; camisa-pijama que vira farda. Tecido com simulação. Hematomas envelhecendo nos três rounds e voltando na revanche. | Fotos do rosto nos rounds 1, 2 e 3 e na revanche. | Artista de personagem + Claude (material de ferimentos) |
| **R5 · Animação** | Locomoção com Motion Matching sem pé deslizando; golpes de mocap com Motion Warping (a mão chega no rosto, não atravessa); reações por zona com física parcial; queda em ragdoll e levantar animado; respiração e tremor. | Vídeo de 60 s gravado no Play + `luta_*`. Nenhum golpe atravessando. | Estúdio de mocap (1 a 3 diárias) + animador + Claude (AnimBP, montagens) |
| **R6 · Luta** | Peso do impacto (hit-stop, câmera, som), IA do Igor diferente a cada round, Visão do Caos justa, ground and pound, decisão e nocaute. No mundo aberto: briga de rua contra 3 a 5, com travamento de alvo, troca no analógico e a câmera enquadrando o grupo; no máximo dois batem ao mesmo tempo. Teste com 5 pessoas: entendem os controles em 2 minutos, lutas duram 2 a 4 minutos. | Planilha dos testes + vídeo da arena e de uma briga em grupo no Mutirão. | Designer de combate (pode ser o autor) + Claude |
| **R7 · Sombra e Leis** | Pós-processamento da Sombra na cor certa, garras, olhos no céu, 2ª Lei antes dela, som abafado da 1ª Lei, Realidade 2, falas com a voz certa. Trilha e desenho de som. | Vídeo de uma luta inteira com a Sombra ativada. Aprovação do autor. | Sound designer + dublagem + Claude (sistemas e pós) |
| **R8 · Desempenho e acabamento** | 60 qps a 1440p com TSR numa RTX 3070 (ou equivalente de console), sem travadas de shader (cache de PSO), carregamento abaixo de 15 s, interface final, menu, legendas, acessibilidade (remapear controles, tamanho da legenda, reduzir tremor). | `desempenho.png` + trace do Unreal Insights de uma luta inteira. | Claude + programador de desempenho |

## Orçamento de desempenho (60 qps = 16,6 ms por quadro)

GPU, 1440p com TSR (resolução interna perto de 1080p):

| Parte | ms |
|---|---|
| Nanite e passe base | 2,5 |
| Lumen (iluminação global e reflexos) | 4,0 |
| Sombras virtuais | 2,0 |
| Dois MetaHumans com cabelo em fios | 2,5 |
| Chuva, respingos, vapor, neblina volumétrica | 1,5 |
| Pós (TSR, profundidade de campo, bloom, M_PP_Novamente) | 2,0 |
| Interface | 0,3 |
| Folga | 1,8 |

CPU (thread do jogo): animação dos dois lutadores com Motion Matching 1,5 ms; público (Mass) 2,0 ms; lógica da luta menos de 0,3 ms.

Regras: medir com Unreal Insights antes de mexer; cache de PSO ligado (o setup liga) e uma passada completa pelo jogo antes de gerar o pacote; LOD de MetaHuman por distância; público com animação por vértice (Vertex Animation) ou Mass, nunca 200 Skeletal Meshes cheios.

## Ferramentas e linguagens

- **C++**: combate, IA, câmera, regras, save (este plugin). Onde o desempenho e a precisão importam.
- **Blueprint**: montagem dos personagens, AnimBP, ajustes de designer, eventos de cena.
- **Python (editor)**: montar cenário, criar materiais, fotos de revisão, automação de revisão.
- **HLSL**: nós Custom do pós-processamento, ferimentos, olhos da Sombra.
- **Engine**: Lumen, Nanite, Sombras Virtuais, TSR, MetaHuman (Creator, Mesh to MetaHuman, Animator), Motion Matching (Game Animation Sample), Motion Warping, Control Rig, Physical Animation, Chaos Cloth, Niagara, PCG para espalhar detalhes, World Partition, MetaSounds, CommonUI, Unreal Insights.
- **Fora da engine**: Blender ou Maya, ZBrush, Substance 3D Painter e Designer, Houdini (chuva e água, opcional), RealityScan (fotogrametria do Largo), captura de movimento (Move.ai, Rokoko, Xsens ou estúdio), iPhone ou câmera para MetaHuman Animator.

## Equipe mínima realista para o slice

| Papel | Dedicação |
|---|---|
| Autor: direção criativa, canon, aprovação | contínua |
| Claude no PC: código, shaders, scripts, revisões, montagem | contínua |
| Artista de personagem (MetaHuman, groom, roupa) | 3 a 4 meses |
| Artista de cenário e luz (Largo, teatro, chuva) | 3 a 4 meses |
| Animador de combate + diárias de mocap | 2 a 3 meses + 1 a 3 diárias |
| Sound designer + trilha | 1 a 2 meses |
| Dublagem (Luan, Igor, Emma, Felipe, Mateus, Sombra) | 1 a 2 semanas |
| Testadores | 2 rodadas de 5 pessoas |

Prazo: 6 a 9 meses com essa equipe em paralelo. Sozinho com o Claude e bibliotecas prontas, o slice chega perto em 12 a 18 meses, com rosto e animação abaixo do nível de estúdio.

## Fases

1. **Agora a 1 mês**: R0 e R1 em blockout. Referências fotográficas do Largo (fotos e escaneamento com RealityScan, se possível).
2. **1 a 4 meses**: R2, R3, R4 em paralelo. Decisões do autor sobre rosto e roupa.
3. **3 a 7 meses**: R5 e R6. Mocap no meio desta fase.
4. **6 a 9 meses**: R7 e R8. Vídeo do slice para mostrar a publicadoras, editais (Ancine, Spcine, leis de incentivo) e financiamento coletivo.
