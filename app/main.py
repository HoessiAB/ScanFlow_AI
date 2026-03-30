"""
ScanFlow AI – Hauptverarbeitungs-Pipeline.

Ablauf einer Datei:
  1. OCR (Texterkennung)
  2. KI-Analyse (Datum, Kategorie, Titel)
  3. Dateiname generieren
  4. Datei umbenennen und verschieben
"""

from pathlib import Path

from app.ocr import extract_text
from app.ai import analyze_document
from app.rename import build_filename, move_to_output
from app.utils import logger, log_result, log_error


def process_file(file_path: Path) -> dict:
    """
    Verarbeitet eine einzelne Datei durch die komplette Pipeline.

    Gibt ein dict mit den Ergebnissen zurück (für das Webinterface).
    """
    file_path = Path(file_path)
    original_name = file_path.name

    logger.info("━━━ Verarbeitung gestartet: %s ━━━", original_name)

    # Schritt 1: OCR
    logger.info("[1/4] OCR läuft…")
    text = extract_text(file_path)

    if not text:
        log_error(original_name, "OCR lieferte keinen Text")
        return _result(original_name, status="Fehler: Kein Text erkannt")

    # Schritt 2: KI-Analyse
    logger.info("[2/4] KI-Analyse läuft…")
    analysis = analyze_document(text)

    # Schritt 3: Dateiname generieren
    logger.info("[3/4] Dateiname wird generiert…")
    new_name = build_filename(analysis)

    # Schritt 4: Datei verschieben
    logger.info("[4/4] Datei wird verschoben…")
    nas_path = move_to_output(file_path, new_name)

    log_result(original_name, new_name, analysis.kategorie, "OK")
    logger.info("━━━ Fertig: %s → %s ━━━", original_name, new_name)

    return _result(
        original_name,
        new_name=new_name,
        kategorie=analysis.kategorie,
        datum=analysis.datum,
        titel=analysis.titel,
        status="OK",
    )


def _result(original: str, **kwargs) -> dict:
    """Baut ein Ergebnis-Dictionary."""
    return {
        "original": original,
        "new_name": kwargs.get("new_name", ""),
        "kategorie": kwargs.get("kategorie", ""),
        "datum": kwargs.get("datum", ""),
        "titel": kwargs.get("titel", ""),
        "status": kwargs.get("status", "Unbekannt"),
    }
