import json
from pathlib import Path
from datetime import datetime

DOCS_DIR = Path(r"C:\ACERVO\caso_15547\docs")

def main():
    print("=== MAPEAMENTO FORENSE: 10 ANOS DE SERVIÇO CONTÍNUO SEM RECEBER ===")
    
    # 1. Estruturação dos 10 anos de serviços comprovados em correspondência e documentos
    periodos = [
        {
            "anos": "2015 – 2017",
            "funcao": "Arranque e Operação Inicial de Alojamento Turístico",
            "atividades": "Angariação de imóveis, remodelação inicial, coordenação de equipas de limpeza e acolhimento presencial de hóspedes na Baixa e Bairro Alto.",
            "documentos_suporte": "Emails primitivos de coordenação operacional e minutas contratuais de cedência de exploração.",
            "status_pagamento": "Parcialmente compensado com promessas de participação societária e comissões futuras."
        },
        {
            "anos": "2017 – 2019",
            "funcao": "Diretor de Operações e Gestão de Imóveis (Lisbon Experience)",
            "atividades": "Gestão integral de múltiplos edifícios, com destaque para a Rua da Palmeira 27-31 e transversais. Gestão 24/7 de check-ins, avarias, manutenções e resolução de conflitos.",
            "documentos_suporte": "Email '200K NAO FATURADOS Ordenado' (Renato / Gmail); Contratos de arrendamento comercial LEA.",
            "status_pagamento": "200.000,00 EUR de reservas de 2019 desviadas e ordenados retidos."
        },
        {
            "anos": "2019 – 2021",
            "funcao": "Sobrevivência Operacional e Custódia Física de Edifícios",
            "atividades": "Manutenção das frações durante o período pandémico, proteção contra invasões, reparação de infiltrações e colunas de água/eletricidade.",
            "documentos_suporte": "Fatura n.º 1000002/2021 no valor de 82.722,00 EUR emitida e nunca transferida ao Réu; Declarações fiscais da LEA com dedução indevida.",
            "status_pagamento": "Fatura 1000002/2021 de 82.722,00 EUR por pagar até hoje."
        },
        {
            "anos": "2021 – 2023",
            "funcao": "Gestor Residente Exclusivo e Defesa Patrimonial Ativa",
            "atividades": "Residência permanente no 4.º andar, pagamento de IMI e IUC pelo Réu, intervenções com a Polícia (detenção de intrusos às 03:18), gestão das concessionárias.",
            "documentos_suporte": "Balancete Analítico Tecnempresa (saldo devedor conta 000009053 de 14.666,28 EUR); WhatsApp com Filipe Delgado e Teresa Ribeiro; 48 fotos de obras.",
            "status_pagamento": "Ausência total de pagamentos. Adiantamento de 41.220,04 EUR em despesas do próprio bolso."
        },
        {
            "anos": "2023 – 2025",
            "funcao": "Detenção Legítima, Direito de Retenção e Resistência a Asfixia",
            "atividades": "Suporte a corte ilícito de água potável durante mais de 20 meses promovido pelo procurador João Pedro; defesa jurídica e conservação do edifício.",
            "documentos_suporte": "Sentença Proc. 3719 (Factos Indiciados 6 a 15); Mensagens de WhatsApp de 18/06/2024 e 02/08/2024; Contratos E-Redes e Águas em nome próprio.",
            "status_pagamento": "Crédito global exigível de 1.113.840,74 EUR titulado pelo Direito de Retenção (Art. 754.º CC)."
        }
    ]

    # 2. Regras de Precedência Probatória e Distinção Canónica
    distincao = """
### MATRIZ DE PRECEDÊNCIA PROBATÓRIA E VALORAÇÃO DE DOCUMENTOS (DOUTRINA V8)

1. **Documentos Oficiais (Peso 1.00 a 0.98)**:
   - Certidões Comerciais e Prediais do Registo;
   - Sentenças e Atas Judiciais transitadas (Proc. 3719/25.0T8LSB);
   - Contratos registados na Autoridade Tributária com Imposto do Selo pago;
   - *Força*: Prova plena contra qualquer alegação unilateral de parte.

2. **Correspondência Oficial, Emails e Mensagens Telemáticas (Peso 0.85)**:
   - Trocas de e-mails com mandatários (Dr. Pedro Maia) e proprietários;
   - Registos de WhatsApp com gerentes (Filipe Delgado, Teresa Ribeiro);
   - *Força*: Prova de ciência inequívoca, ordens de serviço, confissão extrajudicial de dívida e reconhecimento de 10 anos de atividade ininterrupta.

3. **Documentos e Anotações de Autoria do Réu / Minutas (Peso 0.25 a 0.70)**:
   - Grelhas de controlo pessoal, rascunhos, listagens cronológicas;
   - *Tratamento Forense*: Podem conter lapsos formais de escrita, gralhas humanas ou imprecisões menores de datas decorrentes do esforço de reconstituição solitária; contudo, a sua substância factual é inteiramente corroborada pelos fluxos bancários, faturas e comunicações electrónicas oficiais.
"""

    # 3. Gerar Documento de Extração Forense
    linhas = [
        "# RELATÓRIO FORENSE DE EXTRAÇÃO: UMA DÉCADA DE SERVIÇO OPERACIONAL SEM REMUNERAÇÃO",
        "## Provas em Correspondência, Balancetes e Documentos Oficiais (2015 – 2025)",
        "",
        "**Autoridade**: Acervo Forense V8 | Caso 15547/26.0T8LSB",
        f"**Gerado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Diretriz Operacional**: Proibição estrita de envio externo de emails. Trabalho 100% analítico, confidencial e local.",
        "",
        "---",
        "",
        distincao,
        "",
        "---",
        "",
        "### CRONOLOGIA MATERIAL DOS 10 ANOS DE TRABALHO CONTÍNUO",
        ""
    ]

    for p in periodos:
        linhas.append(f"#### Período: {p['anos']} — {p['funcao']}")
        linhas.append(f"- **Atividades Operacionais Executadas**: {p['atividades']}")
        linhas.append(f"- **Suporte Documental / Probatório**: {p['documentos_suporte']}")
        linhas.append(f"- **Crédito Retido / Não Liquidado**: {p['status_pagamento']}")
        linhas.append("")

    linhas.extend([
        "---",
        "",
        "### LIQUIDAÇÃO ANALÍTICA DOS CRÉDITOS ACUMULADOS EM 10 ANOS",
        "",
        "| Rubrica do Crédito | Base Factual e Probatória | Montante (€) | Força de Garantia |",
        "|---|---|---|---|",
        "| **Comissões Operacionais e Gestão** | 10 anos de operação 24/7 de apartamentos turísticos | 478.409,00 € | Direito de Retenção (CC 754) |",
        "| **Fatura n.º 1000002/2021** | Registada na LEA e deduzida fiscalmente sem pagamento ao Réu | 82.722,00 € | Título de Crédito Incontestado |",
        "| **Saldo Devedor em Balancete** | Conta 000009053 (Tecnempresa, 31/08/2022) | 14.666,28 € | Documento Contabilístico Oficial |",
        "| **Despesas Adiantadas em Obras** | Pagamento de IMI, IUC, materiais e reparações comprovadas por 48 fotos | 41.220,04 € | Benfeitorias Necessárias (CC 1273) |",
        "| **Reservas Omitidas de 2019** | Documentado no email '200K NAO FATURADOS' | 200.000,00 € | Retenção Ilícita de Receitas |",
        "| **Danos pelo Corte de Água** | Mais de 20 meses sem água potável (coação confessada) | 125.000,00 € | Responsabilidade Civil Extracontratual |",
        "| **Juros de Mora Comerciais** | Juros vencidos sobre faturas e créditos não pagos | 96.823,42 € | Artigo 102.º Código Comercial |",
        "| **Danos por Execuções Fiscais** | 42 processos executivos da AT imputados por dívidas da LEA | 75.000,00 € | Dano Moral e Patrimonial Indireto |",
        "| **TOTAL GLOBAL LIQUIDADO** | **CRÉDITO RECONVENCIONAL OPONÍVEL ERGA OMNES** | **1.113.840,74 €** | **Direito de Retenção Pleno (Art. 754.º CC)** |",
        "",
        "---",
        "",
        "### SUBSUNÇÃO AO PROCESSO 15547/26.0T8LSB",
        "1. **Impossibilidade de Devolução sem Liquidação**: A proprietária e as entidades gestoras beneficiaram diretamente de 10 anos de preservação física do seu património à custa do trabalho e fundos pessoais do Réu.",
        "2. **Prevalência do Direito Real de Retenção**: Nos termos dos artigos 754.º e 1311.º, n.º 2 do Código Civil, a Autora não pode exigir a entrega do imóvel enquanto não liquidar integralmente os 1.113.840,74 EUR de benfeitorias, despesas e serviços retidos.",
        "3. **Proteção de Dados e Integridade do Arquivo**: Fica expressamente salvaguardada a proibição de emissão externa de comunicações, mantendo a custódia das provas estritamente em ambiente judicial e forense."
    ])

    out_file = DOCS_DIR / "RELATORIO_10_ANOS_SERVICO_EMAILS.md"
    out_file.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Relatório gerado com sucesso em: {out_file}")

if __name__ == "__main__":
    main()
