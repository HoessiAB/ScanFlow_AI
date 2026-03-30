"""
ScanFlow AI – Dateiname-Generierung.

Baut den finalen Dateinamen nach dem Schema:
  YYYY-MM-DD_KATEGORIE_TITEL.pdf
"""

import re
import shutil
from pathlib import Path

from app.ai import AnalysisResult
from app.config import NAS_PATH, SCAN_OUTPUT
from app.utils import logger

# Umlaut-Ersetzungen
_UMLAUT_MAP = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    "ß": "ss",
})

# Verbotene Zeichen in Dateinamen
_FORBIDDEN = re.compile(r'[/\\:*?"<>|]')


def build_filename(result: AnalysisResult) -> str:
    """
    Erzeugt einen sauberen Dateinamen aus dem KI-Ergebnis.

    Regeln:
      - Umlaute werden ersetzt (ä→ae usw.)
      - Verbotene Zeichen werden entfernt
      - Leerzeichen werden durch _ ersetzt
    """
    raw = f"{result.datum}_{result.kategorie}_{result.titel}"

    raw = raw.translate(_UMLAUT_MAP)
    raw = _FORBIDDEN.sub("", raw)
    raw = raw.replace(" ", "_")
    raw = re.sub(r"_+", "_", raw)
    raw = raw.strip("_")

    return f"{raw}.pdf"


def move_to_output(source: Path, new_name: str) -> Path:
    """
    Kopiert die verarbeitete Datei in den Output-Ordner und auf das NAS.

    Gibt den finalen NAS-Pfad zurück.
    """
    SCAN_OUTPUT.mkdir(parents=True, exist_ok=True)
    NAS_PATH.mkdir(parents=True, exist_ok=True)

    output_path = SCAN_OUTPUT / new_name
    nas_path = NAS_PATH / new_name

    # Duplikat-Schutz: Zähler anhängen falls Name schon existiert
    output_path = _unique_path(output_path)
    nas_path = _unique_path(nas_path)

    try:
        shutil.copy2(source, output_path)
        logger.info("Kopiert nach Output: %s", output_path)
    except Exception as exc:
        logger.error("Fehler beim Kopieren nach Output: %s", exc)

    try:
        shutil.copy2(source, nas_path)
        logger.info("Kopiert nach NAS: %s", nas_path)
    except Exception as exc:
        logger.error("Fehler beim Kopieren nach NAS: %s", exc)

    # Originaldatei löschen
    try:
        source.unlink()
        logger.info("Original gelöscht: %s", source)
    except Exception as exc:
        logger.warning("Original konnte nicht gelöscht werden: %s", exc)

    return nas_path


def _unique_path(path: Path) -> Path:
    """Hängt (1), (2)… an, falls der Name bereits existiert."""
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        new_path = path.parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
