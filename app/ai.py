"""
ScanFlow AI – KI-Analyse (OpenAI API).

Analysiert den OCR-Text und gibt Datum, Kategorie und Titel zurück.
"""

import os
from dataclasses import dataclass
from datetime import datetime

from openai import OpenAI

from app.utils import logger, today_str

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


@dataclass
class AnalysisResult:
    datum: str
    kategorie: str
    titel: str


def analyze_document(text: str) -> AnalysisResult:
    """
    Sendet den OCR-Text an die OpenAI API und parst die Antwort.

    Falls die API nicht erreichbar ist oder ein Fehler auftritt,
    werden sichere Fallback-Werte verwendet.
    """
    if not text.strip():
        logger.warning("Leerer Text – Fallback-Werte werden verwendet.")
        return _fallback()

    # Key und Modell bei jedem Aufruf frisch aus der Umgebung lesen,
    # damit Änderungen über das Webinterface sofort wirken.
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-nano")

    if not api_key:
        logger.error("Kein OPENAI_API_KEY konfiguriert – Fallback.")
        return _fallback()

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                    today=today_str(), text=text
                )},
            ],
            temperature=0.1,
            max_tokens=100,
        )
        answer = response.choices[0].message.content.strip()
        return _parse(answer)

    except Exception as exc:
        logger.error("OpenAI-Fehler: %s", exc)
        return _fallback()


def _parse(answer: str) -> AnalysisResult:
    """Parst die Pipe-getrennte KI-Antwort."""
    try:
        parts = answer.split("|")
        if len(parts) != 3:
            raise ValueError(f"Unerwartetes Format: {answer}")

        datum = parts[0].strip()
        kategorie = parts[1].strip()
        titel = parts[2].strip()

        # Datum validieren
        datetime.strptime(datum, "%Y-%m-%d")

        return AnalysisResult(datum=datum, kategorie=kategorie, titel=titel)

    except Exception as exc:
        logger.warning("Antwort konnte nicht geparst werden: %s (%s)", answer, exc)
        return _fallback()


def _fallback() -> AnalysisResult:
    """Gibt sichere Standardwerte zurück."""
    return AnalysisResult(
        datum=today_str(),
        kategorie="Sonstiges",
        titel="Unbekanntes_Dokument",
    )
