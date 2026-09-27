# Projeto Integrador I — passo a passo

## Arquivos desta pasta

| Arquivo | Para que serve |
|---|---|
| `Relatorio_Projeto_Integrador_GTI.docx` | Relatório no modelo da faculdade. Amarelo = você preenche. |
| `Kit_Projeto_Integrador.xlsx` | Planilha de trabalho: chamados, matriz de prioridade, contas do AD e resultados já calculados. |
| `Checklist_Acessos.docx` | Checklist de admissão, mudança de função e desligamento. Imprima e use. |
| `exportar_contas_ad.ps1` | Exporta contas habilitadas sem logon há mais de 90 dias. Só leitura. |
| `banco_chamados.sql` | Tabelas e consultas SQL para a parte de Banco de Dados (SQLite). |

## Dia 0 — hoje (30 min)

1. Confira no Portal do Aluno o prazo de entrega. Turma ímpar = setembro; se for isso, o prazo é esta semana.
2. Peça autorização ao seu gestor com uma frase simples: "Vou usar o levantamento de chamados e a revisão de contas do AD como projeto da faculdade, com dados anonimizados. Posso tirar prints sem nomes?"
3. Peça ao RH a lista de desligados dos últimos 3 a 6 meses (só login e data).

## Dia 1 — levantamento (2 h)

1. Exporte do sistema de chamados os tickets das últimas 2 a 4 semanas. Sem sistema? Use seu histórico de e-mail/WhatsApp de atendimento.
2. Cole no `Kit_Projeto_Integrador.xlsx`, aba **Chamados**, com Período = `Antes`. Apague a linha verde de exemplo.
3. Tire nomes, logins e nome da empresa da descrição.
4. Classifique cada chamado: Tipo ITIL, Categoria, Impacto e Urgência. A prioridade aparece sozinha.
5. Rode o `exportar_contas_ad.ps1` numa máquina com RSAT. Cole o `contas_inativas.csv` na aba **Contas_AD** e a lista do RH na aba **Desligados_RH**. A coluna "Desligado segundo o RH?" marca SIM em vermelho.

## Dia 2 — IA e banco de dados (1 h 30)

1. **IA:** copie 20 a 30 descrições já anonimizadas e use este prompt em qualquer IA generativa:

   ```
   Classifique cada chamado de suporte de TI abaixo em UMA destas categorias:
   Senha / conta bloqueada; Criação de usuário (AD/WMS); Alteração de perfil de acesso;
   Desligamento / revogação; WMS indisponível / lento; Coletor / leitor sem conexão;
   Impressora de etiqueta; Integração SAP / interface; Rede / Wi-Fi;
   Estação de trabalho / periférico; Falha recorrente (causa raiz); Outros.
   Responda só com uma linha por chamado, no formato: número;categoria

   1. <descrição>
   2. <descrição>
   ```

   Cole as respostas na coluna "Categoria sugerida pela IA". A coluna ao lado diz se ela acertou.
2. **Banco de dados:** instale o DB Browser for SQLite (gratuito), crie um banco novo, rode o bloco `CREATE TABLE` do `banco_chamados.sql`, importe os CSVs e rode as consultas. Tire print de 2 consultas com resultado.

## Dias 3 a 7 — aplicação

1. Use a matriz de prioridade para classificar os chamados novos e lance-os na aba Chamados com Período = `Depois`.
2. Use o `Checklist_Acessos.docx` impresso em toda admissão ou desligamento que aparecer.
3. Desabilite (com aval do gestor) as contas marcadas SIM e registre na coluna "Ação tomada".

Se o prazo for esta semana, encurte a aplicação para 2 ou 3 dias e escreva isso no relatório. Período curto é limitação, não defeito, desde que seja honesto.

## Fotos (mínimo 3, tire 5)

1. Aba Chamados preenchida (sem dados pessoais).
2. Matriz de prioridade.
3. Checklist impresso preenchido (matrícula tapada).
4. Print da consulta SQL no DB Browser.
5. Aba Resultados.

Borre com a ferramenta de recorte do Windows (caneta) ou qualquer editor antes de colar no relatório.

## Fechar o relatório (1 h)

1. Aba **Resultados** → copie os números para a seção 5 do relatório.
2. Preencha datas na tabela de etapas, período, turma e prazo.
3. Escreva 1 ou 2 frases suas na conclusão. É o trecho que o professor lê procurando a sua voz.
4. Apague as instruções em cinza e tire o fundo amarelo (Página Inicial > Sombreamento > Sem cor).
5. Arquivo > Salvar como > PDF. Envie na plataforma e guarde o comprovante.

## Apresentação ao orientador (5 minutos, 15% da nota)

1. **Problema (1 min):** "No armazém, tudo chega como urgente. Sem separar incidente de requisição, não dá para priorizar o que para a expedição. E conta de ex-funcionário ativa no AD é risco de acesso."
2. **O que fiz (2 min):** levantamento em planilha e banco SQLite, matriz impacto × urgência (ITIL 4), checklist de acessos (ISO 27002: 5.16 identidade, 5.18 direitos de acesso, 5.11 devolução de ativos), IA para sugerir categoria com conferência humana.
3. **Resultado (1 min):** dois ou três números da aba Resultados. Exemplo de frase: "encontrei X contas ativas de desligados; Y foram desabilitadas".
4. **Disciplinas (1 min):** uma frase para cada uma das 5 (está na conclusão do relatório).

Perguntas prováveis e respostas curtas:

- *"Qual a diferença entre incidente e problema?"* Incidente é restaurar o serviço rápido; problema é achar a causa raiz de incidentes que se repetem.
- *"Por que 90 dias e não 30?"* Porque o `LastLogonDate` replica com atraso de até 14 dias entre controladores, e há afastamentos e férias.
- *"Por que desabilitar e não excluir?"* Excluir apaga o SID e a trilha de auditoria; desabilitar corta o acesso e mantém o histórico.
- *"A IA acertou quanto?"* O percentual da aba Resultados, e a conclusão de que ela acelera mas precisa de conferência.
