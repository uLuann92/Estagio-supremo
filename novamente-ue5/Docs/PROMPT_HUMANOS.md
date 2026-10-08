# NOVAMENTE · Prompt de Humanos: gente bonita, proporcional e fiel à Bíblia

## Como usar (para o autor)

- Abra uma sessão só para isto, dentro da pasta do projeto Unreal, com o kit instalado (`instalar.py` copia este prompt e o `auditar_humanos.py`).
- Mande este texto inteiro como primeira mensagem, com anexos:
  - o render do Luan (quatro vistas e close);
  - a capa;
  - os capítulos e a Bíblia, se a IA ainda não tiver acesso a eles no projeto.
- Ele complementa o `PROMPT_PERSONAGENS.md` (corpos padrão, templates e medidas do rosto do Luan). Este aqui decide **como** cada pessoa é feita e **o que é proibido**.

---

## 1. O que está na tela hoje, e não pode continuar

As capturas do capítulo 2 ("Porta do mercadinho" e "Quarto alugado", Realidade 2) mostram:

- **Pessoas montadas por código ou com formas básicas:**
  - tronco de caixa, braço de prisma, pé de bloco, saia de cone;
  - cabelo de bolhas e de planos soltos flutuando;
  - olhos de esfera preta, narina de buraco, boca de polígono, orelha de fita.
- Nenhuma delas é MetaHuman. Por isso parecem bonecos de teste, e o close vira um pesadelo.
- **A câmera entra dentro da cabeça** no quarto alugado.
- **Dois avisos vermelhos na tela:**
  - a exposição da cena (14,3) está fora da faixa segura do Lumen (-8 a 12);
  - há um Sky Light com captura em tempo real sem SkyAtmosphere, então o céu capturado fica preto.
- **Texto da interface quebrado:**
  - "CONSEQUêNCIAS": a caixa alta não trata o acento;
  - "E · E · janela": o aviso de interação sai duplicado.
- **Formas básicas largadas na cena** (as duas esferas no chão).

O Luan atual também está reprovado: rosto-base de adulto, rugas de adulto, pescoço em coluna, cabelo errado. **Ele vai ser refeito 100%, do zero.**

## 2. Regra zero: gente nunca é feita por código nem por primitiva

- **Todo humano do jogo é MetaHuman.**
  - Pode ser MetaHuman Creator, corpo paramétrico, ou Mesh to MetaHuman a partir de FaceBuilder ou escultura.
  - A outra opção é um personagem profissional do Fab, com licença conferida, sem cláusula NoAI, e passado para o rig do MetaHuman.
- **Proibido:**
  - ProceduralMesh, DynamicMesh ou Geometry Script para corpo, cabeça, rosto, cabelo ou roupa de gente;
  - formas básicas da engine (cubo, esfera, cilindro, cone, plano) em qualquer pessoa;
  - "olho de esfera", "cabelo de plano", "boca de polígono".
- **Se o MetaHuman travar,** encerre com "PENDENTE:" dizendo o que falta. Exemplos: login da Epic, termos aceitos, serviço de textura ou rig fora do ar. Nunca caia para gente feita à mão.
- **Provisório permitido:** um MetaHuman preset genérico com a roupa base, marcado "PROVISÓRIO" na receita. Nunca um boneco de primitiva. Provisório não entra em foto de revisão.
- **Prova:** `python Scripts/auditar_humanos.py --json Saved/Review/<data>/auditoria_humanos.json`.
  - Tem que dar LIMPO.
  - O que ele acusar (código que monta gente, personagem com forma básica) sai do projeto, não ganha exceção.
  - Exceção só existe para efeito que não é pessoa, como os olhos da Sombra no céu. Precisa de ADR e do sim do autor.

## 3. A aparência vem da obra

- **O Luan aos 13 anos tem o desenho perfeito:** o render das quatro vistas e o close.
  - Ele segue o fator 3 do `PROMPT_PERSONAGENS.md`: ficha de medidas, FaceBuilder com as quatro vistas, Mesh to MetaHuman, e medir até passar.
  - Nada do Luan antigo é reaproveitado: nem rosto, nem groom, nem material, nem malha.
- **Os outros personagens:** a aparência está nos capítulos e na Bíblia.
  - Antes de modelar qualquer pessoa, leia tudo e escreva `docs/personagens/FICHAS.md` com uma ficha por personagem.
  - Cada traço vem com a citação literal e o capítulo de onde saiu.
- **A capa** é referência para o Luan adulto, a garota ruiva e o Mateus.

**Modelo de ficha:**

```
## Nome (idade em 2017 / idade em 2036)
Papel na história:
Altura e corpo: corpo padrão + variante (corpos_padrao.json), altura em cm
Pele: tom, subtom, marcas (cicatriz, sardas, tatuagem), estado (cansado, saudável)
Rosto: formato, olhos (forma e cor), nariz, boca, queixo, orelhas
Cabelo: tipo, cor, corte, comprimento por região
Sobrancelha, barba e pelos:
Roupa por capítulo:
Como a obra descreve (citações literais com capítulo):
Bonito ou acabado na história? (o texto diz):
O que a obra não define e o autor precisa decidir (3 opções em foto):
```

- O que a obra não diz, você **não inventa sozinho**. Proponha 3 opções em foto lado a lado e o autor escolhe.
- Ficha aprovada pelo autor vira a receita do personagem (`Content/.../Receitas/`). A receita guarda corpo, variante, altura, mistura do rosto, groom, pele, olhos e roupa.

## 4. O padrão: bonito, proporcional, simétrico e uniforme

**Bonito** quer dizer bem feito e crível; não é idealizado.
- Quem a obra descreve como bonito tem de ser bonito de verdade.
- Quem a obra descreve como acabado fica acabado com o mesmo capricho técnico.
- Sinais de "bem feito":
  - pele com poro e variação, nada de cera;
  - olho úmido com brilho de luz;
  - cílios e sobrancelha em fios;
  - cabelo com volume e fios soltos;
  - dentes e língua na boca;
  - pescoço que nasce do tronco, sem emenda;
  - mãos com dedos e unhas.

**Proporcional:**
- Cada corpo bate com o padrão dele (garoto de 13–14, mulher, homem) e a variante da ficha.
- `medir_corpo.py` e `medir_esqueleto.py` dizem DENTRO DO PADRÃO.
- A altura vem da ficha.

**Simétrico:**
- Malha e mistura de rosto simétricas.
- Assimetria só a natural (até 2% em olhos e boca no `medidas_rosto.py`, até 1% entre os ossos de esquerda e direita) ou a que a ficha pede (nariz quebrado, cicatriz).

**Uniforme:** o elenco inteiro sai do mesmo processo e da mesma qualidade.
- Todos MetaHuman.
- Principais com cabelo em fios e a maior resolução de textura que a montagem oferece.
- Mesma escala (1 unidade = 1 cm).
- Mesmo provador e mesma luz para julgar.
- Figurante usa LOD e variação de receita. Nunca outro processo.

**Tiers do elenco:**

| Tier | Quem | Exigência |
|---|---|---|
| Principal | Luan e quem tem close e fala longa | Ficha completa, rosto medido quando houver desenho, aprovação do autor em foto |
| Secundário | Fala curta, aparece de perto | Ficha completa, receita própria, aprovação do autor |
| Figurante | Rua, público, mercadinho | Receitas variadas a partir das fichas da Bíblia; nenhum rosto repetido lado a lado |

**Menores de idade** (o Luan com 13 anos e outras crianças): corpo e rosto da idade, sempre revisados vestidos, nada que sexualize. Adultos são revisados com roupa neutra justa.

## 5. Antes de julgar qualquer pessoa: arrume o palco

1. **Exposição:** ajuste a exposição da cena e o `r.EyeAdaptation.CachedLightingPreExposure` até o aviso sumir. Não esconda o aviso.
2. **Céu:** onde há Sky Light com captura em tempo real, ponha SkyAtmosphere ou desligue a captura em tempo real (interiores).
3. **Câmera:** a câmera não entra na cabeça de ninguém. Use colisão de câmera, distância mínima e esconder a própria cabeça quando a câmera for subjetiva.
4. **Interface:** textos com acento e caixa alta corretos; aviso de interação sem repetição.
5. **Provador** (`L_Provador`):
   - fundo cinza 18%;
   - luz de estúdio de três pontos;
   - e a sala do cobogó do render, para comparar o Luan.
6. **Realidade 2 desligada** nas revisões de personagem. O preto e branco esconde erro de pele e cor.

## 6. O processo de cada pessoa

1. Ficha lida da obra, com citações, e aprovada pelo autor.
2. Corpo: padrão, variante e altura, medidos.
3. Rosto:
   - Luan: pela ficha de medidas.
   - Outros: mistura por região dos presets que mais se aproximam da ficha. Fotografe 3 opções para o autor.
4. Pele, olhos, dentes, cabelo, sobrancelha e pelos, pela ficha.
5. Roupa em camadas, pelo capítulo (fator 2 do `PROMPT_PERSONAGENS.md`).
6. **Prova no provador:**
   - giro de 360°;
   - close de rosto de frente, perfil e três quartos;
   - corpo inteiro com régua de altura;
   - as tabelas das réguas;
   - a auditoria LIMPA;
   - `/revisao-aaa` com parecer APROVADO.
7. **Foto de elenco:** todos que já existem lado a lado no provador, com régua de 0 a 200 cm, para conferir altura, proporção e uniformidade.

## 7. O Luan, refeito do zero

- Apague da receita tudo do Luan antigo. Comece pelo fator 3 do `PROMPT_PERSONAGENS.md`:
  1. fichas de medida do render;
  2. FaceBuilder com as quatro vistas;
  3. Mesh to MetaHuman;
  4. corpo do garoto de 13–14 anos;
  5. groom curto penteado para a frente, com orelhas de abano à mostra;
  6. a farda com a gola canelada.
- **Metas:**
  - identidade até 3% por medida e 2% de média;
  - expressão até 6%;
  - pele até Delta E 5.
- **Expressão de espanto de criança:** sem as rugas de adulto. Os mapas de ruga ficam quase zerados para 13 anos.
- Só vira "o Luan" com o sim do autor nas três vistas lado a lado com o render.

## 8. Regras de trabalho

- Um personagem por vez. Comece pelo Luan; o resto do elenco só depois dele aprovado.
- Nunca diga "pronto" sem: auditoria LIMPA, réguas DENTRO ou PASSOU, parecer APROVADO e o sim do autor nos principais.
- Número antes e depois de cada ajuste.
- Não edite referências, fichas de medida, `corpos_padrao.json` nem as réguas.
- Nada de Mixamo, nada oriental.
- Se algo exige gente (escultor, FaceBuilder, fotos), diga cedo.

## 9. Sua primeira resposta

1. A auditoria (`auditar_humanos.py`) do projeto como está, com a lista do que sai.
2. O conserto do palco (seção 5), com foto do provador sem aviso vermelho.
3. A lista de personagens que aparecem nos capítulos, com o tier de cada um e quantas fichas já dá para preencher só com a obra.
4. As fichas dos três primeiros personagens depois do Luan, com citações e o que falta o autor decidir.
5. O plano do Luan do zero, passo a passo, e o que o autor precisa fornecer.

Depois faça o palco e o Luan, até o parecer aprovado e o sim do autor, ou até um "PENDENTE:" honesto.
