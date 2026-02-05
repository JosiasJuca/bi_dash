"""
Testes básicos para o sistema BI Dashboard.
"""
import unittest
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBasicFunctionality(unittest.TestCase):
    """Testes básicos de funcionalidade."""
    
    def test_imports(self):
        """Testa se todos os módulos podem ser importados."""
        try:
            from src.utils.constants import STATUS_OPTIONS, CATEGORIAS
            from src.utils.helpers import status_badge
            from src.utils.auth import verificar_autenticacao
            from src.database.models import DATABASE_SCHEMA
            self.assertTrue(True, "Imports realizados com sucesso")
        except ImportError as e:
            self.fail(f"Erro de import: {e}")
    
    def test_constants(self):
        """Testa se as constantes estão definidas corretamente."""
        from src.utils.constants import STATUS_OPTIONS, CATEGORIAS
        
        self.assertIsInstance(STATUS_OPTIONS, list)
        self.assertGreater(len(STATUS_OPTIONS), 0)
        self.assertIsInstance(CATEGORIAS, list)
        self.assertGreater(len(CATEGORIAS), 0)
    
    def test_status_badge(self):
        """Testa a função de criação de badges."""
        from src.utils.helpers import status_badge
        
        badge = status_badge("1. Implantado com problema")
        self.assertIn("status-badge", badge)
        self.assertIn("background-color", badge)
    
    def test_database_schema(self):
        """Testa se o esquema do banco está correto."""
        from src.database.models import DATABASE_SCHEMA
        
        self.assertIn('clientes', DATABASE_SCHEMA)
        self.assertIn('chamados', DATABASE_SCHEMA)
        
        # Verifica se as tabelas têm campos obrigatórios
        self.assertIn('id', DATABASE_SCHEMA['clientes'])
        self.assertIn('nome', DATABASE_SCHEMA['clientes'])
        self.assertIn('id', DATABASE_SCHEMA['chamados'])
        self.assertIn('cliente_id', DATABASE_SCHEMA['chamados'])


class TestDatabaseOperations(unittest.TestCase):
    """Testes das operações de banco de dados."""
    
    def setUp(self):
        """Configuração dos testes."""
        # Aqui você pode criar um banco temporário para testes
        pass
    
    def test_database_connection(self):
        """Testa se a conexão com o banco funciona."""
        try:
            from src.database.operations import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
        except Exception as e:
            self.fail(f"Erro na conexão com banco: {e}")


if __name__ == '__main__':
    unittest.main()