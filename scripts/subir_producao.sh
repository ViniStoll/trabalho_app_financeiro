# Sobe o ambiente de producao.
set -e
source "$(dirname "$0")/config.sh"

# Garante que a imagem existe
if ! sudo docker image inspect "$IMAGEM" >/dev/null 2>&1; then
    echo ">>> Construindo a imagem '$IMAGEM'..."
    sudo docker build -t "$IMAGEM" "$PROJETO_DIR"
fi

# Libera a porta da producao no firewall
sudo ufw allow "$PORTA_PROD"/tcp 2>/dev/null || true
sudo docker network create "$REDE" 2>/dev/null || true

# Sobe o container de producao
echo ">>> Subindo a PRODUCAO (porta $PORTA_PROD)..."
sudo docker rm -f "$CONT_PROD" 2>/dev/null || true
sudo docker run -d --name "$CONT_PROD" --network "$REDE" -p "$PORTA_PROD":8000 "$IMAGEM"

# Cria o banco
flyway_migrate "$CONT_PROD"
esperar_app "$PORTA_PROD"

IP_VM=$(hostname -I | awk '{print $1}')
echo ""
echo "============================================================"
echo " Producao no ar -> http://$IP_VM:$PORTA_PROD"
echo "============================================================"
sudo docker ps
