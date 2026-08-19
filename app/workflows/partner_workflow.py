"""Partner workflow state machine definitions and helpers."""
from app.models.partner_lead import LeadStatus

WORKFLOW_STEPS = [
    LeadStatus.IN_PROGRESS,
    LeadStatus.PARTNER_FINDER,
    LeadStatus.ELIGIBILITY,
    LeadStatus.DAMEX,
    LeadStatus.COMPLIANCE,
    LeadStatus.ZONAL_REVIEW,
    LeadStatus.PRE_APPROVED,
]

WORKFLOW_DESCRIPTIONS = {
    LeadStatus.IN_PROGRESS: "Lead created, initial data collection in progress",
    LeadStatus.PARTNER_FINDER: "Partner identified, awaiting eligibility assessment",
    LeadStatus.ELIGIBILITY: "Eligibility assessed, awaiting DAMEX screening",
    LeadStatus.DAMEX: "DAMEX screening complete, awaiting compliance check",
    LeadStatus.COMPLIANCE: "Compliance screening done, awaiting zonal review",
    LeadStatus.ZONAL_REVIEW: "Under zonal review, awaiting pre-approval",
    LeadStatus.PRE_APPROVED: "Pre-approved — ready for final onboarding",
    LeadStatus.REJECTED: "Application rejected",
}


def get_step_number(status: LeadStatus) -> int:
    if status == LeadStatus.REJECTED:
        return -1
    try:
        return WORKFLOW_STEPS.index(status) + 1
    except ValueError:
        return 0


def get_next_status(current: LeadStatus) -> LeadStatus | None:
    if current == LeadStatus.REJECTED or current == LeadStatus.PRE_APPROVED:
        return None
    idx = WORKFLOW_STEPS.index(current)
    if idx + 1 < len(WORKFLOW_STEPS):
        return WORKFLOW_STEPS[idx + 1]
    return None


def is_terminal(status: LeadStatus) -> bool:
    return status in {LeadStatus.PRE_APPROVED, LeadStatus.REJECTED}
