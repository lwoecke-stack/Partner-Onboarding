# Siemens Partner Eligibility & Onboarding Automation System

A production-ready local development environment for automating partner lead qualification, DAMEX screening, compliance checks, and AI-assisted eligibility decisions.

---

## Quickstart (Windows / Python 3.12)

```bash
cd C:/Users/z004zm2s/PartnerAutomation

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env — especially AZURE_OPENAI_* if you want AI analysis

# 3. Start the API (auto-creates DB, seeds 500 records, creates backup)
python main.py

# 4. Start the Streamlit frontend (separate terminal)
streamlit run streamlit_app.py
```

- **API docs**: http://localhost:8000/docs  
- **Frontend**: http://localhost:8501

---

## Default Login Credentials

| Username     | Password         | Role                 |
|--------------|------------------|----------------------|
| admin        | Admin@1234!      | Admin                |
| gbs_user     | GBSUser@1234!    | GBSUser              |
| compliance   | Compliance@1234! | ComplianceUser       |
| zone_ops     | ZoneOps@1234!    | ZoneOperationsUser   |

---

## Project Structure

```
PartnerAutomation/
├── main.py                         # FastAPI entry point + startup lifecycle
├── streamlit_app.py                # Streamlit multi-page frontend
├── requirements.txt
├── .env                            # Environment variables (not committed)
├── alembic.ini
├── alembic/
│   ├── env.py                      # render_as_batch=True for SQLite
│   └── versions/
├── app/
│   ├── config/
│   │   ├── settings.py             # Pydantic BaseSettings
│   │   ├── database.py             # SQLAlchemy engine, WAL mode, get_db()
│   │   └── logging_config.py       # Loguru structured logging
│   ├── models/
│   │   ├── base.py                 # DeclarativeBase
│   │   ├── partner_lead.py         # PartnerLead + all enums
│   │   ├── user.py                 # User + UserRole
│   │   └── audit_trail.py          # AuditTrail + AuditAction
│   ├── repositories/
│   │   ├── base_repository.py      # Generic[T] BaseRepository
│   │   └── partner_repository.py   # Partner-specific queries
│   ├── services/
│   │   ├── auth_service.py         # JWT auth, bcrypt, seed users
│   │   ├── eligibility_service.py  # Rule-based eligibility engine
│   │   ├── damex_service.py        # Simulated DAMEX screening
│   │   ├── compliance_service.py   # Simulated compliance check
│   │   ├── workflow_service.py     # State machine + auto-advance
│   │   └── backup_service.py       # DB backup with 20-file retention
│   ├── ai/
│   │   ├── azure_openai_client.py  # OpenAI SDK + retry logic
│   │   └── eligibility_analyst.py  # AI scores + fallback analysis
│   ├── reports/
│   │   └── pdf_generator.py        # ReportLab PDF (Siemens branding)
│   ├── security/
│   │   └── rbac.py                 # Role-based access control
│   ├── api/
│   │   ├── dependencies.py         # CurrentUser, DBSession, require_role
│   │   └── routes/
│   │       ├── auth.py             # /auth/login, /auth/me
│   │       ├── partners.py         # CRUD, search, export, stats
│   │       ├── workflow.py         # advance, run-full, batch endpoints
│   │       └── reports.py          # PDF generation endpoints
│   └── workflows/
│       └── partner_workflow.py     # High-level workflow orchestration
├── scripts/
│   ├── generate_dummy_data.py      # Faker-based 500-record seeder
│   ├── seed_database.py            # Standalone seed script
│   ├── backup_database.py          # Manual backup script
│   └── restore_database.py         # Interactive restore script
├── database/
│   └── PartnerOnboarding.db        # SQLite database (auto-created)
├── backups/                        # DB backups (max 20 retained)
├── reports/                        # Generated PDF reports
├── exports/                        # CSV / JSON / XLSX exports
├── logs/                           # Loguru log files
└── tests/
    ├── conftest.py                  # In-memory test DB, fixtures
    ├── unit/
    │   └── test_eligibility.py     # Eligibility engine unit tests
    ├── integration/
    │   └── test_partner_api.py     # FastAPI route integration tests
    └── e2e/
        └── test_partner_workflow.py # Full workflow end-to-end tests
```

---

## Startup Lifecycle

**First run (no database):**
1. Create `database/PartnerOnboarding.db`
2. Apply schema (WAL mode, foreign keys, indexes)
3. Seed 4 default users
4. Generate 500 dummy partner records (8 European countries)
5. Create initial backup → `backups/PartnerOnboarding_<timestamp>.db`

**Subsequent runs (existing database):**
1. Validate and sync schema (`create_all` is idempotent)
2. Create startup backup

---

## Eligibility Engine

| Condition | Decision |
|---|---|
| Missing required fields / invalid email | REJECTED |
| `TotalEmployees < 30` | REJECTED |
| `SalesEmployees < 5` | REJECTED |
| `TechnicalEmployees < 5` | REJECTED |
| `AnnualRevenue < 100,000` | REJECTED |
| All thresholds met + `FoundingYear < 2022` | QUALIFIED |
| All thresholds met + `FoundingYear >= 2022` | INVESTIGATION_REQUIRED |

---

## DAMEX & Compliance Simulation

Both services use deterministic hash-based simulation so results are consistent per company:

- **DAMEX**: `hash(CompanyName + Email) % 100` → < 85 = NO_RECORD_FOUND, ≥ 85 = RED_FLAG_FOUND
- **Compliance**: `hash(CompanyName + Country) % 100` → < 75 = NO_MATCH, < 90 = NON_RELEVANT_MATCH, ≥ 90 = MATCH (+ escalation)

---

## Azure OpenAI Integration

Set in `.env`:
```
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

When not configured, the system falls back to deterministic score calculation from revenue and employee counts. All AI reasoning is appended to the `QualificationReason` field.

---

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# With coverage
pytest --cov=app --cov-report=html
```

---

## Manual Scripts

```bash
# Create manual backup
python scripts/backup_database.py

# List available backups
python scripts/restore_database.py list

# Restore latest backup
python scripts/restore_database.py latest

# Restore specific backup
python scripts/restore_database.py restore 3

# Regenerate seed data
python scripts/seed_database.py 500
```

---

## API Endpoints (Summary)

### Auth
- `POST /auth/login` — returns JWT token
- `GET /auth/me` — current user info

### Partners
- `GET /partners/` — list with search + pagination
- `POST /partners/` — create lead
- `GET /partners/{id}` — get lead
- `PATCH /partners/{id}` — update lead
- `GET /partners/status/{status}` — filter by status
- `GET /partners/stats/summary` — dashboard stats
- `GET /partners/export/csv|json|xlsx` — data exports

### Workflow
- `POST /workflow/{id}/advance` — advance one step
- `POST /workflow/{id}/run-full` — run complete workflow
- `POST /workflow/{id}/reject` — reject lead
- `POST /workflow/{id}/eligibility` — trigger eligibility check
- `POST /workflow/{id}/damex` — trigger DAMEX check
- `POST /workflow/{id}/compliance` — trigger compliance check
- `POST /workflow/{id}/ai-analysis` — request AI analysis
- `POST /workflow/batch/eligibility|damex|compliance` — batch processing

### Reports (PDF)
- `GET /reports/{id}/partner-history`
- `GET /reports/{id}/eligibility`
- `GET /reports/{id}/damex`
- `GET /reports/{id}/compliance`

---

## Architecture

- **Clean Architecture**: Repository Pattern → Service Layer → API Routes
- **Dependency Injection**: FastAPI `Depends()` throughout
- **Database**: SQLite with WAL mode, foreign keys, 7 indexes
- **Auth**: JWT (HS256) + bcrypt + RBAC (4 roles, 14 permissions)
- **Audit Trail**: Every state change logged with old/new values
- **Backups**: Automatic on startup + manual, max 20 retained
- **PDF Reports**: ReportLab with Siemens teal (#009999) branding
- **Exports**: Pandas → CSV / JSON / XLSX (openpyxl)
- **Logging**: Loguru with daily rotation, 30-day retention

---

*Siemens GBS — Partner Eligibility & Onboarding Automation System*
