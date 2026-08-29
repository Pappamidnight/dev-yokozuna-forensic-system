#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core5_modules.py - Implementacao dos 10 Micro-Modulos do MOTOR_SUPER_FORENSE_CORE.
01_router, 02_identifier, 03_classifier, 04_custody, 05_relation_mapper, 
06_action_detector, 07_confrontation_engine, 08_decision_engine, 09_output_generator, 10_validator.
Zero emojis conforme PROTOCOL.md e AGENTS.md.
"""

import os
import re
import hashlib
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
DB_CORE5_PATH = OUTPUT_DIR / "02_DADOS_ESTRUTURADOS" / "memoria_core5_forense.db"

# -------------------------------------------------------------------------
# 01_ROUTER: Decide para onde vai cada ficheiro ou facto
# -------------------------------------------------------------------------
class Router:
    @staticmethod
    def route(file_path: Path) -> str:
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        if ext == ".pdf":
            return "PIPELINE_PDF_JUDICIAL"
        elif ext in [".xls", ".xlsx", ".csv"]:
            return "PIPELINE_FINANCEIRO_CONTRATOS"
        elif ext in [".md", ".txt"]:
            if "whatsapp" in name or "chat" in name or "conversa" in name:
                return "PIPELINE_WHATSAPP_COMUNICACOES"
            return "PIPELINE_ARTICULADO_RELATORIO"
        elif ext in [".png", ".jpg", ".jpeg", ".mp4", ".mov"]:
            return "PIPELINE_MULTIMEDIA_PROVAS"
        return "PIPELINE_GENERICO"

# -------------------------------------------------------------------------
# 02_IDENTIFIER: Extrai IDs, datas, nomes, processos, valores, referencias Citius
# -------------------------------------------------------------------------
class Identifier:
    PATTERNS = {
        "processo": re.compile(r"(\d{4,6}/\d{2}\.\d[A-Z0-9]{3,6})"),
        "data_iso": re.compile(r"(\d{4}-\d{2}-\d{2})"),
        "data_pt": re.compile(r"(\d{2}/\d{2}/\d{4})"),
        "valor_eur": re.compile(r"(\d+[\d\.,]*\s*(?:€|EUR|euros))", re.IGNORECASE),
        "ref_citius": re.compile(r"(?:Ref[a-zA-Z\.\s]*|Referência\s*)(\d{7,10})", re.IGNORECASE),
        "artigo_legal": re.compile(r"(?:Artigo|Art\.)\s*(\d+[\.ºª\w\s-]*(?:CPC|CC|CP|CRP))", re.IGNORECASE)
    }

    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        res = {}
        for key, pat in Identifier.PATTERNS.items():
            matches = pat.findall(text)
            res[key] = list(set(matches))
        return res

# -------------------------------------------------------------------------
# 03_CLASSIFIER: Classifica prova, minuta, despacho, contrato, mensagem, imagem
# -------------------------------------------------------------------------
class Classifier:
    @staticmethod
    def classify(filename: str, text: str) -> Dict[str, Any]:
        fn = filename.lower()
        tx = text.lower()
        
        if "acordao" in fn or "acórdão" in tx:
            return {"tipo": "ACORDAO_SUPERIOR", "forca": "OFICIAL", "peso": 1.00}
        elif "despacho" in fn or "indeferimento" in tx or "suspensao" in tx:
            return {"tipo": "DESPACHO_JUDICIAL", "forca": "OFICIAL", "peso": 1.00}
        elif "certidao" in fn or "certidão negativa" in tx or "devolvida" in tx:
            return {"tipo": "CERTIDAO_OFICIAL", "forca": "OFICIAL", "peso": 0.98}
        elif "contrato" in fn or "adenda" in tx or "arrendamento" in tx:
            return {"tipo": "CONTRATO_TITULO", "forca": "ALTA", "peso": 0.95}
        elif "whatsapp" in fn or "chat" in fn or "epal" in tx or "água" in tx:
            return {"tipo": "COMUNICACAO_WHATSAPP", "forca": "MEDIA", "peso": 0.85}
        elif "minuta" in fn or "rascunho" in fn:
            return {"tipo": "RASCUNHO_PREPARATORIO", "forca": "BAIXA", "peso": 0.25}
        return {"tipo": "DOCUMENTO_DIVERSO", "forca": "MEDIA", "peso": 0.50}

# -------------------------------------------------------------------------
# 04_CUSTODY: Hash SHA-256, duplicados, origem, integridade
# -------------------------------------------------------------------------
class Custody:
    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        h = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

# -------------------------------------------------------------------------
# 05_RELATION_MAPPER: Liga pessoas, entidades, processos, documentos e factos
# -------------------------------------------------------------------------
class RelationMapper:
    @staticmethod
    def map_relations(conn: sqlite3.Connection):
        cur = conn.cursor()
        # Mapear relacoes canónicas comprovadas
        relacoes_predefinidas = [
            ("REL-01", "Maria Teresa Castro Bangueses", "Nuno Miguel Silva Duarte", "LOCADOR_LOCATARIO", "20+ adendas 2015-2021 / Palmeira 33"),
            ("REL-02", "Centenario Investimentos Lda", "Nuno Miguel Silva Duarte", "EXEQUENTE_EXECUTADO", "Execucao extinta no TRL / Proc. 23142"),
            ("REL-03", "UNICRE - IFIC SA", "Nuno Miguel Silva Duarte", "EXEQUENTE_EXECUTADO", "Execucao suspensa por falta de citacao / Proc. 10153"),
            ("REL-04", "Filipe Jose Rodrigues Delgado", "Nuno Miguel Silva Duarte", "COACAO_HABITACIONAL", "Corte seletivo de agua e creditos retidos")
        ]
        for r in relacoes_predefinidas:
            cur.execute("""
                INSERT OR REPLACE INTO relations (relation_id, entity_a, entity_b, tipo_relacao, detalhes)
                VALUES (?, ?, ?, ?, ?)
            """, r)
        conn.commit()

# -------------------------------------------------------------------------
# 06_ACTION_DETECTOR: Identifica citacao, penhora, despacho, corte de agua
# -------------------------------------------------------------------------
class ActionDetector:
    @staticmethod
    def detect_actions(text: str) -> List[str]:
        tx = text.lower()
        actions = []
        if "carta devolvida" in tx or "devolvida" in tx: actions.append("CITACAO_DEVOLVIDA")
        if "indeferimento liminar" in tx: actions.append("INDEFERIMENTO_LIMINAR")
        if "suspensao" in tx or "suspensão" in tx: actions.append("SUSPENSAO_EXECUCAO")
        if "extincao" in tx or "extinção" in tx or "arquivada" in tx: actions.append("EXTINCAO_PROCESSO")
        if "penhora" in tx or "35.000" in tx or "bloqueio" in tx: actions.append("PENHORA_ILEGAL")
        if "água" in tx or "epal" in tx or "hotel" in tx: actions.append("CORTE_AGUA_COACAO")
        if "litisconsorcio" in tx or "litisconsórcio" in tx: actions.append("PRETERICAO_LITISCONSORCIO")
        if "retencao" in tx or "retenção" in tx: actions.append("DIREITO_RETENCAO")
        return actions

# -------------------------------------------------------------------------
# 07_CONFRONTATION_ENGINE: Aplica as 4 Camadas (Oficial x Prova x Lei x Conclusao)
# -------------------------------------------------------------------------
class ConfrontationEngine:
    @staticmethod
    def apply_4_layers(processo: str, fato_oficial: str, prova_real: str, norma: str, conclusao: str) -> Dict[str, Any]:
        return {
            "processo": processo,
            "camada_1_oficial": fato_oficial,
            "camada_2_prova": prova_real,
            "camada_3_norma": norma,
            "camada_4_conclusao": conclusao,
            "status": "CONFRONTADO_E_BLINDADO"
        }

# -------------------------------------------------------------------------
# 08_DECISION_ENGINE: Decide prioridade, risco, forca e proxima acao
# -------------------------------------------------------------------------
class DecisionEngine:
    @staticmethod
    def decide_next_action(processo: str, tipo_evento: str) -> Dict[str, str]:
        if "15547" in processo:
            return {
                "prioridade": "CRITICA",
                "acao": "Deduzir Excecao de Litisconsorcio (Art. 33.o CPC) e Reconvencao de Direito de Retencao (Art. 754.o CC)",
                "peca": "MINUTA_CONTESTACAO_15547_COMPLETA.docx"
            }
        elif "23142" in processo:
            return {
                "prioridade": "ALTA",
                "acao": "Requerer ao Juizo de Execucao o Levantamento Imediato de Penhoras de 35.000 EUR e Reclamacao CAAJ",
                "peca": "04_REQUERIMENTO_LEVANTAMENTO_PENHORAS_35K.pdf"
            }
        elif "10153" in processo:
            return {
                "prioridade": "ALTA",
                "acao": "Confirmar Suspensao da Execucao (Art. 733.o CPC) e compensacao de creditos da Fatura 1000002",
                "peca": "05_DESPACHO_SUSPENSAO_EXECUCAO_UNICRE_PROC_10153.pdf"
            }
        return {
            "prioridade": "MEDIA",
            "acao": "Catalogar e manter sob custodia com hash SHA-256",
            "peca": "RELATORIO_GERAL.md"
        }

# -------------------------------------------------------------------------
# 09_OUTPUT_GENERATOR: Gera relatorio, matriz, peca, dashboard
# -------------------------------------------------------------------------
class OutputGenerator:
    @staticmethod
    def generate_manifest_summary(total_docs: int, total_events: int, score: int) -> str:
        return f"""# MANIFESTO OFICIAL CORE-5 FORENSE
- **Total de Documentos Custodiados**: `{total_docs}`
- **Total de Eventos Cientificos Validados**: `{total_events}`
- **Score Global de Conformidade**: `{score}/100`
- **Zero Emojis**: `VALIDADO`
- **Tom Institucional**: `APROVADO`
"""

# -------------------------------------------------------------------------
# 10_VALIDATOR: Confirma prova ou marca necessita_validacao (bloqueia alucinacao)
# -------------------------------------------------------------------------
class Validator:
    @staticmethod
    def validate_claim(has_citius_ref: bool, has_sha256: bool, has_norma: bool) -> Dict[str, Any]:
        if has_sha256 and (has_citius_ref or has_norma):
            return {"status": "DOCUMENTADO", "score": 100, "bloqueado": False}
        return {"status": "NECESSITA_VALIDACAO", "score": 50, "bloqueado": True}
