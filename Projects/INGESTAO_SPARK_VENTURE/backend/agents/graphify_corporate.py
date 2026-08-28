from __future__ import annotations

import json
from typing import List, Dict, Any, Tuple
from backend.schemas.corporate_models import CorporateEntity, ShareholdingRelation


class GraphifyCorporateAgent:
    """Constroi o Grafo de Conhecimento e Relacoes Societarias (Nos e Arestas)."""

    def build_corporate_graph(
        self,
        entities: List[CorporateEntity],
        relations: List[ShareholdingRelation]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        
        nodes = []
        edges = []

        # 1. Criar Nos de Entidades
        for ent in entities:
            nodes.append({
                "node_id": ent.entity_id,
                "label": ent.name,
                "node_type": ent.corporate_type,
                "properties": {
                    "nif": ent.nif_nipc,
                    "registro_cmvm": ent.registro_cmvm,
                    "jurisdicao": ent.jurisdicao,
                    "evidence_count": ent.evidence_count,
                    "sha256": ent.sha256_primary,
                    "tags": ent.tags
                }
            })

        # 2. Criar Arestas de Relacionamento
        for rel in relations:
            edges.append({
                "edge_id": rel.relation_id,
                "source_id": rel.parent_entity,
                "target_id": rel.child_entity,
                "relation_type": rel.relation_type,
                "weight": rel.percentage or 1.0,
                "properties": {
                    "evidence_id": rel.evidence_id,
                    "sha256": rel.sha256
                }
            })

        return nodes, edges
