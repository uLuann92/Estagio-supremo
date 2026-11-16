# Protocolo obrigatório de roteamento: Claude orquestra, Gemini faz o trabalho pesado

Objetivo: gastar os tokens do Claude só em orquestração, revisão crítica final (duplo pensamento) e edições cirúrgicas. O resto vai para o Gemini pelo servidor MCP `gemini-bridge` (`~/.claude/mcp/high_effort_bridge.py`).

Ferramentas da ponte:
- `gemini_direct_file_worker(task_prompt, input_files, output_file, overwrite)`: o Gemini lê os arquivos direto do disco e, com `output_file`, grava o resultado no disco. Volta só um resumo de até 10 linhas e as assinaturas.
- `dual_think_high_effort(prompt, cache_name)`: segundo pensamento sobre um plano, um bug ou uma decisão.
- `cache_heavy_context(cache_name, file_paths)`: várias perguntas sobre o mesmo material grande (vídeo, repositório).
- `carbon_web_research(query, save_report_to)`: pesquisa na web com a busca do Google ligada (personagens, obras, lutas, episódios, capítulos, tags do Sakugabooru; também engenharia e jogos). Com `save_report_to`, grava o dossiê em Markdown com as fontes e volta só o resumo executivo.
- `check_active_models()`: modelos que a chave alcança.

Script auxiliar (via Bash, depois do dossiê): `python ~/.claude/mcp/fetch_media_refs.py <subcomando>` grava em `./referencias/` do projeto, com `creditos.json`:
- `sakuga-tags` e `sakuga`: acha a tag e baixa cortes de animação do Sakugabooru, como referência de estudo;
- `mangadex`, `mangadex-capitulos`, `mangadex-capas`: dados da obra, numeração de capítulos e capas;
- `jikan`, `jikan-episodios`: dados e lista de episódios.
- Ele **não baixa páginas de capítulos de mangá**. As páginas vêm do usuário.

## 0. Modelo
- **Motor principal: `gemini-4-carbon`**, com raciocínio alto (`HIGH`), em tudo: código, shaders, vídeo, áudio, jogo, livro e pesquisa. É o padrão da ponte; não passe `model_id` nessas tarefas.
- **`gemini-4-argon` só por pedido explícito** (`model_id="gemini-4-argon"`) e só em tarefa puramente mecânica: ler log simples, formatar JSON.
- Se o carbon não responder, a ponte cai para a fila de reserva e **diz qual modelo respondeu**: repasse isso ao usuário.
- Medido em 15/11/2026: carbon + busca na web + raciocínio alto passa de 8 minutos. Na `carbon_web_research`, a ponte tenta o nível alto e, se estourar o tempo, repete no nível padrão do próprio carbon (foi o que respondeu no teste, em ~1 a 2 minutos por pergunta curta). Uma pesquisa pode levar até ~9 minutos: rode em segundo plano.

## 1. Proibido ler arquivos grandes direto
Nunca use `Read` em arquivos com mais de 250 linhas, logs de erro, JSONs grandes ou código descompilado. Passe o caminho em `input_files` para o Gemini ler, resumir ou localizar o bug (ele cita arquivo e linha).
- Depois, leia só o trecho apontado (`Read` com `offset` e `limit`) para conferir e editar.

## 2. Geração pesada direto no disco (zero-copy)
Sempre que precisar criar um arquivo novo grande (componentes Remotion, shaders GLSL, sistemas do jogo, scripts Python de análise), mande a especificação técnica para `gemini_direct_file_worker` gravar direto no `output_file`. Depois, rode um `git diff` rápido ou leia somente as linhas críticas para auditar.
- A especificação precisa ser completa: entradas, saídas, nomes, dependências permitidas, casos de borda. O Gemini não vê a conversa.
- Um arquivo por chamada. Se a ponte disser que a resposta veio cortada, divida a tarefa.

## 3. Roteamento por especialidade
- **100% Gemini via MCP:** análise de vídeos (.mp4), músicas do Suno (.mp3/.wav), leitura de diretórios inteiros, geração de boilerplate, shaders, cálculos matemáticos e física de jogos, tradução e documentação.
- **Duplo pensamento (Gemini gera → Claude audita):** arquitetura de sistemas complexos do jogo, sincronia de timeline de vídeo e correção de bugs que falharem no terminal.
- **100% Claude:** execução de comandos Bash/Git, ajustes cirúrgicos (`Edit` de poucas linhas) e validação final de qualidade depois que o Gemini escrever o arquivo.

## 4. O que mantém a qualidade (parte do protocolo, não opcional)
- **Nada escrito pelo Gemini é dado como pronto sem rodar.** Depois de cada arquivo gerado: executar, compilar ou testar. Resumo e assinaturas dizem o que ele afirma ter feito, não o que funciona.
- **Número de capítulo, episódio ou minutagem vindo da pesquisa é pista, não fato:** confira os que forem usados (na numeração do MangaDex, na lista de episódios, ou com o usuário) antes de pedir uma página por ele.
- **O que o Gemini afirma sobre um arquivo, vídeo ou áudio é conferido** no trecho citado ou por medida antes de virar mudança. Tempo de vídeo citado por ele é aproximado; ele não enxerga detalhe de poucos frames (tremida, flash).
- **Falhou duas vezes pela ponte, o Claude assume:** lê o que for preciso e resolve direto. Insistir gasta mais do que economiza.
- **Se a ponte não estiver disponível** (sem chave, sem cota, sem rede), avise em uma linha e trabalhe normalmente, sem travar.
- **Segredos não saem do computador:** `.env`, chaves, credenciais e dados pessoais nunca vão em `input_files` (a ponte recusa os nomes óbvios; os outros são responsabilidade do Claude).
- **Código alheio ou sob sigilo** (cliente, trabalho): pergunte antes de enviar ao Google.
- Diga ao usuário, no fim, o que foi feito pelo Gemini e o que foi conferido.
