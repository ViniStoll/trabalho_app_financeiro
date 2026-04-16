from flask import Flask, render_template_string, request, redirect, url_for, send_file
import psycopg2
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configurações do Banco
DB_HOST = "localhost"
DB_NAME = "financeiro"
DB_USER = "postgres"
DB_PASS = "admin" 
DB_PORT = "5433" 

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

# --- FUNÇÕES AUXILIARES (E-MAIL E PDF) ---

def enviar_email_notificacao(acao, descricao):
    # --- CONFIGURAÇÕES DO E-MAIL ---
    meu_email = "vinicius.stoll1@universo.univates.br"  # O teu e-mail do Gmail
    minha_senha = "elnmxudviyaovqlk" # A senha de 16 dígitos que geraste
    destinatario = "vinicius.stoll1@universo.univates.br" # Para o teste, envia para ti mesmo

    # --- MONTAGEM DA MENSAGEM ---
    msg = MIMEMultipart()
    msg['From'] = meu_email
    msg['To'] = destinatario
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
        server.starttls() # Encripta a ligação
        server.login(meu_email, minha_senha)
        
        texto_final = msg.as_string()
        server.sendmail(meu_email, destinatario, texto_final)
        server.quit()
        print(f"DEBUG: E-mail de {acao} enviado com sucesso!")
    except Exception as e:
        print(f"DEBUG: Erro ao enviar e-mail: {e}")

# --- ROTAS DA APLICAÇÃO ---

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
                    <a href="/novo" style="font-size: 16px; background: #007bff; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none;">+ Novo Lançamento</a>
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

        # 3. Cria o arquivo PDF (Mesma lógica anterior)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        
        pdf.cell(200, 10, txt="Relatorio Financeiro Filtrado", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        
        # Opcional: Mostrar no PDF quais filtros foram aplicados
        filtros_texto = f"Filtros - Data: {filtro_data or 'Todas'} | Status: {filtro_status or 'Todos'}"
        pdf.cell(200, 10, txt=filtros_texto, ln=True, align='L')
        pdf.ln(5)

        # Cabeçalho da Tabela
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
    app.run(host='127.0.0.1', port=8000, debug=True)