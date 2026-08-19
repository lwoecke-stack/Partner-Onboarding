"""Database restore script — list, restore selected, or restore latest."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from app.config.logging_config import configure_logging
from app.services.backup_service import BackupService
from loguru import logger


def list_backups() -> None:
    svc = BackupService()
    backups = svc.list_backups()
    if not backups:
        print("No backups found.")
        return
    print(f"\nAvailable backups ({len(backups)}):")
    for i, b in enumerate(backups, 1):
        size_kb = b.stat().st_size // 1024
        print(f"  [{i:02d}] {b.name}  ({size_kb} KB)")


def restore_latest() -> None:
    svc = BackupService()
    latest = svc.get_latest_backup()
    if not latest:
        print("No backups available.")
        return
    confirm = input(f"Restore latest backup: {latest.name}? (yes/no): ").strip().lower()
    if confirm == "yes":
        ok = svc.restore_backup(latest)
        print("Restore successful." if ok else "Restore failed.")
    else:
        print("Restore cancelled.")


def restore_selected(index: int) -> None:
    svc = BackupService()
    backups = svc.list_backups()
    if index < 1 or index > len(backups):
        print(f"Invalid index. Choose 1-{len(backups)}")
        return
    chosen = backups[index - 1]
    confirm = input(f"Restore: {chosen.name}? (yes/no): ").strip().lower()
    if confirm == "yes":
        ok = svc.restore_backup(chosen)
        print("Restore successful." if ok else "Restore failed.")
    else:
        print("Restore cancelled.")


def main() -> None:
    configure_logging()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python restore_database.py list")
        print("  python restore_database.py latest")
        print("  python restore_database.py restore <index>")
        return

    cmd = sys.argv[1].lower()
    if cmd == "list":
        list_backups()
    elif cmd == "latest":
        restore_latest()
    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("Provide backup index: python restore_database.py restore <index>")
            return
        restore_selected(int(sys.argv[2]))
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
