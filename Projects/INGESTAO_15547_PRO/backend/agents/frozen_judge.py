from __future__ import annotations

from backend.schemas.models import Claim, EstadoProbatorio, EvidenceFile, RouteDecision


class FrozenJudgeAgent:
    """Portao congelado: decide rotas com regras deterministicas e auditaveis."""

    SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".jsonl", ".log", ".rtf"}
    SUPPORTED_BINARY_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".docx", ".eml", ".msg"}

    def route_evidence(self, evidence: EvidenceFile) -> RouteDecision:
        ext = evidence.extension.lower()
        if evidence.size_bytes <= 0:
            return RouteDecision(
                item_id=evidence.evidence_id,
                item_type="evidence",
                route="quarantine/empty_file",
                accepted=False,
                reason="Ficheiro vazio nao pode ser ingerido como evidencia util.",
                required_actions=["Substituir por export/fonte original valida."],
            )
        if ext in self.SUPPORTED_TEXT_EXTENSIONS:
            return RouteDecision(
                item_id=evidence.evidence_id,
                item_type="evidence",
                route="extract/text",
                accepted=True,
                reason="Formato textual suportado para extracao deterministica.",
            )
        if ext in self.SUPPORTED_BINARY_EXTENSIONS:
            return RouteDecision(
                item_id=evidence.evidence_id,
                item_type="evidence",
                route="index/binary_requires_special_parser",
                accepted=True,
                reason="Formato binario indexado por hash; requer parser/OCR especializado para extracao textual completa.",
                required_actions=["Adicionar parser especializado ou converter para texto pesquisavel preservando RAW."],
            )
        return RouteDecision(
            item_id=evidence.evidence_id,
            item_type="evidence",
            route="quarantine/unsupported_extension",
            accepted=False,
            reason=f"Extensao nao suportada: {ext or '[sem extensao]'}.",
            required_actions=["Classificar manualmente o tipo de ficheiro ou converter copia de trabalho para formato suportado."],
        )

    def route_claim(self, claim: Claim) -> RouteDecision:
        if not claim.suporte:
            return RouteDecision(
                item_id=claim.claim_id,
                item_type="claim",
                route="quarantine/no_support",
                accepted=False,
                reason="Claim sem suporte nao entra na cronologia nem no indice principal.",
                required_actions=["Associar fragmento, documento, hash ou referencia verificavel."],
            )
        if claim.estado == EstadoProbatorio.FACTO_DOCUMENTADO:
            return RouteDecision(
                item_id=claim.claim_id,
                item_type="claim",
                route="outputs/documented_facts",
                accepted=True,
                reason="Entra como facto documentado apenas quanto ao teor da fonte.",
            )
        return RouteDecision(
            item_id=claim.claim_id,
            item_type="claim",
            route=f"outputs/{claim.estado.lower()}",
            accepted=True,
            reason="Entra separado do bloco de factos documentados.",
        )
