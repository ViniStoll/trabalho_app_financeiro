#!/bin/bash
# ============================================================
# Sobe SOMENTE o ambiente de HOMOLOGACAO.
# A producao NAO e criada aqui (vem depois, com o subir_producao.sh).
#
# Faz toda a infraestrutura: instala o Docker (se preciso),
# constroi a imagem e sobe o container de homologacao com o banco.
# ============================================================
set -e
source "$(dirname "$0")/config.sh"

# 1. Instala o Docker, caso ainda nao esteja instalado
if ! command -v docker >/dev/null 2>&1; then
    echo ">>> Docker nao encontrado. Instalando..."
    curl -fsSL https://get.docker.com | sudo sh
fi

# 2. Libera a porta da homologacao no firewall
sudo ufw allow "$PORTA_HOMOLOG"/tcp 2>/dev/null || true

# 3. Cria a rede do Docker (se ainda nao existir)
sudo docker network create "$REDE" 2>/dev/null || true

# 4. Constroi a imagem da aplicacao
echo ">>> Construindo a imagem '$IMAGEM' (pode demorar na primeira vez)..."
sudo docker build -t "$IMAGEM" "$PROJETO_DIR"

# 5. Prepara o ambiente de testes (usado depois pelas atualizacoes)
echo ">>> Preparando o ambiente de testes..."
rodar_testes || true

# 6. Sobe o container de HOMOLOGACAO
echo ">>> Subindo a HOMOLOGACAO (porta $PORTA_HOMOLOG)..."
sudo docker rm -f "$CONT_HOMOLOG" 2>/dev/null || true
sudo docker run -d --name "$CONT_HOMOLOG" --network "$REDE" -p "$PORTA_HOMOLOG":8000 "$IMAGEM"

# 7. Cria o banco (aplica as migracoes)
flyway_migrate "$CONT_HOMOLOG"
esperar_app "$PORTA_HOMOLOG"

IP_VM=$(hostname -I | awk '{print $1}')
echo ""
echo "============================================================"
echo " Homologacao no ar -> http://$IP_VM:$PORTA_HOMOLOG"
echo " (A Producao ainda NAO foi criada.)"
echo "============================================================"
sudo docker ps
