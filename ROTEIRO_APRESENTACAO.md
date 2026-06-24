# Roteiro da Apresentação — passo a passo

Este é o guia para a apresentação final. Siga na ordem. Os comandos já
estão prontos para copiar e colar.

- **VM:** `ssh univates@177.44.248.122`
- **Homologação:** http://177.44.248.122:8081
- **Produção:** http://177.44.248.122:8082
- **Repositório:** https://github.com/ViniStoll/trabalho_app_financeiro

### Onde cada passo é feito

Você vai usar **dois lugares**. Cada passo abaixo está marcado com um ícone:

- 💻 **No seu computador** (terminal na pasta do projeto): para editar o
  código e fazer `git push`. É o "Workspace local" do diagrama.
- 🖥️ **Na VM** (via `ssh`): para montar os ambientes e promover produção.

> 💻 No seu computador, abra um terminal na pasta do projeto:
> ```bash
> cd "/Users/viniciusstoll/Documents/Univates/Gerencia de Configuração de Software/app_financeiro"
> ```
> 🖥️ E, em outra aba/terminal, conecte na VM:
> ```bash
> ssh univates@177.44.248.122
> cd ~/trabalho_app_financeiro
> ```

### Antes da apresentação (conferir 1x)

O deploy automático da Homologação é feito por um **runner self-hosted** do
GitHub Actions que roda na VM. Confirme que o serviço dele está ativo:

```bash
sudo systemctl status actions.runner.* --no-pager | grep Active
```

Deve aparecer `Active: active (running)`. Se não estiver, inicie com:

```bash
sudo systemctl start actions.runner.*
```

---

## Passo 1 — 🖥️ (VM) Provar que a VM está zerada

Mostra que não há Docker, containers nem imagens criadas.

```bash
docker --version || echo "Docker NAO instalado"
sudo docker ps -a 2>/dev/null || echo "Nenhum container"
sudo docker images 2>/dev/null || echo "Nenhuma imagem"
```

> Esperado: Docker não instalado / nada criado. (A instalação será feita
> automaticamente pelo script no passo 2 — isso atende o requisito de
> "instalação automatizada das ferramentas".)

---

## Passo 2 — 🖥️ (VM) Montar Homologação e Produção (1 script)

```bash
cd ~/trabalho_app_financeiro
git pull
bash scripts/01_montar_ambientes.sh
```

Esse script faz **tudo sozinho**: instala o Docker, libera as portas no
firewall, constrói a imagem, sobe os 2 containers (homolog e prod) e aplica
as migrações do banco (Flyway) nos dois.

Ao final, confirme que os 2 containers estão rodando:

```bash
sudo docker ps
```

---

## Passo 3 — 🌐 (Navegador) Mostrar a aplicação nos 2 ambientes

No navegador, abra **duas abas**:

- Homologação: **http://177.44.248.122:8081**
- Produção: **http://177.44.248.122:8082**

Login: usuário `admin` / senha `123456`.
Mostre a lista de lançamentos funcionando nas duas.

---

## Passo 4 — 🌐 (GitHub) Registrar a mudança (Controle de Mudança)

No GitHub, vá em **Issues → New issue** e crie, por exemplo:

> **Título:** Alterar label da tela e criar tabela de categoria
> **Descrição:** Trocar o label "Meus Lançamentos" e adicionar a tabela
> `categoria` no banco.

(Guarde o número da issue, ex.: `#1`.)

---

## Passo 5 — 💻 (Seu computador) Implementar as 2 mudanças

### 5.1 Mudança de CÓDIGO (a label que o professor pedir)

Abra o arquivo `app.py` no seu editor (ex.: VSCode) e altere a label que o
professor pedir. Exemplo: trocar `Meus Lançamentos` por `Painel Financeiro`.

> Labels fáceis de achar (busque pelo texto no `app.py`):
> `Financeiro Login`, `Meus Lançamentos`, `Novo Lançamento`, `Categorias`.

### 5.2 Mudança de BANCO (criar a tabela de categoria)

O arquivo já está pronto na pasta de exemplo. Basta copiá-lo para a pasta
de migrações:

```bash
cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
```

> Se o professor pedir outro nome/colunas, edite o arquivo antes de copiar.

---

## Passo 6 — 💻 (Seu computador) Versionar (commit + push)

```bash
git add app.py db/migrations/V2__criar_tabela_categoria.sql
git commit -m "Altera label e cria tabela categoria (closes #1)"
git push
```

O `git push` **dispara o GitHub Actions** automaticamente.

---

## Passo 7 — 🌐 (Navegador) Integração + atualização da Homologação

Abra a aba **Actions** do GitHub:
https://github.com/ViniStoll/trabalho_app_financeiro/actions

Mostre o pipeline rodando, em ordem:

1. **20 testes** passando + a tabela de estatísticas (no "Summary" da execução)
2. **Qualidade** (Flake8 + Pylint)
3. **Build** da imagem
4. **Deploy na Homologação** — o job "Atualizar Homologacao" roda no
   *runner self-hosted* da própria VM e atualiza o ambiente automaticamente.

Quando terminar (verde), volte ao navegador na aba de **Homologação**
(http://177.44.248.122:8081):

- A label nova já aparece.
- Clique em **Categorias** → a nova tabela aparece com os dados.

Confirme que o banco **não foi apagado** (os lançamentos antigos continuam lá).
Para provar pelo banco:

```bash
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c '\dt'"
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c 'SELECT * FROM categoria;'"
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c 'SELECT count(*) FROM lancamento;'"
```

> Repare que a tabela `categoria` foi **adicionada** e a `lancamento`
> continua com todos os dados.

---

## Passo 8 — 🖥️ (VM) Atualizar a Produção (1 script)

A produção é promovida manualmente, rodando um script:

```bash
bash scripts/03_atualizar_producao.sh
```

Volte ao navegador na aba de **Produção** (http://177.44.248.122:8082):

- A label nova aparece.
- A tela **Categorias** mostra a nova tabela.
- Os dados antigos continuam lá (banco não foi apagado).

Para provar pelo banco:

```bash
sudo docker exec app_prod su postgres -c "psql -d financeiro -c '\dt'"
sudo docker exec app_prod su postgres -c "psql -d financeiro -c 'SELECT * FROM categoria;'"
```

---

## Resumo (o que cada passo entrega da tarefa)

| Passo | Fase da tarefa |
|---|---|
| 1 | Ambientes com estrutura não existente |
| 2 | Criar Homologação e Produção (H) |
| 3 | Aplicação funcionando em Homolog e Prod |
| 4 | Registro da mudança (A) |
| 5 | Implementação: código e banco (B) |
| 6 | Versionamento (C) |
| 7 | Integração: testes (D) + qualidade (E) + build + atualizar Homolog (F) |
| 8 | Atualizar Produção (G) |
