"""Workflow and eligibility routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.dependencies import DBSession
from app.services.workflow_service import WorkflowService
from app.services.eligibility_service import EligibilityService
from app.services.damex_service import DamexService
from app.services.compliance_service import ComplianceService
from app.ai.eligibility_analyst import AIEligibilityAnalyst
from app.api.routes.partners import PartnerResponse

router = APIRouter(prefix="/workflow", tags=["Workflow"])


class WorkflowResult(BaseModel):
    lead_id: int
    message: str
    lead: PartnerResponse


class BatchResult(BaseModel):
    total: int
    results: dict


@router.post("/{lead_id}/advance", response_model=WorkflowResult)
def advance_workflow(lead_id: int, db: DBSession):
    svc = WorkflowService(db)
    try:
        lead = svc.advance_workflow(lead_id)
        return WorkflowResult(
            lead_id=lead_id,
            message=f"Workflow advanced to {lead.LeadStatus}",
            lead=PartnerResponse.model_validate(lead),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/run-full", response_model=WorkflowResult)
def run_full_workflow(lead_id: int, db: DBSession):
    svc = WorkflowService(db)
    try:
        lead = svc.run_full_workflow(lead_id)
        return WorkflowResult(
            lead_id=lead_id,
            message=f"Full workflow completed. Final status: {lead.LeadStatus}",
            lead=PartnerResponse.model_validate(lead),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/approve")
def approve_lead(lead_id: int, note: str, db: DBSession):
    svc = WorkflowService(db)
    try:
        lead = svc.approve_lead(lead_id, note)
        return {"message": "Lead manually approved", "lead_id": lead_id, "status": lead.LeadStatus}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/reject")
def reject_lead(lead_id: int, reason: str, db: DBSession):
    svc = WorkflowService(db)
    try:
        lead = svc.reject_lead(lead_id, reason)
        return {"message": "Lead rejected", "lead_id": lead_id, "status": lead.LeadStatus}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/eligibility", response_model=PartnerResponse)
def run_eligibility(lead_id: int, db: DBSession):
    svc = EligibilityService(db)
    try:
        lead = svc.run_eligibility(lead_id)
        return PartnerResponse.model_validate(lead)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/damex", response_model=PartnerResponse)
def run_damex(lead_id: int, db: DBSession):
    svc = DamexService(db)
    try:
        lead = svc.run_damex_check(lead_id)
        return PartnerResponse.model_validate(lead)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/compliance", response_model=PartnerResponse)
def run_compliance(lead_id: int, db: DBSession):
    svc = ComplianceService(db)
    try:
        lead = svc.run_compliance_check(lead_id)
        return PartnerResponse.model_validate(lead)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{lead_id}/ai-analysis")
def run_ai_analysis(lead_id: int, db: DBSession):
    analyst = AIEligibilityAnalyst(db)
    try:
        result = analyst.analyse(lead_id)
        return {
            "lead_id": lead_id,
            "eligibility_summary": result.eligibility_summary,
            "business_potential_score": result.business_potential_score,
            "risk_score": result.risk_score,
            "recommendation": result.recommendation.value,
            "recommendation_reason": result.recommendation_reason,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/batch/eligibility", response_model=BatchResult)
def batch_eligibility(db: DBSession):
    svc = EligibilityService(db)
    results = svc.run_batch_eligibility()
    return BatchResult(total=results["total"], results=results)


@router.post("/batch/damex", response_model=BatchResult)
def batch_damex(db: DBSession):
    svc = DamexService(db)
    results = svc.run_batch_damex()
    return BatchResult(total=results["total"], results=results)


@router.post("/batch/compliance", response_model=BatchResult)
def batch_compliance(db: DBSession):
    svc = ComplianceService(db)
    results = svc.run_batch_compliance()
    return BatchResult(total=results["total"], results=results)
