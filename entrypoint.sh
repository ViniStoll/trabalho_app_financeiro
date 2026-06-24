#!/bin/bash
# ============================================================
# Script de inicializacao do container.
# Inicia o PostgreSQL e depois a aplicacao Flask.
# ============================================================

# Inicia o servico do banco de dados dentro do container
service postgresql start

# Garante que o banco 'financeiro' exista (caso ainda nao tenha sido criado).
# O "|| true" evita que o script pare caso o banco ja exista.
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='financeiro'\" | grep -q 1 || psql -c \"CREATE DATABASE financeiro;\"" || true

# Inicia a aplicacao Flask em primeiro plano (mantem o container vivo).
# O 'exec' faz o Flask virar o processo principal do container.
cd /app
exec /opt/venv/bin/python app.py
