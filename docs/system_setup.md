# ScanFlow AI – System Setup

Diese Anleitung beschreibt die Installation von ScanFlow AI
auf dem vorbereiteten Ubuntu Server.

---

## 1. Repository klonen

```bash
cd /opt
sudo git clone https://github.com/DEIN-USER/scanflow-ai.git
cd scanflow-ai
```

Oder manuell die Dateien auf den Server kopieren:

```bash
sudo mkdir -p /opt/scanflow-ai
# Dateien per SCP kopieren:
scp -r ./* scanflow@SERVER-IP:/opt/scanflow-ai/
```

---

## 2. Installations-Script ausführen

```bash
cd /opt/scanflow-ai
sudo bash scripts/install.sh
```

Das Script erledigt automatisch:
- System-Pakete installieren
- Python Virtual Environment erstellen
- Python-Abhängigkeiten installieren
- Ordner erstellen (`/scan/inbox`, `/scan/output`)
- `.env` Datei erstellen
- Systemd Services einrichten
- Nginx konfigurieren

---

## 3. OpenAI API-Key eintragen

```bash
sudo nano /opt/scanflow-ai/.env
```

Ändere die Zeile:

```
OPENAI_API_KEY=sk-DEIN-API-KEY-HIER
```

Trage deinen echten OpenAI API-Key ein.

> **Tipp:** Den API-Key kannst du auch über das Webinterface ändern
> (Einstellungen-Seite).

---

## 4. Pfade anpassen (optional)

Falls dein NAS unter einem anderen Pfad gemountet ist, passe die `.env` an:

```
NAS_PATH=/mnt/nas_scans
```

---

## 5. Services neustarten

```bash
sudo systemctl restart scanflow-watcher
sudo systemctl restart scanflow-web
```

---

## 6. Status prüfen

```bash
sudo systemctl status scanflow-watcher
sudo systemctl status scanflow-web
```

Beide Services sollten `active (running)` anzeigen.

---

## 7. Webinterface öffnen

Öffne im Browser:

```
http://IP-DER-VM
```

Du solltest das ScanFlow AI Dashboard sehen.

---

## 8. Testlauf

Lege eine Test-PDF oder ein Test-Bild in den Inbox-Ordner:

```bash
cp /tmp/testscan.png /scan/inbox/
```

Prüfe die Logs:

```bash
tail -f /opt/scanflow-ai/log.txt
```

Nach wenigen Sekunden sollte die Datei verarbeitet und umbenannt
auf dem NAS erscheinen.

---

## Befehle im Überblick

| Befehl | Beschreibung |
|--------|-------------|
| `sudo systemctl start scanflow-watcher` | Watcher starten |
| `sudo systemctl stop scanflow-watcher` | Watcher stoppen |
| `sudo systemctl restart scanflow-watcher` | Watcher neustarten |
| `sudo systemctl status scanflow-watcher` | Status prüfen |
| `sudo systemctl start scanflow-web` | Webinterface starten |
| `sudo systemctl stop scanflow-web` | Webinterface stoppen |
| `sudo journalctl -u scanflow-watcher -f` | Live-Logs anzeigen |

---

> **Nächster Schritt:** [Bedienung](usage.md)
