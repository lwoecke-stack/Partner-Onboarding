"""Partner lead CRUD routes."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.api.dependencies import DBSession
from app.models.partner_lead import (
    PartnerLead, PartnershipType, LeadStatus,
    EligibilityDecision, DamexStatus, ComplianceStatus, AIRecommendation,
)
from app.repositories.partner_repository import PartnerRepository

router = APIRouter(prefix="/partners", tags=["Partners"])


class PartnerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    company_name: str
    country: str
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    annual_revenue: Optional[float] = None
    founding_year: Optional[int] = None
    total_employees: Optional[int] = None
    sales_employees: Optional[int] = None
    technical_employees: Optional[int] = None
    partnership_type: Optional[PartnershipType] = None


class PartnerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    annual_revenue: Optional[float] = None
    founding_year: Optional[int] = None
    total_employees: Optional[int] = None
    sales_employees: Optional[int] = None
    technical_employees: Optional[int] = None
    partnership_type: Optional[PartnershipType] = None


class PartnerResponse(BaseModel):
    ID: int
    FirstName: str
    LastName: str
    Email: str
    CompanyName: str
    Country: str
    City: Optional[str]
    Street: Optional[str]
    PostalCode: Optional[str]
    AnnualRevenue: Optional[float]
    FoundingYear: Optional[int]
    TotalEmployees: Optional[int]
    SalesEmployees: Optional[int]
    TechnicalEmployees: Optional[int]
    PartnershipType: Optional[PartnershipType]
    LeadStatus: Optional[LeadStatus]
    EligibilityDecision: Optional[EligibilityDecision]
    DamexStatus: Optional[DamexStatus]
    ComplianceStatus: Optional[ComplianceStatus]
    AIRecommendation: Optional[AIRecommendation]
    QualificationReason: Optional[str]
    CreatedDate: Optional[datetime]
    UpdatedDate: Optional[datetime]

    model_config = {"from_attributes": True}


@router.post("/", response_model=PartnerResponse, status_code=201)
def create_partner(payload: PartnerCreate, db: DBSession):
    repo = PartnerRepository(db)
    if repo.get_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    lead = PartnerLead(
        FirstName=payload.first_name,
        LastName=payload.last_name,
        Email=payload.email,
        CompanyName=payload.company_name,
        Country=payload.country,
        City=payload.city,
        Street=payload.street,
        PostalCode=payload.postal_code,
        AnnualRevenue=payload.annual_revenue,
        FoundingYear=payload.founding_year,
        TotalEmployees=payload.total_employees,
        SalesEmployees=payload.sales_employees,
        TechnicalEmployees=payload.technical_employees,
        PartnershipType=payload.partnership_type,
        LeadStatus=LeadStatus.IN_PROGRESS,
    )
    return PartnerResponse.model_validate(repo.create(lead))


@router.get("/stats/summary")
def get_summary(db: DBSession):
    repo = PartnerRepository(db)
    by_status = repo.get_status_summary()
    by_eligibility = repo.get_eligibility_summary()
    return {"total": repo.count(), "by_status": by_status, "by_eligibility": by_eligibility}


@router.get("/status/{status}", response_model=List[PartnerResponse])
def list_by_status(status: LeadStatus, db: DBSession):
    repo = PartnerRepository(db)
    return [PartnerResponse.model_validate(p) for p in repo.get_by_status(status)]


@router.get("/export/csv")
def export_csv(db: DBSession):
    from app.services.export_service import ExportService
    from fastapi.responses import FileResponse
    path = ExportService(db).export_csv()
    return FileResponse(str(path), media_type="text/csv", filename=path.name)


@router.get("/export/json")
def export_json(db: DBSession):
    from app.services.export_service import ExportService
    from fastapi.responses import FileResponse
    path = ExportService(db).export_json()
    return FileResponse(str(path), media_type="application/json", filename=path.name)


@router.get("/export/xlsx")
def export_xlsx(db: DBSession):
    from app.services.export_service import ExportService
    from fastapi.responses import FileResponse
    path = ExportService(db).export_xlsx()
    return FileResponse(
        str(path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name,
    )


@router.get("/backups/list")
def list_backups():
    from app.services.backup_service import BackupService
    svc = BackupService()
    backups = svc.list_backups()
    return [{"name": b.name, "size_kb": b.stat().st_size // 1024} for b in backups]


@router.post("/backups/create")
def create_backup():
    from app.services.backup_service import BackupService
    path = BackupService().create_backup("manual-api")
    return {"path": str(path)}


@router.get("/", response_model=List[PartnerResponse])
def list_partners(
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    country: Optional[str] = None,
    search: Optional[str] = None,
):
    repo = PartnerRepository(db)
    if search:
        return [PartnerResponse.model_validate(p) for p in repo.search(search)]
    if country:
        return [PartnerResponse.model_validate(p) for p in repo.get_by_country(country)]
    return [PartnerResponse.model_validate(p) for p in repo.get_all(skip=skip, limit=limit)]


@router.get("/{lead_id}", response_model=PartnerResponse)
def get_partner(lead_id: int, db: DBSession):
    lead = PartnerRepository(db).get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Partner not found")
    return PartnerResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=PartnerResponse)
def update_partner(lead_id: int, payload: PartnerUpdate, db: DBSession):
    repo = PartnerRepository(db)
    lead = repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Partner not found")

    if payload.first_name is not None:
        lead.FirstName = payload.first_name
    if payload.last_name is not None:
        lead.LastName = payload.last_name
    if payload.email is not None:
        lead.Email = payload.email
    if payload.company_name is not None:
        lead.CompanyName = payload.company_name
    if payload.country is not None:
        lead.Country = payload.country
    if payload.city is not None:
        lead.City = payload.city
    if payload.street is not None:
        lead.Street = payload.street
    if payload.postal_code is not None:
        lead.PostalCode = payload.postal_code
    if payload.annual_revenue is not None:
        lead.AnnualRevenue = payload.annual_revenue
    if payload.founding_year is not None:
        lead.FoundingYear = payload.founding_year
    if payload.total_employees is not None:
        lead.TotalEmployees = payload.total_employees
    if payload.sales_employees is not None:
        lead.SalesEmployees = payload.sales_employees
    if payload.technical_employees is not None:
        lead.TechnicalEmployees = payload.technical_employees
    if payload.partnership_type is not None:
        lead.PartnershipType = payload.partnership_type

    return PartnerResponse.model_validate(repo.update(lead))


@router.delete("/{lead_id}", status_code=204)
def delete_partner(lead_id: int, db: DBSession):
    repo = PartnerRepository(db)
    lead = repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Partner not found")
    repo.delete(lead)
