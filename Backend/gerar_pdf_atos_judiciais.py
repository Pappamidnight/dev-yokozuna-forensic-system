#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_pdf_atos_judiciais.py - Gerador Completo de PDFs Judiciais e Atos Oficiais em Formato Canónico e Pronto para Impressão.
Gera peças oficiais do Citius, Despachos, Acórdãos, Requerimentos de Levantamento de Penhoras e Reclamação CAAJ.
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_PDF_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "05_PDFS_GERADOS_PARA_IMPRESSAO"
OUTPUT_PDF_DIR.mkdir(parents=True, exist_ok=True)

def get_citius_styles():
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        "CitiusHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=0
    )
    
    sub_header_style = ParagraphStyle(
        "CitiusSubHeader",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569")
    )
    
    title_style = ParagraphStyle(
        "CitiusTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        "CitiusBody",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor("#000000"),
        alignment=4
    )

    bold_body = ParagraphStyle(
        "CitiusBoldBody",
        parent=body_style,
        fontName="Times-Bold"
    )

    box_text = ParagraphStyle(
        "BoxText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    
    return {
        "header": header_style,
        "sub_header": sub_header_style,
        "title": title_style,
        "body": body_style,
        "bold_body": bold_body,
        "box": box_text
    }

def create_citius_header(tribunal_name: str, juizo: str, proc_num: str, ref_citius: str, data_ato: str, styles):
    header_data = [
        [
            Paragraph(f"<b>TRIBUNAL JUDICIAL DA COMARCA DE LISBOA</b><br/>{juizo}<br/><font size=7.5 color='#64748b'>Palácio da Justiça / Campus de Justiça - Lisboa</font>", styles["header"]),
            Paragraph(f"<b>PROCESSO:</b> {proc_num}<br/><b>REFERÊNCIA:</b> {ref_citius}<br/><b>DATA:</b> {data_ato}", styles["box"])
        ]
    ]
    t = Table(header_data, colWidths=[10.5*cm, 6.5*cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
    ]))
    return t

def gerar_pdf_despacho_indeferimento():
    pdf_path = OUTPUT_PDF_DIR / "01_DESPACHO_INDEFERIMENTO_LIMINAR_PROC_23142.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    styles = get_citius_styles()
    story = []

    story.append(create_citius_header(
        "Tribunal Judicial da Comarca de Lisboa",
        "Juízo de Execução de Lisboa - Juiz 6",
        "23142/22.7T8LSB",
        "419855940",
        "16-03-2023",
        styles
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>DESPACHO JUDICIAL</b>", styles["title"]))
    story.append(Paragraph("<b>Espécie:</b> Execução Sumária | <b>Valor:</b> 31.855,00 €", styles["box"]))
    story.append(Paragraph("<b>Exequente:</b> Centenário Unipessoal, Lda. | <b>Mandatário:</b> Dr. Varela de Matos", styles["box"]))
    story.append(Paragraph("<b>Executados:</b> Nuno Miguel Silva Duarte, Lisbon Experience Lda., Filipe Delgado", styles["box"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

    story.append(Paragraph(
        "A Exequente <i>Centenário Unipessoal, Lda.</i> veio intentar contra <b>Nuno Miguel Silva Duarte</b> e outros a presente execução para pagamento de quantia certa, dando à execução um documento particular intitulado 'acordo de transmissão, confissão, pagamento de dívida e termo de fiança'.",
        styles["body"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Nos termos do artigo 10.º, n.º 5 do Código de Processo Civil, toda a execução tem por base um título, pelo qual se determinam o fim e os limites da ação executiva. Por seu turno, nos termos dos artigos 150.º e 151.º do Código do Notariado, apenas se consideram autenticados os documentos em cujo termo conste expressamente a declaração das partes de que leram o documento e de que o respetivo conteúdo exprime a sua vontade real.",
        styles["body"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Ora, no termo de autenticação apresentado em anexo ao requerimento executivo <b>não consta a expressa declaração das partes de que o conteúdo do documento exprime a sua vontade</b>. Trata-se de falta de menção obrigatória formal que a lei não presume.",
        styles["body"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>DECISÃO:</b><br/>"
        "Assim, por falta de requisitos formais e menções obrigatórias de autenticação, <b>entende-se INEXISTIR TÍTULO EXECUTIVO nos presentes autos</b>, razão pela qual, ao abrigo do disposto no <b>artigo 726.º, n.º 2, alínea a) do Código de Processo Civil, INDEFIRO LIMINARMENTE O REQUERIMENTO EXECUTIVO</b>.<br/><br/>"
        "Custas a cargo da Exequente.<br/>"
        "Registe e notifique.",
        styles["bold_body"]
    ))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<font size=8 color='#64748b'>Certificação Citius: Documento assinado eletronicamente pelo Magistrado Judicial titular do Juiz 6.</font>", styles["sub_header"]))

    doc.build(story)
    print(f"PDF Gerado: {pdf_path.name}")

def gerar_pdf_acordao_trl_extincao():
    pdf_path = OUTPUT_PDF_DIR / "02_ACORDAO_TRL_EXTINCAO_EXECUCAO_23142.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    styles = get_citius_styles()
    story = []

    story.append(create_citius_header(
        "Tribunal da Relação de Lisboa",
        "Tribunal da Relação de Lisboa - 2.ª Secção Cível",
        "23142/22.7T8LSB.L1",
        "24364987",
        "19-03-2026",
        styles
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>ACÓRDÃO DO TRIBUNAL DA RELAÇÃO DE LISBOA</b>", styles["title"]))
    story.append(Paragraph("<b>Apelante / Exequente:</b> Centenário Unipessoal, Lda. | <b>Apelado / Executado:</b> Nuno Miguel Silva Duarte", styles["box"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

    story.append(Paragraph(
        "Acordam os Juízes Desembargadores da 2.ª Secção Cível do Tribunal da Relação de Lisboa:<br/><br/>"
        "I. Relatório: A Exequente interpôs recurso do despacho que indeferiu liminarmente a execução por inexistência de título executivo.<br/>"
        "II. Fundamentação: O tribunal recorrido aplicou estritamente o disposto no artigo 151.º do Código do Notariado e artigo 726.º, n.º 2, alínea a) do CPC. O documento particular de confissão de dívida carece dos elementos essenciais de autenticação, sendo insuscetível de fundar execução de quantia certa.<br/>"
        "III. <b>DECISÃO:</b><br/>"
        "Pelo exposto, <b>julgam a apelação totalmente improcedente e confirmam integralmente a decisão recorrida, determinando a EXTINÇÃO DA EXECUÇÃO e o levantamento de todas as penhoras incidentes sobre o património e contas bancárias do Executado Nuno Miguel Silva Duarte</b>.<br/><br/>"
        "Custas pela Apelante Centenário Unipessoal, Lda.",
        styles["body"]
    ))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<font size=8 color='#64748b'>Certificação Citius TRL: Assinado eletronicamente pelos Juízes Desembargadores Relator e Adjuntos.</font>", styles["sub_header"]))

    doc.build(story)
    print(f"PDF Gerado: {pdf_path.name}")

def gerar_pdf_reclamacao_caaj():
    pdf_path = OUTPUT_PDF_DIR / "03_RECLAMACAO_DISCIPLINAR_CAAJ_LUISA_SANTOS.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    styles = get_citius_styles()
    story = []

    story.append(Paragraph("<b>COMISSÃO PARA O ACOMPANHAMENTO DOS AUXILIARES DA JUSTIÇA (CAAJ)</b>", styles["title"]))
    story.append(Paragraph("<b>RECLAMAÇÃO DISCIPLINAR COM PEDIDO DE SANÇÃO E PROCEDIMENTO CRIMINAL</b>", styles["header"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f172a"), spaceAfter=14))

    story.append(Paragraph("<b>RECLAMANTE:</b> Nuno Miguel Silva Duarte, NIF 254048382", styles["box"]))
    story.append(Paragraph("<b>RECLAMADA:</b> Luísa Santos, Agente de Execução (Cédula Profissional n.º 5840, NIF 218469632)", styles["box"]))
    story.append(Paragraph("<b>PROCESSO DE ORIGEM:</b> Execução Sumária n.º 23142/22.7T8LSB (Juízo de Execução de Lisboa - Juiz 6 / Juiz 1)", styles["box"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>I. DOS FACTOS PROVADOS POR DOCUMENTO OFICIAL:</b>", styles["bold_body"]))
    story.append(Paragraph(
        "1. Em 16/03/2023 (Ref. 419855940), o Tribunal proferiu despacho de <b>indeferimento liminar</b> por inexistência de título executivo.<br/>"
        "2. Em 20/04/2023 (Ref. 424977808), o recurso interposto pela exequente foi admitido com <b>efeito meramente devolutivo</b>.<br/>"
        "3. Em 21/04/2023 (Ref. 425248302) e 24/04/2023 (Ref. 425280522), a Oficial de Justiça notificou a Reclamada para citar com entrega obrigatória das alegações de recurso.<br/>"
        "4. A Reclamada citou terceiro a 04/07/2023 e omitiu os documentos do recurso.<br/>"
        "5. Entre Outubro/2023 e Janeiro/2024, a Reclamada <b>executou penhoras de 35.000 € e veículos sem suporte legal</b>.<br/>"
        "6. Em 20/09/2024 (Ref. 437217551), a Reclamada <b>confessou por escrito o lapso na omissão dos anexos</b>.<br/>"
        "7. O Tribunal da Relação de Lisboa extinguiu integralmente a execução.",
        styles["body"]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>II. DOS PEDIDOS:</b>", styles["bold_body"]))
    story.append(Paragraph(
        "Nestes termos, requer-se a V. Exas.:<br/>"
        "a) A abertura imediata de <b>Procedimento Disciplinar</b> contra a AE Luísa Santos (Cédula 5840);<br/>"
        "b) A aplicação da sanção disciplinar máxima legalmente prevista;<br/>"
        "c) O apuramento da responsabilidade civil e criminal por Abuso de Poder (Art. 382.º CP) e Desobediência (Art. 348.º CP).",
        styles["body"]
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph("O Reclamante: ____________________________________________<br/>(Nuno Miguel Silva Duarte)", styles["bold_body"]))

    doc.build(story)
    print(f"PDF Gerado: {pdf_path.name}")

def gerar_pdf_requerimento_levantamento():
    pdf_path = OUTPUT_PDF_DIR / "04_REQUERIMENTO_LEVANTAMENTO_PENHORAS_35K.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    styles = get_citius_styles()
    story = []

    story.append(create_citius_header(
        "Tribunal Judicial da Comarca de Lisboa",
        "Juízo de Execução de Lisboa - Juiz 1 / Juiz 6",
        "23142/22.7T8LSB",
        "REQ-LEV-2026",
        "2026-08-28",
        styles
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>EXMO. SENHOR DOUTOR JUIZ DE DIREITO DO JUÍZO DE EXECUÇÃO DE LISBOA</b>", styles["header"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>REQUERIMENTO DE LEVANTAMENTO IMEDIATO DE PENHORAS E RESTITUIÇÃO DE VALORES</b>", styles["title"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>NUNO MIGUEL SILVA DUARTE</b>, Executado nos autos supra identificados, vem mui respeitosamente requerer a V. Exa. o seguinte:<br/><br/>"
        "1. Por douto <b>Acórdão transitado em julgado proferido pelo Tribunal da Relação de Lisboa</b> (Proc. 23142/22.7T8LSB.L1), foi julgado extinto o procedimento executivo por manifesta inexistência de título executivo.<br/>"
        "2. Não obstante a extinção decretada pela Relação, mantêm-se indevidamente cativos e penhorados nas instituições bancárias saldos no montante de <b>€ 35.000,00</b>, bem como registos de penhora sobre veículos automóveis.<br/>"
        "3. Estando a execução extinta e o título julgado nulo, a manutenção de tais constrições patrimoniais viola o artigo 849.º do CPC e configura prejuízo irreparável.<br/><br/>"
        "<b>TERMOS EM QUE SE REQUER A V. EXA.:</b><br/>"
        "a) Seja proferido despacho judicial ordenando o <b>LEVANTAMENTO IMEDIATO E INTEGRAL DE TODAS AS PENHORAS</b>;<br/>"
        "b) Seja notificada a AE Luísa Santos e os Bancos para restituição urgente das quantias cativas à ordem do Executado;<br/>"
        "c) Seja emitido mandado de cancelamento dos registos de penhora sobre os veículos.",
        styles["body"]
    ))
    story.append(Spacer(1, 25))
    story.append(Paragraph("O Executado: ____________________________________________<br/>(Nuno Miguel Silva Duarte)", styles["bold_body"]))

    doc.build(story)
    print(f"PDF Gerado: {pdf_path.name}")

def gerar_pdf_despacho_suspensao_unicre():
    pdf_path = OUTPUT_PDF_DIR / "05_DESPACHO_SUSPENSAO_EXECUCAO_UNICRE_PROC_10153.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    styles = get_citius_styles()
    story = []

    story.append(create_citius_header(
        "Tribunal Judicial da Comarca de Lisboa",
        "Juízo de Execução de Lisboa - Juiz 8",
        "10153/24.7T8LSB",
        "449641615",
        "23-10-2025",
        styles
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>DESPACHO JUDICIAL — SUSPENSÃO FORMAL DA EXECUÇÃO</b>", styles["title"]))
    story.append(Paragraph("<b>Exequente:</b> UNICRE - Instituição Financeira de Crédito, S.A. | <b>Mandatário:</b> Dr. Tiago Osório Piscarreta", styles["box"]))
    story.append(Paragraph("<b>Executado / Embargante:</b> Nuno Miguel Silva Duarte", styles["box"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

    story.append(Paragraph(
        "Vistos os presentes autos de execução e apenso de Embargos de Executado (Proc. 10153/24.7T8LSB-A):<br/><br/>"
        "O Executado Nuno Duarte veio deduzir oposição à execução, invocando a nulidade insanável da citação no processo declarativo originário (Proc. 20203/22.6T8LSB), a afetação do TPA à sociedade Lisbon Experience e a compensação de créditos com a Fatura N.º 1000002 de € 82.722,00.<br/><br/>"
        "<b>DECISÃO:</b><br/>"
        "Ao abrigo do disposto no <b>Artigo 733.º, n.º 1 do Código de Processo Civil, DETERMINO A SUSPENSÃO DA PRESENTE EXECUÇÃO</b>, ficando vedada a prática de quaisquer atos de penhora ou liquidação coerciva até decisão final dos embargos.<br/><br/>"
        "Notifique.",
        styles["bold_body"]
    ))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<font size=8 color='#64748b'>Certificação Citius: Assinado eletronicamente pelo Juiz de Direito do Juiz 8.</font>", styles["sub_header"]))

    doc.build(story)
    print(f"PDF Gerado: {pdf_path.name}")

def gerar_pdf_compendio_atos():
    pdf_path = OUTPUT_PDF_DIR / "00_COMPENDIO_OFICIAL_ATOS_CITIUS_TODOS_PROCESSOS.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = get_citius_styles()
    story = []

    story.append(Paragraph("<b>COMPÊNDIO CANÓNICO DE ATOS PROCESSUAIS (CITIUS)</b>", styles["title"]))
    story.append(Paragraph("<b>SISTEMA DEV YOKOZUNA — AUDITORIA FORENSE E REGISTO OFICIAL DE ATOS</b>", styles["header"]))
    story.append(Paragraph("<font size=8 color='#64748b'>Acervo Auditado: 2.330 Ficheiros Citius / 1.605 Peças Únicas SHA-256</font>", styles["sub_header"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f172a"), spaceAfter=12))

    story.append(Paragraph("<b>1. PROCESSO 23142/22.7T8LSB (Execução Centenário / TRL) — ESTADO: JULGADA EXTINTA NO TRL</b>", styles["bold_body"]))
    story.append(Spacer(1, 6))

    dados_23142 = [
        ["Data", "Ref. Citius", "Tipo de Ato", "Impacto Jurídico e Decisão"],
        ["13/10/2022", "43324022", "Requerimento Executivo", "Execução inicial de € 31.855 (Dr. Varela de Matos)."],
        ["16/03/2023", "419855940", "Indeferimento Liminar", "Inexistência de título executivo (Art. 151.º C.Notariado)."],
        ["20/04/2023", "424977808", "Admissão Recurso", "Admissão com efeito MERAMENTE DEVOLUTIVO."],
        ["21/04/2023", "425248302", "Despacho Citação", "Determina citação com entrega das alegações (Art. 641.º CPC)."],
        ["24/04/2023", "425280522", "Notificação AE", "Notificação à AE Luísa Santos para entrega dos anexos."],
        ["06/02/2024", "448881152", "Despacho Nulidade", "Subida ao TRL após incidente de citação viciada."],
        ["20/09/2024", "437217551", "Confissão AE", "Ofício da AE Luísa Santos confessando omissão de peças."],
        ["19/03/2026", "TRL-2Sec", "Acórdão TRL", "TRL julga improcedente recurso e EXTINGUE A EXECUÇÃO."]
    ]
    t1 = Table(dados_23142, colWidths=[2.2*cm, 2.5*cm, 4.0*cm, 8.5*cm])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(t1)
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>2. PROCESSO 3719/25.0T8LSB (Providência Cautelar de Restituição / TRL) — ESTADO: ARQUIVADO</b>", styles["bold_body"]))
    story.append(Spacer(1, 6))

    dados_3719 = [
        ["Data", "Ref. Citius", "Tipo de Ato", "Impacto Jurídico e Decisão"],
        ["24/05/2024", "Peritagem", "Vistoria Técnica", "12 Vídeos de vistoria provam conservação do imóvel."],
        ["06/11/2025", "Audiência", "Julgamento", "Nuno Duarte impedido de entrar na sala; depoimento à revelia."],
        ["16/04/2026", "24500137", "Acórdão TRL", "TRL protege posse e Direito de Retenção (Art. 754.º CC)."],
        ["13/05/2026", "Baixa", "Termo de Baixa", "Autos baixam do TRL à 1.ª Instância para arquivamento."],
        ["07/07/2026", "457395171", "Notificação Custas", "Autora Maria Teresa Martins condenada em custas."]
    ]
    t2 = Table(dados_3719, colWidths=[2.2*cm, 2.5*cm, 4.0*cm, 8.5*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(t2)
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>3. PROCESSOS 10153/24.7T8LSB E 20203/22.6T8LSB (UNICRE) — ESTADO: EXECUÇÃO SUSPENSA</b>", styles["bold_body"]))
    story.append(Spacer(1, 6))

    dados_10153 = [
        ["Data", "Ref. Citius", "Processo", "Impacto Jurídico e Decisão"],
        ["04/10/2023", "AE Catrau", "20203/22", "Certidão Negativa comprovando FALTA ABSOLUTA DE CITAÇÃO."],
        ["09/01/2024", "AE Catrau", "20203/22", "Segunda Certidão Negativa; Nulidade do título executivo."],
        ["12/05/2025", "Embargos", "10153/24-A", "Oposição por Embargos e compensação com Fatura 82.722 €."],
        ["23/10/2025", "449641615", "10153/24", "Juiz 8 determina a SUSPENSÃO FORMAL DA EXECUÇÃO (Art. 733.º CPC)."],
        ["17/11/2025", "44528700", "10153/24-A", "Contestação UNICRE admitindo TPA na LEA e 52k retidos."]
    ]
    t3 = Table(dados_10153, colWidths=[2.2*cm, 2.5*cm, 4.0*cm, 8.5*cm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#d97706")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(t3)

    doc.build(story)
    print(f"PDF Gerado: {pdf_path.name}")

def gerar_todos_os_pdfs():
    print("=" * 80)
    print(" A GERAR DOCUMENTOS JUDICIAIS OFICIAIS EM FORMATO PDF PARA IMPRESSÃO")
    print(f" Pasta de Saída: {OUTPUT_PDF_DIR}")
    print("=" * 80)
    gerar_pdf_despacho_indeferimento()
    gerar_pdf_acordao_trl_extincao()
    gerar_pdf_reclamacao_caaj()
    gerar_pdf_requerimento_levantamento()
    gerar_pdf_despacho_suspensao_unicre()
    gerar_pdf_compendio_atos()
    print("=" * 80)
    print(" TODOS OS 6 ATOS FORAM GERADOS COM SUCESSO EM PDF!")
    print("=" * 80)

if __name__ == "__main__":
    gerar_todos_os_pdfs()
