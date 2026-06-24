-- ============================================================
-- Migracao V1 - Schema inicial do sistema financeiro
-- O Flyway executa este arquivo apenas UMA vez e guarda o
-- registro na tabela flyway_schema_history. Assim o banco
-- fica versionado (cada alteracao vira um novo arquivo V2, V3...).
-- ============================================================

-- 1. Tabela de usuarios (login do sistema)
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    situacao VARCHAR(20) NOT NULL
);

-- 2. Tabela de lancamentos financeiros
CREATE TABLE lancamento (
    id SERIAL PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    data_lancamento DATE NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    tipo_lancamento VARCHAR(20) NOT NULL, -- 'Receita' ou 'Despesa'
    situacao VARCHAR(20) NOT NULL         -- 'Pago' ou 'Pendente'
);

-- 3. Usuario padrao para conseguir entrar no sistema
INSERT INTO usuario (nome, login, senha, situacao)
VALUES ('Administrador', 'admin', '123456', 'Ativo');

-- 4. Alguns lancamentos de exemplo para a tela ja vir com dados
INSERT INTO lancamento (descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES
('Salário', '2026-03-05', 4500.00, 'Receita', 'Pago'),
('Conta de Luz', '2026-03-10', 150.50, 'Despesa', 'Pago'),
('Conta de Água', '2026-03-12', 80.00, 'Despesa', 'Pago'),
('Aluguel', '2026-03-15', 1200.00, 'Despesa', 'Pago'),
('Supermercado', '2026-03-18', 600.00, 'Despesa', 'Pago'),
('Venda de Bicicleta', '2026-03-20', 850.00, 'Receita', 'Pago'),
('Internet', '2026-03-22', 110.00, 'Despesa', 'Pendente'),
('Manutenção Carro', '2026-03-25', 450.00, 'Despesa', 'Pendente'),
('Rendimento Investimento', '2026-03-26', 120.00, 'Receita', 'Pago'),
('Jantar Fora', '2026-03-28', 180.00, 'Despesa', 'Pendente');
