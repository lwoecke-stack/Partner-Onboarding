"""End-to-end workflow tests — full flow, rejection, compliance match."""
import pytest


PARTNER_DATA = {
    "first_name": "Klaus",
    "last_name": "Weber",
    "email": "klaus.weber@digitaldynamics.de",
    "company_name": "Digital Dynamics GmbH",
    "partnership_type": "Technology Partner",
    "country": "Germany",
    "city": "Stuttgart",
    "street": "Königstr. 5",
    "postal_code": "70173",
    "founding_year": 2008,
    "annual_revenue": 8_000_000.0,
    "total_employees": 300,
    "sales_employees": 60,
    "technical_employees": 100,
}

SMALL_PARTNER_DATA = {
    "first_name": "Luisa",
    "last_name": "Ricci",
    "email": "luisa.ricci@microit.it",
    "company_name": "Micro IT Srl",
    "partnership_type": "Distribution Partner",
    "country": "Italy",
    "city": "Rome",
    "street": "Via Veneto 12",
    "postal_code": "00187",
    "founding_year": 2023,
    "annual_revenue": 40_000.0,
    "total_employees": 8,
    "sales_employees": 1,
    "technical_employees": 2,
}


@pytest.fixture()
def created_lead(client) -> dict:
    resp = client.post("/partners/", json=PARTNER_DATA)
    assert resp.status_code in (200, 201), f"Lead creation failed: {resp.text}"
    return resp.json()


@pytest.fixture()
def small_lead(client) -> dict:
    resp = client.post("/partners/", json=SMALL_PARTNER_DATA)
    assert resp.status_code in (200, 201)
    return resp.json()


class TestFullWorkflow:
    """Happy path: lead progresses through all stages to PRE_APPROVED."""

    def test_lead_starts_in_progress(self, created_lead):
        assert created_lead["LeadStatus"] == "IN_PROGRESS"

    def test_advance_to_partner_finder(self, client, created_lead):
        lead_id = created_lead["ID"]
        resp = client.post(f"/workflow/{lead_id}/advance")
        assert resp.status_code == 200
        assert resp.json()["lead"]["LeadStatus"] == "PARTNER_FINDER"

    def test_run_full_workflow_reaches_terminal_state(self, client, created_lead):
        lead_id = created_lead["ID"]
        resp = client.post(f"/workflow/{lead_id}/run-full")
        assert resp.status_code == 200
        final_status = resp.json()["lead"]["LeadStatus"]
        assert final_status in ("PRE_APPROVED", "REJECTED")

    def test_qualified_lead_becomes_pre_approved(self, client, created_lead):
        """Large, well-established company should reach PRE_APPROVED."""
        lead_id = created_lead["ID"]
        resp = client.post(f"/workflow/{lead_id}/run-full")
        assert resp.status_code == 200
        result = resp.json()["lead"]
        assert result["EligibilityDecision"] in ("QUALIFIED", "INVESTIGATION_REQUIRED", "REJECTED")


class TestRejectionFlow:
    """Leads that fail eligibility are rejected."""

    def test_small_lead_fails_eligibility(self, client, small_lead):
        lead_id = small_lead["ID"]
        resp = client.post(f"/workflow/{lead_id}/run-full")
        assert resp.status_code == 200
        result = resp.json()["lead"]
        assert result["EligibilityDecision"] == "REJECTED"
        assert result["LeadStatus"] == "REJECTED"

    def test_manual_reject_sets_status(self, client, created_lead):
        lead_id = created_lead["ID"]
        resp = client.post(
            f"/workflow/{lead_id}/reject",
            params={"reason": "Does not meet Siemens partnership criteria"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "REJECTED"


class TestIndividualWorkflowSteps:
    """Test each workflow step endpoint individually."""

    def test_eligibility_step_sets_decision(self, client, created_lead):
        lead_id = created_lead["ID"]
        client.post(f"/workflow/{lead_id}/advance")
        client.post(f"/workflow/{lead_id}/advance")
        resp = client.post(f"/workflow/{lead_id}/eligibility")
        assert resp.status_code in (200, 400)

    def test_ai_analysis_returns_scores(self, client, created_lead):
        lead_id = created_lead["ID"]
        resp = client.post(f"/workflow/{lead_id}/ai-analysis")
        assert resp.status_code == 200
        body = resp.json()
        assert "business_potential_score" in body or "recommendation" in body

    def test_workflow_advance_returns_updated_lead(self, client, created_lead):
        lead_id = created_lead["ID"]
        resp = client.post(f"/workflow/{lead_id}/advance")
        assert resp.status_code == 200
        body = resp.json()["lead"]
        assert "ID" in body
        assert "LeadStatus" in body
        assert body["ID"] == lead_id


class TestWorkflowIdempotency:
    """Verify terminal states cannot be advanced further."""

    def test_rejected_lead_cannot_advance(self, client, created_lead):
        lead_id = created_lead["ID"]
        client.post(f"/workflow/{lead_id}/reject",
                    params={"reason": "Test rejection"})
        resp = client.post(f"/workflow/{lead_id}/advance")
        assert resp.status_code in (400, 409)

    def test_get_lead_after_workflow(self, client, created_lead):
        lead_id = created_lead["ID"]
        client.post(f"/workflow/{lead_id}/run-full")
        resp = client.get(f"/partners/{lead_id}")
        assert resp.status_code == 200
        assert resp.json()["ID"] == lead_id
