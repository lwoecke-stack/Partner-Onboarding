"""Repository layer — data access abstraction."""
from app.repositories.base_repository import BaseRepository
from app.repositories.partner_repository import PartnerRepository

__all__ = ["BaseRepository", "PartnerRepository"]
