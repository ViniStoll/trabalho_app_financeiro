# ZERAR A VM

echo ">>> Removendo containers, imagens, volumes e redes do Docker..."
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null
sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null
sudo docker system prune -a -f --volumes 2>/dev/null

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
