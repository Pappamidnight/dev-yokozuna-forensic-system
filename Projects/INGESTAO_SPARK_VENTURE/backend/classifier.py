from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional, Any
from backend.schemas.corporate_models import CorporateEntity, CorporateEvidence, ShareholdingRelation, CorporateTypeEnum, SupportLevelEnum

# Dicionario Mestre Heuristico de Entidades Societarias
CORPORATE_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "SPARK_CELTIS_VENTURE_PARTNERS": {
        "name": "Spark Celtis Venture Partners — Sociedade de Capital de Risco, S.A.",
        "type": CorporateTypeEnum.SOCIEDADE_CAPITAL_RISCO,
        "keywords": ["celtis", "capital de risco", "scr", "sociedade de capital de risco", "spark celtis"],
        "registro_cmvm": "CMVM-SCR-7241",
        "nif": "514892341",
        "tags": ["capital-de-risco", "gestora-fundos", "cmvm", "spark-group"]
    },
    "SPARK_CONTAINER_FUND_CMVM": {
        "name": "Spark Container Fund — Fundo de Capital de Risco Fechado (CMVM)",
        "type": CorporateTypeEnum.FUNDO_CMVM,
        "keywords": ["container fund", "fcr", "fundo de capital de risco", "fundo cmvm", "spark container"],
        "registro_cmvm": "CMVM-FCR-9812",
        "tags": ["fundo-cmvm", "fcr", "investimento", "spark-group"]
    },
    "GROWTH_PARTNERS_CAPITAL": {
        "name": "Growth Partners Capital, S.A.",
        "type": CorporateTypeEnum.SOCIEDADE_INVESTIMENTO,
        "keywords": ["growth partners", "growth partners capital", "gpc"],
        "tags": ["investimento-direto", "growth-capital", "spark-group"]
    },
    "INTEGRITATE_CAPITAL_PARTNERS": {
        "name": "Integritate Capital Partners, Lda.",
        "type": CorporateTypeEnum.SOCIEDADE_COMERCIAL_LDA,
        "keywords": ["integritate", "integritate capital", "integritate capital partners"],
        "tags": ["advisory", "participacoes", "spark-group"]
    },
    "NOGUI_CAPITAL_PARTNERS": {
        "name": "Nogui Capital Partners, Lda.",
        "type": CorporateTypeEnum.SOCIEDADE_COMERCIAL_LDA,
        "keywords": ["nogui", "nogui capital", "nogui capital partners"],
        "tags": ["participacoes", "veiculo-holding", "spark-group"]
    },
    "KORA_CAPITAL_PARTNERS": {
        "name": "Kora Capital Partners, Lda.",
        "type": CorporateTypeEnum.SOCIEDADE_COMERCIAL_LDA,
        "keywords": ["kora", "kora capital", "kora capital partners"],
        "tags": ["gestao", "capital-partners", "spark-group"]
    },
    "LIZ_CAPITAL_PARTNERS": {
        "name": "Liz Capital Partners, Lda.",
        "type": CorporateTypeEnum.SOCIEDADE_COMERCIAL_LDA,
        "keywords": ["liz capital", "liz capital partners"],
        "tags": ["advisory", "capital-partners", "spark-group"]
    },
    "UNICORN_RE_CAPITAL_PARTNERS_HOLDING": {
        "name": "Unicorn Re Capital Partners Holding Co, SL",
        "type": CorporateTypeEnum.VEICULO_INTERNACIONAL,
        "keywords": ["unicorn re", "unicorn re capital", "holding co sl"],
        "jurisdicao": "Espanha / Internacional",
        "tags": ["holding-internacional", "veiculo-re", "spark-group"]
    },
    "SPARKWAVE_ENERGY_HOLDING_SA": {
        "name": "Sparkwave Energy Holding, S.A.",
        "type": CorporateTypeEnum.HOLDING_SOCIETARIA,
        "keywords": ["sparkwave", "sparkwave energy", "energy holding"],
        "tags": ["energia", "holding-setorial", "spark-group"]
    },
    "SPARK_ENERGY_ASSETS_SA": {
        "name": "Spark Energy Assets, S.A.",
        "type": CorporateTypeEnum.SOCIEDADE_ANONIMA_SA,
        "keywords": ["spark energy", "spark energy assets", "energy assets"],
        "tags": ["ativos-energia", "sociedade-operacional", "spark-group"]
    },
    "ZELIJE_CAPITAL_PARTNERS": {
        "name": "Zelije Capital Partners, Lda.",
        "type": CorporateTypeEnum.SOCIEDADE_COMERCIAL_LDA,
        "keywords": ["zelije", "zelije capital", "zelije capital partners"],
        "tags": ["capital-partners", "veiculo-participacoes", "spark-group"]
    },
    "NOMAD_PARTNERS_LDA": {
        "name": "Nomad Partners, Lda.",
        "type": CorporateTypeEnum.SOCIEDADE_COMERCIAL_LDA,
        "keywords": ["nomad partners", "nomad"],
        "tags": ["sociedade-comercial", "gestao", "spark-group"]
    }
}


class HeuristicCorporateClassifier:
    """Classificador Heuristico e Dicionario para Entidades Societarias e Fundos."""

    def __init__(self, dictionary: Dict[str, Dict[str, Any]] = CORPORATE_DICTIONARY):
        self.dict = dictionary

    def classify_text(self, filename: str, content: str = "") -> Tuple[Optional[str], CorporateTypeEnum, float, List[str]]:
        norm_fn = filename.replace("_", " ").replace("-", " ").lower()
        norm_content = content.replace("_", " ").replace("-", " ").lower()
        combined_text = f"{norm_fn} {norm_content}"
        best_entity_id = None
        best_score = 0.0
        best_type = CorporateTypeEnum.OUTRO_ENTE
        matched_kws = []

        for entity_id, meta in self.dict.items():
            matches = []
            for kw in meta["keywords"]:
                norm_kw = kw.lower()
                if norm_kw in combined_text:
                    matches.append(kw)

            if matches:
                # Score ponderado: matches de keywords e mencao no filename
                score = len(matches) / len(meta["keywords"])
                if any(kw.lower() in norm_fn for kw in meta["keywords"]):
                    score += 0.5

                score = min(1.0, score)

                if score > best_score:
                    best_score = score
                    best_entity_id = entity_id
                    best_type = meta["type"]
                    matched_kws = matches

        if best_score < 0.2:
            return None, CorporateTypeEnum.OUTRO_ENTE, 0.0, []

        return best_entity_id, best_type, round(best_score, 2), matched_kws

    def extract_nif(self, text: str) -> Optional[str]:
        # Regex para NIF portugues de pessoa coletiva (5xx xxx xxx)
        match = re.search(r'\b(5\d{8})\b', text)
        return match.group(1) if match else None

    def build_entity_model(self, entity_id: str, evidence_count: int = 1, sha256_primary: Optional[str] = None) -> CorporateEntity:
        meta = self.dict.get(entity_id, {})
        return CorporateEntity(
            entity_id=entity_id,
            name=meta.get("name", entity_id),
            corporate_type=meta.get("type", CorporateTypeEnum.OUTRO_ENTE),
            nif_nipc=meta.get("nif"),
            registro_cmvm=meta.get("registro_cmvm"),
            jurisdicao=meta.get("jurisdicao", "Portugal"),
            evidence_count=evidence_count,
            sha256_primary=sha256_primary,
            support_level=SupportLevelEnum.DOCUMENTADO,
            tags=meta.get("tags", ["spark-group"])
        )
