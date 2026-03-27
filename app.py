from flask import Flask, render_template_string, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Configurações
DB_HOST = "localhost"
DB_NAME = "financeiro"
DB_USER = "postgres"
DB_PASS = "admin"
DB_PORT = "5432"

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login']
        senha_input = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuario WHERE login = %s AND senha = %s", (login_input, senha_input))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return redirect(url_for('listagem'))
        else:
            return "Login ou senha incorretos! <a href='/'>Tentar novamente</a>"

    return '''
        <body style="font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f7f6;">
            <form method="post" style="background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 300px;">
                <h2 style="text-align: center; color: #333;">Financeiro Login</h2>
                <input type="text" name="login" placeholder="Usuário" required style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
                <input type="password" name="senha" placeholder="Senha" required style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
                <button type="submit" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Entrar</button>
            </form>
        </body>
    '''

@app.route('/listagem')
def listagem():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento ORDER BY data_lancamento DESC")
        dados = cur.fetchall()
        cur.close()
        conn.close()

        html_tabela = '''
        <body style="font-family: sans-serif; padding: 40px; background: #f4f7f6;">
            <div style="max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
                <h2 style="color: #333;">Meus Lançamentos Financeiros</h2>
                <table border="0" style="width:100%; border-collapse: collapse; margin-top: 20px;">
                    <tr style="background-color: #333; color: white; text-align: left;">
                        <th style="padding: 12px;">ID</th><th style="padding: 12px;">Descrição</th>
                        <th style="padding: 12px;">Data</th><th style="padding: 12px;">Valor</th>
                        <th style="padding: 12px;">Tipo</th><th style="padding: 12px;">Situação</th>
                    </tr>
                    {% for item in dados %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px;">{{ item[0] }}</td><td style="padding: 12px;">{{ item[1] }}</td>
                        <td style="padding: 12px;">{{ item[2] }}</td><td style="padding: 12px;">R$ {{ "%.2f"|format(item[3]) }}</td>
                        <td style="padding: 12px;">{{ item[4] }}</td><td style="padding: 12px;">{{ item[5] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                <br><a href="/" style="text-decoration: none; color: #dc3545; font-weight: bold;">Sair do Sistema</a>
            </div>
        </body>
        '''
        return render_template_string(html_tabela, dados=dados)
    except Exception as e:
        return f"Erro de conexão: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
