# Projeto Integrador I: passo a passo

O projeto está pronto em **cenário simulado**, com todos os dados fictícios, como o manual permite ("situação prática real ou simulada"). O relatório declara isso na Justificativa e nos Resultados. Não apague esses trechos.

## Arquivos desta pasta

| Arquivo | O que é |
|---|---|
| `Relatorio_Projeto_Integrador_GTI.docx` | Relatório completo, com 4 figuras. Falta preencher só o que está em amarelo. |
| `Kit_Projeto_Integrador.xlsx` | Planilha com os 127 chamados fictícios, a matriz, as contas do AD, a lista do RH e os resultados calculados por fórmula. |
| `banco_chamados_simulado.db` | Banco SQLite com as mesmas tabelas, pronto para abrir no DB Browser for SQLite. |
| `banco_chamados.sql` | Criação das tabelas e consultas usadas. |
| `Checklist_Acessos.docx` | Checklist de admissão, mudança de função e desligamento. |
| `exportar_contas_ad.ps1` | Script de exportação de contas inativas do AD (somente leitura). |
| `figuras/` | As 4 imagens do registro fotográfico. |

## O que você precisa fazer (cerca de 1 hora)

1. **Prazo:** confira no Portal do Aluno. Turma ímpar = setembro, ou seja, esta semana.
2. **Relatório:** preencha nome, turma, período e prazo (os campos em amarelo). Depois tire o fundo amarelo em Página Inicial > Sombreamento > Sem cor.
3. **Leia o relatório inteiro uma vez.** Na apresentação, o professor vai perguntar sobre ele. Troque por palavras suas qualquer frase que você não falaria.
4. **Abra os arquivos no seu computador** (15 min). Abra a planilha, vá à aba Resultados e mude uma célula de Impacto na aba Chamados para ver a prioridade mudar. Abra o `.db` no DB Browser for SQLite (gratuito) e rode a consulta do JOIN. Se quiser, tire seus próprios prints e troque pelas figuras do relatório.
5. **Salve em PDF** (Arquivo > Salvar como > PDF), envie na plataforma e guarde o comprovante.

## Apresentação ao orientador (5 min, 15% da nota)

1. **Problema (1 min):** "No armazém, tudo chega como urgente. Sem separar incidente de requisição, não dá para priorizar o que para a expedição. E conta de ex-funcionário ativa no AD é risco de acesso."
2. **Por que simulado (20 s):** "Chamados e contas têm dado pessoal, protegido pela LGPD. Montei um cenário fictício com base na rotina real de suporte, como o manual permite."
3. **O que fiz (2 min):**
   - Montei a base em planilha e em SQLite.
   - Classifiquei os chamados pelo ITIL 4 e criei a matriz impacto × urgência.
   - Fiz o checklist de acessos com base na ISO 27002 (5.16, 5.18, 5.11).
   - Testei a IA na classificação.
   - Cruzei as contas do AD com o RH por meio de JOIN.
4. **Resultados (1 min):**
   - O tempo dos chamados P1 e P2 caiu de 88 para 55 minutos, mas o tempo médio geral ficou igual, porque os P3 e P4 passaram a esperar mais. A matriz redistribui a fila, não cria capacidade.
   - A IA acertou 27 de 30 e errou só nas descrições ambíguas.
   - 9 das 42 contas inativas eram de ex-colaboradores.
5. **Disciplinas (40 s):** uma frase para cada uma, como está na conclusão.

## Perguntas prováveis

- *"Os números provam que funciona?"* Não. No período "Depois" eu assumi uma redução de cerca de 30% nos chamados críticos. O projeto mostra o método de medir, e o próximo passo seria aplicar com dados reais.
- *"Qual a diferença entre incidente e problema?"* Incidente é restaurar o serviço rápido. Problema é achar a causa raiz de incidentes que se repetem.
- *"Por que 90 dias e não 30?"* O LastLogonDate replica com atraso de até 14 dias entre controladores de domínio, e há férias e afastamentos.
- *"Por que desabilitar e não excluir a conta?"* Excluir perde o histórico e a trilha de auditoria. Desabilitar corta o acesso e mantém o registro.
- *"Onde entra COBIT?"* No DSS02 (requisições e incidentes) e no DSS05 (serviços de segurança). O COBIT diz o que precisa ser governado, e o ITIL diz como operar.
