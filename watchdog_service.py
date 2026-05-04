"""
watchdog_service.py
-------------------
Monitors a folder (local or SMB mount) for file changes and triggers
smart_ingest.py automatically — no manual re-runs needed.

Behavior:
  - Watches WATCH_PATH from .env recursively
  - Debounces rapid bursts (e.g. 20 files saved at once → waits 5s → one batch)
  - On CREATE / MODIFY  → calls smart_ingest.process_file()
  - On DELETE           → calls smart_ingest.delete_file()
  - On MOVE/RENAME      → deletes old path vectors, ingests new path
  - Skips unsupported extensions and temp/hidden files silently

Usage:
  python watchdog_service.py                       # watches WATCH_PATH from .env
  python watchdog_service.py "\\\\server\\share"   # watches a specific SMB path
"""

import os
import time
import threading
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent,
)

from smart_ingest import process_file, delete_file, SUPPORTED_EXTENSIONS, WATCH_PATH

# ── Config ────────────────────────────────────────────────────────────────────
DEBOUNCE_SECONDS = 5.0   # wait this long after last event before processing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(message)s",
)
log = logging.getLogger(__name__)


# ── Debounced event handler ───────────────────────────────────────────────────
class SmartFileHandler(FileSystemEventHandler):
    """
    Collects file system events and debounces them so that rapid saves
    (e.g. an app writing a file in multiple chunks) only trigger one ingest.
    """

    def __init__(self):
        self._pending: dict = {}   # filepath → (Timer, action)
        self._lock = threading.Lock()

    def _is_valid_file(self, filepath: str) -> bool:
        name = Path(filepath).name
        ext  = Path(filepath).suffix.lower()

        if name.startswith('.') or name.startswith('~$'):
            return False  # hidden files and Office temp files

        if ext not in SUPPORTED_EXTENSIONS:
            return False  # silently ignore unsupported types

        return True

    def _schedule(self, filepath: str, action: str):
        """Schedule processing after the debounce window."""
        if not self._is_valid_file(filepath):
            return

        with self._lock:
            # Cancel any pending timer for this file (reset debounce window)
            existing = self._pending.get(filepath)
            if existing:
                existing[0].cancel()

            timer = threading.Timer(
                DEBOUNCE_SECONDS,
                self._execute,
                args=(filepath, action),
            )
            self._pending[filepath] = (timer, action)
            timer.start()
            log.info(f"Queued ({action}) — debounce {DEBOUNCE_SECONDS}s: {filepath}")

    def _execute(self, filepath: str, action: str):
        """Run after debounce window expires."""
        with self._lock:
            self._pending.pop(filepath, None)

        if action == "delete":
            log.info(f"Processing DELETE: {filepath}")
            delete_file(filepath)

        else:  # create or modify
            if not os.path.exists(filepath):
                log.info(f"Skipping {action} — file no longer exists: {filepath}")
                return
            log.info(f"Processing {action.upper()}: {filepath}")
            process_file(filepath)

    # ── watchdog event hooks ──────────────────────────────────────────────────
    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            self._schedule(event.src_path, "create")

    def on_modified(self, event: FileModifiedEvent):
        if not event.is_directory:
            self._schedule(event.src_path, "modify")

    def on_deleted(self, event: FileDeletedEvent):
        if not event.is_directory:
            self._schedule(event.src_path, "delete")

    def on_moved(self, event: FileMovedEvent):
        if not event.is_directory:
            # Treat a rename/move as: delete old path, create new path
            self._schedule(event.src_path, "delete")
            self._schedule(event.dest_path, "create")


# ── Service entry point ───────────────────────────────────────────────────────
def start_watching(watch_path: str = WATCH_PATH):
    watch_path = str(Path(watch_path).resolve())

    if not os.path.exists(watch_path):
        log.error(f"Watch path does not exist: {watch_path}")
        log.error("Set WATCH_PATH in your .env file or pass the path as an argument.")
        return

    handler  = SmartFileHandler()
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=True)
    observer.start()

    log.info(f"=== Watching: {watch_path} ===")
    log.info(f"=== Debounce: {DEBOUNCE_SECONDS}s | Ctrl+C to stop ===")

    try:
        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Shutdown signal received — stopping watchdog...")
    finally:
        observer.stop()
        observer.join()
        log.info("Watchdog stopped.")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else WATCH_PATH
    start_watching(path)
