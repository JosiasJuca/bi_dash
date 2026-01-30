"""
Sistema de Banco de Dados SQLite para BI de Integrações
Versão simplificada e robusta
"""
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "integracoes.db")

@contextmanager
def get_db():
    """Context manager para conexões seguras"""
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

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabela de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                classificacao TEXT DEFAULT 'Guilherme',
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de chamados/integrações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                categoria TEXT NOT NULL,
                observacao TEXT,
                resolucao TEXT,
                data_abertura DATE NOT NULL,
                data_resolucao DATE,
                status_original TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chamados_cliente ON chamados(cliente_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chamados_categoria ON chamados(categoria)")
        
        print("✅ Banco de dados inicializado!")

# ==================== FUNÇÕES DE CLIENTE ====================

def adicionar_cliente(nome, classificacao='Guilherme'):
    """Adiciona um novo cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, classificacao) VALUES (?, ?)", (nome.strip().title(), classificacao))
        return cursor.lastrowid

def listar_clientes():
    """Lista todos os clientes ativos"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

def buscar_cliente_por_nome(nome):
    """Busca cliente por nome (case insensitive)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE LOWER(nome) = LOWER(?)", (nome.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None

# ==================== FUNÇÕES DE CHAMADO ====================

def adicionar_chamado(cliente_id, status, categoria, observacao="", data_abertura=None):
    """Adiciona um novo chamado"""
    if data_abertura is None:
        data_abertura = datetime.now().date().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chamados (cliente_id, status, categoria, observacao, data_abertura)
            VALUES (?, ?, ?, ?, ?)
        """, (cliente_id, status, categoria, observacao, data_abertura))
        return cursor.lastrowid

def resolver_chamado(chamado_id, data_resolucao=None):
    """Marca um chamado como resolvido"""
    if data_resolucao is None:
        data_resolucao = datetime.now().date().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        # preserva status original antes de marcar como '7. Status Normal'
        cursor.execute("SELECT status FROM chamados WHERE id = ?", (chamado_id,))
        row = cursor.fetchone()
        status_atual = row['status'] if row and 'status' in row.keys() else None
        cursor.execute("""
            UPDATE chamados 
            SET status_original = COALESCE(status_original, ?),
                status = '7. Status Normal', 
                data_resolucao = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status_atual, data_resolucao, chamado_id))

def reabrir_chamado(chamado_id, status_original="1. Implantado com problema"):
    """Reabre um chamado resolvido"""
    with get_db() as conn:
        cursor = conn.cursor()
        # Se existe status_original salvo, usa ele; senão usa o argumento
        cursor.execute("SELECT status_original FROM chamados WHERE id = ?", (chamado_id,))
        row = cursor.fetchone()
        saved = row['status_original'] if row and 'status_original' in row.keys() else None
        target_status = saved if saved else status_original
        if target_status == "7. Status Normal" or not target_status:
            target_status = "1. Implantado com problema"
        cursor.execute("""
            UPDATE chamados 
            SET status = ?, 
                data_resolucao = NULL,
                status_original = NULL,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (target_status, chamado_id))

def listar_chamados_abertos():
    """Lista todos os chamados não resolvidos (todos os status, exclui Geral e N/A)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome as cliente, c.classificacao as classificacao, ch.id as chamado_id, ch.status, 
                   ch.categoria, ch.observacao, ch.data_abertura, ch.data_resolucao
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE (ch.data_resolucao IS NULL OR ch.data_resolucao = '')
                AND ch.categoria != 'Geral'
                AND ch.observacao != 'N/A'
            ORDER BY ch.data_abertura DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def listar_chamados_abertos_completos():
    """Lista todos os chamados não resolvidos (retorna também chamados 'Geral' e N/A)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome as cliente, c.classificacao as classificacao, ch.id as id, ch.status, 
                   ch.categoria, ch.observacao, ch.data_abertura, ch.data_resolucao
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE ch.data_resolucao IS NULL OR ch.data_resolucao = ''
            ORDER BY ch.data_abertura DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def listar_chamados_problemas():
    """Lista apenas chamados com problemas (status 1 e 2, exclui Geral e N/A)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome as cliente, c.classificacao as classificacao, ch.id as chamado_id, ch.status, 
                   ch.categoria, ch.observacao, ch.data_abertura, ch.data_resolucao
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE (ch.data_resolucao IS NULL OR ch.data_resolucao = '')
            AND ch.status IN ('1. Implantado com problema', '2. Implantado refazendo')
            AND ch.categoria != 'Geral'
            AND ch.observacao != 'N/A'
            ORDER BY ch.data_abertura DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def listar_chamados_resolvidos():
    """Lista todos os chamados resolvidos (exclui Geral e N/A)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome as cliente, c.classificacao as classificacao, ch.id as chamado_id, ch.status, 
                   ch.categoria, ch.observacao, ch.resolucao, ch.data_abertura, ch.data_resolucao
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE ch.data_resolucao IS NOT NULL
                AND ch.categoria != 'Geral'
                AND ch.observacao != 'N/A'
            ORDER BY ch.data_resolucao DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def atualizar_classificacao(cliente_id, classificacao):
    """Atualiza a classificacao de um cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE clientes SET classificacao = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (classificacao, cliente_id))
        return cursor.rowcount > 0

def obter_estatisticas():
    """Retorna estatísticas gerais do sistema"""
    with get_db() as conn:
        cursor = conn.cursor()
        status_criticos = ["1. Implantado com problema", "2. Implantado refazendo"]
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE ativo = 1")
        total_clientes = cursor.fetchone()['total']
        
        # Chamados abertos (exclui categoria Geral e N/A)
        cursor.execute("""
            SELECT COUNT(*) as total FROM chamados 
            WHERE status != '7. Status Normal'
                AND status NOT IN ('3. Novo cliente sem integração', '5. Implantado sem integração', '6. Integração Parcial', '8. Integração em construção')
                AND categoria != 'Geral'
                AND observacao != 'N/A'
        """)
        chamados_abertos = cursor.fetchone()['total']
        
        # Chamados resolvidos (exclui categoria Geral e N/A)
        cursor.execute("SELECT COUNT(*) as total FROM chamados WHERE data_resolucao IS NOT NULL AND categoria != 'Geral' AND observacao != 'N/A'")
        chamados_resolvidos = cursor.fetchone()['total']
        
        # Clientes sem integração (inclui status que contenham 'sem integração', 'parcial' ou 'Em construção')
        cursor.execute("""
            SELECT COUNT(DISTINCT cliente_id) as total 
            FROM chamados 
            WHERE status LIKE '%sem integração%'
               OR status LIKE '%parcial%'
               OR status LIKE '%constru%'
               OR status = '8. Integração em construção'
        """)
        sem_integracao = cursor.fetchone()['total']
        
        # Distribuição por status (exclui categoria Geral e N/A)
        cursor.execute("""
            SELECT status, COUNT(*) as total 
            FROM chamados 
            WHERE status != '7. Status Normal'
                AND categoria != 'Geral'
                AND observacao != 'N/A'
            GROUP BY status
        """)
        por_status = {row['status']: row['total'] for row in cursor.fetchall()}
        
        # Distribuição por categoria (exclui Geral e N/A)
        cursor.execute("""
              SELECT categoria, 
                    SUM(CASE 
                          WHEN status IN (?, ?) 
                              AND (data_resolucao IS NULL OR data_resolucao = '')
                              AND observacao != 'N/A' THEN 1 
                          ELSE 0 END) as abertos,
                    SUM(CASE 
                          WHEN data_resolucao IS NOT NULL 
                              AND COALESCE(status_original, status) IN (?, ?)
                              AND observacao != 'N/A' THEN 1 
                          ELSE 0 END) as resolvidos
              FROM chamados
              WHERE (status IN (?, ?) OR COALESCE(status_original, status) IN (?, ?))
                AND categoria != 'Geral'
                AND observacao != 'N/A'
              GROUP BY categoria
           """, status_criticos * 4)
        por_categoria = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_clientes': total_clientes,
            'chamados_abertos': chamados_abertos,
            'chamados_resolvidos': chamados_resolvidos,
            'sem_integracao': sem_integracao,
            'por_status': por_status,
            'por_categoria': por_categoria
        }

# ==================== FUNÇÕES DE GERENCIAMENTO DE CHECKLIST ==

def excluir_chamado(chamado_id):
    """Exclui um chamado do sistema"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chamados WHERE id = ?", (chamado_id,))
        return cursor.rowcount > 0

def excluir_cliente(cliente_id):
    """Exclui um cliente e todos os seus dados relacionados"""
    with get_db() as conn:
        cursor = conn.cursor()
        # Exclui chamados do cliente
        cursor.execute("DELETE FROM chamados WHERE cliente_id = ?", (cliente_id,))
        # Exclui o cliente
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        return cursor.rowcount > 0

def atualizar_cliente_checklist(cliente_id, status_geral, categorias):
    """
    Atualiza o checklist de um cliente de forma completa.
    Remove chamados antigos e cria novos baseado no status selecionado.
    
    Args:
        cliente_id: ID do cliente
        status_geral: Status geral (3, 4 ou 6)
        categorias: Dict com {categoria: estado} onde estado é "✓ OK", "✗ Problema", "🛠️ Em Construção" ou "N/A"
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Remove TODOS os chamados abertos do tipo 3, 4 ou 6 deste cliente (incluindo Geral)
        cursor.execute("""
            DELETE FROM chamados 
            WHERE cliente_id = ? 
            AND (data_resolucao IS NULL OR data_resolucao = '')
            AND status IN ('3. Novo cliente sem integração', '5. Implantado sem integração', '6. Integração Parcial', '8. Integração em construção')
        """, (cliente_id,))
        
        # SEMPRE cria um chamado "Geral" com o status escolhido pelo usuário
        cursor.execute("""
            INSERT INTO chamados (cliente_id, status, categoria, observacao, data_abertura)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente_id, 
            status_geral, 
            "Geral", 
            "Status geral do cliente",
            datetime.now().date().isoformat()
        ))
        
        # Para cada categoria, cria chamado se necessário
        for categoria, estado in categorias.items():
            # OK não precisa de chamado - pula para próxima
            if estado == "✓ OK":
                continue
            
            # N/A cria um chamado especial para aparecer no dashboard
            if estado == "N/A":
                cursor.execute("""
                    INSERT INTO chamados (cliente_id, status, categoria, observacao, data_abertura)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    cliente_id, 
                    status_geral, 
                    categoria, 
                    "N/A",
                    datetime.now().date().isoformat()
                ))
                continue
            
            # Determina o status baseado no estado
            if "🛠" in estado or "Em Construção" in estado:
                # Se tem emoji de martelo ou texto "Em Construção", é status 8
                status_cat = "8. Integração em construção"
            elif "✗" in estado or "Problema" in estado:
                # Se tem X ou texto "Problema", usa o status geral (3 ou 4)
                status_cat = status_geral
            else:
                # Fallback: usa o status geral
                status_cat = status_geral
            
            # Cria o chamado
            cursor.execute("""
                INSERT INTO chamados (cliente_id, status, categoria, observacao, data_abertura)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cliente_id, 
                status_cat, 
                categoria, 
                f"Atualizado via checklist: {estado}",
                datetime.now().date().isoformat()
            ))

def limpar_checklist_cliente(cliente_id):
    """Remove todos os chamados de checklist (status 3, 4, 6) de um cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM chamados 
            WHERE cliente_id = ? 
            AND (data_resolucao IS NULL OR data_resolucao = '')
            AND status IN ('3. Novo cliente sem integração', '5. Implantado sem integração', '6. Integração Parcial', '8. Integração em construção')
        """, (cliente_id,))
        return cursor.rowcount

def deletar_chamados_por_status(status):
    """Deleta todos os chamados com um status específico"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM chamados 
            WHERE status = ?
            AND (data_resolucao IS NULL OR data_resolucao = '')
        """, (status,))
        return cursor.rowcount

def deletar_chamados_por_cliente(cliente_id):
    """Deleta todos os chamados abertos de um cliente específico"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM chamados 
            WHERE cliente_id = ?
            AND (data_resolucao IS NULL OR data_resolucao = '')
        """, (cliente_id,))
        return cursor.rowcount

