#!/bin/bash
# ============================================================
# PASSO 1 - ZERAR A VM
#
# Remove TUDO que foi criado no Docker (containers, imagens,
# volumes e redes), para a aplicacao antiga e apaga o codigo.
#
# O Docker NAO e desinstalado de proposito: assim os comandos
# 'sudo docker ps' e 'sudo docker images' continuam funcionando
# e mostram que esta tudo vazio (a prova de que a VM esta zerada).
#
# Este script nao depende de mais nada e pode ser rodado direto:
#   bash 00_limpar_vm.sh
# ============================================================

echo ">>> Removendo containers, imagens, volumes e redes do Docker..."
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null
sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null
sudo docker system prune -a -f --volumes 2>/dev/null

echo ">>> Parando a aplicacao antiga que rodava direto no host (porta 8000)..."
sudo pkill -f "trabalho_app_financeiro/venv" 2>/dev/null

echo ">>> Apagando o codigo do projeto..."
rm -rf "$HOME/trabalho_app_financeiro"

echo ""
echo "============================================================"
echo " VM zerada. Conferindo (devem estar vazios):"
echo "--- docker ps ---"
sudo docker ps
echo "--- docker images ---"
sudo docker images
echo "============================================================"
