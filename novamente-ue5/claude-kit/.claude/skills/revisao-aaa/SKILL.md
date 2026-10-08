---
name: revisao-aaa
description: Rodada de revisão visual do NOVAMENTE com prova. Fotografa as câmeras Rev_* na qualidade 4 e numa menor, mede a fidelidade contra as referências do autor e chama o revisor-visual para o PARECER.md. Use depois de qualquer mudança visual e antes de dizer que uma etapa terminou.
when_to_use: Depois de mexer em asset, mapa, material, shader, personagem, luz, pós, animação ou config de renderização. Quando o gancho exigir_prova bloquear o fim da vez. Quando o autor pedir "revisão", "fotos" ou "prova".
argument-hint: "[mapa] [qualidades]"
effort: max
---

# Revisão AAA com prova

Argumentos opcionais: $ARGUMENTS (mapa, por exemplo `/Game/Novamente/Maps/L_Mutirao`, e qualidades, por exemplo `4,1`).

## 1. Fotografar

Salve tudo no editor antes. Depois, com o editor fechado ou por linha de comando (ajuste os caminhos do CLAUDE.md):

```
:: mapa (sem esta linha, o Largo)
set NOV_MAP=/Game/Novamente/Maps/L_Mutirao
:: 4 é a verdade visual; 1 prova que o estilo aguenta PC fraco
set NOV_TIERS=4,1
set NOV_CAPTURE=editor
set NOV_QUIT=1
"%UE%\Engine\Binaries\Win64\UnrealEditor.exe" "%PROJ%" -ExecutePythonScript="%CD%\Scripts\capture_review.py"
```

No Git Bash, use `NOV_MAP=... NOV_TIERS=4,1 NOV_CAPTURE=editor NOV_QUIT=1 "$UE/Engine/Binaries/Win64/UnrealEditor.exe" "$PROJ" -ExecutePythonScript="$PWD/Scripts/capture_review.py"`.

Confira que a pasta nova em `Saved/Review/<data-hora>/` tem `REVISAO.md` e uma foto `<Rev_...>_q4.png` e `<Rev_...>_q1.png` para cada câmera. Se o mapa não tem câmeras `Rev_*`, crie antes (CameraActor com a tag `Rev_01_...`, com a mesma lente, altura e enquadramento da referência correspondente).

## 2. Medir

```
python Scripts/fidelidade.py --pares Referencias/pares.json --dir "Saved/Review/<data-hora>"
```

Leia a tabela inteira. O `fidelidade.json` fica na pasta da rodada. Não mexa nas tolerâncias nem nas referências: são do autor e estão seladas.

Se a rodada mexeu em gente (personagem, NPC, rosto, cabelo, roupa), rode também a auditoria e deixe o resultado na pasta:

```
python Scripts/auditar_humanos.py --json "Saved/Review/<data-hora>/auditoria_humanos.json"
```

Ela tem que dar LIMPO. Pessoa feita por código ou com forma básica sai do projeto; não vira exceção.

## 3. Julgar

Chame o subagente **revisor-visual** com o caminho da rodada. Não escreva o PARECER.md você mesmo e não discuta com o veredito: corrija.

## 4. Relatar e continuar

- Mostre ao autor: o veredito, as três piores notas, os números da medição e as fotos lado a lado com a referência (caminhos).
- Registre em `Docs/REVISOES.md`: data, portão, câmeras, notas, o que mudou desde a anterior.
- **REPROVADO:** pegue o primeiro item de "O que corrigir", corrija na causa (material, malha, luz, rig, câmera), e volte ao passo 1. Uma causa por vez, com número antes e depois.
- **APROVADO:** siga para a próxima etapa do plano. As 5 correções do parecer entram na lista da próxima rodada.

Para ver o que o gancho vai cobrar antes de encerrar: `python .claude/hooks/exigir_prova.py --checar`.
