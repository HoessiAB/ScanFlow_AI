# Proxmox – VM erstellen

Diese Anleitung zeigt dir Schritt für Schritt, wie du eine neue VM in Proxmox erstellst.

---

## Voraussetzungen

- Proxmox VE ist installiert und erreichbar
- Ubuntu Server 24.04 LTS ISO wurde heruntergeladen

---

## 1. ISO hochladen

1. Öffne das Proxmox Webinterface: `https://DEINE-PROXMOX-IP:8006`
2. Klicke links auf deinen **Server-Knoten** (z. B. `pve`)
3. Gehe zu **local (pve)** → **ISO Images**
4. Klicke auf **Upload**
5. Wähle die Ubuntu Server 24.04 ISO aus
6. Warte bis der Upload abgeschlossen ist

---

## 2. VM erstellen

1. Klicke oben rechts auf **Create VM**

### Tab: General
| Einstellung | Wert |
|-------------|------|
| Node | dein Server |
| VM ID | automatisch (z. B. 100) |
| Name | `scanflow-ai` |

### Tab: OS
| Einstellung | Wert |
|-------------|------|
| ISO Image | ubuntu-24.04-live-server-amd64.iso |
| Type | Linux |
| Version | 6.x - 2.6 Kernel |

### Tab: System
| Einstellung | Wert |
|-------------|------|
| BIOS | Default (SeaBIOS) |
| SCSI Controller | VirtIO SCSI single |

Alles andere auf Standard lassen.

### Tab: Disks
| Einstellung | Wert |
|-------------|------|
| Bus/Device | SCSI |
| Disk size | **20 GB** |
| Storage | local-lvm |

### Tab: CPU
| Einstellung | Wert |
|-------------|------|
| Cores | **2** |
| Type | host |

### Tab: Memory
| Einstellung | Wert |
|-------------|------|
| Memory | **2048 MB** (2 GB) |

### Tab: Network
| Einstellung | Wert |
|-------------|------|
| Bridge | vmbr0 |
| Model | VirtIO |

### Tab: Confirm
- Prüfe alle Einstellungen
- Haken bei **Start after created** setzen
- Klicke auf **Finish**

---

## 3. VM starten

Die VM startet automatisch. Gehe zu **Console**, um die Ubuntu-Installation zu beginnen.

---

## Zusammenfassung

| Eigenschaft | Wert |
|-------------|------|
| Name | scanflow-ai |
| CPU | 2 Kerne |
| RAM | 2 GB |
| Disk | 20 GB |
| OS | Ubuntu Server 24.04 LTS |

> **Nächster Schritt:** [Linux installieren](install_linux.md)
