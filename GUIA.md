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
sudo docker volume ls
```

## 2. Sobe só a homologação:
```bash
curl -fsSL https://raw.githubusercontent.com/ViniStoll/trabalho_app_financeiro/main/scripts/bootstrap.sh | bash
```

## 3. Sobe a produção:
```bash
cd ~/trabalho_app_financeiro
bash scripts/subir_producao.sh
```

## 4. Alterações:
- **Código:** label
- **Banco:** tabela categoria
```bash
cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
```
- **Erro proposital:** linha do erro: # self.assertEqual(1, 2)

Versiona:
```bash
git add app.py test_app.py db/migrations/V2__criar_tabela_categoria.sql
git commit -m "Altera label e cria tabela categoria (closes #1)"
git push
```

## 5. Tenta atualizar a homologação:
```bash
cd ~/trabalho_app_financeiro
bash scripts/atualizar_homologacao.sh
```

Ajusta o erro e versiona:
```bash
git add test_app.py
git commit -m "Corrige o teste"
git push
```

Atualizo a homologação de novo:
```bash
bash scripts/atualizar_homologacao.sh
```

```bash
sudo docker exec app_homolog su postgres -c "psql -d financeiro -c '\dt categoria'"
```

## 6. Confiro que a produção não mudou e então atualizo:
Atualizo a produção:
```bash
bash scripts/atualizar_producao.sh
```

```bash
sudo docker exec app_prod su postgres -c "psql -d financeiro -c '\dt categoria'"
```
