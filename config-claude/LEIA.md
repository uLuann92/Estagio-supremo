# Configuração global: Claude orquestra, Gemini faz o trabalho pesado

Dois arquivos para a pasta `~/.claude/` do seu computador (no Windows: `C:\Users\<você>\.claude\`):

| Aqui | Vai para |
|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` (se já existir um, junte o conteúdo) |
| `mcp/high_effort_bridge.py` | `~/.claude/mcp/high_effort_bridge.py` |

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
4. Conferir dentro do Claude Code com `/mcp`: o servidor `gemini-bridge` deve aparecer com 4 ferramentas.

## Ajustes (variáveis de ambiente opcionais)
- `BRAIN_MODEL_ID`: fila de modelos, separados por vírgula. Padrão: `gemini-4-argon,gemini-pro-latest,gemini-flash-latest`.
- `BRAIN_ROOTS`: pastas onde a ponte pode gravar (separadas por `;`). Padrão: só a pasta em que o Claude Code foi aberto.

## Proteções da ponte
- Só grava dentro das pastas permitidas; não sobrescreve sem `overwrite=True` e guarda uma cópia `.bak`.
- Recusa enviar arquivos com nome de segredo (`.env`, `*.pem`, `*.key`, `credentials*`…).
- Não grava resposta cortada ou fora do formato.
- Confere a sintaxe de `.py` e `.json` e avisa se o arquivo tem trechos omitidos.
