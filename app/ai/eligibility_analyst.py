"""AI Eligibility Analyst — generates AI recommendations via Azure OpenAI."""
import json
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from app.models.partner_lead import PartnerLead, AIRecommendation
from app.repositories.partner_repository import PartnerRepository
from app.ai.azure_openai_client import azure_client
from loguru import logger

SYSTEM_PROMPT = """You are a Siemens Partner Eligibility Analyst AI.
Analyse the partner profile and return a JSON response with exactly these fields:
{
  "eligibility_summary": "<2-3 sentence summary>",
  "business_potential_score": <integer 0-100>,
  "risk_score": <integer 0-100>,
  "recommendation": "<Approve|Reject|Investigate>",
  "recommendation_reason": "<1-2 sentence justification>"
}
Be objective. Base scores on company size, revenue, employee profile, and founding year.
High revenue + large team = high potential. New company + missing data = higher risk.
"""


@dataclass
class AIAnalysisResult:
    eligibility_summary: str
    business_potential_score: int
    risk_score: int
    recommendation: AIRecommendation
    recommendation_reason: str


def _build_prompt(lead: PartnerLead) -> str:
    return f"""
Partner Profile:
- Company: {lead.CompanyName}
- Country: {lead.Country}
- Partnership Type: {lead.PartnershipType}
- Annual Revenue: EUR {lead.AnnualRevenue:,.0f}
- Total Employees: {lead.TotalEmployees}
- Sales Employees: {lead.SalesEmployees}
- Technical Employees: {lead.TechnicalEmployees}
- Founded: {lead.FoundingYear}
- Email: {lead.Email}
- Current Eligibility: {lead.EligibilityDecision}
- DAMEX Status: {lead.DamexStatus}
- Compliance Status: {lead.ComplianceStatus}
- Qualification Reason: {lead.QualificationReason}

Provide your analysis as the specified JSON.
"""


def _fallback_analysis(lead: PartnerLead) -> AIAnalysisResult:
    revenue = lead.AnnualRevenue or 0
    employees = lead.TotalEmployees or 0

    potential = min(100, int((revenue / 1_000_000) * 10 + (employees / 100) * 5))
    risk = 20 if employees > 50 else 60

    if potential > 60 and risk < 40:
        rec = AIRecommendation.APPROVE
    elif risk > 60:
        rec = AIRecommendation.REJECT
    else:
        rec = AIRecommendation.INVESTIGATE

    return AIAnalysisResult(
        eligibility_summary=f"{lead.CompanyName} shows {'strong' if potential > 60 else 'moderate'} business potential with {employees} employees and EUR {revenue:,.0f} revenue.",
        business_potential_score=potential,
        risk_score=risk,
        recommendation=rec,
        recommendation_reason="Score-based assessment (AI service unavailable — fallback mode).",
    )


class AIEligibilityAnalyst:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partner_repo = PartnerRepository(db)

    def analyse(self, lead_id: int) -> Optional[AIAnalysisResult]:
        lead = self.partner_repo.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"PartnerLead {lead_id} not found")

        if not azure_client.is_configured():
            logger.warning("Azure OpenAI not configured — using fallback analysis for lead={}", lead_id)
            result = _fallback_analysis(lead)
        else:
            try:
                raw = azure_client.complete(SYSTEM_PROMPT, _build_prompt(lead))
                data = json.loads(raw)
                rec_str = data.get("recommendation", "Investigate")
                rec = AIRecommendation(rec_str) if rec_str in [r.value for r in AIRecommendation] else AIRecommendation.INVESTIGATE
                result = AIAnalysisResult(
                    eligibility_summary=data.get("eligibility_summary", ""),
                    business_potential_score=int(data.get("business_potential_score", 50)),
                    risk_score=int(data.get("risk_score", 50)),
                    recommendation=rec,
                    recommendation_reason=data.get("recommendation_reason", ""),
                )
            except Exception as exc:
                logger.error("AI analysis failed for lead={}: {} — using fallback", lead_id, exc)
                result = _fallback_analysis(lead)

        lead.AIRecommendation = result.recommendation
        if lead.QualificationReason:
            lead.QualificationReason += f" | AI: {result.recommendation_reason}"
        else:
            lead.QualificationReason = f"AI: {result.recommendation_reason}"
        self.partner_repo.update(lead)

        logger.info(
            "AI analysis — lead={} potential={} risk={} rec={}",
            lead_id, result.business_potential_score, result.risk_score, result.recommendation,
        )
        return result
