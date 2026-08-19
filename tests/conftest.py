"""Pytest configuration — shared fixtures for all test layers."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.models.base import Base
from app.models import PartnerLead  # noqa: register models
from app.models.partner_lead import PartnershipType, LeadStatus
from app.config.database import get_db
from main import app

# ── In-memory test database ───────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_schema():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_lead(db) -> PartnerLead:
    lead = PartnerLead(
        FirstName="Hans",
        LastName="Müller",
        Email="hans.mueller@techsolutions.de",
        CompanyName="Tech Solutions GmbH",
        Country="Germany",
        City="Munich",
        Street="Maximilianstr. 42",
        PostalCode="80333",
        AnnualRevenue=2_500_000.0,
        FoundingYear=2010,
        TotalEmployees=120,
        SalesEmployees=25,
        TechnicalEmployees=45,
        PartnershipType=PartnershipType.SOLUTION_PARTNER,
        LeadStatus=LeadStatus.IN_PROGRESS,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@pytest.fixture()
def disqualified_lead(db) -> PartnerLead:
    """Lead that will fail eligibility — too few employees."""
    lead = PartnerLead(
        FirstName="Peter",
        LastName="Klein",
        Email="peter.klein@micro.de",
        CompanyName="Micro GbR",
        Country="Germany",
        City="Berlin",
        Street="Unter den Linden 1",
        PostalCode="10117",
        AnnualRevenue=50_000.0,
        FoundingYear=2023,
        TotalEmployees=5,
        SalesEmployees=1,
        TechnicalEmployees=2,
        PartnershipType=PartnershipType.DISTRIBUTION_PARTNER,
        LeadStatus=LeadStatus.IN_PROGRESS,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
