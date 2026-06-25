import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestAppFinanceiro(unittest.TestCase):
    
    def setUp(self):
        # Ativa o modo de teste no app principal
        app.config['TESTING'] = True
        # Cria um "cliente de teste" para simular o navegador
        self.app = app.test_client()
        # Ja entra "logado" para conseguir testar as telas internas
        with self.app.session_transaction() as sessao:
            sessao['logado'] = True

    # --- TESTES DE CONFIGURAÇÃO E LOGIN ---
    def test_01_app_is_testing(self):
        """1. Testa se o modo de testes do Flask está ativo"""
        self.assertTrue(app.config['TESTING'])

    def test_02_login_route_get(self):
        """2. Testa se a página de login carrega corretamente (Status 200)"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_03_login_page_content(self):
        """3. Testa se o HTML do login possui o título correto"""
        response = self.app.get('/')
        self.assertIn(b'Financeiro Login', response.data)

    @patch('app.get_db_connection')
    def test_04_login_post_invalid(self, mock_db):
        """4. Testa erro ao inserir login/senha errados"""
        # Configura o mock para fingir que o banco não achou o usuário
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.post('/', data=dict(login='errado', senha='123'))
        self.assertIn(b'Login ou senha incorretos', response.data)

    @patch('app.get_db_connection')
    def test_05_login_post_valid(self, mock_db):
        """5. Testa sucesso no login (Redirecionamento HTTP 302)"""
        # Finge que achou o usuário no banco
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('admin', 'admin') 
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.post('/', data=dict(login='admin', senha='123'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/listagem', response.headers.get('Location'))

    # --- TESTES DA LISTAGEM E FILTROS ---
    @patch('app.get_db_connection')
    def test_06_listagem_route_get(self, mock_db):
        """6. Testa se a página de listagem abre corretamente"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/listagem')
        self.assertEqual(response.status_code, 200)

    @patch('app.get_db_connection')
    def test_07_listagem_content(self, mock_db):
        """7. Testa se a tabela de lançamentos é renderizada"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, 'Conta de Luz', '2026-04-10', 150.0, 'Despesa', 'Pendente')]
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/listagem')
        self.assertIn(b'Conta de Luz', response.data)

    @patch('app.get_db_connection')
    def test_08_listagem_filtro_data(self, mock_db):
        """8. Testa se a listagem aceita filtro de data sem quebrar"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/listagem?data=2026-04-10')
        self.assertEqual(response.status_code, 200)

    @patch('app.get_db_connection')
    def test_09_listagem_filtro_status(self, mock_db):
        """9. Testa se a listagem aceita filtro de status sem quebrar"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/listagem?status=Pago')
        self.assertEqual(response.status_code, 200)

    # --- TESTES DO NOVO LANÇAMENTO (CREATE) ---
    def test_10_novo_route_get(self):
        """10. Testa se o formulário de novo lançamento abre"""
        response = self.app.get('/novo')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Novo Lançamento'.encode('utf-8'), response.data)

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_11_novo_route_post(self, mock_db, mock_email):
        """11. Testa o envio do formulário de novo lançamento"""
        response = self.app.post('/novo', data=dict(
            descricao='Teste Unitário', data_lancamento='2026-05-01',
            valor='100', tipo_lancamento='Receita', situacao='Pago'
        ))
        self.assertEqual(response.status_code, 302) # Deve redirecionar após salvar

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_12_novo_chama_email(self, mock_db, mock_email):
        """12. Testa se a função de e-mail é chamada ao criar"""
        self.app.post('/novo', data=dict(
            descricao='Teste E-mail', data_lancamento='2026-05-01',
            valor='100', tipo_lancamento='Receita', situacao='Pago'
        ))
        mock_email.assert_called_once_with('criado', 'Teste E-mail')

    # --- TESTES DA EDIÇÃO (UPDATE) ---
    @patch('app.get_db_connection')
    def test_13_editar_route_get(self, mock_db):
        """13. Testa se o formulário de edição carrega dados"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'Venda', '2026-04-10', 200.0, 'Receita', 'Pago')
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/editar/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Editar', response.data)

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_14_editar_route_post(self, mock_db, mock_email):
        """14. Testa o envio do formulário de edição"""
        response = self.app.post('/editar/1', data=dict(
            descricao='Editado', data_lancamento='2026-05-01',
            valor='150', tipo_lancamento='Receita', situacao='Pago'
        ))
        self.assertEqual(response.status_code, 302)

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_15_editar_chama_email(self, mock_db, mock_email):
        """15. Testa se a função de e-mail é chamada ao editar"""
        self.app.post('/editar/1', data=dict(
            descricao='Editado E-mail', data_lancamento='2026-05-01',
            valor='150', tipo_lancamento='Receita', situacao='Pago'
        ))
        mock_email.assert_called_once_with('atualizado', 'Editado E-mail')

    # --- TESTES DA EXCLUSÃO (DELETE) ---
    @patch('app.get_db_connection')
    def test_16_excluir_route(self, mock_db):
        """16. Testa a rota de exclusão (Redirecionamento)"""
        response = self.app.get('/excluir/1')
        self.assertEqual(response.status_code, 302)

    # --- TESTES DO PDF ---
    @patch('app.get_db_connection')
    def test_17_pdf_route_get(self, mock_db):
        """17. Testa se o PDF é gerado sem erros de servidor"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, 'PDF Teste', '2026-04-10', 100.0, 'Receita', 'Pago')]
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/exportar_pdf')
        self.assertEqual(response.status_code, 200)

    @patch('app.get_db_connection')
    def test_18_pdf_mimetype(self, mock_db):
        """18. Testa se o arquivo retornado realmente é do tipo PDF"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/exportar_pdf')
        self.assertEqual(response.mimetype, 'application/pdf')

    @patch('app.get_db_connection')
    def test_19_pdf_attachment(self, mock_db):
        """19. Testa se o PDF força o download (attachment)"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.app.get('/exportar_pdf')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))

    # --- TESTE DE ROTA INVÁLIDA ---
    def test_20_rota_inexistente(self):
        """20. Testa acesso a uma URL que não existe (Erro 404)"""
        response = self.app.get('/pagina_falsa_do_vinicius')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main(verbosity=2)