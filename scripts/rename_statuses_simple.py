#!/usr/bin/env python3
"""scripts/rename_statuses_simple.py



Uso:
  # Ver
  python scripts/rename_statuses_simple.py --old "6. Integração Parcial" --new "6. Integração Nova"

  # aplicar 
  python scripts/rename_statuses_simple.py --old "6. Integração Parcial" --new "6. Integração Nova" --apply

O script faz um backup simples do arquivo de banco antes de aplicar se --apply for usado.
"""
import argparse
import os
import shutil
import sqlite3
import sys
from datetime import datetime


def find_db():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    path = os.path.join(repo, 'integracoes.db')
    if not os.path.exists(path):
        print('Banco integracoes.db não encontrado no workspace.', file=sys.stderr)
        sys.exit(2)
    return path


def backup_db(db_path):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = f"{db_path}.backup.{ts}"
    shutil.copy2(db_path, dest)
    return dest


def parse_args():
    p = argparse.ArgumentParser(description='Renomear status (simples)')
    p.add_argument('--old', required=True, help='Status antigo (texto completo)')
    p.add_argument('--new', required=True, help='Novo texto para o status')
    p.add_argument('--apply', action='store_true', help='Aplica as alterações (por padrão é dry-run)')
    return p.parse_args()


def main():
    args = parse_args()
    db = find_db()
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # mostra contagens
    cur.execute('SELECT COUNT(*) FROM chamados WHERE status = ?', (args.old,))
    c1 = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM chamados WHERE status_original = ?', (args.old,))
    c2 = cur.fetchone()[0]

    print(f"Encontrado '{args.old}': status={c1}, status_original={c2}")

    if not args.apply:
        print('Dry-run. Use --apply para efetivar as mudanças.')
        conn.close()
        return

    # backup
    bak = backup_db(db)
    print('Backup criado em:', bak)

    # aplicar
    cur.execute('BEGIN')
    try:
        cur.execute('UPDATE chamados SET status = ? WHERE status = ?', (args.new, args.old))
        u1 = cur.rowcount
        cur.execute('UPDATE chamados SET status_original = ? WHERE status_original = ?', (args.new, args.old))
        u2 = cur.rowcount
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print('Erro ao aplicar:', e, file=sys.stderr)
        sys.exit(1)

    conn.close()
    print(f'Aplicado. Atualizado status={u1}, status_original={u2}')


if __name__ == '__main__':
    main()
