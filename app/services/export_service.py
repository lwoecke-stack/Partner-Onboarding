"""Data export service — CSV, JSON, XLSX."""
import json
from datetime import datetime
from pathlib import Path
from typing import List
import pandas as pd
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.partner_lead import PartnerLead
from app.repositories.partner_repository import PartnerRepository
from loguru import logger


def _leads_to_records(leads: List[PartnerLead]) -> List[dict]:
    return [
        {
            "ID": lead.ID,
            "FirstName": lead.FirstName,
            "LastName": lead.LastName,
            "Email": lead.Email,
            "CompanyName": lead.CompanyName,
            "Country": lead.Country,
            "City": lead.City,
            "Street": lead.Street,
            "PostalCode": lead.PostalCode,
            "AnnualRevenue": lead.AnnualRevenue,
            "FoundingYear": lead.FoundingYear,
            "TotalEmployees": lead.TotalEmployees,
            "SalesEmployees": lead.SalesEmployees,
            "TechnicalEmployees": lead.TechnicalEmployees,
            "PartnershipType": lead.PartnershipType.value if lead.PartnershipType else None,
            "LeadStatus": lead.LeadStatus.value if lead.LeadStatus else None,
            "EligibilityDecision": lead.EligibilityDecision.value if lead.EligibilityDecision else None,
            "DamexStatus": lead.DamexStatus.value if lead.DamexStatus else None,
            "ComplianceStatus": lead.ComplianceStatus.value if lead.ComplianceStatus else None,
            "AIRecommendation": lead.AIRecommendation.value if lead.AIRecommendation else None,
            "QualificationReason": lead.QualificationReason,
            "CreatedDate": lead.CreatedDate.isoformat() if lead.CreatedDate else None,
            "UpdatedDate": lead.UpdatedDate.isoformat() if lead.UpdatedDate else None,
        }
        for lead in leads
    ]


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)
        self.export_dir = Path(settings.EXPORT_DIR)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _filename(self, fmt: str) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.export_dir / f"PartnerLeads_{ts}.{fmt}"

    def export_csv(self) -> Path:
        leads = self.partner_repo.get_all(limit=100_000)
        records = _leads_to_records(leads)
        path = self._filename("csv")
        pd.DataFrame(records).to_csv(path, index=False, encoding="utf-8-sig")
        logger.info("CSV export: {} ({} records)", path, len(records))
        return path

    def export_json(self) -> Path:
        leads = self.partner_repo.get_all(limit=100_000)
        records = _leads_to_records(leads)
        path = self._filename("json")
        path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("JSON export: {} ({} records)", path, len(records))
        return path

    def export_xlsx(self) -> Path:
        leads = self.partner_repo.get_all(limit=100_000)
        records = _leads_to_records(leads)
        path = self._filename("xlsx")
        df = pd.DataFrame(records)
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="PartnerLeads", index=False)
        logger.info("XLSX export: {} ({} records)", path, len(records))
        return path
