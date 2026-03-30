"""
ScanFlow AI – Zentrale Konfiguration.

Alle Einstellungen werden aus Umgebungsvariablen / .env geladen.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── .env laden ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

# ── Pfade ───────────────────────────────────────────────────────────────
SCAN_INBOX = Path(os.getenv("SCAN_INBOX", "/scan/inbox"))
SCAN_OUTPUT = Path(os.getenv("SCAN_OUTPUT", "/scan/output"))
NAS_PATH = Path(os.getenv("NAS_PATH", "/mnt/nas_scans"))
LOG_FILE = BASE_DIR / "log.txt"

# ── OpenAI ──────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── OCR ─────────────────────────────────────────────────────────────────
OCR_LANG = os.getenv("OCR_LANG", "deu")
OCR_MAX_CHARS = int(os.getenv("OCR_MAX_CHARS", "1200"))

# ── Sonstiges ───────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
