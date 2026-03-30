# ScanFlow AI – Bedienung

---

## So funktioniert es

```
  Dokument einlegen
        ↓
  Scan-Button drücken
        ↓
    (automatisch)
        ↓
  Datei erscheint im NAS:
  YYYY-MM-DD_KATEGORIE_TITEL.pdf
```

**Das war's.** Kein Umbenennen, kein Sortieren, kein Nachdenken.

---

## Schritt für Schritt

### 1. Dokument einlegen

Lege das Dokument in den Scanner ein (Einzug oder Flachbett).

### 2. Scan-Button drücken

Drücke den Scan-Button am Scanner.

### 3. Fertig

Die Datei wird automatisch:
- gescannt
- per OCR gelesen
- von der KI analysiert
- umbenannt
- auf dem NAS gespeichert

### Ergebnis

Im NAS-Ordner erscheint:

```
2025-03-15_Steuer_Steuerbescheid.pdf
2025-03-15_Versicherung_KFZ_Versicherungsschein.pdf
2025-03-16_Rechnung_Amazon_Bestellung.pdf
```

---

## Webinterface

Öffne im Browser:

```
http://IP-DER-VM
```

### Dashboard
- Übersicht der letzten Scans
- Status: Inbox, NAS-Verbindung, API-Key

### Logs
- Zeigt alle Verarbeitungs-Logs an

### Einstellungen
- OpenAI API-Key ändern
- Modell wählen

### Testverarbeitung
- Auf dem Dashboard gibt es einen Button "Testverarbeitung starten"
- Verarbeitet alle Dateien in der Inbox sofort

---

## Manuell scannen (ohne Button)

Falls der Hardware-Button nicht eingerichtet ist:

```bash
scanimage --format=png --resolution=200 -o /scan/inbox/scan.png
```

Oder lege eine Datei manuell in den Inbox-Ordner:

```bash
cp mein_dokument.pdf /scan/inbox/
```

---

## Logs ansehen

### Im Webinterface
Klicke auf "Logs" in der Navigation.

### Per Terminal

```bash
tail -f /opt/scanflow-ai/log.txt
```

---

## Häufige Fragen

### Was passiert wenn das NAS nicht erreichbar ist?
Die Datei wird trotzdem in `/scan/output` gespeichert. Sobald das NAS
wieder erreichbar ist, kann sie manuell kopiert werden.

### Was passiert bei einem Fehler?
Der Fehler wird geloggt. Die Original-Datei bleibt in der Inbox erhalten
und kann erneut verarbeitet werden.

### Welche Dateiformate werden unterstützt?
PDF, PNG, JPG, JPEG, TIFF, TIF, BMP

### Kann ich die Kategorien anpassen?
Die Kategorien werden von der KI automatisch erkannt. Die häufigsten:
Steuer, Versicherung, Vertrag, Rechnung, Bank, Sonstiges

### Wie viel kostet die KI-Analyse?
Mit dem Modell `gpt-4o-mini` kostet ein Dokument ca. 0,001 € (weniger
als ein Zehntel Cent).
