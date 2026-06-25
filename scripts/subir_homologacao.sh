# Sobe somente o ambiente de homologacao.
set -e
source "$(dirname "$0")/config.sh"

# Instala o Docker
if ! command -v docker >/dev/null 2>&1; then
    echo ">>> Docker nao encontrado. Instalando..."
    curl -fsSL https://get.docker.com | sudo sh
fi

# Libera a porta da homologacao no firewall
sudo ufw allow "$PORTA_HOMOLOG"/tcp 2>/dev/null || true

# Cria a rede do Docker
sudo docker network create "$REDE" 2>/dev/null || true

# Constroi a imagem da aplicacao
echo ">>> Construindo a imagem '$IMAGEM' (pode demorar na primeira vez)..."
sudo docker build -t "$IMAGEM" "$PROJETO_DIR"

# Prepara o ambiente de testes
echo ">>> Preparando o ambiente de testes..."
rodar_testes || true

# Sobe o container de homologacao
echo ">>> Subindo a HOMOLOGACAO (porta $PORTA_HOMOLOG)..."
sudo docker rm -f "$CONT_HOMOLOG" 2>/dev/null || true
sudo docker run -d --name "$CONT_HOMOLOG" --network "$REDE" -p "$PORTA_HOMOLOG":8000 "$IMAGEM"

# Cria o banco 
flyway_migrate "$CONT_HOMOLOG"
esperar_app "$PORTA_HOMOLOG"

IP_VM=$(hostname -I | awk '{print $1}')
echo ""
echo "============================================================"
echo " Homologacao no ar -> http://$IP_VM:$PORTA_HOMOLOG"
echo "============================================================"
sudo docker ps
