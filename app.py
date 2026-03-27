from flask import Flask, render_template_string
import psycopg2

app = Flask(__name__)

# Banco de Dados
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "financeiro"
DB_USER = "postgres"
DB_PASS = "admin" 

# Interface
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Meus Lançamentos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9;}
        h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; background-color: white; }
        th, td { border: 1px solid #dddddd; text-align: left; padding: 12px; }
        th { background-color: #007BFF; color: white; }
    </style>
</head>
<body>
    <h2>Listagem de Lançamentos</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Descrição</th>
            <th>Data</th>
            <th>Valor (R$)</th>
            <th>Tipo</th>
            <th>Situação</th>
        </tr>
        {% for lancamento in lancamentos %}
        <tr>
            <td>{{ lancamento[0] }}</td>
            <td>{{ lancamento[1] }}</td>
            <td>{{ lancamento[2] }}</td>
            <td>{{ lancamento[3] }}</td>
            <td>{{ lancamento[4] }}</td>
            <td>{{ lancamento[5] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    # Conectando ao banco de dados
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    
    # Buscando os lançamentos
    cur.execute("SELECT * FROM lancamento ORDER BY data_lancamento ASC;")
    meus_lancamentos = cur.fetchall()
    
    # Fechando a conexão
    cur.close()
    conn.close()
    
    # Mostrando a tela com os dados cadastrados
    return render_template_string(HTML_PAGE, lancamentos=meus_lancamentos)

if __name__ == '__main__':
    app.run(debug=True, port=8000)