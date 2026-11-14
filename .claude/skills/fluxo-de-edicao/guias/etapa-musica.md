# Etapa: música (o "preparar" do clipe musical)

Transforma a faixa em algo que o Claude consegue ler e que os scripts conseguem usar: a **grade de batidas**, a **estrutura**, os **acentos** e a **letra alinhada por palavra**. Tudo o que vem depois (corte, letra, efeito) se apoia aqui. Um erro de 2 frames nesta etapa aparece no vídeo inteiro.

O Claude não ouve a música. Ele lê o que os scripts medem e o que a pessoa conta. Por isso esta etapa tem **dois testes de ouvido** obrigatórios (§5).

## 1. Entradas
- **A mixagem final** (WAV, de preferência). É ela que vai no vídeo, sem reprocessar.
- **Faixas separadas**, se existirem: voz e instrumental (melhor ainda: bateria à parte). Sem elas, separe por programa (ex.: Demucs; pesquise o estado atual). Voz isolada melhora muito o alinhamento; bateria isolada, os acentos.
- **A letra escrita**, na versão final, com as quebras de linha que a pessoa usa e quem canta cada parte.
- Do briefing: BPM e tom, se a pessoa souber; onde fica o refrão; os versos de que ela mais gosta.

## 2. Grade de batidas
- **Andamento e batidas** com um detector (ex.: librosa, beat_this, essentia; pesquise). Ache também o **primeiro tempo de cada compasso**.
- **Batida produzida tem andamento fixo.** Ajuste uma grade constante (BPM + deslocamento do início) às batidas detectadas, em vez de usar cada batida detectada solta: elas tremem alguns milissegundos e isso vira corte fora do tempo. Se o ajuste deixar resíduo crescente, a música muda de andamento: divida em trechos.
- **Dobro ou metade:** detector confunde 70 com 140 BPM, comum em trap. Confirme com a pessoa ou pelo teste do clique. Anote qual das duas leituras guia os cortes; a outra continua valendo para subdividir.
- **Frames:** a batida quase nunca dura um número inteiro de frames (140 BPM a 30 fps dá 12,86 frames). **Nunca some intervalos arredondados**: calcule o tempo de cada batida pela grade e arredonde cada uma, sozinha, para o frame mais próximo. Somando arredondado, o erro cresce até o fim da música.
- **O zero do projeto é o zero do arquivo da música.** Se a música não começar no primeiro frame do vídeo, anote o deslocamento num lugar só.

## 3. Estrutura e acentos
- **Seções** em compassos (intro, verso, pré-refrão, refrão, ponte, final), quase sempre em múltiplos de 4. Proponha pela energia e pela repetição, e confirme com a pessoa numa mensagem curta.
- **Energia por compasso** (volume e densidade de ataques), numa escala simples (1–5). É ela que dosa corte e efeito.
- **Acentos:** os momentos em que a música bate mais forte. Entrada do refrão (o *drop*), viradas de bateria, pausas (o instrumental some por um tempo ou um compasso), subidas, o bumbo e a caixa de cada compasso. Com a bateria isolada, saem dos ataques dela.
- **Silêncios e pausas** são acentos ao contrário: valem ouro para um corte seco, um congelamento ou a tela preta.

## 4. Letra alinhada
- **Alinhamento forçado**, não transcrição: o texto é a letra da pessoa; o áudio (a voz isolada) só dá o tempo de cada palavra (ex.: WhisperX no modo de alinhamento, stable-ts, alinhadores CTC; pesquise). Transcrever rap do zero erra gíria, nome próprio e verso rápido.
- **A letra é a verdade da grafia; o áudio é a verdade do tempo.** Se a pessoa cantou diferente do papel, pergunte qual vale para a tela.
- **Onde o alinhamento falha:** verso muito rápido, dobras e vozes de fundo por cima, efeito pesado na voz, palavra esticada. Marque cada palavra de confiança baixa e cada linha em que o tempo das palavras não cresce de forma natural; essas vão para o teste do karaokê.
- **Dobras, respostas e gritos de fundo** (ad-libs) são anotados à parte: quem canta e o tempo. Na tela, têm tratamento próprio.
- **Mais de uma voz:** cada linha leva quem canta.
- **Palavras-chave:** proponha, por linha, a palavra que carrega o peso (nome, golpe, rima final, frase de efeito). A pessoa corrige. É delas que saem o destaque na letra e os efeitos de ênfase.

## 5. Os dois testes de ouvido (antes de aprovar)
1. **Clique:** um áudio da música com um clique em cada batida e um som diferente no primeiro tempo do compasso. A pessoa ouve 20–30 s do começo, do meio e do fim. Clique adiantado, atrasado ou em dobro se resolve aqui.
2. **Karaokê:** um vídeo simples, em resolução baixa, com cada palavra acendendo no tempo alinhado, o número do compasso e o nome da seção no canto. A pessoa assiste e aponta as linhas fora do tempo. O Claude corrige só essas (realinha o trecho ou ajusta à mão pelo tempo que ela disser).

Com o segundo olhar ligado, o Gemini assiste ao karaokê em blocos curtos, com fps alto, e lista as linhas que parecem fora. É triagem: quem aprova é a pessoa.

## 6. O que o Claude lê depois
- **O mapa da música:** uma linha por compasso, com o número, o tempo, a seção, a energia, os acentos e a letra cantada naquele compasso (com quem canta e a palavra-chave marcada). É por ele que as etapas seguintes decidem.
- O arquivo por palavra e a lista de batidas em frames são só para os scripts.
- No estado do vídeo: BPM, deslocamento, a leitura escolhida (dobro ou metade), as seções em compassos, os caminhos dos arquivos e o que os dois testes confirmaram.

## 7. Depois de aprovada, trava
A grade e a letra alinhada não mudam mais. Se a música for trocada (nova mixagem com duração diferente), esta etapa roda de novo e avisa tudo o que precisa ser recalculado.
