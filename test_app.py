import unittest
from unittest.mock import patch, MagicMock
from app import app

class EmailDummy:
    def enviar(self, *args):
        pass 

class BancoFake:
    def __init__(self):
        self.itens = []

    def salvar(self, item):
        self.itens.append(item)

    def listar(self):
        return self.itens

class TestAppFinanceiro(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        with self.app.session_transaction() as sessao:
            sessao['logado'] = True

    # Testes de tela de login
    def test_01_app_em_modo_teste(self):
        """1. O modo de testes do Flask deve estar ativo"""
        self.assertTrue(app.config['TESTING'])

    def test_02_login_abre(self):
        """2. A pagina de login deve carregar (HTTP 200)"""
        resposta = self.app.get('/')
        self.assertEqual(resposta.status_code, 200)

    def test_03_login_tem_titulo(self):
        """3. A pagina de login deve ter o titulo certo"""
        resposta = self.app.get('/')
        self.assertIn(b'Financeiro Login', resposta.data)

    @patch('app.get_db_connection')
    def test_04_login_errado(self, banco_falso):
        """4. Login/senha errados devem ser recusados"""
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        banco_falso.return_value.cursor.return_value = cursor

        resposta = self.app.post('/', data=dict(login='errado', senha='123'))
        self.assertIn(b'Login ou senha incorretos', resposta.data)

    @patch('app.get_db_connection')
    def test_05_login_certo(self, banco_falso):
        """5. Login certo deve redirecionar (HTTP 302) para a listagem"""
        cursor = MagicMock()
        cursor.fetchone.return_value = ('admin', 'admin')
        banco_falso.return_value.cursor.return_value = cursor

        resposta = self.app.post('/', data=dict(login='admin', senha='admin'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/listagem', resposta.headers.get('Location'))

    @patch('app.get_db_connection')
    def test_06_listagem_mostra_dado(self, banco_falso):
        """6. A listagem deve mostrar o lancamento que o banco devolveu"""
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, 'Conta de Luz', '2026-04-10', 150.0, 'Despesa', 'Pendente')]
        banco_falso.return_value.cursor.return_value = cursor

        resposta = self.app.get('/listagem')
        self.assertIn(b'Conta de Luz', resposta.data)

    @patch('app.get_db_connection')
    def test_07_listagem_vazia(self, banco_falso):
        """7. A listagem sem dados deve abrir normalmente (HTTP 200)"""
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        banco_falso.return_value.cursor.return_value = cursor

        resposta = self.app.get('/listagem')
        self.assertEqual(resposta.status_code, 200)

    @patch('app.get_db_connection')
    def test_08_editar_carrega_dado(self, banco_falso):
        """8. A tela de editar deve carregar o lancamento do banco"""
        cursor = MagicMock()
        cursor.fetchone.return_value = (1, 'Venda', '2026-04-10', 200.0, 'Receita', 'Pago')
        banco_falso.return_value.cursor.return_value = cursor

        resposta = self.app.get('/editar/1')
        self.assertIn(b'Venda', resposta.data)

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_09_criar_chama_email(self, banco_falso, email_mock):
        """9. Ao criar um lancamento, o e-mail deve ser chamado"""
        self.app.post('/novo', data=dict(
            descricao='Teste E-mail', data_lancamento='2026-05-01',
            valor='100', tipo_lancamento='Receita', situacao='Pago'
        ))
        email_mock.assert_called_once_with('criado', 'Teste E-mail')

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_10_editar_chama_email(self, banco_falso, email_mock):
        """10. Ao editar um lancamento, o e-mail deve ser chamado"""
        self.app.post('/editar/1', data=dict(
            descricao='Editado', data_lancamento='2026-05-01',
            valor='150', tipo_lancamento='Receita', situacao='Pago'
        ))
        email_mock.assert_called_once_with('atualizado', 'Editado')

    def test_11_fake_salva_e_lista(self):
        """11. O banco fake deve guardar e devolver os itens"""
        banco = BancoFake()
        banco.salvar('Conta de Luz')
        banco.salvar('Aluguel')
        self.assertEqual(banco.listar(), ['Conta de Luz', 'Aluguel'])

    def test_12_fake_comeca_vazio(self):
        """12. O banco fake deve comecar sem nenhum item"""
        banco = BancoFake()
        self.assertEqual(len(banco.listar()), 0)

    def test_13_dummy_nao_faz_nada(self):
        """13. O e-mail dummy pode ser chamado sem nenhum efeito"""
        email = EmailDummy()
        self.assertIsNone(email.enviar('qualquer coisa'))

    @patch('app.get_db_connection')
    def test_14_sem_email_nao_quebra(self, banco_falso):
        """14. Sem e-mail configurado (age como dummy), criar ainda funciona"""
        resposta = self.app.post('/novo', data=dict(
            descricao='Sem e-mail', data_lancamento='2026-05-01',
            valor='50', tipo_lancamento='Despesa', situacao='Pago'
        ))
        self.assertEqual(resposta.status_code, 302)

    def test_15_novo_abre(self):
        """15. A tela de novo lancamento deve abrir"""
        resposta = self.app.get('/novo')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('Novo Lançamento'.encode('utf-8'), resposta.data)

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_16_novo_salva(self, banco_falso, email_mock):
        """16. Salvar um novo lancamento deve redirecionar (302)"""
        resposta = self.app.post('/novo', data=dict(
            descricao='Mercado', data_lancamento='2026-05-01',
            valor='100', tipo_lancamento='Despesa', situacao='Pago'
        ))
        self.assertEqual(resposta.status_code, 302)

    @patch('app.enviar_email_notificacao')
    @patch('app.get_db_connection')
    def test_17_editar_salva(self, banco_falso, email_mock):
        """17. Salvar a edicao de um lancamento deve redirecionar (302)"""
        resposta = self.app.post('/editar/1', data=dict(
            descricao='Mercado editado', data_lancamento='2026-05-01',
            valor='120', tipo_lancamento='Despesa', situacao='Pago'
        ))
        self.assertEqual(resposta.status_code, 302)

    @patch('app.get_db_connection')
    def test_18_excluir(self, banco_falso):
        """18. Excluir um lancamento deve redirecionar (302)"""
        resposta = self.app.get('/excluir/1')
        self.assertEqual(resposta.status_code, 302)

    @patch('app.get_db_connection')
    def test_19_exportar_pdf(self, banco_falso):
        """19. O relatorio exportado deve ser um arquivo PDF"""
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        banco_falso.return_value.cursor.return_value = cursor

        resposta = self.app.get('/exportar_pdf')
        self.assertEqual(resposta.mimetype, 'application/pdf')

    def test_20_pagina_inexistente(self):
        """20. Uma URL que nao existe deve dar erro 404"""
        resposta = self.app.get('/pagina_que_nao_existe')
        self.assertEqual(resposta.status_code, 404)

if __name__ == '__main__':
    unittest.main(verbosity=2)
