# Exemplo: um quadro de mangá animado

Um quadro de teste (desenho próprio, simples de propósito) separado em 4 camadas e animado por código, no HyperFrames. É o ponto de partida das **peças-base** da etapa "animar painéis" (`guias/etapa-paineis.md`). Não é um estilo: o estilo vem das suas referências.

## O que tem
- `index.html`: a composição (4 s, 24 fps, 140 BPM). Um objeto de estado animado e uma função `aplicar()` que calcula tudo num lugar só: câmera com limite de borda, paralaxe, tremida com semente, linhas de velocidade, quadro de impacto, brilho.
- `assets/`: `fundo.png` (com o buraco fechado) e as camadas recortadas por `ferramentas/painel.py camadas`.
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
2. Máscaras do personagem e dos elementos (ver o guia, §3); `painel.py camadas`.
3. No topo do script do `index.html`, troque: o tamanho do quadro (`LARG`, `ALT`), os pontos de interesse (`ROSTO`, `PUNHO`, `CENTRO`), a posição de cada camada (do `camadas.json`), as profundidades (`PROF`) e os tempos (`BATIDA`, `T_IMPACTO`, `T_ABRE`).
4. `check`, `snapshot`, olhar, render, medir a tremida.

## O que este teste ensinou
- A tremida da primeira versão existia no código e não se lia no vídeo (o chicote da câmera a engolia). A medida quadro a quadro mostrou; a segunda versão separa a parada do golpe (2 frames) do chicote e da tremida.
- Camada que encolhe ou some mostra o remendo do fundo. No exemplo, balão e estrela só crescem e voltam.
- O zoom mínimo é o que cobre a tela: um quadro quase quadrado num vídeo deitado nunca aparece inteiro.
