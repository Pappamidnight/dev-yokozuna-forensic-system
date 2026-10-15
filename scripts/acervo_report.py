# -*- coding: utf-8 -*-
"""
acervo_report.py - Relatorios consolidados (HTML + JSON + CSV)
==============================================================
Uso:
    python acervo_report.py --html
    python acervo_report.py --json
    python acervo_report.py --snapshot
    python acervo_report.py --diff <snap1> <snap2>
"""
import os
import sys
import json
import argparse
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_core import (
    carregar_csv, gravar_json, garantir_dirs, humano, agora_str, timestamp,
    TIPOS, DIR_RELAT, DIR_SNAP, DIR_MANIF,
)


def gerar_dados():
    """Recolhe dados de todos os manifestos + CSV mestre."""
    regs = carregar_csv(verbose=False)

    cont = Counter(r["tipo"] for r in regs)
    tam = {}
    for r in regs:
        tam[r["tipo"]] = tam.get(r["tipo"], 0) + r["tamanho"]

    dados = {
        "gerado_em": agora_str(),
        "total_regs": len(regs),
        "total_bytes": sum(tam.values()),
        "tipos": [],
    }

    for t in TIPOS:
        dados["tipos"].append({
            "tipo": t,
            "regs": cont.get(t, 0),
            "bytes": tam.get(t, 0),
            "bytes_humano": humano(tam.get(t, 0)),
        })

    dados["tipos"].sort(key=lambda x: -x["bytes"])
    return dados


def gerar_html(dados, output):
    """Gera relatorio HTML com graficos."""
    html = f'''<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>ACERVO - Relatorio</title>
<style>
body {{ font-family: -apple-system, Segoe UI, sans-serif; background: #f5f5f7; color: #1d1d1f; margin: 0; padding: 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ color: #0071e3; border-bottom: 3px solid #0071e3; padding-bottom: 10px; }}
h2 {{ color: #333; margin-top: 30px; }}
.header {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.08); margin-bottom: 20px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
.stat {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.08); text-align: center; }}
.stat .valor {{ font-size: 32px; font-weight: bold; color: #0071e3; }}
.stat .label {{ color: #666; font-size: 13px; margin-top: 5px; }}
table {{ width: 100%; background: white; border-radius: 12px; border-collapse: collapse; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
th {{ background: #0071e3; color: white; padding: 12px; text-align: left; font-weight: 600; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #f9f9f9; }}
.bar {{ height: 20px; background: linear-gradient(90deg, #0071e3, #42a5f5); border-radius: 4px; display: inline-block; vertical-align: middle; }}
.pct {{ color: #666; font-size: 12px; margin-left: 8px; }}
.footer {{ text-align: center; color: #999; margin-top: 30px; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
<h1>📊 ACERVO — Relatorio</h1>
<div class="header">
<p><strong>Gerado em:</strong> {dados['gerado_em']}</p>
</div>

<div class="stats">
<div class="stat"><div class="valor">{dados['total_regs']:,}</div><div class="label">Registos</div></div>
<div class="stat"><div class="valor">{humano(dados['total_bytes'])}</div><div class="label">Tamanho Total</div></div>
<div class="stat"><div class="valor">{len(dados['tipos'])}</div><div class="label">Tipos</div></div>
</div>

<h2>Distribuicao por Tipo</h2>
<table>
<tr><th>Tipo</th><th>Registos</th><th>Tamanho</th><th>%</th><th>Grafico</th></tr>
'''
    total_b = dados["total_bytes"] or 1
    for t in dados["tipos"]:
        pct = 100 * t["bytes"] / total_b
        bar_w = max(2, pct * 4)
        html += f'''<tr>
<td><strong>{t['tipo']}</strong></td>
<td>{t['regs']:,}</td>
<td>{t['bytes_humano']}</td>
<td>{pct:.1f}%</td>
<td><div class="bar" style="width: {bar_w}px;"></div><span class="pct">{pct:.1f}%</span></td>
</tr>
'''
    html += f'''</table>
<div class="footer">ACERVO Report — gerado automaticamente</div>
</div>
</body>
</html>'''

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    return output


def snapshot(dados):
    """Guarda snapshot datado."""
    ts = timestamp()
    path = os.path.join(DIR_SNAP, f"report_{ts}.json")
    gravar_json(path, dados)
    return path


def diff_snapshots(p1, p2):
    """Compara 2 snapshots."""
    with open(p1, encoding="utf-8") as f:
        a = json.load(f)
    with open(p2, encoding="utf-8") as f:
        b = json.load(f)

    print()
    print("=" * 88)
    print("  DIFF DE SNAPSHOTS")
    print("=" * 88)
    print(f"  A: {a['gerado_em']}")
    print(f"  B: {b['gerado_em']}")
    print()
    print(f"  Regs: {a['total_regs']:,} -> {b['total_regs']:,}  "
          f"({b['total_regs']-a['total_regs']:+,})")
    print(f"  Bytes: {humano(a['total_bytes'])} -> {humano(b['total_bytes'])}  "
          f"({humano(b['total_bytes']-a['total_bytes'])})")
    print()

    ma = {t["tipo"]: t for t in a["tipos"]}
    mb = {t["tipo"]: t for t in b["tipos"]}
    print(f"  {'TIPO':<14} {'A':>15} {'B':>15} {'DELTA':>15}")
    print("  " + "-" * 84)
    for t in sorted(set(ma) | set(mb)):
        ta = ma.get(t, {"bytes": 0})
        tb = mb.get(t, {"bytes": 0})
        d = tb["bytes"] - ta["bytes"]
        sinal = "+" if d > 0 else ""
        print(f"  {t:<14} {humano(ta['bytes']):>15} {humano(tb['bytes']):>15} "
              f"{sinal}{humano(d):>15}")
    print("=" * 88)


def main():
    parser = argparse.ArgumentParser(description="Relatorios ACERVO")
    parser.add_argument("--html", action="store_true", help="Gerar HTML")
    parser.add_argument("--json", action="store_true", help="Gerar JSON")
    parser.add_argument("--snapshot", action="store_true", help="Guardar snapshot")
    parser.add_argument("--diff", nargs=2, metavar=("A", "B"), help="Diff snapshots")
    parser.add_argument("--output", help="Output customizado")
    args = parser.parse_args()

    garantir_dirs()

    if args.diff:
        diff_snapshots(args.diff[0], args.diff[1])
        return

    dados = gerar_dados()

    if args.snapshot:
        p = snapshot(dados)
        print(f"[OK] Snapshot: {p}")

    if args.json:
        p = args.output or os.path.join(DIR_RELAT, f"report_{timestamp()}.json")
        gravar_json(p, dados)
        print(f"[OK] JSON: {p}")

    if args.html:
        p = args.output or os.path.join(DIR_RELAT, f"report_{timestamp()}.html")
        gerar_html(dados, p)
        print(f"[OK] HTML: {p}")

    if not (args.html or args.json or args.snapshot):
        parser.print_help()


if __name__ == "__main__":
    main()
