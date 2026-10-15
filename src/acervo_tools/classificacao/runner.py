"""Runner — classifica uma arvore e gera outputs."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from acervo_tools.classificacao.classificador_arvore import ClassificadorArvore


RAIZ_DEFAULT = Path(
    r"C:\Users\Yokozuna\Desktop\_SCAN_v4_2026-10-07_214331"
    r"\PROVAS_15547\REFUTACAO_CONSOLIDADA\REPOSITORIOS\LegalAI_Hub"
)
OUT_DIR = Path(r"C:\ACERVO\data\classificacoes")


def _banner(titulo: str):
    print()
    print("=" * 60)
    print(f"  {titulo}")
    print("=" * 60)


def _tabela(dic: dict, limite: int = 20, largura: int = 30) -> str:
    itens = sorted(dic.items(), key=lambda x: -x[1])[:limite]
    linhas = []
    for k, v in itens:
        linhas.append(f"  {k:<{largura}} {v:>6}")
    return "\n".join(linhas) if linhas else "  (vazio)"


def _fmt_bytes(b: int) -> str:
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"


def main():
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ_DEFAULT
    projeto = sys.argv[2] if len(sys.argv) > 2 else raiz.name

    _banner("ACERVO — CLASSIFICADOR DE ARVORE")
    print(f"  Raiz:      {raiz}")
    print(f"  Projeto:   {projeto}")
    print(f"  Existe:    {raiz.exists()}")

    if not raiz.exists():
        print()
        print("[ERRO] Raiz nao existe.")
        sys.exit(1)

    # Classificar
    clf = ClassificadorArvore(projeto=projeto)
    print()
    print("[1/4] A classificar arvore...")
    itens = clf.classificar_arvore(raiz)
    resumo = clf.resumo(itens)
    print(f"  [OK] {resumo['total']} itens classificados")

    # Output estruturado
    print()
    print("[2/4] RESUMO POR TIPO")
    print("-" * 60)
    print(_tabela(resumo["por_tipo"]))

    print()
    print("[3/4] RESUMO POR FUNCAO")
    print("-" * 60)
    print(_tabela(resumo["por_funcao"]))

    print()
    print("      RESUMO POR DOMINIO")
    print("-" * 60)
    print(_tabela(resumo["por_dominio"]))

    print()
    print("      RESUMO POR MODULO")
    print("-" * 60)
    print(_tabela(resumo["por_modulo"]))

    print()
    print("      RESUMO POR SUBCATEGORIA")
    print("-" * 60)
    print(_tabela(resumo["por_subcategoria"]))

    print()
    print("      RESUMO POR EXTENSAO (top 20)")
    print("-" * 60)
    print(_tabela(resumo["por_extensao"], limite=20))

    print()
    print("      ESPACO TOTAL")
    print("-" * 60)
    print(f"  {_fmt_bytes(resumo['espaco_total'])} ({resumo['espaco_total']} bytes)")

    # Guardar JSON
    print()
    print("[4/4] A guardar outputs...")
    ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = OUT_DIR / f"classificacao_{projeto}_{ts}.json"
    out_html = OUT_DIR / f"classificacao_{projeto}_{ts}.html"

    clf.guardar_json(itens, out_json)
    clf.guardar_html(itens, out_html)

    print(f"  [OK] JSON: {out_json}")
    print(f"  [OK] HTML: {out_html}")

    # Amostra
    print()
    print("AMOSTRA (10 itens)")
    print("-" * 60)
    for c in itens[:10]:
        tipo = c.tipo
        func = f" / {c.funcao}" if c.funcao else ""
        dom = f" / {c.dominio}" if c.dominio else ""
        print(f"  [{tipo}{func}{dom}] {c.nome}")

    print()
    print("=" * 60)
    print("  FIM")
    print("=" * 60)
    print()
    print("Outputs gerados:")
    print(f"  - {out_json}")
    print(f"  - {out_html}")


if __name__ == "__main__":
    main()
