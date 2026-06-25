# PC:
```bash
cd "/Users/viniciusstoll/Documents/Univates/Gerencia de Configuração de Software/app_financeiro"
```

# VM:
```bash
ssh univates@177.44.248.122
```
viniciusrs8

# Acessos:
- Homologação: http://177.44.248.122:8081
- Produção: http://177.44.248.122:8082
- Repositório: https://github.com/ViniStoll/trabalho_app_financeiro

# Limpa VM:
```bash
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null; sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null; sudo docker system prune -a -f --volumes; rm -rf ~/trabalho_app_financeiro
```

## 1. Mostra que VM está zerada:
```bash
sudo docker ps
sudo docker images
```

## 2. Sobe tudo pra VM:
```bash
curl -fsSL https://raw.githubusercontent.com/ViniStoll/trabalho_app_financeiro/main/scripts/bootstrap.sh | bash
```

## 3. Mostrar a aplicação funcionando:
- Homologação: http://177.44.248.122:8081
- Produção: http://177.44.248.122:8082
admin

## 4. Fazer as duas mudanças solicitadas:
```bash
cd "/Users/viniciusstoll/Documents/Univates/Gerencia de Configuração de Software/app_financeiro"
```

**Mudança de código:** abro o `app.py` no VSCode e troco a label que o professor pedir. Salvo.

**Mudança de banco:** a tabela categoria já está pronta (simples e vazia) no arquivo `mudanca_exemplo/V2__criar_tabela_categoria.sql`. Para "criar" a tabela, copio esse arquivo para a pasta de migrações:
```bash
cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
```
(Se o professor pedir outro nome/colunas, edito o arquivo antes de copiar.)

## 5. Causar um erro de propósito:
No `test_app.py`, dentro do `test_01`, já deixei um erro pronto e comentado. Descomento a linha para o CI/CD encontrar o erro:
```python
# self.assertEqual(1, 2)   <- descomentar para causar o erro
```

## 6. Versionar (MEU computador)
```bash
git add app.py test_app.py db/migrations/V2__criar_tabela_categoria.sql
git commit -m "Altera label e cria tabela categoria (closes #1)"
git push
```
O push dispara o GitHub Actions sozinho.

## 7. Integração + atualizar a homologação (VM)

Na aba **Actions** do GitHub mostro o pipeline rodando: os 20 testes, a qualidade (Flake8 + Pylint) e o build — tudo junto.

Como deixei o erro de propósito, **um teste falha e o pipeline fica vermelho**. Na VM, se eu tentar atualizar, ele também barra (roda os testes antes):
```bash
cd ~/trabalho_app_financeiro
bash scripts/02_atualizar_homologacao.sh
```
→ ele vê o erro e **cancela** a atualização (não sobe nada).

Aí corrijo: comento de novo a linha do erro no `test_app.py` e versiono:
```bash
git add test_app.py
git commit -m "Corrige o teste"
git push
```
Agora o pipeline fica verde. Atualizo a homologação:
```bash
bash scripts/02_atualizar_homologacao.sh
```
Volto no navegador (http://177.44.248.122:8081) e atualizo a página: o sistema reiniciou e **volta pra tela de login**. Faço login (admin / admin) e mostro a label nova.

A tabela categoria não aparece no sistema (é só no banco). Provo que foi criada por comando:
```bash
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c '\dt'"
```
A tabela `categoria` aparece na lista e as outras continuam com os dados (o banco não foi apagado).

## 8. Atualizar a produção (VM)
```bash
bash scripts/03_atualizar_producao.sh
```
No navegador da produção (http://177.44.248.122:8082): volta pro login, faço login, mostro a label nova, e confirmo a tabela:
```bash
sudo docker exec app_prod su postgres -c "psql -d financeiro -c '\dt'"
```

---

> Lembrete: todo comando na VM é rodado de dentro de `~/trabalho_app_financeiro`. Se cair na home, é só `cd ~/trabalho_app_financeiro`.
