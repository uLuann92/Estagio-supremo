---
name: fluxo-de-edicao
description: "Guia a pessoa a montar o próprio fluxo de edição de vídeo com o Claude Code (YouTube, reels, vídeo narrado, clipe musical com letra na tela no estilo rap geek/AMV, ou outro formato): entrevista sobre o tipo de vídeo, o programa de revisão (ou nenhum), a transcrição ou a música, motion, câmera, efeitos, som e finalização; analisa as referências dela para criar o estilo; liga o Google Gemini como segundo olhar (duplo pensamento), se ela quiser; e escreve as skills de cada etapa, a skill mestra, as regras comuns e o caderno de aprendizados, a partir de um fluxo de 8 etapas já testado em vídeos reais e de um fluxo próprio para clipe musical. Use em /fluxo-de-edicao, ou quando a pessoa pedir para montar, adaptar ou continuar o fluxo de edição dela, fazer clipes de música/rap geek, ou usar o Gemini junto com o Claude na edição."
---

# fluxo-de-edicao

Você vai ajudar a pessoa a construir o **fluxo de edição dela**: um conjunto de skills que editam vídeo com o Claude Code, etapa por etapa, no estilo dela.

Você não edita vídeo nesta skill. Você conversa, decide junto e escreve as skills. Há dois pontos de partida:
- **vídeo falado:** um fluxo de 8 etapas já usado em vídeos reais (YouTube, apresentador falando para a câmera, revisão no Premiere);
- **clipe musical com letra na tela** (rap geek, AMV, lyric video): um fluxo em que a música manda e tudo se alinha pela batida e pela letra cantada (`guias/clipe-musical.md`). Este fluxo é mais novo que o primeiro e passou por menos vídeos: diga isso à pessoa, e dê mais peso ao teste da fase 6.

Os dois são **sugestão, não molde**: tudo se adapta ao que a pessoa quer. Ela pode seguir o roteiro, perguntar à vontade ou mudar tudo.

Em qualquer um, o Google Gemini pode entrar como **segundo olhar**: ele assiste ao vídeo com som (o Claude só vê quadros e números) e dá um pensamento independente para comparar com o seu (`guias/segundo-olhar.md`). É opcional.

## Como falar
- Português, frases curtas, sem jargão sem explicar. Muita gente aqui nunca editou com código.
- Uma pergunta (ou um bloco pequeno de perguntas ligadas) por vez. Sempre com a sua sugestão já dita: "Eu sugiro X, porque Y. Prefere outra coisa?"
- Explique o porquê das escolhas em uma frase. A pessoa precisa entender para decidir.
- Antes de instalar, apagar ou gravar algo fora da pasta da montagem, diga o que vai fazer e espere o "sim".

## Arquivos desta skill (leia só o que a fase pedir)
| Arquivo | Quando |
|---|---|
| `guias/principios-do-fluxo.md` | Fase 0, sempre: os bons costumes que valem para qualquer fluxo |
| `guias/decisoes.md` | Fase 2: cada decisão, com as opções e os critérios para escolher |
| `guias/referencias.md` | Fase 3: como analisar referências e criar o perfil |
| `guias/segundo-olhar.md` | Fases 1 e 2 (preparar e decidir), e sempre que for perguntar algo ao Gemini |
| `guias/clipe-musical.md` | Fase 2, se o tipo de vídeo for clipe musical: o que muda no fluxo, as decisões a mais, direitos, o que medir nas referências |
| `guias/etapa-musica.md`, `etapa-cenas.md`, `etapa-roteiro-clipe.md`, `etapa-letra.md`, `etapa-efeitos.md` | Fase 5, nas etapas do clipe musical |
| `guias/etapa-finalizar.md` | Fase 5, se o fluxo tiver a etapa de finalizar (edição completa) |
| `guias/etapa-*.md` | Fase 5: o ofício de cada etapa, lido quando for escrever aquela skill |
| `guias/oficio-motion.md`, `guias/hyperframes.md` | Fase 5, nas etapas de motion |
| `guias/entrega-no-editor.md` | Fase 5, em toda etapa que entrega para o programa de edição (ou renderiza o vídeo) |
| `modelos/*.md` | Fase 5: os esqueletos das skills que você vai escrever |
| `ferramentas/gemini.py` | O script do segundo olhar, pronto. Copie para a pasta de ferramentas da pessoa (`guias/segundo-olhar.md` §8) |

Os guias trazem **critérios e armadilhas**, não detalhes que envelhecem. Preço, versão, comando de instalação e recursos de cada ferramenta: pesquise na hora.

## Progresso (a montagem pode levar várias conversas)
Tudo o que for decidido fica em `<pasta de ferramentas>/montagem.md` (a pasta é escolhida na fase 2; modelo em `modelos/montagem.md`). Grave ao fim de cada fase: as decisões, o que já foi escrito e o que falta. Ao abrir esta skill:
1. Procure um `montagem.md` (pergunte onde, se não achar). Se existir, mostre em 3–5 linhas onde a montagem parou e siga de lá.
2. Se não existir, comece pela fase 0.

## Fase 0. Apresentar
Leia `guias/principios-do-fluxo.md`. Em poucas linhas, diga à pessoa:
- **que esta skill não edita vídeo: ela monta o fluxo.** No fim, a pessoa terá as próprias skills, entre elas uma skill mestra com o nome que ela escolher (ex.: `/editar`). **É essa skill mestra que ela vai usar para editar cada vídeo.** `/fluxo-de-edicao` volta a ser usada só para continuar a montagem ou mudar o fluxo;
- o que vai acontecer (entrevista → referências → plano do fluxo → escrever as skills → teste num clipe curto);
- que dá para parar e continuar depois (`/fluxo-de-edicao` de novo);
- que o resultado é dela: skills em texto que ela pode ler e mudar.

## Fase 1. Ambiente
Confira, sem instalar nada ainda: sistema operacional, Python, FFmpeg, Node.js (o HyperFrames roda por `npx`), Git e a placa de vídeo (uma GPU NVIDIA acelera muito a transcrição local e a separação de voz e instrumental; sem ela, funciona mais devagar, ou com transcrição na nuvem).
Confira também se existe a variável de ambiente `GEMINI_API_KEY` (só se existe; **nunca mostre o valor**). Se não existir, não é problema: o segundo olhar é decidido na fase 2.
Mostre o que existe e o que falta. Instale só depois das decisões da fase 2 (só o que o fluxo dela vai usar), explicando cada instalação.

## Fase 2. Entrevista
Leia `guias/decisoes.md` e siga a ordem de lá. A primeira decisão é sempre **onde a pessoa revisa o vídeo** (num programa de edição ou só assistindo ao vídeo pronto), porque ela muda o fluxo inteiro. Para cada decisão: explique as opções em 2–3 linhas, dê a sua sugestão para o caso dela e registre a escolha no `montagem.md`.

- **Clipe musical:** se o tipo de vídeo (decisão 2) for clipe com música e letra na tela, leia `guias/clipe-musical.md` e faça as decisões de lá no lugar das de transcrição, notas faladas e cortes.
- **Segundo olhar:** na decisão sobre o Gemini, leia `guias/segundo-olhar.md`. Se a pessoa quiser, ajude-a a criar a chave (ela mesma guarda; nunca no chat), copie o script, rode `testar`, escolha os modelos pela lista e pergunte o que pode ser enviado. Anote tudo no `montagem.md`.

## Fase 3. Referências e perfil
Leia `guias/referencias.md`. Guie a pessoa a juntar trechos de vídeos de que ela gosta, analise e escreva o **perfil** dela (identidade visual, estilo de motion, de câmera, de corte e de som). Sem referências, o resultado tende ao genérico: insista com gentileza, mas não trave a montagem (dá para começar com um perfil simples e completar depois).

- **Quando a pessoa citar um canal como estilo** ("quero no estilo do canal X"): o estilo não vem da sua memória, vem de **trechos reais** daquele canal, medidos. Peça 5 a 10 trechos (um refrão, um verso, uma transição de que ela gosta) e diga por quê. O que sai é o jeito de editar; a identidade (logo, fontes, vinheta) é a dela.
- **Com o segundo olhar ligado:** o Gemini assiste a cada referência e descreve o que se vê e se ouve; você mede com os scripts; a ficha junta os dois (`guias/referencias.md` §6).

## Fase 4. Plano do fluxo
Proponha as etapas, partindo do fluxo de referência do tipo de vídeo dela e adaptando às respostas.

**Vídeo falado (as 8 de referência):**

1. **iniciar:** abre o projeto e organiza o briefing.
2. **preparar:** inventário da mídia, sincronia, transcrição com tempo por palavra, notas de edição faladas.
3. **cortes:** escolhe takes, tira erros e pausas, entrega o primeiro corte.
4. **motion-mapa:** planeja as animações (onde, o quê, como) e a câmera em volta delas. Sem animar nada.
5. **assets:** busca logos, ícones e prints que as animações precisam.
6. **motion-render:** constrói e renderiza cada animação.
7. **câmera:** zooms e movimentos de câmera casados com a fala e as animações.
8. **sfx:** efeitos sonoros em camadas, alinhados ao que se vê.

**Clipe musical com letra** (detalhes em `guias/clipe-musical.md`):

1. **iniciar:** abre o projeto e organiza o briefing (música, tema, letra, material).
2. **música:** grade de batidas, estrutura, acentos e letra alinhada por palavra, com os testes do clique e do karaokê.
3. **cenas:** cataloga o material bruto, cena por cena.
4. **roteiro:** o plano do clipe, compasso a compasso (cena, letra, efeito, energia). Sem montar nada.
5. **montagem:** as cenas escolhidas, cortadas e encaixadas na batida.
6. **letra:** a tipografia animada, sincronizada por palavra.
7. **efeitos:** punch, tremida, flash, rampas e transições no ritmo.
8. **sfx:** poucos sons, apoiando a música.
9. **finalizar:** acabamento, áudio, exportação, conferência e extras.

**Em qualquer fluxo:**
- a etapa **finalizar** (`guias/etapa-finalizar.md`) é o que faz a edição ser completa. Sugira sempre para quem não usa programa de edição, e ofereça a quem usa (ao menos a conferência);
- a **skill mestra** (mostra onde o vídeo está e chama a etapa certa) e as **regras comuns** (o que vale para todas);
- se o segundo olhar foi ligado, diga em quais etapas ele entra (sugestão no `guias/segundo-olhar.md` §4) e confirme.

Exemplos de adaptação: reels pode juntar etapas e pular assets; vídeo sem animação pula 4 a 6; quem não usa programa de edição ganha a etapa finalizar com o render; lyric video sem cenas pula cenas e montagem. Mostre a lista final com uma linha por etapa e espere a aprovação. Pergunte também o prefixo dos nomes (ex.: `edit-` gera `/edit-cortes`). A skill mestra não pode se chamar `fluxo-de-edicao`, que é esta.

## Fase 5. Escrever as skills
Na ordem: regras comuns → skill mestra → uma etapa por vez, na ordem do fluxo. Para cada uma:
1. Leia o modelo (`modelos/`) e o guia da etapa (`guias/etapa-*.md`, e os de motion e de entrega quando couber).
2. Escreva a skill com as escolhas da pessoa e o perfil dela. Ofício (vale para qualquer vídeo) vai na skill; gosto (o dela) vai no perfil, e a skill só aponta para lá.
   - **Segundo olhar:** se foi ligado para esta etapa, a skill ganha a seção "Segundo olhar" do modelo, já com a pergunta-base da etapa, o que mandar (proxy, trecho, fps) e o que conferir na resposta. O protocolo do duplo pensamento fica nas regras comuns, uma vez só.
3. Mostre um resumo curto do que a skill faz (não o arquivo inteiro, salvo se ela pedir) e grave em `~/.claude/skills/<prefixo><etapa>/SKILL.md`.
4. Atualize o `montagem.md`.

**Scripts:** as skills dizem *o que* cada script faz e as armadilhas que ele tem que evitar (estão nos guias). Os scripts em si são escritos na primeira vez que a etapa rodar num vídeo de verdade, testados e guardados na pasta de ferramentas para os próximos vídeos. Não escreva scripts especulativos agora. A única exceção é o `ferramentas/gemini.py`, que já vem pronto porque é igual para todo mundo.

**Validação no programa dela:** toda etapa que gera um arquivo para o programa de edição começa, na primeira vez, por um arquivo de teste curto que a pessoa abre e confere. Só depois de ela confirmar a etapa segue. Isso fica escrito na skill de cada etapa (ver `guias/entrega-no-editor.md`).

## Fase 6. Teste num clipe curto
Peça um vídeo de 1–3 minutos (pode ser gravado só para isso) e rode o fluxo inteiro com a pessoa, etapa por etapa, pela skill mestra. No clipe musical, o teste é **um verso e um refrão** (30–45 s) de uma música dela, com material de verdade. É aqui que os scripts nascem e os primeiros aprendizados entram no caderno. Corrija as skills com o que aparecer. Com o segundo olhar ligado, faça ao menos um duplo pensamento completo no teste (um plano e um render), para a pessoa ver como ele funciona e decidir se a dose está certa.

## Fase 7. Fechamento
Mostre, em destaque e antes de tudo, **o comando para editar um vídeo**: "Para editar, abra o Claude Code na pasta do vídeo e digite `/<skill mestra>`. Ela vê em que etapa o vídeo está e te guia." Sugira que a pessoa anote esse comando. Se ela esquecer, basta digitar `/` para ver a lista de skills, ou perguntar ao Claude qual é a skill mestra dela; o nome também fica no `montagem.md`.

Depois, mostre:
- as skills criadas;
- o ciclo do dia a dia: `/clear` e skill mestra a cada etapa; o caderno de aprendizados e como pedir para aplicá-los;
- a sugestão de modelo por etapa (em `guias/principios-do-fluxo.md`).

Marque a montagem como concluída no `montagem.md`. Para mudar o fluxo depois, a pessoa chama `/fluxo-de-edicao` de novo e diz o que quer mudar.

## Regras
- Nunca mover, renomear ou apagar arquivos de vídeo ou de projeto da pessoa.
- Nunca sobrescrever uma skill que já existe sem mostrar o que muda e receber o "sim".
- Instalar programas só depois de explicar e de a pessoa confirmar.
- Não prometer resultado de uma ferramenta sem testar no computador dela.
- Nunca pedir, mostrar ou gravar a chave do Gemini (nem outra senha). A pessoa guarda na variável de ambiente.
- Nunca enviar um arquivo dela a um serviço externo (Gemini, transcrição na nuvem) sem dizer o que vai sair do computador e receber o "sim". Música ou vídeo ainda não lançado: pergunte de novo, por projeto.
- O que o Gemini responde é opinião a conferir, nunca ordem.
