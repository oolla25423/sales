#!/usr/bin/env python3
"""
Миграция данных из SQLite в PostgreSQL.

Процесс:
 1. Экспорт данных из локального `db.sqlite3` через `manage.py dumpdata` (с настройкой DB_ENGINE=sqlite3).
 2. Применение миграций в целевой (Postgres) БД.
 3. Импорт данных в Postgres через `manage.py loaddata`.

Запуск:
  python migrate_sqlite_to_postgres.py

Примечание: скрипт вызывает `manage.py` как отдельные процессы и временно переопределяет
переменную окружения `DB_ENGINE` для корректного доступа к исходной SQLite и целевой PostgreSQL.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANAGE_PY = ROOT / 'manage.py'
SQLITE_DB = ROOT / 'db.sqlite3'
DUMP_FILE = ROOT / 'data_dump.json'

def run_manage(cmd_args, extra_env=None, capture_output=False):
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    cmd = [sys.executable, str(MANAGE_PY)] + cmd_args
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, env=env, stdout=subprocess.PIPE if capture_output else None, stderr=subprocess.STDOUT)
    if res.returncode != 0:
        print(f"Command failed (rc={res.returncode}).")
        if capture_output and res.stdout:
            print(res.stdout.decode('utf-8', errors='ignore'))
        return False
    return True


def migrate_sqlite_to_postgres():
    print("="*60)
    print("Migrate SQLite -> PostgreSQL")
    print("="*60)

    if not MANAGE_PY.exists():
        print("Error: manage.py not found. Run this script from project root.")
        return False

    if not SQLITE_DB.exists():
        print("No local SQLite DB (db.sqlite3) found. Running migrations on target DB only.")
        # Ensure migrations applied on Postgres
        return run_manage(['migrate'], extra_env={'DB_ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql')})

    print(f"Found SQLite DB at: {SQLITE_DB}")
    print("This will export data from SQLite and import into the configured PostgreSQL database.")
    ans = input('Continue? (y/N): ').strip().lower()
    if ans != 'y':
        print('Cancelled by user.')
        return False

    if DUMP_FILE.exists():
        print(f"Removing existing dump file: {DUMP_FILE}")
        DUMP_FILE.unlink()

    env_sqlite = {'DB_ENGINE': 'django.db.backends.sqlite3'}
    print('\n1) Exporting data from SQLite...')
    with DUMP_FILE.open('wb') as f:
        cmd = [sys.executable, str(MANAGE_PY), 'dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes', '--natural-foreign', '--natural-primary']
        proc = subprocess.run(cmd, env={**os.environ, **env_sqlite}, stdout=f, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            print('Error exporting data from SQLite:')
            print(proc.stderr.decode('utf-8', errors='ignore'))
            return False

    print(f"Exported data to {DUMP_FILE}")

    env_postgres = {'DB_ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql')}
    print('\n2) Applying migrations on target (PostgreSQL) DB...')
    if not run_manage(['migrate'], extra_env=env_postgres):
        print('Migrations failed on target DB.')
        return False

    print('\n3) Importing data into PostgreSQL...')
    if not run_manage(['loaddata', str(DUMP_FILE)], extra_env=env_postgres):
        print('Failed to import data into PostgreSQL.')
        return False

    print('\nMigration completed successfully!')
    print('You may now remove db.sqlite3 if no longer needed.')
    return True


if __name__ == '__main__':
    ok = migrate_sqlite_to_postgres()
    sys.exit(0 if ok else 1)
