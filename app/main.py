"""
ScanFlow AI – Hauptverarbeitungs-Pipeline.

Ablauf einer Datei:
  1. OCR (Texterkennung)
  2. KI-Analyse (Datum, Kategorie, Titel)
  3. Bild → PDF konvertieren (falls nötig)
  4. Dateiname generieren
  5. Datei umbenennen und verschieben
"""

from pathlib import Path

from PIL import Image

from app.ocr import extract_text
from app.ai import analyze_document
from app.rename import build_filename, move_to_output
from app.utils import logger, log_result, log_error

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def _convert_to_pdf(image_path: Path) -> Path:
    """Konvertiert ein Bild in ein echtes PDF. Gibt den PDF-Pfad zurück."""
    pdf_path = image_path.with_suffix(".pdf")
    img = Image.open(image_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(pdf_path, "PDF", resolution=200.0)
    img.close()

    # Original-Bild löschen, da wir jetzt das PDF haben
    try:
        image_path.unlink()
    except OSError:
        pass

    logger.info("Bild → PDF konvertiert: %s → %s", image_path.name, pdf_path.name)
    return pdf_path


def process_file(file_path: Path) -> dict:
    """
    Verarbeitet eine einzelne Datei durch die komplette Pipeline.

    Gibt ein dict mit den Ergebnissen zurück (für das Webinterface).
    """
    file_path = Path(file_path)
    original_name = file_path.name

    logger.info("━━━ Verarbeitung gestartet: %s ━━━", original_name)

    # Schritt 1: OCR
    logger.info("[1/5] OCR läuft…")
    text = extract_text(file_path)

    if not text:
        log_error(original_name, "OCR lieferte keinen Text")
        return _result(original_name, status="Fehler: Kein Text erkannt")

    # Schritt 2: KI-Analyse
    logger.info("[2/5] KI-Analyse läuft…")
    analysis = analyze_document(text)

    # Schritt 3: Bild → PDF konvertieren
    if file_path.suffix.lower() in _IMAGE_EXTENSIONS:
        logger.info("[3/5] Bild wird in PDF konvertiert…")
        try:
            file_path = _convert_to_pdf(file_path)
        except Exception as exc:
            logger.error("PDF-Konvertierung fehlgeschlagen: %s", exc)
            return _result(original_name, status="Fehler: PDF-Konvertierung")
    else:
        logger.info("[3/5] Bereits PDF – keine Konvertierung nötig.")

    # Schritt 4: Dateiname generieren
    logger.info("[4/5] Dateiname wird generiert…")
    new_name = build_filename(analysis)

    # Schritt 5: Datei verschieben
    logger.info("[5/5] Datei wird verschoben…")
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
