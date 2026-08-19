"""Database backup and restore service."""
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from app.config.settings import settings
from loguru import logger


class BackupService:
    def __init__(self) -> None:
        self.backup_dir = Path(settings.BACKUP_DIR)
        self.db_path = settings.get_database_path()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, reason: str = "manual") -> Path:
        if not self.db_path.exists():
            logger.warning("Database not found — skipping backup")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"PartnerOnboarding_{timestamp}.db"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(self.db_path, backup_path)
        logger.info("Backup created: {} (reason: {})", backup_path, reason)

        self._enforce_retention()
        return backup_path

    def list_backups(self) -> List[Path]:
        backups = sorted(self.backup_dir.glob("PartnerOnboarding_*.db"), reverse=True)
        return backups

    def get_latest_backup(self) -> Optional[Path]:
        backups = self.list_backups()
        return backups[0] if backups else None

    def restore_backup(self, backup_path: Path) -> bool:
        if not backup_path.exists():
            logger.error("Backup file not found: {}", backup_path)
            return False

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if self.db_path.exists():
            pre_restore = self.create_backup("pre-restore")
            logger.info("Pre-restore backup created: {}", pre_restore)

        shutil.copy2(backup_path, self.db_path)
        logger.info("Database restored from: {}", backup_path)
        return True

    def restore_latest(self) -> bool:
        latest = self.get_latest_backup()
        if not latest:
            logger.error("No backups available to restore")
            return False
        return self.restore_backup(latest)

    def _enforce_retention(self) -> None:
        backups = self.list_backups()
        if len(backups) > settings.MAX_BACKUPS:
            to_delete = backups[settings.MAX_BACKUPS:]
            for old in to_delete:
                old.unlink()
                logger.info("Old backup removed: {}", old)
