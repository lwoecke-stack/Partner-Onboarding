"""Partner workflow orchestration service."""
from sqlalchemy.orm import Session
from app.models.partner_lead import PartnerLead, LeadStatus, EligibilityDecision, DamexStatus, ComplianceStatus
from app.repositories.partner_repository import PartnerRepository
from app.services.eligibility_service import EligibilityService
from app.services.damex_service import DamexService
from app.services.compliance_service import ComplianceService
from loguru import logger

WORKFLOW_TRANSITIONS = {
    LeadStatus.IN_PROGRESS: LeadStatus.PARTNER_FINDER,
    LeadStatus.PARTNER_FINDER: LeadStatus.ELIGIBILITY,
    LeadStatus.ELIGIBILITY: LeadStatus.DAMEX,
    LeadStatus.DAMEX: LeadStatus.COMPLIANCE,
    LeadStatus.COMPLIANCE: LeadStatus.ZONAL_REVIEW,
    LeadStatus.ZONAL_REVIEW: LeadStatus.PRE_APPROVED,
}


class WorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)
        self.eligibility_svc = EligibilityService(db)
        self.damex_svc = DamexService(db)
        self.compliance_svc = ComplianceService(db)

    def advance_workflow(self, lead_id: int) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        if lead.LeadStatus == LeadStatus.REJECTED:
            raise ValueError("Cannot advance a REJECTED lead")
        if lead.LeadStatus == LeadStatus.PRE_APPROVED:
            raise ValueError("Lead is already PRE_APPROVED")

        old_status = lead.LeadStatus
        next_status = WORKFLOW_TRANSITIONS.get(lead.LeadStatus)

        if next_status is None:
            raise ValueError(f"No transition defined for status: {lead.LeadStatus}")

        if next_status == LeadStatus.ELIGIBILITY:
            lead = self.eligibility_svc.run_eligibility(lead_id)
            if lead.LeadStatus == LeadStatus.REJECTED:
                return lead
        elif next_status == LeadStatus.DAMEX:
            lead = self.damex_svc.run_damex_check(lead_id)
            if lead.LeadStatus == LeadStatus.REJECTED:
                return lead
        elif next_status == LeadStatus.COMPLIANCE:
            lead = self.compliance_svc.run_compliance_check(lead_id)
            if lead.LeadStatus == LeadStatus.REJECTED:
                return lead
        else:
            lead.LeadStatus = next_status
            self.partner_repo.update(lead)

        logger.info("Workflow advanced — lead={} {} → {}", lead_id, old_status, lead.LeadStatus)
        return lead

    def run_full_workflow(self, lead_id: int) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        terminal = {LeadStatus.REJECTED, LeadStatus.PRE_APPROVED}
        while lead.LeadStatus not in terminal:
            lead = self.advance_workflow(lead_id)

        logger.info("Full workflow complete — lead={} final_status={}", lead_id, lead.LeadStatus)
        return lead

    def reject_lead(self, lead_id: int, reason: str) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        lead.LeadStatus = LeadStatus.REJECTED
        lead.QualificationReason = reason
        updated = self.partner_repo.update(lead)

        logger.info("Lead rejected — lead={} reason={}", lead_id, reason)
        return updated

    def approve_lead(self, lead_id: int, note: str) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        if lead.LeadStatus == LeadStatus.PRE_APPROVED:
            raise ValueError("Lead ist bereits PRE_APPROVED")

        previous = lead.LeadStatus
        lead.LeadStatus = LeadStatus.PRE_APPROVED
        lead.QualificationReason = f"[Manuelle Freigabe] {note}"
        updated = self.partner_repo.update(lead)

        logger.info("Lead manually approved — lead={} previous={} note={}", lead_id, previous, note)
        return updated
