"""Seed script — creates schema, default users, and 500 dummy records."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.logging_config import configure_logging
from app.config.database import engine, SessionLocal
from app.models.base import Base
from app.models import PartnerLead, User, AuditTrail  # noqa: register models
from app.services.auth_service import seed_default_users
from app.services.backup_service import BackupService
from scripts.generate_dummy_data import generate_dummy_data
from loguru import logger


def seed(record_count: int = 500) -> None:
    configure_logging()
    logger.info("=== Seeding database ===")

    logger.info("Creating database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Schema created")

    with SessionLocal() as db:
        logger.info("Creating default users...")
        seed_default_users(db)

        existing = db.query(PartnerLead).count()
        if existing == 0:
            logger.info("Generating {} dummy partner records...", record_count)
            count = generate_dummy_data(db, record_count)
            logger.info("Generated {} records", count)
        else:
            logger.info("Database already has {} records — skipping seed", existing)

    logger.info("Creating initial backup...")
    backup_svc = BackupService()
    backup_path = backup_svc.create_backup("seed")
    logger.info("Backup created: {}", backup_path)
    logger.info("=== Seeding complete ===")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    seed(count)
