#!/bin/bash
# ============================================================
# PASSO 2 - BOOTSTRAP (UM UNICO COMANDO)
#
# Monta TODO o ambiente do zero numa VM limpa:
#   1. baixa o codigo do GitHub
#   2. chama o script que instala o Docker, constroi a imagem,
#      sobe os 2 containers (homolog e prod) e aplica o banco
#
# Este script e auto-suficiente e pode ser rodado direto do
# GitHub (e o "comando que inicia o processo"):
#
#   curl -fsSL https://raw.githubusercontent.com/ViniStoll/trabalho_app_financeiro/main/scripts/bootstrap.sh | bash
# ============================================================
set -e

REPO_URL="https://github.com/ViniStoll/trabalho_app_financeiro.git"
DEST="$HOME/trabalho_app_financeiro"

# Garante que o git esteja instalado (necessario para baixar o codigo)
if ! command -v git >/dev/null 2>&1; then
    echo ">>> Instalando o git..."
    sudo apt-get update -y && sudo apt-get install -y git
fi

echo ">>> Baixando o codigo do projeto do GitHub..."
rm -rf "$DEST"
git clone "$REPO_URL" "$DEST"

echo ">>> Montando os ambientes (instala Docker, constroi e sobe homolog e prod)..."
bash "$DEST/scripts/01_montar_ambientes.sh"
