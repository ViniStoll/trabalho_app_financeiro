# Pasta de exemplo da mudança (apresentação)

Esta pasta guarda, **pronto e testado**, o material das 2 mudanças que o
professor vai pedir durante a apresentação (passo 4 do roteiro):

1. **Mudança de banco** → criar uma tabela de categoria
2. **Mudança de código** → alterar uma label de uma tela

Ela **não** faz parte do sistema em si — fica aqui só para você aplicar a
mudança rapidamente e sem erros na hora da apresentação.

---

## 1. Mudança de BANCO (criar tabela `categoria`)

O arquivo `V2__criar_tabela_categoria.sql` já está pronto. Na hora da
apresentação, basta copiá-lo para a pasta de migrações e versionar:

```bash
cp mudanca_exemplo/V2__criar_tabela_categoria.sql db/migrations/
git add db/migrations/V2__criar_tabela_categoria.sql
```

> Se o professor pedir uma tabela com outro nome/colunas, é só editar o
> conteúdo do arquivo antes de copiar. O nome do arquivo deve sempre seguir
> o padrão `V<numero>__descricao.sql` (próximo número livre).

## 2. Mudança de CÓDIGO (alterar uma label)

As labels ficam no arquivo `app.py`. As mais fáceis de alterar ao vivo:

| Tela | Texto atual (label) | Onde está |
|------|---------------------|-----------|
| Login | `Financeiro Login` | função `login()` |
| Listagem | `Meus Lançamentos` | função `listagem()` |
| Novo | `Novo Lançamento` | função `novo()` |
| Categorias | `Categorias` | função `categorias()` |

Exemplo: o professor pede para trocar "Meus Lançamentos" por
"Painel Financeiro". Você edita essa linha no `app.py`, salva, e versiona.

## 3. Versionar e disparar o pipeline

Depois de fazer as 2 mudanças acima:

```bash
git add app.py db/migrations/
git commit -m "Altera label e cria tabela de categoria"
git push
```

O `git push` dispara o GitHub Actions (Integração), que roda os testes, a
análise de qualidade, o build e, se tudo passar, atualiza a **Homologação**
automaticamente.
