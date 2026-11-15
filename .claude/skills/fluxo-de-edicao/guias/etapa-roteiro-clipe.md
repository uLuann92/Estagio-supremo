# Etapa: roteiro do clipe (o plano, compasso a compasso)

O equivalente do `etapa-motion-mapa.md` para o clipe musical, e a etapa que mais decide a qualidade. Planeja **o clipe inteiro**: que cena em cada compasso, como a letra aparece, onde entram os efeitos e quanta energia cada seção tem. **Não monta nem anima nada**: propõe, ajusta com a pessoa e grava. Aqui mudar é barato.

Leia antes: o mapa da música, o índice de cenas, o briefing e o perfil (letra, efeitos, ritmo de corte, identidade).

## 1. Primeiro a curva, depois os detalhes
- **A curva de energia do clipe** segue a da música, seção por seção: quanto corte, quanta letra, quanto efeito. Escreva-a numa tabela curta antes de escolher qualquer cena.
- **Escalada:** o clipe guarda o melhor para o fim. O primeiro refrão não pode gastar tudo: o último tem de ser maior (cenas-herói, o efeito mais forte, a letra maior). O maior momento do clipe é um só.
- **Respiro:** depois de um trecho forte, um compasso mais calmo. Sem contraste, o forte deixa de parecer forte.
- **A história:** mesmo num clipe de cenas soltas, existe um arco (quem é o personagem → o conflito → o ápice → o que fica). Diga em uma frase por seção o que o espectador deve sentir.

## 2. Ritmo de corte por seção (tendência; os números são do perfil)
| Momento | Corte | Imagem |
|---|---|---|
| Intro | lento: 2–4 compassos por cena | apresenta o personagem e o clima |
| Verso | 1–2 compassos; meio compasso nas rimas fortes | acompanha o que a letra conta |
| Pré-refrão / subida | acelera: 1 compasso → meio → um tempo | tensão; a rajada termina no acento |
| Entrada do refrão | o acento mais forte da seção | a cena-herói, com o ápice na batida |
| Refrão | por tempo ou a cada dois tempos, com pausas | ação, as imagens-marca |
| Pausa da música | corte seco, congelamento ou preto | o silêncio também é batida |
| Ponte | lento outra vez | o momento mais emotivo |
| Final | o refrão maior; depois, uma cena que segura | fecha o arco |

- **Rajada** (cenas de 2–4 frames): só em subida, com fim marcado no acento, e poucas vezes no clipe.
- O refrão que volta pode repetir a **estrutura** (mesmos pontos de corte) com cenas novas: dá identidade sem repetir imagem.

## 3. Casar cena e letra
- **Literal nas palavras-chave:** quando a letra cita um golpe, um nome, um lugar, a imagem mostra aquilo, com o ápice na palavra.
- **Clima no resto:** entre as palavras-chave, a cena acompanha o sentimento do verso. Ilustrar toda linha ao pé da letra vira legenda de imagem.
- **Quem canta:** com mais de uma voz ou personagem, a imagem acompanha de quem é o verso.
- Cena que a pessoa pediu no briefing tem prioridade.

## 4. A letra no plano
Por seção (e por linha, no refrão e nas frases de efeito):
- **Quanto aparece:** tudo, só o refrão, só palavras-chave. É do perfil.
- **O tratamento:** qual das formas do `etapa-letra.md` (linha em bloco com destaque, palavra a palavra, palavra gigante). O refrão tem um tratamento **fixo e reconhecível**; os versos variam.
- **Onde fica:** longe do rosto e da área de interesse da cena escolhida (o índice traz).
- **As frases de efeito** do clipe (3 a 6 no total) ganham um momento próprio: a letra é a protagonista, a cena recua.

## 5. Os efeitos no plano (intenção em palavras)
A etapa de efeitos decide curva e valor. Aqui fica **o quê e onde**:
- por seção: o repertório e a dose ("verso: punch leve no primeiro tempo; refrão: tremida na caixa e flash na entrada");
- por acento marcado: o efeito e a força ("compasso 33, tempo 1: congelamento + flash forte");
- as **transições** entre seções (rampa, clarão, corte seco no silêncio).
Um protagonista por momento: quando a letra é a estrela, o efeito na cena é mínimo, e vice-versa.

## 6. O que falta (assets)
Liste o que o roteiro pede e não existe: uma cena específica que não está no índice, a fonte, o logo do canal, texturas e partículas. Cena que falta vira pedido à pessoa ("preciso de um close do personagem X bravo; tem em que episódio?"), nunca uma troca silenciosa por algo genérico.

## 7. Duplo pensamento (o melhor lugar para ele)
Com o segundo olhar ligado, siga o `segundo-olhar.md` §3:
1. O Claude grava a curva de energia e o roteiro do primeiro refrão.
2. O Gemini recebe o mapa da música, a letra, o índice de cenas e o trecho do perfil, **sem** o roteiro, e propõe o dele para o mesmo refrão. Com o áudio junto, ele também diz onde sente os acentos.
3. O Claude compara, confere e mostra à pessoa o resumo dos dois pensamentos.
Aprovado o refrão, o resto do clipe pode ir só com crítica (mais barato que um parecer inteiro).

## 8. Revisão
- Mostre primeiro a **curva** (a tabela por seção) e espere o "sim". Depois, o roteiro por seção, começando pelo primeiro refrão: uma linha por compasso (ou por corte), com o tempo, a cena (id + descrição curta), a letra e o efeito.
- Junto, uma folha de contato das cenas escolhidas, em ordem: a pessoa vê o clipe em miniatura.
- Ela aprova, troca ou risca por compasso. Ao gravar de novo, preserve o que já foi aprovado.
- No estado: por compasso, a cena, o ponto de ápice, o tratamento da letra e os efeitos pedidos, com ids estáveis (`rt017` para o compasso 17).
