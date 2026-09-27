# NOVAMENTE · Luta no Largo (Unreal Engine 5)

Vertical slice do jogo NOVAMENTE em Unreal Engine 5. A luta é a do protótipo: Luan contra Igor "O Relógio", à noite e na chuva, num octógono montado no Largo de São Sebastião, em frente ao Teatro Amazonas (Manaus, 2017).

O estilo visual segue Ghost of Tsushima: luz, vento, textura, sombra e peso da animação. O lugar, as pessoas e a história são de Manaus. Nada de Japão.

## Estado atual (leia primeiro)

- Todo o código foi escrito numa máquina na nuvem sem Unreal e sem placa de vídeo. **Nada foi compilado ainda.** A primeira tarefa no seu PC é compilar e corrigir o que a sua versão da engine (5.8) reclamar. O `CLAUDE.md` explica esse ciclo para o Claude rodando no seu PC.
- A lógica da luta é uma porta fiel do protótipo "Luta no Largo", com os mesmos números convertidos para centímetros.
- O cenário gerado por script é um **blockout**: caixas e esferas no lugar e na escala certos, com luz, neblina e materiais procedurais (pedra portuguesa em ondas, azulejos da cúpula, alambrado). A arte final entra nas fases do `Docs/ROADMAP.md`.
- Sem MetaHuman e sem montagens, os lutadores são cápsulas invisíveis que lutam de verdade (a lógica roda sem animação). Com as malhas e montagens, tudo se liga pelos campos descritos abaixo.

## O que tem aqui

```
novamente-ue5/
  Plugins/NovamenteCombat/        plugin C++ (copie para <SeuProjeto>/Plugins/)
    Source/NovamenteCombat/
      NovCombatTypes              golpes, zonas, resultado do golpe, hematomas, fases da luta
      NovMoveSet                  Data Asset com a tabela de golpes (tempos, dano, alcance, montagem)
      NovCombatComponent          preparação, janela ativa, recuperação, combos, buffer, guarda, esquiva, Motion Warping
      NovDamageComponent          vida por zona, fôlego, 1ª Lei (dor atrasada), Lei de Goggins (hematomas)
      NovFighterCharacter         lutador: movimento em relação ao adversário, reações com física, suor, vapor, queda
      NovFightGameMode            rounds, relógio, quedas, nocaute, decisão, Visão do Caos, hit-stop, falas, save
      NovSombraSubsystem          a Sombra, a 2ª Lei, Realidade 2, relâmpago, coração, sussurros, parâmetros de tela
      NovIgorBrainComponent       IA do Igor (contra-ataque, lê o golpe, castiga golpe no vazio, tique-taque)
      NovFightCamera              câmera de transmissão com o teatro ao fundo
      NovPlayerController         controles (teclado e controle) criados em tempo de execução
      NovHUDWidget                interface montada em C++ (barras, relógio, legendas, abertura, pausa, fim)
      NovSaveGame                 hematomas e o que o jogador já viu, entre lutas
      NovamenteSettings           Configurações do Projeto > Game > Novamente
  Scripts/
    setup_novamente.py            cria materiais, coleção de parâmetros, som abafado e ajusta Config/*.ini
    build_largo.py                monta o mapa L_Largo (blockout com luz e clima)
    capture_review.py             tira as fotos de revisão sempre dos mesmos ângulos
  Shaders/
    PP_Novamente_Custom.hlsl      pós-processamento: Sombra (duotone + garras), túnel, pulso, Caos, Realidade 2, grão
    M_SombraEyes_Custom.hlsl      olhos amarelos da Sombra no céu
    Bruises_Custom.hlsl           hematomas que envelhecem e corte no rosto
  Docs/ROADMAP.md                 portões de revisão R0 a R8, orçamento de desempenho, equipe
  CLAUDE.md                       instruções para o Claude no seu PC (ciclo compilar, fotografar, comparar, corrigir)
```

## Requisitos

- Unreal Engine 5.8 (o código usa APIs presentes desde a 5.4).
- Visual Studio 2022 com "Desenvolvimento de jogos com C++" e o Windows SDK. Ou Rider.
- Plugins do projeto: Enhanced Input, Motion Warping, Niagara (o plugin liga sozinho) e **Python Editor Script Plugin** (Editar > Plugins).
- Placa de vídeo com Lumen e MetaHuman confortáveis: RTX 3070 / RX 6800 ou melhor, 8 GB de VRAM no mínimo (12 GB recomendados). 32 GB de RAM (64 GB para MetaHuman Animator). SSD NVMe.

## Instalação

1. Copie `Plugins/NovamenteCombat` para `<SeuProjeto>/Plugins/NovamenteCombat`.
2. Feche o editor e compile. Pelo terminal (troque os caminhos e o nome do projeto):
   ```
   "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" NovamenteEditor Win64 Development -Project="C:\Projetos\Novamente\Novamente.uproject" -WaitMutex
   ```
   Ou abra o `.uproject` e aceite "reconstruir módulos". Se o projeto for só Blueprint, funciona do mesmo jeito com o Visual Studio instalado.
3. Prepare o projeto (materiais, coleção de parâmetros, som abafado, Config/*.ini):
   ```
   "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "C:\Projetos\Novamente\Novamente.uproject" -run=pythonscript -script="C:\caminho\novamente-ue5\Scripts\setup_novamente.py"
   ```
   O script mostra no log cada linha que mudou nos `.ini`. Ele liga Lumen, sombras virtuais, TSR, cache de PSO e o Enhanced Input.
4. Monte o Largo:
   ```
   ...UnrealEditor-Cmd.exe "...Novamente.uproject" -run=pythonscript -script="C:\caminho\novamente-ue5\Scripts\build_largo.py"
   ```
5. Abra `/Game/Novamente/Maps/L_Largo` e aperte Play. Qualquer golpe sai da abertura.

## Controles

| Ação | Teclado | Controle (Xbox / PlayStation) |
|---|---|---|
| Andar (trás + soco = golpe no corpo) | W A S D | analógico esquerdo |
| Jab / Direto / Gancho / Uppercut | J / K / L / I | X / Y / B / RB (Quadrado / Triângulo / Círculo / R1) |
| Chute baixo / alto | U / O | A / LB (X / L1) |
| Guarda (segurar) | Shift | LT (L2) |
| Esquiva de pêndulo | Espaço (+ lado) | RT (R2) |
| Ouvir a Sombra (barra cheia) | Q | R3 |
| Realidade 2 | R | D-pad cima |
| Pausa e controles | Esc / H | Start / Options |
| Tela final: revanche / curar e lutar | J / K | X / Y |

Soco com o Igor caído e perto vira ground and pound. Esquiva no último instante antes do golpe dele abre a Visão do Caos (câmera lenta, próximo golpe com 1,7 vez o dano).

## Ligando os personagens (MetaHuman)

1. **Criar o Luan e o Igor.** MetaHuman Creator (dentro da engine desde a 5.6). Para parecer com a capa e com o render 3D, use Mesh to MetaHuman a partir de um escaneamento ou de um modelo esculpido em cima das referências.
   - Luan adulto: pele parda clara, quase branca; 1,63 m; magro e seco; cabelo escuro bagunçado; olhos cor de oliva; rosto cansado. Camisa branca (pijama) que vira a farda: gola canelada amarela e azul.
   - Igor: 1,72 m; pele morena; cabeça raspada; cara fechada; bandagem verde; bermuda preta.
2. **Blueprint do lutador.** Crie `BP_Luan` filho de `NovFighterCharacter`. Em "Mesh" coloque o corpo do MetaHuman. Adicione os outros componentes do MetaHuman (Face, Torso, Legs, Feet, cabelo) como filhos da malha, com o mesmo esqueleto seguindo o corpo (Leader Pose ou Live Retarget, como no Blueprint que o MetaHuman gera). O componente do rosto precisa se chamar `Face` (ou troque `Face Component Name`).
   - `Fighter Id`: `Luan` e `Igor`. O modo de jogo encontra os dois no mapa por esse nome; se não achar, cria a partir de `Player Fighter Class` e `Opponent Fighter Class`.
   - `Reach Scale`: 0,96 para o Luan e 1,01 para o Igor (altura dividida por 1,70 m, como no protótipo).
   - O atraso da dor do jogador (1ª Lei) é aplicado pelo modo de jogo: 0,75 s no Luan, 0,5 s no Igor.
3. **Material do rosto.** No material do rosto do MetaHuman, adicione a função `MF_NovamenteFerimentos` (criada pelo setup): ligue a UV do rosto, e misture `BaseColor = lerp(pele, Hematomas.rgb, Hematomas.a)`. Use a saída `Suor` para baixar a rugosidade e subir o especular (pele molhada). O lutador escreve os parâmetros `Sweat`, `Bruise0..7`, `BruiseAge0..7` e `Cut` em tempo real.
   - Os pontos dos hematomas (maçãs do rosto, sobrancelhas, olhos, boca) estão em `NovDamageComponent::AddBruise`, em coordenadas de UV. Ajuste para a UV real da cabeça do MetaHuman olhando o resultado nas fotos de revisão.
4. **Physics Asset.** O do MetaHuman serve. A reação ao golpe usa física parcial a partir de `neck_01`, `spine_03` e `thigh_l`; a queda usa ragdoll inteiro; ao levantar, a cápsula vai até a pélvis.

## Ligando as animações

- **Locomoção.** Game Animation Sample (Motion Matching), redirecionado para o esqueleto do MetaHuman. O AnimBP lê `MoveInput` (x direita, y frente, em relação ao adversário), `IsBlocking`, `GetFightState`, `Exertion` (respiração), `Tremble` (ruído aditivo nas mãos depois da Sombra) e `GetSlipDirection` (+1 esquerda, -1 direita).
- **Golpes.** Crie um `NovMoveSet` (Data Asset), clique em "Fill With Prototype Values" e coloque uma montagem em cada golpe. A montagem é tocada na velocidade que casa com Preparação + Ativo + Recuperação, então o tempo de jogo manda, não o tamanho do clipe. Coloque uma janela de Motion Warping chamada `Strike` durante a preparação: o golpe se alinha com a cabeça, o corpo ou a coxa do adversário.
- **Reações.** `Hit Reactions` por zona, `Block Reaction`, `Get Up Montage` e `Victory Montage` no lutador. Sem elas, a física parcial já dá a reação.
- **Mocap.** Para golpes de MMA com peso real: captura com Move.ai, Rokoko ou Xsens (ou pacotes do Fab), limpeza em Control Rig, rosto com MetaHuman Animator.

## Parâmetros de tela (MPC_Novamente)

O `NovSombraSubsystem` escreve a cada quadro: `Sombra`, `SombraPresence`, `SombraColor`, `SombraEyes`, `Tunnel`, `Pulse`, `Flash`, `Desat`, `Caos`, `Chroma`, `Lightning`, `Crowd`. O pós-processamento, os olhos no céu, o céu (relâmpago) e o público podem ler qualquer um deles.

A cor da Sombra muda a cada aparição: escolhe na paleta (Configurações do Projeto > Novamente) a cor que mais briga com o matiz do lugar (`Environment Hue`), nunca repetindo a última.

## Sons

Em Configurações do Projeto > Novamente: coração, zumbido, sussurro, trovão e a mixagem abafada. No modo de jogo: sino e público. No cérebro do Igor: o tique-taque do relógio. Tudo opcional; sem som, nada quebra.

## Revisões

O ciclo é: compilar, montar, fotografar com `capture_review.py`, comparar com as referências, corrigir, fotografar de novo. Os portões R0 a R8 e o que conta como prova estão em `Docs/ROADMAP.md`. O `CLAUDE.md` diz como o Claude faz isso sozinho no seu PC.

## Problemas conhecidos

- Não compilado (ver acima). Pontos com mais chance de mudar entre versões: `UInputMappingContext::MapKey`, nomes de propriedades de pós-processamento no Python, entrada de posição do mundo em nó Custom (LWC).
- Os arquivos C++ têm acentos nos textos; estão em UTF-8 com BOM para o Visual Studio ler certo.
- A chuva (Niagara) e o público são feitos no editor; os scripts deixam o lugar e a luz prontos para eles.
