#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# ScanFlow AI – Scanner-Script (für scanbd)
# ═══════════════════════════════════════════════════════════════
# Wird von scanbd aufgerufen, wenn die Scan-Taste gedrückt wird.
#
# Funktionsweise:
#   1. Erstellt einen Batch-Ordner (batch_TIMESTAMP) in /scan/inbox
#   2. Scannt ALLE Seiten im Einzug (ADF Duplex, mehrseitig)
#   3. Legt .done-Marker an → Watcher startet die Verarbeitung
#
# Installation:
#   sudo cp scripts/scan.sh /etc/scanbd/scripts/scan.sh
#   sudo chmod +x /etc/scanbd/scripts/scan.sh
# ═══════════════════════════════════════════════════════════════

export TZ="Europe/Berlin"

INBOX="/scan/inbox"
BATCH_DIR="$INBOX/batch_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BATCH_DIR"

logger -t scanflow "Starte Batch-Scan → $BATCH_DIR"

scanimage \
    --device-name="fujitsu:fi-7030:5306" \
    --format=png \
    --resolution=200 \
    --mode=Color \
    --source="ADF Duplex" \
    --batch="$BATCH_DIR/page_%03d.png" \
    --batch-count=-1

PAGE_COUNT=$(ls "$BATCH_DIR"/*.png 2>/dev/null | wc -l)

if [ "$PAGE_COUNT" -eq 0 ]; then
    logger -t scanflow "Keine Seiten gescannt – Batch-Ordner wird gelöscht."
    rmdir "$BATCH_DIR" 2>/dev/null
    exit 0
fi

logger -t scanflow "Scan abgeschlossen: $PAGE_COUNT Seite(n) in $BATCH_DIR"

# Marker-Datei signalisiert dem Watcher: Batch komplett
touch "$BATCH_DIR/.done"

logger -t scanflow "Batch bereit zur Verarbeitung: $BATCH_DIR"
