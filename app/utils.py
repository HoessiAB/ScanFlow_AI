"""
ScanFlow AI – Hilfsfunktionen (Logging, Dateisystem).
"""

import logging
from datetime import datetime
from pathlib import Path

from app.config import LOG_FILE

# ── Logger einrichten ───────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("scanflow")
logger.setLevel(logging.INFO)

_fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s",
                         datefmt="%Y-%m-%d %H:%M:%S")

_fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)
logger.addHandler(_sh)


def log_result(filename: str, new_name: str, kategorie: str, status: str) -> None:
    """Schreibt ein Verarbeitungsergebnis ins Log."""
    logger.info("Datei=%s | Neu=%s | Kategorie=%s | Status=%s",
                filename, new_name, kategorie, status)


def log_error(filename: str, error: str) -> None:
    """Schreibt einen Fehler ins Log."""
    logger.error("Datei=%s | Fehler=%s", filename, error)


def ensure_dirs() -> None:
    """Stellt sicher, dass Inbox / Output existieren."""
    from app.config import SCAN_INBOX, SCAN_OUTPUT, NAS_PATH
    for p in (SCAN_INBOX, SCAN_OUTPUT, NAS_PATH):
        p.mkdir(parents=True, exist_ok=True)


def is_allowed_file(path: Path) -> bool:
    """Prüft, ob die Datei eine erlaubte Erweiterung hat."""
    from app.config import ALLOWED_EXTENSIONS
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def today_str() -> str:
    """Heutiges Datum als YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")
