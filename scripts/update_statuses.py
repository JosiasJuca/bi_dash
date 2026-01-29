import sqlite3
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if os.path.basename(__file__) == 'update_statuses.py' else os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'integracoes.db')

if not os.path.exists(DB_PATH):
    print('Erro: integracoes.db não encontrado em', DB_PATH)
    raise SystemExit(1)

# Backup
backup_name = f"integracoes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
backup_path = os.path.join(BASE_DIR, backup_name)
shutil.copy2(DB_PATH, backup_path)
print('Backup criado em:', backup_path)

# Atualizar status
old_statuses = ['3. Novo cliente sem integração', '4. Implantado sem integração']
new_status = '3. Cliente sem integração'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Contar ocorrências antes
placeholders = ','.join(['?'] * len(old_statuses))
cur.execute(f"SELECT COUNT(*) as c FROM chamados WHERE status IN ({placeholders})", old_statuses)
count_status_before = cur.fetchone()['c']
cur.execute(f"SELECT COUNT(*) as c FROM chamados WHERE status_original IN ({placeholders})", old_statuses)
count_status_orig_before = cur.fetchone()['c']

# Atualizar
cur.execute(f"UPDATE chamados SET status = ? WHERE status IN ({placeholders})", (new_status, *old_statuses))
cur.execute(f"UPDATE chamados SET status_original = ? WHERE status_original IN ({placeholders})", (new_status, *old_statuses))
conn.commit()

# Contar ocorrências depois
cur.execute("SELECT COUNT(*) as c FROM chamados WHERE status = ?", (new_status,))
count_status_after = cur.fetchone()['c']
cur.execute("SELECT COUNT(*) as c FROM chamados WHERE status_original = ?", (new_status,))
count_status_orig_after = cur.fetchone()['c']

print('Resumo:')
print(f"- Chamados com status antigo encontrados: {count_status_before}")
print(f"- Chamados com status_original antigo encontrados: {count_status_orig_before}")
print(f"- Chamados agora com status '{new_status}': {count_status_after}")
print(f"- Chamados agora com status_original '{new_status}': {count_status_orig_after}")
print('Pronto.')

conn.close()
