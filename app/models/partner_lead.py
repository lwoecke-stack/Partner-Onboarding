"""PartnerLead ORM model with all enumerations."""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    Enum as SAEnum, Index, CheckConstraint,
)
from sqlalchemy.orm import Mapped
from app.models.base import Base


class PartnershipType(str, enum.Enum):
    DISTRIBUTION_PARTNER = "Distribution Partner"
    SOLUTION_PARTNER = "Solution Partner"
    TECHNOLOGY_PARTNER = "Technology Partner"


class LeadStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    PARTNER_FINDER = "PARTNER_FINDER"
    ELIGIBILITY = "ELIGIBILITY"
    DAMEX = "DAMEX"
    COMPLIANCE = "COMPLIANCE"
    ZONAL_REVIEW = "ZONAL_REVIEW"
    PRE_APPROVED = "PRE_APPROVED"
    REJECTED = "REJECTED"


class EligibilityDecision(str, enum.Enum):
    QUALIFIED = "QUALIFIED"
    REJECTED = "REJECTED"
    INVESTIGATION_REQUIRED = "INVESTIGATION_REQUIRED"


class DamexStatus(str, enum.Enum):
    NO_RECORD_FOUND = "No Record Found"
    RED_FLAG_FOUND = "Red Flag Found"


class ComplianceStatus(str, enum.Enum):
    NO_MATCH = "No Match"
    NON_RELEVANT_MATCH = "Non-Relevant Match"
    MATCH = "Match"


class AIRecommendation(str, enum.Enum):
    APPROVE = "Approve"
    REJECT = "Reject"
    INVESTIGATE = "Investigate"


class PartnerLead(Base):
    __tablename__ = "PartnerLead"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(100), nullable=False)
    LastName = Column(String(100), nullable=False)
    Email = Column(String(255), nullable=False, unique=True)
    CompanyName = Column(String(255), nullable=False)
    Country = Column(String(100), nullable=False)
    City = Column(String(100), nullable=True)
    Street = Column(String(255), nullable=True)
    PostalCode = Column(String(20), nullable=True)
    AnnualRevenue = Column(Float, nullable=True)
    FoundingYear = Column(Integer, nullable=True)
    TotalEmployees = Column(Integer, nullable=True)
    SalesEmployees = Column(Integer, nullable=True)
    TechnicalEmployees = Column(Integer, nullable=True)

    PartnershipType = Column(
        SAEnum(PartnershipType, name="partnership_type_enum"),
        nullable=True,
    )
    LeadStatus = Column(
        SAEnum(LeadStatus, name="lead_status_enum"),
        default=LeadStatus.IN_PROGRESS,
        nullable=False,
    )
    EligibilityDecision = Column(
        SAEnum(EligibilityDecision, name="eligibility_decision_enum"),
        nullable=True,
    )
    DamexStatus = Column(
        SAEnum(DamexStatus, name="damex_status_enum"),
        nullable=True,
    )
    ComplianceStatus = Column(
        SAEnum(ComplianceStatus, name="compliance_status_enum"),
        nullable=True,
    )
    AIRecommendation = Column(
        SAEnum(AIRecommendation, name="ai_recommendation_enum"),
        nullable=True,
    )
    QualificationReason = Column(Text, nullable=True)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_partner_email", "Email"),
        Index("ix_partner_company", "CompanyName"),
        Index("ix_partner_country", "Country"),
        Index("ix_partner_status", "LeadStatus"),
        Index("ix_partner_eligibility", "EligibilityDecision"),
        CheckConstraint("TotalEmployees >= 0", name="ck_total_employees_positive"),
        CheckConstraint("AnnualRevenue >= 0", name="ck_revenue_positive"),
    )

    def __repr__(self) -> str:
        return f"<PartnerLead id={self.ID} company={self.CompanyName} status={self.LeadStatus}>"

    @property
    def full_name(self) -> str:
        return f"{self.FirstName} {self.LastName}"
