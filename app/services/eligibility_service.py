"""Rule-based eligibility engine — evaluates partner qualification."""
import re
from typing import Tuple
from sqlalchemy.orm import Session
from app.models.partner_lead import PartnerLead, EligibilityDecision, LeadStatus
from app.repositories.partner_repository import PartnerRepository
from loguru import logger


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

MIN_TOTAL_EMPLOYEES = 30
MIN_SALES_EMPLOYEES = 5
MIN_TECHNICAL_EMPLOYEES = 5


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email or ""))


def _has_missing_data(lead: PartnerLead) -> bool:
    required = [lead.Email, lead.CompanyName, lead.TotalEmployees, lead.FoundingYear]
    return any(v is None for v in required)


def evaluate_eligibility(lead: PartnerLead) -> Tuple[EligibilityDecision, str]:
    if _has_missing_data(lead):
        return EligibilityDecision.INVESTIGATION_REQUIRED, "Missing required data fields — manual review needed"

    if not (lead.CompanyName or "").strip():
        return EligibilityDecision.REJECTED, "Company name is required"

    if not _is_valid_email(lead.Email):
        return EligibilityDecision.REJECTED, "Invalid email address format"

    total = lead.TotalEmployees or 0
    sales = lead.SalesEmployees or 0
    technical = lead.TechnicalEmployees or 0
    revenue = lead.AnnualRevenue or 0

    if total < MIN_TOTAL_EMPLOYEES:
        return EligibilityDecision.REJECTED, f"Insufficient total employees ({total} < {MIN_TOTAL_EMPLOYEES})"

    if sales < MIN_SALES_EMPLOYEES:
        return EligibilityDecision.REJECTED, f"Insufficient sales employees ({sales} < {MIN_SALES_EMPLOYEES})"

    if technical < MIN_TECHNICAL_EMPLOYEES:
        return EligibilityDecision.REJECTED, f"Insufficient technical employees ({technical} < {MIN_TECHNICAL_EMPLOYEES})"

    if revenue < 100_000:
        return EligibilityDecision.REJECTED, "Annual revenue below minimum threshold (EUR 100,000)"

    founding = lead.FoundingYear or 2024
    if founding >= 2022:
        return EligibilityDecision.INVESTIGATION_REQUIRED, f"Company established recently (founded {founding}) — further assessment required"

    return (
        EligibilityDecision.QUALIFIED,
        f"Qualifies: {total} employees, {sales} sales, {technical} technical staff, EUR {revenue:,.0f} revenue",
    )


class EligibilityService:
    @staticmethod
    def evaluate_eligibility(lead: PartnerLead) -> Tuple[EligibilityDecision, str]:
        return evaluate_eligibility(lead)

    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)

    def run_eligibility(self, lead_id: int) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        decision, reason = evaluate_eligibility(lead)
        lead.EligibilityDecision = decision
        lead.QualificationReason = reason

        if decision == EligibilityDecision.REJECTED:
            lead.LeadStatus = LeadStatus.REJECTED
        else:
            lead.LeadStatus = LeadStatus.ELIGIBILITY

        updated = self.partner_repo.update(lead)
        logger.info("Eligibility evaluated — lead={} decision={} reason={}", lead_id, decision, reason)
        return updated

    def run_batch_eligibility(self) -> dict:
        leads = self.partner_repo.get_pending_eligibility()
        results = {"qualified": 0, "rejected": 0, "investigation": 0, "total": len(leads)}

        for lead in leads:
            updated = self.run_eligibility(lead.ID)
            if updated.EligibilityDecision == EligibilityDecision.QUALIFIED:
                results["qualified"] += 1
            elif updated.EligibilityDecision == EligibilityDecision.REJECTED:
                results["rejected"] += 1
            else:
                results["investigation"] += 1

        logger.info("Batch eligibility complete: {}", results)
        return results
