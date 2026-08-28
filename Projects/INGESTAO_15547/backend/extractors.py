from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from backend.io_utils import TEXT_EXTENSIONS, read_text_lossy
from backend.schemas.models import Claim, EstadoProbatorio, TextFragment, TimelineEvent


DATE_PATTERNS = [
    re.compile(r"\b(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>\d{2,4})(?:,\s*(?P<hour>\d{1,2}:\d{2}))?\b"),
    re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(?:[ T](?P<hour>\d{2}:\d{2}))?\b"),
]
VALUE_RE = re.compile(r"(?:€\s*)?\b\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?\s*(?:€|euros?)?\b", re.IGNORECASE)

THEMES = {
    "agua_servicos": ["agua", "água", "epal", "luz", "gas", "gás", "contador"],
    "imoveis": ["rua da palmeira", "31", "33", "sky", "heaven", "family", "penthouse"],
    "reservas_rendas": ["reserva", "reservas", "renda", "pagar", "pagamentos", "5 mil", "5000", "€"],
    "habitacao_nuno": ["hotel", "casa", "apartamento", "miudas", "miúdas", "filhas", "nuno"],
    "processual": ["15547", "3719", "citius", "processo", "prova", "mandatario", "mandatário"],
}

PEOPLE_HINTS = ["Nuno Duarte", "Nuno", "Filipe Delgado", "Filipe", "Renato"]
PLACE_HINTS = ["Rua da Palmeira", "Rua Cecílio de Sousa", "Sky", "Heaven", "Family", "Penthouse"]


@dataclass(frozen=True)
class ExtractionResult:
    fragments: list[TextFragment]
    claims: list[Claim]
    timeline: list[TimelineEvent]


def extract_from_file(path: Path, evidence_id: str) -> ExtractionResult:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return ExtractionResult([], [], [])

    text = read_text_lossy(path)
    lines = text.splitlines()
    fragments: list[TextFragment] = []
    claims: list[Claim] = []
    timeline: list[TimelineEvent] = []

    for index, line in enumerate(lines, start=1):
        clean = " ".join(line.strip().split())
        if not clean:
            continue
        if not _is_relevant(clean):
            continue

        fragment_id = f"{evidence_id}-L{index:06d}"
        fragment = TextFragment(
            fragment_id=fragment_id,
            evidence_id=evidence_id,
            source_path=str(path),
            line_start=index,
            line_end=index,
            text=clean,
        )
        fragments.append(fragment)

        dates = _extract_dates(clean)
        values = VALUE_RE.findall(clean)
        theme = _theme_for(clean)
        estado = _classify(clean, dates)
        support = [fragment_id]

        claim = Claim(
            claim_id=f"CLM-{fragment_id}",
            estado=estado,
            tema=theme,
            descricao=clean,
            suporte=support,
            pessoas=[p for p in PEOPLE_HINTS if p.lower() in clean.lower()],
            locais=[p for p in PLACE_HINTS if p.lower() in clean.lower()],
            valores=values,
            datas=dates,
            confianca_deterministica=_confidence(estado, clean),
            notas_validacao=_validation_notes(estado, clean),
        )
        claims.append(claim)

        if dates:
            first_date = dates[0]
            timeline.append(
                TimelineEvent(
                    event_id=f"EVT-{fragment_id}",
                    data=first_date,
                    estado=estado,
                    titulo=_title_for(theme, clean),
                    descricao=clean,
                    suporte=support,
                    ordenacao=_sort_key(first_date),
                )
            )

    timeline.sort(key=lambda event: event.ordenacao)
    return ExtractionResult(fragments, claims, timeline)


def _is_relevant(text: str) -> bool:
    lowered = text.lower()
    if any(term in lowered for terms in THEMES.values() for term in terms):
        return True
    return bool(_extract_dates(text) and len(text) >= 12)


def _theme_for(text: str) -> str:
    lowered = text.lower()
    scores = {
        theme: sum(1 for term in terms if term in lowered)
        for theme, terms in THEMES.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] else "geral"


def _classify(text: str, dates: list[str]) -> EstadoProbatorio:
    lowered = text.lower()
    allegation_markers = ["alega", "alegação", "diz que", "segundo", "tese", "pretende"]
    inference_markers = ["indicia", "sugere", "permite inferir", "aparenta", "parece"]
    defense_markers = ["defesa", "contrariar", "tese de defesa", "estrategia", "estratégia"]
    validation_markers = ["por validar", "validar", "confirmar", "sem suporte", "a apurar"]

    if any(marker in lowered for marker in validation_markers):
        return EstadoProbatorio.POR_VALIDAR
    if any(marker in lowered for marker in defense_markers):
        return EstadoProbatorio.TESE_DEFESA
    if any(marker in lowered for marker in inference_markers):
        return EstadoProbatorio.INFERENCIA
    if any(marker in lowered for marker in allegation_markers):
        return EstadoProbatorio.ALEGACAO
    if dates or _looks_like_chat_export(text):
        return EstadoProbatorio.FACTO_DOCUMENTADO
    return EstadoProbatorio.POR_VALIDAR


def _looks_like_chat_export(text: str) -> bool:
    return bool(re.match(r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}\s+-\s+", text))


def _extract_dates(text: str) -> list[str]:
    dates: list[str] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            day = match.group("day").zfill(2)
            month = match.group("month").zfill(2)
            year = match.group("year")
            if len(year) == 2:
                year = "20" + year
            hour = match.groupdict().get("hour") or "00:00"
            dates.append(f"{year}-{month}-{day} {hour}")
    return dates


def _sort_key(date_text: str) -> str:
    return date_text.replace("/", "-")


def _title_for(theme: str, text: str) -> str:
    labels = {
        "agua_servicos": "Servicos essenciais",
        "imoveis": "Imoveis / fracoes",
        "reservas_rendas": "Reservas / pagamentos",
        "habitacao_nuno": "Habitacao de Nuno",
        "processual": "Referencia processual",
    }
    return labels.get(theme, text[:80])


def _confidence(estado: EstadoProbatorio, text: str) -> float:
    if estado == EstadoProbatorio.FACTO_DOCUMENTADO:
        return 0.85 if _looks_like_chat_export(text) else 0.75
    if estado == EstadoProbatorio.POR_VALIDAR:
        return 0.35
    return 0.55


def _validation_notes(estado: EstadoProbatorio, text: str) -> list[str]:
    notes: list[str] = []
    lowered = text.lower()
    if "confiss" in lowered:
        notes.append("Qualificacao como confissao exige validacao juridica humana e contraditorio.")
    if estado == EstadoProbatorio.FACTO_DOCUMENTADO:
        notes.append("Facto documentado apenas quanto ao teor textual encontrado, nao quanto a verdade material externa.")
    if estado == EstadoProbatorio.POR_VALIDAR:
        notes.append("Requer fonte primaria, contexto integral ou confirmacao independente.")
    return notes
