# Instruções para o Claude neste projeto

Você está no PC do autor (Rawriter), com o projeto Unreal Engine 5.8 de NOVAMENTE. Seu trabalho é levar o vertical slice "Luta no Largo" até o nível de estúdio grande, em rodadas de revisão com prova visual. Responda em português.

## A obra (não negociável)

- NOVAMENTE é seinen sombrio, realismo sujo. Manaus, Zona Norte (Mutirão, Novo Aleixo), 2017. A luta do slice é no Largo de São Sebastião, em frente ao Teatro Amazonas, à noite, na chuva.
- Ghost of Tsushima é **só** referência de estilo: luz, vento, partículas, textura, sombra, peso e fluidez da animação. **Nunca** coloque nada japonês (templo, torii, cerejeira, katana, samurai, kimono, pagode) nem "sol baixo o dia todo".
- Luan adulto: pele parda clara, quase branca; 1,63 m; magro; cansado. A camisa branca é pijama e pode virar a farda (camiseta branca com gola canelada amarela e azul).
- A Sombra pode ter qualquer cor; a que deixa o ambiente mais perturbador. Olhos amarelos, garras, fala em legenda itálica.
- Leis: 1ª (a dor chega atrasada, som abafado), 2ª (o corpo falha antes da Sombra: coração, zumbido, túnel), Lei de Goggins (os ferimentos ficam de uma luta para a outra), Realidade 2 (preto e branco), Visão do Caos (esquiva perfeita, câmera lenta).
- Referências visuais do autor ficam em `Referencias/` (capa v1 a v3, render 3D do Luan criança, fotos do Largo). Se a pasta não existir, peça ao autor para criar e colocar as imagens.

## Regras de arquitetura (não negociáveis)

Qualquer exceção precisa de ADR com o motivo e da aprovação do autor.

- **Zero assets orientais.** Nada de pacotes "oriental", "japanese", "asian village", "samurai", "shrine", "torii" ou "bamboo", nem como provisório.
- **Mixamo descartado.**
  - Animação de luta vem de captura de movimento (Rokoko, Move.ai ou estúdio), refinada no Control Rig e aplicada em MetaHumans.
  - Para testar lógica antes disso, use as animações do Game Animation Sample.
- **Base de movimento: Game Animation Sample (Motion Matching).** O Lyra não entra: é rede e tiro multiplayer, só polui.
- **Combate mão e pé, estilo UFC, no plugin NovamenteCombat.** Sem espada e sem troca de armas.
- **GAS só por ADR.** Os golpes, janelas e acertos ficam no C++ próprio. O GAS entra quando o mundo aberto pedir atributos e efeitos paralelos (fôlego, buffs da Sombra, ferimentos, itens), e só para eles.
- **Mundo aberto em World Partition:** células, HLOD, Data Layers para dia, noite e chuva, Level Instances para os quarteirões, PCG para detalhe.
- **Calibração de exposição e materiais antes de qualquer efeito.** Nanite e Lumen não salvam material de plástico.

## Fidelidade e prova

- O prompt principal é `Docs/PROMPT_AAA_PLUS.md`. As regras fixas dele ficam em `.claude/rules/aaa-plus.md` (instalado pelo `claude-kit/`).
- O Luan tem que ser o da referência. `Scripts/fidelidade.py` mede o rosto (proporções), a pele (Delta E) e o clima da imagem contra `Referencias/`; número vence opinião.
- Depois de mudança visual, rode `/revisao-aaa`: fotos das câmeras `Rev_*` nas qualidades 4 e 1, medição, subagente revisor-visual, `PARECER.md`.
- O gancho `exigir_prova` não deixa a vez terminar sem rodada nova aprovada. Saídas honestas: "PENDENTE:" ou "SEM EFEITO VISUAL:".
- Referências, `pares.json` e `fidelidade.py` são do autor e estão selados. Não edite.

## Onde está cada coisa

- Plugin C++: `Plugins/NovamenteCombat` (dentro do projeto). Cópia de trabalho no repositório: `novamente-ue5/`.
- Scripts do editor: `novamente-ue5/Scripts/` (setup, montar o Largo, fotos de revisão).
- Shaders dos nós Custom: `novamente-ue5/Shaders/` (o setup cola o código nos materiais; edite o `.hlsl` e rode o setup de novo).
- Portões de revisão e orçamento de desempenho: `novamente-ue5/Docs/ROADMAP.md`.
- Registro das rodadas: `novamente-ue5/Docs/REVISOES.md` (crie se não existir).

## Comandos (ajuste os caminhos uma vez e anote aqui)

```
set UE=C:\Program Files\Epic Games\UE_5.8
set PROJ=C:\Projetos\Novamente\Novamente.uproject
set REPO=C:\caminho\novamente-ue5

:: compilar (editor fechado)
"%UE%\Engine\Build\BatchFiles\Build.bat" NovamenteEditor Win64 Development -Project="%PROJ%" -WaitMutex

:: preparar materiais e config / montar o Largo (sem janela)
"%UE%\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJ%" -run=pythonscript -script="%REPO%\Scripts\setup_novamente.py"
"%UE%\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%PROJ%" -run=pythonscript -script="%REPO%\Scripts\build_largo.py"

:: fotos de revisão (precisa de janela: renderiza de verdade) e fecha no fim
set NOV_QUIT=1
"%UE%\Engine\Binaries\Win64\UnrealEditor.exe" "%PROJ%" -ExecutePythonScript="%REPO%\Scripts\capture_review.py"
```

O nome do alvo é o nome do `.uproject` + `Editor`. Veja em `Source/*.Target.cs` se houver.

## O ciclo de cada rodada

1. **Compilar.** Leia o log inteiro. Corrija um erro de cada vez, começando pelo primeiro. Não desligue avisos nem comente código para passar.
2. **Montar.** Rode o setup e o `build_largo.py` se mexeu em material, shader ou cenário.
3. **Fotografar.** Rode `capture_review.py`. Ele cria `Saved/Review/<data-hora>/` com as fotos e um `REVISAO.md` com a lista do que conferir.
4. **Comparar.** Abra cada foto (você lê imagens) ao lado das referências em `Referencias/` e da rodada anterior. Responda cada item da lista com OK ou com o problema concreto (arquivo, o que está errado, o que mudar).
5. **Registrar.** Acrescente em `Docs/REVISOES.md`: data, portão (R0 a R8), fotos usadas, problemas, correções feitas, o que ficou para o autor decidir.
6. **Corrigir e repetir.** Volte ao passo 1. Um portão só fecha com a prova pedida no `ROADMAP.md`.

Pare e pergunte ao autor quando a decisão for de gosto ou de canon (rosto do Luan, cor da farda, falas novas). Mostre as opções em fotos lado a lado.

## Regras do código

- C++ no estilo da Unreal (prefixos U/A/F/E, `TObjectPtr`, `UPROPERTY` em tudo que é UObject). Comentários e textos de interface em português.
- Textos que aparecem na tela sempre com `LOCTEXT`/`NSLOCTEXT`. Arquivos com acento em UTF-8 com BOM.
- Os números de combate vêm do protótipo. Se mudar um, diga qual, de quanto e por quê em `Docs/REVISOES.md`.
- Tempo real (`FApp::GetDeltaTime`) para câmera, tela e som; tempo do mundo para a luta (a câmera lenta afeta a luta, não o operador de câmera).
- Nada de `Tick` pesado em Blueprint. Meça com Unreal Insights antes de otimizar.
- Não crie pull request nem envie nada para fora sem o autor pedir.
