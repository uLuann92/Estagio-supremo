# Prompt para mandar junto com o Arsenal AAA

Anexei o **Arsenal AAA**, um HTML com 212 ferramentas para fazer um jogo AAA. Se não conseguir abrir como página, leia o texto: cada item tem nome, para que serve e etiquetas. A mesma lista está em `Docs/FERRAMENTAS_AAA.md`.

## O que é

É um catálogo de referência, separado em 23 categorias (mundo, movimentação, iluminação, otimização e outras). Não é uma ordem para instalar tudo. Cada item tem quatro etiquetas:

- **Prioridade**
  - Essencial: sem isso não sai AAA, ou é o padrão da indústria para a função.
  - Recomendado: acelera muito.
  - Opcional: alternativa ou caso específico.
- **Custo**
  - Grátis.
  - Vem na Unreal: já está na engine; às vezes é só ligar o plugin.
  - Grátis limitado: versão grátis, teste ou grátis até certo faturamento.
  - Pago.
- **Tipo:** programa, recurso da Unreal, plugin, serviço, equipamento, prática.
- **NOVAMENTE:** o item já está decidido no plano do jogo (Prompt AAA+, Prompt de Personagens, roadmap).

## O que eu quero de você

1. **Auditoria.** Compare o catálogo com o projeto de verdade: `.uproject`, plugins ligados, `Config/`, pastas e o que está instalado no PC. Para cada categoria, faça uma tabela:

   | Ferramenta | Situação no projeto | O que fazer | Quem faz | Custo |
   |---|---|---|---|---|

   - Situação: em uso, falta ou não se aplica.
   - Quem faz: você, ou o autor quando for download, licença ou compra.

2. **Prioridade**, nesta ordem:
   1. o que é Essencial e tem a etiqueta NOVAMENTE e ainda falta;
   2. os outros essenciais;
   3. os recomendados, só quando resolvem um problema atual (um defeito do último parecer, um portão travado).
3. **Top 10 ações**, na ordem, cada uma ligada a um portão do plano (R0 a R8, P0 a P6, C1 a C4).

## Regras

- Não instale nem compre nada nesta primeira resposta. Entregue a auditoria e o plano. Depois do meu sim, integre um item por vez, com prova: compila e, se mudou a imagem, `/revisao-aaa`.
- Recurso "Vem na Unreal": confira se o plugin está ligado e configurado. Recurso experimental (MegaLights, Mover, Gameplay Cameras, Substrate) só entra com ADR.
- Item pago: nunca assuma que eu tenho. Liste com o preço conferido no site oficial, a alternativa grátis e o que se perde com ela.
- A lista foi feita para a Unreal 5.x. Confira o nome, o estado e a licença de cada item na 5.8 antes de recomendar. Se algo do catálogo estiver errado ou desatualizado, diga.
- Continuam valendo as regras do projeto:
  - nada de Mixamo;
  - o Lyra não é base;
  - nenhum pacote oriental;
  - GAS só por ADR.
- Mais ferramenta não é mais qualidade. Cada adição precisa de um motivo concreto no jogo.

## Sua primeira resposta

1. A auditoria por categoria.
2. As 10 ações em ordem.
3. A lista de downloads, licenças e compras para eu decidir.
4. Os plugins da Unreal que você ligaria no `.uproject` e por quê (com ADR quando precisar).
5. O que no catálogo está errado ou não serve para o NOVAMENTE.
