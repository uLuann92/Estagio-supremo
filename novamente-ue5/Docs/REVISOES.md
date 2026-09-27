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
