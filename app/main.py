"""
ScanFlow AI – Hauptverarbeitungs-Pipeline.

Einzeldatei-Modus:
  1. OCR → 2. KI-Analyse → 3. Bild→durchsuchbares PDF → 4. Umbenennen → 5. Verschieben

Batch-Modus (mehrere Dokumente auf einmal scannen):
  1. OCR aller Seiten → 2. KI gruppiert Seiten zu Dokumenten
  → 3. Durchsuchbare mehrseitige PDFs erzeugen → 4. Umbenennen → 5. Verschieben
"""

import io
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfWriter

from app.config import OCR_LANG
from app.ocr import extract_text, extract_text_per_page
from app.ai import (
    analyze_document, analyze_batch,
    AnalysisResult, BatchDocument,
)
from app.rename import build_filename, move_to_output
from app.utils import logger, log_result, log_error, today_str

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}

PDF_JPEG_QUALITY = 75


# ── Durchsuchbare PDF-Erzeugung (JPEG-komprimiert) ──────────────────────

def _image_to_searchable_pdf(image_path: Path) -> bytes:
    """
    Erzeugt aus einem Bild ein durchsuchbares, JPEG-komprimiertes PDF.

    Speichert das Bild als JPEG-Zwischendatei und ruft Tesseract direkt auf,
    damit die PDF JPEG-komprimierte Bilder enthält statt unkomprimierter Bitmaps.
    """
    img = Image.open(image_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_jpg = Path(tmp.name)

    try:
        img.save(tmp_jpg, format="JPEG", quality=PDF_JPEG_QUALITY, optimize=True)
        img.close()

        tmp_out = tmp_jpg.with_suffix("")
        subprocess.run(
            ["tesseract", str(tmp_jpg), str(tmp_out), "-l", OCR_LANG, "pdf"],
            check=True, capture_output=True,
        )

        pdf_path = tmp_out.with_suffix(".pdf")
        pdf_bytes = pdf_path.read_bytes()
    finally:
        tmp_jpg.unlink(missing_ok=True)
        tmp_out.with_suffix(".pdf").unlink(missing_ok=True)

    return pdf_bytes


def _convert_to_pdf(image_path: Path) -> Path:
    """Konvertiert ein Bild in ein durchsuchbares PDF. Gibt den PDF-Pfad zurück."""
    pdf_path = image_path.with_suffix(".pdf")
    pdf_bytes = _image_to_searchable_pdf(image_path)
    pdf_path.write_bytes(pdf_bytes)

    try:
        image_path.unlink()
    except OSError:
        pass

    logger.info("Bild → durchsuchbares PDF: %s → %s", image_path.name, pdf_path.name)
    return pdf_path


def process_file(file_path: Path) -> dict:
    """
    Verarbeitet eine einzelne Datei durch die komplette Pipeline.

    Gibt ein dict mit den Ergebnissen zurück (für das Webinterface).
    """
    file_path = Path(file_path)
    original_name = file_path.name

    logger.info("━━━ Verarbeitung gestartet: %s ━━━", original_name)

    logger.info("[1/5] OCR läuft…")
    text = extract_text(file_path)

    if not text:
        log_error(original_name, "OCR lieferte keinen Text")
        return _result(original_name, status="Fehler: Kein Text erkannt")

    logger.info("[2/5] KI-Analyse läuft…")
    analysis = analyze_document(text)

    if file_path.suffix.lower() in _IMAGE_EXTENSIONS:
        logger.info("[3/5] Bild wird in PDF konvertiert…")
        try:
            file_path = _convert_to_pdf(file_path)
        except Exception as exc:
            logger.error("PDF-Konvertierung fehlgeschlagen: %s", exc)
            return _result(original_name, status="Fehler: PDF-Konvertierung")
    else:
        logger.info("[3/5] Bereits PDF – keine Konvertierung nötig.")

    logger.info("[4/5] Dateiname wird generiert…")
    new_name = build_filename(analysis)

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


# ── Batch-Pipeline (mehrere Seiten → mehrere Dokumente) ─────────────────

def process_batch(batch_dir: Path) -> list[dict]:
    """
    Verarbeitet ein Batch-Verzeichnis mit gescannten Seiten.

    Die KI gruppiert die Seiten automatisch zu logischen Dokumenten.
    Jedes Dokument wird als mehrseitiges PDF gespeichert.
    """
    batch_dir = Path(batch_dir)

    pages = sorted(
        [p for p in batch_dir.iterdir()
         if p.suffix.lower() in _IMAGE_EXTENSIONS and not p.name.startswith(".")],
        key=lambda p: p.name,
    )

    if not pages:
        logger.warning("Batch leer: %s", batch_dir)
        return []

    total = len(pages)
    logger.info("━━━ Batch-Verarbeitung: %d Seiten in %s ━━━", total, batch_dir.name)

    # 1 – OCR aller Seiten
    logger.info("[1/4] OCR aller %d Seiten…", total)
    page_texts = extract_text_per_page(pages)

    # Leere Seiten herausfiltern (Duplex-Rückseiten ohne Inhalt)
    non_empty = [(i, t) for i, t in enumerate(page_texts) if t.strip()]
    logger.info("%d von %d Seiten enthalten Text.", len(non_empty), total)

    # 2 – KI-Analyse + Dokumenten-Trennung
    logger.info("[2/4] KI-Analyse und Dokumenten-Trennung…")
    if total == 1:
        text = page_texts[0] if page_texts[0].strip() else ""
        if text:
            analysis = analyze_document(text)
        else:
            analysis = AnalysisResult(
                datum=today_str(),
                kategorie="Sonstiges", titel="Unbekanntes_Dokument",
            )
        documents = [BatchDocument(
            pages=[1], datum=analysis.datum,
            kategorie=analysis.kategorie, titel=analysis.titel,
        )]
    else:
        documents = analyze_batch(page_texts)

    logger.info("KI hat %d Dokument(e) erkannt.", len(documents))

    # 3+4 – PDFs erzeugen, benennen, verschieben
    results: list[dict] = []
    for i, doc in enumerate(documents, 1):
        doc_pages = [pages[p - 1] for p in doc.pages if 1 <= p <= len(pages)]
        if not doc_pages:
            continue

        analysis = AnalysisResult(
            datum=doc.datum, kategorie=doc.kategorie, titel=doc.titel,
        )
        new_name = build_filename(analysis)
        pdf_path = batch_dir / new_name

        logger.info("[3/4] Dokument %d/%d: Seiten %s → %s",
                     i, len(documents), doc.pages, new_name)

        try:
            _merge_pages_to_pdf(doc_pages, pdf_path)
            logger.info("PDF erstellt: %s (%d Seiten)", new_name, len(doc_pages))
        except Exception as exc:
            logger.error("PDF-Erstellung fehlgeschlagen für Dok %d: %s", i, exc)
            continue

        logger.info("[4/4] Dokument %d wird verschoben…", i)
        move_to_output(pdf_path, new_name)

        log_result(f"Batch:{batch_dir.name}", new_name, doc.kategorie, "OK")
        results.append(_result(
            f"Batch:{batch_dir.name} (Seiten {doc.pages})",
            new_name=new_name,
            kategorie=doc.kategorie,
            datum=doc.datum,
            titel=doc.titel,
            status="OK",
        ))

    _cleanup_batch(batch_dir)
    logger.info("━━━ Batch fertig: %d Dokument(e) erstellt ━━━", len(results))
    return results


def _merge_pages_to_pdf(page_paths: list[Path], output_path: Path) -> None:
    """Fügt mehrere Seitenbilder zu einem durchsuchbaren mehrseitigen PDF zusammen."""
    writer = PdfWriter()
    try:
        for p in page_paths:
            pdf_bytes = _image_to_searchable_pdf(p)
            writer.append(io.BytesIO(pdf_bytes))

        with open(output_path, "wb") as f:
            writer.write(f)
    finally:
        writer.close()


def _cleanup_batch(batch_dir: Path) -> None:
    """Löscht den Batch-Ordner nach erfolgreicher Verarbeitung."""
    try:
        for f in batch_dir.iterdir():
            try:
                f.unlink()
            except OSError:
                pass
        batch_dir.rmdir()
        logger.info("Batch-Ordner gelöscht: %s", batch_dir.name)
    except OSError as exc:
        logger.warning("Batch-Ordner konnte nicht gelöscht werden: %s", exc)


# ── Hilfsfunktionen ─────────────────────────────────────────────────────

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
