"""
ScanFlow AI – KI-Analyse (OpenAI API).

Analysiert den OCR-Text und gibt Datum, Kategorie und Titel zurück.
Für mehrseitige Batches: gruppiert Seiten zu logischen Dokumenten.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI

from app.utils import logger, today_str

# ── Einzeldokument-Analyse ──────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Du bist ein Dokumenten-Analyse-Assistent. "
    "Antworte IMMER exakt im Format: DATUM|KATEGORIE|TITEL"
)

USER_PROMPT_TEMPLATE = """Analysiere dieses Dokument und gib zurück:

1. Datum im Format YYYY-MM-DD (wenn unbekannt → heutiges Datum: {today})
2. Kategorie (ein Wort, z. B. Steuer, Versicherung, Vertrag, Rechnung, Bank, Sonstiges)
3. Titel (max. 5 Wörter, keine Sonderzeichen)

Antwortformat:
DATUM|KATEGORIE|TITEL

Dokumenttext:
{text}"""

# ── Batch-Analyse (Dokumenten-Trennung) ─────────────────────────────────

BATCH_SYSTEM_PROMPT = (
    "Du bist ein Dokumenten-Analyse-Assistent. "
    "Du erhältst OCR-Texte von mehreren gescannten Seiten. "
    "Bestimme, welche Seiten zu welchem Dokument gehören, und analysiere jedes Dokument. "
    "Antworte NUR mit dem geforderten Format, keine Erklärungen."
)

BATCH_USER_PROMPT_TEMPLATE = """Du erhältst die OCR-Texte von {count} gescannten Seiten.

Aufgaben:
1. Bestimme, welche Seiten zusammen EIN Dokument bilden (inhaltlich zusammengehören)
2. Für jedes erkannte Dokument: Datum (YYYY-MM-DD), Kategorie (ein Wort), Titel (max. 5 Wörter)

Regeln:
- Vorder- und Rückseite desselben Blatts gehören zusammen
- Mehrseitige Briefe/Verträge/Rechnungen gehören zusammen
- Wenn du unsicher bist, ob Seiten zusammengehören → lieber als ein Dokument behandeln
- Leere Seiten (markiert als "leer") gehören zur vorherigen Seite
- Datum unbekannt → heutiges Datum: {today}
- Kategorien: Steuer, Versicherung, Vertrag, Rechnung, Bank, Arzt, Behoerde, Sonstiges

Antwortformat (eine Zeile pro Dokument, NUR dieses Format):
SEITEN|DATUM|KATEGORIE|TITEL

Beispiele:
1-3|2025-03-15|Steuer|Steuerbescheid 2024
4|2025-03-15|Rechnung|Amazon Bestellung
5-6|2025-03-10|Versicherung|KFZ Versicherungsschein

{pages_text}"""


@dataclass
class AnalysisResult:
    datum: str
    kategorie: str
    titel: str


@dataclass
class BatchDocument:
    """Ein erkanntes Dokument innerhalb eines Batch-Scans."""
    pages: list[int] = field(default_factory=list)
    datum: str = ""
    kategorie: str = ""
    titel: str = ""


def _get_client() -> tuple[OpenAI | None, str]:
    """Liefert einen frischen OpenAI-Client und den Modellnamen."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-nano")
    if not api_key:
        logger.error("Kein OPENAI_API_KEY konfiguriert – Fallback.")
        return None, model
    return OpenAI(api_key=api_key), model


# ── Einzeldokument ──────────────────────────────────────────────────────

def analyze_document(text: str) -> AnalysisResult:
    """
    Sendet den OCR-Text an die OpenAI API und parst die Antwort.

    Falls die API nicht erreichbar ist oder ein Fehler auftritt,
    werden sichere Fallback-Werte verwendet.
    """
    if not text.strip():
        logger.warning("Leerer Text – Fallback-Werte werden verwendet.")
        return _fallback()

    client, model = _get_client()
    if client is None:
        return _fallback()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                    today=today_str(), text=text
                )},
            ],
            temperature=0.1,
            max_completion_tokens=100,
        )
        answer = response.choices[0].message.content.strip()
        return _parse(answer)

    except Exception as exc:
        logger.error("OpenAI-Fehler: %s", exc)
        return _fallback()


# ── Batch-Analyse (mehrere Seiten → mehrere Dokumente) ──────────────────

def analyze_batch(page_texts: list[str]) -> list[BatchDocument]:
    """
    Analysiert mehrere gescannte Seiten und gruppiert sie zu Dokumenten.

    Die KI entscheidet anhand des Inhalts, welche Seiten zusammengehören.
    """
    total = len(page_texts)

    if not page_texts or all(not t.strip() for t in page_texts):
        logger.warning("Keine OCR-Texte im Batch – Fallback: ein Dokument.")
        return [_batch_fallback(total)]

    pages_text = ""
    for i, text in enumerate(page_texts, 1):
        label = text if text.strip() else "(leer / kein Text erkannt)"
        pages_text += f"\n--- SEITE {i} ---\n{label}\n"

    client, model = _get_client()
    if client is None:
        return [_batch_fallback(total)]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": BATCH_SYSTEM_PROMPT},
                {"role": "user", "content": BATCH_USER_PROMPT_TEMPLATE.format(
                    count=total,
                    today=today_str(),
                    pages_text=pages_text,
                )},
            ],
            temperature=0.1,
            max_completion_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        logger.info("KI-Batch-Antwort:\n%s", answer)
        return _parse_batch(answer, total)

    except Exception as exc:
        logger.error("OpenAI Batch-Fehler: %s", exc)
        return [_batch_fallback(total)]


# ── Parser ───────────────────────────────────────────────────────────────

def _parse(answer: str) -> AnalysisResult:
    """Parst die Pipe-getrennte KI-Antwort (Einzeldokument)."""
    try:
        parts = answer.split("|")
        if len(parts) != 3:
            raise ValueError(f"Unerwartetes Format: {answer}")

        datum = parts[0].strip()
        kategorie = parts[1].strip()
        titel = parts[2].strip()

        datetime.strptime(datum, "%Y-%m-%d")

        return AnalysisResult(datum=datum, kategorie=kategorie, titel=titel)

    except Exception as exc:
        logger.warning("Antwort konnte nicht geparst werden: %s (%s)", answer, exc)
        return _fallback()


def _parse_batch(answer: str, total_pages: int) -> list[BatchDocument]:
    """Parst die mehrzeilige Batch-Antwort der KI."""
    documents: list[BatchDocument] = []

    for line in answer.strip().splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) != 4:
            continue

        pages_str, datum, kategorie, titel = (p.strip() for p in parts)

        pages = _parse_pages(pages_str)
        if not pages:
            continue

        try:
            datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            datum = today_str()

        documents.append(BatchDocument(
            pages=pages, datum=datum,
            kategorie=kategorie, titel=titel,
        ))

    if not documents:
        logger.warning("Batch-Antwort nicht parsbar: %s", answer)
        return [_batch_fallback(total_pages)]

    assigned: set[int] = set()
    for doc in documents:
        assigned.update(doc.pages)

    missing = set(range(1, total_pages + 1)) - assigned
    if missing:
        logger.warning("Nicht zugeordnete Seiten: %s", sorted(missing))
        documents.append(BatchDocument(
            pages=sorted(missing),
            datum=today_str(),
            kategorie="Sonstiges",
            titel="Nicht_Zugeordnete_Seiten",
        ))

    return documents


def _parse_pages(pages_str: str) -> list[int]:
    """Parst Seitenangaben: '1-3' → [1,2,3], '4' → [4], '1,3,5' → [1,3,5]."""
    pages: list[int] = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                pages.extend(range(int(start), int(end) + 1))
            except ValueError:
                continue
        else:
            try:
                pages.append(int(part))
            except ValueError:
                continue
    return pages


# ── Fallbacks ────────────────────────────────────────────────────────────

def _fallback() -> AnalysisResult:
    """Sichere Standardwerte für Einzeldokument."""
    return AnalysisResult(
        datum=today_str(),
        kategorie="Sonstiges",
        titel="Unbekanntes_Dokument",
    )


def _batch_fallback(total_pages: int) -> BatchDocument:
    """Sichere Standardwerte für Batch (alle Seiten = ein Dokument)."""
    return BatchDocument(
        pages=list(range(1, total_pages + 1)),
        datum=today_str(),
        kategorie="Sonstiges",
        titel="Unbekanntes_Dokument",
    )
