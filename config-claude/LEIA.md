# Configuração global: Claude orquestra, Gemini faz o trabalho pesado

Dois arquivos para a pasta `~/.claude/` do seu computador (no Windows: `C:\Users\<você>\.claude\`):

| Aqui | Vai para |
|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` (se já existir um, junte o conteúdo) |
| `mcp/high_effort_bridge.py` | `~/.claude/mcp/high_effort_bridge.py` |
| `mcp/fetch_media_refs.py` | `~/.claude/mcp/fetch_media_refs.py` |

## Instalar (uma vez)
1. Dependências:
```bash
pip install mcp google-genai
```
2. A chave na variável de ambiente `GEMINI_API_KEY` (no Windows: `setx GEMINI_API_KEY "sua-chave"` e abra o terminal de novo). Nunca dentro de um arquivo.
3. Registrar o servidor no Claude Code, para todos os projetos (troque o caminho pelo seu):
```bash
claude mcp add --scope user gemini-bridge -- python ~/.claude/mcp/high_effort_bridge.py
```
4. Conferir dentro do Claude Code com `/mcp`: o servidor `gemini-bridge` deve aparecer com 5 ferramentas.

## Vertex AI (créditos do Google Cloud)
1. No Google Cloud: ative a API "Vertex AI" no projeto, crie uma conta de serviço com o papel **Vertex AI User** e baixe a chave JSON.
2. Salve a chave como `~/.claude/vertex-key.json` (no Windows: `C:\Users\<você>\.claude\vertex-key.json`). Nunca cole o conteúdo dela num chat nem a coloque num repositório.
3. Pronto: a ponte liga a Vertex sozinha quando esse arquivo existe (ou com `USE_VERTEX_AI=true`). O projeto vem do `project_id` da própria chave; a região começa em `global` e cai para `us-central1` quando o modelo pede região.
4. Teste fora do Claude Code:
```bash
python ~/.claude/mcp/high_effort_bridge.py --teste
```
Ele mostra se a Vertex ligou, o projeto, as regiões e **qual modelo respondeu e por qual caminho** ("via Vertex AI/global", "via Vertex AI/us-central1" ou "via AI Studio (chave)"). Se a Vertex falhar e houver `GEMINI_API_KEY`, a ponte segue pela chave e diz isso na resposta.

## Ajustes (variáveis de ambiente opcionais)
- `BRAIN_MODEL_ID`: fila de modelos, separados por vírgula. Padrão: `gemini-4-carbon,gemini-pro-latest,gemini-flash-latest`.
- `BRAIN_ROOTS`: pastas onde a ponte pode gravar (separadas por `;`). Padrão: só a pasta em que o Claude Code foi aberto.

## Proteções da ponte
- Só grava dentro das pastas permitidas; não sobrescreve sem `overwrite=True` e guarda uma cópia `.bak`.
- Recusa enviar arquivos com nome de segredo (`.env`, `*.pem`, `*.key`, `credentials*`…).
- Não grava resposta cortada ou fora do formato.
- Confere a sintaxe de `.py` e `.json` e avisa se o arquivo tem trechos omitidos.
