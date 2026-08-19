"""
Siemens Partner Eligibility & Onboarding Automation System
Application entry point — startup, schema creation, seeding, and FastAPI launch.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.logging_config import configure_logging
from app.config.settings import settings
from app.config.database import engine, verify_database
from app.models.base import Base
from app.models import PartnerLead  # noqa: register all models
from app.api.routes import partners, workflow, reports


def _bootstrap_database() -> None:
    db_path = settings.get_database_path()
    is_new = not db_path.exists()

    settings.ensure_directories()

    if is_new:
        logger.info("New database — creating schema and seeding data...")
        Base.metadata.create_all(bind=engine)
        logger.info("Schema created")

        from app.config.database import SessionLocal
        from scripts.generate_dummy_data import generate_dummy_data
        from app.services.backup_service import BackupService

        with SessionLocal() as db:
            count = generate_dummy_data(db, settings.SEED_RECORDS)
            logger.info("Seeded {} partner records", count)

        backup_svc = BackupService()
        backup_svc.create_backup("initial-startup")
        logger.info("Initial backup created")
    else:
        logger.info("Existing database found — validating schema...")
        Base.metadata.create_all(bind=engine)

        from app.services.backup_service import BackupService
        backup_svc = BackupService()
        backup_svc.create_backup("startup")
        logger.info("Startup backup created")

    verify_database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("=" * 60)
    logger.info("Starting {} v{}", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Environment: {}", settings.APP_ENV)
    logger.info("=" * 60)

    _bootstrap_database()
    logger.info("Application ready")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Siemens Partner Eligibility & Onboarding Automation System API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(partners.router)
app.include_router(workflow.router)
app.include_router(reports.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "database": "sqlite"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
