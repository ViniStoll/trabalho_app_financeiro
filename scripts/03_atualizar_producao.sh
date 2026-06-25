#!/bin/bash
# ============================================================
# Passo final da apresentacao: atualizar a PRODUCAO.
#
# E o mesmo processo da homologacao, mas rodado manualmente
# (o professor pede para "rodar um script" para promover a
# mudanca para producao).
#
# IMPORTANTE: o banco NAO e apagado. Apenas as migracoes novas
# sao aplicadas e os dados antigos sao preservados.
# ============================================================
set -e
source "$(dirname "$0")/config.sh"

# 1. Pega a versao mais nova do codigo no GitHub
echo ">>> Atualizando o codigo a partir do GitHub..."
cd "$PROJETO_DIR"
git fetch origin
git reset --hard origin/main

# 2. Roda os testes automatizados. Se algum falhar, CANCELA a atualizacao.
echo ">>> Rodando os testes automatizados..."
if ! rodar_testes; then
    echo ""
    echo "############################################################"
    echo " TESTES FALHARAM! A atualizacao da PRODUCAO foi cancelada."
    echo " Corrija o erro, faca commit e push, e rode o script de novo."
    echo "############################################################"
    exit 1
fi
echo ">>> Todos os testes passaram. Seguindo com a atualizacao..."

# 3. Aplica SOMENTE as migracoes novas do banco
echo ">>> Aplicando migracoes do banco em PRODUCAO..."
flyway_migrate "$CONT_PROD"

# 3. Copia o codigo novo da aplicacao para dentro do container
echo ">>> Atualizando o codigo da aplicacao no container..."
sudo docker cp "$PROJETO_DIR/app.py" "$CONT_PROD":/app/app.py

# 4. Reinicia a aplicacao (o banco e os dados sao preservados)
echo ">>> Reiniciando a aplicacao..."
sudo docker restart "$CONT_PROD"

# 5. Espera a aplicacao voltar a responder
esperar_app "$PORTA_PROD"

echo ">>> Producao atualizada com sucesso!"
