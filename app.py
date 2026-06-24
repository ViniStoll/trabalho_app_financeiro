import os
from flask import Flask, render_template_string, request, redirect, url_for, send_file
import psycopg2
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# ------------------------------------------------------------------
# Configuracoes do Banco de Dados
# Os valores vem de variaveis de ambiente. Assim a MESMA imagem roda
# em Homologacao e Producao apenas mudando as variaveis, e nada de
# senha fica "chumbado" no codigo. Se a variavel nao existir, usa o
# valor padrao (que e o do banco que roda dentro do proprio container).
# ------------------------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "financeiro")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")

# Configuracoes do envio de e-mail (tambem via variaveis de ambiente).
# Se nao estiverem configuradas, o envio simplesmente e ignorado.
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE")
EMAIL_SENHA = os.environ.get("EMAIL_SENHA")
EMAIL_DESTINATARIO = os.environ.get("EMAIL_DESTINATARIO", EMAIL_REMETENTE)


def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

# --- FUNCOES AUXILIARES (E-MAIL E PDF) ---

def enviar_email_notificacao(acao, descricao):
    # Se o e-mail nao foi configurado nas variaveis de ambiente, nao faz nada.
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        print("DEBUG: Envio de e-mail desativado (configure EMAIL_REMETENTE e EMAIL_SENHA).")
        return

    # --- MONTAGEM DA MENSAGEM ---
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO
    msg['Subject'] = f"Aviso Financeiro: Lancamento {acao.capitalize()}"

    corpo = f"""
    Olá,

    Informamos que o lançamento '{descricao}' foi {acao} com sucesso no seu sistema.

    Atenciosamente,
    Sistema de Finanças Pessoais
    """
    msg.attach(MIMEText(corpo, 'plain'))

    # --- PROCESSO DE ENVIO ---
    try:
        # Liga ao servidor do Gmail (Porta 587 para TLS)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Encripta a ligacao
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
        server.quit()
        print(f"DEBUG: E-mail de {acao} enviado com sucesso!")
    except Exception as e:
        print(f"DEBUG: Erro ao enviar e-mail: {e}")

# --- ROTAS DA APLICACAO ---

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
        # Captura os filtros da URL (ex: ?data=2026-03-05&status=Pago)
        filtro_data = request.args.get('data')
        filtro_status = request.args.get('status')

        query = "SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE 1=1"
        params = []

        if filtro_data:
            query += " AND data_lancamento = %s"
            params.append(filtro_data)
        if filtro_status:
            query += " AND situacao = %s"
            params.append(filtro_status)

        query += " ORDER BY data_lancamento DESC"

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, tuple(params))
        dados = cur.fetchall()
        cur.close()
        conn.close()

        html_tabela = '''
        <body style="font-family: sans-serif; padding: 40px; background: #f4f7f6;">
            <div style="max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
                <h2 style="color: #333; display: flex; justify-content: space-between;">
                    Meus Lançamentos
                    <span>
                        <a href="/categorias" style="font-size: 16px; background: #6f42c1; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; margin-right: 8px;">Categorias</a>
                        <a href="/novo" style="font-size: 16px; background: #007bff; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none;">+ Novo Lançamento</a>
                    </span>
                </h2>

                <form method="get" style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; display: flex; gap: 10px; align-items: center;">
                    <label>Data:</label>
                    <input type="date" name="data" value="{{ request.args.get('data', '') }}" style="padding: 5px;">
                    <label>Status:</label>
                    <select name="status" style="padding: 5px;">
                        <option value="">Todos</option>
                        <option value="Pago" {% if request.args.get('status') == 'Pago' %}selected{% endif %}>Pago</option>
                        <option value="Pendente" {% if request.args.get('status') == 'Pendente' %}selected{% endif %}>Pendente</option>
                    </select>
                    <button type="submit" style="padding: 5px 15px; background: #6c757d; color: white; border: none; border-radius: 3px; cursor: pointer;">Filtrar</button>
                    <a href="/listagem" style="padding: 5px 10px; text-decoration: none; color: #6c757d; font-size: 14px;">Limpar</a>
                    <a href="/exportar_pdf?data={{ request.args.get('data', '') }}&status={{ request.args.get('status', '') }}" style="margin-left: auto; padding: 5px 15px; background: #dc3545; color: white; text-decoration: none; border-radius: 3px;">Exportar PDF</a>
                </form>

                <table border="0" style="width:100%; border-collapse: collapse;">
                    <tr style="background-color: #333; color: white; text-align: left;">
                        <th style="padding: 12px;">ID</th><th style="padding: 12px;">Descrição</th>
                        <th style="padding: 12px;">Data</th><th style="padding: 12px;">Valor</th>
                        <th style="padding: 12px;">Tipo</th><th style="padding: 12px;">Situação</th>
                        <th style="padding: 12px;">Ações</th>
                    </tr>
                    {% for item in dados %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px;">{{ item[0] }}</td><td style="padding: 12px;">{{ item[1] }}</td>
                        <td style="padding: 12px;">{{ item[2] }}</td><td style="padding: 12px;">R$ {{ "%.2f"|format(item[3]) }}</td>
                        <td style="padding: 12px;">{{ item[4] }}</td><td style="padding: 12px;">{{ item[5] }}</td>
                        <td style="padding: 12px;">
                            <a href="/editar/{{ item[0] }}" style="color: #28a745; text-decoration: none; margin-right: 10px;">Editar</a>
                            <a href="/excluir/{{ item[0] }}" style="color: #dc3545; text-decoration: none;" onclick="return confirm('Tem certeza?');">Excluir</a>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                <br><a href="/" style="text-decoration: none; color: #dc3545; font-weight: bold;">Sair do Sistema</a>
            </div>
        </body>
        '''
        return render_template_string(html_tabela, dados=dados, request=request)
    except Exception as e:
        return f"Erro de conexão: {e}"

@app.route('/categorias')
def categorias():
    # Tela simples que lista as categorias cadastradas.
    # A tabela 'categoria' e criada pela migracao V2 do banco.
    # Enquanto a migracao nao for aplicada, mostramos um aviso amigavel.
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, descricao FROM categoria ORDER BY id")
        dados = cur.fetchall()
        cur.close()
        conn.close()
        tabela_existe = True
    except Exception:
        dados = []
        tabela_existe = False

    html = '''
        <body style="font-family: sans-serif; padding: 40px; background: #f4f7f6;">
            <div style="max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
                <h2 style="color: #333;">Categorias</h2>
                {% if not tabela_existe %}
                    <p style="color: #856404; background: #fff3cd; padding: 12px; border-radius: 5px;">
                        A tabela de categorias ainda não foi criada (será adicionada pela migração V2 do banco).
                    </p>
                {% else %}
                    <table border="0" style="width:100%; border-collapse: collapse;">
                        <tr style="background-color: #6f42c1; color: white; text-align: left;">
                            <th style="padding: 12px;">ID</th>
                            <th style="padding: 12px;">Nome</th>
                            <th style="padding: 12px;">Descrição</th>
                        </tr>
                        {% for item in dados %}
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px;">{{ item[0] }}</td>
                            <td style="padding: 12px;">{{ item[1] }}</td>
                            <td style="padding: 12px;">{{ item[2] }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                {% endif %}
                <br><a href="/listagem" style="text-decoration: none; color: #007bff; font-weight: bold;">&larr; Voltar para Lançamentos</a>
            </div>
        </body>
    '''
    return render_template_string(html, dados=dados, tabela_existe=tabela_existe)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        descricao = request.form['descricao']
        data_lancamento = request.form['data_lancamento']
        valor = request.form['valor']
        tipo_lancamento = request.form['tipo_lancamento']
        situacao = request.form['situacao']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO lancamento (descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES (%s, %s, %s, %s, %s)",
            (descricao, data_lancamento, valor, tipo_lancamento, situacao)
        )
        conn.commit()
        cur.close()
        conn.close()

        enviar_email_notificacao("criado", descricao)
        return redirect(url_for('listagem'))

    html_form = '''
        <body style="font-family: sans-serif; padding: 40px; background: #f4f7f6;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
                <h2>Novo Lançamento</h2>
                <form method="post">
                    <input type="text" name="descricao" placeholder="Descrição" required style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                    <input type="date" name="data_lancamento" required style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                    <input type="number" step="0.01" name="valor" placeholder="Valor" required style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                    <select name="tipo_lancamento" style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                        <option value="Receita">Receita</option>
                        <option value="Despesa">Despesa</option>
                    </select>
                    <select name="situacao" style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                        <option value="Pago">Pago</option>
                        <option value="Pendente">Pendente</option>
                    </select>
                    <button type="submit" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; cursor: pointer; margin-top: 10px;">Salvar</button>
                    <a href="/listagem" style="display: block; text-align: center; margin-top: 15px; color: #666; text-decoration: none;">Cancelar</a>
                </form>
            </div>
        </body>
    '''
    return render_template_string(html_form)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        descricao = request.form['descricao']
        data_lancamento = request.form['data_lancamento']
        valor = request.form['valor']
        tipo_lancamento = request.form['tipo_lancamento']
        situacao = request.form['situacao']

        cur.execute(
            "UPDATE lancamento SET descricao=%s, data_lancamento=%s, valor=%s, tipo_lancamento=%s, situacao=%s WHERE id=%s",
            (descricao, data_lancamento, valor, tipo_lancamento, situacao, id)
        )
        conn.commit()
        cur.close()
        conn.close()

        enviar_email_notificacao("atualizado", descricao)
        return redirect(url_for('listagem'))

    cur.execute("SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE id = %s", (id,))
    item = cur.fetchone()
    cur.close()
    conn.close()

    html_form = '''
        <body style="font-family: sans-serif; padding: 40px; background: #f4f7f6;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
                <h2>Editar Lançamento</h2>
                <form method="post">
                    <input type="text" name="descricao" value="{{ item[1] }}" required style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                    <input type="date" name="data_lancamento" value="{{ item[2] }}" required style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                    <input type="number" step="0.01" name="valor" value="{{ item[3] }}" required style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                    <select name="tipo_lancamento" style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                        <option value="Receita" {% if item[4] == 'Receita' %}selected{% endif %}>Receita</option>
                        <option value="Despesa" {% if item[4] == 'Despesa' %}selected{% endif %}>Despesa</option>
                    </select>
                    <select name="situacao" style="width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box;">
                        <option value="Pago" {% if item[5] == 'Pago' %}selected{% endif %}>Pago</option>
                        <option value="Pendente" {% if item[5] == 'Pendente' %}selected{% endif %}>Pendente</option>
                    </select>
                    <button type="submit" style="width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; margin-top: 10px;">Atualizar</button>
                    <a href="/listagem" style="display: block; text-align: center; margin-top: 15px; color: #666; text-decoration: none;">Cancelar</a>
                </form>
            </div>
        </body>
    '''
    return render_template_string(html_form, item=item)

@app.route('/excluir/<int:id>')
def excluir(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lancamento WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('listagem'))

@app.route('/exportar_pdf')
def exportar_pdf():
    try:
        # 1. Captura os mesmos filtros que a listagem usa
        filtro_data = request.args.get('data')
        filtro_status = request.args.get('status')

        query = "SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE 1=1"
        params = []

        if filtro_data:
            query += " AND data_lancamento = %s"
            params.append(filtro_data)
        if filtro_status:
            query += " AND situacao = %s"
            params.append(filtro_status)

        query += " ORDER BY data_lancamento DESC"

        # 2. Busca os dados FILTRADOS no banco
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, tuple(params))
        dados = cur.fetchall()
        cur.close()
        conn.close()

        # 3. Cria o arquivo PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)

        pdf.cell(200, 10, txt="Relatorio Financeiro Filtrado", ln=True, align='C')
        pdf.set_font("Arial", size=10)

        # Mostra no PDF quais filtros foram aplicados
        filtros_texto = f"Filtros - Data: {filtro_data or 'Todas'} | Status: {filtro_status or 'Todos'}"
        pdf.cell(200, 10, txt=filtros_texto, ln=True, align='L')
        pdf.ln(5)

        # Cabecalho da Tabela
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(15, 10, "ID", border=1, align='C')
        pdf.cell(65, 10, "Descricao", border=1)
        pdf.cell(30, 10, "Data", border=1, align='C')
        pdf.cell(30, 10, "Valor", border=1, align='C')
        pdf.cell(25, 10, "Tipo", border=1, align='C')
        pdf.cell(25, 10, "Situacao", border=1, align='C')
        pdf.ln()

        # Linhas da Tabela
        pdf.set_font("Arial", size=10)
        for item in dados:
            pdf.cell(15, 10, str(item[0]), border=1, align='C')
            pdf.cell(65, 10, str(item[1]), border=1)
            pdf.cell(30, 10, str(item[2]), border=1, align='C')
            pdf.cell(30, 10, f"R$ {item[3]:.2f}", border=1, align='C')
            pdf.cell(25, 10, str(item[4]), border=1, align='C')
            pdf.cell(25, 10, str(item[5]), border=1, align='C')
            pdf.ln()

        nome_arquivo = "relatorio_filtrado.pdf"
        pdf.output(nome_arquivo)
        return send_file(nome_arquivo, as_attachment=True)

    except Exception as e:
        return f"Erro ao gerar PDF: {e}"

if __name__ == '__main__':
    # A porta e o modo debug tambem podem vir de variaveis de ambiente.
    porta = int(os.environ.get("APP_PORT", 8000))
    modo_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=porta, debug=modo_debug)
