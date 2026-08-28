"""
Definicao dos 6 agentes canonicos e modelos operacionais.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class EvidenceLevel(str, Enum):
    INDICE = "INDICE"
    OFICIAL = "OFICIAL"
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


@dataclass(frozen=True)
class CanonicalAgentDefinition:
    folder_name: str
    agent_id: str
    weight: float
    evidence_level: EvidenceLevel
    description: str
    immutable_source: bool = True
    precedence_rank: int = 1


CANONICAL_AGENTS_MAP: Dict[str, CanonicalAgentDefinition] = {
    "00_Indice_E_MOCs": CanonicalAgentDefinition(
        folder_name="00_Indice_E_MOCs",
        agent_id="agente-indice-mocs",
        weight=0.70,
        evidence_level=EvidenceLevel.INDICE,
        description="Mapeamento de arvore, catalogacao e navegacao (MOC). Nao e prova material.",
        immutable_source=True,
        precedence_rank=1,
    ),
    "01_PDFs_Oficiais": CanonicalAgentDefinition(
        folder_name="01_PDFs_Oficiais",
        agent_id="agente-pdfs-oficiais",
        weight=1.00,
        evidence_level=EvidenceLevel.OFICIAL,
        description="Extracao de atos formais, sentencas e despachos com hash SHA-256 obrigatorio.",
        immutable_source=True,
        precedence_rank=2,
    ),
    "04_Processos_E_Pecas_Escritas": CanonicalAgentDefinition(
        folder_name="04_Processos_E_Pecas_Escritas",
        agent_id="agente-pecas",
        weight=0.98,
        evidence_level=EvidenceLevel.OFICIAL,
        description="Pecas processuais integrais, artigos do CPC e cadeia de prazos e notificacoes.",
        immutable_source=True,
        precedence_rank=3,
    ),
    "03_Contratos_E_Acordos": CanonicalAgentDefinition(
        folder_name="03_Contratos_E_Acordos",
        agent_id="agente-contratos",
        weight=0.95,
        evidence_level=EvidenceLevel.ALTA,
        description="Partes outorgantes, imoveis, clausulas resolutivas, valores e assinaturas.",
        immutable_source=True,
        precedence_rank=4,
    ),
    "05_Correspondencia_E_Comunicacoes": CanonicalAgentDefinition(
        folder_name="05_Correspondencia_E_Comunicacoes",
        agent_id="agente-correspondencia",
        weight=0.85,
        evidence_level=EvidenceLevel.MEDIA,
        description="Emails e cartas. Separacao estrita entre FACTO (com aviso) e ALEGACAO.",
        immutable_source=True,
        precedence_rank=5,
    ),
    "02_Minutas_E_Rascunhos": CanonicalAgentDefinition(
        folder_name="02_Minutas_E_Rascunhos",
        agent_id="agente-minutas",
        weight=0.25,
        evidence_level=EvidenceLevel.BAIXA,
        description="Rascunhos, notas e apontamentos. Nunca promovido a despacho judicial.",
        immutable_source=True,
        precedence_rank=6,
    ),
}

EXECUTION_ORDER: List[str] = [
    "00_Indice_E_MOCs",
    "01_PDFs_Oficiais",
    "04_Processos_E_Pecas_Escritas",
    "03_Contratos_E_Acordos",
    "05_Correspondencia_E_Comunicacoes",
    "02_Minutas_E_Rascunhos",
]
