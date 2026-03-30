# Ubuntu Server 24.04 – Installation & Grundkonfiguration

---

## 1. Ubuntu installieren

Nach dem Start der VM erscheint der Ubuntu-Installer.

### Installer durchgehen:

1. **Sprache:** Deutsch oder Englisch
2. **Keyboard:** German (oder dein Layout)
3. **Installation type:** Ubuntu Server (minimized)
4. **Network:** DHCP (automatisch)
5. **Proxy:** leer lassen
6. **Mirror:** Standard lassen
7. **Storage:** Use an entire disk → Bestätigen
8. **Profil einrichten:**

| Feld | Beispiel |
|------|----------|
| Name | scanflow |
| Server-Name | scanflow-ai |
| Benutzername | scanflow |
| Passwort | (sicheres Passwort wählen) |

9. **SSH:** ✅ Install OpenSSH server (Haken setzen!)
10. **Featured Server Snaps:** Nichts auswählen
11. **Installation starten** und warten

Nach Abschluss: **Reboot Now**

---

## 2. Erster Login

Nach dem Neustart mit deinen Zugangsdaten einloggen.

---

## 3. SSH-Verbindung testen

Auf deinem PC (nicht in der VM):

```bash
ssh scanflow@IP-DER-VM
```

Die IP findest du mit:

```bash
ip addr show
```

---

## 4. System updaten

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 5. Alle benötigten Pakete installieren

```bash
sudo apt install -y \
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
```

### Was wird installiert?

| Paket | Zweck |
|-------|-------|
| python3 | Programmiersprache für ScanFlow AI |
| python3-pip | Python-Paketmanager |
| python3-venv | Virtuelle Umgebungen |
| git | Versionsverwaltung |
| tesseract-ocr | Texterkennung (OCR) |
| tesseract-ocr-deu | Deutsche Sprachdaten für OCR |
| sane / sane-utils | Scanner-Anbindung |
| cifs-utils | NAS-Verbindung (SMB/CIFS) |
| nginx | Webserver (Reverse Proxy) |
| poppler-utils | PDF-zu-Bild Konvertierung |

---

## 6. Neustart

```bash
sudo reboot
```

---

> **Nächster Schritt:** [USB Passthrough einrichten](usb_passthrough.md)
