# Trabalho Final — Gerência de Configuração de Software

Sistema de **finanças pessoais** (CRUD) usado para demonstrar um pipeline
completo de CI/CD, com ambientes de Integração, Homologação e Produção.

## Tecnologias

- **Linguagem:** Python 3 (Flask)
- **Banco de dados:** PostgreSQL
- **Contêineres:** Docker (Ubuntu 24.04)
- **Versionamento de código:** Git + GitHub
- **Versionamento de banco:** Flyway (migrações)
- **Integração (CI/CD):** GitHub Actions
- **Testes:** pytest (20 testes)
- **Qualidade de código:** Flake8 + Pylint
- **Controle de mudança:** GitHub Issues

## Estrutura do projeto

```
.
├── app.py                  # Aplicação Flask
├── test_app.py             # 20 testes automatizados
├── requirements.txt        # Dependências da aplicação
├── requirements-dev.txt    # Ferramentas de teste e qualidade
├── Dockerfile              # Imagem (Ubuntu + Python + PostgreSQL)
├── entrypoint.sh           # Inicialização do container
├── db/migrations/          # Migrações do banco (Flyway)
│   └── V1__schema_inicial.sql
├── scripts/                # Automação da infraestrutura
│   ├── config.sh
│   ├── 00_limpar_vm.sh
│   ├── 01_montar_ambientes.sh
│   ├── 02_atualizar_homologacao.sh
│   └── 03_atualizar_producao.sh
├── .github/workflows/
│   └── pipeline.yml        # Pipeline de CI/CD
├── mudanca_exemplo/        # Material pronto para a mudança da apresentação
└── docs/
    └── ARQUITETURA.md      # Documento de arquitetura (entregável)
```

## Como usar

Veja o passo a passo completo em **[ROTEIRO_APRESENTACAO.md](ROTEIRO_APRESENTACAO.md)**.

Resumo:

```bash
# Na VM, dentro do repositório:
bash scripts/01_montar_ambientes.sh      # cria Homologação e Produção
# ... faça a mudança, commit e push (dispara o GitHub Actions) ...
bash scripts/03_atualizar_producao.sh    # promove para Produção
```

## Ambientes

| Ambiente | Endereço |
|---|---|
| Homologação | http://177.44.248.122:8081 |
| Produção | http://177.44.248.122:8082 |

Login padrão: `admin` / `123456`
