import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\memoria_forense_unificada.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print("Tabelas:", tables)
for t in tables:
    c.execute(f"PRAGMA table_info({t[0]});")
    print(f"Colunas de {t[0]}:", [col[1] for col in c.fetchall()])
