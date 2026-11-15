# Clipe musical com letra na tela (rap geek, AMV, lyric video)

O tipo de vídeo em que **a música manda**: uma faixa pronta (rap, trap, rock), cenas montadas no ritmo (anime, jogo, arte própria, filmagem) e a letra animada na tela. É o formato dos canais de rap geek.

Ele muda a base do fluxo. No vídeo falado, tudo se alinha pela **fala**. Aqui, tudo se alinha pela **grade de batidas** e pela **letra cantada**. O resto dos princípios (`principios-do-fluxo.md`) vale igual.

## 1. O que muda em relação ao fluxo de referência
| Fluxo falado | Clipe musical | Guia |
|---|---|---|
| preparar (transcrição da fala) | **música:** grade de batidas, estrutura, letra alinhada por palavra | `etapa-musica.md` |
| — | **cenas:** catálogo do material bruto (cada cena descrita e medida) | `etapa-cenas.md` |
| motion-mapa (plano das animações) | **roteiro:** o plano do clipe inteiro, compasso a compasso (cena, letra, efeito, energia) | `etapa-roteiro-clipe.md` |
| cortes | **montagem:** as cenas escolhidas, cortadas e encaixadas na grade | `etapa-cenas.md` |
| motion-render | **letra:** a tipografia animada, sincronizada por palavra | `etapa-letra.md` |
| câmera | **efeitos:** punch, tremida, flash, transições e rampas no ritmo | `etapa-efeitos.md` |
| sfx | **sfx:** poucos, apoiando a música, nunca brigando com ela | `etapa-sfx.md` (§5) |
| — | **finalizar:** look, áudio, exportação, conferência e extras | `etapa-finalizar.md` |

Ordem sugerida: iniciar → música → cenas → roteiro → montagem → letra → efeitos → sfx → finalizar. A etapa de **assets** entra depois do roteiro, quando ele pedir algo que falta (fonte, logo do canal, textura, partículas, uma cena específica).

**De onde vem a imagem** (decida cedo; muda duas etapas):
- **Vídeo pronto** (episódios, gameplay, filmagem): etapas **cenas** e **montagem**, como na tabela.
- **Quadros de mangá animados** (o "mangá animado" dos edits de rap geek): no lugar delas, **painéis** (catálogo dos quadros) e **animar painéis** (camadas, câmera, impacto, tremida, linhas de velocidade, cor). Cada quadro animado vira uma cena. Guia: `etapa-paineis.md`. A pessoa não precisa trazer vídeo; precisa das páginas.
- **Os dois misturados:** dá, com um catálogo só e o roteiro dizendo de onde vem cada compasso.

Adaptações comuns:
- **Lyric video sem cenas** (só fundo e letra): pula cenas e montagem; o roteiro planeja fundo e letra.
- **Clipe sem letra na tela:** pula a etapa de letra; a letra alinhada ainda serve para casar cena com verso.
- **Vídeo curto vertical** (um refrão): junta roteiro + montagem e letra + efeitos.

## 2. Decisões a mais na entrevista
Pergunte depois das decisões 1 a 3 do `decisoes.md`:
- **A música:** quem produz, e se a pessoa tem as **faixas separadas** (voz e instrumental). Com elas, o alinhamento da letra e a leitura da batida ficam muito melhores. Sem elas, o fluxo separa por programa (ex.: Demucs).
- **A letra:** existe escrita, na versão final? Ela é a verdade para a grafia. Quantas vozes cantam (participações), e se cada uma tem tratamento próprio.
- **O material das cenas:** vídeo pronto ou quadros de mangá para animar (acima). De onde vem (episódios, gameplay, volumes digitais, arte encomendada, imagem gerada, filmagem), em que qualidade, e se vem com legenda, balão em outra língua ou marca d'água queimada na imagem.
- **Mangá animado, se for o caso:** preto e branco com acento de cor ou colorido; os balões ficam, saem ou viram tipografia; quem corrige as máscaras dos quadros-herói (a pessoa, num editor de imagem, ou só o automático); se há plano pago de um modelo de imagem para refazer fundos (`etapa-paineis.md` §3).
- **Taxa de quadros do projeto:** a do material principal. Anime costuma estar em 23,976; jogar isso numa sequência de 30 duplica quadros e treme nos movimentos de câmera. Decida uma vez, pelo material.
- **Letra na tela:** quanta (tudo, só refrão, só palavras-chave), e onde nasce (no render, com transparência, ou montada no programa).
- **Quem faz os efeitos:** keyframes no programa de edição (ajustável à mão), queimados no render (igual para todo mundo, sem ajuste fino) ou os dois. Ver `etapa-efeitos.md` §5.
- **Extras:** legenda `.srt` da letra, versão vertical do refrão, quadros para a capa.

## 3. Direitos (diga uma vez, com clareza, e siga)
- **Cenas de anime, páginas de mangá, filme e jogo têm dono.** Usar trechos pode gerar reivindicação, bloqueio ou desmonetização, mesmo com edição pesada. Canais do gênero convivem com isso de formas diferentes (arte própria, trechos curtos, acordos). Não é o Claude quem decide o risco: explique e pergunte à pessoa de onde vem o material dela.
- **O instrumental** precisa de licença ou autoria. Anote no briefing de quem é.
- **Fontes, texturas e sobreposições:** só com licença que permita o uso; anote no arquivo de créditos.
- As referências medem o **jeito de editar**. A identidade (logo, fontes, marca, vinheta) de outro canal não se copia: a do vídeo é a da pessoa.

## 4. Referências deste tipo: o que medir
Além do que está no `referencias.md`:
- **Corte × batida:** ache os cortes (detector de cenas) e a grade de batidas da referência. Quantos cortes caem na batida, em qual tempo do compasso, e quantos cortes por compasso em cada seção (verso, pré-refrão, refrão).
- **Duração dos planos** por seção: mediana e os extremos.
- **Letra:** quantas palavras por tela, se entra por palavra, por linha ou por bloco; em quantos frames entra e sai; onde fica no quadro; como destaca a palavra-chave; o que muda no refrão.
- **Efeitos:** picos de brilho (flash), tremida (resíduo do movimento global quadro a quadro), punch de escala. Quantos por compasso e em que tempos.
- **Cor e acabamento:** paleta dominante por seção, contraste, grão, vinheta, barras.
- **Escalada:** como o refrão final difere do primeiro.

Com o segundo olhar ligado, o Gemini assiste a cada referência e descreve o que sente (`segundo-olhar.md` §9). O Claude mede. A ficha da referência junta os dois.

## 5. O teste curto (fase 6)
Em vez de um vídeo de 1–3 min, use **um verso e um refrão** (30–45 s) de uma música da pessoa, com material de verdade. No mangá animado, comece por **um quadro só**, do recorte ao render medido (parta de `exemplos/painel-animado/`), antes de catalogar um capítulo inteiro. É onde nascem a grade, o alinhamento, a primeira peça de letra e o primeiro conjunto de efeitos.
