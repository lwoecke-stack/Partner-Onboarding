"""Report orchestration service."""
from pathlib import Path
from sqlalchemy.orm import Session
from app.repositories.partner_repository import PartnerRepository
from app.reports.pdf_generator import (
    generate_partner_history_report,
    generate_eligibility_report,
    generate_damex_report,
    generate_compliance_report,
)
from loguru import logger


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)

    def generate_all_reports(self, lead_id: int) -> dict[str, Path]:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        reports = {}
        reports["history"] = generate_partner_history_report(lead)
        reports["eligibility"] = generate_eligibility_report(lead)
        reports["damex"] = generate_damex_report(lead)
        reports["compliance"] = generate_compliance_report(lead)

        logger.info("All reports generated for lead={}", lead_id)
        return reports

    def generate_history_report(self, lead_id: int) -> Path:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")
        return generate_partner_history_report(lead)

    def generate_eligibility_report(self, lead_id: int) -> Path:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")
        return generate_eligibility_report(lead)

    def generate_damex_report(self, lead_id: int) -> Path:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")
        return generate_damex_report(lead)

    def generate_compliance_report(self, lead_id: int) -> Path:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")
        return generate_compliance_report(lead)
