"""Application settings via Pydantic BaseSettings."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Siemens Partner Onboarding System"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///database/PartnerOnboarding.db"
    DATABASE_ECHO: bool = False

    # Security
    SECRET_KEY: str = "siemens-partner-automation-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_OPENAI_MAX_TOKENS: int = 2000
    AZURE_OPENAI_TEMPERATURE: float = 0.3

    # Paths
    LOG_FILE: str = "logs/application.log"
    BACKUP_DIR: str = "database/backups"
    EXPORT_DIR: str = "database/exports"
    REPORTS_DIR: str = "reports"
    DATABASE_DIR: str = "database"

    # Backup
    MAX_BACKUPS: int = 20

    # Seed
    SEED_RECORDS: int = 500

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Frontend
    STREAMLIT_PORT: int = 8501

    def get_database_path(self) -> Path:
        url = self.DATABASE_URL.replace("sqlite:///", "")
        return Path(url)

    def ensure_directories(self) -> None:
        for d in [self.BACKUP_DIR, self.EXPORT_DIR, self.REPORTS_DIR, self.DATABASE_DIR, "logs"]:
            Path(d).mkdir(parents=True, exist_ok=True)


settings = Settings()
