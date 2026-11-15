# Montagem do fluxo de edição

Fase atual: 5 (skills escritas com escolhas-padrão; falta a fase 3, referências, e a fase 6, teste com material real) · Atualizado em 15/11/2026

> As decisões marcadas com **(padrão)** foram escolhidas pelo Claude para adiantar a montagem, sem entrevista. Mude qualquer uma com `/fluxo-de-edicao`.

## Ambiente
- Onde roda: sessão na nuvem do Claude Code, neste repositório (Linux, Python 3.13, FFmpeg, Node 22, Chromium). Sem GPU.
- Instalado: opencv-python-headless, numpy, pillow, mcp, google-genai. HyperFrames por `npx hyperframes@0.9.45`.
- No computador da pessoa: ainda não instalado (passo a passo em `config-claude/LEIA.md`).

## Decisões
- Revisão: **vídeo pronto** (sem programa de edição); a pessoa assiste e pede ajustes pelo chat **(padrão)**
- Tipo e formato: clipe musical com letra na tela, imagem de **quadros de mangá animados**; 16:9, 1920×1080, 24 fps **(padrão)**
- Pastas: projeto em `projetos/AAAA-MM-DD_Nome/` com `Musica/`, `Paginas/`, `Docs/`, `Renders/` e `_CLAUDE/`; ferramentas em `edicao/`
- Música: mixagem final em WAV ou MP3 (Suno); faixas separadas se houver; a letra escrita é a verdade da grafia
- Alinhamento da letra: Demucs (voz isolada) + stable-ts `medium` (alinhamento forçado), em CPU
- Animação: HyperFrames (HTML/CSS/GSAP), versão fixada por vídeo
- Mangá animado: preto e branco com acento de cor; balões saem (a letra da música ocupa o lugar); fundo limpo pelo modelo de imagem do Gemini; máscaras por diferença, com conferência **(padrão)**
- Efeitos: queimados no render **(padrão, por não haver programa de edição)**
- Som: poucos efeitos sobre a música; biblioteca em `edicao/sons/` (vazia: montar no primeiro vídeo)
- Finalização: o fluxo faz tudo (acabamento, áudio, exportação, conferência); extras: legenda `.srt` e quadros para a capa **(padrão)**
- Segundo olhar: **ligado nas etapas-chave** (referências, análise dos quadros, roteiro do primeiro refrão, render do refrão, vídeo final); modelo capaz `gemini-4-argon`, modelo leve `gemini-flash-latest`, imagem `gemini-3.1-flash-image`; pode enviar: referências, páginas, renders e a música; chave na variável `GEMINI_API_KEY`
- Teto de gasto do Gemini: **a combinar** (padrão provisório: avisar a pessoa ao passar de ~R$ 15 num vídeo; o Claude não vê o saldo)
- Nomes: prefixo `clipe-`; skill mestra `/clipe`

## Perfil
- `padrao` (`edicao/perfis/padrao/`): só o esqueleto. Falta medir as referências (links do YouTube dos canais de que a pessoa gosta).

## Fluxo aprovado (padrão; a pessoa ainda não revisou)
1. iniciar — abre o projeto e organiza o briefing
2. musica — grade de batidas, estrutura, acentos, letra alinhada; testes do clique e do karaokê
3. paineis — fatia as páginas e cataloga os quadros
4. roteiro — o plano do clipe, compasso a compasso
5. animar — camadas e animação de cada quadro escolhido, no tempo da música
6. letra — a tipografia animada
7. efeitos — transições e efeitos de seção sobre as cenas
8. sfx — poucos sons de apoio
9. finalizar — montagem final, acabamento, exportação, conferência, extras

## Skills escritas
- [x] regras comuns (`.claude/skills/clipe/regras-comuns.md`)
- [x] skill mestra `/clipe`
- [x] clipe-iniciar, clipe-musica, clipe-paineis, clipe-roteiro, clipe-animar, clipe-letra, clipe-efeitos, clipe-sfx, clipe-finalizar
- Escritas pelo Gemini (ponte) a partir dos guias e conferidas pelo Claude. **Nenhuma rodou ainda num vídeo real.**

## Scripts prontos e testados
- `edicao/scripts/estado.py`: estado do vídeo (testado: iniciar, status, alertas, pendências, blocos).
- `edicao/scripts/musica.py`: `grade`, `clique`, `mapa` (testado numa batida sintética de 140 BPM: andamento exato, início com erro abaixo de 5 ms, primeiro tempo certo).
- `.claude/skills/fluxo-de-edicao/ferramentas/gemini.py` e `painel.py` (testados com a API real e num quadro de teste).

- `edicao/scripts/grade_variavel.py`: grade para música com andamento que varia (testada na Asa Carmesim: mix e instrumental coincidem).
- `edicao/scripts/separar_voz.py` (Demucs) e `edicao/scripts/alinhar_letra.py` (alinhamento forçado com stable-ts, modelo `medium`): rodam em CPU na nuvem; conferidos contra os tempos do Gemini.
- `edicao/scripts/karaoke.py`: o teste do karaokê.

## Scripts que faltam (nascem no primeiro vídeo)
- índice de quadros; montagem final com FFmpeg; conferência do arquivo; legenda `.srt`.

## Aprendido no primeiro vídeo
- Faixa do Suno: o andamento varia (135 a 137 BPM). Usar a grade variável quando o resíduo do `musica.py grade` vier alto.
- Na nuvem dá para baixar os modelos do Demucs e do Whisper: separação e alinhamento rodam aqui (CPU, alguns minutos).
- Para tempo de linha da letra, o `gemini-4-argon` ficou a ~0,2 s do alinhador; o `gemini-pro-latest` inventou tempos. O Gemini serve de conferência, não de fonte.

## Próximo passo
A pessoa manda: a música, a letra, as páginas do mangá e os links das referências. Depois, `/clipe` na pasta do projeto.
