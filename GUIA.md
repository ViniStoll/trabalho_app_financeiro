# Guia da apresentação

Sistema financeiro (CRUD em Python/Flask) com o fluxo completo de CI/CD.

Uso **dois lugares** durante a apresentação:

- **Meu computador** — a pasta do projeto. É onde eu altero o código e dou `git push`.
- **A VM** — `ssh univates@177.44.248.122`. É onde eu monto os ambientes e atualizo homologação/produção.

Endereços e acessos:

- Homologação: http://177.44.248.122:8081
- Produção: http://177.44.248.122:8082
- Login do sistema: **admin / admin**
- Repositório: https://github.com/ViniStoll/trabalho_app_financeiro

O que eu usei (diagrama em `docs/arquitetura.svg`): Python/Flask, PostgreSQL, Docker, Git + GitHub, GitHub Actions, Flyway, pytest e Flake8/Pylint.

---

## 1. Mostrar que a VM está zerada (na VM)

Rodo um comando que apaga tudo (containers, imagens, volumes e o código). O Docker continua instalado só para conseguir provar que não tem nada:

```bash
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null; sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null; sudo docker system prune -a -f --volumes; rm -rf ~/trabalho_app_financeiro
```

Aí provo que está zerada (é o que o professor confere):

```bash
sudo docker ps
sudo docker images
```

Os dois têm que aparecer vazios (só o cabeçalho).

## 2. Montar tudo do zero (na VM) — um comando só

Esse comando baixa o projeto do GitHub e sobe tudo (constrói a imagem, sobe os 2 ambientes e cria o banco):

```bash
curl -fsSL https://raw.githubusercontent.com/ViniStoll/trabalho_app_financeiro/main/scripts/bootstrap.sh | bash
```

No fim, confirmo os containers no ar:

```bash
sudo docker ps
```

## 3. Mostrar a aplicação funcionando (navegador)

Abro as duas abas e faço login com **admin / admin** nas duas:

- Homologação: http://177.44.248.122:8081
- Produção: http://177.44.248.122:8082

## 4. Registrar a mudança (GitHub → Issues)

No GitHub, em **Issues → New issue**, crio uma issue simples descrevendo a mudança que o professor pedir (ex.: "Alterar a label X e criar a tabela categoria"). Anoto o número (ex.: #1).

## 5. Fazer as duas mudanças (no MEU computador)

Abro a pasta do projeto no computador:

```bash
cd "/Users/viniciusstoll/Documents/Univates/Gerencia de Configuração de Software/app_financeiro"
```

**Mudança de código:** abro o `app.py` no VSCode e troco a label que o professor pedir (ex.: "Meus Lançamentos" → "Painel Financeiro"). Salvo.

**Mudança de banco:** copio a migração que cria a tabela categoria:

```bash
cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
```

## 6. Versionar (no MEU computador)

```bash
git add app.py db/migrations/V2__criar_tabela_categoria.sql
git commit -m "Altera label e cria tabela categoria (closes #1)"
git push
```

O push dispara o GitHub Actions sozinho.

## 7. Integração + atualizar a homologação

Na aba **Actions** do GitHub mostro o pipeline rodando: os 20 testes, a análise de qualidade (Flake8 + Pylint) e o build — tudo junto.

Quando ficar verde, **na VM** atualizo a homologação:

```bash
cd ~/trabalho_app_financeiro
bash scripts/02_atualizar_homologacao.sh
```

Esse script roda os testes de novo e, se passarem, atualiza o ambiente. Volto no navegador (http://177.44.248.122:8081) e atualizo a página: como o sistema reiniciou, ele **volta para a tela de login**. Faço login de novo e mostro a label nova.

A tabela categoria não aparece no sistema (é só no banco). Provo que ela foi criada por comando:

```bash
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c '\dt'"
```

Mostro que a tabela `categoria` está na lista e que a `lancamento` continua com os dados (o banco não foi apagado).

## 8. Atualizar a produção (na VM)

```bash
bash scripts/03_atualizar_producao.sh
```

Mesma coisa no navegador da produção (http://177.44.248.122:8082): volta pro login, faço login, mostro a label nova, e confirmo a tabela:

```bash
sudo docker exec app_prod su postgres -c "psql -d financeiro -c '\dt'"
```

---

## Demonstrar o teste bloqueando o deploy

Se o professor pedir para eu colocar um erro de propósito:

1. No **meu computador**, quebro um teste no `test_app.py` (ex.: trocar um valor esperado numa assertiva), faço commit e push.
2. Na **VM**, tento atualizar: `bash scripts/02_atualizar_homologacao.sh`. Ele roda os testes, vê que falhou e **cancela a atualização** (não sobe nada para homologação).
3. No **meu computador**, conserto o teste, faço commit e push.
4. Na **VM**, rodo de novo `bash scripts/02_atualizar_homologacao.sh`. Agora os testes passam e o ambiente atualiza normalmente.

---

> Lembrete: todo comando na VM é rodado de dentro de `~/trabalho_app_financeiro`. Se cair na home, é só `cd ~/trabalho_app_financeiro`.
