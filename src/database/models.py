"""
Modelos de dados para o banco SQLite.
Contém as definições de estrutura das tabelas.
"""

# Esquema das tabelas do banco de dados
DATABASE_SCHEMA = {
    'clientes': {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'nome': 'TEXT NOT NULL UNIQUE',
        'classificacao': 'TEXT DEFAULT "Guilherme"',
        'criado_em': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'atualizado_em': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    },
    
    'chamados': {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'cliente_id': 'INTEGER NOT NULL',
        'status': 'TEXT NOT NULL',
        'status_original': 'TEXT',
        'categoria': 'TEXT NOT NULL',
        'observacao': 'TEXT',
        'resolucao': 'TEXT',
        'etapa': 'TEXT DEFAULT "Não iniciado"',
        'data_abertura': 'DATE NOT NULL',
        'data_resolucao': 'DATE',
        'criado_em': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'atualizado_em': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'FOREIGN KEY (cliente_id)': 'REFERENCES clientes(id) ON DELETE CASCADE'
    }
}

def get_create_table_sql():
    """
    Retorna as queries SQL para criação das tabelas.
    
    Returns:
        list: Lista de comandos SQL CREATE TABLE
    """
    queries = []
    
    for table_name, columns in DATABASE_SCHEMA.items():
        column_definitions = []
        foreign_keys = []
        
        for column, definition in columns.items():
            if column.startswith('FOREIGN KEY'):
                foreign_keys.append(f"{column} {definition}")
            else:
                column_definitions.append(f"{column} {definition}")
        
        all_definitions = column_definitions + foreign_keys
        sep = ',\n    '
        joined = sep.join(all_definitions)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {joined}\n);"
        queries.append(query)
    
    return queries


def get_indexes_sql():
    """
    Retorna as queries SQL para criação de índices.
    
    Returns:
        list: Lista de comandos SQL CREATE INDEX
    """
    return [
        "CREATE INDEX IF NOT EXISTS idx_chamados_cliente_id ON chamados(cliente_id);",
        "CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados(status);", 
        "CREATE INDEX IF NOT EXISTS idx_chamados_data_abertura ON chamados(data_abertura);",
        "CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome);"
    ]


# Queries SQL predefinidas para operações comuns
QUERIES = {
    'insert_cliente': """
        INSERT INTO clientes (nome, classificacao) VALUES (?, ?)
    """,
    
    'insert_chamado': """
        INSERT INTO chamados (cliente_id, status, categoria, observacao, data_abertura, etapa)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    
    'update_chamado_resolucao': """
        UPDATE chamados SET 
            resolucao = ?, 
            status_original = COALESCE(status_original, status), 
            status = '7. Status Normal', 
            data_resolucao = CURRENT_DATE, 
            atualizado_em = CURRENT_TIMESTAMP 
        WHERE id = ?
    """,
    
    'reabrir_chamado': """
        UPDATE chamados SET 
            status = COALESCE(status_original, status), 
            status_original = NULL, 
            data_resolucao = NULL, 
            resolucao = NULL,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    """,
    
    'list_chamados_abertos': """
        SELECT c.nome as cliente, c.classificacao, ch.* 
        FROM chamados ch 
        JOIN clientes c ON ch.cliente_id = c.id 
        WHERE (ch.data_resolucao IS NULL OR ch.data_resolucao = '') 
        ORDER BY ch.data_abertura DESC
    """,
    
    'list_chamados_resolvidos': """
        SELECT c.nome as cliente, c.classificacao, ch.id as chamado_id, ch.* 
        FROM chamados ch 
        JOIN clientes c ON ch.cliente_id = c.id 
        WHERE ch.data_resolucao IS NOT NULL AND ch.data_resolucao != '' 
        ORDER BY ch.data_resolucao DESC
    """,
    
    'estatisticas_basicas': """
        SELECT 
            (SELECT COUNT(*) FROM clientes) as total_clientes,
            (SELECT COUNT(*) FROM chamados WHERE data_resolucao IS NULL OR data_resolucao = '') as chamados_abertos,
            (SELECT COUNT(*) FROM chamados WHERE data_resolucao IS NOT NULL AND data_resolucao != '') as chamados_resolvidos
    """
}