from __future__ import annotations

import re
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class CorporateTypeEnum(str, Enum):
    SOCIEDADE_CAPITAL_RISCO = "SOCIEDADE_CAPITAL_RISCO"
    FUNDO_CMVM = "FUNDO_CMVM"
    HOLDING_SOCIETARIA = "HOLDING_SOCIETARIA"
    SOCIEDADE_INVESTIMENTO = "SOCIEDADE_INVESTIMENTO"
    SOCIEDADE_COMERCIAL_LDA = "SOCIEDADE_COMERCIAL_LDA"
    SOCIEDADE_ANONIMA_SA = "SOCIEDADE_ANONIMA_SA"
    VEICULO_INTERNACIONAL = "VEICULO_INTERNACIONAL"
    OUTRO_ENTE = "OUTRO_ENTE"


class SupportLevelEnum(str, Enum):
    DOCUMENTADO = "DOCUMENTADO"
    INDICIADO = "INDICIADO"
    NAO_INDICIADO = "NAO_INDICIADO"


class CorporateEntity(BaseModel):
    model_config = ConfigDict(extra="forbid", strip_whitespace=True, use_enum_values=True)

    entity_id: str = Field(..., description="Identificador unico da entidade societaria")
    name: str = Field(..., description="Denominacao social completa")
    corporate_type: CorporateTypeEnum = Field(..., description="Tipo societario formal")
    nif_nipc: Optional[str] = Field(None, description="Numero de Identificacao de Pessoa Coletiva (NIF/NIPC)")
    registro_cmvm: Optional[str] = Field(None, description="Codigo de registo oficial na CMVM se aplicavel")
    sede: Optional[str] = Field(None, description="Sede social declarada")
    capital_social: Optional[str] = Field(None, description="Capital social nominal")
    jurisdicao: str = Field(default="Portugal", description="Jurisdicao da constituicao")
    evidence_count: int = Field(default=0, ge=0)
    sha256_primary: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$")
    support_level: SupportLevelEnum = Field(default=SupportLevelEnum.DOCUMENTADO)
    tags: List[str] = Field(default_factory=list)


class CorporateEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strip_whitespace=True, use_enum_values=True)

    evidence_id: str
    filepath: str
    filename: str
    extension: str
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    classified_entity: Optional[str] = None
    classified_type: CorporateTypeEnum = CorporateTypeEnum.OUTRO_ENTE
    support_level: SupportLevelEnum = SupportLevelEnum.DOCUMENTADO
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    matched_keywords: List[str] = Field(default_factory=list)


class ShareholdingRelation(BaseModel):
    model_config = ConfigDict(extra="forbid", strip_whitespace=True, use_enum_values=True)

    relation_id: str
    parent_entity: str
    child_entity: str
    relation_type: str = Field(default="PARTICIPACAO_SOCIAL", description="Tipo de vinculo (PARTICIPACAO_SOCIAL, GESTAO_FUNDO, ADMINISTRACAO, CONTROLO)")
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    evidence_id: Optional[str] = None
    sha256: Optional[str] = None


class CorporateManifest(BaseModel):
    project_name: str = "INGESTAO_SPARK_VENTURE"
    generated_at: str
    total_evidences: int
    total_entities: int
    total_relations: int
    frozen_judge_score: int = 100
    status: str = "PASS"
    outputs: Dict[str, str] = Field(default_factory=dict)
