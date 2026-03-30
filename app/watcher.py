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

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not is_allowed_file(file_path):
            logger.info("Übersprungen (falscher Typ): %s", file_path.name)
            return

        # Kurz warten, bis die Datei fertig geschrieben ist
        time.sleep(2)

        logger.info("Neue Datei erkannt: %s", file_path.name)
        try:
            process_file(file_path)
        except Exception as exc:
            logger.error("Verarbeitung fehlgeschlagen: %s – %s",
                         file_path.name, exc)


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
