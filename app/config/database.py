"""SQLAlchemy engine, session factory, and WAL/FK pragma setup."""
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings
from loguru import logger


def _apply_pragmas(dbapi_conn, _record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


def create_db_engine():
    db_path = settings.get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DATABASE_ECHO,
    )
    event.listen(engine, "connect", _apply_pragmas)
    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_database() -> bool:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode"))
            mode = result.scalar()
            logger.info("Database WAL mode: {}", mode)
            return True
    except Exception as exc:
        logger.error("Database verification failed: {}", exc)
        return False
