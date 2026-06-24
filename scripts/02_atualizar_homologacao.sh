#!/bin/bash
# ============================================================
# Atualiza o ambiente de HOMOLOGACAO com a versao mais nova.
#
# Este script e chamado automaticamente pelo GitHub Actions
# (ambiente de Integracao) depois que os testes e a analise de
# qualidade passam.
#
# IMPORTANTE: o banco NAO e apagado. As migracoes novas (ex: a
# tabela categoria) sao apenas adicionadas, e os dados antigos
# continuam la.
# ============================================================
set -e
source "$(dirname "$0")/config.sh"

# 1. Pega a versao mais nova do codigo no GitHub
echo ">>> Atualizando o codigo a partir do GitHub..."
cd "$PROJETO_DIR"
git fetch origin
git reset --hard origin/main

# 2. Aplica SOMENTE as migracoes novas do banco
echo ">>> Aplicando migracoes do banco em HOMOLOGACAO..."
flyway_migrate "$CONT_HOMOLOG"

# 3. Copia o codigo novo da aplicacao para dentro do container
echo ">>> Atualizando o codigo da aplicacao no container..."
sudo docker cp "$PROJETO_DIR/app.py" "$CONT_HOMOLOG":/app/app.py

# 4. Reinicia a aplicacao (o banco e os dados sao preservados)
echo ">>> Reiniciando a aplicacao..."
sudo docker restart "$CONT_HOMOLOG"

# 5. Espera a aplicacao voltar a responder
esperar_app "$PORTA_HOMOLOG"

echo ">>> Homologacao atualizada com sucesso!"
