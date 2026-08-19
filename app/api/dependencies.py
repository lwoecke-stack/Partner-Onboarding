"""FastAPI dependency injection — DB session."""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.database import get_db

DBSession = Annotated[Session, Depends(get_db)]
