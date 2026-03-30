# USB Passthrough – Scanner an VM durchreichen

Damit die VM auf den USB-Scanner zugreifen kann, muss das USB-Gerät
vom Proxmox-Host an die VM durchgereicht werden.

---

## 1. Scanner anschließen

Schließe den Scanner (z. B. Fujitsu fi-7030) per USB an den Proxmox-Host an.

---

## 2. USB-Gerät identifizieren

Auf dem **Proxmox-Host** (nicht in der VM!) per SSH einloggen:

```bash
ssh root@DEINE-PROXMOX-IP
```

USB-Geräte auflisten:

```bash
lsusb
```

Beispiel-Ausgabe:

```
Bus 002 Device 003: ID 04c5:132e Fujitsu, Ltd fi-7030
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

**Notiere dir:**
- Vendor ID: `04c5`
- Product ID: `132e`

---

## 3. USB-Gerät zur VM hinzufügen

### Option A: Über das Proxmox Webinterface

1. Gehe zu deiner VM `scanflow-ai`
2. Klicke auf **Hardware**
3. Klicke auf **Add** → **USB Device**
4. Wähle **Use USB Vendor/Device ID**
5. Wähle dein Scanner-Gerät aus der Liste
6. Klicke auf **Add**

### Option B: Über die Kommandozeile

```bash
qm set 100 -usb0 host=04c5:132e
```

(Ersetze `100` durch deine VM-ID und die IDs durch deine Werte.)

---

## 4. VM neustarten

```bash
qm reboot 100
```

---

## 5. In der VM prüfen

Logge dich in die VM ein und prüfe:

```bash
lsusb
```

Der Scanner sollte jetzt in der Liste erscheinen:

```
Bus 001 Device 002: ID 04c5:132e Fujitsu, Ltd fi-7030
```

---

## Fehlerbehebung

### Scanner wird nicht erkannt?

1. Prüfe, ob der Scanner am Host sichtbar ist: `lsusb` auf dem Proxmox-Host
2. Stelle sicher, dass die VM ausgeschaltet war beim Hinzufügen (oder starte neu)
3. Prüfe die USB-Version (USB 2.0 vs 3.0) – ggf. den Port wechseln

### Berechtigungsprobleme?

In der VM:

```bash
sudo usermod -aG scanner scanflow
sudo usermod -aG lp scanflow
```

Dann ausloggen und wieder einloggen.

---

> **Nächster Schritt:** [Scanner einrichten](scanner_setup.md)
