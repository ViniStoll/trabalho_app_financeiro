#!/bin/bash
# ============================================================
# Configuracoes compartilhadas por todos os scripts.
# Este arquivo nao roda sozinho: ele e "carregado" pelos outros
# scripts com o comando 'source'.
# ============================================================

# Descobre a pasta do projeto automaticamente (pasta acima de /scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO_DIR="$(dirname "$SCRIPT_DIR")"

# Nome da imagem Docker da aplicacao
IMAGEM="imagem_financeiro"

# Rede Docker usada pelos containers e pelo Flyway
REDE="rede_gcs"

# Ambiente de HOMOLOGACAO
CONT_HOMOLOG="app_homolog"
PORTA_HOMOLOG=8081

# Ambiente de PRODUCAO
CONT_PROD="app_prod"
PORTA_PROD=8082

# Pasta com as migracoes do banco (lidas pelo Flyway)
MIGRACOES_DIR="$PROJETO_DIR/db/migrations"

# Imagem oficial do Flyway (ferramenta de versionamento do banco)
FLYWAY_IMG="flyway/flyway:10"

# Ambiente virtual Python usado so para rodar os testes na VM
VENV_TESTES="$PROJETO_DIR/.venv_testes"

# ------------------------------------------------------------
# Funcao que roda os 20 testes automatizados E a analise de
# qualidade do codigo. Cria o ambiente na primeira vez (instala
# as dependencias). Retorna 0 se passar tudo, diferente de 0 se
# algo falhar. E usada para BLOQUEAR o deploy quando ha erro.
# ------------------------------------------------------------
rodar_testes() {
    if [ ! -d "$VENV_TESTES" ]; then
        echo "    (preparando o ambiente de testes pela primeira vez...)"
        python3 -m venv "$VENV_TESTES"
        "$VENV_TESTES/bin/pip" install -q --upgrade pip
        "$VENV_TESTES/bin/pip" install -q -r "$PROJETO_DIR/requirements.txt" -r "$PROJETO_DIR/requirements-dev.txt"
    fi
    # 1) testes automatizados
    "$VENV_TESTES/bin/pytest" "$PROJETO_DIR/test_app.py" -q || return 1
    # 2) qualidade do codigo (erros graves: sintaxe, variavel indefinida, etc.)
    "$VENV_TESTES/bin/flake8" "$PROJETO_DIR/app.py" --select=E9,F63,F7,F82 || return 1
    return 0
}

# ------------------------------------------------------------
# Funcao que aplica as migracoes do banco em um container.
# Recebe como parametro o nome do container alvo (ex: app_homolog).
# O Flyway aplica SOMENTE as migracoes que ainda nao foram
# executadas, sem apagar os dados existentes.
# ------------------------------------------------------------
flyway_migrate() {
    local alvo="$1"
    sudo docker run --rm \
        --network "$REDE" \
        -v "$MIGRACOES_DIR":/flyway/sql \
        "$FLYWAY_IMG" \
        -url="jdbc:postgresql://$alvo:5432/financeiro" \
        -user=postgres \
        -password=postgres \
        -connectRetries=20 \
        migrate
}

# ------------------------------------------------------------
# Funcao que espera a aplicacao responder em uma porta.
# Apos um restart, o container leva alguns segundos para o
# PostgreSQL e o Flask ficarem prontos.
# ------------------------------------------------------------
esperar_app() {
    local porta="$1"
    echo "    Aguardando a aplicacao responder na porta $porta..."
    for i in $(seq 1 30); do
        if curl -s -m 2 "http://localhost:$porta/" >/dev/null 2>&1; then
            echo "    Aplicacao no ar!"
            return 0
        fi
        sleep 2
    done
    echo "    Aviso: a aplicacao demorou mais que o esperado para responder."
}
