# NAS einbinden (CIFS/SMB)

ScanFlow AI speichert die verarbeiteten Dokumente auf einem NAS
(Network Attached Storage). Die Verbindung erfolgt über CIFS/SMB.

---

## 1. Mountpoint erstellen

```bash
sudo mkdir -p /mnt/nas_scans
```

---

## 2. Credentials-Datei erstellen

Die Zugangsdaten für das NAS werden sicher in einer Datei gespeichert:

```bash
sudo nano /etc/nas-credentials
```

Inhalt (eigene Werte eintragen):

```
username=DEIN_NAS_BENUTZER
password=DEIN_NAS_PASSWORT
domain=WORKGROUP
```

Berechtigungen setzen (nur root darf lesen):

```bash
sudo chmod 600 /etc/nas-credentials
```

---

## 3. Manuell testen

Erst manuell mounten, um zu prüfen, ob die Verbindung funktioniert:

```bash
sudo mount -t cifs \
    //NAS-IP/Freigabe/Scans \
    /mnt/nas_scans \
    -o credentials=/etc/nas-credentials,uid=1000,gid=1000,file_mode=0664,dir_mode=0775
```

Ersetze:
- `NAS-IP` → IP-Adresse deines NAS (z. B. `192.168.1.100`)
- `Freigabe/Scans` → Pfad zur Freigabe auf dem NAS

Prüfen:

```bash
ls /mnt/nas_scans
touch /mnt/nas_scans/testfile && rm /mnt/nas_scans/testfile
```

Wenn `touch` ohne Fehler funktioniert, ist alles korrekt.

---

## 4. Automatisch mounten (fstab)

```bash
sudo nano /etc/fstab
```

Folgende Zeile am Ende hinzufügen (eine Zeile!):

```
//NAS-IP/Freigabe/Scans  /mnt/nas_scans  cifs  credentials=/etc/nas-credentials,uid=1000,gid=1000,file_mode=0664,dir_mode=0775,_netdev,nofail  0  0
```

### Erklärung der Optionen:

| Option | Bedeutung |
|--------|-----------|
| `credentials=...` | Datei mit Zugangsdaten |
| `uid=1000` | Dateien gehören Benutzer 1000 (scanflow) |
| `gid=1000` | Dateien gehören Gruppe 1000 |
| `file_mode=0664` | Dateiberechtigungen |
| `dir_mode=0775` | Ordnerberechtigungen |
| `_netdev` | Warten auf Netzwerk vor dem Mounten |
| `nofail` | System bootet auch wenn NAS offline ist |

### fstab testen (ohne Neustart):

```bash
sudo mount -a
```

Prüfen:

```bash
df -h | grep nas_scans
```

---

## 5. Nach Neustart prüfen

```bash
sudo reboot
```

Nach dem Neustart:

```bash
ls /mnt/nas_scans
```

Wenn der Ordner sichtbar ist, funktioniert alles.

---

## Fehlerbehebung

### mount: wrong fs type

```bash
sudo apt install -y cifs-utils
```

### Permission denied

- Prüfe Benutzername/Passwort in `/etc/nas-credentials`
- Prüfe Berechtigungen auf der NAS-Freigabe

### NAS nicht erreichbar nach Reboot

Die Option `_netdev` sollte das verhindern. Falls es trotzdem Probleme gibt:

```bash
sudo systemctl enable systemd-networkd-wait-online.service
```

---

> **Nächster Schritt:** [System Setup](system_setup.md)
