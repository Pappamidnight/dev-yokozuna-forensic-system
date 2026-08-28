"""
Modelos Pydantic v2 para Atos Processuais e Cadeias Judiciais CPC.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
import re

PROCESS_REGEX = re.compile(r"^\d{1,6}/\d{2}\.\d[A-Z0-9]{2,8}$")


class AtoProcessualModel(BaseModel):
    filename: str
    path: str
    folder: str
    process_id: Optional[str] = None
    tipo_cpc: str = "DOCUMENTO_DIVERSO"
    suporte: str = "DOCUMENTADO"
    evidence_level: str = "OFICIAL"
    sha256: Optional[str] = None
    data_pratica: Optional[str] = None
    autor_ato: Optional[str] = None
    antecedente_obrigatorio: Optional[str] = None
    lacuna_detetada: bool = False
    artigo_cpc: Optional[str] = None

    @model_validator(mode="after")
    def validate_ato(self):
        if self.folder == "02_Minutas_E_Rascunhos":
            if self.tipo_cpc == "DESPACHO":
                self.tipo_cpc = "RASCUNHO"
            if self.suporte == "DOCUMENTADO":
                self.suporte = "INDICIADO"
            if self.evidence_level == "OFICIAL":
                self.evidence_level = "BAIXA"
        return self


class CadeiaProcessualModel(BaseModel):
    process_id: str
    total_atos: int = 0
    atos: List[AtoProcessualModel] = Field(default_factory=list)
    tem_citacao: bool = False
    tem_despacho: bool = False
    tem_sentenca: bool = False
    lacunas: List[str] = Field(default_factory=list)
    score_qualidade: float = 1.0
