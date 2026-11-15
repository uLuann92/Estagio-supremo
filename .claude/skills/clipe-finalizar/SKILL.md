---
name: clipe-finalizar
description: "Monta o vídeo final do clipe com FFmpeg, aplica o acabamento e áudio final, confere o arquivo e gera os extras (legenda .srt e capas). Use em /clipe-finalizar, após a clipe-sfx."
---

# clipe-finalizar

Última etapa do fluxo: junta as cenas com efeitos, a letra animada, a música inteira e os efeitos sonoros com FFmpeg. Aplica o acabamento da imagem (look), confere a qualidade técnica e visual, e entrega o arquivo final pronto para publicar junto com a legenda `.srt` e quadros para a capa. Não refaz animações, cortes do roteiro ou tipografia: problemas dessas etapas voltam para elas.

- **Lê:** `_CLAUDE/projeto.json`, perfil em `edicao/perfis/<perfil>/`, música e letra alinhada (`_CLAUDE/musica/`), roteiro (`_CLAUDE/roteiro/`), cenas com efeitos (`_CLAUDE/efeitos/` ou `_CLAUDE/animar/`), letra renderizada (`_CLAUDE/letra/`), trilha de efeitos sonoros (`_CLAUDE/sfx/`)
- **Escreve:** bloco `finalizar` no estado, relatórios e arquivos de trabalho em `_CLAUDE/finalizar/`, entregas em `Renders/` (`<projeto>_conferencia_vNN.mp4`, `<projeto>_final_vNN.mp4`, `<projeto>.srt` e `Renders/capas/`)
- **Próximo passo:** fim do fluxo (aplicar aprendizados de `_CLAUDE/aprendizados.md` no perfil e voltar a `/clipe`)

Se a etapa `clipe-sfx` não estiver `concluido`, pare e sugira terminá-la.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-finalizar.md` e `.claude/skills/fluxo-de-edicao/guias/entrega-no-editor.md` (Caminho C e Clipe musical). Princípios essenciais (decisões criativas são tendência, não regra; regras técnicas são firmes):
- **Acabamento da imagem (look):** iguale brilho e contraste entre cenas que destoam antes de estilizar. Cor e curva de contraste entram por baixo da letra (que já tem as cores da identidade); grão e vinheta entram por cima de tudo para colar as camadas. Nunca duplique grão, nitidez ou lente que já vieram queimados das etapas anteriores.
- **Áudio final:** a música em A1 é a master, inteira do frame 0 ao fim, nunca cortada. Não comprima, não equalize e não normalize a música. Some apenas os efeitos sonoros com fades curtos (1 frame nas pontas) e meça o pico real (música masterizada não tem folga; impacto por cima pode estourar) e a loudness integrada para o alvo atual da plataforma (pesquisar na hora).
- **Exportação e versões:** gere primeiro um rascunho de conferência em resolução baixa e rápido. Só exporte o final em 1920×1080 a 24 fps após a aprovação. Numere as versões (`_v01`, `_v02`), nunca sobrescreva entregas e rode o FFmpeg em segundo plano.
- **Tempo em frames inteiros:** converta segundos para frames (`round(segundos * 24)`) numa função única antes de montar a linha do tempo.

## Perfil
Leia em `edicao/perfis/<perfil>/` (o nome do perfil está em `_CLAUDE/projeto.json`):
- `identidade.md` — define a curva de contraste, cor dominante por seção, doses de grão, vinheta e barras do look final.
- `audio.md` (ou seção de som do perfil, pesquisar na hora na pasta do perfil) — define a margem de segurança dos efeitos sobre a música e alvos de volume.

## Scripts
Na primeira vez que a etapa rodar num vídeo, escreva os scripts que faltam em `edicao/scripts/`, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas a evitar |
| :--- | :--- | :--- |
| `edicao/scripts/medir_cenas.py` | Mede brilho e saturação médios por cena e aponta as que destoam. | Não alterar arquivos originais; gerar apenas a tabela de correção em `_CLAUDE/finalizar/`. |
| `edicao/scripts/montar_final.py` | Monta o comando FFmpeg (cenas + look base + letra + grão/vinheta + música do frame 0 + sfx) e renderiza conferência ou final. | Arredondar tempos em frames inteiros a 24 fps; aplicar cor abaixo da letra e grão/vinheta acima; não filtrar a música master; nunca sobrescrever `_vNN`. |
| `edicao/scripts/conferir_final.py` | Confere o MP4 exportado: duração, sincronia no início e no fim, quadros pretos/congelados, flashes/s, loudness e pico real. | Recusar o arquivo se a duração divergir da música, se houver deriva de sincronia entre o começo e o fim ou se o pico real estourar. |
| `edicao/scripts/extras_final.py` | Gera a legenda `.srt` por linha a partir da letra alinhada aprovada e extrai 6–10 quadros fortes em 1920×1080 sem texto para a capa. | Garantir grafia idêntica à letra aprovada no `.srt`; extrair quadros das cenas antes da camada de letra. |

## Passo a passo
1. Confira o status e as pendências da etapa com `python edicao/scripts/estado.py <pasta do projeto> status`.
2. Rode `medir_cenas.py` sobre as cenas prontas, defina os ajustes de igualação e o look conforme o perfil.
3. **Primeira vez de todas:** gere um arquivo de teste curto (3–4 cenas com letra, música e sfx) com `montar_final.py`, peça para o usuário abrir e conferir (vídeo, áudio, sincronia), anote no arquivo de validação em `edicao/` e só então siga.
4. Renderize o vídeo de conferência (`Renders/<projeto>_conferencia_v01.mp4`, resolução baixa) em segundo plano.
5. Rode `conferir_final.py` no arquivo gerado. Se acusar erro técnico (duração, deriva de fps, pico estourado, quadros pretos não planejados, "ASSET FALTANDO"), corrija antes de seguir.
6. Faça a inspeção visual: extraia 8–12 quadros espalhados mais o primeiro e o último segundos; confira área segura da letra, cortes e coerência de cor.
7. Rode o **Segundo olhar** (abaixo) sobre o vídeo de conferência e trate os apontamentos válidos.
8. Gere os extras com `extras_final.py`: legenda `Renders/<projeto>.srt` e 6–10 quadros limpos em `Renders/capas/`.
9. Entregue o render de conferência ao usuário. Após a aprovação (e eventuais revisões), exporte o render final em resolução cheia (`Renders/<projeto>_final_v01.mp4`, 1920×1080, 24 fps) e rode `conferir_final.py` novamente nele.

## Segundo olhar
- **Quando:** após o render de conferência passar por `conferir_final.py` e pela sua inspeção de quadros, antes de mostrar ao usuário.
- **Uso:** crítica com o modelo capaz (`gemini-4-argon`) via `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py perguntar`.
- **O que mandar:** o vídeo de conferência inteiro (proxy em resolução baixa, 1 fps na chamada inicial) e a letra aprovada.
- **Pergunta-base:** "Assista a este clipe musical completo como espectador crítico. Aponte, com minutagem exata: 1) os 5 momentos mais fracos do vídeo; 2) onde a atenção cai; 3) qualquer erro visível de leitura da letra, corte, cor ou sincronia com a música." (Anexar o resumo de `identidade.md` do perfil).
- **O que conferir na resposta:** todo tempo citado pelo Gemini deve ser reconferido extraindo quadros em fps alto (24 fps) do trecho antes de virar correção. Salve o parecer em `_CLAUDE/segundo-olhar/`.
Seguir o protocolo da seção 6 das regras comuns.

## Resumo no chat
Curto: o que foi feito, os números medidos por `conferir_final.py` (duração, loudness integrada e pico real), o que precisa da atenção do usuário e os caminhos em `Renders/` (vídeo, `.srt` e `capas/`). Marque a etapa como `aguardando_aprovacao`.

## Revisão
O usuário assiste ao vídeo e pede ajustes pelo chat citando o tempo (ex.: "em 01:12 a letra sumiu rápido"). Converta o tempo para o compasso e cena do roteiro: se o problema for de etapa anterior (`clipe-animar`, `clipe-letra`, `clipe-efeitos`, `clipe-sfx`), avise o usuário que a correção pertence àquela etapa antes de mexer; ajustes leves de acabamento, cor ou nível de som resolva aqui. Agrupe os pedidos, gere nova versão (`_v02`...) sem sobrescrever e anote aprendizados em `_CLAUDE/aprendizados.md`.

## Aprovação
Com o render final em 1920×1080 aprovado e conferido, marque `concluido` no estado, informe os números finais medidos e diga quantos aprendizados ficaram anotados em `_CLAUDE/aprendizados.md`. Como esta é a última etapa do vídeo, lembre de consolidar os aprendizados no perfil (`edicao/perfis/<perfil>/`) e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Nunca sobrescrever um render em `Renders/`; sempre incrementar `_vNN`.
- Nunca comprimir, equalizar ou normalizar a faixa da música master.
- Falar com o usuário em português, de forma curta.
