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
                classificacao TEXT DEFAULT 'novo',
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
        
        # Tabela de checklist (integrações por cliente)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                batida BOOLEAN DEFAULT 0,
                escala BOOLEAN DEFAULT 0,
                feriados BOOLEAN DEFAULT 0,
                funcionarios BOOLEAN DEFAULT 0,
                pdv BOOLEAN DEFAULT 0,
                venda BOOLEAN DEFAULT 0,
                sso BOOLEAN DEFAULT 0,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                UNIQUE(cliente_id)
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chamados_cliente ON chamados(cliente_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chamados_categoria ON chamados(categoria)")
        # Garante compatibilidade: se coluna status_original, resolucao ou classificacao não existir em DBs antigos, adiciona
        cursor.execute("PRAGMA table_info(chamados)")
        cols = [r[1] for r in cursor.fetchall()]
        if 'status_original' not in cols:
            cursor.execute("ALTER TABLE chamados ADD COLUMN status_original TEXT")
        if 'resolucao' not in cols:
            cursor.execute("ALTER TABLE chamados ADD COLUMN resolucao TEXT")
        # Clientes: compatibilidade para banco antigo que não tinha classificacao ou atualizado_em
        cursor.execute("PRAGMA table_info(clientes)")
        cols_cli = [r[1] for r in cursor.fetchall()]
        if 'classificacao' not in cols_cli:
            cursor.execute("ALTER TABLE clientes ADD COLUMN classificacao TEXT DEFAULT 'novo'")
        if 'atualizado_em' not in cols_cli:
            # Não usamos DEFAULT CURRENT_TIMESTAMP no ALTER TABLE (algumas versões SQLite reclamam).
            cursor.execute("ALTER TABLE clientes ADD COLUMN atualizado_em TIMESTAMP")
            cursor.execute("UPDATE clientes SET atualizado_em = CURRENT_TIMESTAMP WHERE atualizado_em IS NULL")
        
        print("✅ Banco de dados inicializado com sucesso!")

# ==================== FUNÇÕES DE CLIENTE ====================

def adicionar_cliente(nome, classificacao='novo'):
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
        # preserva status original antes de marcar como '5. Status Normal'
        cursor.execute("SELECT status FROM chamados WHERE id = ?", (chamado_id,))
        row = cursor.fetchone()
        status_atual = row['status'] if row and 'status' in row.keys() else None
        cursor.execute("""
            UPDATE chamados 
            SET status_original = COALESCE(status_original, ?),
                status = '5. Status Normal', 
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
        if target_status == "5. Status Normal" or not target_status:
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
    """Lista todos os chamados não resolvidos"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome as cliente, c.classificacao as classificacao, ch.id as chamado_id, ch.status, 
                   ch.categoria, ch.observacao, ch.data_abertura, ch.data_resolucao
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE ch.data_resolucao IS NULL OR ch.data_resolucao = ''
            ORDER BY ch.data_abertura DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def listar_chamados_resolvidos():
    """Lista todos os chamados resolvidos"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome as cliente, c.classificacao as classificacao, ch.id as chamado_id, ch.status, 
                   ch.categoria, ch.observacao, ch.resolucao, ch.data_abertura, ch.data_resolucao
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE ch.data_resolucao IS NOT NULL
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
        
        # Chamados abertos
        cursor.execute("""
            SELECT COUNT(*) as total FROM chamados 
            WHERE status != '5. Status Normal'
                AND status NOT IN ('3. Cliente sem integração', '4. Integração Parcial')
        """)
        chamados_abertos = cursor.fetchone()['total']
        
        # Chamados resolvidos
        cursor.execute("SELECT COUNT(*) as total FROM chamados WHERE data_resolucao IS NOT NULL")
        chamados_resolvidos = cursor.fetchone()['total']
        
        # Clientes sem integração (inclui status que contenham 'sem integração' ou 'Em construção')
        cursor.execute("""
            SELECT COUNT(DISTINCT cliente_id) as total 
            FROM chamados 
            WHERE status LIKE '%sem integração%'
               OR status LIKE '%constru%'
               OR status = '6. Integração em construção'
        """)
        sem_integracao = cursor.fetchone()['total']
        
        # Distribuição por status
        cursor.execute("""
            SELECT status, COUNT(*) as total 
            FROM chamados 
            WHERE status != '5. Status Normal'
            GROUP BY status
        """)
        por_status = {row['status']: row['total'] for row in cursor.fetchall()}
        
        # Distribuição por categoria
        cursor.execute("""
              SELECT categoria, 
                    SUM(CASE 
                          WHEN status IN (?, ?) 
                              AND (data_resolucao IS NULL OR data_resolucao = '') THEN 1 
                          ELSE 0 END) as abertos,
                    SUM(CASE 
                          WHEN data_resolucao IS NOT NULL 
                              AND COALESCE(status_original, status) IN (?, ?) THEN 1 
                          ELSE 0 END) as resolvidos
              FROM chamados
              WHERE status IN (?, ?) OR COALESCE(status_original, status) IN (?, ?)
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

# ==================== FUNÇÕES DE CHECKLIST ====================

def atualizar_checklist(cliente_id, **kwargs):
    """Atualiza o checklist de um cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verifica se já existe checklist para o cliente
        cursor.execute("SELECT id FROM checklist WHERE cliente_id = ?", (cliente_id,))
        existe = cursor.fetchone()
        
        if existe:
            # Update
            campos = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            valores = list(kwargs.values()) + [cliente_id]
            cursor.execute(f"""
                UPDATE checklist 
                SET {campos}, atualizado_em = CURRENT_TIMESTAMP
                WHERE cliente_id = ?
            """, valores)
        else:
            # Insert
            campos = ", ".join(kwargs.keys())
            placeholders = ", ".join(["?" for _ in kwargs])
            valores = list(kwargs.values())
            cursor.execute(f"""
                INSERT INTO checklist (cliente_id, {campos})
                VALUES (?, {placeholders})
            """, [cliente_id] + valores)

def obter_checklist(cliente_id):
    """Obtém o checklist de um cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM checklist WHERE cliente_id = ?", (cliente_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

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
        # Exclui checklist do cliente
        cursor.execute("DELETE FROM checklist WHERE cliente_id = ?", (cliente_id,))
        # Exclui o cliente
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        return cursor.rowcount > 0

def listar_checklists_pendentes():
    """Lista clientes com integrações pendentes"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.nome as cliente, ch.*
            FROM checklist ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE batida = 0 OR escala = 0 OR feriados = 0 
               OR funcionarios = 0 OR pdv = 0 OR venda = 0 OR sso = 0
            ORDER BY c.nome
        """)
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    # Inicializa o banco quando executado diretamente
    init_db()
