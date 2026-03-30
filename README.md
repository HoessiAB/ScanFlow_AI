# ScanFlow AI

**Automatische Dokumentenverarbeitung – vom Scanner direkt ins NAS.**

Dokument scannen → KI erkennt Inhalt → Datei wird automatisch umbenannt und gespeichert.

```
Ergebnis:  2025-03-15_Steuer_Steuerbescheid.pdf
```

---

## Was macht ScanFlow AI?

1. **Scan empfangen** – Datei aus dem Scanner-Eingang
2. **OCR** – Text per Tesseract erkennen
3. **KI-Analyse** – OpenAI bestimmt Datum, Kategorie und Titel
4. **Umbenennen** – Sauberer Dateiname nach Schema
5. **Speichern** – Automatisch auf dem NAS ablegen

**Zero manuelle Nacharbeit.**

---

## Projektstruktur

```
scanflow-ai/
├── app/                    # Python Backend
│   ├── main.py             # Verarbeitungs-Pipeline
│   ├── watcher.py          # Datei-Überwachung
│   ├── ocr.py              # Texterkennung (Tesseract)
│   ├── ai.py               # KI-Analyse (OpenAI)
│   ├── rename.py           # Dateiname-Generierung
│   ├── config.py           # Konfiguration
│   └── utils.py            # Hilfsfunktionen
├── web/                    # Webinterface
│   ├── app.py              # Flask-Anwendung
│   ├── templates/          # HTML-Templates
│   └── static/             # CSS, JavaScript
├── scripts/
│   ├── install.sh          # Installations-Script
│   └── start.sh            # Manueller Start
├── docs/                   # Anleitungen
│   ├── install_proxmox_vm.md
│   ├── install_linux.md
│   ├── usb_passthrough.md
│   ├── scanner_setup.md
│   ├── nas_mount.md
│   ├── system_setup.md
│   └── usage.md
├── .env.example            # Konfigurationsvorlage
├── requirements.txt        # Python-Abhängigkeiten
└── README.md
```

---

## Schnellstart

### 1. Repository klonen

```bash
cd /opt
sudo git clone https://github.com/DEIN-USER/scanflow-ai.git
cd scanflow-ai
```

### 2. Installieren

```bash
sudo bash scripts/install.sh
```

### 3. API-Key eintragen

```bash
sudo nano .env
```

### 4. Fertig

Webinterface: `http://IP-DER-VM`

---

## Systemanforderungen

| Komponente | Minimum |
|-----------|---------|
| Host | Proxmox VE |
| VM | Ubuntu Server 24.04 LTS |
| CPU | 2 Kerne |
| RAM | 2 GB |
| Disk | 20 GB |
| Scanner | USB-Dokumentenscanner (z. B. Fujitsu fi-7030) |
| NAS | SMB/CIFS-fähig |
| Internet | Für OpenAI API |

---

## Anleitungen

| Schritt | Dokument |
|---------|----------|
| 1. VM erstellen | [docs/install_proxmox_vm.md](docs/install_proxmox_vm.md) |
| 2. Linux installieren | [docs/install_linux.md](docs/install_linux.md) |
| 3. USB durchreichen | [docs/usb_passthrough.md](docs/usb_passthrough.md) |
| 4. Scanner einrichten | [docs/scanner_setup.md](docs/scanner_setup.md) |
| 5. NAS einbinden | [docs/nas_mount.md](docs/nas_mount.md) |
| 6. System Setup | [docs/system_setup.md](docs/system_setup.md) |
| 7. Bedienung | [docs/usage.md](docs/usage.md) |

---

## Technologie

| Komponente | Technologie |
|-----------|-------------|
| Scanner | SANE |
| OCR | Tesseract |
| KI | OpenAI API (gpt-4o-mini) |
| Backend | Python |
| Webinterface | Flask |
| Reverse Proxy | Nginx |
| NAS | CIFS/SMB |
| Autostart | systemd |

---

## Bedienung

```
1. Dokument einlegen
2. Scan-Button drücken
3. Fertig – Datei erscheint im NAS
```

---

## Lizenz

MIT License
