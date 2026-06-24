# ============================================================
# Imagem do sistema financeiro: Ubuntu + Python (Flask) + PostgreSQL
# Tudo dentro de um unico container, no mesmo estilo dos exemplos
# usados em aula. A mesma imagem e usada em Homologacao e Producao.
# ============================================================

# 1. Imagem base Ubuntu 24.04
FROM ubuntu:24.04

# Evita perguntas interativas durante a instalacao dos pacotes
ENV DEBIAN_FRONTEND=noninteractive

# 2. Instala o Python, o PostgreSQL e utilitarios necessarios
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    postgresql \
    postgresql-contrib \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Define a senha do usuario 'postgres' e cria o banco 'financeiro'
RUN service postgresql start && \
    su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\"" && \
    su - postgres -c "psql -c \"CREATE DATABASE financeiro;\"" && \
    service postgresql stop

# 4. Libera o acesso ao banco pela rede do Docker (necessario para o Flyway)
RUN CONF_DIR=$(ls -d /etc/postgresql/*/main) && \
    echo "host all postgres 0.0.0.0/0 md5" >> $CONF_DIR/pg_hba.conf && \
    echo "listen_addresses = '*'" >> $CONF_DIR/postgresql.conf

# 5. Instala as dependencias Python num ambiente virtual (/opt/venv)
WORKDIR /app
COPY requirements.txt /app/
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# 6. Copia o codigo da aplicacao e o script de inicializacao
COPY app.py /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Porta do Flask (aplicacao) e do PostgreSQL (acessada pelo Flyway na rede)
EXPOSE 8000
EXPOSE 5432

# Comando que inicia o container
CMD ["/entrypoint.sh"]
