# NOVAMENTE AAA+ (regras que valem em toda sessão)

O prompt completo está em `Docs/PROMPT_AAA_PLUS.md`. Estas são as regras que não podem sair da cabeça.

## Referências mandam

- As imagens em `Referencias/` são a verdade: o render 3D do Luan criança (quatro vistas e o close) e a capa v1 a v3. O jogo tem que parecer com elas, não com "um jogo bonito qualquer".
- O protagonista é o Luan da referência, 100%. Rosto genérico de MetaHuman, preset ou "parecido" é reprovado. O `Scripts/fidelidade.py` mede; número vence opinião.
- As referências, o `pares.json` e o `fidelidade.py` são do autor e estão selados. Nunca edite, troque, recorte por cima nem afrouxe tolerância.

## Templates prontos antes de inventar

- Anatomia: MetaHuman (Creator, Mesh to MetaHuman, esqueleto e LODs dele). Física: Physics Asset do MetaHuman, Chaos Cloth, Kawaii Physics, Physical Animation. Movimento: Game Animation Sample (Motion Matching), Motion Warping, Control Rig. Mundo: World Partition, PCG, Megascans/Fab.
- Proibido: Mixamo, Lyra como base, pacote oriental, primitiva ou manequim em qualquer foto.

## Estilo em qualquer PC

- A imagem de referência é feita na qualidade 4 (cinematográfica). As qualidades 0 a 3 cortam custo, não estilo: mesma paleta, contraste, direção de luz e silhueta.
- Nunca degrade o asset de origem para rodar; use escalabilidade, LOD, Nanite e TSR.

## Anti-cru

- Nada é liso, limpo, novo, vazio ou parado. Toda superfície tem variação, uso e umidade; todo personagem respira, pisca e mexe o olho; toda cena tem vento e partícula no ar.
- Pós-processamento não esconde falta de material, de luz ou de detalhe.

## Prova

- Depois de qualquer mudança visual: `/revisao-aaa` (fotos q4 e q1, `fidelidade.py`, subagente revisor-visual, PARECER.md).
- O gancho `exigir_prova` não deixa a vez terminar sem rodada nova aprovada. Saídas honestas: "PENDENTE:" (o que falta e de quem depende) ou "SEM EFEITO VISUAL:" (e por quê).
- Nunca diga "pronto", "terminado" ou "nível AAA" sem o PARECER.md aprovado da rodada.
- Pare e pergunte ao autor em decisão de gosto ou de canon, com opções em fotos lado a lado.
