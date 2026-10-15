# -*- coding: utf-8 -*-
"""
ler_provas.py - Le os YAML de provas e gera relatorios
=======================================================
Uso:
    python ler_provas.py
    python ler_provas.py --prova PRV-001
    python ler_provas.py --alegacao AL-09
    python ler_provas.py --classificacao PARCIAL
"""
import os
import sys
import json
import argparse
from datetime import datetime

try:
    import yaml
except ImportError:
    print("[ERRO] Instalar: pip install pyyaml")
    sys.exit(1)

GESTAO = r"C:\ACERVO\gestao_provas"
PROVAS = os.path.join(GESTAO, "provas")
INDICES = os.path.join(GESTAO, "indices")
RELATORIOS = os.path.join(GESTAO, "relatorios")

os.makedirs(RELATORIOS, exist_ok=True)


def carregar_todas():
    """Carrega todos os YAML de provas."""
    provas = []
    if not os.path.isdir(PROVAS):
        return provas
    for f in sorted(os.listdir(PROVAS)):
        if not f.endswith((".yaml", ".yml")):
            continue
        path = os.path.join(PROVAS, f)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                dados = yaml.safe_load(fp)
                dados["_ficheiro_yaml"] = path
                provas.append(dados)
        except Exception as e:
            print(f"[ERRO] {f}: {e}")
    return provas


def cor(c):
    return {
        "CONFIRMADA": "\033[92m",
        "PARCIAL":    "\033[93m",
        "CONTRADITA": "\033[91m",
        "LACUNA":     "\033[96m",
        "NEUTRA":     "\033[90m",
    }.get(c, "")


def mostrar(p, detalhado=True):
    c = cor(p.get("classificacao", ""))
    reset = "\033[0m"
    print()
    print("=" * 78)
    print(f"  {p.get('id', '?')}  |  {p.get('tipo', '?')}  |  {p.get('tema', '?')}")
    print("=" * 78)
    print(f"  Classificacao: {c}{p.get('classificacao', '?')}{reset}")
    print(f"  Peso:          {p.get('peso', '?')}")

    f = p.get("fonte", {})
    if f:
        print(f"  Ficheiro:      {f.get('ficheiro', '?')}")
        print(f"  Localizador:   {f.get('pagina', '?')}")

    if not detalhado:
        return

    if p.get("extratos"):
        print()
        print("  EXTRATOS:")
        for e in p["extratos"]:
            txt = e.get("texto", "")
            loc = e.get("local") or e.get("data_hora") or ""
            print(f"    - \"{txt}\"  ({loc})")

    if p.get("alegacoes_relacionadas"):
        print()
        print("  ALEGACOES RELACIONADAS:")
        for a in p["alegacoes_relacionadas"]:
            print(f"    - {a.get('id', '?')} ({a.get('tipo', '?')})")

    if p.get("lacunas"):
        print()
        print("  LACUNAS:")
        for l in p["lacunas"]:
            print(f"    - {l}")

    if p.get("refutacao"):
        r = p["refutacao"]
        print()
        print(f"  REFUTACAO: {r.get('tese', '?')}")
        if r.get("argumentos"):
            print("    Argumentos:")
            for a in r["argumentos"]:
                print(f"      - {a}")

    if p.get("notas"):
        print()
        print("  NOTAS:")
        for linha in str(p["notas"]).strip().split("\n"):
            print(f"    {linha}")


def gerar_relatorio():
    """Gera relatorio HTML + JSON."""
    provas = carregar_todas()
    if not provas:
        print("[AVISO] Nenhuma prova encontrada")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON
    json_path = os.path.join(RELATORIOS, f"relatorio_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(provas, f, indent=2, ensure_ascii=False, default=str)

    # HTML
    html = """<!DOCTYPE html>
<html lang="pt">
<head><meta charset="UTF-8"><title>Relatorio de Provas</title>
<style>
body { font-family: -apple-system, Segoe UI, sans-serif; background: #f5f5f7; margin: 0; padding: 20px; }
.container { max-width: 1200px; margin: 0 auto; }
h1 { color: #0071e3; }
.prova { background: white; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.prova h2 { margin: 0 0 10px 0; color: #333; }
.tag { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-right: 8px; }
.tag.CONFIRMADA { background: #d4edda; color: #155724; }
.tag.PARCIAL { background: #fff3cd; color: #856404; }
.tag.CONTRADITA { background: #f8d7da; color: #721c24; }
.tag.LACUNA { background: #d1ecf1; color: #0c5460; }
.tag.peso { background: #e2e3e5; color: #383d41; }
.tag.critico { background: #dc3545; color: white; }
.extrato { background: #f8f9fa; padding: 10px; border-left: 3px solid #0071e3; margin: 8px 0; font-style: italic; }
.lacuna { color: #856404; }
</style></head><body>
<div class="container">
<h1>Relatorio de Provas - Caso 15547</h1>
"""
    for p in provas:
        c = p.get("classificacao", "")
        peso = p.get("peso", "")
        html += f"""
<div class="prova">
  <h2>{p.get('id', '?')} - {p.get('tema', '?')}</h2>
  <span class="tag {c}">{c}</span>
  <span class="tag peso {peso}">{peso}</span>
  <span class="tag">{p.get('tipo', '?')}</span>
"""
        f = p.get("fonte", {})
        if f:
            html += f"<p><strong>Ficheiro:</strong> {f.get('ficheiro', '?')}</p>"
            html += f"<p><strong>Localizador:</strong> {f.get('pagina', '?')}</p>"

        if p.get("extratos"):
            html += "<h3>Extratos</h3>"
            for e in p["extratos"]:
                loc = e.get("local") or e.get("data_hora") or ""
                html += f'<div class="extrato">"{e.get("texto", "")}" <small>({loc})</small></div>'

        if p.get("alegacoes_relacionadas"):
            html += "<h3>Alegacoes relacionadas</h3><ul>"
            for a in p["alegacoes_relacionadas"]:
                html += f"<li>{a.get('id', '?')} ({a.get('tipo', '?')})</li>"
            html += "</ul>"

        if p.get("lacunas"):
            html += "<h3>Lacunas</h3><ul>"
            for l in p["lacunas"]:
                html += f'<li class="lacuna">{l}</li>'
            html += "</ul>"

        if p.get("refutacao"):
            r = p["refutacao"]
            html += f"<h3>Refutacao</h3><p><strong>{r.get('tese', '?')}</strong></p>"
            if r.get("argumentos"):
                html += "<ul>"
                for a in r["argumentos"]:
                    html += f"<li>{a}</li>"
                html += "</ul>"

        html += "</div>"

    html += "</div></body></html>"

    html_path = os.path.join(RELATORIOS, f"relatorio_{ts}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print()
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] HTML: {html_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prova", help="ID da prova (ex: PRV-001)")
    parser.add_argument("--alegacao", help="Alegacao (ex: AL-09)")
    parser.add_argument("--classificacao", help="Filtrar por classificacao")
    parser.add_argument("--relatorio", action="store_true", help="Gerar HTML+JSON")
    args = parser.parse_args()

    if args.relatorio:
        gerar_relatorio()
        return

    provas = carregar_todas()
    if not provas:
        print("[AVISO] Nenhuma prova encontrada em", PROVAS)
        return

    if args.prova:
        for p in provas:
            if p.get("id") == args.prova:
                mostrar(p)
                return
        print(f"[ERRO] {args.prova} nao encontrada")
        return

    if args.alegacao:
        alvo = args.alegacao.upper()
        for p in provas:
            for a in p.get("alegacoes_relacionadas", []):
                if a.get("id") == alvo:
                    mostrar(p, detalhado=False)
                    break
        return

    if args.classificacao:
        for p in provas:
            if p.get("classificacao") == args.classificacao:
                mostrar(p, detalhado=False)
        return

    # Todas
    print()
    print("=" * 78)
    print(f"  PROVAS ({len(provas)})")
    print("=" * 78)
    for p in provas:
        mostrar(p, detalhado=True)


if __name__ == "__main__":
    main()
