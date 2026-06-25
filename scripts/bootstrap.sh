#!/bin/bash
# ============================================================
# UM comando: baixa o projeto do GitHub e sobe a HOMOLOGACAO.
# (A producao e criada depois, com o subir_producao.sh.)
#
# Rodar direto do GitHub:
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

echo ">>> Baixando o projeto do GitHub..."
rm -rf "$DEST"
git clone "$REPO_URL" "$DEST"

echo ">>> Subindo a Homologacao..."
bash "$DEST/scripts/subir_homologacao.sh"
