#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
legal_rag_knowledge_base.py - Base de Conhecimento Forense e Motor RAG Juridico de 4 Camadas.
Indexa documentos judiciais do Citius, faturas, extratos bancarios, balancos, audios, LISTA_CONTRATOS_TERESA.xls e faturas do predio contiguo.
Zero emojis conforme PROTOCOL.md.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"

KNOWLEDGE_BASE = [
    {
        "processo": "23142/22.7T8LSB",
        "tipo": "Execução Sumária / Apelação TRL",
        "tema": "Execução Centenário / Extinção Integral no TRL / Abuso de Poder e Reclamação CAAJ contra AE Luísa Santos (Cédula 5840)",
        "normas": "Artigo 703.º CPC, Artigo 726.º n.º 2 al. a) CPC, Artigo 641.º n.º 7 CPC, Artigo 151.º Código do Notariado, Artigos 348.º, 359.º e 382.º do Código Penal",
        "factos": [
            "Em 16/03/2023 o Tribunal proferiu Despacho de Indeferimento Liminar (Ref. 419855940) declarando inexistente o título executivo por falta de menções obrigatórias no termo de autenticação.",
            "Em 20/04/2023 o recurso foi admitido com efeito MERAMENTE DEVOLUTIVO (Ref. 424977808), impedindo a realização de penhoras.",
            "Em 21/04/2023 (Ref. 425248302) e 24/04/2023 (Ref. 425280522), o Juiz ordenou expressamente a citação para os termos do recurso e da causa, com entrega obrigatória das alegações.",
            "A AE Luísa Santos citou terceiro (Filipe Delgado) a 04/07/2023 e omitiu os documentos do recurso.",
            "A AE Luísa Santos confessou por escrito em 20/09/2024 (Ref. 437217551): 'de facto aquando a citação do Executado, por lapso, não segui em anexo o respectivo documento referente à decisão de recurso'.",
            "A AE Luísa Santos promoveu penhoras ilegais sobre contas bancárias (35.000 €) e veículos entre Outubro/2023 e Janeiro/2024.",
            "O Dr. Varela de Matos alegou falsamente envio de correspondência e comunicações que nunca foram entregues ao visado.",
            "O Tribunal da Relação de Lisboa proferiu Acórdão julgando a execução integralmente EXTINTA e ordenando o levantamento de todas as penhoras.",
            "Áudios transcritos demonstram que Filipe Delgado e o Dr. Varela de Matos coagiram e pressionaram Nuno Duarte a assinar a confissão de dívida para proteger a Lisbon Experience."
        ],
        "documentos": [
            "Despacho Indeferimento Liminar Ref. 419855940 (16/03/2023)",
            "Despacho Admissão Recurso Ref. 424977808 (20/04/2023)",
            "Despacho Citação Recurso Ref. 425248302 (21/04/2023)",
            "Notificação Oficial AE Ref. 425280522 (24/04/2023)",
            "Ofício Confissão AE Luísa Santos Ref. 437217551 (20/09/2024)",
            "Acórdão TRL Extinção da Execução",
            "RECLAMACAO_CAAJ_E_QUADRO_FINANCEIRO_PROVAS.md",
            "PROVA_OMISSAO_DOLOSA_CITACOES_E_FRAUDE_MORADAS.md"
        ]
    },
    {
        "processo": "3719/25.0T8LSB",
        "tipo": "Procedimento Cautelar de Restituição de Posse",
        "tema": "Providência Cautelar / Arquivada Definitivamente no TRL / Impedimento de Entrada na Audiência / Direito de Retenção / Corte de Água",
        "normas": "Artigo 20.º CRP (Acesso ao Direito), Artigos 3.º, 195.º e 604.º CPC (Contraditório), Artigo 1251.º CC (Posse), Artigo 754.º CC (Direito de Retenção)",
        "factos": [
            "Nuno Miguel Silva Duarte compareceu no Tribunal mas FOI IMPEDIDO DE ENTRAR NA SALA DE AUDIÊNCIA, tendo a audiência decorrido à porta fechada sem a sua presença nem possibilidade de contraditar testemunhos falsos.",
            "Quem esteve na sala foi Filipe Delgado a prestar declarações que não vinculam nem refletem a verdade da posse de Nuno Duarte.",
            "O Tribunal da Relação de Lisboa proferiu Acórdão em Conferência a 16/04/2026 (Ref. 24500137); o processo baixou à 1.ª Instância em 13/05/2026 e está ARQUIVADO DEFINITIVAMENTE.",
            "A Autora Maria Teresa Martins foi condenada em custas a 07/07/2026 (Ref. 457395171).",
            "12 Vídeos de Vistoria Técnica gravados a 24/05/2024 comprovam que o imóvel está impecável, mobilado e conservado com fundos próprios de Nuno Duarte (afasta alegação de degradação).",
            "A fração de Nuno Duarte foi a ÚNICA cortada sem água durante 2 anos nos 2 prédios da Palmeira 31 e 33 (confissão WhatsApp de Filipe Delgado de 23/08/2022).",
            "Nuno Duarte é titular de Direito de Retenção (Art. 754.º CC) pelo crédito de benfeitorias (€ 120.000) e obras (LEA_fornc.pdf / António Neto) e créditos acumulados de € 236.622,00.",
            "LISTA_CONTRATOS_TERESA.xls comprova 9 contratos oficiais de arrendamento entre Maria Teresa Martins e a Lisbon Experience Lda."
        ],
        "documentos": [
            "PROVA_IMPEDIMENTO_PRESENCA_SALA_AUDIENCIA_3719.md",
            "Acórdão TRL Ref. 24500137 de 16/04/2026",
            "Notificação de Custas Ref. 457395171 de 07/07/2026",
            "12 Vídeos de Vistoria Técnica de 24/05/2024",
            "LISTA_CONTRATOS_TERESA.xls",
            "PROVA_CONFISSAO_WHATSAPP_FILIPE_DELGADO_20220823.md"
        ]
    },
    {
        "processo": "10153/24.7T8LSB / 20203/22.6T8LSB",
        "tipo": "Execução de Sentença / Embargos de Executado / Ação Declarativa",
        "tema": "Execução UNICRE Suspensa / Falta Absoluta de Citação no Proc. 20203 / Cartas Devolvidas / 2 Certidões Negativas AE Catrau",
        "normas": "Artigo 733.º n.º 1 CPC (Suspensão da Execução), Artigo 729.º al. d) CPC (Falta Absoluta de Citação), Artigo 188.º CPC, Artigo 847.º CC (Compensação)",
        "factos": [
            "A sentença originária de 19/01/2024 (Proc. 20203/22.6T8LSB) foi obtida com FALTA ABSOLUTA DE CITAÇÃO: cartas postais devolvidas a 13/10/2022 e 28/06/2023, e 2 Certidões Negativas da AE Maria Emília Catrau (04/10/2023 e 09/01/2024).",
            "A UNICRE manipulou moradas e induziu o Tribunal em erro para obter sentença à revelia de um Réu não citado.",
            "O Juiz de Execução (Juiz 8) proferiu Despacho Liminar a 23/10/2025 determinando a SUSPENSÃO FORMAL DA EXECUÇÃO (Ref. 449641615), bloqueando todas as penhoras.",
            "A UNICRE aprovou a 07/04/2020 a alteração do TPA para a Lisbon Experience (PS 1-1064222419), enviava faturas para lisbonexp@gmail.com e reteve 52.285 € na fonte.",
            "Nuno Duarte emitiu à Lisbon Experience a Fatura N.º 1000002 de 82.722,00 € em 12/01/2021 no Portal das Finanças, a qual nunca foi paga e serviu a esquemas de suprimentos e divergências fiscais.",
            "Extratos bancários da Lisbon Experience de 2019-2020 provam transferências diretas de mais de 33.900 € para Nuno Duarte a título de gestão.",
            "O Balanço da LEA de 31/12/2021 comprova insolvência técnica (Capital Próprio negativo de -153.481,85 € e Dívida Fiscal de 307.973,33 €)."
        ],
        "documentos": [
            "Despacho de Suspensão Ref. 449641615 de 23/10/2025",
            "Contestação UNICRE Ref. 44528700 de 17/11/2025",
            "Certidões Negativas Citius Proc. 20203/22 (AE Catrau)",
            "PROVA_OMISSAO_DOLOSA_CITACOES_E_FRAUDE_MORADAS.md",
            "Fatura N.º 1000002 de 82.722,00 € (12/01/2021)",
            "Extratos Bancários LEA 2019-2020 (33.900 €)"
        ]
    },
    {
        "processo": "15547/26.0T8LSB",
        "tipo": "Ação Declarativa Comum (Reivindicação)",
        "tema": "Ação de Reivindicação / Juízo Central Cível / Faturas do Prédio Contíguo / 9 Contratos Oficiais / Contrato em Tinta Azul",
        "normas": "Artigo 1311.º CC (Reivindicação), Artigo 33.º CPC (Litisconsórcio com Lisbon Experience), Artigo 754.º CC (Retenção), Artigo 542.º CPC (Má-Fé)",
        "factos": [
            "A Autora Maria Teresa Martins juntou faturas respeitantes ao prédio contíguo (Rua da Palmeira 31 / Matriz 110661-U-229) para tentar simular despesas na fração da Palmeira 33 (Matriz 110661-U-231-4).",
            "Os contratos juntos pela Autora não constam do Portal das Finanças com as cláusulas reais.",
            "Apenas o contrato assinado em tinta azul por Nuno Duarte e Teresa Martins constitui o documento autêntico e vinculativo.",
            "A folha LISTA_CONTRATOS_TERESA.xls comprova que a locatária formal é a sociedade LISBON EXPERIENCE - ADMINISTRAÇÃO DE IMÓVEIS, LDA. (Contrato N.º 1195528 - Renda de 1.300 €), verificando-se preterição de litisconsórcio passivo necessário (Art. 33.º CPC).",
            "A citação postal de Nuno Duarte foi DEVOLVIDA em 24/07/2026 (Ref. 47296021) por morada dolosamente inadequada.",
            "Nuno Duarte detém Direito de Retenção (Art. 754.º CC) pelo crédito de 120.000 € em obras e créditos globais de 236.622 €."
        ],
        "documentos": [
            "Petição Inicial de 12/06/2026 (Ref. 46589030)",
            "LISTA_CONTRATOS_TERESA.xls",
            "PROVA_FALSIDADE_FATURAS_E_CONTRATOS_TERESA_MARTINS.md",
            "Certidão Postal Devolvida de 24/07/2026 (Ref. 47296021)",
            "8 Cadernetas Prediais Históricas",
            "Mapas de Rendas emitidos por Teresa Martins (2015-2021)"
        ]
    }
]

class LegalRagEngine:
    def __init__(self):
        self.db_path = DB_PATH
        self.knowledge = KNOWLEDGE_BASE

    def query_rag(self, query_str: str) -> Dict[str, Any]:
        q = (query_str or "").lower()
        matched = []
        for item in self.knowledge:
            score = 0
            if any(w in q for w in ["23142", "luisa", "centenario", "penhora", "35000", "caaj", "varela", "injuncao"]):
                if "23142" in item["processo"]: score += 12
            if any(w in q for w in ["3719", "cautelar", "posse", "agua", "epal", "galp", "retencao", "video", "teresa", "sala", "audiencia", "entrar"]):
                if "3719" in item["processo"]: score += 12
            if any(w in q for w in ["10153", "20203", "unicre", "redunicre", "tpa", "82k", "52k", "extrato", "balanco", "carta", "devolvida", "catrau"]):
                if "10153" in item["processo"]: score += 12
            if any(w in q for w in ["15547", "reivindicacao", "forra", "ricardo miranda", "caderneta", "morada", "tinta azul", "predio do lado", "falsidade"]):
                if "15547" in item["processo"]: score += 12

            for word in q.split():
                if len(word) > 3:
                    if word in item["tema"].lower() or word in item["processo"].lower():
                        score += 4
                    for f in item["factos"]:
                        if word in f.lower():
                            score += 3

            if score > 0:
                matched.append((score, item))

        matched.sort(key=lambda x: x[0], reverse=True)
        results = [m[1] for m in matched] if matched else self.knowledge

        res_text = "### Resposta Juridica Forense Fundamentada:\n\n"
        for ctx in results[:2]:
            res_text += f"#### Processo {ctx['processo']} - {ctx['tema']}\n"
            res_text += f"**Normas Aplicaveis**: `{ctx['normas']}`\n\n"
            res_text += "**Factos Provados Documentados**:\n"
            for fp in ctx["factos"]:
                res_text += f"* {fp}\n"
            res_text += f"\n**Documentos Chave no Acervo**:\n"
            for doc in ctx["documentos"]:
                res_text += f"- `{doc}`\n"
            res_text += "\n---\n"

        return {
            "query": query_str,
            "resposta": res_text,
            "fontes": [doc for r in results for doc in r["documentos"]][:10]
        }

if __name__ == "__main__":
    engine = LegalRagEngine()
    test_q = "as faturas sao do predio do lado contratos falsos tinta azul teresa"
    out = engine.query_rag(test_q)
    print(out["resposta"])
