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
PDF_PATH = OUTPUT_DIR / "06_MINUTA_CONTESTACAO_15547_COMPLETA.pdf"

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
    fontName="Times-Roman",
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor("#000000"),
    alignment=4
)

bold_body = ParagraphStyle(
    "CitiusBoldBody",
    parent=body_style,
    fontName="Times-Bold"
)

quote_style = ParagraphStyle(
    "QuoteStyle",
    parent=body_style,
    fontName="Times-Italic",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#334155")
)

doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4, rightMargin=1.8*cm, leftMargin=1.8*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
story = []

# Cabecalho
hdr_data = [
    [
        Paragraph("<b>TRIBUNAL JUDICIAL DA COMARCA DE LISBOA</b><br/>Juízo Central Cível de Lisboa<br/><font size=7.5 color='#64748b'>Palácio da Justiça — Lisboa</font>", header_style),
        Paragraph("<b>PROCESSO:</b> 15547/26.0T8LSB<br/><b>ESPÉCIE:</b> Ação de Reivindicação<br/><b>VALOR:</b> 125.000,00 €", header_style)
    ]
]
t_hdr = Table(hdr_data, colWidths=[11*cm, 6.5*cm])
t_hdr.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
]))
story.append(t_hdr)
story.append(Spacer(1, 10))

story.append(Paragraph("<b>CONTESTAÇÃO E RECONVENÇÃO</b>", title_style))
story.append(Paragraph("<b>(Preterição de Litisconsórcio, Falsidade de Faturas e Direito de Retenção)</b>", header_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

# Articulado Resumido
story.append(Paragraph("<b>NUNO MIGUEL SILVA DUARTE</b>, Réu nos autos à margem identificados em que é Autora <b>MARIA TERESA CASTRO BANGUESES RIBEIRO</b>, vem apresentar a sua Contestação:", body_style))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>I. EXCEÇÃO DILATÓRIA: PRETERIÇÃO DE LITISCONSÓRCIO NECESSÁRIO (ART. 33.º DO CPC)</b>", bold_body))
story.append(Paragraph("A Autora celebrou o Contrato de Arrendamento N.º 1195528 com a sociedade <b>LISBON EXPERIENCE - ADMINISTRAÇÃO DE IMÓVEIS, LDA.</b> (conforme prova <code>LISTA_CONTRATOS_TERESA.xls</code>). A omissão da locatária formal determina a ilegitimidade passiva singular e a absolvição da instância (Art. 577.º, al. e) do CPC).", body_style))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>II. FALSIDADE MATERIAL DAS FATURAS DO PRÉDIO CONTÍGUO (PRÉDIO 31 vs 33)</b>", bold_body))
story.append(Paragraph("As faturas juntas pela Autora respeitam a obras e despesas do prédio contíguo (Rua da Palmeira 31 / Matriz 110661-U-229) e não à fração do Réu (Palmeira 33 / Matriz 110661-U-231-4), constituindo litigância de má-fé.", body_style))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>III. POSSE >10 ANOS E CONTRATO EM TINTA AZUL</b>", bold_body))
story.append(Paragraph("O Réu detém posse titulada e conhecida desde 2015 suportada por 20+ adendas e mapas de rendas. O único contrato genuíno é o assinado com tinta azul.", body_style))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>IV. DIREITO DE RETENÇÃO (ARTIGO 754.º DO CÓDIGO CIVIL)</b>", bold_body))
story.append(Paragraph("O Réu investiu mais de 120.000,00 € em benfeitorias necessárias no imóvel e detém créditos acumulados de 236.622,00 €, assistindo-lhe o <b>Direito de Retenção</b> até integral pagamento.", body_style))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>V. PROVA DO CORTE DE ÁGUA E COAÇÃO HABITACIONAL</b>", bold_body))
story.append(Paragraph("<i>[23/08/2022, 12:19] Nuno Duarte: 'tenho as miudas num Hotel'<br/>[23/08/2022, 12:42] Filipe Delgado: 'Tinhas enviado o vídeo e tinha entrado 5000 para as contas e para uma casa para ti garantida'<br/>[23/08/2022, 19:21] Filipe Delgado: 'Garantia da tua casa para viver só e possível com renda da sky'</i>", quote_style))
story.append(Spacer(1, 8))

story.append(Paragraph("<b>VI. PEDIDOS:</b> Absolvição da instância por ilegitimidade; improcedência total da ação; e procedência da Reconvenção com reconhecimento do <b>Direito de Retenção pelo crédito de 120.000,00 €</b>.", bold_body))
story.append(Spacer(1, 15))

story.append(Paragraph("O Réu: __________________________________________________<br/>(Nuno Miguel Silva Duarte)", bold_body))

doc.build(story)
print(f"PDF Gerado: {PDF_PATH}")
