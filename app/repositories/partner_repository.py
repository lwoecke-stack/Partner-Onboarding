"""PartnerLead repository — all partner data access operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.partner_lead import PartnerLead, LeadStatus, EligibilityDecision
from app.repositories.base_repository import BaseRepository


class PartnerRepository(BaseRepository[PartnerLead]):
    def __init__(self, db: Session) -> None:
        super().__init__(PartnerLead, db)

    def get_by_id(self, entity_id: int) -> Optional[PartnerLead]:
        return self.db.query(PartnerLead).filter(PartnerLead.ID == entity_id).first()

    def get_by_email(self, email: str) -> Optional[PartnerLead]:
        return self.db.query(PartnerLead).filter(PartnerLead.Email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PartnerLead]:
        return self.db.query(PartnerLead).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(PartnerLead).count()

    def get_by_status(self, status: LeadStatus) -> List[PartnerLead]:
        return self.db.query(PartnerLead).filter(PartnerLead.LeadStatus == status).all()

    def get_by_eligibility(self, decision: EligibilityDecision) -> List[PartnerLead]:
        return self.db.query(PartnerLead).filter(PartnerLead.EligibilityDecision == decision).all()

    def get_by_country(self, country: str) -> List[PartnerLead]:
        return self.db.query(PartnerLead).filter(PartnerLead.Country == country).all()

    def search(self, query: str) -> List[PartnerLead]:
        term = f"%{query}%"
        return self.db.query(PartnerLead).filter(
            or_(
                PartnerLead.CompanyName.ilike(term),
                PartnerLead.FirstName.ilike(term),
                PartnerLead.LastName.ilike(term),
                PartnerLead.Email.ilike(term),
            )
        ).all()

    def get_pending_eligibility(self) -> List[PartnerLead]:
        return self.db.query(PartnerLead).filter(
            and_(
                PartnerLead.LeadStatus == LeadStatus.PARTNER_FINDER,
                PartnerLead.EligibilityDecision.is_(None),
            )
        ).all()

    def get_pending_damex(self) -> List[PartnerLead]:
        return self.db.query(PartnerLead).filter(
            and_(
                PartnerLead.LeadStatus == LeadStatus.ELIGIBILITY,
                PartnerLead.DamexStatus.is_(None),
            )
        ).all()

    def get_pending_compliance(self) -> List[PartnerLead]:
        return self.db.query(PartnerLead).filter(
            and_(
                PartnerLead.LeadStatus == LeadStatus.DAMEX,
                PartnerLead.ComplianceStatus.is_(None),
            )
        ).all()

    def get_status_summary(self) -> dict:
        from sqlalchemy import func
        results = (
            self.db.query(PartnerLead.LeadStatus, func.count(PartnerLead.ID))
            .group_by(PartnerLead.LeadStatus)
            .all()
        )
        return {str(status): count for status, count in results}

    def get_eligibility_summary(self) -> dict:
        from sqlalchemy import func
        results = (
            self.db.query(PartnerLead.EligibilityDecision, func.count(PartnerLead.ID))
            .filter(PartnerLead.EligibilityDecision.isnot(None))
            .group_by(PartnerLead.EligibilityDecision)
            .all()
        )
        return {str(decision): count for decision, count in results}

    def create(self, entity: PartnerLead) -> PartnerLead:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: PartnerLead) -> PartnerLead:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def bulk_create(self, entities: List[PartnerLead]) -> List[PartnerLead]:
        self.db.add_all(entities)
        self.db.commit()
        return entities
