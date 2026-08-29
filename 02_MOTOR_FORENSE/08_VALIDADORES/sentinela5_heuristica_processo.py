#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELA-5 — heurística por processo (v1.1).

Determinístico. Zero LLM. Não inventa qualidade processual.
O campo processo só é atribuído com número Citius (ou forma curta controlada).
Palavras-chave e clusters são etiquetas, não identidade.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable

# Forma canónica Citius: NNNNN/AA.DTCCCC  ex. 3719/25.0T8LSB
# Nao usar \b: underscore e letra/digito, e os nomes sao 15547-26.0T8LSB.docx
_EDGE = r"(?:(?<![A-Za-z0-9])|(?<=_))"
_END = r"(?![A-Za-z0-9])"
CITIUS_RE = re.compile(
    _EDGE + r"(\d{1,7})[/_\-.](\d{2})\.(\d)([A-Z0-9]{2,8})" + _END,
    re.IGNORECASE,
)
CITIUS_SHORT_RE = re.compile(
    _EDGE + r"(?:proc(?:esso)?\.?\s*)?(\d{1,7})[/_\-](\d{2})" + _END,
    re.IGNORECASE,
)

MIN_CONF_ASSIGN = 0.70
MIN_CONF_SHORT = 0.55
MIN_MARGIN = 0.15


def _fold(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()


def _norm_citius(num: str, year: str, check: str, court: str) -> str:
    return f"{int(num)}/{year}.{check}{court.upper()}"


def _slug(citius: str) -> str:
    return citius.replace("/", "-")


@dataclass(frozen=True)
class ProcessoRegisto:
    citius: str
    tribunal_declarado: str
    tipo_declarado: str
    notas: str
    keywords: tuple[str, ...]
    # keywords NUNCA atribuem processo sozinhas


PROCESSOS: dict[str, ProcessoRegisto] = {
    "15547/26.0T8LSB": ProcessoRegisto(
        citius="15547/26.0T8LSB",
        tribunal_declarado="Juízo Central Cível de Lisboa (declarado; confirmar no despacho)",
        tipo_declarado="Ação (qualificação jurídica a confirmar no articulado)",
        notas="Não usar 'Centenário' como prova de processo: colide com CLUSTER_SPARK.",
        keywords=(
            "reivindicacao",
            "esbulho",
            "1311",
            "art. 1311",
        ),
    ),
    "3719/25.0T8LSB": ProcessoRegisto(
        citius="3719/25.0T8LSB",
        tribunal_declarado="Juízo Local Cível de Lisboa / TRL (conforme fase)",
        tipo_declarado="Providência cautelar (fase e qualidade das partes a confirmar na peça)",
        notas=(
            "Qualidade Nuno=Requerente nesta ficha está em tensão com declarações "
            "do utilizador (requerido). Heurística NÃO decide a qualidade.",
        ),
        keywords=(
            "providencia cautelar",
            "arbitramento",
            "reparacao provisoria",
        ),
    ),
    "23142/22.7T8LSB": ProcessoRegisto(
        citius="23142/22.7T8LSB",
        tribunal_declarado="Juízo de Execução de Lisboa (declarado)",
        tipo_declarado="Execução / embargos (a confirmar no título)",
        notas="Palavra 'penhora' é transversal; só reforça se o Citius já bateu.",
        keywords=("embargos", "penhora", "execucao"),
    ),
    "10153/24.7T8LSB": ProcessoRegisto(
        citius="10153/24.7T8LSB",
        tribunal_declarado="Juízo de Execução de Lisboa (declarado)",
        tipo_declarado="Oposição à execução (a confirmar no articulado)",
        notas="Não usar o apelido 'Duarte' como sinal: colide com o próprio requerido.",
        keywords=("oposicao", "compensacao", "retencoes", "tpa"),
    ),
}

KNOWN_BY_NUM_YEAR: dict[tuple[int, str], str] = {
    (15547, "26"): "15547/26.0T8LSB",
    (3719, "25"): "3719/25.0T8LSB",
    (23142, "22"): "23142/22.7T8LSB",
    (10153, "24"): "10153/24.7T8LSB",
}

# Cluster NÃO é processo judicial. Exige 2 sinais de grupos distintos.
CLUSTER_GRUPOS: dict[str, tuple[str, ...]] = {
    "marca": ("spark", "venture partners", "venturepartners"),
    "regulador": ("cmvm",),
    "societario": ("cessao de quotas", "contrato de cessao", "pacto social"),
}


@dataclass
class Hit:
    citius: str | None
    slug: str | None
    confianca: float
    origem: str
    evidencias: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    cluster: str | None = None
    suporte: str = "NAO_INDICIADO"  # DOCUMENTADO | PARCIAL | NAO_INDICIADO
    ambiguo: bool = False
    candidatos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "citius": self.citius,
            "slug": self.slug,
            "confianca": self.confianca,
            "origem": self.origem,
            "evidencias": list(self.evidencias),
            "tags": list(self.tags),
            "cluster": self.cluster,
            "suporte": self.suporte,
            "ambiguo": self.ambiguo,
            "candidatos": list(self.candidatos),
        }


def _keyword_boost(folded: str, keys: Iterable[str]) -> tuple[float, list[str]]:
    hits = []
    for k in keys:
        if _fold(k) in folded:
            hits.append(k)
    if not hits:
        return 0.0, []
    return min(0.12 * len(hits), 0.24), hits


def _detect_cluster(folded: str) -> tuple[str | None, list[str]]:
    grupos_hit: list[str] = []
    ev: list[str] = []
    for g, tokens in CLUSTER_GRUPOS.items():
        for t in tokens:
            if t in folded:
                grupos_hit.append(g)
                ev.append(t)
                break
    if len(set(grupos_hit)) >= 2:
        return "CLUSTER_SPARK", ev
    return None, ev


def detectar_processo(texto: str = "", nome_ficheiro: str = "") -> Hit:
    """Devolve no máximo um processo Citius + tags/cluster.

    Nome do ficheiro pesa mais do que o corpo.
    Palavras-chave nunca atribuem processo sem número.
    """
    nome = nome_ficheiro or ""
    corpo = texto or ""
    blob_nome = nome
    blob_corpo = corpo
    folded = _fold(f"{nome} {corpo}")

    scores: dict[str, float] = {}
    evid: dict[str, list[str]] = {}

    def add(citius: str, pts: float, ev: str) -> None:
        scores[citius] = scores.get(citius, 0.0) + pts
        evid.setdefault(citius, []).append(ev)

    for fonte, blob, peso_base in (
        ("filename", blob_nome, 0.98),
        ("body", blob_corpo, 0.88),
    ):
        for m in CITIUS_RE.finditer(blob):
            citius = _norm_citius(*m.groups())
            add(citius, peso_base, f"{fonte}:citius:{citius}")

        for m in CITIUS_SHORT_RE.finditer(blob):
            num, year = int(m.group(1)), m.group(2)
            known = KNOWN_BY_NUM_YEAR.get((num, year))
            if known and known not in scores:
                # forma curta só se ainda não houver Citius completo deste processo
                add(known, 0.58 if fonte == "filename" else 0.50, f"{fonte}:short:{num}/{year}")

    for citius, reg in PROCESSOS.items():
        boost, khits = _keyword_boost(folded, reg.keywords)
        if boost and citius in scores:
            add(citius, boost, "keywords:" + ",".join(khits))
        elif boost and citius not in scores:
            # guarda evidência sem criar candidato de processo
            evid.setdefault("_tags", []).extend(khits)

    cluster, cluster_ev = _detect_cluster(folded)

    tags = list(dict.fromkeys(evid.get("_tags", [])))
    if cluster:
        tags.append(cluster)

    # Processos conhecidos vs Citius desconhecido (ainda assim devolver o número)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    if not ranked:
        return Hit(
            citius=None,
            slug=None,
            confianca=0.0,
            origem="none",
            evidencias=cluster_ev,
            tags=tags,
            cluster=cluster,
            suporte="NAO_INDICIADO",
        )

    best_id, best_sc = ranked[0]
    second_sc = ranked[1][1] if len(ranked) > 1 else 0.0
    ambiguo = (second_sc > 0) and ((best_sc - second_sc) < MIN_MARGIN)

    # Cap
    conf = min(best_sc, 1.0)
    origem = evid[best_id][0].split(":")[0] if evid.get(best_id) else "score"

    if conf >= MIN_CONF_ASSIGN and not ambiguo:
        suporte = "DOCUMENTADO" if any("citius:" in e for e in evid[best_id]) else "PARCIAL"
    elif conf >= MIN_CONF_SHORT and not ambiguo:
        suporte = "PARCIAL"
    else:
        suporte = "PARCIAL" if not ambiguo else "NAO_INDICIADO"

    if ambiguo:
        suporte = "PARCIAL"

    return Hit(
        citius=best_id if conf >= MIN_CONF_SHORT else None,
        slug=_slug(best_id) if conf >= MIN_CONF_SHORT else None,
        confianca=round(conf, 3),
        origem=origem,
        evidencias=evid.get(best_id, []),
        tags=tags,
        cluster=cluster,
        suporte=suporte,
        ambiguo=ambiguo,
        candidatos=[c for c, _ in ranked],
    )


SELFTESTS = [
    ("Peticao_Inicial_15547-26.0T8LSB.docx", "", "15547/26.0T8LSB"),
    ("Providencia_Cautelar_3719-25.0T8LSB.pdf", "", "3719/25.0T8LSB"),
    ("Embargos_23142-22.7T8LSB.docx", "", "23142/22.7T8LSB"),
    ("Oposicao_10153-24.7T8LSB.pdf", "", "10153/24.7T8LSB"),
    ("Documento_sem_referencia.docx", "texto genérico sem número", None),
    ("Contrato_SPARK_CMVM.docx", "pacto social e CMVM", None),  # cluster, não processo
    ("nota_3719-25.pdf", "", "3719/25.0T8LSB"),
    ("mistura.pdf", "ref 3719/25.0T8LSB e também 23142/22.7T8LSB", None),  # ambíguo: citius preenchido mas flag
]


def _run_selftest() -> int:
    failed = 0
    print("SENTINELA-5 heuristica_processo selftest")
    for nome, texto, esperado in SELFTESTS:
        hit = detectar_processo(texto=texto, nome_ficheiro=nome)
        ok = True
        if esperado is None:
            if "mistura" in nome:
                ok = hit.ambiguo and hit.citius is not None
            elif "SPARK" in nome:
                ok = hit.citius is None and hit.cluster == "CLUSTER_SPARK"
            else:
                ok = hit.citius is None
        else:
            ok = hit.citius == esperado and not hit.ambiguo
        status = "OK" if ok else "FALHA"
        if not ok:
            failed += 1
        print(f"  {status}  {nome!r} -> {hit.citius} conf={hit.confianca} "
              f"sup={hit.suporte} amb={hit.ambiguo} cluster={hit.cluster}")
    print(f"falhas={failed}")
    return failed


if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="SENTINELA-5 heuristica Citius")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--file", dest="nome", default="")
    parser.add_argument("--text", dest="texto", default="")
    args = parser.parse_args()
    if args.selftest or (not args.nome and not args.texto):
        raise SystemExit(_run_selftest())
    hit = detectar_processo(texto=args.texto, nome_ficheiro=args.nome)
    json.dump(hit.to_dict(), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    raise SystemExit(0 if hit.suporte != "NAO_INDICIADO" or hit.cluster else 2)
