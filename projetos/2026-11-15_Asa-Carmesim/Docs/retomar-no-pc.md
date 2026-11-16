# Retomar o Asa Carmesim no PC

O projeto saiu da sessão na nuvem em 16/11/2026, na etapa de música (`aguardando_aprovacao`). Tudo o que foi decidido e medido está no repositório. Faltam só os arquivos grandes, que ficam fora do GitHub.

## 1. Pôr a música no lugar
Copie o seu `Asa_Carmesim.mp3` para `projetos\2026-11-15_Asa-Carmesim\Musica\` (com esse nome).

## 2. Instalar o que a etapa de música usa (uma vez)
```bash
pip install numpy librosa opencv-python-headless pillow mcp google-genai demucs stable-ts
```
O Demucs e o stable-ts instalam o PyTorch. Com placa NVIDIA, instale antes o PyTorch com CUDA (pesquise o comando atual no site do PyTorch) para ficar bem mais rápido. Precisa também do FFmpeg no PATH.

## 3. Refazer o que não foi para o GitHub (opcional)
Já estão no repositório: a letra (`Docs/letra.md`), a letra palavra por palavra (`_CLAUDE/musica/letra_por_palavra.json`), a grade de batidas, as seções e o mapa. Só os arquivos de áudio somem. Para recriá-los, na pasta do repositório:

Voz separada do instrumental (alguns minutos):
```bash
python edicao/scripts/separar_voz.py projetos/2026-11-15_Asa-Carmesim/Musica/Asa_Carmesim.mp3 --saida projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/faixas
```

Teste do karaokê:
```bash
python edicao/scripts/karaoke.py --audio projetos/2026-11-15_Asa-Carmesim/Musica/Asa_Carmesim.mp3 --palavras projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/letra_por_palavra.json --batidas projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/batidas.json --suspeitas projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/letra_por_palavra_suspeitas.json --saida projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/testes/teste_do_karaoke.mp4
```

Teste do clique (um trecho; repita com outros `--inicio`/`--fim`):
```bash
python edicao/scripts/musica.py clique projetos/2026-11-15_Asa-Carmesim/Musica/Asa_Carmesim.mp3 --batidas projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/batidas.json --saida projetos/2026-11-15_Asa-Carmesim/_CLAUDE/musica/testes/clique.wav --inicio 40 --fim 62
```

Ou simplesmente abra o Claude Code na pasta do repositório e digite `/clipe`: ele lê o estado e refaz o que faltar.

## 4. Onde o projeto parou
- **Etapa de música:** aguardando você ouvir o clique e assistir ao karaokê (linhas a conferir: 48, 71, 89 e 104).
- **Decidido:** a Asa Carmesim é a Erza (Fairy Tail). Pesquisa em `Docs/pesquisa/erza-scarlet.md`.
- **Pendente (aparece no `/clipe`):** de onde vêm as imagens (as páginas vêm de você; o fluxo não baixa capítulos) e quanta letra vai na tela (as referências quase não usam).
