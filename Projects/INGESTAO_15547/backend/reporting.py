from __future__ import annotations

from collections import Counter
from pathlib import Path

from backend.schemas.models import Claim, EvidenceFile, Gap, TimelineEvent


def render_markdown(
    path: Path,
    evidences: list[EvidenceFile],
    claims: list[Claim],
    timeline: list[TimelineEvent],
    gaps: list[Gap],
) -> None:
    counts = Counter(claim.estado for claim in claims)
    lines: list[str] = [
        "# Relatorio Deterministico - Processo 15547/26.0T8LSB",
        "",
        "Este relatorio organiza informacao extraida de fontes em `raw/`. Nao substitui validacao juridica.",
        "",
        "## Sumario",
        "",
        f"- Evidencias indexadas: {len(evidences)}",
        f"- Claims extraidos: {len(claims)}",
        f"- Eventos cronologicos: {len(timeline)}",
        f"- Lacunas/alertas: {len(gaps)}",
        "",
        "## Estados Probatorios",
        "",
    ]
    for estado, total in sorted(counts.items(), key=lambda item: item[0]):
        lines.append(f"- {estado}: {total}")

    lines.extend(["", "## Evidencias", ""])
    for ev in evidences:
        lines.append(f"- `{ev.evidence_id}` | `{ev.filename}` | SHA-256 `{ev.sha256}` | {ev.size_bytes} bytes")

    lines.extend(["", "## Cronologia", ""])
    for event in timeline:
        lines.append(f"- {event.data} | {event.estado} | {event.titulo}: {event.descricao}")

    lines.extend(["", "## Claims", ""])
    for claim in claims:
        lines.append(f"- `{claim.claim_id}` | {claim.estado} | {claim.tema} | {claim.descricao}")

    lines.extend(["", "## Lacunas e Alertas", ""])
    for gap in gaps:
        lines.append(f"- `{gap.gap_id}` | {gap.severidade} | {gap.tema}: {gap.descricao} Acao: {gap.acao_recomendada}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
