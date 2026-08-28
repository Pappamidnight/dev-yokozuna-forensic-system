from __future__ import annotations

import re

from backend.schemas.models import Claim, GraphEdge, GraphNode


class GraphifyAgent:
    """Mantem mapa simples de entidades, fontes e relacoes relevantes."""

    MONEY_RE = re.compile(r"(?:€\s*)?\b\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?\s*(?:€|euros?)?\b", re.IGNORECASE)

    def build(self, claims: list[Claim]) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: dict[str, GraphNode] = {}
        edges: dict[str, GraphEdge] = {}

        for claim in claims:
            claim_node_id = self._node_id("claim", claim.claim_id)
            nodes[claim_node_id] = GraphNode(
                node_id=claim_node_id,
                kind="claim",
                label=claim.descricao[:160],
                source_ids=claim.suporte,
            )
            for person in claim.pessoas:
                person_id = self._node_id("person", person)
                nodes.setdefault(person_id, GraphNode(node_id=person_id, kind="person", label=person))
                self._edge(edges, person_id, claim_node_id, "mentioned_in", claim.suporte)
            for place in claim.locais:
                place_id = self._node_id("place", place)
                nodes.setdefault(place_id, GraphNode(node_id=place_id, kind="place", label=place))
                self._edge(edges, place_id, claim_node_id, "mentioned_in", claim.suporte)
            for value in claim.valores or self.MONEY_RE.findall(claim.descricao):
                value_id = self._node_id("value", value)
                nodes.setdefault(value_id, GraphNode(node_id=value_id, kind="value", label=value))
                self._edge(edges, value_id, claim_node_id, "mentioned_in", claim.suporte)

        return list(nodes.values()), list(edges.values())

    def _edge(self, edges: dict[str, GraphEdge], source: str, target: str, relation: str, evidence_ids: list[str]) -> None:
        edge_id = f"EDGE-{len(edges) + 1:06d}"
        key = f"{source}|{relation}|{target}"
        edges.setdefault(
            key,
            GraphEdge(edge_id=edge_id, source=source, target=target, relation=relation, evidence_ids=evidence_ids),
        )

    def _node_id(self, kind: str, label: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        return f"{kind}:{cleaned[:80]}"
