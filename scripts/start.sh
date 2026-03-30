#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# ScanFlow AI – Manueller Start
# ═══════════════════════════════════════════════════════════════
# Startet Watcher und Webinterface manuell (ohne systemd).
# Nützlich für Tests und Debugging.
#
# Verwendung:
#   bash scripts/start.sh
# ═══════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Virtual Environment aktivieren
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Fehler: Virtual Environment nicht gefunden."
    echo "Bitte zuerst install.sh ausführen."
    exit 1
fi

export PYTHONPATH="$PROJECT_DIR"

echo "═══════════════════════════════════════════════════════════"
echo " ScanFlow AI wird gestartet…"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo " Watcher:       überwacht /scan/inbox"
echo " Webinterface:  http://localhost:5000"
echo " Beenden:       Strg + C"
echo ""

# Watcher im Hintergrund starten
python -m app.watcher &
WATCHER_PID=$!

# Webinterface starten (blockiert)
python web/app.py

# Aufräumen beim Beenden
kill $WATCHER_PID 2>/dev/null
echo "ScanFlow AI beendet."
