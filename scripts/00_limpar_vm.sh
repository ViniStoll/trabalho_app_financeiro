#!/bin/bash
# ============================================================
# PASSO 1 - LIMPEZA COMPLETA DA VM
#
# Deixa a VM totalmente zerada: remove containers, imagens e
# volumes do Docker, DESINSTALA o Docker, apaga o codigo do
# projeto e para a aplicacao antiga que rodava no host.
#
# Este script e auto-suficiente (nao depende de nenhum outro
# arquivo) e pode ser rodado direto do GitHub:
#
#   curl -fsSL https://raw.githubusercontent.com/ViniStoll/trabalho_app_financeiro/main/scripts/00_limpar_vm.sh | bash
# ============================================================

echo ">>> Removendo containers, imagens, redes e volumes do Docker..."
if command -v docker >/dev/null 2>&1; then
    sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null
    sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null
    sudo docker system prune -a -f --volumes 2>/dev/null
fi

echo ">>> Desinstalando o Docker..."
sudo systemctl stop docker docker.socket containerd 2>/dev/null
sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras >/dev/null 2>&1
sudo apt-get autoremove -y >/dev/null 2>&1
sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker

echo ">>> Parando a aplicacao antiga que rodava direto no host (porta 8000)..."
sudo pkill -f "trabalho_app_financeiro/venv" 2>/dev/null

echo ">>> Apagando o codigo do projeto..."
rm -rf "$HOME/trabalho_app_financeiro"

echo ""
echo "============================================================"
echo " VM zerada. Verificacao:"
command -v docker >/dev/null 2>&1 && echo "  docker  : AINDA instalado (!)" || echo "  docker  : nao instalado (ok)"
[ -d "$HOME/trabalho_app_financeiro" ] && echo "  codigo  : ainda presente (!)" || echo "  codigo  : removido (ok)"
echo "============================================================"
