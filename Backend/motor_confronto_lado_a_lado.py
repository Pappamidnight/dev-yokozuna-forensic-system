#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
motor_confronto_lado_a_lado.py - Motor de Confronto Automatizado Lado a Lado (Documentos Oficiais vs Provas Materiais).
Gera relatorio em Markdown, PDF A4 e Dashboard HTML interativo com argumentacao factual estritamente neutra.
Zero emojis conforme PROTOCOL.md e AGENTS.md.
"""

import os
import sys
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
REPORT_MD = OUTPUT_DIR / "01_INDEX_E_RELATORIOS" / "CONFRONTO_DOCUMENTOS_OFICIAIS_VS_PROVAS.md"
REPORT_HTML = OUTPUT_DIR / "01_INDEX_E_RELATORIOS" / "CONFRONTO_LADO_A_LADO_INTERATIVO.html"
REPORT_PDF = OUTPUT_DIR / "05_PDFS_GERADOS_PARA_IMPRESSAO" / "09_CONFRONTO_LADO_A_LADO_OFICIAL_VS_PROVAS.pdf"

CONFRONTOS = [
    {
        "id": "CONF-01",
        "processo": "23142/22.7T8LSB",
        "tema": "Execucao Centenario e Penhoras de 35.000 EUR",
        "oficial_doc": "Despacho de Indeferimento Liminar (Ref. 419855940 de 16/03/2023) e Admissao em Efeito Devolutivo (Ref. 424977808 de 20/04/2023).",
        "oficial_alegacao": "A Exequente e mandatario alegaram titulo valido e promoveram penhoras coercivas sobre contas bancarias (35.000 EUR) e veiculos.",
        "prova_material": "Oficio de Confissao da AE Luisa Santos (Ref. 437217551 de 20/09/2024) e Acordao do Tribunal da Relacao de Lisboa (Ref. 24500137 de 16/04/2026).",
        "prova_facto": "A AE confessou expressamente por escrito nao ter entregue as alegacoes de recurso; o TRL julgou a execucao integralmente extinta.",
        "norma_legal": "Artigos 703.o, 726.o n.o 2 al. a) e 641.o n.o 7 do CPC; Artigo 382.o do Codigo Penal.",
        "argumento_factual": "O indeferimento liminar transitado e o acordao de extincao do TRL destroem a base executiva, determinando o levantamento imediato e incondicional de todas as quantias cativas."
    },
    {
        "id": "CONF-02",
        "processo": "10153/24.7T8LSB / 20203/22.6T8LSB",
        "tema": "Execucao UNICRE e Falta Absoluta de Citacao",
        "oficial_doc": "Sentenca Condenatoria a Revelia de 19/01/2024 (Proc. 20203/22.6T8LSB).",
        "oficial_alegacao": "A UNICRE alegou que o reu foi regularmente citado e transitou em julgado o montante em divida.",
        "prova_material": "2 Cartas Devolvidas no Citius (13/10/2022 e 28/06/2023), 2 Certidoes Negativas da AE Catrau (04/10/2023 e 09/01/2024) e Fatura N.o 1000002 de 82.722 EUR no Portal das Financas.",
        "prova_facto": "O executado nunca recebeu citacao postal ou pessoal; a UNICRE reteve 52.285 EUR em terminais TPA e o executado detem credito compensavel de 82.722 EUR.",
        "norma_legal": "Artigo 188.o n.o 1 al. e) e Artigo 729.o al. d) do CPC; Artigo 733.o n.o 1 CPC; Artigo 847.o do Codigo Civil.",
        "argumento_factual": "A falta absoluta de citacao gera nulidade insanavel de todo o processo anterior, justificando a suspensao da execucao pelo Juiz 8 a 23/10/2025 (Ref. 449641615) e a compensacao integral de creditos."
    },
    {
        "id": "CONF-03",
        "processo": "3719/25.0T8LSB",
        "tema": "Providencia Cautelar e Estado do Imovel",
        "oficial_doc": "Peticao Cautelar de Restituicao Provisoria de Posse da Autora Maria Teresa Martins.",
        "oficial_alegacao": "A requerente alegou esbulho violento recente e degradacao do imovel para obter mandado de desocupacao urgente.",
        "prova_material": "Acordao do TRL de 16/04/2026 (Ref. 24500137), 12 Videos de Vistoria de 24/05/2024 e Notificacao de Custas de 07/07/2026 (Ref. 457395171).",
        "prova_facto": "Nuno Duarte foi impedido de entrar na audiencia de 06/11/2025; o TRL julgou a providencia arquivada em definitivo; os videos comprovam o imovel integralmente conservado.",
        "norma_legal": "Artigo 20.o da CRP; Artigo 3.o do CPC; Artigo 1251.o e 754.o do Codigo Civil.",
        "argumento_factual": "O arquivamento definitivo no TRL com custas a cargo da requerente demonstra a inexistencia de fundamento cautelar e a publicidade pacifica da posse do requerido."
    },
    {
        "id": "CONF-04",
        "processo": "15547/26.0T8LSB",
        "tema": "Acao de Reivindicacao e Litisconsorcio Necessario",
        "oficial_doc": "Peticao Inicial de 12/06/2026 (Ref. 46589030) - Juizo Central Civel de Lisboa.",
        "oficial_alegacao": "A Autora intentou acao contra Nuno Duarte individualmente alegando posse sem titulo e apresentando faturas do predio.",
        "prova_material": "LISTA_CONTRATOS_TERESA.xls (Contrato N.o 1195528 da Lisbon Experience), Matrizes Prediais 110661-U-229 vs 110661-U-231 e Contrato em Tinta Azul.",
        "prova_facto": "O contrato formal de arrendamento do 4.o andar foi celebrado com a sociedade Lisbon Experience Lda.; as faturas juntas pela Autora pertencem ao predio vizinho n.o 31; Nuno Duarte investiu 120.000 EUR em obras.",
        "norma_legal": "Artigo 33.o e Artigo 577.o al. e) do CPC; Artigo 542.o do CPC; Artigo 754.o do Codigo Civil.",
        "argumento_factual": "Verifica-se pretericao de litisconsorcio necessario (ilegitimidade passiva singular) que impoe a absolvicao da instancia, assistindo subsidiariamente ao reu o Direito de Retencao pelas benfeitorias suportadas."
    },
    {
        "id": "CONF-05",
        "processo": "15547/26.0T8LSB / 3719/25.0T8LSB",
        "tema": "Corte de Agua e Coacao Habitacional",
        "oficial_doc": "Alegacao da senhoria de que o reu se recusava a sair voluntariamente.",
        "oficial_alegacao": "A contraparte alegou inexistencia de relacao contratual ou debitos para com o residente.",
        "prova_material": "Transcricao pericial de mensagens WhatsApp de 23 e 24/08/2022 entre Nuno Duarte e Filipe Delgado.",
        "prova_facto": "Filipe Delgado confessa que usou os fundos da empresa para outras fracoes ('nao tenho dinheiro para pagar a heaven'), admitindo que a renda de Nuno dependia daquelas receitas e que este teve de colocar as filhas num hotel devido ao corte de agua.",
        "norma_legal": "Artigo 70.o do Codigo Civil (Tutela Geral da Personalidade); Artigo 754.o do Codigo Civil.",
        "argumento_factual": "As confissoes escritas provam asfixia e coacao habitacional deliberada, afastando qualquer culpa do reu e fundamentando o seu direito a indemnizacao e retencao."
    }
]

def gerar_relatorio_md():
    md = [
        "# RELATORIO FORENSE: CONFRONTO LADO A LADO (DOCUMENTOS OFICIAIS vs PROVAS MATERIAIS)",
        "",
        "**Data de Geracao**: 2026-08-28  ",
        "**Autoridade**: PROTOCOL.md e AGENTS.md (Dev Yokozuna)  ",
        "**Diretiva de Redacao**: Tom estritamente neutro, factual, institucional e sem emojis. Analise comparativa cruzada.",
        "",
        "---",
        ""
    ]

    for c in CONFRONTOS:
        md.append(f"## {c['id']}: {c['tema']} (`{c['processo']}`)")
        md.append("")
        md.append("| Coluna A: Documento Oficial / Citius | Coluna B: Prova Material / Realidade |")
        md.append("|---|---|")
        md.append(f"| **Documento Oficial**: {c['oficial_doc']}<br/><br/>**Alegação Formal**: *\"{c['oficial_alegacao']}\"* | **Documento de Prova**: {c['prova_material']}<br/><br/>**Facto Provado**: {c['prova_facto']} |")
        md.append("")
        md.append(f"**Normas Legais Aplicáveis**: `{c['norma_legal']}`  ")
        md.append(f"**Argumento Factual e Conclusão de Direito**:  \n{c['argumento_factual']}")
        md.append("")
        md.append("---")
        md.append("")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"[+] Relatorio Markdown gravado em: {REPORT_MD}")

def gerar_dashboard_html():
    html_cards = []
    for c in CONFRONTOS:
        card = f"""
        <div class="confronto-card">
            <div class="card-header">
                <span class="card-id">{c['id']}</span>
                <span class="card-proc">{c['processo']}</span>
                <h3>{c['tema']}</h3>
            </div>
            <div class="columns-grid">
                <div class="col col-oficial">
                    <h4>Coluna A: Documento Oficial / Citius</h4>
                    <p class="doc-title"><strong>Peça:</strong> {c['oficial_doc']}</p>
                    <div class="allegation-box">
                        <strong>Alegação Formal:</strong><br>
                        <em>"{c['oficial_alegacao']}"</em>
                    </div>
                </div>
                <div class="col col-prova">
                    <h4>Coluna B: Prova Material e Factos</h4>
                    <p class="doc-title"><strong>Prova:</strong> {c['prova_material']}</p>
                    <div class="fact-box">
                        <strong>Facto Provado:</strong><br>
                        {c['prova_facto']}
                    </div>
                </div>
            </div>
            <div class="conclusion-box">
                <div class="norma"><strong>Normas Legais:</strong> <code>{c['norma_legal']}</code></div>
                <div class="argument"><strong>Argumentação Factual:</strong> {c['argumento_factual']}</div>
            </div>
        </div>
        """
        html_cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confronto Forense: Documentos Oficiais vs Provas Materiais</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-amber: #fbbf24;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .header {{
            max-width: 1200px;
            margin: 0 auto 30px auto;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 24px;
            color: #ffffff;
            font-weight: 700;
        }}
        .header p {{
            margin: 0;
            color: var(--text-muted);
            font-size: 14px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .confronto-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .card-header {{
            padding: 16px 20px;
            background: rgba(15, 23, 42, 0.6);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .card-id {{
            background: #0284c7;
            color: #ffffff;
            font-weight: 700;
            font-size: 12px;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .card-proc {{
            color: var(--accent-amber);
            font-size: 13px;
            font-family: monospace;
            font-weight: 600;
        }}
        .card-header h3 {{
            margin: 0;
            font-size: 16px;
            color: #ffffff;
            font-weight: 600;
        }}
        .columns-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }}
        .col {{
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px;
        }}
        .col h4 {{
            margin: 0 0 12px 0;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .col-oficial h4 {{ color: #f87171; }}
        .col-prova h4 {{ color: var(--accent-green); }}
        .doc-title {{
            font-size: 13px;
            color: var(--text-muted);
            margin: 0 0 10px 0;
        }}
        .allegation-box, .fact-box {{
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .allegation-box {{
            background: rgba(239, 68, 68, 0.1);
            border-left: 3px solid #ef4444;
            color: #fecaca;
        }}
        .fact-box {{
            background: rgba(16, 185, 129, 0.1);
            border-left: 3px solid #10b981;
            color: #a7f3d0;
        }}
        .conclusion-box {{
            padding: 16px 20px;
            background: rgba(15, 23, 42, 0.7);
            border-top: 1px solid var(--border);
            font-size: 13.5px;
        }}
        .norma {{
            color: var(--accent-blue);
            margin-bottom: 8px;
        }}
        .norma code {{
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            color: #e2e8f0;
        }}
        .argument {{
            color: #e2e8f0;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Confronto Forense Lado a Lado: Documentos Oficiais vs Provas Materiais</h1>
        <p>Sistema Dev Yokozuna — Auditoria Factual e Estruturada sem Conflitos Retoricos (Tom Institucional e Neutro)</p>
    </div>
    <div class="container">
        {"".join(html_cards)}
    </div>
</body>
</html>
    """

    REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Dashboard HTML interativo gravado em: {REPORT_HTML}")

def gerar_pdf_lado_a_lado():
    REPORT_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "CitiusHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )
    title_style = ParagraphStyle(
        "CitiusTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=6
    )

    doc = SimpleDocTemplate(str(REPORT_PDF), pagesize=landscape(A4), rightMargin=1.0*cm, leftMargin=1.0*cm, topMargin=1.0*cm, bottomMargin=1.0*cm)
    story = []

    story.append(Paragraph("<b>QUADRO DE CONFRONTO FORENSE LADO A LADO (DOCUMENTOS OFICIAIS vs PROVAS MATERIAIS)</b>", title_style))
    story.append(Paragraph("<b>SISTEMA DEV YOKOZUNA — AUDITORIA E RECONCILIAÇÃO FACTUAL NEUTRA</b>", header_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0f172a"), spaceAfter=6))

    rows = [["ID / Proc.", "Coluna A: Documento Oficial / Citius", "Coluna B: Prova Material Real", "Normas e Conclusão Factual"]]
    for c in CONFRONTOS:
        col_a = f"<b>Doc:</b> {c['oficial_doc']}<br/><br/><b>Alegação:</b> <i>\"{c['oficial_alegacao']}\"</i>"
        col_b = f"<b>Prova:</b> {c['prova_material']}<br/><br/><b>Facto:</b> {c['prova_facto']}"
        col_c = f"<b>Normas:</b> <font color='#2563eb'>{c['norma_legal']}</font><br/><br/><b>Argumento:</b> {c['argumento_factual']}"
        rows.append([
            f"<b>{c['id']}</b><br/><font size=6 color='#64748b'>{c['processo']}</font><br/><br/><b>{c['tema']}</b>",
            col_a,
            col_b,
            col_c
        ])

    t = Table(rows, colWidths=[3.8*cm, 7.8*cm, 8.2*cm, 8.0*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 6.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))

    story.append(t)
    doc.build(story)
    print(f"[+] PDF horizontal A4 gravado em: {REPORT_PDF}")

if __name__ == "__main__":
    gerar_relatorio_md()
    gerar_dashboard_html()
    gerar_pdf_lado_a_lado()
