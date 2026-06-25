#!/bin/bash
# ============================================================
# Atualiza o ambiente de PRODUCAO com a versao mais nova.
# So deve ser rodado DEPOIS de validar a homologacao.
#
# Antes de atualizar, roda os testes + a qualidade do codigo.
# Se algo falhar, CANCELA a atualizacao (nada sobe).
#
# O banco NAO e apagado: as migracoes novas sao apenas
# adicionadas e os dados antigos ficam.
# ============================================================
set -e
source "$(dirname "$0")/config.sh"

# 1. Pega a versao mais nova do codigo no GitHub
echo ">>> Atualizando o codigo a partir do GitHub..."
cd "$PROJETO_DIR"
git fetch origin
git reset --hard origin/main

# 2. Roda os testes + qualidade. Se falhar, CANCELA a atualizacao.
echo ">>> Rodando os testes e a analise de qualidade..."
if ! rodar_testes; then
    echo ""
    echo "############################################################"
    echo " TESTES/QUALIDADE FALHARAM! Atualizacao da PRODUCAO cancelada."
    echo " Corrija o erro, faca commit e push, e rode o script de novo."
    echo "############################################################"
    exit 1
fi
echo ">>> Tudo passou. Seguindo com a atualizacao..."

# 3. Aplica SOMENTE as migracoes novas do banco
echo ">>> Aplicando migracoes do banco em PRODUCAO..."
flyway_migrate "$CONT_PROD"

# 4. Copia o codigo novo da aplicacao para dentro do container
echo ">>> Atualizando o codigo da aplicacao no container..."
sudo docker cp "$PROJETO_DIR/app.py" "$CONT_PROD":/app/app.py

# 5. Reinicia a aplicacao (o banco e os dados sao preservados)
echo ">>> Reiniciando a aplicacao..."
sudo docker restart "$CONT_PROD"

# 6. Espera a aplicacao voltar a responder
esperar_app "$PORTA_PROD"

echo ">>> Producao atualizada com sucesso!"
