# Arsenal AAA: ferramentas para fazer um jogo AAA

212 ferramentas, recursos, plugins e pontos essenciais em 23 categorias. Pensado para a Unreal Engine 5, que é o motor do NOVAMENTE.

Como ler:

- **Prioridade:**
  - Essencial: sem isso não sai AAA, ou é o padrão da indústria para a função.
  - Recomendado: acelera muito.
  - Opcional: alternativa ou caso específico.
- **Custo:**
  - Grátis;
  - Vem na Unreal;
  - Grátis limitado: versão grátis, teste ou grátis até certo faturamento;
  - Pago;
  - Sob aprovação.
- **NOVAMENTE:** "sim" quando a ferramenta já está no plano do jogo (prompts, roadmap, kit).
- Preços, licenças e o estado de recursos experimentais mudam. Confira no site antes de comprar ou depender.
- Para mandar esta lista a outra IA, use junto o `Docs/PROMPT_ARSENAL.md`.

Resumo:

- 212 itens;
- 69 essenciais;
- 124 grátis ou já na Unreal;
- 77 no plano do NOVAMENTE.

## Motor e código (14)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Unreal Engine 5](https://www.unrealengine.com) | O motor: render, física, animação, áudio e editor. Grátis até US$ 1 milhão de receita bruta por jogo; acima disso, royalty (confira os termos atuais). | Essencial | Grátis | Programa | sim |
| [Visual Studio 2022 Community](https://visualstudio.microsoft.com) | Compilar e depurar o C++ da Unreal no Windows (carga de trabalho de jogos em C++). | Essencial | Grátis | Programa | sim |
| [JetBrains Rider](https://www.jetbrains.com/rider/) | IDE que entende a Unreal: Blueprints, reflexão, testes. Alternativa ao Visual Studio. | Recomendado | Grátis limitado | Programa |  |
| [Visual Assist](https://www.wholetomato.com) | Plugin do Visual Studio que entende o C++ da Unreal (navegação e refatoração). | Opcional | Pago | Plugin |  |
| Unreal Python (Editor Scripting) | Automatizar o editor: montar cenas, criar materiais, importar em lote, fotografar revisões. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Editor Utility Widgets | Ferramentas internas com interface dentro do editor, feitas pela própria equipe. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Live Coding | Recompila o C++ com o editor aberto. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| [Código-fonte da Unreal](https://www.unrealengine.com/en-US/ue-on-github) | Compilar a engine para corrigir bugs e usar Horde, UnrealGameSync e servidor dedicado. | Recomendado | Grátis | Programa |  |
| Enhanced Input | Controles por contexto (andar, lutar, menu), remapeáveis, teclado e controle. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Gameplay Ability System (GAS) | Habilidades, atributos e efeitos (fôlego, bônus, ferimentos). No NOVAMENTE, só por ADR. | Recomendado | Vem na Unreal | Recurso da Unreal | sim |
| Gameplay Tags | Etiquetas hierárquicas para estados e regras (Estado.Caido, Golpe.Chute). | Essencial | Vem na Unreal | Recurso da Unreal |  |
| Game Features | Conteúdo em plugins que ligam e desligam: capítulos, modos, DLC. | Opcional | Vem na Unreal | Recurso da Unreal |  |
| Lyra Starter Game | Projeto de referência de arquitetura da Epic. Para estudar; não serve de base para jogo de luta single player. | Opcional | Grátis | Biblioteca ou projeto |  |
| [Unity 6 / Godot 4](https://godotengine.org) | Alternativas de motor. Unity em C#, forte em mobile; Godot aberto e leve. Nenhum chega ao pacote AAA da Unreal pronto. | Opcional | Grátis limitado | Programa |  |

## Mundo e cenário (21)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| World Partition | Mundo aberto em células que carregam por distância, sem tela de carregamento. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Data Layers | Camadas do mundo que ligam e desligam: dia, noite, chuva, missão. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Level Instances | Blocos reutilizáveis (uma casa, um quarteirão) montados uma vez e repetidos. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| HLOD | Versões simplificadas do longe, geradas automaticamente. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| PCG (Procedural Content Generation) | Espalhar e montar por regras: mato, lixo, postes, fios, casas. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Nanite | Geometria com milhões de polígonos sem LOD manual. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Landscape e Water | Terreno esculpido e pintado; rios, lagos e mar com o plugin Water. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Foliage, Mesh Paint e Decals | Pintar vegetação, sujeira por vértice e decalques (pichação, mancha, rachadura). | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Modeling Mode e Geometry Script | Modelar e gerar malhas dentro do editor, à mão ou por script. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| [Houdini + Houdini Engine](https://www.sidefx.com) | Geração procedural pesada (cidades, ruas, erosão) com ferramentas que rodam dentro da Unreal. | Recomendado | Grátis limitado | Programa | sim |
| [Gaea](https://quadspinner.com) | Terreno com erosão realista e mapas prontos para o Landscape. | Recomendado | Grátis limitado | Programa |  |
| [World Machine](https://www.world-machine.com) | Terreno procedural por nós, veterano da indústria. | Opcional | Grátis limitado | Programa |  |
| [World Creator](https://www.world-creator.com) | Terreno e biomas em tempo real na GPU. | Opcional | Pago | Programa |  |
| [SpeedTree](https://www.speedtree.com) | Árvores e plantas com vento, LOD e variações. | Recomendado | Pago | Programa |  |
| [Quixel Megascans](https://www.fab.com) | Escaneamentos calibrados de chão, pedra, reboco e plantas, no Fab (confira a licença). | Essencial | Grátis limitado | Biblioteca ou projeto | sim |
| [Fab](https://www.fab.com) | Loja da Epic de assets, plugins e Megascans. | Essencial | Grátis limitado | Biblioteca ou projeto | sim |
| City Sample | Cidade gerada da Epic com tráfego e multidão em Mass. Referência para bairro inteiro. | Recomendado | Grátis | Biblioteca ou projeto | sim |
| [Cesium for Unreal](https://cesium.com/platform/cesium-for-unreal/) | Terreno e cidades reais do planeta (inclusive blocos 3D fotorrealistas) como base de layout. | Opcional | Grátis limitado | Plugin |  |
| Blosm (Blender) | Importa ruas e prédios do OpenStreetMap para o Blender. | Opcional | Grátis limitado | Plugin |  |
| [Voxel Plugin](https://voxelplugin.com) | Terreno em voxel com cavernas e escavação. | Opcional | Grátis limitado | Plugin |  |
| Dash (Polygonflow) | Espalha, mistura e organiza assets de cenário dentro da Unreal. | Opcional | Pago | Plugin |  |

## Escaneamento e referência do real (5)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [RealityScan (antigo RealityCapture)](https://www.realityscan.com) | Fotogrametria: fotos viram malha e textura (paredes, chão, objetos, pessoas). | Recomendado | Grátis limitado | Programa | sim |
| [Polycam](https://poly.cam) | Escanear com o celular (LiDAR ou fotos) para referência rápida. | Opcional | Grátis limitado | Programa |  |
| [Google Earth e Street View](https://earth.google.com) | Referência de ruas, alturas, fachadas e fios do lugar real. | Essencial | Grátis | Serviço | sim |
| Kit de fotogrametria | Câmera, cartela de cor (ColorChecker), filtro polarizador e tripé para escanear com a cor certa. | Recomendado | Pago | Equipamento | sim |
| Fotos de referência próprias | Ir ao lugar e fotografar texturas, luz por hora, gente (com autorização) e detalhes. | Essencial | Grátis | Prática | sim |

## Modelagem e escultura (7)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Blender](https://www.blender.org) | Modelagem, UV, rig, bake e animação. Faz quase tudo. | Essencial | Grátis | Programa | sim |
| [Autodesk Maya](https://www.autodesk.com/products/maya) | Padrão de estúdio para rig e animação; também modela. | Recomendado | Pago | Programa |  |
| Autodesk 3ds Max | Modelagem de cenário e props, forte em arquitetura. | Opcional | Pago | Programa |  |
| [ZBrush](https://www.maxon.net/en/zbrush) | Escultura em alta resolução: rosto, corpo, rugas, desgaste. | Essencial | Pago | Programa | sim |
| [Plasticity](https://www.plasticity.xyz) | Superfície dura (carros, objetos, armas) com precisão de CAD. | Opcional | Pago | Programa |  |
| [Marmoset Toolbag](https://marmoset.co) | Bake de mapas e lookdev rápido fora da engine. | Recomendado | Pago | Programa |  |
| [RizomUV](https://www.rizom-lab.com) | UV rápido e com pouca distorção. | Opcional | Pago | Programa |  |

## Materiais e texturas (15)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Substance 3D Painter](https://www.adobe.com/products/substance3d.html) | Pintar texturas em camadas com desgaste inteligente. | Essencial | Pago | Programa | sim |
| Substance 3D Designer | Materiais procedurais repetíveis: reboco, asfalto, tijolo, barro. | Recomendado | Pago | Programa | sim |
| Substance 3D Sampler | Material a partir de foto. | Opcional | Pago | Programa |  |
| Plugin Substance para Unreal | Usa materiais .sbsar ajustáveis dentro da engine. | Opcional | Grátis | Plugin |  |
| InstaMAT | Texturização e materiais procedurais, alternativa ao Substance. | Opcional | Grátis limitado | Programa |  |
| [ArmorPaint](https://armorpaint.org) | Pintura de texturas de código aberto. | Opcional | Grátis limitado | Programa |  |
| Photoshop | Edição de textura, máscaras e concept. | Recomendado | Pago | Programa |  |
| [Krita](https://krita.org) | Pintura digital e textura, grátis. | Recomendado | Grátis | Programa |  |
| [Poly Haven](https://polyhaven.com) | HDRIs, texturas e modelos livres (CC0). | Recomendado | Grátis | Biblioteca ou projeto |  |
| [ambientCG](https://ambientcg.com) | Materiais PBR livres (CC0). | Opcional | Grátis | Biblioteca ou projeto |  |
| [Texturing.XYZ](https://texturing.xyz) | Microdetalhe de pele escaneado (poros, rugas) para rosto de alto nível. | Recomendado | Pago | Biblioteca ou projeto | sim |
| Material Layers e Functions | Material mestre em camadas (base, tinta, sujeira, limo) reaproveitado em tudo. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Substrate | Materiais da Unreal em camadas físicas (verniz, tecido, pele). Confira o estado na sua versão. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Runtime Virtual Texturing | Mistura objeto com terreno (pedra afundando no barro) e acelera o chão. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Virtual Textures | Texturas enormes sem estourar a memória de vídeo. | Recomendado | Vem na Unreal | Recurso da Unreal |  |

## Personagens (12)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [MetaHuman Creator e Mesh to MetaHuman](https://www.unrealengine.com/en-US/metahuman) | Humanos com rig facial e corporal prontos, dentro da Unreal; converte escultura ou escaneamento em MetaHuman. | Essencial | Grátis | Recurso da Unreal | sim |
| MetaHuman Animator | Captura de rosto de estúdio com iPhone, câmera estéreo ou vídeo; nas versões recentes, também a partir de áudio. | Essencial | Grátis | Recurso da Unreal | sim |
| Live Link Face | App de iPhone para rosto ao vivo e captura para o MetaHuman Animator. | Recomendado | Grátis | Programa | sim |
| Groom (cabelo em fios) | Cabelo e pelos em fios com física; cards para o longe. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| [KeenTools FaceBuilder](https://keentools.io) | Cabeça 3D a partir de fotos de vários ângulos, no Blender. | Recomendado | Grátis limitado | Plugin | sim |
| [R3DS Wrap](https://www.russian3dscanner.com) | Transfere a topologia padrão para um escaneamento ou escultura. | Recomendado | Pago | Programa | sim |
| [Marvelous Designer](https://www.marvelousdesigner.com) | Roupa com molde real e simulação de tecido. | Essencial | Pago | Programa | sim |
| [Character Creator 4 + Headshot](https://www.reallusion.com) | Personagem completo com roupa e morphs; foto vira cabeça. Alternativa ao MetaHuman. | Opcional | Pago | Programa |  |
| AccuRIG | Rig automático gratuito da Reallusion. | Opcional | Grátis | Programa |  |
| [Ornatrix](https://ephere.com) | Cabelo e pelos em fios no Maya e no Max, exportados como groom. | Opcional | Pago | Plugin |  |
| Auto-Rig Pro | Rig no Blender compatível com o esqueleto da Unreal, com retarget. | Opcional | Pago | Plugin |  |
| Estúdio de escaneamento | Escanear ator (rosto e corpo) para personagem fiel. | Opcional | Pago | Serviço |  |

## Animação e movimentação (19)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Game Animation Sample | Locomoção de estúdio pronta: Motion Matching, Pose Search, Chooser e centenas de animações. | Essencial | Grátis | Biblioteca ou projeto | sim |
| Motion Warping | Ajusta a animação para o golpe ou o salto chegar no ponto certo. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Control Rig, IK Rig e IK Retargeter | Rig dentro da engine, IK de pé e mão, e animação passada entre esqueletos. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Stride e Orientation Warping | Ajusta passada e direção sem o pé deslizar. | Recomendado | Vem na Unreal | Recurso da Unreal | sim |
| Sequencer e Take Recorder | Editar e gravar animação e cenas. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Rewind Debugger | Volta no tempo e mostra por que a animação escolheu cada pose. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Mover | Sistema novo de movimento do personagem, mais flexível (experimental). | Opcional | Vem na Unreal | Recurso da Unreal |  |
| ML Deformer | Deformação de músculo e pele aprendida por máquina, em tempo real. | Opcional | Vem na Unreal | Recurso da Unreal | sim |
| [Cascadeur](https://cascadeur.com) | Quadro-chave com física assistida (peso e equilíbrio corretos). | Recomendado | Grátis limitado | Programa |  |
| Autodesk MotionBuilder | Limpeza e edição de captura de movimento, padrão de estúdio. | Opcional | Pago | Programa |  |
| [Rokoko](https://www.rokoko.com) | Captura de movimento acessível: roupa com sensores, luvas e captura por vídeo. | Recomendado | Pago | Equipamento | sim |
| [Move.ai](https://www.move.ai) | Captura de movimento sem roupa, só com câmeras ou celulares. | Recomendado | Grátis limitado | Serviço | sim |
| [Xsens (Movella)](https://www.movella.com) | Captura inercial de estúdio, muito usada em AAA. | Opcional | Pago | Equipamento | sim |
| [OptiTrack / Vicon](https://optitrack.com) | Captura óptica com marcadores, o topo de precisão (estúdios alugam a diária). | Opcional | Pago | Equipamento |  |
| Perception Neuron | Captura inercial de entrada. | Opcional | Pago | Equipamento |  |
| DeepMotion | Animação a partir de vídeo, na nuvem. | Opcional | Grátis limitado | Serviço |  |
| [Kawaii Physics](https://github.com/pafuhana1213/KawaiiPhysics) | Movimento secundário (cabelo, roupa solta, acessórios) barato e estável. | Recomendado | Grátis | Plugin | sim |
| [ALS Refactored](https://github.com/Sixze/ALS-Refactored) | Advanced Locomotion System em C++, da comunidade. Bom para estudar. | Opcional | Grátis | Plugin |  |
| [Animation Compression Library (ACL)](https://github.com/nfrechette/acl-ue4-plugin) | Compressão de animação com menos memória e qualidade alta. | Recomendado | Grátis | Plugin |  |

## IA de NPC e navegação (5)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Behavior Trees e EQS | Decisão de NPC e escolha de posição (onde cercar, onde fugir). | Essencial | Vem na Unreal | Recurso da Unreal |  |
| StateTree | Máquina de estados moderna para IA e lógica. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Smart Objects | Pontos de uso no mundo: sentar, encostar, comprar no mercadinho. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Mass e ZoneGraph | Multidão e tráfego com milhares de agentes. | Recomendado | Vem na Unreal | Recurso da Unreal | sim |
| NavMesh e Nav Links | Onde a IA pode andar, pular e subir. | Essencial | Vem na Unreal | Recurso da Unreal |  |

## Física e destruição (6)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Chaos Physics | Corpo rígido, ragdoll e colisão. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Chaos Cloth | Roupa simulada em tempo real (inclui o editor de painéis). | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Physical Animation e Physics Control | Mistura animação com física: reação a golpe, corpo cedendo. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Chaos Destruction | Quebrar objetos e estruturas de forma controlada. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Chaos Vehicles | Carro, moto e ônibus com física. | Opcional | Vem na Unreal | Recurso da Unreal |  |
| Chaos Flesh | Músculo e carne simulados (experimental). | Opcional | Vem na Unreal | Recurso da Unreal |  |

## Iluminação, céu e render (15)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Lumen | Iluminação global e reflexos em tempo real. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Virtual Shadow Maps | Sombras nítidas em mundo grande. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| MegaLights | Muitas luzes com sombra ao mesmo tempo (rua à noite, letreiros). Experimental nas versões recentes. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Sky Atmosphere, nuvens e neblina volumétrica | Céu físico, nuvens volumétricas e neblina que segura a luz. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Ultra Dynamic Sky e Weather | Céu, hora do dia e clima prontos e ajustáveis (no Fab). | Recomendado | Pago | Plugin |  |
| Ray tracing e Path Tracer | Reflexo e sombra por raio; o Path Tracer dá a imagem de referência para calibrar. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Pós-processamento, LUT e OCIO | Exposição, gradação de cor e gerenciamento de cor (OpenColorIO). | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) | Criar LUTs e gradação de cor como no cinema. | Recomendado | Grátis limitado | Programa |  |
| Perfis IES | Formato real da luz de postes e lâmpadas. | Recomendado | Grátis | Biblioteca ou projeto |  |
| Calibração (ColorChecker e visualizações) | Conferir exposição e albedo com cartela e os modos Lighting Only, Base Color e HDR. | Essencial | Grátis limitado | Prática | sim |
| TSR (Temporal Super Resolution) | Resolução alta com custo baixo, da própria Unreal. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| NVIDIA DLSS | Reconstrução de imagem e geração de quadros em placas RTX. | Recomendado | Grátis | Plugin |  |
| AMD FSR | Reconstrução de imagem para qualquer placa. | Recomendado | Grátis | Plugin |  |
| Intel XeSS | Reconstrução de imagem para Intel Arc e outras. | Opcional | Grátis | Plugin |  |
| Movie Render Queue | Trailer e imagens de referência na qualidade máxima. | Essencial | Vem na Unreal | Recurso da Unreal | sim |

## Efeitos visuais (6)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Niagara | Partículas e efeitos: chuva, poeira, faíscas, sangue, vapor. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Niagara Fluids | Fumaça, fogo e líquido simulados em tempo real. | Opcional | Vem na Unreal | Recurso da Unreal |  |
| [EmberGen](https://jangafx.com) | Fumaça, fogo e explosão em tempo real para flipbook e VDB. | Recomendado | Pago | Programa |  |
| [Houdini (Pyro, FLIP, VDB)](https://www.sidefx.com) | Simulação pesada para flipbook, textura de animação e malha. | Opcional | Grátis limitado | Programa |  |
| Heterogeneous Volumes | Renderiza volumes VDB dentro da Unreal. | Opcional | Vem na Unreal | Recurso da Unreal |  |
| Houdini-Niagara | Leva dados de simulação do Houdini para o Niagara. | Opcional | Grátis | Plugin |  |

## Câmera e cinemática (3)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Cine Camera Actor | Câmera com lente, abertura e sensor de verdade. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Gameplay Cameras | Sistema novo de câmeras de jogo por regras (experimental). | Opcional | Vem na Unreal | Recurso da Unreal |  |
| Live Link VCam | iPad ou iPhone como câmera virtual na mão. | Opcional | Grátis | Programa |  |

## Áudio (8)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| MetaSounds | Som procedural e interativo dentro da Unreal. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| [Wwise](https://www.audiokinetic.com) | Middleware de áudio padrão AAA: mistura, estados, espacialização. | Recomendado | Grátis limitado | Plugin |  |
| [FMOD Studio](https://www.fmod.com) | Middleware de áudio, alternativa ao Wwise. | Recomendado | Grátis limitado | Plugin |  |
| [REAPER](https://www.reaper.fm) | Programa de áudio para edição, design de som e trilha. | Recomendado | Pago | Programa |  |
| iZotope RX | Limpeza de gravação (ruído, clique, eco) para falas. | Recomendado | Pago | Programa |  |
| [Sonniss GDC Game Audio Bundle](https://sonniss.com/gameaudiogdc) | Pacote anual gratuito de efeitos sonoros profissionais. | Recomendado | Grátis | Biblioteca ou projeto |  |
| Steam Audio | Áudio espacial com oclusão e reverberação física. | Opcional | Grátis | Plugin |  |
| Gravador de campo | Gravador portátil (Zoom, Tascam) para o som real do lugar: rua, chuva, bicho. | Recomendado | Pago | Equipamento | sim |

## Interface e localização (6)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| UMG e Common UI | Interface que funciona com mouse e controle, com pilha de telas. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| UMG Viewmodel (MVVM) | Separa dados e tela; interface mais fácil de manter. | Opcional | Vem na Unreal | Recurso da Unreal |  |
| [Figma](https://www.figma.com) | Projetar telas e fluxos antes de montar. | Recomendado | Grátis limitado | Programa |  |
| Localization Dashboard | Tradução de textos e legendas dentro da Unreal. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Crowdin / Lokalise | Plataforma de tradução com tradutores de fora. | Opcional | Grátis limitado | Serviço |  |
| NoesisGUI | Interface em XAML com animação vetorial. | Opcional | Grátis limitado | Plugin |  |

## Otimização e diagnóstico (17)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Unreal Insights | Linha do tempo de CPU, GPU, memória e carregamento. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Comandos stat e ProfileGPU | stat unit, stat gpu e stat scenerendering para medir na hora. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Memory Insights e LLM | Quem está gastando memória. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Size Map e Reference Viewer | Tamanho e dependências de cada asset. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Cache de PSO e precaching | Evita travadas de compilação de shader durante o jogo. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Scalability e Device Profiles | Qualidades por máquina, da baixa à cinematográfica. | Essencial | Vem na Unreal | Recurso da Unreal | sim |
| Significance Manager e Animation Budget Allocator | Gasta mais com o que está perto e na tela. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| [RenderDoc](https://renderdoc.org) | Captura um quadro e mostra cada chamada de desenho. | Essencial | Grátis | Programa |  |
| [NVIDIA Nsight Graphics e Systems](https://developer.nvidia.com/nsight-graphics) | Perfil de GPU e CPU em placas NVIDIA. | Recomendado | Grátis | Programa |  |
| [AMD Radeon GPU Profiler](https://gpuopen.com) | Perfil de GPU em placas AMD. | Opcional | Grátis | Programa |  |
| PIX | Perfil de GPU e CPU da Microsoft para DirectX 12. | Recomendado | Grátis | Programa |  |
| Intel VTune e GPA | Perfil de CPU e de GPU Intel. | Opcional | Grátis | Programa |  |
| [Superluminal](https://superluminal.eu) | Perfil de CPU rápido e preciso, muito usado em estúdio. | Opcional | Pago | Programa |  |
| [Tracy Profiler](https://github.com/wolfpld/tracy) | Perfilador aberto de CPU e GPU em tempo real. | Opcional | Grátis | Programa |  |
| Simplygon / InstaLOD | Gerar LODs e proxies e otimizar malhas automaticamente. | Opcional | Grátis limitado | Programa |  |
| Oodle e Bink | Compressão de dados, textura e vídeo (vêm com a Unreal). | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| CSV Profiler e PerfReportTool | Relatório de desempenho de uma sessão de jogo inteira. | Opcional | Vem na Unreal | Recurso da Unreal |  |

## Versão, build e produção (14)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Perforce (Helix Core)](https://www.perforce.com) | Controle de versão padrão de estúdio: arquivos grandes e travas de binário. | Essencial | Grátis limitado | Programa |  |
| [Git + Git LFS](https://git-lfs.com) | Versão para equipe pequena, com os arquivos grandes no LFS. | Recomendado | Grátis | Programa | sim |
| [UEGitPlugin (Project Borealis)](https://github.com/ProjectBorealis/UEGitPlugin) | Git dentro do editor da Unreal, com travas de arquivo. | Opcional | Grátis | Plugin |  |
| Unity Version Control | Antigo Plastic SCM; alternativa ao Perforce, boa para artistas. | Opcional | Grátis limitado | Programa |  |
| UnrealGameSync | Sincroniza a equipe com a versão certa e binários prontos. | Recomendado | Grátis | Programa |  |
| Horde | Build, testes e compilação distribuída da Epic. | Opcional | Grátis | Programa |  |
| Unreal Build Accelerator | Compilação distribuída de C++ e shaders. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Zen Server (cache compartilhado) | Shaders e texturas compilados uma vez para a equipe toda. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| BuildCookRun (Unreal Automation Tool) | Cozinhar e empacotar o jogo por linha de comando. | Essencial | Vem na Unreal | Recurso da Unreal |  |
| Jenkins / TeamCity | Build automática e noturna. | Recomendado | Grátis limitado | Programa |  |
| Incredibuild / FASTBuild | Compilação distribuída em várias máquinas. | Opcional | Grátis limitado | Programa |  |
| Jira, Linear ou Codecks | Tarefas, bugs e sprints. | Recomendado | Grátis limitado | Serviço |  |
| Notion ou Confluence | Documento de design, bíblia do jogo e ADRs. | Recomendado | Grátis limitado | Serviço | sim |
| Miro | Quadros de fluxo, mapa e missões. | Opcional | Grátis limitado | Serviço |  |

## Testes, QA e telemetria (7)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Automation Test Framework | Testes automáticos de código e de mapa (Functional Tests). | Essencial | Vem na Unreal | Recurso da Unreal |  |
| Gauntlet | Roda o jogo em série para testes e medidas de desempenho. | Recomendado | Vem na Unreal | Recurso da Unreal |  |
| Comparação de capturas | Acha mudança visual entre versões pelas fotos (Screen Comparison). | Recomendado | Vem na Unreal | Recurso da Unreal | sim |
| Sentry / BugSplat / Backtrace | Relatório de crash com pilha de chamadas, do jogador para a equipe. | Essencial | Grátis limitado | Serviço |  |
| Steam Playtest | Testes fechados com jogadores pela Steam. | Recomendado | Grátis | Serviço |  |
| GameAnalytics | Telemetria: onde o jogador morre, trava ou desiste. | Opcional | Grátis limitado | Serviço |  |
| Testes com pessoas | Rodadas de 5 jogadores observados em silêncio, com anotação. | Essencial | Grátis | Prática | sim |

## Plataformas e distribuição (4)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Steamworks](https://partner.steamgames.com) | Loja, conquistas, nuvem e builds na Steam (taxa por jogo). | Essencial | Pago | Serviço |  |
| Epic Online Services | Contas, conquistas, multiplayer e anti-cheat, multiplataforma. | Recomendado | Grátis | Serviço |  |
| Epic Games Store | Loja da Epic; publicar lá pode mudar o royalty da engine (confira o programa atual). | Opcional | Grátis | Serviço |  |
| SDKs de console | PlayStation, Xbox GDK e Nintendo; exigem cadastro e aprovação de cada fabricante. | Opcional | Sob aprovação | Serviço |  |

## Plugins da comunidade (4)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Blueprint Assist | Formata e organiza Blueprints automaticamente. | Recomendado | Pago | Plugin |  |
| Electronic Nodes | Fios de Blueprint legíveis. | Opcional | Pago | Plugin |  |
| [Flow Graph](https://github.com/MothCocktail/FlowGraph) | Missões e narrativa por nós, código aberto. | Recomendado | Grátis | Plugin |  |
| Logic Driver Pro | Máquinas de estado em Blueprint para diálogo, missão e IA. | Opcional | Pago | Plugin |  |

## Pré-produção e narrativa (5)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [PureRef](https://www.pureref.com) | Mural de referências sempre à vista. | Essencial | Grátis limitado | Programa | sim |
| [Storyboarder](https://wonderunit.com/storyboarder) | Storyboard rápido. | Opcional | Grátis | Programa |  |
| [articy:draft X](https://www.articy.com) | Diálogo ramificado e roteiro, com importação para a Unreal. | Recomendado | Grátis limitado | Programa |  |
| [Twine](https://twinery.org) | Protótipo de narrativa ramificada. | Opcional | Grátis | Programa |  |
| Bíblia do jogo e ADRs | Documento vivo de canon, arte e decisões técnicas. | Essencial | Grátis | Prática | sim |

## IA de apoio ao desenvolvimento (2)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Claude Code](https://code.claude.com/docs) | Programar, automatizar o editor, revisar com prova e manter a documentação. | Recomendado | Pago | Programa | sim |
| [MediaPipe](https://ai.google.dev/edge/mediapipe) | Medir rosto e corpo em fotos (a régua do fidelidade.py e do medidas_rosto.py). | Opcional | Grátis | Biblioteca ou projeto | sim |

## Estação de trabalho (8)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| Placa de vídeo | RTX 4070 ou melhor, com 12 GB de memória de vídeo ou mais (Lumen, Nanite, ray tracing, DLSS). | Essencial | Pago | Equipamento |  |
| Processador | 12 núcleos ou mais: compilar C++ e shaders é o gargalo do dia a dia. | Essencial | Pago | Equipamento |  |
| Memória RAM | 64 GB para mundo aberto, MetaHuman e Houdini ao mesmo tempo. | Essencial | Pago | Equipamento |  |
| SSD NVMe | 2 TB ou mais só para projeto e cache. | Essencial | Pago | Equipamento |  |
| Monitor calibrado | Cor certa para textura e gradação, com calibrador (Calibrite, Datacolor). | Recomendado | Pago | Equipamento |  |
| Mesa digitalizadora | Esculpir e pintar (Wacom, XP-Pen, Huion). | Recomendado | Pago | Equipamento |  |
| iPhone com Face ID | Captura de rosto com Live Link Face e MetaHuman Animator. | Recomendado | Pago | Equipamento | sim |
| Controle de console | Testar sempre com controle (Xbox, DualSense). | Essencial | Pago | Equipamento | sim |

## Negócio, legal e estudo (9)

| Ferramenta | Para quê | Prioridade | Custo | Tipo | NOVAMENTE |
|---|---|---|---|---|---|
| [Licença da Unreal (EULA)](https://www.unrealengine.com/en-US/eula/unreal) | Royalty de 5% sobre a receita bruta acima de US$ 1 milhão por jogo; confira os termos atuais. | Essencial | Grátis | Referência |  |
| Licenças dos assets | Guardar a licença de cada asset, fonte e música usados (Fab, Megascans, bancos de som). | Essencial | Grátis | Prática |  |
| Classificação indicativa | ClassInd no Brasil e IARC nas lojas que usam. | Essencial | Grátis | Serviço |  |
| Registro de marca (INPI) | Proteger o nome do jogo. | Recomendado | Pago | Serviço | sim |
| Contratos de cessão de direitos | Com cada freelancer: arte, música, dublagem, captura. | Essencial | Pago | Prática |  |
| Editais e incentivo | Ancine, Spcine e leis de incentivo para financiar. | Opcional | Grátis | Serviço | sim |
| [Epic Developer Community](https://dev.epicgames.com/community) | Documentação oficial, cursos e fórum da Unreal. | Essencial | Grátis | Referência |  |
| [GDC Vault e Unreal Fest](https://gdcvault.com) | Palestras técnicas de estúdios AAA. | Recomendado | Grátis limitado | Referência |  |
| [Advances in Real-Time Rendering](https://advances.realtimerendering.com) | Curso anual do SIGGRAPH com as técnicas de render dos AAA. | Opcional | Grátis | Referência |  |

## Fora do NOVAMENTE

Pelas regras de arquitetura do projeto, não entram:
- Mixamo, porque não tem transferência de peso nem contato firme para MMA;
- o Lyra como base de jogo;
- pacotes de assets orientais.
