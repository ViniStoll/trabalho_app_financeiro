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
- Login do sistema: admin / admin
- Repositório: https://github.com/ViniStoll/trabalho_app_financeiro

# Limpa VM:
```bash
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null; sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null; sudo docker system prune -a -f --volumes; rm -rf ~/trabalho_app_financeiro
```

## 1. Mostra que a VM está zerada:
```bash
sudo docker ps
sudo docker images
```

## 2. Sobe SÓ a homologação:
```bash
curl -fsSL https://raw.githubusercontent.com/ViniStoll/trabalho_app_financeiro/main/scripts/bootstrap.sh | bash
```
Só a homologação sobe. A produção ainda NÃO existe (mostro com `sudo docker ps`: só o `app_homolog`).

## 3. Homologação funcionando:
- Abro http://177.44.248.122:8081 e faço login (admin / admin).
- Clico em "+ Novo Lançamento", cadastro um item e mostro que aparece na lista.

## 4. Sobe a produção:
```bash
cd ~/trabalho_app_financeiro
bash scripts/subir_producao.sh
```
- Abro http://177.44.248.122:8082, faço login (admin / admin).
- Cadastro um item e mostro funcionando.

## 5. Faço as mudanças (no PC):
```bash
cd "/Users/viniciusstoll/Documents/Univates/Gerencia de Configuração de Software/app_financeiro"
```
- **Código:** abro o `app.py` no VSCode e troco a label que o professor pedir. Salvo.
- **Banco:** copio a migração da tabela categoria:
```bash
cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
```
- **Erro de propósito:** no `test_app.py` (test_01), descomento a linha do erro:
```python
# self.assertEqual(1, 2)   <- descomentar
```
Versiono tudo:
```bash
git add app.py test_app.py db/migrations/V2__criar_tabela_categoria.sql
git commit -m "Altera label e cria tabela categoria (closes #1)"
git push
```

## 6. Tento atualizar a homologação (com o erro → barra):
Na VM:
```bash
cd ~/trabalho_app_financeiro
bash scripts/atualizar_homologacao.sh
```
→ roda os testes + qualidade, encontra o erro e **CANCELA** (nada sobe). No GitHub Actions o pipeline também fica vermelho.

Corrijo o erro (no PC, comento a linha de novo no `test_app.py`) e versiono:
```bash
git add test_app.py
git commit -m "Corrige o teste"
git push
```
Atualizo a homologação de novo:
```bash
bash scripts/atualizar_homologacao.sh
```
→ agora passa e atualiza. No navegador (8081): a página **volta pro login** (reiniciou), faço login, a **label nova** aparece e o **lançamento que cadastrei continua lá** (o banco não foi apagado). Confiro a tabela nova:
```bash
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c '\dt'"
```

## 7. Confiro que a produção NÃO mudou e só então atualizo:
Primeiro mostro que a produção ainda está como antes (não atualizou sozinha):
- No navegador (8082): a **label antiga** ainda está lá.
- A tabela categoria ainda **não existe** na produção:
```bash
sudo docker exec app_prod su postgres -c "psql -d financeiro -c '\dt'"
```
Agora atualizo a produção:
```bash
bash scripts/atualizar_producao.sh
```
No navegador (8082): a label nova aparece, o lançamento que cadastrei continua, e a tabela já existe:
```bash
sudo docker exec app_prod su postgres -c "psql -d financeiro -c '\dt'"
```

---

> Lembrete: todo comando na VM é rodado de dentro de `~/trabalho_app_financeiro`. Se cair na home, é só `cd ~/trabalho_app_financeiro`.
