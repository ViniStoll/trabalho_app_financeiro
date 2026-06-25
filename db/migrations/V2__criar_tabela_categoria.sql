-- ============================================================
-- Migracao V2 - Criacao da tabela de categorias
--
-- Esta e a alteracao de BANCO que sera feita durante a
-- apresentacao (o professor pede para criar uma tabela de
-- categoria simples).
--
-- IMPORTANTE: o Flyway aplica SOMENTE esta migracao nova, sem
-- apagar/recriar o banco. A tabela 'lancamento' e seus dados
-- continuam intactos - apenas a tabela nova e adicionada.
--
-- COMO USAR NA APRESENTACAO:
-- Copie este arquivo para a pasta db/migrations/ e faca o commit:
--   cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
--   git add db/migrations/V2__criar_tabela_categoria.sql
--   git commit -m "Cria tabela de categoria (migracao V2)"
--   git push
-- ============================================================

-- Tabela de categorias (bem simples, como pedido)
CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255)
);

-- Alguns registros de exemplo para aparecer na tela de Categorias
INSERT INTO categoria (nome, descricao) VALUES
('Moradia', 'Aluguel, condomínio e contas da casa'),
('Alimentação', 'Supermercado e refeições'),
('Transporte', 'Combustível, ônibus e manutenção'),
('Lazer', 'Cinema, viagens e passeios');
