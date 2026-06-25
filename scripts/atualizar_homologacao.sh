# Atualiza o ambiente de homologacao com a versao mais nova.
set -e
source "$(dirname "$0")/config.sh"

# Pega a versao mais nova do codigo no GitHub
echo ">>> Atualizando o codigo a partir do GitHub..."
cd "$PROJETO_DIR"
git fetch origin
git reset --hard origin/main

# Roda os testes + qualidade. Se falhar, cancela a atualizacao.
echo ">>> Rodando os testes e a analise de qualidade..."
if ! rodar_testes; then
    echo ""
    echo "############################################################"
    echo " TESTES/QUALIDADE FALHARAM! Atualizacao da HOMOLOGACAO cancelada."
    echo "############################################################"
    exit 1
fi
echo ">>> Tudo passou. Seguindo com a atualizacao..."

# Aplica somente as migracoes novas do banco
echo ">>> Aplicando migracoes do banco em HOMOLOGACAO..."
flyway_migrate "$CONT_HOMOLOG"

# Copia o codigo novo da aplicacao para dentro do container
echo ">>> Atualizando o codigo da aplicacao no container..."
sudo docker cp "$PROJETO_DIR/app.py" "$CONT_HOMOLOG":/app/app.py

# Reinicia a aplicacao
echo ">>> Reiniciando a aplicacao..."
sudo docker restart "$CONT_HOMOLOG"

# Espera a aplicacao voltar a responder
esperar_app "$PORTA_HOMOLOG"

echo ">>> Homologacao atualizada com sucesso!"
