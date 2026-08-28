from __future__ import annotations

from backend.schemas.models import Claim, EstadoProbatorio, Gap, Severidade


class ValidadeAgent:
    """Procura saltos logicos, rotulos fortes e lacunas probatorias."""

    STRONG_LEGAL_WORDS = [
        "prova plena",
        "confissao extrajudicial",
        "confissão extrajudicial",
        "ilicita",
        "ilícita",
        "coacao",
        "coação",
        "desvio de fundos",
        "gestao ruinosa",
        "gestão ruinosa",
    ]

    def validate_claims(self, claims: list[Claim]) -> tuple[list[Claim], list[Gap]]:
        gaps: list[Gap] = []
        corrected: list[Claim] = []

        for claim in claims:
            lowered = claim.descricao.lower()
            risky = [word for word in self.STRONG_LEGAL_WORDS if word in lowered]
            if risky and claim.estado == EstadoProbatorio.FACTO_DOCUMENTADO:
                claim.estado = EstadoProbatorio.POR_VALIDAR
                claim.confianca_deterministica = min(claim.confianca_deterministica, 0.4)
                claim.notas_validacao.append(
                    "Rotulo juridico forte rebaixado automaticamente para POR_VALIDAR ate validacao humana."
                )

            if risky:
                gaps.append(
                    Gap(
                        gap_id=f"GAP-{claim.claim_id}",
                        severidade=Severidade.ALERTA,
                        tema=claim.tema,
                        descricao=f"Expressao juridica forte detectada: {', '.join(risky)}.",
                        acao_recomendada="Anexar fonte primaria, export integral, hash, cadeia de custodia e validacao por mandatario.",
                        evidencias_relacionadas=claim.suporte,
                    )
                )
            corrected.append(claim)

        if not claims:
            gaps.append(
                Gap(
                    gap_id="GAP-RAW-VAZIO-OU-SEM-TEXTO",
                    severidade=Severidade.CRITICO,
                    tema="ingestao",
                    descricao="Nao foram extraidos claims relevantes.",
                    acao_recomendada="Colocar ficheiros fonte em raw/ ou converter documentos digitalizados para texto pesquisavel.",
                )
            )

        return corrected, gaps
