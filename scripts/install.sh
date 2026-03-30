#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# ScanFlow AI – Installations-Script
# ═══════════════════════════════════════════════════════════════
# Dieses Script installiert alle Abhängigkeiten und richtet
# das System komplett ein.
#
# Verwendung:
#   sudo bash scripts/install.sh
# ═══════════════════════════════════════════════════════════════

set -e

# ── Farben für die Ausgabe ──────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Root-Check ──────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Bitte als Root ausführen: sudo bash scripts/install.sh"
fi

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
info "Projektverzeichnis: $PROJECT_DIR"

# ── 1. System updaten ──────────────────────────────────────────
info "System wird aktualisiert…"
apt update && apt upgrade -y

# ── 2. Pakete installieren ─────────────────────────────────────
info "System-Pakete werden installiert…"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    tesseract-ocr \
    tesseract-ocr-deu \
    sane \
    sane-utils \
    cifs-utils \
    nginx \
    poppler-utils

# ── 3. Ordner erstellen ───────────────────────────────────────
info "Ordner werden erstellt…"
mkdir -p /scan/inbox
mkdir -p /scan/output
mkdir -p /mnt/nas_scans

# Berechtigungen setzen
chmod 777 /scan/inbox
chmod 777 /scan/output

# ── 4. Python Virtual Environment ─────────────────────────────
info "Python Virtual Environment wird erstellt…"
cd "$PROJECT_DIR"

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# ── 5. .env Datei erstellen ────────────────────────────────────
if [ ! -f "$PROJECT_DIR/.env" ]; then
    info ".env Datei wird aus Vorlage erstellt…"
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    warn "Bitte den OpenAI API-Key in .env eintragen!"
else
    info ".env existiert bereits – wird nicht überschrieben."
fi

# ── 6. Systemd Service einrichten ──────────────────────────────
info "Systemd Services werden eingerichtet…"

# Watcher Service
cat > /etc/systemd/system/scanflow-watcher.service << EOF
[Unit]
Description=ScanFlow AI – Datei-Watcher
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python -m app.watcher
Restart=always
RestartSec=5
Environment=PYTHONPATH=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Web Service
cat > /etc/systemd/system/scanflow-web.service << EOF
[Unit]
Description=ScanFlow AI – Webinterface
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 web.app:webapp
Restart=always
RestartSec=5
Environment=PYTHONPATH=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable scanflow-watcher.service
systemctl enable scanflow-web.service

# ── 7. Nginx einrichten ────────────────────────────────────────
info "Nginx wird konfiguriert…"

cat > /etc/nginx/sites-available/scanflow << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
}
EOF

# Default-Seite deaktivieren, ScanFlow aktivieren
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/scanflow /etc/nginx/sites-enabled/scanflow

nginx -t && systemctl restart nginx

# ── 8. Services starten ───────────────────────────────────────
info "Services werden gestartet…"
systemctl start scanflow-watcher.service
systemctl start scanflow-web.service

# ── Fertig ─────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN} ScanFlow AI wurde erfolgreich installiert!${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo " Webinterface:  http://$(hostname -I | awk '{print $1}')"
echo " Inbox-Ordner:  /scan/inbox"
echo " NAS-Mount:     /mnt/nas_scans"
echo ""
echo " Nächste Schritte:"
echo "   1. OpenAI API-Key in .env eintragen"
echo "   2. NAS einbinden (siehe docs/nas_mount.md)"
echo "   3. Scanner einrichten (siehe docs/scanner_setup.md)"
echo ""
echo "═══════════════════════════════════════════════════════════"
