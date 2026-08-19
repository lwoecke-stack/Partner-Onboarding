"""Generate 500 realistic partner lead records using Faker."""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy.orm import Session
from app.models.partner_lead import PartnerLead, PartnershipType, LeadStatus

fakers = {
    "Germany": Faker("de_DE"),
    "Austria": Faker("de_AT"),
    "Switzerland": Faker("de_CH"),
    "France": Faker("fr_FR"),
    "Italy": Faker("it_IT"),
    "Spain": Faker("es_ES"),
    "Netherlands": Faker("nl_NL"),
    "Poland": Faker("pl_PL"),
}

COUNTRY_CITIES = {
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart", "Düsseldorf", "Leipzig", "Dresden", "Nuremberg"],
    "Austria": ["Vienna", "Graz", "Linz", "Salzburg", "Innsbruck", "Klagenfurt"],
    "Switzerland": ["Zurich", "Geneva", "Basel", "Bern", "Lausanne", "Lucerne"],
    "France": ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Strasbourg", "Nantes", "Lille"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Bologna", "Florence", "Venice", "Genoa"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Malaga", "Zaragoza"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Tilburg"],
    "Poland": ["Warsaw", "Krakow", "Gdansk", "Wroclaw", "Poznan", "Lodz", "Katowice"],
}

POSTAL_PATTERNS = {
    "Germany": lambda: f"{random.randint(10000, 99999)}",
    "Austria": lambda: f"{random.randint(1000, 9999)}",
    "Switzerland": lambda: f"{random.randint(1000, 9999)}",
    "France": lambda: f"{random.randint(10000, 99999)}",
    "Italy": lambda: f"{random.randint(10000, 99999)}",
    "Spain": lambda: f"{random.randint(10000, 99999)}",
    "Netherlands": lambda: f"{random.randint(1000, 9999)} {random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}",
    "Poland": lambda: f"{random.randint(10, 99)}-{random.randint(100, 999)}",
}

PARTNERSHIP_TYPES = list(PartnershipType)
STATUSES = [LeadStatus.IN_PROGRESS, LeadStatus.PARTNER_FINDER, LeadStatus.ELIGIBILITY,
            LeadStatus.DAMEX, LeadStatus.COMPLIANCE, LeadStatus.PRE_APPROVED, LeadStatus.REJECTED]
STATUS_WEIGHTS = [15, 20, 20, 15, 10, 10, 10]

INDUSTRY_PREFIXES = [
    "Tech", "Digital", "Smart", "Global", "Euro", "Pro", "Advanced", "Innovative",
    "Integrated", "Unified", "Apex", "Prime", "Core", "Dynamic", "Strategic",
]
INDUSTRY_SUFFIXES = [
    "Systems", "Solutions", "Technologies", "Services", "Consulting", "Engineering",
    "Automation", "Networks", "Software", "Dynamics", "Analytics", "Industries",
]


def generate_company_name(fake: Faker) -> str:
    style = random.randint(0, 2)
    if style == 0:
        return f"{random.choice(INDUSTRY_PREFIXES)} {random.choice(INDUSTRY_SUFFIXES)}"
    elif style == 1:
        word = fake.last_name()
        return f"{word} {random.choice(INDUSTRY_SUFFIXES)}"
    else:
        return fake.company()


def generate_partner_record(db_emails: set) -> PartnerLead:
    country = random.choice(list(fakers.keys()))
    fake = fakers[country]

    first_name = fake.first_name()
    last_name = fake.last_name()
    company_name = generate_company_name(fake)

    safe_company = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")[:20]
    email_base = f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}@{safe_company}.com"
    email = email_base
    counter = 1
    while email in db_emails:
        email = f"{first_name.lower()}.{last_name.lower()}{counter}@{safe_company}.com"
        counter += 1
    db_emails.add(email)

    city = random.choice(COUNTRY_CITIES[country])
    postal_code = POSTAL_PATTERNS[country]()

    total_employees = random.randint(5, 10000)
    sales_employees = max(1, int(total_employees * random.uniform(0.05, 0.25)))
    sales_employees = min(sales_employees, 1000)
    technical_employees = max(1, int(total_employees * random.uniform(0.1, 0.4)))
    technical_employees = min(technical_employees, 5000)

    revenue_base = random.lognormvariate(13, 2)
    annual_revenue = max(100_000, min(100_000_000, int(revenue_base)))

    return PartnerLead(
        FirstName=first_name,
        LastName=last_name,
        Email=email,
        CompanyName=company_name,
        Country=country,
        City=city,
        Street=fake.street_address(),
        PostalCode=postal_code,
        AnnualRevenue=float(annual_revenue),
        FoundingYear=random.randint(1980, 2025),
        TotalEmployees=total_employees,
        SalesEmployees=sales_employees,
        TechnicalEmployees=technical_employees,
        PartnershipType=random.choice(PARTNERSHIP_TYPES),
        LeadStatus=random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
    )


def generate_dummy_data(db: Session, count: int = 500) -> int:
    existing_emails: set = set(
        email for (email,) in db.query(PartnerLead.Email).all()
    )

    records = []
    for _ in range(count):
        record = generate_partner_record(existing_emails)
        records.append(record)

    db.add_all(records)
    db.commit()
    return len(records)


if __name__ == "__main__":
    from app.config.database import SessionLocal
    from app.config.logging_config import configure_logging
    configure_logging()

    with SessionLocal() as db:
        count = generate_dummy_data(db)
        print(f"Generated {count} partner records")
