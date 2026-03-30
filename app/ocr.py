"""
ScanFlow AI – OCR-Modul (Tesseract).

Extrahiert Text aus Bildern und PDFs.
"""

import subprocess
import tempfile
from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path

from app.config import OCR_LANG, OCR_MAX_CHARS
from app.utils import logger

BATCH_MAX_CHARS_PER_PAGE = 800


def extract_text(file_path: Path) -> str:
    """
    Liest Text aus einer Bild- oder PDF-Datei.

    Bei PDFs wird jede Seite in ein Bild konvertiert und dann per OCR
    verarbeitet.  Der Gesamttext wird auf OCR_MAX_CHARS Zeichen begrenzt,
    damit die KI-Analyse schnell und günstig bleibt.
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    try:
        if suffix == ".pdf":
            text = _ocr_pdf(file_path)
        else:
            text = _ocr_image(file_path)
    except Exception as exc:
        logger.error("OCR fehlgeschlagen für %s: %s", file_path.name, exc)
        return ""

    text = text.strip()
    if len(text) > OCR_MAX_CHARS:
        text = text[:OCR_MAX_CHARS]

    logger.info("OCR fertig: %s → %d Zeichen", file_path.name, len(text))
    return text


def extract_text_per_page(page_paths: list[Path]) -> list[str]:
    """
    OCR für eine Liste einzelner Seitenbilder (Batch-Modus).

    Gibt eine Liste von Texten zurück – ein Eintrag pro Seite.
    Leere Seiten (< 20 Zeichen OCR-Text) werden als leerer String geliefert.
    """
    results: list[str] = []
    for path in page_paths:
        try:
            text = _ocr_image(path).strip()
            if len(text) < 20:
                logger.info("Seite %s: leer / kein Text", path.name)
                results.append("")
                continue
            if len(text) > BATCH_MAX_CHARS_PER_PAGE:
                text = text[:BATCH_MAX_CHARS_PER_PAGE]
            results.append(text)
            logger.info("OCR Seite %s: %d Zeichen", path.name, len(text))
        except Exception as exc:
            logger.error("OCR fehlgeschlagen für %s: %s", path.name, exc)
            results.append("")
    return results


def _ocr_image(path: Path) -> str:
    """OCR auf ein einzelnes Bild."""
    img = Image.open(path)
    return pytesseract.image_to_string(img, lang=OCR_LANG)


def _ocr_pdf(path: Path) -> str:
    """Konvertiert PDF-Seiten zu Bildern und führt OCR aus."""
    pages = convert_from_path(str(path), dpi=200)
    parts: list[str] = []
    for page in pages:
        parts.append(pytesseract.image_to_string(page, lang=OCR_LANG))
    return "\n".join(parts)
