"""
Script para Remover Chamados com Status 3 (Cliente sem integração)
Remove todos os chamados com status "3. Cliente sem integração"
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

# Backup automático
backup_name = f"integracoes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
backup_path = os.path.join(BASE_DIR, backup_name)
shutil.copy2(DB_PATH, backup_path)
print(f'✅ Backup criado em: {backup_name}\n')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Contar chamados com status 3 ANTES
cur.execute("""
    SELECT COUNT(*) as total 
    FROM chamados 
    WHERE status = '3. Cliente sem integração'
""")
total_antes = cur.fetchone()['total']

print(f'📊 Chamados com status "3. Cliente sem integração": {total_antes}')

if total_antes == 0:
    print('\n✅ Nenhum chamado para remover!')
    conn.close()
    raise SystemExit(0)

# Mostrar alguns exemplos do que será removido
print('\n📋 Exemplos de chamados que serão removidos:')
cur.execute("""
    SELECT c.nome as cliente, ch.categoria, ch.data_abertura
    FROM chamados ch
    JOIN clientes c ON ch.cliente_id = c.id
    WHERE ch.status = '3. Cliente sem integração'
    LIMIT 5
""")
for idx, row in enumerate(cur.fetchall(), 1):
    print(f"  {idx}. {row['cliente']} - {row['categoria']} (aberto em {row['data_abertura']})")

if total_antes > 5:
    print(f"  ... e mais {total_antes - 5} chamados")

# Confirmação
print(f'\n⚠️  ATENÇÃO: Você está prestes a REMOVER {total_antes} chamados!')
print('💾 Um backup foi criado automaticamente.')
confirmacao = input('\nDigite "SIM" para confirmar a remoção: ')

if confirmacao.strip().upper() != 'SIM':
    print('\n❌ Operação cancelada pelo usuário.')
    conn.close()
    raise SystemExit(0)

# Remover chamados
print('\n🗑️  Removendo chamados...')
cur.execute("DELETE FROM chamados WHERE status = '3. Cliente sem integração'")
total_removido = cur.rowcount

conn.commit()

# Verificar
cur.execute("""
    SELECT COUNT(*) as total 
    FROM chamados 
    WHERE status = '3. Cliente sem integração'
""")
total_depois = cur.fetchone()['total']

# Estatísticas finais
print(f'\n✅ REMOÇÃO CONCLUÍDA!\n')
print(f'📊 Resumo:')
print(f'  - Chamados removidos: {total_removido}')
print(f'  - Chamados restantes com status 3: {total_depois}')
print(f'  - Backup salvo em: {backup_name}')

# Mostrar chamados restantes por status
print('\n📋 Chamados restantes no sistema:')
cur.execute("SELECT status, COUNT(*) as total FROM chamados WHERE data_resolucao IS NULL GROUP BY status")
for row in cur.fetchall():
    print(f"  - {row['status']}: {row['total']}")

conn.close()

print('\n🚀 Operação finalizada com sucesso!')
