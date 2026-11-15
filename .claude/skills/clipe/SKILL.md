---
name: clipe
description: "Ponto de entrada das skills de edição do usuário: mostra onde o vídeo está (etapas, pendências, alertas, aprendizados anotados) e abre a skill da etapa certa. Também aplica os aprendizados (/clipe aprendizados). Use em /clipe, ao abrir ou retomar um vídeo, depois de um /clear, ou quando o usuário perguntar em que pé está o vídeo."
---

# clipe

Fluxo: `clipe-iniciar` → `clipe-musica` → `clipe-paineis` → `clipe-roteiro` → `clipe-animar` → `clipe-letra` → `clipe-efeitos` → `clipe-sfx` → `clipe-finalizar`

Antes de tudo, leia `.claude/skills/clipe/regras-comuns.md`, uma vez por sessão.

## /clipe

1. **Sem projeto:** os projetos ficam em `projetos/AAAA-MM-DD_Nome/`.
   - Se o usuário abrir `/clipe` na raiz do repositório, liste os projetos existentes em `projetos/` e pergunte qual abrir — ou ofereça a `clipe-iniciar` para criar um novo.
   - Se estiver numa pasta de projeto sem `_CLAUDE/projeto.json`, diga que o vídeo ainda não foi iniciado e ofereça a `clipe-iniciar`.
   - Se a pasta atual não for a raiz nem parecer um projeto em `projetos/`, pergunte se o Claude Code foi aberto no lugar certo.

2. **Status:** rode `python edicao/scripts/estado.py <pasta do projeto> status` e mostre de forma curta:
   - Etapas concluídas, em andamento e travadas.
   - O que já foi feito por trecho (quando a etapa rodar por partes).
   - Pendências de revisão anotadas e ainda não aplicadas.
   - Alertas de dependência ou de teto de gasto do Gemini (~R$ 15 no vídeo).
   - Quantos aprendizados estão anotados em `_CLAUDE/aprendizados.md` com `[ ]`.
   - Se o perfil em `edicao/perfis/<nome do perfil>/` ainda estiver sem referências medidas, avise.

3. **Próximo passo:** diga qual é a etapa seguinte e pergunte se segue. Com o "sim" do usuário, abra a skill da etapa (`.claude/skills/<etapa>/SKILL.md`) e siga as instruções dela.
   - **Etapa aguardando revisão:** o próximo passo é continuar essa mesma etapa e aplicar ou anotar o retorno do usuário, nunca pular para a seguinte.
   - **Alerta de algo desatualizado** (ex.: a grade da música ou o roteiro mudou depois de cenas já animadas): mostre o impacto primeiro e espere a decisão do usuário antes de abrir qualquer etapa.
   - **O usuário pediu outra etapa ou um trecho** (ex.: "sim, até o primeiro refrão", "faz só o verso 1"): abra a etapa pedida e passe o recorte de trecho.

4. **Uma etapa por vez:**
   - Não encadeie etapas sozinho. Ao terminar uma etapa e gerar a entrega em `Renders/`, pare e aguarde a aprovação.
   - Nunca dê `/clear` por conta própria (isso é sempre do usuário; apenas sugira quando houver ponto salvo sem pendências).

5. **Modelo sugerido:** lembre ao usuário, numa linha, o modelo e o esforço recomendados para a etapa que vai abrir (trocar logo após `/clear` não custa limite):
   - `clipe`, `clipe-iniciar`: modelo mais leve, esforço baixo.
   - `clipe-musica`, `clipe-paineis`: modelo intermediário, esforço médio (quase tudo é script).
   - `clipe-roteiro`, `clipe-animar`, `clipe-letra`, `clipe-efeitos`: modelo mais capaz, esforço alto.
   - `clipe-sfx`, `clipe-finalizar`, `/clipe aprendizados`: modelo mais capaz, esforço médio.

6. **Segundo olhar (Gemini):** diga, numa linha, se a etapa que vai abrir usa o segundo olhar por padrão:
   - Ligado nas etapas-chave: `clipe-iniciar` (referências, se houver), `clipe-paineis` (análise dos quadros e limpeza de fundo), `clipe-roteiro` (roteiro do primeiro refrão), `clipe-animar` / `clipe-letra` / `clipe-efeitos` (render do refrão) e `clipe-finalizar` (vídeo final).
   - Lembre que o usuário pode pedir a qualquer hora: "pede um segundo olhar nisso" (seção 6 de `.claude/skills/clipe/regras-comuns.md`, usando `python .claude/skills/fluxo-de-edicao/ferramentas/gemini.py`).

## /clipe aprendizados

Quando o usuário rodar `/clipe aprendizados` ou pedir "aplica os aprendizados":
1. Siga a seção 5 de `.claude/skills/clipe/regras-comuns.md`.
2. Leia os itens abertos (`- [ ]`) em `_CLAUDE/aprendizados.md` do projeto atual (ou dos projetos em `projetos/`, se estiver na raiz).
3. Para cada item, proponha em uma linha onde ele deve entrar: no perfil (`edicao/perfis/<nome do perfil>/`, se for gosto) ou numa skill/regra (`.claude/skills/clipe*/`, se for ofício).
4. Aguarde o usuário filtrar o que entra e o que era só daquele vídeo.
5. Grave apenas o aprovado e marque no caderno: `[x] → <arquivo onde entrou>` ou `[-]` se descartado.

## Regras

- Não edite vídeo, não chame o HyperFrames nem rode scripts de etapa: o papel da `/clipe` é apenas recepcionar, ler o status e encaminhar.
- Nunca mova, renomeie ou apague arquivos do projeto (`Musica/`, `Paginas/`, `Docs/`, `Renders/`).
- Se `edicao/scripts/estado.py` ainda não existir no primeiro vídeo, avise o usuário e ofereça abrir a `clipe-iniciar` para criar a estrutura inicial.
