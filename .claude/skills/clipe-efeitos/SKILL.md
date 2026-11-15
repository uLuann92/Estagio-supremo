---
name: clipe-efeitos
description: "Aplica transições entre seções e efeitos rítmicos de seção sobre as cenas já animadas e a letra. Use em /clipe-efeitos, após a clipe-letra."
---

# clipe-efeitos

Desenha e queima no render as transições entre seções e os efeitos rítmicos que ligam os quadros ou valem para a seção inteira (punch, tremida, flash, rampas, congelamento, glitch, barras, luz). Não refaz a atuação interna dos quadros (feita na `clipe-animar`) nem altera a tipografia da letra (feita na `clipe-letra`).

- **Lê:** `_CLAUDE/projeto.json` (blocos `musica`, `roteiro`, `animar`, `letra`), `_CLAUDE/musica/` (batidas e acentos), `_CLAUDE/roteiro/`, renders das etapas `clipe-animar` e `clipe-letra`, perfil em `edicao/perfis/<perfil>/estilo-efeitos.md`
- **Escreve:** bloco `efeitos` em `_CLAUDE/projeto.json`, plano e eventos para o som em `_CLAUDE/efeitos/`, cenas/seções processadas e prévia em `Renders/` (versionadas)
- **Próximo passo:** `/clipe-sfx`

Se `clipe-letra` não estiver `concluido`, pare e sugira terminá-la.

## Ofício
Tendência, não regra nas escolhas criativas; detalhes e tabela completa do repertório em `.claude/skills/fluxo-de-edicao/guias/etapa-efeitos.md` (curvas em `oficio-motion.md`).

- **O efeito sublinha a música:** todo efeito responde a um acento real do som. Punch e flash entram no frame exato do acento (ou 1 frame antes); tremida começa no frame do acento com semente fixa para o render sair repetível.
- **Foco na ligação e na seção:** golpes internos de cada quadro já vieram da `clipe-animar`. Aqui entram a base rítmica por seção (automática, segundo a dose do perfil) e os destaques numerados (`fx01`, `fx02`…) nos acentos do roteiro.
- **Um protagonista por momento:** se a letra faz o show ou há palavra gigante, a cena fica firme; se a cena treme ou leva punch, a letra não compete.
- **Dose, variação e escalada:** siga a curva de energia do roteiro (verso contido, subida crescendo, refrão cheio, ponte limpa). Alterne tipos e compassos em branco para não virar metrônomo. Guarde o efeito mais forte para o ápice do clipe.
- **Transições entre seções:** terminam exatamente no primeiro tempo da seção nova, ocupando o fim da anterior (último tempo ou meio compasso). Uma transição marcante por virada de seção (corte seco no silêncio, clarão, rampa de velocidade, zoom, glitch curto, mergulho no preto) e corte seco dentro da seção.
- **Folga de borda:** toda cena que recebe punch ou tremida precisa de folga de escala (ex.: 104–108% de base) para nunca revelar borda preta.
- **Saúde e flashes (regra firme):** no máximo 3 flashes por segundo, evitando branco puro de quadro inteiro ou vermelho saturado. Prefira opacidade parcial e a cor de acento do perfil.
- **Queimado no render:** como não há programa de edição, aplique tudo em vídeo (via filtros do FFmpeg ou recompondo no HyperFrames `npx --yes hyperframes@<versão>` com a cena como fundo; pesquisar na hora o melhor suporte para cada efeito).

## Perfil
Leia `edicao/perfis/<perfil>/estilo-efeitos.md` antes de planejar. Ele decide:
- Quais efeitos do repertório são usados ou proibidos.
- A dose e a força da base automática em cada tipo de seção (verso, subida, refrão, ponte).
- O estilo de transição preferido nas viradas e a cor/opacidade dos flashes.

## Scripts
Na primeira vez que a etapa rodar num vídeo, escreva os scripts que faltam em `edicao/scripts/`, teste num trecho curto e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar |
|---|---|---|
| `edicao/scripts/planejar_efeitos.py` | Gera a base por seção a partir das batidas e valida o plano completo (`_CLAUDE/efeitos/plano.json`), exportando também os eventos de impacto/transição para a `clipe-sfx` | Passar de 3 flashes/s (recusar o plano); somar dois efeitos de escala no mesmo frame; aplicar punch/tremida sem folga de borda; colidir destaque de câmera com palavra gigante da letra |
| `edicao/scripts/render_efeitos.py` | Queima os efeitos da base, os destaques (`fxNN`) e as transições sobre os renders das cenas/letra a 24 fps, 1920×1080 | Semente aleatória solta na tremida (muda a cada render); atrasar o efeito em relação ao frame do acento; mostrar borda escapando; sobrescrever versão anterior em `Renders/` |

## Passo a passo
1. Confira status e pendências: `python edicao/scripts/estado.py <pasta do projeto> status`.
2. Leia o perfil (`estilo-efeitos.md`), o roteiro, os acentos da música e o mapa da letra.
3. Escreva o plano em `_CLAUDE/efeitos/plano.json`: regras de base por seção, transições de virada e destaques desenhados à mão (`fx01`, `fx02`… com efeito, compasso/tempo, força e cena).
4. Rode `planejar_efeitos.py` para expandir a base, validar limite de flashes (≤ 3/s), folga de borda e conflitos com a letra, e salvar a lista de eventos para o som (`_CLAUDE/efeitos/eventos-sfx.json`).
5. **Primeira vez ou efeito novo:** renderize um teste curto de 10 s (contendo um punch, uma tremida, um flash e uma transição) em `Renders/`, peça para o usuário conferir, anote na validação e só então siga para o clipe inteiro.
6. Renderize o vídeo com efeitos e transições queimados em arquivo versionado em `Renders/` (`*_efeitos_v1.mp4`), mantendo a música sincronizada.

## Resumo no chat
Curto: o que entrou na base por seção, quantos destaques (`fx01`..`fxNN`) e transições foram aplicados, confirmação de que o limite de flashes passou na verificação, pontos que pedem atenção do usuário e o caminho do vídeo em `Renders/`. Marque a etapa como `aguardando_aprovacao` com `python edicao/scripts/estado.py <pasta do projeto> ...`.

## Revisão
O usuário devolve pelo chat por código ou por seção (ex.: `"fx07 mais forte"`, `"menos tremida no verso 2"`, `"troca a transição para o refrão final"`). Ajuste no plano apenas o que foi pedido, revalide flashes e conflitos, re-renderize só os trechos afetados gerando versão nova (`v2`, `v3`… sem apagar a anterior) e anote aprendizados em `_CLAUDE/aprendizados.md`.

*(Nota: se o usuário pedir diagnóstico extra num trecho específico, pode-se usar o segundo olhar com `gemini.py perguntar` em fps alto — a 1 fps flash e tremida somem — respeitando o teto de gasto.)*

## Aprovação
Marque `concluido` no estado do vídeo, informe quantos aprendizados foram anotados em `_CLAUDE/aprendizados.md` e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto, nem sobrescrever renders anteriores.
- Recusar qualquer plano com mais de 3 flashes por segundo.
- Se a montagem (`clipe-animar`) ou a letra (`clipe-letra`) mudarem depois, recalcular os efeitos do trecho afetado.
- Falar com o usuário em português, de forma curta e direta.
