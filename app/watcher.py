"""
ScanFlow AI – Datei-Watcher.

Überwacht den Inbox-Ordner und verarbeitet neue Dateien automatisch.
"""

import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from app.config import SCAN_INBOX
from app.utils import logger, is_allowed_file, ensure_dirs
from app.main import process_file


class ScanHandler(FileSystemEventHandler):
    """Reagiert auf neue Dateien im Inbox-Ordner."""

    def __init__(self) -> None:
        super().__init__()
        # Dateien, die von der Pipeline erzeugt werden (z.B. PNG→PDF),
        # sollen nicht nochmal verarbeitet werden.
        self._processing: set[str] = set()

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not is_allowed_file(file_path):
            logger.info("Übersprungen (falscher Typ): %s", file_path.name)
            return

        # Von der Pipeline erzeugte PDF ignorieren (z.B. nach PNG→PDF)
        stem = file_path.stem
        if stem in self._processing:
            logger.info("Übersprungen (Pipeline-intern): %s", file_path.name)
            self._processing.discard(stem)
            return

        # Warten, bis die Datei fertig geschrieben ist:
        # Dateigröße muss sich 3× hintereinander nicht mehr ändern.
        _wait_until_stable(file_path)

        if not file_path.exists():
            return

        # Stem merken, damit die konvertierte PDF nicht nochmal getriggert wird
        self._processing.add(file_path.stem)

        logger.info("Neue Datei erkannt: %s", file_path.name)
        try:
            process_file(file_path)
        except Exception as exc:
            logger.error("Verarbeitung fehlgeschlagen: %s – %s",
                         file_path.name, exc)
        finally:
            self._processing.discard(file_path.stem)


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

    logger.info("Watcher gestartet – überwache: %s", SCAN_INBOX)

    handler = ScanHandler()
    observer = Observer()
    observer.schedule(handler, str(SCAN_INBOX), recursive=False)
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
