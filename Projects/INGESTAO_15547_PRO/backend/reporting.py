from __future__ import annotations

from collections import Counter
from pathlib import Path
from datetime import datetime

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
        "# Relatorio Deterministico PRO - Processo 15547/26.0T8LSB",
        "",
        f"**Data de Geracao**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Motor**: Fabrica Multiagente Deterministica INGESTAO_15547_PRO",
        "",
        "## 1. Sumario Executivo",
        "",
        f"- Evidencias indexadas: {len(evidences)}",
        f"- Claims extraidos: {len(claims)}",
        f"- Eventos cronologicos: {len(timeline)}",
        f"- Lacunas/alertas: {len(gaps)}",
        "",
        "## 2. Estados Probatorios",
        "",
    ]
    for estado, total in sorted(counts.items(), key=lambda item: item[0]):
        lines.append(f"- **{estado}**: {total}")

    lines.extend(["", "## 3. Evidencias e Provas Documentais", ""])
    for ev in evidences:
        lines.append(f"- `{ev.evidence_id}` | `{ev.filename}` | SHA-256 `{ev.sha256[:16]}...` | {ev.size_bytes} bytes")

    lines.extend(["", "## 4. Cronologia Mestre Ordenada", ""])
    for event in timeline:
        lines.append(f"- `{event.data}` | **{event.estado}** | {event.titulo}: {event.descricao}")

    lines.extend(["", "## 5. Claims e Teses Juridicas", ""])
    for claim in claims:
        lines.append(f"- `{claim.claim_id}` | **{claim.estado}** | `{claim.tema}` | {claim.descricao}")

    lines.extend(["", "## 6. Lacunas e Alertas Processuais", ""])
    for gap in gaps:
        lines.append(f"- `{gap.gap_id}` | [{gap.severidade}] | **{gap.tema}**: {gap.descricao} (Acao: {gap.acao_recomendada})")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Render HTML Dashboard
    html_path = path.parent.parent / "html" / "PAINEL_15547_PRO.html"
    render_html(html_path, evidences, claims, timeline, gaps, counts)


def render_html(
    html_path: Path,
    evidences: list[EvidenceFile],
    claims: list[Claim],
    timeline: list[TimelineEvent],
    gaps: list[Gap],
    counts: Counter,
) -> None:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Forense PRO: Processo 15547/26.0T8LSB</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0b0f19;
            --bg-card: #151d30;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-emerald: #10b981;
            --accent-purple: #a855f7;
            --border-color: #263352;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            padding: 2rem 1.5rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            background: linear-gradient(135deg, #151d30 0%, #0b0f19 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        h1 {{ font-size: 1.8rem; color: var(--accent-blue); margin-bottom: 0.5rem; }}
        .badge {{
            display: inline-block;
            background: rgba(16, 185, 129, 0.2);
            color: var(--accent-emerald);
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.5rem;
        }}
        .card h3 {{ font-size: 1.1rem; color: var(--accent-blue); margin-bottom: 0.8rem; }}
        .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent-emerald); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            background-color: var(--bg-card);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        th, td {{
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.9rem;
        }}
        th {{ background-color: rgba(38, 51, 82, 0.5); color: var(--text-secondary); }}
        code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--accent-purple); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Painel Forense PRO: Processo 15547/26.0T8LSB</h1>
            <p style="color: var(--text-secondary);">Comarca de Lisboa — Juizo Central Civel | Atualizado em: {timestamp}</p>
            <div class="badge">Fabrica Multiagente INGESTAO_15547_PRO Ativa</div>
        </header>

        <div class="grid">
            <div class="card">
                <h3>Evidencias Indexadas</h3>
                <div class="metric">{len(evidences)}</div>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">100% SHA-256 Verificado</p>
            </div>
            <div class="card">
                <h3>Claims & Declaracoes</h3>
                <div class="metric">{len(claims)}</div>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Pydantic v2 Validadas</p>
            </div>
            <div class="card">
                <h3>Eventos Cronologicos</h3>
                <div class="metric">{len(timeline)}</div>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Ordenacao Temporal ISO</p>
            </div>
            <div class="card">
                <h3>Lacunas & Alertas</h3>
                <div class="metric" style="color: var(--accent-purple);">{len(gaps)}</div>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Acoes Sugeridas</p>
            </div>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h3>Estados Probatorios</h3>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem;">
"""
    for estado, total in sorted(counts.items()):
        html_content += f"""                <div style="background: rgba(38, 51, 82, 0.4); padding: 0.8rem 1.2rem; border-radius: 8px; border: 1px solid var(--border-color);">
                    <div style="color: var(--text-secondary); font-size: 0.85rem;">{estado}</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: var(--accent-blue);">{total}</div>
                </div>\n"""

    html_content += """            </div>
        </div>

        <div class="card">
            <h3>Cronologia Mestre</h3>
            <table>
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Estado</th>
                        <th>Titulo</th>
                        <th>Descricao</th>
                    </tr>
                </thead>
                <tbody>
"""
    for event in timeline:
        html_content += f"""                    <tr>
                        <td><code>{event.data}</code></td>
                        <td><span style="color: var(--accent-emerald); font-weight: 600;">{event.estado}</span></td>
                        <td>{event.titulo}</td>
                        <td style="color: var(--text-secondary);">{event.descricao}</td>
                    </tr>\n"""

    html_content += """                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")
