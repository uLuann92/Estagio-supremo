# Etapa: efeitos no ritmo (a "câmera" do clipe musical)

Os movimentos e efeitos sobre as cenas, casados com a batida: punch, tremida, flash, rampas e transições. É o equivalente do `etapa-camera.md`, e vem **depois** da montagem e da letra travadas. As curvas são as do `oficio-motion.md`; os cuidados de escala e borda são os do `etapa-camera.md` §4.

Tudo aqui é tendência. Quanto efeito, que tipos e que força são do **perfil** (`estilo-efeitos.md`).

## 1. Princípios
1. **O efeito sublinha a música; não a substitui.** Cada efeito responde a um acento que existe no som. Efeito fora de acento parece defeito.
2. **Dose pela energia.** A curva do roteiro manda: verso com pouco, subida crescendo, refrão cheio, ponte quase nada.
3. **Um protagonista por momento.** Se a letra está fazendo o show, a cena fica quieta. Se a cena treme, a letra fica firme.
4. **Escalada.** O efeito mais forte do clipe aparece uma vez, no ápice. Usado no primeiro refrão, não sobra nada para o último.
5. **Variar.** O mesmo punch em toda batida vira metrônomo. Alterne o tipo, a força e o tempo do compasso, e deixe compassos sem nada.
6. **A base é automática; os destaques são desenhados.** Um script espalha a base por seção (dose do perfil); o Claude desenha à mão só os acentos marcados no roteiro.

## 2. O repertório
| Efeito | Como é | Casa com |
|---|---|---|
| **Punch de escala** | a cena salta ~3–8% no frame do acento e assenta em 4–6 frames (`power2.out`/`expo.out`) | bumbo, entrada de palavra-chave |
| **Tremida** | deslocamento que decai em 4–8 frames, amplitude pequena, direções alternadas (semente fixa, para o render sair igual) | caixa, impacto dentro da cena |
| **Flash** | 1–2 frames de claro (branco ou a cor do perfil), em opacidade parcial, caindo rápido | corte forte, entrada do refrão, ápice de golpe |
| **Aproximação lenta** | escala contínua dentro da cena (2–6%), linear | dá vida a cena parada; por baixo de tudo |
| **Rampa de velocidade** | acelera, corta no frame mais rápido, chega freando (`oficio-motion.md` §4) | transição entre seções |
| **Congelamento** | o quadro do ápice para por um ou dois tempos, com tratamento (escurece, contorno, cor) | frase de efeito, pausa da música |
| **Separação de cor / glitch** | canais deslocados, blocos, ruído, por 2–6 frames | transição, virada de bateria, tema tecnológico |
| **Eco / rastro** | quadros anteriores somados, decaindo | movimento rápido, clima de poder |
| **Barras** | faixas pretas que fecham ou abrem | muda o peso de uma seção (ponte, final) |
| **Luz e partículas** | sobreposição em modo de soma, na periferia | preenche a seção forte; nunca sobre a letra |

- **A câmera parte de onde está** e nunca mostra a borda: toda cena que recebe punch ou tremida já fica com folga de escala (ex.: 104–108% de base).
- **Efeito no frame do acento, não depois.** Punch e flash entram no frame exato (ou 1 antes). A tremida começa no frame do acento.

## 3. Transições entre seções
- A transição **termina no primeiro tempo** da seção nova. Ela ocupa o fim da anterior (o último tempo ou meio compasso).
- Repertório: corte seco no silêncio (o mais forte quando a música para), clarão, rampa de velocidade com direção casada, zoom que atravessa, glitch curto, mergulho no preto.
- **Uma transição marcante por virada de seção** e corte seco dentro dela. Transição enfeitada em todo corte tira o peso das viradas.

## 4. Cuidado com flashes (saúde e plataforma)
- Sequências de clarão rápido podem provocar crise em pessoas com epilepsia fotossensível. A referência usada em acessibilidade é **no máximo 3 flashes por segundo**, e menos ainda se forem de quadro inteiro, fortes ou vermelhos.
- Um script conta os flashes por segundo no plano e **recusa** o que passar. Estrobo, só com área e intensidade reduzidas, e por decisão clara da pessoa.
- Opacidade parcial e cor do perfil no lugar de branco puro costumam ficar melhores e mais seguros.

## 5. Onde o efeito é feito (decidido na entrevista)
| Caminho | O que vai | Bom | Ruim |
|---|---|---|---|
| **Keyframes no programa** | escala e posição (punch, tremida, aproximação), flash como clipe de cor numa trilha acima, com opacidade | a pessoa ajusta à mão | o XML só carrega transformações simples |
| **Queimado no render** | separação de cor, glitch, eco, desfoque, congelamento tratado | sai igual ao planejado | mudar é renderizar de novo |
| **Marcador para a pós** | o que a pessoa prefere fazer com os efeitos dela | usa os plugins dela | depende dela |

- O mais comum é misturar: transformações por keyframe; os efeitos de imagem **pré-renderizados por cena** (um arquivo novo, versionado, que substitui a cena na trilha), só nas cenas que precisam.
- **Sem programa** (o Claude entrega o vídeo): tudo é aplicado no render final. Escolha a ferramenta na hora (filtros do FFmpeg, ou a mesma ferramenta de animação com a cena como vídeo de fundo; pesquise o que ela suporta) e teste num trecho de 10 s antes de aplicar no clipe.
- Na primeira vez, o **teste curto** do `entrega-no-editor.md`: um punch, uma tremida e um flash, para a pessoa conferir como chegam no programa dela.

## 6. Plano e revisão
- O Claude escreve os destaques numerados (`fx01`, `fx02`…): o efeito, o compasso e o tempo, a força, a cena. A base por seção vai como regra ("verso: punch 4% no tempo 1, um compasso sim, um não").
- O script gera os keyframes ou os pré-renders, confere a regra dos flashes, a folga de borda e os conflitos (dois efeitos de escala no mesmo frame; efeito sob uma palavra gigante).
- **Revisão por número ou por seção:** "fx07 mais forte", "menos tremida no verso 2", "o refrão final precisa de mais".
- **Segundo olhar:** crítica de um trecho com fps alto (a 1 fps ele não vê flash nem tremida), perguntando onde o efeito cansa, onde falta e onde não bate com o som.
- **Eventos para o som:** transições, congelamentos e os destaques fortes viram eventos com tempo e força.
- Se a montagem ou a letra mudarem depois, os efeitos daquele trecho são recalculados.
