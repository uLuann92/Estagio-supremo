-- Banco do Projeto Integrador (SQLite). Use no DB Browser for SQLite:
-- 1) Novo banco de dados > execute o bloco CREATE TABLE.
-- 2) Arquivo > Importar > Tabela de arquivo CSV para cada tabela
--    (chamados: salve a aba Chamados do kit como CSV; contas_ad: contas_inativas.csv, separador ";").
-- 3) Execute as consultas e tire print dos resultados (serve de foto para o relatório).

CREATE TABLE chamados (
    id               INTEGER PRIMARY KEY,
    data             TEXT,
    periodo          TEXT CHECK (periodo IN ('Antes', 'Depois')),
    setor            TEXT,
    descricao        TEXT,
    tipo_itil        TEXT CHECK (tipo_itil IN ('Incidente', 'Requisição de serviço', 'Problema')),
    categoria        TEXT,
    impacto          INTEGER CHECK (impacto BETWEEN 1 AND 3),
    urgencia         INTEGER CHECK (urgencia BETWEEN 1 AND 3),
    prioridade       TEXT,
    categoria_ia     TEXT,
    ia_acertou       TEXT,
    tempo_solucao_min INTEGER
);

CREATE TABLE contas_ad (
    SamAccountName TEXT PRIMARY KEY,
    Name           TEXT,
    LastLogonDate  TEXT
);

CREATE TABLE desligados_rh (
    login             TEXT PRIMARY KEY,
    data_desligamento TEXT
);

-- Tipos de chamado mais frequentes, antes e depois
SELECT periodo, categoria, COUNT(*) AS qtd
FROM chamados
GROUP BY periodo, categoria
ORDER BY periodo, qtd DESC;

-- Incidente x requisição x problema
SELECT periodo, tipo_itil, COUNT(*) AS qtd
FROM chamados
GROUP BY periodo, tipo_itil;

-- Tempo médio de solução por prioridade
SELECT periodo, prioridade, ROUND(AVG(tempo_solucao_min), 1) AS media_min, COUNT(*) AS qtd
FROM chamados
WHERE prioridade <> ''
GROUP BY periodo, prioridade
ORDER BY periodo, prioridade;

-- Acerto da IA na sugestão de categoria
SELECT ROUND(100.0 * SUM(categoria_ia = categoria) / COUNT(*), 1) AS acerto_pct, COUNT(*) AS conferidos
FROM chamados
WHERE categoria_ia <> '';

-- Contas ainda habilitadas de quem o RH já desligou
SELECT a.SamAccountName, a.LastLogonDate, d.data_desligamento
FROM contas_ad a
JOIN desligados_rh d ON d.login = a.SamAccountName
ORDER BY d.data_desligamento;
