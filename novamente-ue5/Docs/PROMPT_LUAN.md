# NOVAMENTE · Prompt do Luan: 13 anos e 31 anos, do zero

## Como usar (para o autor)

- Mande junto com o `PROMPT_HUMANOS.md` (a regra zero vale aqui) ou depois dele, na mesma sessão.
- Anexe e coloque em `Referencias/` com estes nomes:

  | Arquivo | O que é |
  |---|---|
  | `luan_crianca_frente.jpg`, `_perfil`, `_34`, `_costas`, `_close` | o render da criança (já existe) |
  | `luan_adulto_a.jpg` | o adulto de cabelo longo ondulado e jaqueta: o alvo principal dos 31 anos |
  | `luan_adulto_b.jpg` | o adulto de cabelo curto cacheado e camiseta preta: a mesma pessoa, um pouco mais velha |
  | `capa_v3.jpg` | a capa; o personagem do meio é o Luan adulto |

- Se puder, faça para o adulto a mesma prancha de quatro vistas que existe da criança (frente, perfil, três quartos, costas). Sem isso, o perfil e as orelhas do adulto ficam no chute.
- Depois de colocar as imagens, tire as fichas e sele:
  ```
  python Scripts/medidas_rosto.py --ficha Referencias/luan_adulto_a.jpg --out Referencias/ficha_luan_adulto_a.json
  python Scripts/medidas_rosto.py --ficha Referencias/luan_adulto_b.jpg --out Referencias/ficha_luan_adulto_b.json
  python .claude/hooks/exigir_prova.py --selar
  ```

---

## 1. O que está na tela e por que parece um homem velho e abatido

Medido com o `medidas_rosto.py` contra o render da criança:
- erro médio de identidade de 5,5% (meta 2%);
- 18 medidas fora.

**Rosto**
- Testa 27% alta demais: a linha do cabelo recuou nas têmporas (entrada de adulto).
- Do olho à base do nariz, 10,5% mais comprido; nariz 8% mais comprido até a ponta.
- Mandíbula 7,6% mais larga e mais quadrada (136° contra 143°); queixo 4% mais estreito.
- Olhos 5,8% mais afastados, quase fechados, inclinados, com íris amarelo-esverdeada.
- Inchaço rosado em volta dos dois olhos. Parece o material de ferimentos (Lei de Goggins) ligado; nas fotos de referência ele fica desligado.
- Boca pequena com os cantos para baixo; pescoço grosso emendado na mandíbula; orelhas pequenas e coladas.
- Cabelo de adulto penteado de lado, com volume em cima e testa à mostra.

**Corpo**
- Barriga saliente.
- Ombros caídos e estreitos.
- Braços compridos até o meio da coxa.
- Cabeça pequena para o corpo: o garoto de 13 anos tem 7,1 cabeças de altura e cabeça proporcionalmente grande.

**Luz**
- A luz chapada do nível do Game Animation Sample (roxo) não serve para julgar pele nem cor.

Conclusão: a base continua sendo de adulto, e o corpo não é o do garoto magro. Nada disso se conserta com slider. **As duas idades são refeitas do zero.**

## 2. Quem é a verdade de cada idade

| Idade | Identidade (o rosto) | Cabelo, barba e aparência | Luz para comparar |
|---|---|---|---|
| 13 anos (2017) | o render das quatro vistas | o do render: curto, castanho escuro, penteado para a frente, orelhas de abano à mostra | a sala do cobogó |
| 31 anos (2036) | `luan_adulto_a` e `luan_adulto_b` (medidos: a mesma pessoa, 2,8% de diferença) | o do `luan_adulto_a` e do centro da capa: cabelo escuro longo e ondulado na testa, barba e bigode ralos, olheira funda, cansado | noite com contraluz quente, folhas e fagulhas, como nas imagens do adulto |

- **O adulto de 31 anos parece um pouco mais novo que o `luan_adulto_b`:**
  - menos marcas no rosto;
  - barba mais rala;
  - nenhum fio branco.
- **O mesmo menino crescido.**
  - Da criança, o adulto herda a cor dos olhos (avelã), o tom de pele de base (pardo claro) e a forma do olho.
  - O cabelo escurece e ondula com a idade, o que é comum.
  - O autor aprova a continuidade numa foto com as duas idades lado a lado.
- **A Sombra usa o mesmo corpo do adulto.** Ela só é feita depois do adulto aprovado.

## 3. Como fazer

**Para as duas idades:**
1. Apague do projeto e da receita tudo do Luan atual: rosto, corpo, groom, materiais. Rode o `auditar_humanos.py`.
2. Rosto pelo FaceBuilder com as vistas da idade, depois Mesh to MetaHuman. Nada de partir de preset de adulto ajustado.
3. Corpo pelo `corpos_padrao.json`:
   - 13 anos: `garoto_13_14`, magro, 1,58 m. Sem barriga, ombro estreito mas reto, braço até o meio da coxa só quando relaxado, 7,1 cabeças.
   - 31 anos: `masculino`, na altura que o autor confirmar (1,63 m no canon antigo, 1,84 m no registro novo) e na variante que ele escolher (magro ou médio).
4. Medir até passar:
   - `medidas_rosto.py` contra a ficha da idade;
   - `medir_corpo.py` e `medir_esqueleto.py` contra o corpo padrão.
5. Pele, olhos, cabelo e roupa, só com a forma aprovada.
   - Criança: a farda com a gola canelada.
   - Adulto: camiseta preta gasta e a jaqueta azul-marinho com listras lilás, suja de terra.
6. Ferimentos, suor e sujeira desligados nas fotos de referência; ligados só nas fotos de jogo.
7. Expressão:
   - criança: espanto sem ruga de adulto;
   - adulto: cansado, olhar firme, sobrancelha baixa, como nas imagens.
8. Fotografar no provador e na luz da idade: frente, perfil, três quartos e corpo inteiro com régua. Depois as duas idades lado a lado.

**Metas:**

| | 13 anos | 31 anos |
|---|---|---|
| Identidade (cada medida) | até 3% | até 3% |
| Identidade (média) | até 2% | até 2% |
| Pele (Delta E) | até 5, na sala do cobogó | até 5, na luz da noite |
| Corpo | dentro do `garoto_13_14` | dentro do `masculino` na altura e variante aprovadas |
| Aprovação | o autor nas três vistas | o autor nas três vistas e lado a lado com a criança |

## 4. Regras

- Uma idade por vez: primeiro os 13 anos, depois os 31.
- Número antes e depois de cada ajuste.
- Nunca "pronto" sem: auditoria LIMPA, réguas PASSOU e DENTRO, parecer APROVADO e o sim do autor.
- Se o FaceBuilder, o login da Epic ou a montagem do MetaHuman travarem, encerre com "PENDENTE:". Nunca volte para preset ajustado nem para malha feita à mão.
- O garoto tem 13 anos: sempre revisado vestido.

## 5. Sua primeira resposta

1. A ficha das duas idades: medidas do render e das imagens do adulto, as cores, e o que falta de vista (perfil e costas do adulto).
2. A confirmação de que o Luan atual foi apagado e a auditoria limpa.
3. O plano dos 13 anos, passo a passo, com o que o autor precisa fornecer.
4. As duas decisões do autor, com fotos de opção: a altura dos 31 anos e a variante de corpo.
