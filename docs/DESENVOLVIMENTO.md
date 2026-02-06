# 🚀 Guia de Desenvolvimento

## 🎯 Começando

### Pré-requisitos
- Python 3.9+
- Git
- VSCode (recomendado)

### Configuração do Ambiente
```bash
# 1. Navegar para o diretório do projeto
cd bi_dash

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar aplicação
streamlit run app.py
```

---

## 📁 Estrutura do Projeto

### Organização Modular
```
src/
├── components/    # 🎨 Interface do usuário
├── database/      # 🗄️ Camada de dados
└── utils/         # 🛠️ Utilitários
```

### Princípios de Design
- **Separação de Responsabilidades**: Cada arquivo tem função específica
- **Reutilização**: Componentes modulares e reutilizáveis
- **Manutenibilidade**: Código limpo e bem documentado
- **Escalabilidade**: Estrutura preparada para crescimento

---

## 🎨 Desenvolvimento Frontend

### Componentes Streamlit
Cada componente segue o padrão:
```python
def renderizar_componente():
    """Docstring explicativa do componente."""
    # 1. Configuração inicial
    st.subheader("Título do Componente")
    
    # 2. Obter dados
    dados = database.obter_dados()
    
    # 3. Processar dados se necessário
    dados_processados = processar_dados(dados)
    
    # 4. Renderizar interface
    for item in dados_processados:
        with st.container():
            # Render item
            pass
```

### Boas Práticas de UI
- **Containers**: Use `st.container()` para agrupamento
- **Colunas**: `st.columns()` para layouts responsivos
- **Expanders**: `st.expander()` para conteúdo condicional
- **Forms**: `st.form()` para inputs relacionados

### Styling e CSS
```python
# utils/constants.py
CSS_STYLES = """
<style>
.custom-class {
    /* Estilos personalizados */
}
</style>
"""
```

---

## 🗄️ Desenvolvimento Backend

### Camada de Dados
```python
# database/operations.py
from contextlib import contextmanager

@contextmanager
def get_db():
    """Context manager para conexões seguras."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### Padrões de CRUD
```python
def listar_entidade():
    """Lista todas as entidades."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entidade")
        return [dict(row) for row in cursor.fetchall()]

def adicionar_entidade(nome, categoria):
    """Adiciona nova entidade."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entidade (nome, categoria) VALUES (?, ?)",
            (nome, categoria)
        )
        return cursor.lastrowid
```

### Validação de Dados
```python
def validar_entrada(valor, tipo, obrigatorio=True):
    """Valida entrada do usuário."""
    if obrigatorio and not valor:
        raise ValueError("Campo obrigatório")
    
    if tipo == "email" and "@" not in valor:
        raise ValueError("Email inválido")
    
    return True
```

---

## 🔧 Utilitários e Helpers

### Constantes Centralizadas
```python
# utils/constants.py
STATUS_OPTIONS = [
    "1. Implantado com problema",
    "2. Implantado refazendo",
    # ...
]

CATEGORIAS = [
    "Batida",
    "Escala", 
    # ...
]
```

### Funções Auxiliares
```python
# utils/helpers.py
def status_badge(status):
    """Gera badge colorido para status."""
    cor = obter_cor_status(status)
    return f'<span style="background-color: {cor};">{status}</span>'

def formatar_data(data):
    """Formata data para exibição."""
    return data.strftime('%d/%m/%Y') if data else "N/A"
```

### Sistema de Autenticação
```python
# utils/auth.py
def verificar_autenticacao():
    """Verifica se usuário está autenticado."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    return st.session_state.authenticated
```

---

## 📊 Trabalhando com Dados

### Consultas SQLite
```sql
-- Estatísticas básicas
SELECT COUNT(*) as total FROM clientes WHERE ativo = 1;

-- Dados relacionais
SELECT 
    c.nome as cliente,
    ch.status,
    ch.categoria
FROM clientes c
JOIN chamados ch ON c.id = ch.cliente_id
WHERE ch.data_resolucao IS NULL;
```

### Processamento de Dados
```python
def obter_estatisticas():
    """Calcula estatísticas do dashboard."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
        total_clientes = cursor.fetchone()[0]
        
        # Chamados abertos
        cursor.execute("""
            SELECT COUNT(*) FROM chamados 
            WHERE data_resolucao IS NULL
        """)
        chamados_abertos = cursor.fetchone()[0]
        
        return {
            'total_clientes': total_clientes,
            'chamados_abertos': chamados_abertos
        }
```

---

## 🎯 Adicionando Novas Funcionalidades

### 1. Novo Componente
```python
# src/components/meu_componente.py
def renderizar_meu_componente():
    """Nova funcionalidade."""
    st.subheader("Minha Nova Funcionalidade")
    
    # Implementar lógica
    dados = database.obter_meus_dados()
    
    # Renderizar interface
    for item in dados:
        st.write(item)
```

### 2. Nova Função de Database
```python
# src/database/operations.py
def obter_meus_dados():
    """Obtém dados específicos."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM minha_tabela")
        return [dict(row) for row in cursor.fetchall()]
```

### 3. Integração no App Principal
```python
# app.py
from src.components.meu_componente import renderizar_meu_componente

def main():
    # ... código existente
    
    if opcao_selecionada == "Minha Aba":
        renderizar_meu_componente()
```

---

## 🧪 Testes

### Estrutura de Testes
```
tests/
├── test_database.py      # Testes de banco
├── test_components.py    # Testes de componentes
└── test_utils.py         # Testes de utilitários
```

### Exemplo de Teste
```python
# tests/test_database.py
import unittest
from src.database.operations import listar_clientes

class TestDatabase(unittest.TestCase):
    def test_listar_clientes(self):
        clientes = listar_clientes()
        self.assertIsInstance(clientes, list)
        
    def test_adicionar_cliente(self):
        cliente_id = adicionar_cliente("Teste")
        self.assertIsNotNone(cliente_id)
```

---

## 🚀 Deploy e Produção

### Variáveis de Ambiente
```env
# .env
DASH_SENHA=senha_super_secreta
DEBUG=False
STREAMLIT_SERVER_PORT=8502
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Dockerfile (Opcional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8502

CMD ["streamlit", "run", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  bi-dashboard:
    build: .
    ports:
      - "8502:8502"
    volumes:
      - ./integracoes.db:/app/integracoes.db
    environment:
      - DASH_SENHA=${DASH_SENHA}
```

---

## 📋 Checklist para PRs

### Antes de Submeter
- [ ] Código segue padrões estabelecidos
- [ ] Funções possuem docstrings
- [ ] Testes foram executados
- [ ] Não há código comentado
- [ ] Imports estão organizados
- [ ] Variáveis têm nomes descritivos

### Review Checklist
- [ ] Funcionalidade funciona conforme esperado
- [ ] Código é legível e manutenível
- [ ] Performance não foi degradada
- [ ] Documentação está atualizada
- [ ] Testes cobrem novos cenários

---

## 🐛 Debug e Troubleshooting

### Logs Úteis
```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def minha_funcao():
    logger.info("Iniciando operação")
    try:
        # código
        logger.info("Operação concluída")
    except Exception as e:
        logger.error(f"Erro: {e}")
```

### Debug no Streamlit
```python
# Para debug temporário
if st.checkbox("Debug Mode"):
    st.write("Estado da sessão:", st.session_state)
    st.write("Dados:", dados)
```

### Problemas Comuns
1. **Banco não encontrado**: Verificar caminho em `DB_PATH`
2. **Imports falhando**: Verificar estrutura de diretórios
3. **Session state perdido**: Usar `st.rerun()` com cuidado
4. **Performance lenta**: Otimizar consultas SQL

---

## 📚 Recursos Adicionais

### Documentação
- [Streamlit Docs](https://docs.streamlit.io)
- [SQLite Documentation](https://sqlite.org/docs.html)
- [Plotly Documentation](https://plotly.com/python/)

### Ferramentas Recomendadas
- **VSCode**: Editor com extensões Python
- **DB Browser for SQLite**: Visualizar banco
- **Postman**: Testar APIs (futuro)
- **Git**: Controle de versão

---

*Versão: 2.0 | Guia de Desenvolvimento | Fevereiro 2026*