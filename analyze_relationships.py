import sqlite3
from pathlib import Path

DB = Path("c:/Users/tum/Desktop/PythonProject16/game.db")

def conn():
    c = sqlite3.connect(str(DB))
    c.execute("PRAGMA foreign_keys = ON")
    c.row_factory = sqlite3.Row
    return c

print("=== PHAN TICH LIEN KET DATABASE ===")
print()

c = conn()
cur = c.cursor()

# 1. Xem cac bang va cot
print("1. CAC BANG VA COT:")
cur.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name")
tables = [r[0] for r in cur.fetchall()]

for table in tables:
    print(f"\n  Bang: {table}")
    cur.execute(f"PRAGMA table_info({table})")
    for col in cur.fetchall():
        pk = " (PRIMARY KEY)" if col[5] else ""
        print(f"    - {col[1]}: {col[2]}{pk}")

# 2. Xem du lieu
print("\n\n2. DU LIEU TRONG CAC BANG:")
for table in tables:
    cur.execute(f"SELECT COUNT(*) as cnt FROM {table}")
    cnt = cur.fetchone()[0]
    print(f"  {table}: {cnt} dong")

c.close()
print("\nOK!")
