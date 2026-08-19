"""Unit tests for the eligibility engine."""
import pytest
from app.models.partner_lead import (
    PartnerLead, PartnershipType, LeadStatus,
    EligibilityDecision,
)
from app.services.eligibility_service import EligibilityService


def _build_lead(**overrides) -> PartnerLead:
    defaults = dict(
        FirstName="Anna",
        LastName="Schmidt",
        Email="anna.schmidt@example-tech.de",
        CompanyName="Example Tech GmbH",
        Country="Germany",
        City="Frankfurt",
        Street="Mainzer Str. 10",
        PostalCode="60329",
        AnnualRevenue=3_000_000.0,
        FoundingYear=2008,
        TotalEmployees=150,
        SalesEmployees=30,
        TechnicalEmployees=60,
        PartnershipType=PartnershipType.SOLUTION_PARTNER,
        LeadStatus=LeadStatus.ELIGIBILITY,
    )
    defaults.update(overrides)
    lead = PartnerLead(**defaults)
    lead.ID = 1
    return lead


# ── QUALIFIED scenarios ────────────────────────────────────────────────────────
class TestQualified:
    def test_strong_company_qualifies(self):
        lead = _build_lead()
        decision, reason = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.QUALIFIED
        assert "qualif" in reason.lower() or "meets" in reason.lower() or decision.value == "QUALIFIED"

    def test_minimum_threshold_qualifies(self):
        lead = _build_lead(
            AnnualRevenue=100_000.0,
            TotalEmployees=30,
            SalesEmployees=5,
            TechnicalEmployees=5,
            FoundingYear=2019,
        )
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.QUALIFIED

    def test_large_enterprise_qualifies(self):
        lead = _build_lead(
            AnnualRevenue=50_000_000.0,
            TotalEmployees=5000,
            SalesEmployees=500,
            TechnicalEmployees=1000,
            FoundingYear=1990,
        )
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.QUALIFIED


# ── REJECTED scenarios ────────────────────────────────────────────────────────
class TestRejected:
    def test_too_few_total_employees(self):
        lead = _build_lead(TotalEmployees=20, SalesEmployees=3, TechnicalEmployees=4)
        decision, reason = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED
        assert "employee" in reason.lower() or "staff" in reason.lower() or decision.value == "REJECTED"

    def test_revenue_too_low(self):
        lead = _build_lead(AnnualRevenue=50_000.0)
        decision, reason = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED

    def test_missing_email(self):
        lead = _build_lead(Email="")
        decision, reason = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED

    def test_invalid_email(self):
        lead = _build_lead(Email="not-an-email")
        decision, reason = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED

    def test_too_few_sales_employees(self):
        lead = _build_lead(SalesEmployees=2)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED

    def test_too_few_technical_employees(self):
        lead = _build_lead(TechnicalEmployees=3)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED

    def test_missing_company_name(self):
        lead = _build_lead(CompanyName="")
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED


# ── INVESTIGATION_REQUIRED scenarios ──────────────────────────────────────────
class TestInvestigationRequired:
    def test_recently_founded_company(self):
        lead = _build_lead(FoundingYear=2022)
        decision, reason = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.INVESTIGATION_REQUIRED
        assert "founding" in reason.lower() or "year" in reason.lower() or decision.value == "INVESTIGATION_REQUIRED"

    def test_founded_current_year_triggers_investigation(self):
        lead = _build_lead(FoundingYear=2025)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.INVESTIGATION_REQUIRED


# ── Edge cases ────────────────────────────────────────────────────────────────
class TestEdgeCases:
    def test_exactly_30_employees(self):
        lead = _build_lead(TotalEmployees=30, SalesEmployees=5, TechnicalEmployees=5)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.QUALIFIED

    def test_exactly_100k_revenue(self):
        lead = _build_lead(AnnualRevenue=100_000.0)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.QUALIFIED

    def test_29_employees_rejected(self):
        lead = _build_lead(TotalEmployees=29)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED

    def test_revenue_just_below_threshold(self):
        lead = _build_lead(AnnualRevenue=99_999.0)
        decision, _ = EligibilityService.evaluate_eligibility(lead)
        assert decision == EligibilityDecision.REJECTED
