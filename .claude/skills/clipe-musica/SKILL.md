---
name: clipe-musica
description: "Mapeia a grade de batidas, estrutura, acentos e alinha a letra por palavra, gerando os testes de clique e karaokê. Use em /clipe-musica, após a clipe-iniciar."
---

# clipe-musica

Transforma a música e a letra escrita na base técnica do projeto: grade de batidas em 24 fps, seções, acentos, letra alinhada por palavra e o mapa da música por compasso. Entrega os testes de ouvido (clique e karaokê) para o usuário aprovar. Não foca em imagens do mangá nem cria animações finais.

- **Lê:** `_CLAUDE/projeto.json` (bloco `iniciar`), arquivos em `Musica/` (mixagem final e faixas separadas, se houver), letra e briefing em `Docs/`, perfil em `edicao/perfis/<nome do perfil>/`
- **Escreve:** bloco `musica` em `_CLAUDE/projeto.json`, dados e mapa em `_CLAUDE/musica/`, entregas de teste em `Renders/testes/` (ou `_CLAUDE/musica/testes/`)
- **Próximo passo:** `/clipe-paineis`

Se a etapa `iniciar` não estiver `concluido`, pare e sugira terminá-la com `/clipe-iniciar`.

## Ofício
Consulte `.claude/skills/fluxo-de-edicao/guias/etapa-musica.md` para detalhes. Princípios essenciais:
- **Grade constante e exata (regra técnica):** Batida produzida tem andamento fixo. Ajuste uma grade constante (BPM + deslocamento) em vez de usar batidas detectadas soltas. A 24 fps, nunca some intervalos arredondados: calcule o tempo de cada batida pela grade e arredonde cada uma sozinha para o frame inteiro mais próximo. O zero do projeto é o zero do arquivo da música.
- **Dobro ou metade:** Confirme com o usuário se o corte segue o BPM cheio ou a metade (comum em trap).
- **Estrutura, energia e acentos (tendência, não regra):** Seções em compassos (quase sempre múltiplos de 4), energia de 1 a 5 por compasso. Marque entradas de refrão (*drops*), viradas, bumbo/caixa e silêncios (pausas valem ouro para cortes secos).
- **Alinhamento forçado:** A letra escrita é a verdade da grafia; o áudio é a verdade do tempo. Se cantou diferente do papel, pergunte ao usuário. Marque quem canta cada linha, ad-libs à parte e proponha uma palavra-chave de peso por linha. Destaque palavras de confiança baixa para revisão no karaokê.
- **Trava pós-aprovação:** Depois de aprovada, a grade e a letra alinhada não mudam mais.

## Perfil
Leia em `edicao/perfis/<nome do perfil>/` (nome definido em `_CLAUDE/projeto.json`):
- Critérios de ritmo e divisão de energia para orientar a leitura de dobro/metade e a escolha das palavras-chave de cada verso.

## Scripts
O script `edicao/scripts/musica.py` já existe. Os demais serão escritos e testados na primeira vez que a etapa rodar num vídeo real; anote o uso aqui depois para reaproveitar nos próximos.

| Script | O que faz | Armadilhas a evitar |
| :--- | :--- | :--- |
| `python edicao/scripts/musica.py grade` | Detecta BPM, primeiro tempo do compasso e ajusta grade constante em 24 fps. | Somar intervalos arredondados (gera deriva); usar batidas soltas sem grade; ignorar mudança de andamento. |
| `python edicao/scripts/musica.py clique` | Gera áudio da música com clique nas batidas e som distinto na cabeça do compasso. | Reprocessar ou alterar a mixagem original; errar o deslocamento inicial. |
| `python edicao/scripts/musica.py mapa` | Gera o mapa da música (uma linha por compasso com tempo, seção, energia, acentos, letra e palavra-chave). | Dessincronizar número de compasso com a lista de frames e tempos das palavras. |
| `edicao/scripts/alinhar.py` *(escrever na 1ª vez)* | Alinhamento forçado da letra escrita contra o áudio (voz isolada se houver). Sem GPU e sem acesso ao Hugging Face na nuvem: pesquisar na hora a ferramenta viável. | Transcrever do zero (erra gíria e nome próprio); esconder palavras de baixa confiança ou tempos não crescentes. |
| `edicao/scripts/karaoke.py` *(escrever na 1ª vez)* | Gera vídeo simples em baixa resolução (24 fps) com palavra acendendo no tempo, número do compasso e seção no canto. | Vídeo pesado demais; omitir marcação visual nas linhas de baixa confiança. |

## Passo a passo
1. Verifique o status e pendências (`python edicao/scripts/estado.py <pasta do projeto> status`).
2. Analise a faixa com `python edicao/scripts/musica.py grade` e gere o áudio de teste com `python edicao/scripts/musica.py clique`.
3. Se não houver voz/bateria isoladas e for necessário para acentos ou alinhamento, pesquise na hora ferramenta leve que rode sem GPU/Hugging Face ou use a mixagem combinada com o parecer do Gemini.
4. Na primeira música, pesquise na hora, escreva e teste o script de alinhamento forçado e o gerador de vídeo de karaokê. Rode o alinhamento da letra, marque quem canta, ad-libs, palavras de baixa confiança e proponha as palavras-chave por linha.
5. Proponha as seções em compassos, a energia (1–5) e os acentos; gere `_CLAUDE/musica/mapa.md` com `python edicao/scripts/musica.py mapa`.
6. Passe pelo Segundo olhar (Gemini) para checar seções, viradas e triar o karaokê.
7. Entregue o áudio do clique e o vídeo do karaokê (sem nunca sobrescrever versões anteriores). **Primeira vez de todas:** gere um arquivo de teste curto (20–30s), peça para o usuário conferir, anote na validação e só então gere o completo.

## Segundo olhar
- **Quando:** Ao mapear seções/acentos da música e logo após gerar o vídeo do teste de karaokê, antes de entregar ao usuário.
- **Uso:** Parecer independente no áudio e olhar de triagem no vídeo de karaokê com `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py perguntar` (modelo leve `gemini-flash-latest` para triagem rápida ou capaz `gemini-4-argon` se houver dúvida complexa).
- **O que mandar:** Arquivo da música para estrutura/clima; vídeo do karaokê dividido em blocos curtos com fps alto, acompanhado da letra escrita.
- **Pergunta-base:** 1) Áudio: "Ouça a faixa e indique em segundos as mudanças de seção (intro, verso, pré-refrão, refrão, ponte), quedas/pausas e viradas fortes de bateria." 2) Karaokê: "Assista ao bloco do karaokê e liste os números de compasso e linhas em que a palavra acende visivelmente adiantada ou atrasada em relação à voz."
- **O que conferir na resposta:** Confrontar os tempos apontados pelo Gemini com a grade de compassos e os dados de confiança do alinhador; ajustar antes de mostrar ao usuário.
Seguir o protocolo da seção 6 das regras comuns (`.claude/skills/clipe/regras-comuns.md`).

## Resumo no chat
Curto: BPM encontrado (e se está em dobro/metade), seções propostas em compassos, linhas da letra que tiveram baixa confiança ou divergência com o áudio, e os caminhos do áudio de clique, do vídeo de karaokê e do mapa da música. Marque a etapa como `aguardando_aprovacao` com `python edicao/scripts/estado.py <pasta do projeto> ...`.

## Revisão
O usuário devolve pelo chat dizendo se o clique está cravado (ou adiantado/atrasado/em dobro) e listando linhas, números de compasso ou tempos fora de sincronia no karaokê, além de ajustes nas seções e palavras-chave. Ajuste só o que foi citado (recalcule a grade se o clique mudou, ou realinhe/ajuste à mão os trechos da letra), gere versão nova numerada dos testes e atualize o mapa. Anote aprendizados em `_CLAUDE/aprendizados.md`.

## Aprovação
Quando o usuário aprovar clique, karaokê e mapa, salve os dados finais no bloco `musica` de `_CLAUDE/projeto.json`, marque a etapa como `concluido` via `edicao/scripts/estado.py`, diga quantos aprendizados ficaram anotados e sugira `/clear` e `/clipe`.

## Regras comuns
Antes de começar, leia `.claude/skills/clipe/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto, nem sobrescrever entregas anteriores.
- Nunca somar intervalos de batida arredondados; calcular sempre pela grade constante e arredondar cada batida individualmente para o frame (24 fps).
- Falar com o usuário em português, de forma curta e direta.
