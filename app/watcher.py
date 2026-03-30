"""
ScanFlow AI – Datei-Watcher.

Überwacht den Inbox-Ordner und verarbeitet neue Dateien automatisch.

Zwei Modi:
  • Einzeldatei: Datei direkt in /scan/inbox → process_file()
  • Batch:       scanbd legt Ordner batch_TIMESTAMP/ mit .done-Marker an
                 → process_batch() (KI trennt Dokumente automatisch)
"""

import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from app.config import SCAN_INBOX
from app.utils import logger, is_allowed_file, ensure_dirs
from app.main import process_file, process_batch


class ScanHandler(FileSystemEventHandler):
    """Reagiert auf neue Dateien und Batch-Marker im Inbox-Ordner."""

    def __init__(self) -> None:
        super().__init__()
        self._processing: set[str] = set()

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # ── Batch-Modus: .done Marker in einem batch_*-Ordner ───────
        if file_path.name == ".done" and file_path.parent.name.startswith("batch_"):
            self._handle_batch(file_path.parent)
            return

        # ── Einzeldatei-Modus: nur Dateien direkt im Inbox ──────────
        if file_path.parent != SCAN_INBOX:
            return

        if not is_allowed_file(file_path):
            return

        stem = file_path.stem
        if stem in self._processing:
            logger.info("Übersprungen (Pipeline-intern): %s", file_path.name)
            self._processing.discard(stem)
            return

        _wait_until_stable(file_path)

        if not file_path.exists():
            return

        self._processing.add(file_path.stem)

        logger.info("Neue Datei erkannt: %s", file_path.name)
        try:
            process_file(file_path)
        except Exception as exc:
            logger.error("Verarbeitung fehlgeschlagen: %s – %s",
                         file_path.name, exc)
        finally:
            self._processing.discard(file_path.stem)

    def _handle_batch(self, batch_dir: Path) -> None:
        """Startet die Batch-Verarbeitung für einen fertig gescannten Stapel."""
        batch_name = batch_dir.name
        if batch_name in self._processing:
            return

        self._processing.add(batch_name)
        logger.info("━━━ Batch erkannt: %s ━━━", batch_name)

        try:
            process_batch(batch_dir)
        except Exception as exc:
            logger.error("Batch-Verarbeitung fehlgeschlagen: %s – %s",
                         batch_name, exc)
        finally:
            self._processing.discard(batch_name)


def _wait_until_stable(path: Path, interval: float = 2.0, checks: int = 3) -> None:
    """Wartet, bis die Dateigröße sich nicht mehr ändert."""
    stable = 0
    last_size = -1
    while stable < checks:
        time.sleep(interval)
        try:
            size = path.stat().st_size
        except OSError:
            return
        if size == last_size and size > 0:
            stable += 1
        else:
            stable = 0
            last_size = size


def start_watching() -> None:
    """Startet den Datei-Watcher (blockiert den Thread)."""
    ensure_dirs()

    logger.info("Watcher gestartet – überwache: %s (inkl. Unterordner)", SCAN_INBOX)

    handler = ScanHandler()
    observer = Observer()
    observer.schedule(handler, str(SCAN_INBOX), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Watcher wird gestoppt…")
        observer.stop()

    observer.join()
    logger.info("Watcher beendet.")


if __name__ == "__main__":
    start_watching()
