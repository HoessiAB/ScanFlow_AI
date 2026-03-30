# Scanner einrichten (SANE)

SANE (Scanner Access Now Easy) ist das Standard-Framework für
Scanner unter Linux.

---

## 1. Scanner erkennen

```bash
sudo scanimage -L
```

Erwartete Ausgabe (Beispiel):

```
device `fujitsu:ScanSnap fi-7030:12345' is a FUJITSU fi-7030 scanner
```

Falls der Scanner **nicht** gefunden wird:

```bash
sudo sane-find-scanner
```

---

## 2. Testscan durchführen

Einen einfachen Scan als PNG speichern:

```bash
sudo scanimage --device-name="fujitsu:ScanSnap fi-7030:12345" \
    --format=png \
    --resolution=200 \
    --mode=Color \
    -o /tmp/testscan.png
```

Prüfen, ob die Datei erstellt wurde:

```bash
ls -la /tmp/testscan.png
```

---

## 3. Scanner-Berechtigungen

Damit ScanFlow AI ohne `sudo` scannen kann:

```bash
sudo usermod -aG scanner scanflow
sudo usermod -aG lp scanflow
```

Danach ausloggen und wieder einloggen:

```bash
exit
```

Dann erneut per SSH verbinden und testen:

```bash
scanimage -L
```

---

## 4. Scanner-Button (optional)

Viele Scanner haben einen physischen Scan-Button. Mit `scanbd` kann
dieser Button erkannt und ein Script ausgelöst werden.

### scanbd installieren

```bash
sudo apt install -y scanbd
```

### Button-Script erstellen

```bash
sudo nano /etc/scanbd/scripts/scan.sh
```

Inhalt:

```bash
#!/bin/bash
# ScanFlow AI – Button-Trigger
INBOX="/scan/inbox"
FILENAME="scan_$(date +%Y%m%d_%H%M%S).png"

scanimage \
    --format=png \
    --resolution=200 \
    --mode=Color \
    -o "$INBOX/$FILENAME"
```

Ausführbar machen:

```bash
sudo chmod +x /etc/scanbd/scripts/scan.sh
```

### scanbd konfigurieren

```bash
sudo nano /etc/scanbd/scanbd.conf
```

Den `action`-Block für deinen Scanner anpassen:

```
action scan {
    filter = "^scan.*"
    numerical-trigger {
        from-value = 1
        to-value = 0
    }
    desc = "Scan-Button gedrückt"
    script = "/etc/scanbd/scripts/scan.sh"
}
```

### scanbd starten

```bash
sudo systemctl enable scanbd
sudo systemctl start scanbd
```

---

## 5. Alternativer Ansatz (ohne scanbd)

Falls scanbd nicht funktioniert oder dein Scanner keinen Button hat,
kannst du Scans auch direkt in den Inbox-Ordner legen:

```bash
scanimage --format=png --resolution=200 -o /scan/inbox/mein_scan.png
```

Der ScanFlow AI Watcher erkennt die Datei automatisch und verarbeitet sie.

---

> **Nächster Schritt:** [NAS einbinden](nas_mount.md)
