# Kit AAA+ para o Claude Code (NOVAMENTE)

Um prompt pede. Este kit obriga.

O motivo de o jogo sair "cru" quase nunca é a IA não saber fazer. É que ela para cedo: troca o material, acha que ficou bom sem olhar, diz "pronto" e passa para a próxima coisa. O kit fecha essa porta dentro do Claude Code:

| Peça | Arquivo | O que faz |
|---|---|---|
| Gancho de prova | `.claude/hooks/exigir_prova.py` + `.claude/settings.json` | Depois de qualquer mudança visual na sessão, o Claude **não consegue encerrar a vez** sem uma rodada nova de fotos, a medição de fidelidade e um parecer APROVADO. Se o parecer reprovou, os defeitos voltam para ele e ele continua. |
| Juiz | `.claude/agents/revisor-visual.md` | Um subagente separado, duro, que compara as fotos com as referências do autor e com a rodada anterior e escreve o `PARECER.md`. Na dúvida, reprova. |
| Rodada | `.claude/skills/revisao-aaa/SKILL.md` | `/revisao-aaa`: fotografa as câmeras `Rev_*` na qualidade 4 e na 1, roda o `fidelidade.py`, chama o juiz, registra. |
| Regras fixas | `.claude/rules/aaa-plus.md` | Carregadas em toda sessão, mesmo depois de a conversa ser resumida. |
| Selo | `.claude/hooks/selo.json` | Guarda a impressão digital das referências e do `fidelidade.py`. Se alguém trocar a referência pela foto do jogo ou afrouxar a régua, o gancho bloqueia. |
| Travas | `permissions.deny` no `settings.json` | O Claude não edita `Referencias/`, `Scripts/fidelidade.py` nem `.claude/`. |
| Esforço | `effortLevel: xhigh` no `settings.json` | Raciocínio alto por padrão; o juiz e a rodada usam o máximo. |

## Instalar (uma vez, no PC)

1. **Claude Code no PC**, aberto na pasta do projeto Unreal (a do `.uproject`): app desktop do Claude (aba Code) ou `claude` no terminal.
2. **Copie o kit para o projeto:**
   ```
   python caminho\do\repo\novamente-ue5\claude-kit\instalar.py "C:\Projetos\SeuJogo"
   ```
   Se o projeto já tem `.claude/settings.json`, o instalador junta, não apaga.
3. **Referências com os nomes fixos** em `C:\Projetos\SeuJogo\Referencias\`:
   ```
   python Scripts\preparar_referencias.py prancha_4_vistas.jpg Referencias
   ```
   Isso corta a prancha do render em `luan_crianca_frente.jpg`, `_costas`, `_perfil` e `_34`. Coloque à mão o close do render como `luan_crianca_close.jpg` e as capas como `capa_v1.jpg`, `capa_v2.jpg`, `capa_v3.jpg`.
4. **Bibliotecas da medição:** `pip install mediapipe opencv-python numpy` (o modelo de rosto baixa sozinho na primeira vez).
5. **Sele as referências** (só você faz isso, de novo sempre que trocar uma referência de propósito):
   ```
   python .claude\hooks\exigir_prova.py --selar
   ```
6. **Câmeras de revisão no mapa.** Um CameraActor por linha do `Referencias/pares.json`, com a tag igual ao nome. A câmera tem que repetir a referência (mesma lente, altura, ângulo e distância). É isso que deixa a comparação ser por número.

   | Tag | Repete |
   |---|---|
   | `Rev_05_Rosto_Frente` | render, vista de frente |
   | `Rev_05_Rosto_Perfil` | render, perfil |
   | `Rev_05_Rosto_34` | render, três quartos |
   | `Rev_05_Rosto_Close` | o close do render |
   | `Rev_06_Cobogo_Costas` | render, costas (a sala do cobogó) |
   | `Rev_07_Clima_Capa` | a capa: noite azul, luz quente, contraste alto |

   Acrescente câmeras de cenário (`Rev_01_Rua`, `Rev_02_Muro`...) no `pares.json` com `"rosto": false`, apontando para a referência de clima certa.
7. **Confira:** no Claude Code, `/hooks` mostra o gancho `Stop`; `/agents` mostra o `revisor-visual`; `/context` mostra `aaa-plus.md`. No terminal, `python .claude\hooks\exigir_prova.py --checar` diz o que falta.

Se o Windows não achar `python` quando o gancho roda, troque `python` por `py -3` no `.claude/settings.json` (você edita; o Claude não pode).

## Usar

1. No Claude Code, `/model` e escolha o modelo mais forte da lista. Para sessões pesadas, `/effort max`.
2. Mande como primeira mensagem o `Docs/PROMPT_AAA_PLUS.md` inteiro, com as imagens de referência anexadas.
3. Deixe trabalhar. Ele vai fotografar, medir, ser julgado e corrigir em volta, sozinho, até aprovar ou até precisar de você.

Quando ele parar, a última mensagem tem uma destas formas:
- a rodada com **VEREDITO: APROVADO**, as notas e os caminhos das fotos;
- **PENDENTE:** o que falta e de quem depende (um download, uma decisão sua, uma diária de captura);
- **SEM EFEITO VISUAL:** a mudança não altera a imagem, e o motivo. Se não concordar, diga.

Se ele girar 8 vezes seguidas sem conseguir provar, o gancho libera e avisa as pendências (`NOV_MAX_BLOQUEIOS` muda o limite).

## Limites (honestos)

- O gancho pega pressa e esquecimento, que é o que deixa tudo cru. Ele não impede uma IA decidida a burlar pelo terminal. As regras dizem que as referências e o juiz são seus; o selo avisa se algo mudou.
- O juiz é outra instância do mesmo tipo de modelo: é mais duro que o autor do trabalho, mas não é neutro. Por isso a medição do `fidelidade.py` vence o parecer, e **a aprovação final do rosto é sua**.
- O `fidelidade.py` mede proporção do rosto, tom de pele e clima da imagem. Não mede se o cabelo está em fios ou se a roupa tem trama: isso é o juiz e você.
- Rosto 100% fiel sai de escultura ou de FaceBuilder a partir das quatro vistas, passado para MetaHuman. Nenhuma IA acerta isso "no olho" no Creator.
