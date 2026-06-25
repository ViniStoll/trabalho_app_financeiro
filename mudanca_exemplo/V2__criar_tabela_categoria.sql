-- ============================================================
-- Migracao V2 - Criacao da tabela de categorias
--
-- Esta e a alteracao de BANCO que o professor pede na hora
-- (criar uma tabela de categoria simples). A tabela fica vazia.
--
-- O Flyway aplica SOMENTE esta migracao nova, sem apagar/recriar
-- o banco. A tabela 'lancamento' e seus dados continuam intactos.
--
-- Para usar: copie este arquivo para db/migrations/, faca commit
-- e push no SEU computador.
-- ============================================================

CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);
