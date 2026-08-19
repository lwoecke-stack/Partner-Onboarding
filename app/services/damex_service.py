"""DAMEX screening service — simulated adapter layer."""
from sqlalchemy.orm import Session
from app.models.partner_lead import PartnerLead, DamexStatus, LeadStatus
from app.repositories.partner_repository import PartnerRepository
from loguru import logger


def _simulate_damex_check(lead: PartnerLead) -> tuple[DamexStatus, str]:
    seed = hash(f"{lead.CompanyName}{lead.Email}") % 100

    if seed < 85:
        return DamexStatus.NO_RECORD_FOUND, "No adverse records found in DAMEX database"
    else:
        return DamexStatus.RED_FLAG_FOUND, "Potential adverse record detected — manual review required"


class DamexService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)

    def run_damex_check(self, lead_id: int) -> PartnerLead:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        damex_result, details = _simulate_damex_check(lead)
        lead.DamexStatus = damex_result

        if damex_result == DamexStatus.RED_FLAG_FOUND:
            lead.LeadStatus = LeadStatus.REJECTED
        else:
            lead.LeadStatus = LeadStatus.DAMEX

        updated = self.partner_repo.update(lead)
        logger.info("DAMEX check — lead={} result={}", lead_id, damex_result)
        return updated

    def run_batch_damex(self) -> dict:
        leads = self.partner_repo.get_pending_damex()
        results = {"no_record": 0, "red_flag": 0, "total": len(leads)}

        for lead in leads:
            updated = self.run_damex_check(lead.ID)
            if updated.DamexStatus == DamexStatus.NO_RECORD_FOUND:
                results["no_record"] += 1
            else:
                results["red_flag"] += 1

        logger.info("Batch DAMEX complete: {}", results)
        return results
