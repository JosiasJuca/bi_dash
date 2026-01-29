"""
Script de Limpeza e Atualização do Banco de Dados
Limpa dados desnecessários e prepara para o novo sistema de Checklist
"""
import sqlite3
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'integracoes.db')

if not os.path.exists(DB_PATH):
    print('❌ Erro: integracoes.db não encontrado em', DB_PATH)
    raise SystemExit(1)

# Backup
backup_name = f"integracoes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
backup_path = os.path.join(BASE_DIR, backup_name)
shutil.copy2(DB_PATH, backup_path)
print(f'✅ Backup criado em: {backup_path}')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print('\n📊 ANÁLISE DO BANCO...\n')

# 1. Contar chamados por status
cur.execute("SELECT status, COUNT(*) as total FROM chamados GROUP BY status")
print('Chamados por status ANTES da limpeza:')
for row in cur.fetchall():
    print(f"  - {row['status']}: {row['total']}")

# 2. Verificar tabela checklist (antiga, não é mais usada)
cur.execute("SELECT COUNT(*) as total FROM checklist")
total_checklist = cur.fetchone()['total']
print(f'\nRegistros na tabela checklist (antiga): {total_checklist}')

print('\n🧹 INICIANDO LIMPEZA...\n')

# LIMPEZA 1: Remover chamados duplicados por cliente/categoria/status
print('1. Removendo chamados duplicados...')
cur.execute("""
    DELETE FROM chamados 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM chamados 
        GROUP BY cliente_id, categoria, status, COALESCE(data_resolucao, '')
    )
""")
duplicados_removidos = cur.rowcount
print(f'   ✅ {duplicados_removidos} chamados duplicados removidos')

# LIMPEZA 2: Remover chamados resolvidos muito antigos (opcional - comentado)
# print('2. Removendo chamados resolvidos antigos (mais de 1 ano)...')
# cur.execute("""
#     DELETE FROM chamados 
#     WHERE data_resolucao IS NOT NULL 
#     AND date(data_resolucao) < date('now', '-1 year')
# """)
# antigos_removidos = cur.rowcount
# print(f'   ✅ {antigos_removidos} chamados antigos removidos')

# LIMPEZA 3: Limpar observações vazias
print('2. Limpando observações vazias...')
cur.execute("UPDATE chamados SET observacao = NULL WHERE observacao = '' OR observacao = '-'")
print(f'   ✅ {cur.rowcount} observações limpas')

# LIMPEZA 4: Normalizar datas vazias
print('3. Normalizando datas vazias...')
cur.execute("UPDATE chamados SET data_resolucao = NULL WHERE data_resolucao = ''")
print(f'   ✅ {cur.rowcount} datas normalizadas')

# LIMPEZA 5: Remover clientes inativos sem chamados
print('4. Removendo clientes inativos sem chamados...')
cur.execute("""
    DELETE FROM clientes 
    WHERE ativo = 0 
    AND id NOT IN (SELECT DISTINCT cliente_id FROM chamados)
""")
clientes_inativos = cur.rowcount
print(f'   ✅ {clientes_inativos} clientes inativos removidos')

# LIMPEZA 6: Limpar tabela checklist antiga (não é mais usada)
print('5. Limpando tabela checklist antiga (não é mais utilizada)...')
cur.execute("DELETE FROM checklist")
checklist_removidos = cur.rowcount
print(f'   ✅ {checklist_removidos} registros removidos da tabela checklist')

# ATUALIZAÇÃO 1: Adicionar índices para melhor performance
print('\n🔧 OTIMIZAÇÕES...\n')
print('1. Criando índices adicionais...')
indices = [
    ("idx_chamados_data_abertura", "CREATE INDEX IF NOT EXISTS idx_chamados_data_abertura ON chamados(data_abertura)"),
    ("idx_chamados_data_resolucao", "CREATE INDEX IF NOT EXISTS idx_chamados_data_resolucao ON chamados(data_resolucao)"),
    ("idx_clientes_classificacao", "CREATE INDEX IF NOT EXISTS idx_clientes_classificacao ON clientes(classificacao)"),
]
for idx_name, idx_sql in indices:
    cur.execute(idx_sql)
    print(f'   ✅ Índice {idx_name} criado')

# ATUALIZAÇÃO 2: Garantir que todas colunas necessárias existem
print('2. Verificando schema...')
cur.execute("PRAGMA table_info(chamados)")
colunas_chamados = {row[1] for row in cur.fetchall()}
colunas_necessarias = ['id', 'cliente_id', 'status', 'categoria', 'observacao', 
                       'data_abertura', 'data_resolucao', 'status_original', 
                       'resolucao', 'criado_em', 'atualizado_em']
faltando = set(colunas_necessarias) - colunas_chamados
if faltando:
    print(f'   ⚠️  Colunas faltando: {faltando}')
else:
    print('   ✅ Todas colunas necessárias presentes')

conn.commit()

# ESTATÍSTICAS FINAIS
print('\n📊 ESTATÍSTICAS FINAIS...\n')

cur.execute("SELECT status, COUNT(*) as total FROM chamados WHERE data_resolucao IS NULL GROUP BY status")
print('Chamados ABERTOS por status:')
for row in cur.fetchall():
    print(f"  - {row['status']}: {row['total']}")

cur.execute("SELECT COUNT(*) as total FROM chamados WHERE data_resolucao IS NOT NULL")
resolvidos = cur.fetchone()['total']
print(f'\nTotal de chamados resolvidos: {resolvidos}')

cur.execute("SELECT COUNT(*) as total FROM clientes WHERE ativo = 1")
clientes_ativos = cur.fetchone()['total']
print(f'Total de clientes ativos: {clientes_ativos}')

# Calcular tamanho do banco
db_size = os.path.getsize(DB_PATH) / 1024  # KB
print(f'\nTamanho do banco de dados: {db_size:.2f} KB')

conn.close()

print('\n✅ LIMPEZA E ATUALIZAÇÃO CONCLUÍDAS!\n')
print('Resumo:')
print(f'  - {duplicados_removidos} chamados duplicados removidos')
print(f'  - {clientes_inativos} clientes inativos removidos')
print(f'  - {checklist_removidos} registros da tabela checklist antiga removidos')
print(f'  - Backup salvo em: {backup_name}')
print('\n🚀 Banco otimizado e pronto para uso!')
