"""Integration tests for the Partner API routes."""
import pytest


VALID_PARTNER = {
    "first_name": "Maria",
    "last_name": "Bauer",
    "email": "maria.bauer@testco.de",
    "company_name": "TestCo GmbH",
    "partnership_type": "Solution Partner",
    "country": "Germany",
    "city": "Berlin",
    "street": "Friedrichstr. 50",
    "postal_code": "10117",
    "founding_year": 2005,
    "annual_revenue": 5_000_000.0,
    "total_employees": 200,
    "sales_employees": 40,
    "technical_employees": 80,
}


class TestCreatePartner:
    def test_create_partner_returns_201(self, client):
        resp = client.post("/partners/", json=VALID_PARTNER)
        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body["CompanyName"] == "TestCo GmbH"
        assert body["LeadStatus"] == "IN_PROGRESS"

    def test_create_partner_duplicate_email_returns_400(self, client):
        client.post("/partners/", json=VALID_PARTNER)
        resp = client.post("/partners/", json=VALID_PARTNER)
        assert resp.status_code in (400, 409, 422)

    def test_create_partner_missing_required_field_returns_422(self, client):
        incomplete = {k: v for k, v in VALID_PARTNER.items() if k != "email"}
        resp = client.post("/partners/", json=incomplete)
        assert resp.status_code == 422


class TestGetPartner:
    def test_get_existing_partner(self, client, sample_lead):
        resp = client.get(f"/partners/{sample_lead.ID}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ID"] == sample_lead.ID
        assert body["CompanyName"] == sample_lead.CompanyName

    def test_get_nonexistent_partner_returns_404(self, client):
        resp = client.get("/partners/999999")
        assert resp.status_code == 404

    def test_list_partners_returns_array(self, client, sample_lead):
        resp = client.get("/partners/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_list_partners_respects_limit(self, client, sample_lead):
        resp = client.get("/partners/?limit=1")
        assert resp.status_code == 200
        assert len(resp.json()) <= 1

    def test_get_partners_by_status(self, client, sample_lead):
        resp = client.get("/partners/status/IN_PROGRESS")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestUpdatePartner:
    def test_update_partner_city(self, client, sample_lead):
        resp = client.patch(
            f"/partners/{sample_lead.ID}",
            json={"city": "Hamburg"},
        )
        assert resp.status_code == 200
        assert resp.json()["City"] == "Hamburg"

    def test_update_nonexistent_partner_returns_404(self, client):
        resp = client.patch("/partners/999999", json={"city": "Berlin"})
        assert resp.status_code == 404


class TestSearchPartner:
    def test_search_by_company_name(self, client, sample_lead):
        resp = client.get("/partners/?search=Tech%20Solutions")
        assert resp.status_code == 200

    def test_search_by_email(self, client, sample_lead):
        resp = client.get(f"/partners/?search={sample_lead.Email}")
        assert resp.status_code == 200


class TestStatsEndpoint:
    def test_stats_summary_has_expected_keys(self, client, sample_lead):
        resp = client.get("/partners/stats/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body
        assert "by_status" in body
        assert "by_eligibility" in body
