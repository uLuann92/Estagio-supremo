# Exemplo: um quadro de mangá animado

Um quadro de teste (desenho próprio, simples de propósito) separado em 4 camadas e animado por código, no HyperFrames. É o ponto de partida das **peças-base** da etapa "animar painéis" (`guias/etapa-paineis.md`). Não é um estilo: o estilo vem das suas referências.

## O que tem
- `index.html`: a composição (4 s, 24 fps, 140 BPM). Um objeto de estado animado e uma função `aplicar()` que calcula tudo num lugar só: câmera com limite de borda, paralaxe, tremida com semente, linhas de velocidade, quadro de impacto, brilho.
- `assets/`: `quadro-original.png`; `fundo-limpo-do-modelo.jpg` (o quadro sem personagem, refeito pelo modelo de imagem do Gemini); `fundo.png` e as camadas, recortadas por `ferramentas/painel.py` a partir da diferença entre os dois. Nada foi retocado à mão.
- `quadros-do-render.jpg`: nove quadros do render, para ver o resultado sem rodar.

## Como rodar
```
npx hyperframes init meu-teste --example blank --non-interactive
```
Troque o `index.html` e copie a pasta `assets/` para dentro de `meu-teste/`. Depois:
```
npx hyperframes check
npx hyperframes snapshot --at 0.5,1.2,1.29,1.34,1.42,1.8,2.9,3.9
npx hyperframes render --fps 24
```

## Como adaptar a um quadro seu
1. `painel.py fatiar` na página; escolha o quadro.
2. Fundo limpo (`gemini.py imagem`), máscaras por diferença (`painel.py mascaras --limpo`) e `painel.py camadas --fundo-limpo` (ver o guia, §3).
3. No topo do script do `index.html`, troque: o tamanho do quadro (`LARG`, `ALT`), os pontos de interesse (`ROSTO`, `PUNHO`, `CENTRO`), a posição de cada camada (do `camadas.json`), as profundidades (`PROF`) e os tempos (`BATIDA`, `T_IMPACTO`, `T_ABRE`).
4. `check`, `snapshot`, olhar, render, medir a tremida.

## O que este teste ensinou
- A tremida da primeira versão existia no código e não se lia no vídeo: o chicote da câmera a engolia e o decaimento com ease-out forte deixava só dois quadros tremendo. Agora a parada do golpe (2 frames) vem antes, o sinal alterna a cada quadro e o decaimento é quase linear em 14 quadros.
- O Gemini não enxerga tremida (disse "não há" com ±33 px medidos). Enquadramento e entrada de elementos ele vê bem: foi ele quem apontou o balão cortado na borda.
- Com fundo remendado, camada que encolhe ou some mostra o remendo. Com o fundo limpo do modelo de imagem, o balão pôde nascer do nada.
- O punho é ligado ao braço: fica na camada do herói, e o que pula no impacto é uma cópia por cima.
- O zoom mínimo é o que cobre a tela: um quadro quase quadrado num vídeo deitado nunca aparece inteiro.
