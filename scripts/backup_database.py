"""Manual database backup script."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.logging_config import configure_logging
from app.services.backup_service import BackupService
from loguru import logger


def main() -> None:
    configure_logging()
    reason = sys.argv[1] if len(sys.argv) > 1 else "manual"
    svc = BackupService()
    path = svc.create_backup(reason)
    if path:
        logger.info("Backup complete: {}", path)
        print(f"Backup created: {path}")
    else:
        logger.warning("No database found — backup skipped")
        print("No database to backup")


if __name__ == "__main__":
    main()
