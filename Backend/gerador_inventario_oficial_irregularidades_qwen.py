#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerador_inventario_oficial_irregularidades_qwen.py - Inventario Forense Mestre de Atos Oficiais, Irregularidades e Narrativas Falsas vs Verdade.
Tom estritamente neutro, sobrio e documental. Proibicao absoluta de emocoes e emojis conforme PROTOCOL.md e AGENTS.md.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
REPORT_MD = OUTPUT_DIR / "01_INDEX_E_RELATORIOS" / "INVENTARIO_GERAL_OFICIAL_E_IRREGULARIDADES_QWEN.md"
REPORT_PDF = OUTPUT_DIR / "05_PDFS_GERADOS_PARA_IMPRESSAO" / "08_INVENTARIO_GERAL_OFICIAL_E_IRREGULARIDADES.pdf"

PROCESSOS_OFICIAIS = [
    {
        "processo": "23142/22.7T8LSB",
        "tribunal": "Tribunal Judicial da Comarca de Lisboa",
        "juizo": "Juízo de Execução de Lisboa - Juiz 6 / Juiz 1 (e Tribunal da Relação de Lisboa)",
        "especie": "Ação Executiva Sumária (e Recurso de Apelação)",
        "polo_ativo": "Centenário Investimentos Imobiliários, Lda. (Mandatário: Dr. Varela de Matos)",
        "polo_passivo": "Nuno Miguel Silva Duarte (NIF 254048382)",
        "agente_execucao": "Luísa Santos (Cédula Profissional 5840)",
        "datas_chave": "16/03/2023 (Indeferimento Liminar), 20/04/2023 (Admissão Recurso Devolutivo), 20/09/2024 (Confissão AE), 16/04/2026 (Acórdão TRL Extinção)",
        "referencias_citius": [
            {"ref": "419855940", "data": "16/03/2023", "ato": "Despacho de Indeferimento Liminar", "significado": "Declara inexistente o título executivo por omissão de menções no termo notarial."},
            {"ref": "424977808", "data": "20/04/2023", "ato": "Despacho de Admissão de Recurso", "significado": "Fixa efeito MERAMENTE DEVOLUTIVO ao recurso de apelação da exequente."},
            {"ref": "425248302", "data": "21/04/2023", "ato": "Despacho de Citação para Recurso", "significado": "Ordena citação expressa do executado com entrega das alegações de recurso."},
            {"ref": "425280522", "data": "24/04/2023", "ato": "Notificação Oficial da Secretaria à AE", "significado": "Determina à AE Luísa Santos o cumprimento da citação com todos os anexos."},
            {"ref": "437217551", "data": "20/09/2024", "ato": "Ofício de Confissão da AE Luísa Santos", "significado": "Confessa formalmente por escrito omissão das alegações e decisão na citação."},
            {"ref": "448881152", "data": "18/10/2024", "ato": "Despacho Judicial sobre Incidente", "significado": "Reconhece a falta de envio das alegações e abre contraditório."},
            {"ref": "24500137",  "data": "16/04/2026", "ato": "Acórdão do Tribunal da Relação de Lisboa", "significado": "Julga a execução integralmente EXTINTA e ordena levantamento de penhoras."}
        ]
    },
    {
        "processo": "3719/25.0T8LSB",
        "tribunal": "Tribunal Judicial da Comarca de Lisboa",
        "juizo": "Juízo Local Cível de Lisboa (e Tribunal da Relação de Lisboa)",
        "especie": "Procedimento Cautelar Comum / Restituição Provisória de Posse",
        "polo_ativo": "Maria Teresa Castro Bangueses Ribeiro (Mandatário: Dr. Nuno Forra)",
        "polo_passivo": "Nuno Miguel Silva Duarte",
        "datas_chave": "06/11/2025 (Audiência com impedimento de presença), 16/04/2026 (Acórdão TRL Arquivamento), 13/05/2026 (Baixa à 1.ª Instância), 07/07/2026 (Custas à Autora)",
        "referencias_citius": [
            {"ref": "445890123", "data": "06/11/2025", "ato": "Ata de Audiência de Julgamento", "significado": "Audiência realizada com terceiros sem a presença física de Nuno Duarte."},
            {"ref": "24500137",  "data": "16/04/2026", "ato": "Acórdão da Relação de Lisboa", "significado": "Julga o procedimento cautelar extinto e determina o seu arquivamento definitivo."},
            {"ref": "455899454", "data": "19/05/2026", "ato": "Notificação de Baixa dos Autos", "significado": "Confirmação de trânsito e arquivamento formal dos autos no tribunal recorrido."},
            {"ref": "457395171", "data": "07/07/2026", "ato": "Conta e Notificação de Custas", "significado": "Condenação integral da Requerente Maria Teresa Martins no pagamento das custas."}
        ]
    },
    {
        "processo": "10153/24.7T8LSB (e apenso Proc. 20203/22.6T8LSB)",
        "tribunal": "Tribunal Judicial da Comarca de Lisboa",
        "juizo": "Juízo de Execução de Lisboa - Juiz 8",
        "especie": "Embargos de Executado / Oposição à Execução de Sentença",
        "polo_ativo": "UNICRE - Instituição Financeira de Crédito, S.A.",
        "polo_passivo": "Nuno Miguel Silva Duarte",
        "agente_execucao": "Maria Emília Catrau",
        "datas_chave": "13/10/2022 e 28/06/2023 (Cartas devolvidas), 04/10/2023 e 09/01/2024 (2 Certidões Negativas AE), 19/01/2024 (Sentença à revelia), 23/10/2025 (Despacho Suspensão)",
        "referencias_citius": [
            {"ref": "430112998", "data": "04/10/2023", "ato": "1.ª Certidão Negativa de Citação (AE Catrau)", "significado": "Comprova impossibilidade de citação por morada incorreta."},
            {"ref": "434009112", "data": "09/01/2024", "ato": "2.ª Certidão Negativa de Citação (AE Catrau)", "significado": "Segunda certidão formal comprovando a falta de citação do réu."},
            {"ref": "435112009", "data": "19/01/2024", "ato": "Sentença Condenatória à Revelia", "significado": "Sentença nula por ter sido proferida com falta absoluta de citação."},
            {"ref": "449641615", "data": "23/10/2025", "ato": "Despacho Liminar de Suspensão (Juiz 8)", "significado": "Determina formalmente a SUSPENSÃO DA EXECUÇÃO ao abrigo do art. 733.º n.º 1 CPC."},
            {"ref": "44528700",  "data": "17/11/2025", "ato": "Contestação da UNICRE", "significado": "UNICRE admite retenções e operações do TPA associadas à Lisbon Experience."}
        ]
    },
    {
        "processo": "15547/26.0T8LSB",
        "tribunal": "Tribunal Judicial da Comarca de Lisboa",
        "juizo": "Juízo Central Cível de Lisboa - Juiz 4",
        "especie": "Processo Comum Declarativo Cível (Ação de Reivindicação - Artigo 1311.º do CC)",
        "polo_ativo": "Maria Teresa Castro Bangueses Ribeiro (Mandatário: Dr. Nuno Forra)",
        "polo_passivo": "Nuno Miguel Silva Duarte",
        "solicitador_delegado": "Ricardo Miranda",
        "datas_chave": "12/06/2026 (Entrada Petição Inicial), 24/07/2026 (Citação postal devolvida), 04/08/2026 (Delegação para citação pessoal)",
        "referencias_citius": [
            {"ref": "46589030",  "data": "12/06/2026", "ato": "Petição Inicial da Autora", "significado": "Pedido de restituição de fração e indemnização com omissão do litisconsórcio."},
            {"ref": "47296021",  "data": "24/07/2026", "ato": "Certidão de Devolução de Carta Postal", "significado": "Citação postal devolvida por morada incorreta/insuficiente."},
            {"ref": "47917847",  "data": "04/08/2026", "ato": "Termo de Delegação de Citação Pessoal", "significado": "Solicitador Ricardo Miranda delega diligência pessoal após falha postal."}
        ]
    }
]

MATRIZ_NARRATIVAS_E_IRREGULARIDADES = [
    {
        "caso": "Caso 1: Transmissão de Dívida e Penhoras Imediatas",
        "processo": "23142/22.7T8LSB",
        "narrativa_falsa": "A Exequente e mandatário alegaram possuir título executivo líquido e exigível contra Nuno Duarte para cobrança imediata de quantias.",
        "prova_documental_real": "O Juiz 6 indeferiu liminarmente a execução a 16/03/2023 (Ref. 419855940). O recurso subiu com efeito meramente devolutivo (Ref. 424977808). A AE Luísa Santos confessou omissão da citação (Ref. 437217551) e o Tribunal da Relação de Lisboa julgou a execução EXTINTA.",
        "normas_aplicaveis": "Artigos 703.º, 726.º n.º 2 al. a), 641.º n.º 7 e 188.º do CPC; Artigo 382.º do Código Penal.",
        "resultado_processual": "Extinção definitiva da execução, levantamento obrigatório das penhoras de € 35.000 e veículos, e processo disciplinar na CAAJ."
    },
    {
        "caso": "Caso 2: Sentença à Revelia UNICRE",
        "processo": "10153/24.7T8LSB / 20203/22.6T8LSB",
        "narrativa_falsa": "A UNICRE sustentou que o executado foi regularmente notificado e não deduziu oposição, devendo pagar a quantia reclamada.",
        "prova_documental_real": "Constam dos autos duas cartas postais devolvidas (13/10/2022 e 28/06/2023) e duas certidões negativas formais da AE Catrau (04/10/2023 e 09/01/2024). A UNICRE reteve € 52.285 no TPA e Nuno Duarte detém a Fatura N.º 1000002 de € 82.722 emitida no Portal das Finanças.",
        "normas_aplicaveis": "Artigos 188.º, 729.º al. d) e 733.º n.º 1 do CPC; Artigo 847.º do Código Civil (Compensação).",
        "resultado_processual": "Suspensão formal da execução decretada pelo Juiz 8 a 23/10/2025 (Ref. 449641615) e nulidade insanável da sentença por falta absoluta de citação."
    },
    {
        "caso": "Caso 3: Providência Cautelar e Ocupação Recente",
        "processo": "3719/25.0T8LSB",
        "narrativa_falsa": "A Requerente Maria Teresa Martins alegou esbulho violento e ocupação sem título para obter entrega urgente do imóvel.",
        "prova_documental_real": "Nuno Duarte foi impedido de entrar na audiência de 06/11/2025. O TRL proferiu Acórdão em Conferência a 16/04/2026 determinando o arquivamento definitivo da providência e condenando a requerente em custas a 07/07/2026 (Ref. 457395171). 12 vídeos de 24/05/2024 comprovam excelente estado de conservação.",
        "normas_aplicaveis": "Artigo 20.º da CRP (Acesso ao Direito); Artigo 3.º do CPC; Artigo 1251.º e 754.º do Código Civil.",
        "resultado_processual": "Procedimento cautelar arquivado no TRL, trânsito em julgado e custas imputadas integralmente à Requerente."
    },
    {
        "caso": "Caso 4: Ação de Reivindicação e Imputação Cruzada de Faturas",
        "processo": "15547/26.0T8LSB",
        "narrativa_falsa": "A Autora alega que Nuno Duarte é ocupante clandestino e apresenta faturas e caderneta predial para exigir a restituição da posse.",
        "prova_documental_real": "A folha oficial LISTA_CONTRATOS_TERESA.xls comprova que o Contrato N.º 1195528 (4.º andar) foi celebrado com a sociedade Lisbon Experience Lda. (preterição de litisconsórcio necessário). As faturas juntas respeitam ao prédio contíguo (Palmeira 31 / Matriz 110661-U-229). O único contrato autêntico foi assinado em tinta azul. Nuno Duarte suportou € 120.000 em benfeitorias, gozando de Direito de Retenção (Art. 754.º CC).",
        "normas_aplicaveis": "Artigo 33.º e Artigo 577.º al. e) do CPC; Artigo 542.º do CPC (Má-Fé); Artigo 754.º e 1311.º do Código Civil.",
        "resultado_processual": "Exceção dilatória de ilegitimidade singular com absolvição da instância ou improcedência com procedência da Reconvenção e Direito de Retenção."
    }
]

def gerar_inventario_markdown():
    md = [
        "# INVENTÁRIO FORENSE OFICIAL E MATRIZ DE IRREGULARIDADES (ANÁLISE NEUTRA E ESTRUTURADA)",
        "",
        "**Data de Consolidação**: 2026-08-28  ",
        "**Autoridade**: PROTOCOL.md e AGENTS.md (Dev Yokozuna)  ",
        "**Princípio Redatorial**: Tom estritamente sóbrio, neutro, factual e institucional. Proibição de juízos de valor subjetivos ou emotivos.",
        "",
        "---",
        "",
        "## 1. IDENTIFICAÇÃO ESTRUTURADA DOS 4 PROCESSOS JUDICIAIS",
        ""
    ]

    for p in PROCESSOS_OFICIAIS:
        md.append(f"### Processo: `{p['processo']}`")
        md.append(f"- **Tribunal**: {p['tribunal']}")
        md.append(f"- **Juízo / Secção**: {p['juizo']}")
        md.append(f"- **Espécie Processual**: {p['especie']}")
        md.append(f"- **Polo Ativo (Exequente / Autora)**: {p['polo_ativo']}")
        md.append(f"- **Polo Passivo (Executado / Réu)**: {p['polo_passivo']}")
        if "agente_execucao" in p:
            md.append(f"- **Agente de Execução**: {p['agente_execucao']}")
        if "solicitador_delegado" in p:
            md.append(f"- **Solicitador Delegado**: {p['solicitador_delegado']}")
        md.append(f"- **Cronologia de Datas Chave**: {p['datas_chave']}")
        md.append("")
        md.append("#### Atos Oficiais e Referências Citius Registadas:")
        md.append("| Ref. Citius | Data | Peça Processual / Ato | Significado Jurídico e Processual |")
        md.append("|---|---|---|---|")
        for r in p["referencias_citius"]:
            md.append(f"| `{r['ref']}` | {r['data']} | {r['ato']} | {r['significado']} |")
        md.append("")
        md.append("---")
        md.append("")

    md.append("## 2. MATRIZ DE IRREGULARIDADES PROCESSUAIS E CONFRONTO DOCUMENTAL")
    md.append("")

    for m in MATRIZ_NARRATIVAS_E_IRREGULARIDADES:
        md.append(f"### {m['caso']} — `{m['processo']}`")
        md.append("")
        md.append("| Dimensão de Auditoria | Descrição Factual e Documental |")
        md.append("|---|---|")
        md.append(f"| **1. Narrativa da Contraparte** | {m['narrativa_falsa']} |")
        md.append(f"| **2. Prova Documental Real no Acervo** | {m['prova_documental_real']} |")
        md.append(f"| **3. Normas Legais Violadas** | `{m['normas_aplicaveis']}` |")
        md.append(f"| **4. Efeito e Resposta Processual** | **{m['resultado_processual']}** |")
        md.append("")
        md.append("---")
        md.append("")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"[+] Inventário estruturado gravado em: {REPORT_MD}")

def gerar_inventario_pdf():
    REPORT_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "CitiusHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    title_style = ParagraphStyle(
        "CitiusTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=8
    )

    doc = SimpleDocTemplate(str(REPORT_PDF), pagesize=A4, rightMargin=1.2*cm, leftMargin=1.2*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
    story = []

    story.append(Paragraph("<b>INVENTÁRIO OFICIAL DE PROCESSOS, ATOS CITIUS E MATRIZ DE AUDITORIA FORENSE</b>", title_style))
    story.append(Paragraph("<b>AUDITORIA TÉCNICA E DOCUMENTAL — SISTEMA DEV YOKOZUNA (PROTOCOLO NEUTRO E INSTITUCIONAL)</b>", header_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f172a"), spaceAfter=8))

    # Tabela 1: Processos
    proc_rows = [["Processo / Juízo", "Espécie", "Partes / Intervenientes", "Atos e Referências Citius Chave"]]
    for p in PROCESSOS_OFICIAIS:
        partes = f"Req/Autora: {p['polo_ativo']}\nRéu: {p['polo_passivo']}"
        refs = "\n".join([f"• Ref. {r['ref']} ({r['data']}): {r['ato']}" for r in p["referencias_citius"][:3]])
        proc_rows.append([
            f"<b>{p['processo']}</b>\n<font size=6.5 color='#475569'>{p['juizo']}</font>",
            p['especie'],
            partes,
            refs
        ])

    t_proc = Table(proc_rows, colWidths=[4.2*cm, 3.2*cm, 4.8*cm, 6.4*cm])
    t_proc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t_proc)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>MATRIZ DE IRREGULARIDADES PROCESSUAIS E CONFRONTO DOCUMENTAL</b>", header_style))
    story.append(Spacer(1, 4))

    matriz_rows = [["Caso / Processo", "Alegação da Contraparte", "Prova Documental Real", "Resposta Jurídica"]]
    for m in MATRIZ_NARRATIVAS_E_IRREGULARIDADES:
        matriz_rows.append([
            f"<b>{m['caso']}</b>\n<font size=6.5 color='#2563eb'>{m['processo']}</font>",
            m['narrativa_falsa'],
            m['prova_documental_real'],
            f"<b>{m['resultado_processual']}</b>\n<font size=6.5 color='#dc2626'>{m['normas_aplicaveis']}</font>"
        ])

    t_matriz = Table(matriz_rows, colWidths=[3.2*cm, 4.6*cm, 5.8*cm, 5.0*cm])
    t_matriz.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 6.8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t_matriz)

    doc.build(story)
    print(f"[+] PDF consolidado gravado em: {REPORT_PDF}")

if __name__ == "__main__":
    gerar_inventario_markdown()
    gerar_inventario_pdf()
