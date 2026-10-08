# Registro de revisões

Cada rodada: data, portão, o que foi conferido, problemas, correções, o que ficou para o autor.

## 2026-09-27 · Rodadas 1 a 5 (na nuvem, sem Unreal)

Ambiente: máquina sem placa de vídeo e sem Unreal. Por isso as checagens abaixo substituem a compilação real, mas **não** a dispensam. O portão R0 continua aberto até compilar na 5.8.

**Rodada 1 · coerência do código**
- Script que cruza cada função declarada nos headers com a definição nos `.cpp`: nada faltando, nada sobrando.
- Balanço de chaves, parênteses e colchetes em todos os arquivos: ok.

**Rodada 2 · paridade com o protótipo "Luta no Largo"**
- Alcance: o protótipo multiplica por altura / 1,70 m. Corrigido: Luan 0,96, Igor 1,01 (antes 1,0 para os dois).
- 1ª Lei: o jogador tem 0,75 s de atraso da dor, o Igor 0,5 s. Corrigido: o modo de jogo aplica no jogador.
- A Sombra acabava no intervalo; no protótipo ela atravessa. Corrigido.
- Lutador caído: a distância e a direção agora usam a pélvis do ragdoll (a cápsula fica para trás). Afetava o ground and pound e a IA.
- Montagem com root motion andava duas vezes (root motion + avanço do código). Corrigido: o avanço só vale sem root motion.
- Ground and pound em corpo caído agora dá impulso no ragdoll.
- Revanche para a montagem de vitória que estava tocando.

**Rodada 3 · compilação contra cabeçalhos de checagem**
- Os 14 `.cpp` compilam com clang (C++20, `-Wall -Wextra -Wshadow`) contra uma imitação mínima da API da Unreal. Teste negativo confirma que assinatura errada de evento é pega.
- Checagem própria de "variável que esconde membro herdado" (o compilador da Microsoft trata como erro na Unreal): corrigidos `Mesh` (escondia `ACharacter::Mesh`) e `Slot` (escondia `UWidget::Slot`).
- `FMath::Max` com float e double misturados na câmera: corrigido.
- Arquivos C++ salvos em UTF-8 com BOM (acentos nos textos).

**Rodada 4 · shaders**
- Os 6 nós Custom (pós da Sombra, olhos, hematomas, pedra portuguesa, cúpula, alambrado) compilam como HLSL (glslang, SPIR-V) do jeito que a Unreal monta a função.
- Render de conferência do pós-processamento em Python com a mesma matemática: duotone, garras, Realidade 2 e Visão do Caos batem com o protótipo. Defeito achado e corrigido: as garras da direita curvavam para cima e se cruzavam (herdado do protótipo); agora são espelhadas.
- Comentários são tirados antes de colar no material (o compilador de shader quer ASCII).

**Rodada 5 · scripts do editor**
- `setup_novamente.py`, `build_largo.py` e `capture_review.py` rodam do começo ao fim contra um módulo `unreal` falso (pega erro de Python, não de API).
- O ajuste dos `.ini` preserva o que existe, atualiza só as chaves dele e não duplica nada rodando duas vezes.

**Não verificado (primeira coisa a fazer no PC)**
- Compilar na 5.8 de verdade (nomes de API que podem ter mudado: `MapKey`, propriedades de pós-processamento no Python, posição do mundo em nó Custom).
- Rodar os três scripts no editor e fotografar (portão R0).
- Pontos dos hematomas na UV real da cabeça do MetaHuman.

## 2026-09-28 · Rodada 6: mundo aberto e travamento de alvo (na nuvem, sem Unreal)

**O que mudou**
- Regras de cada golpe saíram do modo de jogo da arena para o `NovCombatDirectorSubsystem`, que vale em qualquer mapa: queda, nocaute, hit-stop, Visão do Caos, medidor da Sombra, legendas. A arena escuta os eventos e ficou só com rounds, relógio, decisão, falas da cena e tela final.
- Novo `NovTargetingComponent`:
  - soft-lock pela direção do analógico, com folga para não piscar e prioridade para quem está atacando;
  - trava liga e desliga no botão;
  - troca de alvo por toque do analógico direito, puxão do mouse ou Z / C;
  - solta ou troca sozinho quando o alvo cai nocauteado, some de vista por 1 s ou fica a mais de 22 m.
- Nova `NovCombatCamera`: câmera de ombro que mistura exploração e enquadramento de luta pelo peso do travamento, abre para caber o grupo e encosta sem atravessar parede nas ruas estreitas.
- O lutador anda em relação à câmera quando não tem alvo e vira na direção do passo.
- A IA percebe o Luan no mundo aberto, só reage a golpe que é para ela, desiste quando ele foge e pede ficha de ataque (no máximo dois batendo ao mesmo tempo; os outros rodeiam mais longe).
- A Sombra no controle foi para L3; R3 virou a trava, como é padrão.
- Regras de arquitetura no prompt principal e no `CLAUDE.md`:
  - zero assets orientais;
  - Mixamo descartado;
  - Game Animation Sample em vez de Lyra;
  - combate mão e pé no plugin;
  - GAS só por ADR;
  - World Partition;
  - calibração antes de efeito.

**Paridade da arena conferida**
- Mesmo hit-stop (só os dois lutadores), mesmos limites de queda e nocaute.
- A Visão do Caos com a fala do Felipe na primeira vez.
- A câmera lenta do nocaute somada com a da Visão do Caos (vale a menor).
- A fala do Mateus e o rugido do público.
- A arena com um só inimigo nunca esbarra no limite de fichas.

**Checagens**
- Os 17 `.cpp` compilam com clang contra os cabeçalhos de checagem (`-Wall -Wextra -Wshadow`), sem erro nem aviso.
- Nenhuma variável esconde membro herdado.
- Toda função declarada tem corpo.

**Não verificado**
- Compilar na 5.8.
- Sensação do soft-lock e da câmera com gente jogando (valores de distância, ângulo e velocidade estão expostos para ajuste).

## 2026-09-29 · Rodada 7: prompt AAA+ e kit que obriga a prova (na nuvem, sem Unreal)

**O que mudou**
- `Docs/PROMPT_AAA_PLUS.md`, o novo prompt principal. Mantém só as referências (render do Luan criança e capa), descritas em detalhe e com números medidos; o diagnóstico antigo saiu porque o jogo mudou. Traz:
  - tabela de templates prontos por área (anatomia, física, movimento, mundo, luz);
  - o caminho do rosto 100% fiel (FaceBuilder ou escultura, Mesh to MetaHuman, sala do render recriada, medição);
  - o estilo em qualquer PC (o que nunca muda entre qualidades e o que pode baixar);
  - a lista anti-cru com números;
  - portões P0 a P6 e as regras de trabalho sem atalho.
- `Scripts/fidelidade.py`: mede proporções do rosto (MediaPipe, 478 pontos), tom de pele (Delta E 2000) e clima da imagem contra as referências. Modo lote por `Referencias/pares.json`; referência ausente vira reprovação com motivo, não queda.
- `Scripts/preparar_referencias.py`: corta a prancha de quatro vistas nos nomes fixos.
- `Scripts/capture_review.py`: qualquer mapa, câmeras com tag `Rev_*` e várias qualidades por rodada (`NOV_TIERS=4,1`).
- `claude-kit/` (instalado com `instalar.py`):
  - gancho `Stop` que exige rodada nova, medição e parecer APROVADO depois de mudança visual;
  - subagente revisor-visual (juiz duro com notas de 0 a 10);
  - skill `/revisao-aaa`;
  - regras fixas em `.claude/rules/aaa-plus.md`;
  - selo das referências e do juiz;
  - travas de edição e esforço alto.

**Checagens**
- Gancho em projeto falso, 10 cenários:
  - sem mudança libera;
  - mudança sem rodada bloqueia;
  - "PENDENTE:" libera;
  - rodada sem qualidade 1, sem medição ou sem parecer bloqueia;
  - parecer REPROVADO devolve os defeitos;
  - parecer aprova com medição reprovada bloqueia;
  - tudo certo libera;
  - mudança depois da rodada bloqueia;
  - referência alterada bloqueia pelo selo.
- Também conferidos: o limite de 8 bloqueios seguidos, o reinício na vez seguinte, a conversa ausente e a entrada vazia.
- Instalador rodado duas vezes num projeto com `settings.json` próprio: junta sem apagar e não duplica o gancho.
- `fidelidade.py` nas imagens do autor:
  - o render contra o close passa (erro médio 1,1%, pele Delta E 1,5);
  - o manequim antigo reprova;
  - o três quartos contra a frente reprova pelo ângulo;
  - o perfil não tem rosto detectável e é julgado só pelo clima e pelo revisor;
  - a vista de costas também.

**Não verificado**
- O gancho dentro do Claude Code no Windows (caminho do `python`; se falhar, trocar por `py -3` no `settings.json`).
- As fotos com câmeras `Rev_*` num mapa de verdade.

**Para o autor decidir**
- Cor dos olhos: proposta de íris avelã com anel verde-oliva (castanho na luz quente, verde na fria), que explica o render e a capa.

## 2026-09-29 · Rodada 8: prompt de personagens e medidas de rosto e corpo (na nuvem, sem Unreal)

**O que mudou**
- `Docs/PROMPT_PERSONAGENS.md`, separado do AAA+ e só com três fatores:
  - corpos padrão proporcionais (garoto de 13 a 14 anos, mulher e homem, magros);
  - biblioteca de templates por região (rosto, cabelo, sobrancelha, pelos, braços, pernas, barriga, cintura, ombros, postura, mãos, pés, pele, olhos, dentes, roupa em camadas, tecidos);
  - o rosto do Luan refeito pelas medidas do render.
- `Scripts/medidas_rosto.py`:
  - ficha com 35 medidas, 3 ângulos, 5 proporções, assimetria e cores (pele, cabelo, íris, lábio, sobrancelha, roupa);
  - comparação com tolerância de identidade, expressão e cor.
- `Scripts/corpos_padrao.json`: os três corpos padrão e as variantes (médio, forte, acima do peso).
- `Scripts/medir_corpo.py`: fita métrica da malha em .obj, só com numpy. Mede altura, cabeças, entrepernas, larguras e as voltas de pescoço, peito, cintura, quadril, coxa e panturrilha.
- `Scripts/medir_esqueleto.py`: segmentos entre articulações e simetria pelos ossos do MetaHuman, dentro da Unreal.
- Kit:
  - o selo e as travas cobrem os scripts de medida, o `corpos_padrao.json` e as fichas;
  - o instalador copia tudo e os dois prompts.

**Checagens**
- `medidas_rosto.py` nas imagens do autor:
  - a vista de frente contra a ficha do close passa (erro médio de identidade 0,9%, pior 1,8%; cores com Delta E até 3,1). Isso mede o ruído e justifica a tolerância de 3%;
  - o rosto esticado 6% na largura reprova (nariz, filtro, terço médio);
  - o três quartos reprova pelo ângulo;
  - a imagem aquecida reprova na pele e na roupa;
  - a vista de costas diz que não há rosto.
- `medir_corpo.py` num corpo sintético em pose A com medidas conhecidas:
  - todas as medidas batem com a geometria dentro de 0,5 cm;
  - a mesma malha em metros e com Z para cima dá o mesmo resultado;
  - uma cintura fora do padrão é apontada.
- `medir_esqueleto.py` contra um módulo `unreal` falso: os segmentos batem, e uma coxa direita 3% maior é pega na simetria.
- O instalador sela os scripts novos; mexer no `corpos_padrao.json` bloqueia pelo selo.

**Não verificado**
- As funções da Unreal chamadas pelo `medir_esqueleto.py` (`set_skeletal_mesh_asset`, `get_socket_location`, `get_bone_index`, `get_bounds`) numa 5.8 de verdade.
- O `medir_corpo.py` num corpo de MetaHuman exportado (o queixo é achado pelo perfil; se falhar, avisa).

**Para o autor decidir**
- Altura do Luan aos 13–14 anos (padrão 1,58 m; o canon adulto é 1,63 m).
- Os números dos corpos padrão são ponto de partida anatômico, não canon.

## 2026-10-08 · Rodada 9: gente só de MetaHuman (na nuvem, sem Unreal)

**Por quê**
- As capturas do capítulo 2 mostraram pessoas montadas por código e com formas básicas:
  - tronco de caixa;
  - olhos de esfera preta;
  - cabelo de planos soltos.
- Também mostraram a câmera dentro de uma cabeça e dois avisos vermelhos (exposição do Lumen e Sky Light sem céu).

**O que mudou**
- `Docs/PROMPT_HUMANOS.md`:
  - regra zero: todo humano é MetaHuman, nunca código nem primitiva;
  - aparência vinda da obra, numa ficha por personagem com citações literais e capítulo;
  - padrão de bonito, proporcional, simétrico e uniforme, com tiers de elenco;
  - conserto do palco antes de julgar;
  - processo de cada pessoa e o Luan refeito do zero.
- `Scripts/auditar_humanos.py` acusa:
  - código que monta malha num arquivo que fala de gente;
  - asset de personagem com formas básicas ou malha procedural;
  - personagem sem MetaHuman (este como aviso).
  Exceção só declarada no arquivo e mostrada no relatório; a única hoje são os olhos da Sombra no céu do `build_largo.py`.
- Kit:
  - a auditoria entra no selo e nas travas;
  - as regras fixas proíbem gente de primitiva;
  - o revisor reprova pessoa de código ou forma básica e lê o `auditoria_humanos.json`;
  - a rodada roda a auditoria quando mexe em gente;
  - o gancho não deixa encerrar com a auditoria reprovada;
  - o instalador copia o prompt e a auditoria.

**Checagens**
- Num projeto falso, a auditoria:
  - reprova a cabeça montada em C++ e o NPC com cubo e esfera;
  - avisa do personagem sem MetaHuman;
  - não acusa poste feito por código, blockout de cenário, mapa nem a pasta MetaHumans.
- No próprio repositório, dá LIMPO, com a exceção declarada dos olhos da Sombra.
- O gancho bloqueia com a auditoria reprovada e libera com ela limpa.

## 2026-10-08 · Rodada 10: o Luan nas duas idades (na nuvem, sem Unreal)

**Medição**
- O Luan atual (MetaHuman no nível do Game Animation Sample) contra o render da criança:
  - erro médio de identidade 5,5%;
  - 18 medidas fora: testa +27% (entrada de cabelo), olho à base do nariz +10,5%, mandíbula +7,6% e mais quadrada.
  - Também parece haver o material de ferimentos ligado em volta dos olhos.
- As duas imagens do adulto (cabelo longo e cabelo curto cacheado) dão 2,8% entre si, com ângulos diferentes: são a mesma pessoa.

**O que mudou**
- `Docs/PROMPT_LUAN.md`:
  - diagnóstico medido;
  - a verdade de cada idade: o render para os 13 anos; as duas imagens do adulto e o centro da capa para os 31;
  - o que o adulto herda da criança;
  - processo do zero com FaceBuilder, Mesh to MetaHuman e corpo padrão;
  - metas e decisões do autor (altura e variante do adulto).
- `pares.json` do kit ganhou as câmeras do adulto (`Rev_08_Adulto_A` e `_B`); o instalador copia o prompt novo.

**Para o autor**
- Prancha de quatro vistas do adulto, como a da criança.
- Altura dos 31 anos (1,63 m ou 1,84 m) e variante de corpo (magro ou médio).
