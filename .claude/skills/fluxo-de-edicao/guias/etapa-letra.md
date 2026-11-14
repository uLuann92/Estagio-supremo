# Etapa: letra (a tipografia animada do clipe)

A letra na tela, sincronizada com a voz, palavra por palavra. É o "motion-render" do clipe musical: constrói e renderiza o que o roteiro aprovou. Vale tudo do `oficio-motion.md` (curvas, uma protagonista por vez, alinhamento) e do `hyperframes.md` (ou do guia da ferramenta escolhida). Aqui fica o que é próprio de letra de música.

Fontes, cores, contorno, tamanho e quanto a letra se mexe são do **perfil** (`estilo-letra.md`).

## 1. Ler antes de enfeitar
- **Dá para ler na velocidade em que é cantado?** É a única pergunta que importa. Rap rápido passa de 5 palavras por segundo: ninguém lê uma palavra voando por vez nesse ritmo.
- **No máximo ~2 linhas e ~6–7 palavras na tela** ao mesmo tempo. Linha longa se divide onde o cantor respira ou onde o compasso vira, nunca no meio de uma expressão.
- **Tempo mínimo na tela:** um bloco fica pelo menos o tempo de ser lido (~0,25–0,3 s por palavra, e nunca menos de ~0,6 s), mesmo que o verso já tenha passado. Se o próximo bloco empurrar, o anterior sai rápido, mas não antes de ser visto.
- **Contraste sobre imagem em movimento:** contorno, sombra, uma placa escura ou a cena escurecida e desfocada atrás. Teste sobre o quadro mais claro e o mais confuso da cena, não sobre preto.
- **Área segura** (80% do quadro) e **longe do rosto** e da área de interesse da cena. A posição vem do roteiro e do índice de cenas.
- **Tamanho** para celular: no mínimo o do `hyperframes.md` (28 px em 1080p), e bem maior nas palavras-chave.

## 2. As formas (escolha por seção; variar é o ofício)
| Forma | Como é | Quando |
|---|---|---|
| **Bloco com destaque** | a linha entra inteira no primeiro som dela; cada palavra acende, cresce ou muda de cor quando é cantada | verso rápido: lê-se a linha, sente-se o ritmo |
| **Palavra a palavra** | cada palavra entra no tempo dela, e o bloco se recentraliza (ver `oficio-motion.md` §5) | verso lento, refrão cadenciado |
| **Palavra gigante** | uma palavra ou expressão ocupa o quadro, com impacto | palavra-chave, frase de efeito, o grito do refrão |
| **Empilhado** | as palavras se acumulam, em tamanhos diferentes, formando uma composição | enumeração, verso que cresce |
| **Dobra / fundo** | menor, de lado, outra cor ou opacidade | dobras, respostas, gritos de fundo |

- **O refrão tem uma forma só**, reconhecível, que volta igual (ou maior, na escalada). É a marca do clipe.
- **Não trocar de forma a cada linha.** Uma forma por trecho de 4–8 compassos; a troca acompanha a música.
- **Vozes diferentes, tratamentos diferentes** (cor ou posição), constantes no clipe inteiro.

## 3. Sincronia
- **A palavra entra no começo do som dela** (o tempo alinhado), não na batida. A voz do rap anda entre as batidas; a letra segue a voz.
- **A entrada é curta:** 3–6 frames. Com palavras a cada 5–8 frames, uma entrada de 15 frames nunca termina.
- **Na dúvida, 1 frame adiantada.** Letra atrasada parece erro; adiantada, antecipação.
- **O destaque dura a palavra:** acende no início dela e apaga (ou assenta numa cor de "já cantado") no início da próxima.
- **O bloco troca na virada da linha**, que quase sempre é a virada do compasso. Se cair junto com um corte da montagem, use o frame exato do corte.
- **Os tempos vêm do arquivo de alinhamento, lidos pelo código da animação.** Nunca digitados à mão: a letra de uma música tem centenas de palavras, e uma correção no alinhamento tem de valer sem reescrever a animação.
- **Palavra esticada** (cantada longa): a animação acompanha a duração (cresce, treme, enche de cor) em vez de entrar e ficar parada.

## 4. Ênfase sem bagunça
- **A palavra-chave** é maior, de outra cor ou outra fonte, e ganha o punch no tempo dela. Uma por linha, no máximo.
- **A letra reage à batida com parcimônia:** um pulso leve no bumbo ou uma tremida na caixa, na seção forte. Texto que pula em toda batida não se lê.
- **Quando a cena treme ou pisca, a letra fica firme** (ou o contrário). Tudo tremendo junto vira borrão. Combine com a etapa de efeitos.
- **Saída:** rápida (~0,15–0,25 s), ou levada pelo corte. Letreiro que demora para sair atropela o próximo.

## 5. Grafia (erro aqui é o que o público mais comenta)
- A grafia é a da **letra escrita** aprovada. Um script compara todo texto que vai para a tela com ela e acusa qualquer diferença.
- **Acentos e cedilha:** confira se a fonte escolhida tem todos (ã, õ, ç, é, í, ô) antes de construir. Fonte de impacto gratuita muitas vezes não tem, e o navegador troca por outra sem avisar.
- **Caixa alta** muda a leitura de algumas palavras e some com a diferença entre nomes próprios e comuns: é escolha do perfil.
- **Quebra de linha:** nunca separar artigo ou preposição da palavra seguinte, nem um nome composto.

## 6. Construir e renderizar
- **Uma composição por seção** (ou por 8–16 compassos), não por linha nem o clipe inteiro. Curta o bastante para renderizar e revisar rápido, longa o bastante para a letra ter continuidade.
- **Fundo transparente** (sobreposição), no tempo exato da seção: o número de frames bate com a montagem.
- **Peças-base cedo:** a primeira vez que uma forma ficar boa (o bloco com destaque do verso, a palavra gigante), vira peça reaproveitável, com a letra e os tempos como dados. O resto do clipe, e os próximos, usam a peça.
- **Conferir cada seção:** snapshots no primeiro som de 3–4 palavras espalhadas (a palavra certa está acesa?), no quadro mais cheio (cabe?) e sobre o quadro real da cena (dá para ler? cobre o rosto?).
- **Eventos para o som e para os efeitos:** anote as palavras gigantes e as frases de efeito, com tempo e força.

## 7. Revisão
- A entrega junta a montagem + a letra, por seção. Revisão por linha ou por compasso: "a linha do compasso 21 entra atrasada", "a palavra 'imortal' maior", "refrão: outra cor".
- **Fora do tempo numa linha só** é ajuste no alinhamento daquela linha (volta à etapa de música só para ela), não na animação.
- **Segundo olhar:** crítica de um trecho de 20–30 s com fps alto, perguntando só de leitura e sincronia. Ele assiste com som; o Claude, não.
- Feedback de qualidade geral ("sem graça", "amador") pede refazer a forma, não retocar (`etapa-motion-render.md`).
