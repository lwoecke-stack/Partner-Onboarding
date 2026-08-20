"""PDF report generator using ReportLab."""
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from app.config.settings import settings
from app.models.partner_lead import PartnerLead
from loguru import logger

SIEMENS_TEAL = colors.HexColor("#009999")
SIEMENS_DARK = colors.HexColor("#1B1534")
LIGHT_GREY = colors.HexColor("#F5F5F5")


def _header_style():
    style = ParagraphStyle(
        "SiemensHeader",
        fontSize=16,
        textColor=SIEMENS_DARK,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    return style


def _sub_header_style():
    return ParagraphStyle(
        "SiemensSubHeader",
        fontSize=12,
        textColor=SIEMENS_TEAL,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )


def _body_style():
    return ParagraphStyle(
        "SiemensBody",
        fontSize=10,
        textColor=colors.black,
        spaceAfter=3,
        fontName="Helvetica",
    )


def _build_table(data: list, col_widths=None) -> Table:
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SIEMENS_TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _output_path(company: str, report_type: str) -> Path:
    reports_dir = Path(settings.REPORTS_DIR)
    reports_dir.mkdir(parents=True, exist_ok=True)
    safe_company = "".join(c if c.isalnum() else "_" for c in company)
    date_str = datetime.now().strftime("%Y%m%d")
    return reports_dir / f"{safe_company}_{report_type}_{date_str}.pdf"


def generate_partner_history_report(lead: PartnerLead) -> Path:
    path = _output_path(lead.CompanyName, "PartnerHistory")
    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("SIEMENS PARTNER HISTORY REPORT", _header_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=SIEMENS_TEAL))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", _body_style()))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Partner Information", _sub_header_style()))
    info_data = [
        ["Field", "Value"],
        ["Company", lead.CompanyName],
        ["Contact", f"{lead.FirstName} {lead.LastName}"],
        ["Email", lead.Email],
        ["Country", lead.Country],
        ["City", lead.City or "—"],
        ["Annual Revenue", f"EUR {lead.AnnualRevenue:,.0f}" if lead.AnnualRevenue else "—"],
        ["Founded", str(lead.FoundingYear) if lead.FoundingYear else "—"],
        ["Total Employees", str(lead.TotalEmployees) if lead.TotalEmployees else "—"],
        ["Partnership Type", lead.PartnershipType.value if lead.PartnershipType else "—"],
    ]
    story.append(_build_table(info_data, col_widths=[7*cm, 11*cm]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Workflow Status", _sub_header_style()))
    status_data = [
        ["Stage", "Status"],
        ["Lead Status", lead.LeadStatus.value if lead.LeadStatus else "—"],
        ["Eligibility", lead.EligibilityDecision.value if lead.EligibilityDecision else "—"],
        ["DAMEX", lead.DamexStatus.value if lead.DamexStatus else "—"],
        ["Compliance", lead.ComplianceStatus.value if lead.ComplianceStatus else "—"],
        ["AI Recommendation", lead.AIRecommendation.value if lead.AIRecommendation else "—"],
    ]
    story.append(_build_table(status_data, col_widths=[7*cm, 11*cm]))

    if lead.QualificationReason:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Qualification Notes", _sub_header_style()))
        story.append(Paragraph(lead.QualificationReason, _body_style()))

    doc.build(story)
    logger.info("Partner history report: {}", path)
    return path


def generate_eligibility_report(lead: PartnerLead) -> Path:
    path = _output_path(lead.CompanyName, "Eligibility")
    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("SIEMENS PARTNER ELIGIBILITY REPORT", _header_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=SIEMENS_TEAL))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", _body_style()))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Eligibility Assessment", _sub_header_style()))
    data = [
        ["Criterion", "Value", "Assessment"],
        ["Total Employees", str(lead.TotalEmployees or 0), "PASS" if (lead.TotalEmployees or 0) > 30 else "FAIL"],
        ["Sales Employees", str(lead.SalesEmployees or 0), "PASS" if (lead.SalesEmployees or 0) > 5 else "FAIL"],
        ["Technical Employees", str(lead.TechnicalEmployees or 0), "PASS" if (lead.TechnicalEmployees or 0) > 5 else "FAIL"],
        ["Annual Revenue", f"EUR {lead.AnnualRevenue:,.0f}" if lead.AnnualRevenue else "—", "PASS" if (lead.AnnualRevenue or 0) >= 100_000 else "FAIL"],
        ["Email Valid", lead.Email, "PASS"],
        ["Decision", lead.EligibilityDecision.value if lead.EligibilityDecision else "PENDING", ""],
    ]
    story.append(_build_table(data, col_widths=[6*cm, 8*cm, 4*cm]))

    if lead.QualificationReason:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Decision Reason", _sub_header_style()))
        story.append(Paragraph(lead.QualificationReason, _body_style()))

    doc.build(story)
    logger.info("Eligibility report: {}", path)
    return path


def generate_damex_report(lead: PartnerLead) -> Path:
    path = _output_path(lead.CompanyName, "DAMEX")
    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("SIEMENS DAMEX SCREENING REPORT", _header_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=SIEMENS_TEAL))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", _body_style()))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("DAMEX Screening Result", _sub_header_style()))
    data = [
        ["Field", "Value"],
        ["Company", lead.CompanyName],
        ["Country", lead.Country],
        ["DAMEX Status", lead.DamexStatus.value if lead.DamexStatus else "PENDING"],
        ["Lead Status", lead.LeadStatus.value if lead.LeadStatus else "—"],
    ]
    story.append(_build_table(data, col_widths=[7*cm, 11*cm]))

    story.append(Spacer(1, 0.5*cm))
    status = lead.DamexStatus.value if lead.DamexStatus else "Not screened"
    story.append(Paragraph(f"DAMEX screening result: {status}", _body_style()))

    doc.build(story)
    logger.info("DAMEX report: {}", path)
    return path


def generate_compliance_report(lead: PartnerLead) -> Path:
    path = _output_path(lead.CompanyName, "Compliance")
    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("SIEMENS COMPLIANCE SCREENING REPORT", _header_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=SIEMENS_TEAL))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", _body_style()))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Compliance Screening Result", _sub_header_style()))
    data = [
        ["Field", "Value"],
        ["Company", lead.CompanyName],
        ["Country", lead.Country],
        ["Compliance Status", lead.ComplianceStatus.value if lead.ComplianceStatus else "PENDING"],
        ["Escalation Required", "YES" if lead.ComplianceStatus and lead.ComplianceStatus.value == "Match" else "NO"],
        ["Lead Status", lead.LeadStatus.value if lead.LeadStatus else "—"],
    ]
    story.append(_build_table(data, col_widths=[7*cm, 11*cm]))

    doc.build(story)
    logger.info("Compliance report: {}", path)
    return path
