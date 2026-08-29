import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

OUTPUT_DIR = Path(r"C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\05_PDFS_GERADOS_PARA_IMPRESSAO")
PDF_PATH = OUTPUT_DIR / "07_CHECKLIST_IRREGULARIDADES_E_RESPOSTAS_DEFESA.pdf"

styles = getSampleStyleSheet()

header_style = ParagraphStyle(
    "CitiusHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#1e293b")
)

title_style = ParagraphStyle(
    "CitiusTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#0f172a"),
    alignment=1,
    spaceAfter=10
)

body_style = ParagraphStyle(
    "CitiusBody",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor("#000000")
)

bold_body = ParagraphStyle(
    "CitiusBoldBody",
    parent=body_style,
    fontName="Helvetica-Bold"
)

doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
story = []

story.append(Paragraph("<b>CHECKLIST FORENSE DE IRREGULARIDADES E RESPOSTAS DE DEFESA</b>", title_style))
story.append(Paragraph("<b>SISTEMA DEV YOKOZUNA — AUDITORIA E RESPOSTAS PRONTAS PARA O TRIBUNAL</b>", header_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f172a"), spaceAfter=10))

table_data = [
    ["ID / Proc.", "Irregularidade e Prova Citius", "Norma Violada", "Resposta Jurídica Pronta"],
    ["IRREG-01\n23142/22", "Citação a terceiro e omissão de anexos da apelação (Confissão AE Ref. 437217551).", "Art. 188.º, 195.º CPC;\nArt. 382.º CP", "Execução EXTINTA no TRL. Requerer levantamento imediato dos 35.000 € e veículos."],
    ["IRREG-02\n23142/22", "Penhoras ilegais após indeferimento liminar e recurso com efeito meramente devolutivo.", "Art. 647.º, 703.º CPC;\nArt. 348.º CP", "Reclamação Disciplinar CAAJ com sanção máxima e queixa-crime por abuso de poder."],
    ["IRREG-03\n10153/24", "Sentença à revelia UNICRE com FALTA ABSOLUTA DE CITAÇÃO (2 certidões negativas Catrau).", "Art. 188.º al. e) CPC;\nArt. 729.º al. d) CPC", "Execução SUSPENSA (Art. 733.º CPC). Invocar compensação de fatura 82.722 €."],
    ["IRREG-04\n3719/25", "Nuno Duarte impedido de entrar na sala de audiência; depoimento à revelia.", "Art. 20.º CRP;\nArt. 3.º CPC", "Revertido no TRL: Processo ARQUIVADO DEFINITIVAMENTE e custas à Autora."],
    ["IRREG-05\n15547/26", "Preterição de Litisconsórcio: Contrato N.º 1195528 é com a Lisbon Experience Lda.", "Art. 33.º CPC;\nArt. 577.º al. e) CPC", "Deduzir Exceção Dilatória de Ilegitimidade Passiva: absolvição da instância."],
    ["IRREG-06\n15547/26", "Falsidade de Faturas: junção de despesas do prédio contíguo (Prédio 31 vs 33).", "Art. 542.º CPC\n(Má-Fé)", "Impugnação material das faturas e pedido de condenação em multa e indemnização."],
    ["IRREG-07\n15547/26", "Corte seletivo de água durante 2 anos (WhatsApp 23/08/2022 / filhas no hotel).", "Art. 70.º CC;\nArt. 754.º CC", "Reconvenção exigindo DIREITO DE RETENÇÃO (120k € em obras) e indemnização."]
]

t = Table(table_data, colWidths=[2.2*cm, 5.5*cm, 3.2*cm, 7.1*cm])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('TOPPADDING', (0,0), (-1,-1), 4)
]))

story.append(t)
doc.build(story)
print(f"PDF Gerado: {PDF_PATH}")
