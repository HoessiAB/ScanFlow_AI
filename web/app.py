"""
ScanFlow AI – Webinterface (Flask).

Bietet eine Übersicht der letzten Scans, Logs und Einstellungen.
"""

import os
import json
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import LOG_FILE, SCAN_INBOX, SCAN_OUTPUT, NAS_PATH, ENV_PATH
from app.utils import ensure_dirs, logger
from app.main import process_file

webapp = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)
webapp.secret_key = os.urandom(24)

# Verarbeitungs-History (im Speicher, wird beim Neustart geleert)
_history: list[dict] = []
MAX_HISTORY = 50


@webapp.route("/")
def index():
    """Hauptseite – Übersicht der letzten Scans."""
    return render_template("index.html", history=_history[:MAX_HISTORY])


@webapp.route("/logs")
def logs():
    """Zeigt die Log-Datei an (neueste oben)."""
    log_content = ""
    if LOG_FILE.exists():
        log_content = LOG_FILE.read_text(encoding="utf-8")
    lines = log_content.strip().split("\n")
    lines = list(reversed(lines[-500:]))
    log_content = "\n".join(lines)
    return render_template("logs.html", log_content=log_content)


@webapp.route("/api/logs")
def api_logs():
    """JSON-Endpoint für Live-Log-Updates."""
    log_content = ""
    if LOG_FILE.exists():
        log_content = LOG_FILE.read_text(encoding="utf-8")
    lines = log_content.strip().split("\n")
    lines = list(reversed(lines[-500:]))
    return jsonify({"logs": "\n".join(lines)})


@webapp.route("/settings", methods=["GET", "POST"])
def settings():
    """API-Key und Einstellungen verwalten."""
    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        model = request.form.get("model", "gpt-5.4-nano").strip()

        _update_env("OPENAI_API_KEY", api_key)
        _update_env("OPENAI_MODEL", model)

        flash("Einstellungen gespeichert. Neustart erforderlich.", "success")
        return redirect(url_for("settings"))

    current_key = os.getenv("OPENAI_API_KEY", "")
    current_model = os.getenv("OPENAI_MODEL", "gpt-5.4-nano")
    masked_key = _mask_key(current_key)

    return render_template("settings.html",
                           masked_key=masked_key,
                           current_model=current_model)


@webapp.route("/test", methods=["POST"])
def test_process():
    """Testverarbeitung: verarbeitet alle Dateien in der Inbox."""
    ensure_dirs()

    files = list(SCAN_INBOX.iterdir())
    processed = 0

    for f in files:
        if f.is_file() and f.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}:
            try:
                result = process_file(f)
                _history.insert(0, {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    **result,
                })
                processed += 1
            except Exception as exc:
                logger.error("Testverarbeitung fehlgeschlagen: %s – %s", f.name, exc)

    flash(f"{processed} Datei(en) verarbeitet.", "success")
    return redirect(url_for("index"))


@webapp.route("/api/status")
def api_status():
    """JSON-Endpoint für den Systemstatus."""
    return jsonify({
        "inbox_files": len(list(SCAN_INBOX.iterdir())) if SCAN_INBOX.exists() else 0,
        "output_files": len(list(SCAN_OUTPUT.iterdir())) if SCAN_OUTPUT.exists() else 0,
        "nas_mounted": NAS_PATH.exists() and NAS_PATH.is_mount(),
        "api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "history_count": len(_history),
    })


def _update_env(key: str, value: str) -> None:
    """Aktualisiert einen Wert in der .env Datei."""
    lines = []
    found = False

    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break

    if not found:
        lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ[key] = value


def _mask_key(key: str) -> str:
    """Maskiert einen API-Key für die Anzeige."""
    if not key or len(key) < 8:
        return "(nicht gesetzt)"
    return key[:4] + "•" * (len(key) - 8) + key[-4:]


def register_result(result: dict) -> None:
    """Wird vom Watcher aufgerufen, um Ergebnisse zu registrieren."""
    _history.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **result,
    })
    if len(_history) > MAX_HISTORY:
        _history.pop()


if __name__ == "__main__":
    webapp.run(host="0.0.0.0", port=5000, debug=True)
