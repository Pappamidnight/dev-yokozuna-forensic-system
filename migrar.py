import os
import sys
import shutil
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

# Configuração
FLAT = Path(r"C:\Users\Yokozuna\Desktop\_ACERVO_MASTER\_FLAT")
STORAGE = Path(r"C:\ACERVO\storage")
DB = Path(r"C:\ACERVO\db\acervo.db")

# Criar pastas
STORAGE.mkdir(parents=True, exist_ok=True)

# Conectar DB
conn = sqlite3.connect(str(DB))
cur = conn.cursor()

# Estatísticas
total = 0
importados = 0
duplicados = 0
erros = 0

print("=" * 70)
print("  MIGRAÇÃO _FLAT → C:\\ACERVO\\storage")
print("=" * 70)
print()

# Listar ficheiros
ficheiros = list(FLAT.glob("*"))
total = len(ficheiros)

print(f"Ficheiros a migrar: {total}")
print()

for i, f in enumerate(ficheiros, 1):
    if not f.is_file():
        continue
    
    try:
        # Ler ficheiro
        dados = f.read_bytes()
        tamanho = len(dados)
        
        # Hash
        hash_sha = hashlib.sha256(dados).hexdigest()
        hash_b3 = hashlib.blake2b(dados, digest_size=32).hexdigest()
        
        # Verificar se já existe
        cur.execute("SELECT id FROM ficheiros WHERE hash_sha256 = ?", (hash_sha,))
        existente = cur.fetchone()
        
        if existente:
            duplicados += 1
            continue
        
        # Copiar para storage (estrutura hash/ab/hash)
        subdir = hash_sha[:2]
        destino = STORAGE / "files" / subdir / hash_sha
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(dados)
        
        # Inserir na DB
        s3_key = f"files/{subdir}/{hash_sha}"
        cur.execute("""
            INSERT INTO ficheiros (hash_sha256, hash_blake3, nome, s3_key, tamanho)
            VALUES (?, ?, ?, ?, ?)
        """, (hash_sha, hash_b3, f.name, s3_key, tamanho))
        
        importados += 1
        
        if i % 500 == 0:
            conn.commit()
            print(f"  {i}/{total} — importados: {importados}, duplicados: {duplicados}")
    
    except Exception as e:
        erros += 1
        if erros < 10:
            print(f"  ERRO: {f.name} — {e}")

# Commit final
conn.commit()

# Estatísticas finais
cur.execute("SELECT COUNT(*) FROM ficheiros")
total_db = cur.fetchone()[0]

print()
print("=" * 70)
print("  MIGRAÇÃO CONCLUÍDA")
print("=" * 70)
print(f"  Total processados: {total}")
print(f"  Importados:        {importados}")
print(f"  Duplicados:        {duplicados}")
print(f"  Erros:             {erros}")
print(f"  Total na DB:       {total_db}")
print()
print(f"  Storage: {STORAGE}")
print(f"  DB:      {DB}")
print("=" * 70)

conn.close()
