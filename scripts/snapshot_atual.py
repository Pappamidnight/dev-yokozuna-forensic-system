import subprocess, os, csv, time
OUT = r"C:\ACERVO\logs\snapshot_atual.csv"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
t0 = time.time()
print("[1/1] A listar C:\\ACERVO com fd...")
cmd = ["fd", "--type", "f", "--absolute-path", "--hidden", "--no-ignore",
       "--exclude", "node_modules", "--exclude", ".git", "--exclude", "__pycache__",
       ".", r"C:\ACERVO"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, encoding="utf-8", errors="replace", bufsize=1)
total = 0
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Nome", "Caminho", "Tamanho", "DataMod", "Extensao"])
    for linha in proc.stdout:
        p = linha.strip()
        if not p:
            continue
        try:
            st = os.stat(p)
            n = os.path.basename(p)
            ext = os.path.splitext(n)[1].lower()
            dm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
            w.writerow([n, p, st.st_size, dm, ext])
            total += 1
            if total % 5000 == 0:
                print(f"  ... {total:,}", end="\r", flush=True)
        except Exception:
            continue
proc.wait()
print(f"\n[OK] {OUT}")
print(f"  Registos: {total:,}")
print(f"  Tempo: {time.time()-t0:.2f}s")
