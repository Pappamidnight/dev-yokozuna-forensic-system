# ============================================================
# V9 TOOLKIT - Acervo Forense
# Menu interativo com todos os scripts reutilizaveis
# ============================================================

$ErrorActionPreference = "Stop"
$BASE     = "C:\ACERVO"
$SCRIPTS  = Join-Path $BASE "scripts"
$DEDUP    = Join-Path $BASE "logs\deduplicado"
$OUTPUT   = Join-Path $BASE "logs\cruzamento_v9"
$SANDBOX  = Join-Path $BASE "SANDBOX"
$TIPOS    = @("database","video","excel","audio","word","pdf","imagem","json","texto","yaml","csv","markdown")

function Show-Menu {
    Clear-Host
    Write-Host "=" * 78 -ForegroundColor Cyan
    Write-Host "  V9 TOOLKIT - ACERVO FORENSE" -ForegroundColor Cyan
    Write-Host "=" * 78 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1]  Validar originais + criar CSVs consolidados" -ForegroundColor Yellow
    Write-Host "  [2]  Mover duplicados para SANDBOX (5 dias)" -ForegroundColor Yellow
    Write-Host "  [3]  Reverter duplicados da SANDBOX" -ForegroundColor Yellow
    Write-Host "  [4]  Ver estado dos CSVs" -ForegroundColor Yellow
    Write-Host "  [5]  Ver manifesto de isolamento" -ForegroundColor Yellow
    Write-Host "  [6]  Cruzamento multi-sinal com Polars" -ForegroundColor Yellow
    Write-Host "  [7]  Pipeline completo (tudo numa vez)" -ForegroundColor Yellow
    Write-Host "  [0]  Sair" -ForegroundColor Red
    Write-Host ""
    Write-Host "=" * 78 -ForegroundColor Cyan
}

# ============================================================
# FUNCAO 1 - VALIDAR E CRIAR CSVs
# ============================================================
function Invoke-Validar {
    Write-Host "`n[A executar] Validar originais..." -ForegroundColor Green
    $py = @"
import os, json, time
import polars as pl

D = r"$DEDUP"
O = r"$OUTPUT"
T = $($TIPOS | ConvertTo-Json -Compress)
T = json.loads(T) if isinstance(T, str) else T

os.makedirs(O, exist_ok=True)

def contar(p):
    if not os.path.isfile(p): return 0
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return max(0, sum(1 for _ in f) - 1)
    except Exception:
        return 0

print("=" * 78)
print("  VALIDACAO DE ORIGINAIS")
print("=" * 78)

frames = []
tot = 0
for t in T:
    p = os.path.join(D, t, f"originais_{t}.csv")
    n = contar(p)
    if n > 0:
        print(f"  [OK] originais_{t}.csv -> {n:,} linhas")
        try:
            df = pl.read_csv(p, infer_schema_length=0, ignore_errors=True, truncate_ragged_lines=True)
            df = df.with_columns(pl.lit(t).alias("tipo"))
            frames.append(df)
            tot += n
        except Exception as e:
            print(f"  ! erro {p}: {e}")
    else:
        print(f"  [FALHA] originais_{t}.csv -> vazio")

if frames:
    co = pl.concat(frames, how="diagonal_relaxed")
    out = os.path.join(O, "ORIGINAIS_CONSOLIDADOS.csv")
    co.write_csv(out)
    print(f"\n  [OK] {out} ({co.height:,} linhas)")

print(f"\n  Total originais: {tot:,}")
"@
    $py | Out-File -FilePath "$SCRIPTS\_tmp_validar.py" -Encoding UTF8
    python -u "$SCRIPTS\_tmp_validar.py"
    Remove-Item "$SCRIPTS\_tmp_validar.py" -ErrorAction SilentlyContinue
    Read-Host "`nPrima Enter para voltar ao menu"
}

# ============================================================
# FUNCAO 2 - MOVER PARA SANDBOX
# ============================================================
function Invoke-Mover {
    Write-Host "`n[A executar] Mover duplicados para SANDBOX..." -ForegroundColor Green
    $py = @"
import os, json, shutil, time
from datetime import datetime, timedelta

D = r"$DEDUP"
S = r"$SANDBOX\duplicados_isolados"
M = r"$SANDBOX\manifesto_isolamento.json"
T = $($TIPOS | ConvertTo-Json -Compress)
T = json.loads(T) if isinstance(T, str) else T
DIAS = 5

os.makedirs(S, exist_ok=True)
dt = datetime.now()
dl = dt + timedelta(days=DIAS)
mov, fal, tb = [], [], 0

print("=" * 78)
print(f"  MOVER DUPLICADOS -> SANDBOX ({DIAS} DIAS)")
print("=" * 78)

for t in T:
    src = os.path.join(D, t, f"duplicados_{t}.csv")
    dst = os.path.join(S, t, f"duplicados_{t}.csv")
    if not os.path.isfile(src):
        print(f"  [SKIP] duplicados_{t}.csv nao existe")
        fal.append(t)
        continue
    try:
        sz = os.path.getsize(src)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        mov.append({"tipo": t, "origem": src, "destino": dst, "bytes": sz})
        tb += sz
        print(f"  [OK] duplicados_{t}.csv -> {sz:,} bytes")
    except Exception as e:
        print(f"  [ERRO] {t}: {e}")
        fal.append(t)

json.dump({
    "data": dt.isoformat(),
    "liberta": dl.isoformat(),
    "dias": DIAS,
    "sandbox": S,
    "total": len(mov),
    "bytes": tb,
    "ficheiros": mov,
    "falhas": fal,
}, open(M, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"\n  Movidos: {len(mov)}/{len(T)}")
print(f"  Bytes: {tb:,}")
print(f"  Liberta: {dl.isoformat()}")
print(f"  Manifesto: {M}")
"@
    $py | Out-File -FilePath "$SCRIPTS\_tmp_mover.py" -Encoding UTF8
    python -u "$SCRIPTS\_tmp_mover.py"
    Remove-Item "$SCRIPTS\_tmp_mover.py" -ErrorAction SilentlyContinue
    Read-Host "`nPrima Enter para voltar ao menu"
}

# ============================================================
# FUNCAO 3 - REVERTER
# ============================================================
function Invoke-Reverter {
    Write-Host "`n[A executar] Reverter duplicados da SANDBOX..." -ForegroundColor Green
    $confirma = Read-Host "Tem a certeza? (S/N)"
    if ($confirma -ne "S" -and $confirma -ne "s") {
        Write-Host "Cancelado." -ForegroundColor Yellow
        Start-Sleep 1
        return
    }
    $py = @"
import json, shutil, os
M = r"$SANDBOX\manifesto_isolamento.json"
if not os.path.isfile(M):
    print("Manifesto nao encontrado:", M)
else:
    m = json.load(open(M, encoding="utf-8"))
    n = 0
    for f in m["ficheiros"]:
        if os.path.isfile(f["destino"]):
            os.makedirs(os.path.dirname(f["origem"]), exist_ok=True)
            shutil.move(f["destino"], f["origem"])
            n += 1
            print(f"  [OK] {f['tipo']}")
    print(f"\nRevertidos: {n}/{len(m['ficheiros'])}")
"@
    $py | Out-File -FilePath "$SCRIPTS\_tmp_reverter.py" -Encoding UTF8
    python -u "$SCRIPTS\_tmp_reverter.py"
    Remove-Item "$SCRIPTS\_tmp_reverter.py" -ErrorAction SilentlyContinue
    Read-Host "`nPrima Enter para voltar ao menu"
}

# ============================================================
# FUNCAO 4 - VER ESTADO
# ============================================================
function Show-Estado {
    Clear-Host
    Write-Host "=" * 78 -ForegroundColor Cyan
    Write-Host "  ESTADO DOS CSVs" -ForegroundColor Cyan
    Write-Host "=" * 78 -ForegroundColor Cyan
    Write-Host ""

    Write-Host "--- Consolidados ($OUTPUT) ---" -ForegroundColor Yellow
    if (Test-Path $OUTPUT) {
        Get-ChildItem $OUTPUT -Filter "*.csv" -ErrorAction SilentlyContinue |
            Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,2)}}, LastWriteTime |
            Format-Table -Auto
    } else {
        Write-Host "  (pasta nao existe)" -ForegroundColor DarkGray
    }

    Write-Host "`n--- Originais por tipo ($DEDUP) ---" -ForegroundColor Yellow
    foreach ($t in $TIPOS) {
        $p = Join-Path $DEDUP "$t\originais_$t.csv"
        if (Test-Path $p) {
            $kb = [math]::Round((Get-Item $p).Length/1KB, 2)
            Write-Host "  [OK] originais_$t.csv - $kb KB" -ForegroundColor Green
        } else {
            Write-Host "  [--] originais_$t.csv" -ForegroundColor DarkGray
        }
    }

    Write-Host "`n--- Duplicados por tipo ($DEDUP) ---" -ForegroundColor Yellow
    foreach ($t in $TIPOS) {
        $p = Join-Path $DEDUP "$t\duplicados_$t.csv"
        if (Test-Path $p) {
            $kb = [math]::Round((Get-Item $p).Length/1KB, 2)
            Write-Host "  [OK] duplicados_$t.csv - $kb KB" -ForegroundColor Green
        } else {
            Write-Host "  [--] duplicados_$t.csv" -ForegroundColor DarkGray
        }
    }

    Write-Host "`n--- SANDBOX ($SANDBOX) ---" -ForegroundColor Yellow
    if (Test-Path "$SANDBOX\duplicados_isolados") {
        $count = (Get-ChildItem "$SANDBOX\duplicados_isolados" -Recurse -Filter "*.csv" -ErrorAction SilentlyContinue).Count
        Write-Host "  Ficheiros isolados: $count" -ForegroundColor Cyan
        Write-Host "  Manifesto: $(Test-Path "$SANDBOX\manifesto_isolamento.json")" -ForegroundColor Cyan
    } else {
        Write-Host "  (SANDBOX vazia)" -ForegroundColor DarkGray
    }

    Read-Host "`nPrima Enter para voltar ao menu"
}

# ============================================================
# FUNCAO 5 - VER MANIFESTO
# ============================================================
function Show-Manifesto {
    $m = Join-Path $SANDBOX "manifesto_isolamento.json"
    if (Test-Path $m) {
        Clear-Host
        Write-Host "=" * 78 -ForegroundColor Cyan
        Write-Host "  MANIFESTO DE ISOLAMENTO" -ForegroundColor Cyan
        Write-Host "=" * 78 -ForegroundColor Cyan
        Get-Content $m -Raw
    } else {
        Write-Host "Manifesto nao existe." -ForegroundColor Yellow
    }
    Read-Host "`nPrima Enter para voltar ao menu"
}

# ============================================================
# FUNCAO 6 - CRUZAMENTO POLARS
# ============================================================
function Invoke-Cruzamento {
    Write-Host "`n[A executar] Cruzamento multi-sinal..." -ForegroundColor Green
    $py = @"
import os, json, time, re
import polars as pl
from datetime import datetime

D = r"$DEDUP"
O = r"$OUTPUT"
MOD = "DRYRUN"
MIN_SCORE = 70
T = $($TIPOS | ConvertTo-Json -Compress)
T = json.loads(T) if isinstance(T, str) else T

RANK_ORD = {
    "ACERVO_CONSOLIDADO": 0, "VAULT_CENTRAL": 1,
    "DOSSIERS_MASTER": 2, "01_WORK": 3,
    "DEV": 4, "LEGACY_COOKBOOK": 5,
    "LEGACY_ARQUIVO_HISTORICO": 6,
}
RE_SUF = re.compile(r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$", re.IGNORECASE)

def rank_expr(col):
    e = pl.lit(7, dtype=pl.Int8)
    for nome, r in sorted(RANK_ORD.items(), key=lambda x: -x[1]):
        e = pl.when(col.str.to_uppercase().str.contains(nome, literal=True)).then(pl.lit(r, dtype=pl.Int8)).otherwise(e)
    return e

os.makedirs(O, exist_ok=True)
t0 = time.time()

print("=" * 78)
print("  CRUZAMENTO MULTI-SINAL V9")
print("=" * 78)

frames = []
for t in T:
    p = os.path.join(D, t, f"originais_{t}.csv")
    if os.path.isfile(p):
        try:
            df = pl.read_csv(p, infer_schema_length=0, ignore_errors=True, truncate_ragged_lines=True)
            cols = {c.lower(): c for c in df.columns}
            cn = cols.get("nome"); cc = cols.get("caminho")
            if cn and cc:
                df = df.select([
                    pl.lit(t).alias("tipo"),
                    pl.col(cn).cast(pl.Utf8).alias("nome"),
                    pl.col(cc).cast(pl.Utf8).alias("caminho"),
                ])
                frames.append(df)
        except Exception as e:
            print(f"  ! {t}: {e}")

if not frames:
    print("  Nenhum dado. Abortar.")
else:
    df = pl.concat(frames, how="diagonal_relaxed")
    print(f"  Registos: {df.height:,}")
    df = df.with_columns([
        pl.col("nome").str.to_lowercase().str.replace(RE_SUF.pattern, "").alias("stem"),
        rank_expr(pl.col("caminho")).alias("rank"),
    ])
    df = df.with_columns(pl.col("stem").cum_count().over(["stem"]).alias("pos"))
    orig = df.filter(pl.col("pos") == 0)
    dup = df.filter(pl.col("pos") > 0)
    out = orig
    print(f"  Originais: {orig.height:,}")
    print(f"  Duplicados: {dup.height:,}")
    p_out = os.path.join(O, "cruzamento_v9.csv")
    out.write_csv(p_out)
    print(f"  [OK] {p_out}")

print(f"\n  Tempo: {time.time()-t0:.2f}s")
"@
    $py | Out-File -FilePath "$SCRIPTS\_tmp_cruz.py" -Encoding UTF8
    python -u "$SCRIPTS\_tmp_cruz.py"
    Remove-Item "$SCRIPTS\_tmp_cruz.py" -ErrorAction SilentlyContinue
    Read-Host "`nPrima Enter para voltar ao menu"
}

# ============================================================
# FUNCAO 7 - PIPELINE COMPLETO
# ============================================================
function Invoke-PipelineCompleto {
    Write-Host "`n[A executar] PIPELINE COMPLETO..." -ForegroundColor Green
    $confirma = Read-Host "Executar tudo (validar + consolidar + mover)? (S/N)"
    if ($confirma -ne "S" -and $confirma -ne "s") {
        Write-Host "Cancelado." -ForegroundColor Yellow
        Start-Sleep 1
        return
    }
    Invoke-Validar
    Invoke-Mover
    Write-Host "`n[OK] Pipeline completo terminado!" -ForegroundColor Green
    Read-Host "Prima Enter para voltar ao menu"
}

# ============================================================
# LOOP PRINCIPAL
# ============================================================
while ($true) {
    Show-Menu
    $opcao = Read-Host "Escolha uma opcao"
    switch ($opcao) {
        "1" { Invoke-Validar }
        "2" { Invoke-Mover }
        "3" { Invoke-Reverter }
        "4" { Show-Estado }
        "5" { Show-Manifesto }
        "6" { Invoke-Cruzamento }
        "7" { Invoke-PipelineCompleto }
        "0" { Write-Host "`nAdeus!" -ForegroundColor Cyan; exit }
        default { Write-Host "Opcao invalida." -ForegroundColor Red; Start-Sleep 1 }
    }
}
