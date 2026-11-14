# Fluxo de edição com o Claude Code

Uma skill gratuita que te guia, passo a passo, a montar o **seu** fluxo de edição de vídeo com o Claude Code: cortes, animações, movimentos de câmera e efeitos sonoros, no seu estilo.

Ela não é um prompt mágico e não entrega o meu fluxo pronto. Ela conversa com você, pergunta o que você quer, analisa as referências de que você gosta e escreve as skills de cada etapa para o seu jeito de trabalhar: YouTube, reels, vídeo narrado, com ou sem programa de edição.

O ponto de partida é um fluxo de 8 etapas que eu uso nos meus vídeos, com os bons costumes de animação e de fluxo que aprendi testando: curvas, ritmo, câmera, sincronia de som, as armadilhas do HyperFrames e do XML do Premiere. Sem a minha identidade visual: o estilo é o seu.

## Nesta versão (adaptada)
Esta cópia parte da skill original de Lucas Leite ([LeiteZ/fluxo-de-edicao](https://github.com/LeiteZ/fluxo-de-edicao), licença MIT) e acrescenta:

- **Clipe musical com letra na tela** (rap geek, AMV, lyric video): um segundo fluxo de referência, em que tudo se alinha pela batida e pela letra cantada. Etapas novas: música, cenas, roteiro, montagem, letra, efeitos.
- **Segundo olhar com o Google Gemini** (duplo pensamento): o Gemini assiste ao vídeo com som e dá um parecer independente; o Claude confere, compara com o próprio e mostra a você onde os dois concordam e onde não. Opcional, com um script pronto (`ferramentas/gemini.py`).
- **Mangá animado:** em vez de trazer vídeos, você aponta as páginas. A skill fatia a página em quadros, separa as camadas (`ferramentas/painel.py`) e anima cada quadro com câmera, profundidade, antecipação, quadro de impacto, tremida, linhas de velocidade e cor. Há um exemplo que roda em `exemplos/painel-animado/`.
- **Etapa finalizar**, para a edição sair completa: acabamento da imagem, áudio final, exportação, conferência automática do arquivo e extras (legenda, capa, créditos).

O estilo de um canal de que você gosta não vem pronto aqui: ele é **medido** nos trechos de referência que você juntar, e a identidade visual é a sua.

## O que você precisa
- Assinatura do Claude (Pro ou superior).
- [Claude Code](https://claude.com/claude-code) instalado no computador.
- O resto (Python, FFmpeg, transcrição, HyperFrames…) a própria skill confere e instala com você, explicando cada passo.
- Para o segundo olhar (opcional): uma chave do Google Gemini, guardada por você na variável de ambiente `GEMINI_API_KEY`. A skill explica como criar. No plano gratuito funcionam só os modelos "flash"; com faturamento ligado, também o modelo mais capaz e os de imagem (que refazem o fundo dos quadros de mangá).

## Como instalar
Abra o Claude Code e cole:

```
Instala esta skill para mim: https://github.com/LeiteZ/fluxo-de-edicao
```

Ou, pelo terminal:

```bash
git clone https://github.com/LeiteZ/fluxo-de-edicao ~/.claude/skills/fluxo-de-edicao
```

Os comandos acima instalam a skill **original**. Para instalar **esta versão adaptada**, copie a pasta `fluxo-de-edicao` deste repositório (em `.claude/skills/`) para `~/.claude/skills/` no seu computador.

## Como usar
No Claude Code, digite:

```
/fluxo-de-edicao
```

Ela começa a te guiar:

1. **Ambiente:** confere o que já está instalado.
2. **Entrevista:** tipo de vídeo, formato, programa de edição (ou nenhum), transcrição ou música, animação, câmera, som, finalização e o segundo olhar.
3. **Referências:** você junta trechos de vídeos de que gosta, e ela analisa e cria o seu perfil de estilo.
4. **Plano do fluxo:** as etapas, adaptadas para você.
5. **As skills:** ela escreve uma por etapa, mais uma skill mestra que te guia pelo fluxo e um caderno de aprendizados.
6. **Teste:** um vídeo curto, do começo ao fim.

Dá para parar e continuar depois: ela anota onde parou.

## Depois de montar: como editar um vídeo
O `/fluxo-de-edicao` não edita vídeo: ele monta o seu fluxo. Durante a montagem, você escolhe o nome da sua **skill mestra** (por exemplo, `/editar`). É ela que você usa no dia a dia:

1. Abra o Claude Code na pasta do vídeo.
2. Digite a sua skill mestra (ex.: `/editar`).
3. Ela vê em que etapa o vídeo está e te guia, uma etapa por vez.

Esqueceu o nome? Digite `/` para ver a lista de skills, ou pergunte ao Claude qual é a sua skill mestra. Para continuar a montagem ou mudar o fluxo depois, use `/fluxo-de-edicao` de novo.

## O que tem aqui
| Pasta | O que tem |
|---|---|
| `SKILL.md` | O roteiro da conversa |
| `guias/` | O conhecimento: princípios do fluxo, decisões, análise de referências, ofício de animação, HyperFrames, entrega no programa de edição e o ofício de cada etapa |
| `modelos/` | Os esqueletos das skills, do perfil e do estado do vídeo |
| `ferramentas/` | `gemini.py` (conversa com o Gemini; aceita vídeo, imagem e link do YouTube) e `painel.py` (fatia páginas de mangá e separa camadas) |
| `exemplos/` | Um quadro de mangá animado que roda no HyperFrames, para servir de ponto de partida |

Tudo em texto. Leia, mude, adapte.

## Licença
MIT. Use, mude e compartilhe à vontade.

Skill original feita por Lucas Leite. Esta versão foi adaptada a partir dela.
