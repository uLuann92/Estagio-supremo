---
name: clipe-sfx
description: "Adiciona poucos efeitos sonoros de apoio sobre a música e as cenas animadas. Use em /clipe-sfx, após a clipe-efeitos."
---

# clipe-sfx

Escolhe, sincroniza e nivela poucos efeitos sonoros de apoio sobre a música, guiado pelas transições, movimentos de câmera e golpes das cenas. Gera a faixa de efeitos mixada e um vídeo de prévia para revisão. Não altera a música original nem faz a masterização final.

- **Lê:** `_CLAUDE/projeto.json` (blocos `musica`, `roteiro`, `animar`, `efeitos`), `_CLAUDE/musica/` (grade de batidas, acentos e LUFS), `_CLAUDE/roteiro/`, `_CLAUDE/efeitos/`, biblioteca em `edicao/sons/`, perfil em `edicao/perfis/<perfil>/`
- **Escreve:** bloco `sfx` no estado, arquivos em `_CLAUDE/sfx/` (`eventos.json`, `plano-sfx.json`, `faixa-sfx.wav`, `faltando.md`), entrega de revisão em `Renders/previa-sfx-v1.mp4`
- **Próximo passo:** `/clipe-finalizar`

Se a etapa `efeitos` não estiver `concluido`, pare e sugira terminá-la com `/clipe-efeitos`.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-sfx.md` (sobretudo §2 e §5) quando precisar de detalhes. Escolhas criativas são tendência, não regra; sincronia e teto de pico são regras firmes.

- **A música é a protagonista:** o efeito sonoro só apoia. Use poucos sons (um punhado por seção), apenas nas viradas, transições fortes e acentos visuais claros (golpe na cena, entrada do refrão, subida sem riser na batida).
- **A música não se mexe:** nunca abaixe, corte ou equalize a faixa da música para caber efeito, salvo pedido do usuário.
- **Sem briga no grave:** não empilhe sub ou grave sobre o bumbo ou 808 (embola e estoura). Impactos sobre a música devem ser médios e agudos; o peso já vem da batida.
- **Tom e ruído:** sons com nota precisam combinar com o tom da música. Na dúvida, prefira sons de ruído (whoosh, impacto seco, papel, corte), que não têm nota.
- **Sincronia na grade:** o pico do efeito cai cravado no frame do acento ou evento (pela grade da etapa `musica`, a 24 fps):
  - **Impacto:** transiente no frame exato do evento.
  - **Whoosh:** o **pico** cai no frame da troca ou chegada (quando freia), nunca o frame inicial do arquivo.
  - **Riser:** termina exatamente no frame do evento e corta seco (deixe ~0,5 s de respiro sem outros efeitos antes do impacto).
- **Camadas e variação:** no máximo 3 camadas por momento forte (`principal`, `apoio`, `doce`). Não repita o mesmo arquivo de áudio em menos de ~20 s.
- **Nível contra a música:** meça a loudness da música e posicione os efeitos abaixo dela, audíveis sem competir. Música masterizada não tem folga: cuide do pico real ao somar.
- **Biblioteca (`edicao/sons/`):** começa vazia. Monte aos poucos com sons de licença clara, separados por categoria (`whoosh/`, `impacto/`, `riser/`, `corte/`, `interface/`). Se faltar um som bom, deixe sem e anote em `_CLAUDE/sfx/faltando.md`; nunca force um som ruim.

## Perfil
Leia em `edicao/perfis/<perfil>/` antes de planejar:
- `sfx.md` (ou seção equivalente do perfil): densidade de efeitos por seção, alvos de nível em dB relativos à música por categoria/camada, teto de pico e timbres preferidos.

## Scripts
Na primeira vez que a etapa rodar num vídeo, escreva os scripts que faltam em `edicao/scripts/`, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar |
|---|---|---|
| `edicao/scripts/sfx_indexar.py` | Varre `edicao/sons/`, mede duração útil (sem silêncio inicial), tempo exato até o pico, forma e brilho, e gera `edicao/sons/indice.json`. | Não contar silêncio inicial no tempo até o pico; ignorar arquivos corrompidos ou com clipping. |
| `edicao/scripts/sfx_eventos.py` | Junta cortes, movimentos de câmera (`animar`), transições (`efeitos`) e acentos (`musica`) em `_CLAUDE/sfx/eventos.json` com IDs estáveis (`ev01`…) e mede a loudness da música. | Mudar IDs de eventos que não mudaram entre rodadas; listar cortes invisíveis sob tela cheia. |
| `edicao/scripts/sfx_montar.py` | Lê `_CLAUDE/sfx/plano-sfx.json`, alinha cada som pelo pico/início/fim a 24 fps, ajusta o nível, gera `_CLAUDE/sfx/faixa-sfx.wav` e o vídeo `Renders/previa-sfx-vN.mp4` somando música + efeitos sem mexer na faixa da música. | Alinhar whoosh pelo início em vez do pico; repetir arquivo em <20 s; estourar 0 dBFS na soma com a música; sobrescrever versão anterior (`v1`, `v2`…). |

## Passo a passo
1. Confira o status e pendências (`python edicao/scripts/estado.py <pasta do projeto> status`).
2. Verifique `edicao/sons/`. Se estiver vazia ou sem índice, organize os sons disponíveis de licença clara e rode `sfx_indexar.py`.
3. Rode `sfx_eventos.py` para consolidar os gatilhos visuais e musicais em `_CLAUDE/sfx/eventos.json`.
4. Escreva `_CLAUDE/sfx/plano-sfx.json` atribuindo IDs `sfx01`, `sfx02`… apenas aos momentos que pedem apoio sonoro, definindo evento, camada, arquivo, alinhamento (`pico`, `inicio` ou `fim`) e ajuste fino em dB.
5. **Primeira vez de todas:** gere um trecho curto de teste (~15 s no refrão) com `sfx_montar.py`, peça ao usuário para conferir sincronia e volume contra a música, anote no arquivo de validação e só então siga para o vídeo completo.
6. Gere ` _CLAUDE/sfx/faixa-sfx.wav` e a entrega `Renders/previa-sfx-v1.mp4` (sem sobrescrever versões anteriores). Corrija qualquer aviso do script (som não achado, repetição próxima, pico estourando).

## Resumo no chat
Curto: quantos efeitos entraram (`sfx01` a `sfxNN`), lista rápida com tempo e papel de cada um, sons anotados em `faltando.md` (se houver) e o caminho `Renders/previa-sfx-v1.mp4`. Marque a etapa como `aguardando_aprovacao`.

## Revisão
O usuário devolve pelo chat por número ou tempo (`sfx04 mais baixo`, `sfx02 tira`, `troca o sfx05`, `sfx01 um frame antes`):
- "mais baixo" / "mais alto": ajuste 3 dB na direção pedida (salvo valor explícito).
- Ajuste apenas o que foi citado em `_CLAUDE/sfx/plano-sfx.json`, gere nova versão (`previa-sfx-v2.mp4`) e anote aprendizados de gosto e nível em `_CLAUDE/aprendizados.md`.

## Aprovação
Quando o usuário aprovar, marque `sfx` como `concluido` no estado, diga quantos aprendizados ficaram anotados em `_CLAUDE/aprendizados.md` e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos originais do projeto.
- Nunca alterar, cortar, comprimir ou abaixar a faixa da música original sem pedido explícito do usuário.
- Nunca sobrescrever um render de entrega anterior; incremente sempre a versão (`v1`, `v2`…).
- Falar com o usuário em português, de forma curta e direta.
