#!/bin/bash
# ============================================================
# Passo 2 da apresentacao: montar do zero os ambientes de
# Homologacao e Producao, cada um em seu proprio container.
#
# Este script faz TODA a infraestrutura de forma automatizada:
#  - instala o Docker (se preciso)
#  - libera as portas no firewall
#  - constroi a imagem da aplicacao
#  - sobe os 2 containers (homolog e prod)
#  - aplica as migracoes do banco (Flyway) nos dois
# ============================================================
set -e
source "$(dirname "$0")/config.sh"

# 1. Instala o Docker, caso ainda nao esteja instalado
if ! command -v docker >/dev/null 2>&1; then
    echo ">>> Docker nao encontrado. Instalando..."
    curl -fsSL https://get.docker.com | sudo sh
fi

# 2. Garante que o codigo do projeto esta atualizado com o GitHub
echo ">>> Atualizando o codigo a partir do GitHub..."
cd "$PROJETO_DIR"
git fetch origin
git reset --hard origin/main

# 3. Libera as portas dos ambientes no firewall (ufw)
echo ">>> Liberando as portas $PORTA_HOMOLOG e $PORTA_PROD no firewall..."
sudo ufw allow "$PORTA_HOMOLOG"/tcp 2>/dev/null || true
sudo ufw allow "$PORTA_PROD"/tcp 2>/dev/null || true

# 4. Cria a rede Docker (se ainda nao existir)
sudo docker network create "$REDE" 2>/dev/null || true

# 5. Constroi a imagem da aplicacao
echo ">>> Construindo a imagem '$IMAGEM' (pode demorar na primeira vez)..."
sudo docker build -t "$IMAGEM" "$PROJETO_DIR"

# 6. Sobe o container de HOMOLOGACAO
echo ">>> Subindo o ambiente de HOMOLOGACAO (porta $PORTA_HOMOLOG)..."
sudo docker rm -f "$CONT_HOMOLOG" 2>/dev/null || true
sudo docker run -d --name "$CONT_HOMOLOG" --network "$REDE" -p "$PORTA_HOMOLOG":8000 "$IMAGEM"

# 7. Sobe o container de PRODUCAO
echo ">>> Subindo o ambiente de PRODUCAO (porta $PORTA_PROD)..."
sudo docker rm -f "$CONT_PROD" 2>/dev/null || true
sudo docker run -d --name "$CONT_PROD" --network "$REDE" -p "$PORTA_PROD":8000 "$IMAGEM"

# 8. Aplica as migracoes do banco (cria as tabelas e dados iniciais)
echo ">>> Aplicando migracoes do banco em HOMOLOGACAO..."
flyway_migrate "$CONT_HOMOLOG"
echo ">>> Aplicando migracoes do banco em PRODUCAO..."
flyway_migrate "$CONT_PROD"

# 9. Espera as duas aplicacoes responderem
esperar_app "$PORTA_HOMOLOG"
esperar_app "$PORTA_PROD"

# 10. Mostra o resultado
IP_VM=$(hostname -I | awk '{print $1}')
echo ""
echo "============================================================"
echo " Ambientes no ar!"
echo " Homologacao -> http://$IP_VM:$PORTA_HOMOLOG"
echo " Producao    -> http://$IP_VM:$PORTA_PROD"
echo "============================================================"
sudo docker ps
