"""
Siemens Partner Eligibility & Onboarding Automation System
Streamlit Frontend — Siemens Corporate Design
"""
import requests
import pandas as pd
import streamlit as st

# ── Network config ────────────────────────────────────────────────────────────
# Streamlit runs server-side → API calls go via localhost (always correct).
# Other users access the Streamlit UI via the server's local IP on port 8501.
API_BASE = "http://localhost:8000"

# ── Siemens Brand Colors ──────────────────────────────────────────────────────
NAVY      = "#000028"   # Siemens Dark Navy — primary background
TEAL      = "#00BEDC"   # Siemens Petrol/Cyan — primary action color
TEAL_DARK = "#009999"   # Siemens Teal — secondary
WHITE     = "#FFFFFF"
CARD_BG   = "#1B1B3A"   # Slightly lighter navy for cards
BORDER    = "rgba(0,190,220,0.35)"
GRAY_LIGHT = "#F3F3F0"

st.set_page_config(
    page_title="Siemens | Partner Onboarding",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Siemens Corporate CSS ─────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── Global ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', 'Siemens Sans', Arial, sans-serif;
    background-color: {NAVY} !important;
    color: {WHITE} !important;
  }}

  .stApp {{
    background-color: {NAVY} !important;
  }}

  /* ── Main content area ── */
  .main .block-container {{
    padding: 1.5rem 2rem 2rem 2rem;
    background-color: {NAVY};
    max-width: 1400px;
  }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
    background-color: #00001A !important;
    border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] * {{
    color: {WHITE} !important;
  }}
  [data-testid="stSidebar"] .stRadio label {{
    color: rgba(255,255,255,0.75) !important;
    padding: 0.4rem 0.5rem;
    border-radius: 4px;
    transition: all 0.2s;
    display: block;
  }}
  [data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(0,190,220,0.12);
    color: {TEAL} !important;
    cursor: pointer;
  }}

  /* ── Inputs & Selects ── */
  .stTextInput input, .stNumberInput input,
  .stSelectbox select, .stTextArea textarea {{
    background-color: {CARD_BG} !important;
    color: {WHITE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 4px !important;
  }}
  .stTextInput input:focus, .stNumberInput input:focus {{
    border-color: {TEAL} !important;
    box-shadow: 0 0 0 2px rgba(0,190,220,0.2) !important;
  }}
  div[data-baseweb="select"] > div {{
    background-color: {CARD_BG} !important;
    border-color: {BORDER} !important;
    color: {WHITE} !important;
  }}
  div[data-baseweb="select"] span {{
    color: {WHITE} !important;
  }}
  li[role="option"] {{
    background-color: {CARD_BG} !important;
    color: {WHITE} !important;
  }}
  li[role="option"]:hover {{
    background-color: rgba(0,190,220,0.15) !important;
  }}

  /* ── Buttons ── */
  .stButton > button[kind="primary"],
  .stButton > button[data-testid="baseButton-primary"] {{
    background-color: {TEAL} !important;
    color: {NAVY} !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 0px !important;
    padding: 0.5rem 1.5rem !important;
    letter-spacing: 0.03em;
    transition: all 0.2s !important;
  }}
  .stButton > button[kind="primary"]:hover {{
    background-color: #00D4F5 !important;
    transform: translateY(-1px);
  }}
  .stButton > button[kind="secondary"],
  .stButton > button[data-testid="baseButton-secondary"],
  .stButton > button:not([kind="primary"]) {{
    background-color: transparent !important;
    color: {WHITE} !important;
    border: 1px solid {WHITE} !important;
    font-weight: 500 !important;
    border-radius: 0px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
  }}
  .stButton > button:not([kind="primary"]):hover {{
    background-color: rgba(255,255,255,0.08) !important;
    border-color: {TEAL} !important;
    color: {TEAL} !important;
  }}

  /* ── Download button ── */
  .stDownloadButton > button {{
    background-color: {TEAL} !important;
    color: {NAVY} !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 0px !important;
  }}

  /* ── Metrics ── */
  [data-testid="metric-container"] {{
    background-color: {CARD_BG} !important;
    border: 1px solid {BORDER};
    border-left: 3px solid {TEAL} !important;
    border-radius: 0px !important;
    padding: 1rem 1.2rem !important;
  }}
  [data-testid="metric-container"] label {{
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {WHITE} !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
  }}

  /* ── Dataframe / Table ── */
  .stDataFrame, [data-testid="stDataFrame"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 0px !important;
  }}
  .stDataFrame thead tr th {{
    background-color: {TEAL_DARK} !important;
    color: {WHITE} !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }}
  .stDataFrame tbody tr:nth-child(even) td {{
    background-color: rgba(27,27,58,0.6) !important;
  }}
  .stDataFrame tbody tr:hover td {{
    background-color: rgba(0,190,220,0.08) !important;
  }}
  iframe[title="st_aggrid.agGrid"] {{
    border: 1px solid {BORDER};
  }}

  /* ── Alerts ── */
  .stSuccess {{ background-color: rgba(0,190,220,0.12) !important; border-left: 3px solid {TEAL} !important; border-radius: 0 !important; color: {WHITE} !important; }}
  .stError   {{ background-color: rgba(220,53,69,0.12) !important;  border-left: 3px solid #dc3545 !important; border-radius: 0 !important; color: {WHITE} !important; }}
  .stWarning {{ background-color: rgba(255,193,7,0.12) !important;  border-left: 3px solid #ffc107 !important; border-radius: 0 !important; color: {WHITE} !important; }}
  .stInfo    {{ background-color: rgba(0,190,220,0.08) !important;  border-left: 3px solid {TEAL} !important; border-radius: 0 !important; color: {WHITE} !important; }}

  /* ── Expander ── */
  .streamlit-expanderHeader {{
    background-color: {CARD_BG} !important;
    color: {WHITE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0 !important;
  }}
  .streamlit-expanderContent {{
    background-color: #12122A !important;
    border: 1px solid {BORDER} !important;
    border-top: none !important;
  }}

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {{
    background-color: transparent !important;
    border-bottom: 1px solid {BORDER};
    gap: 0;
  }}
  .stTabs [data-baseweb="tab"] {{
    background-color: transparent !important;
    color: rgba(255,255,255,0.55) !important;
    border-radius: 0 !important;
    padding: 0.6rem 1.4rem;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
  }}
  .stTabs [aria-selected="true"] {{
    color: {TEAL} !important;
    border-bottom: 2px solid {TEAL} !important;
    background-color: transparent !important;
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    color: {WHITE} !important;
  }}

  /* ── Divider ── */
  hr {{
    border-color: {BORDER} !important;
    margin: 1rem 0 !important;
  }}

  /* ── Form ── */
  [data-testid="stForm"] {{
    background-color: {CARD_BG};
    padding: 1.5rem;
    border: 1px solid {BORDER};
    border-radius: 0;
  }}

  /* ── Spinner ── */
  .stSpinner > div {{
    border-top-color: {TEAL} !important;
  }}

  /* ── Caption / small text ── */
  .stCaption, caption, small {{
    color: rgba(255,255,255,0.5) !important;
  }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: {NAVY}; }}
  ::-webkit-scrollbar-thumb {{ background: {TEAL_DARK}; border-radius: 3px; }}

  /* ── Page title H1/H2/H3 ── */
  h1, h2, h3, h4 {{ color: {WHITE} !important; }}

  /* ── Number input arrows ── */
  button[data-testid="stNumberInput-StepUp"],
  button[data-testid="stNumberInput-StepDown"] {{
    background-color: {CARD_BG} !important;
    color: {WHITE} !important;
    border-color: {BORDER} !important;
  }}

  /* ── Siemens header bar ── */
  .siemens-topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #00001A;
    padding: 0.75rem 2rem;
    border-bottom: 2px solid {TEAL};
    margin: -1.5rem -2rem 1.5rem -2rem;
  }}
  .siemens-logo {{
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    color: {WHITE};
    text-transform: uppercase;
  }}
  .siemens-logo span {{
    color: {TEAL};
  }}
  .siemens-app-title {{
    font-size: 0.85rem;
    color: rgba(255,255,255,0.6);
    font-weight: 400;
    letter-spacing: 0.04em;
  }}

  /* ── Section header ── */
  .section-header {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {WHITE};
    border-left: 4px solid {TEAL};
    padding-left: 0.75rem;
    margin-bottom: 1.25rem;
    letter-spacing: 0.01em;
  }}

  /* ── Stat card ── */
  .stat-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-top: 3px solid {TEAL};
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
  }}
  .stat-card .label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.5);
    margin-bottom: 0.3rem;
  }}
  .stat-card .value {{
    font-size: 2rem;
    font-weight: 700;
    color: {WHITE};
    line-height: 1;
  }}
  .stat-card .sub {{
    font-size: 0.78rem;
    color: {TEAL};
    margin-top: 0.3rem;
  }}

  /* ── Status badge ── */
  .badge {{
    display: inline-block;
    padding: 0.15rem 0.55rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-radius: 2px;
  }}
  .badge-teal  {{ background: rgba(0,190,220,0.18); color: {TEAL}; border: 1px solid {TEAL}; }}
  .badge-green {{ background: rgba(0,200,100,0.15); color: #00C864; border: 1px solid #00C864; }}
  .badge-red   {{ background: rgba(220,53,69,0.15); color: #FF4B6E; border: 1px solid #FF4B6E; }}
  .badge-gray  {{ background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.2); }}

  /* ── Sidebar logo area ── */
  .sidebar-logo {{
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    color: {WHITE};
    text-transform: uppercase;
    margin-bottom: 0.2rem;
  }}
  .sidebar-subtitle {{
    font-size: 0.72rem;
    color: rgba(255,255,255,0.45);
    letter-spacing: 0.04em;
    margin-bottom: 1rem;
    text-transform: uppercase;
  }}
  .sidebar-divider {{
    border: none;
    border-top: 1px solid rgba(0,190,220,0.25);
    margin: 0.75rem 0 1rem 0;
  }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _api(method: str, path: str, **kwargs):
    try:
        return getattr(requests, method)(f"{API_BASE}{path}", timeout=10, **kwargs)
    except requests.ConnectionError:
        st.error("API-Server nicht erreichbar. Backend starten: `python main.py`")
        return None


def _section(title: str):
    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)


def _badge(text: str, kind: str = "teal") -> str:
    return f"<span class='badge badge-{kind}'>{text}</span>"


STATUS_BADGE = {
    "IN_PROGRESS":   ("gray",  "In Bearbeitung"),
    "PARTNER_FINDER":("teal",  "Partner Finder"),
    "ELIGIBILITY":   ("teal",  "Eligibility"),
    "DAMEX":         ("teal",  "DAMEX"),
    "COMPLIANCE":    ("teal",  "Compliance"),
    "PRE_APPROVED":  ("green", "Vorab genehmigt"),
    "REJECTED":      ("red",   "Abgelehnt"),
    "ARCHIVED":      ("gray",  "Archiviert"),
}
ELIG_BADGE = {
    "QUALIFIED":             ("green", "Qualifiziert"),
    "REJECTED":              ("red",   "Abgelehnt"),
    "INVESTIGATION_REQUIRED":("teal",  "Prüfung erforderlich"),
}


# ── Pages ─────────────────────────────────────────────────────────────────────
def dashboard_page():
    _section("Dashboard")

    resp = _api("get", "/partners/stats/summary")
    if not resp or resp.status_code != 200:
        st.warning("Statistiken konnten nicht geladen werden.")
        return

    stats = resp.json()
    total        = stats.get("total", 0)
    by_status    = stats.get("by_status", {})
    by_eligibility = stats.get("by_eligibility", {})

    approved  = by_status.get("PRE_APPROVED", 0)
    rejected  = by_status.get("REJECTED", 0)
    qualified = by_eligibility.get("QUALIFIED", 0)
    active    = total - approved - rejected

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, sub, color in [
        (c1, "Partner Leads gesamt", total,     "Alle Einträge",        TEAL),
        (c2, "Vorab genehmigt",      approved,  "PRE_APPROVED",         "#00C864"),
        (c3, "In Bearbeitung",       active,    "Aktive Workflows",     TEAL),
        (c4, "Abgelehnt",            rejected,  "REJECTED",             "#FF4B6E"),
    ]:
        col.markdown(f"""
        <div class='stat-card'>
          <div class='label'>{label}</div>
          <div class='value' style='color:{color}'>{value}</div>
          <div class='sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    ca, cb = st.columns(2)
    with ca:
        st.markdown("<div style='font-weight:600;font-size:0.9rem;text-transform:uppercase;"
                    f"letter-spacing:0.08em;color:rgba(255,255,255,0.6);margin-bottom:0.75rem;'>Status-Verteilung</div>",
                    unsafe_allow_html=True)
        if by_status:
            df_s = pd.DataFrame(list(by_status.items()), columns=["Status", "Anzahl"])
            st.bar_chart(df_s.set_index("Status"), color=TEAL)

    with cb:
        st.markdown("<div style='font-weight:600;font-size:0.9rem;text-transform:uppercase;"
                    f"letter-spacing:0.08em;color:rgba(255,255,255,0.6);margin-bottom:0.75rem;'>Eligibility-Verteilung</div>",
                    unsafe_allow_html=True)
        if by_eligibility:
            df_e = pd.DataFrame(list(by_eligibility.items()), columns=["Entscheidung", "Anzahl"])
            st.bar_chart(df_e.set_index("Entscheidung"), color=TEAL_DARK)


def partner_list_page():
    _section("Partner Leads")

    col_s, col_f, col_l = st.columns([3, 2, 1])
    with col_s:
        search = st.text_input("Suche (Name, E-Mail, Unternehmen)", placeholder="Suchbegriff eingeben …", key="search_q")
    with col_f:
        status_filter = st.selectbox("Status Filter", ["Alle", "IN_PROGRESS", "PARTNER_FINDER",
                                                        "ELIGIBILITY", "DAMEX", "COMPLIANCE",
                                                        "PRE_APPROVED", "REJECTED", "ARCHIVED"])
    with col_l:
        limit = st.selectbox("Anzeigen", [50, 100, 200, 500], index=1)

    params   = {"limit": limit}
    endpoint = "/partners/"
    if search:
        params["search"] = search
    if status_filter != "Alle":
        endpoint = f"/partners/status/{status_filter}"

    resp = _api("get", endpoint, params=params)
    if not resp or resp.status_code != 200:
        st.warning("Daten konnten nicht geladen werden.")
        return

    data = resp.json()
    if not data:
        st.info("Keine Einträge gefunden.")
        return

    df = pd.DataFrame(data)
    cols_show = ["ID", "CompanyName", "FirstName", "LastName", "Email",
                 "Country", "LeadStatus", "EligibilityDecision", "PartnershipType"]
    existing  = [c for c in cols_show if c in df.columns]
    st.dataframe(
        df[existing],
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID":                  st.column_config.NumberColumn("ID",        width="small"),
            "CompanyName":         st.column_config.TextColumn("Unternehmen", width="medium"),
            "FirstName":           st.column_config.TextColumn("Vorname",     width="small"),
            "LastName":            st.column_config.TextColumn("Nachname",    width="small"),
            "Email":               st.column_config.TextColumn("E-Mail",      width="medium"),
            "Country":             st.column_config.TextColumn("Land",        width="small"),
            "LeadStatus":          st.column_config.TextColumn("Status",      width="medium"),
            "EligibilityDecision": st.column_config.TextColumn("Eligibility", width="medium"),
            "PartnershipType":     st.column_config.TextColumn("Typ",         width="medium"),
        },
    )
    st.caption(f"{len(df)} Einträge angezeigt")

    st.divider()
    st.markdown("<div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;"
                "color:rgba(255,255,255,0.5);margin-bottom:0.5rem;'>Export</div>", unsafe_allow_html=True)
    ce, cj, cx = st.columns(3)
    with ce:
        if st.button("CSV exportieren", key="exp_csv"):
            r = _api("get", "/partners/export/csv")
            if r:
                st.download_button("CSV herunterladen", r.content, "partners.csv", "text/csv", key="dl_csv")
    with cj:
        if st.button("JSON exportieren", key="exp_json"):
            r = _api("get", "/partners/export/json")
            if r:
                st.download_button("JSON herunterladen", r.content, "partners.json", "application/json", key="dl_json")
    with cx:
        if st.button("Excel exportieren", key="exp_xlsx"):
            r = _api("get", "/partners/export/xlsx")
            if r:
                st.download_button("Excel herunterladen", r.content, "partners.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx")


def add_partner_page():
    _section("Neuen Partner Lead erfassen")

    with st.form("add_partner", clear_on_submit=True):
        st.markdown("<div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;"
                    "color:rgba(255,255,255,0.45);margin-bottom:0.75rem;'>Kontaktdaten</div>",
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            first_name = st.text_input("Vorname *")
            email      = st.text_input("E-Mail *")
        with c2:
            last_name  = st.text_input("Nachname *")
            partnership_type = st.selectbox("Partnerschaftstyp *",
                                            ["Distribution Partner", "Solution Partner", "Technology Partner"])
        with c3:
            company_name = st.text_input("Unternehmen *")
            founding_year = st.number_input("Gründungsjahr", min_value=1900, max_value=2025, value=2010)

        st.divider()
        st.markdown("<div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;"
                    "color:rgba(255,255,255,0.45);margin-bottom:0.75rem;'>Adresse</div>",
                    unsafe_allow_html=True)
        ca, cb, cc, cd = st.columns(4)
        with ca:
            country = st.selectbox("Land *", ["Deutschland", "Österreich", "Schweiz", "Frankreich",
                                               "Italien", "Spanien", "Niederlande", "Polen",
                                               "Germany", "Austria", "Switzerland", "France",
                                               "Italy", "Spain", "Netherlands", "Poland"])
        with cb:
            city   = st.text_input("Stadt")
        with cc:
            street = st.text_input("Straße & Hausnummer")
        with cd:
            postal_code = st.text_input("Postleitzahl")

        st.divider()
        st.markdown("<div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;"
                    "color:rgba(255,255,255,0.45);margin-bottom:0.75rem;'>Unternehmenskennzahlen</div>",
                    unsafe_allow_html=True)
        cm1, cm2, cm3, cm4 = st.columns(4)
        with cm1:
            annual_revenue = st.number_input("Jahresumsatz (€)", min_value=0.0, value=500_000.0, step=50_000.0,
                                             format="%.0f")
        with cm2:
            total_employees = st.number_input("Mitarbeiter gesamt", min_value=1, value=50)
        with cm3:
            sales_employees = st.number_input("Vertrieb", min_value=0, value=10)
        with cm4:
            technical_employees = st.number_input("Technik", min_value=0, value=15)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Lead einreichen", type="primary")

    if submitted:
        country_map = {
            "Deutschland": "Germany", "Österreich": "Austria", "Schweiz": "Switzerland",
            "Frankreich": "France",   "Italien": "Italy",      "Spanien": "Spain",
            "Niederlande": "Netherlands", "Polen": "Poland",
        }
        payload = {
            "first_name": first_name, "last_name": last_name, "email": email,
            "company_name": company_name, "partnership_type": partnership_type,
            "country": country_map.get(country, country),
            "city": city, "street": street, "postal_code": postal_code,
            "founding_year": int(founding_year), "annual_revenue": float(annual_revenue),
            "total_employees": int(total_employees), "sales_employees": int(sales_employees),
            "technical_employees": int(technical_employees),
        }
        r = _api("post", "/partners/", json=payload)
        if r and r.status_code in (200, 201):
            st.success(f"Partner Lead erfolgreich angelegt — ID: **{r.json().get('ID')}**")
        else:
            err = r.json().get("detail", "Unbekannter Fehler") if r else "Server nicht erreichbar"
            st.error(f"Fehler: {err}")


def workflow_page():
    _section("Workflow Management")

    lead_id = st.number_input("Partner Lead ID", min_value=1, step=1, key="wf_id")

    if not lead_id:
        return

    resp = _api("get", f"/partners/{lead_id}")
    if not resp:
        return

    if resp.status_code == 404:
        st.warning(f"Kein Partner mit ID {lead_id} gefunden.")
        return

    lead = resp.json()
    status_raw = lead.get("LeadStatus", "-")
    elig_raw   = lead.get("EligibilityDecision") or "—"

    s_kind, s_label = STATUS_BADGE.get(status_raw, ("gray", status_raw))
    e_kind, e_label = ELIG_BADGE.get(elig_raw, ("gray", elig_raw))

    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-top:3px solid {TEAL};
                padding:1.2rem 1.5rem;margin-bottom:1.25rem;'>
      <div style='display:flex;gap:2rem;align-items:center;flex-wrap:wrap;'>
        <div>
          <div style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:rgba(255,255,255,0.4);margin-bottom:0.25rem;'>Unternehmen</div>
          <div style='font-size:1.05rem;font-weight:700;'>{lead.get("CompanyName","—")}</div>
          <div style='font-size:0.82rem;color:rgba(255,255,255,0.5);'>
            {lead.get("FirstName","")} {lead.get("LastName","")} · {lead.get("Country","—")}
          </div>
        </div>
        <div>
          <div style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:rgba(255,255,255,0.4);margin-bottom:0.35rem;'>Workflow-Status</div>
          {_badge(s_label, s_kind)}
        </div>
        <div>
          <div style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:rgba(255,255,255,0.4);margin-bottom:0.35rem;'>Eligibility</div>
          {_badge(e_label, e_kind)}
        </div>
        <div>
          <div style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:rgba(255,255,255,0.4);margin-bottom:0.25rem;'>Jahresumsatz</div>
          <div style='font-size:1rem;font-weight:600;color:{TEAL};'>
            EUR {lead.get("AnnualRevenue", 0):,.0f}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("Workflow voranschreiten", type="primary", key="wf_advance"):
            r = _api("post", f"/workflow/{lead_id}/advance")
            if r and r.status_code == 200:
                new_status = r.json().get("lead", {}).get("LeadStatus", "—")
                st.success(f"Status geändert → **{new_status}**")
                st.rerun()
            else:
                st.error(r.json().get("detail") if r else "Fehler")

    with col_b:
        if st.button("Vollständigen Workflow starten", key="wf_full"):
            with st.spinner("Workflow wird ausgeführt …"):
                r = _api("post", f"/workflow/{lead_id}/run-full")
            if r and r.status_code == 200:
                final = r.json().get("lead", {}).get("LeadStatus", "—")
                st.success(f"Workflow abgeschlossen → **{final}**")
                st.rerun()
            else:
                st.error(r.json().get("detail") if r else "Fehler")

    with col_c:
        if st.button("KI-Analyse starten", key="wf_ai"):
            with st.spinner("KI analysiert …"):
                r = _api("post", f"/workflow/{lead_id}/ai-analysis")
            if r and r.status_code == 200:
                ai = r.json()
                st.info(f"Business Potential: **{ai.get('business_potential_score')}/100**")
                st.info(f"Risiko-Score: **{ai.get('risk_score')}/100**")
                st.info(f"Empfehlung: **{ai.get('recommendation')}**")
            else:
                st.error(r.json().get("detail") if r else "Fehler")

    st.divider()

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        with st.expander("✅  Lead manuell freigeben"):
            st.markdown(
                f"<div style='font-size:0.8rem;color:rgba(255,255,255,0.5);margin-bottom:0.75rem;'>"
                "Setzt den Status unabhängig vom aktuellen Workflow-Stand direkt auf "
                f"<span style='color:{TEAL};font-weight:600;'>PRE_APPROVED</span>. "
                "Begründung wird im Datensatz gespeichert.</div>",
                unsafe_allow_html=True,
            )
            note = st.text_input(
                "Begründung / Freigabe-Notiz *",
                key="approve_note",
                placeholder="Z.B. Ausnahme nach Rücksprache mit Vertriebsleitung …",
            )
            approver = st.text_input(
                "Freigegeben durch (Name)",
                key="approve_by",
                placeholder="Vor- und Nachname …",
            )
            if st.button("Freigabe bestätigen", type="primary", key="wf_approve"):
                if note:
                    full_note = f"{note}" + (f" — {approver}" if approver else "")
                    r = _api("post", f"/workflow/{lead_id}/approve", params={"note": full_note})
                    if r and r.status_code == 200:
                        st.success("Lead wurde manuell auf **PRE_APPROVED** gesetzt.")
                        st.rerun()
                    else:
                        err = r.json().get("detail") if r else "Server nicht erreichbar"
                        st.error(f"Fehler: {err}")
                else:
                    st.warning("Bitte eine Begründung angeben.")

    with col_exp2:
        with st.expander("❌  Lead ablehnen"):
            reason = st.text_input("Ablehnungsgrund *", key="reject_reason",
                                   placeholder="Grund für die Ablehnung eingeben …")
            if st.button("Ablehnung bestätigen", type="secondary", key="wf_reject"):
                if reason:
                    r = _api("post", f"/workflow/{lead_id}/reject", params={"reason": reason})
                    if r and r.status_code == 200:
                        st.success("Lead wurde abgelehnt.")
                        st.rerun()
                    else:
                        st.error(r.json().get("detail") if r else "Fehler")
                else:
                    st.warning("Bitte Ablehnungsgrund angeben.")


def reports_page():
    _section("PDF-Berichte")

    c1, c2 = st.columns(2)
    with c1:
        lead_id = st.number_input("Partner Lead ID", min_value=1, step=1, key="rep_id")
    with c2:
        report_type = st.selectbox("Berichtstyp", [
            ("Partner-Historie",  "partner-history"),
            ("Eligibility",       "eligibility"),
            ("DAMEX-Prüfung",     "damex"),
            ("Compliance",        "compliance"),
        ], format_func=lambda x: x[0])

    if st.button("Bericht generieren", type="primary", key="rep_gen"):
        with st.spinner("PDF wird erstellt …"):
            r = _api("get", f"/reports/{lead_id}/{report_type[1]}")
        if r and r.status_code == 200:
            disposition = r.headers.get("Content-Disposition", f"report_{lead_id}.pdf")
            filename    = disposition.split("filename=")[-1].strip('"')
            st.success("Bericht erfolgreich erstellt!")
            st.download_button(
                label=f"{report_type[0]}-Bericht herunterladen",
                data=r.content,
                file_name=filename,
                mime="application/pdf",
                key="rep_dl",
            )
        else:
            err = r.json().get("detail") if r else "Server nicht erreichbar"
            st.error(f"Fehler beim Erstellen: {err}")


def admin_page():
    _section("Administration")

    tab_backup, tab_batch = st.tabs(["Datenbank-Backups", "Batch-Verarbeitung"])

    with tab_backup:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown("<div style='font-size:0.8rem;color:rgba(255,255,255,0.5);"
                        "margin-bottom:0.75rem;'>Vorhandene Backups</div>", unsafe_allow_html=True)
            r = _api("get", "/partners/backups/list")
            if r and r.status_code == 200:
                backups = r.json()
                if backups:
                    st.dataframe(pd.DataFrame(backups), use_container_width=True, hide_index=True)
                else:
                    st.info("Noch keine Backups vorhanden.")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Backup jetzt erstellen", type="primary", key="backup_now"):
                r = _api("post", "/partners/backups/create")
                if r and r.status_code == 200:
                    st.success(f"Backup erstellt")
                else:
                    st.error("Backup fehlgeschlagen.")

    with tab_batch:
        st.markdown("<div style='font-size:0.82rem;color:rgba(255,255,255,0.55);margin-bottom:1rem;'>"
                    "Batch-Verarbeitung führt Prüfungen auf allen qualifizierten Leads gleichzeitig aus."
                    "</div>", unsafe_allow_html=True)

        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown("<div style='background:{CARD_BG};border:1px solid {BORDER};"
                        "padding:1rem;margin-bottom:0.5rem;'></div>".format(CARD_BG=CARD_BG, BORDER=BORDER),
                        unsafe_allow_html=True)
            st.markdown("**Eligibility-Check**")
            st.caption("Prüft alle Leads im Status PARTNER_FINDER")
            if st.button("Batch Eligibility", type="primary", key="batch_elig"):
                with st.spinner("Wird ausgeführt …"):
                    r = _api("post", "/workflow/batch/eligibility")
                if r and r.status_code == 200:
                    res = r.json()
                    st.success(f"Fertig — {res.get('total', 0)} Leads verarbeitet")
        with b2:
            st.markdown("**DAMEX-Check**")
            st.caption("Prüft alle Leads im Status ELIGIBILITY")
            if st.button("Batch DAMEX", type="primary", key="batch_damex"):
                with st.spinner("Wird ausgeführt …"):
                    r = _api("post", "/workflow/batch/damex")
                if r and r.status_code == 200:
                    res = r.json()
                    st.success(f"Fertig — {res.get('total', 0)} Leads verarbeitet")
        with b3:
            st.markdown("**Compliance-Check**")
            st.caption("Prüft alle Leads im Status DAMEX")
            if st.button("Batch Compliance", type="primary", key="batch_comp"):
                with st.spinner("Wird ausgeführt …"):
                    r = _api("post", "/workflow/batch/compliance")
                if r and r.status_code == 200:
                    res = r.json()
                    st.success(f"Fertig — {res.get('total', 0)} Leads verarbeitet")


# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar_nav() -> str:
    with st.sidebar:
        st.markdown(f"""
        <div class='sidebar-logo'>SIEMENS</div>
        <div class='sidebar-subtitle'>Partner Onboarding System</div>
        <hr class='sidebar-divider'>
        """, unsafe_allow_html=True)

        pages = {
            "Dashboard":          "📊",
            "Partner Leads":      "🏢",
            "Lead erfassen":      "➕",
            "Workflow":           "⚙️",
            "Berichte":           "📄",
            "Administration":     "🔧",
        }

        # Build labeled options
        labels = [f"{icon}  {name}" for name, icon in pages.items()]
        keys   = list(pages.keys())

        choice = st.radio("Navigation", labels, label_visibility="collapsed")
        idx    = labels.index(choice)

        st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:0.68rem;color:rgba(255,255,255,0.3);letter-spacing:0.04em;'>"
            f"Siemens AG · Internes System<br>v1.0.0 · Partner Automation"
            f"</div>",
            unsafe_allow_html=True,
        )

        return keys[idx]


# ── Top bar ───────────────────────────────────────────────────────────────────
def topbar():
    st.markdown(f"""
    <div class='siemens-topbar'>
      <div class='siemens-logo'>SIEMENS</div>
      <div class='siemens-app-title'>Partner Eligibility &amp; Onboarding Automation</div>
    </div>
    """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    topbar()
    page = sidebar_nav()

    dispatch = {
        "Dashboard":      dashboard_page,
        "Partner Leads":  partner_list_page,
        "Lead erfassen":  add_partner_page,
        "Workflow":       workflow_page,
        "Berichte":       reports_page,
        "Administration": admin_page,
    }
    dispatch.get(page, dashboard_page)()


if __name__ == "__main__":
    main()
