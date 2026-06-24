#!/bin/bash
# ============================================================
# Passo 1 da apresentacao: deixar a VM "zerada".
# Remove os containers, a imagem e a rede do projeto, e para a
# aplicacao antiga que rodava direto no host. No final mostra
# que nao ha nada criado no Docker.
# ============================================================
source "$(dirname "$0")/config.sh"

echo ">>> Parando e removendo os containers do projeto..."
sudo docker rm -f "$CONT_HOMOLOG" "$CONT_PROD" 2>/dev/null || true

echo ">>> Removendo a imagem da aplicacao..."
sudo docker rmi "$IMAGEM" 2>/dev/null || true

echo ">>> Removendo a rede docker do projeto..."
sudo docker network rm "$REDE" 2>/dev/null || true

echo ">>> Limpando imagens, caches e volumes nao utilizados..."
sudo docker system prune -a -f 2>/dev/null || true

echo ">>> Parando a aplicacao antiga que rodava direto no host (porta 8000)..."
sudo pkill -f "trabalho_app_financeiro/venv" 2>/dev/null || true

echo ""
echo ">>> Estado atual do Docker (deve estar vazio):"
echo "--- Containers ---"
sudo docker ps -a 2>/dev/null || echo "(docker nao instalado)"
echo "--- Imagens ---"
sudo docker images 2>/dev/null || echo "(docker nao instalado)"
