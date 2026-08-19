"""Compliance screening service — Compass-style simulation."""
from sqlalchemy.orm import Session
from app.models.partner_lead import PartnerLead, ComplianceStatus, LeadStatus
from app.repositories.partner_repository import PartnerRepository
from loguru import logger


def _simulate_compliance_check(lead: PartnerLead) -> tuple[ComplianceStatus, str, bool]:
    seed = hash(f"{lead.CompanyName}{lead.Country}") % 100

    if seed < 75:
        return ComplianceStatus.NO_MATCH, "No sanctions or watchlist matches found", False
    elif seed < 90:
        return ComplianceStatus.NON_RELEVANT_MATCH, "Non-relevant name match found — contextually cleared", False
    else:
        return ComplianceStatus.MATCH, "Potential sanctions/watchlist match — escalation required", True


class ComplianceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)

    def run_compliance_check(self, lead_id: int) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        compliance_result, details, requires_escalation = _simulate_compliance_check(lead)
        lead.ComplianceStatus = compliance_result

        if compliance_result == ComplianceStatus.MATCH:
            lead.LeadStatus = LeadStatus.REJECTED
            logger.warning("Compliance MATCH — escalation required for lead={}", lead_id)
        else:
            lead.LeadStatus = LeadStatus.COMPLIANCE

        updated = self.partner_repo.update(lead)
        logger.info("Compliance check — lead={} result={}", lead_id, compliance_result)
        return updated

    def run_batch_compliance(self) -> dict:
        leads = self.partner_repo.get_pending_compliance()
        results = {"no_match": 0, "non_relevant": 0, "match": 0, "total": len(leads)}

        for lead in leads:
            updated = self.run_compliance_check(lead.ID)
            if updated.ComplianceStatus == ComplianceStatus.NO_MATCH:
                results["no_match"] += 1
            elif updated.ComplianceStatus == ComplianceStatus.NON_RELEVANT_MATCH:
                results["non_relevant"] += 1
            else:
                results["match"] += 1

        logger.info("Batch Compliance complete: {}", results)
        return results
