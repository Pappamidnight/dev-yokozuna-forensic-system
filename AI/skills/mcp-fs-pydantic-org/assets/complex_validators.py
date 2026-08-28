"""
Validadores Complexos e Regras Cruzadas para Modelos Pydantic v2.
"""
from typing import Dict, Any, List


def validate_cross_rules(record: Dict[str, Any]) -> List[str]:
    """Verifica regras semanticas cruzadas sobre um registo de documento."""
    errors = []
    
    kind = record.get("kind", "")
    suporte = record.get("suporte", "")
    folder = record.get("folder", "")
    evidence_level = record.get("evidence_level", "")
    sha256 = record.get("sha256", "")
    
    # Regra 1: ALEGACAO nao pode ser DOCUMENTADO
    if kind == "ALEGACAO" and suporte == "DOCUMENTADO":
        errors.append("ALEGACAO nao pode ter suporte DOCUMENTADO.")
        
    # Regra 2: FACTO, DECISAO ou PROVA_FISICA nao podem ser NAO_INDICIADO
    if kind in ["FACTO", "DECISAO", "PROVA_FISICA"] and suporte == "NAO_INDICIADO":
        errors.append(f"{kind} nao pode ter suporte NAO_INDICIADO.")
        
    # Regra 3: 02_Minutas_E_Rascunhos nunca e prova OFICIAL nem DESPACHO
    if folder == "02_Minutas_E_Rascunhos":
        if evidence_level == "OFICIAL":
            errors.append("Minutas em 02_Minutas_E_Rascunhos nao podem ter evidence_level OFICIAL.")
        if suporte == "DOCUMENTADO":
            errors.append("Minutas em 02_Minutas_E_Rascunhos nao podem ter suporte DOCUMENTADO.")
            
    # Regra 4: 00_Indice_E_MOCs nunca e prova OFICIAL
    if folder == "00_Indice_E_MOCs" and evidence_level == "OFICIAL":
        errors.append("Indices em 00_Indice_E_MOCs nao podem ter evidence_level OFICIAL.")
        
    # Regra 5: DOCUMENTADO exige hash SHA-256 de 64 caracteres
    if suporte == "DOCUMENTADO" and (not sha256 or len(sha256) != 64):
        errors.append("Registo DOCUMENTADO exige hash sha256 valido de 64 caracteres.")
        
    return errors
