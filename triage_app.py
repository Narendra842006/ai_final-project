"""
Smart Patient Triage System — Main Application
Professional UI · Multi-language · AI Chat · Analytics · Patient Details
"""

import streamlit as st
import PyPDF2
import io
import uuid
import pandas as pd
import numpy as np
from datetime import datetime

import utils
import config
import chatbot

# ── Database imports ──────────────────────────────────────────────────────────
from backend.database import init_db, SessionLocal, Patient, HospitalQueue, AuditLog

init_db()

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Patient Triage System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session-state defaults ────────────────────────────────────────────────────
_defaults = {
    "authenticated": False,
    "email": "",
    "role": "",
    "language": "English",
    "patients": [],
    "login_step": 1,
    "selected_role": None,
    "patient_age": 30,
    "patient_gender": "Male",
    "vitals": {"heart_rate": 75.0, "bp_systolic": 120.0, "bp_diastolic": 80.0, "temperature": 98.6},
    "selected_symptoms": [],
    "show_prediction": False,
    "last_prediction": None,
    "chat_history": [],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "chatbot" not in st.session_state:
    st.session_state.chatbot = chatbot.MedicalChatbot("English")


# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def save_patient_to_db(patient_data: dict, prediction: dict):
    db = SessionLocal()
    try:
        pid = str(uuid.uuid4())
        patient = Patient(
            id=pid,
            email=st.session_state.email,
            age=patient_data["Age"],
            gender=patient_data["Gender"],
            vitals=st.session_state.vitals,
            symptoms=patient_data.get("full_symptoms", []),
            risk_level=prediction["risk_level"],
            priority_score=prediction["risk_score"],
            department=_infer_department(prediction["risk_level"], patient_data.get("full_symptoms", [])),
            ai_confidence=prediction["confidence"],
            feature_importance=prediction["feature_importance"],
        )
        db.add(patient)

        vs = st.session_state.vitals
        vitals_summary = f"HR:{int(vs['heart_rate'])} BP:{int(vs['bp_systolic'])}/{int(vs['bp_diastolic'])} T:{vs['temperature']:.1f}"
        queue = HospitalQueue(
            patient_id=pid,
            email=st.session_state.email,
            priority_score=prediction["risk_score"],
            risk_level=prediction["risk_level"],
            department=patient.department,
            vitals_summary=vitals_summary,
            immediate=prediction["immediate"],
        )
        db.add(queue)

        audit = AuditLog(
            id=str(uuid.uuid4()),
            patient_id=pid,
            action="triage_assessment",
            risk_level=prediction["risk_level"],
            priority_score=prediction["risk_score"],
            rationale=f"AI triage – {prediction['risk_level']} risk ({prediction['risk_score']:.0f}/100)",
            feature_importance=prediction["feature_importance"],
            user_email=st.session_state.email,
            system_version="2.0",
        )
        db.add(audit)
        db.commit()
        return pid
    except Exception as e:
        db.rollback()
        st.error(f"Database error: {e}")
        return None
    finally:
        db.close()


def _infer_department(risk_level: str, symptoms: list) -> str:
    cardiac = ["chest pain", "chest", "heart", "palpitations"]
    if any(any(kw in s.lower() for kw in cardiac) for s in symptoms):
        return "Cardiology"
    if risk_level == "HIGH":
        return "Emergency"
    return "General Medicine"


def load_patients_from_db():
    db = SessionLocal()
    try:
        records = db.query(Patient).order_by(Patient.created_at.desc()).all()
        patients = []
        for r in records:
            sym = r.symptoms if isinstance(r.symptoms, list) else []
            vit = r.vitals if isinstance(r.vitals, dict) else {}
            patients.append({
                "ID": len(patients) + 1,
                "patient_id": r.id,
                "email": r.email,
                "Name": r.email.split("@")[0].title(),
                "Age": r.age,
                "Gender": r.gender,
                "Heart Rate": int(vit.get("heart_rate", 75)),
                "BP Systolic": int(vit.get("bp_systolic", 120)),
                "BP Diastolic": int(vit.get("bp_diastolic", 80)),
                "BP": f"{int(vit.get('bp_systolic', 120))}/{int(vit.get('bp_diastolic', 80))}",
                "Temp": round(vit.get("temperature", 98.6), 1),
                "Symptoms": ", ".join(sym[:3]) + ("..." if len(sym) > 3 else ""),
                "full_symptoms": sym,
                "Risk Score": round(r.priority_score, 1),
                "Risk Level": r.risk_level,
                "Immediate": r.priority_score >= 70 and any("chest" in s.lower() for s in sym),
                "confidence": r.ai_confidence,
                "feature_importance": r.feature_importance if isinstance(r.feature_importance, dict) else {},
                "department": r.department,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            })
        return patients
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}

/* Hide Streamlit chrome */
#MainMenu,footer,header,[data-testid="collapsedControl"]{display:none!important}
section[data-testid="stSidebar"]{display:none!important}
.block-container{padding-top:.5rem!important;max-width:1180px!important}

.stApp{background:#f0f2f6!important}

/* ── All text dark ── */
label, .stSelectbox label, .stMultiSelect label, .stNumberInput label,
.stTextInput label, .stFileUploader label,
[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li, .stCaption p{
    color:#1a1a2e!important;
}

/* ── Selectbox – white bg, dark text ── */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"]{
    background:#fff!important;border:1px solid #d0d5dd!important;border-radius:8px!important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stMultiSelect"] [data-baseweb="select"] span,
[data-testid="stMultiSelect"] [data-baseweb="select"] div{color:#1a1a2e!important}
[data-testid="stSelectbox"] svg,[data-testid="stMultiSelect"] svg{fill:#1a1a2e!important}

/* Drop-down menu */
[data-baseweb="menu"] li,[data-baseweb="menu"] ul,[role="listbox"] li,[role="option"]{background:#fff!important;color:#1a1a2e!important}
[role="option"]:hover,[data-baseweb="menu"] li:hover{background:#e8f0fe!important}

/* ── Number/text inputs ── */
.stNumberInput input,.stTextInput input{color:#1a1a2e!important;background:#fff!important;border:1px solid #d0d5dd!important}
.stNumberInput button{background:#fff!important;color:#1a1a2e!important;border:1px solid #d0d5dd!important}
.stNumberInput button:hover{background:#e8f0fe!important}
.stNumberInput button svg{fill:#1a1a2e!important}

/* ── File uploader ── */
[data-testid="stFileUploader"]{background:#fff!important;border-radius:10px!important}
[data-testid="stFileUploader"] section{background:#f8f9fb!important;border:2px dashed #c0c8d4!important;border-radius:10px!important}
[data-testid="stFileUploader"] section div,[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small,[data-testid="stFileUploader"] section p{color:#555!important}
[data-testid="stFileUploader"] button{background:#0066FF!important;color:#fff!important;border:none!important;border-radius:8px!important}

/* ── Buttons ── */
.stButton>button{border-radius:8px;font-weight:600;transition:all .2s}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0066FF,#00B4D8)!important;border:none;color:#fff!important}
.stButton>button:not([kind="primary"]){background:#fff!important;color:#1a1a2e!important;border:1px solid #d0d5dd!important}
.stButton>button:not([kind="primary"]):hover{background:#f0f2f5!important}

/* ── Tabs ── */
button[data-baseweb="tab"]{color:#1a1a2e!important;font-weight:600!important;font-size:.92rem!important}
button[data-baseweb="tab"][aria-selected="true"]{color:#0052CC!important;border-bottom-color:#0052CC!important}

/* ── Metrics & Dataframe ── */
[data-testid="stMetricValue"]{color:#0052CC!important}
[data-testid="stMetricLabel"]{color:#555!important}
.stDataFrame td,.stDataFrame th{color:#1a1a2e!important}

/* ── MultiSelect tags ── */
[data-testid="stMultiSelect"] [data-baseweb="tag"]{background:#e8f0fe!important;color:#0052CC!important}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span{color:#0052CC!important}

/* ── Expander ── */
[data-testid="stExpander"]{background:#fff!important;border:1px solid #e5e9f0!important;border-radius:10px!important}
details summary span{color:#1a1a2e!important}

/* ── Language selector special styling ── */
.lang-select [data-baseweb="select"]{
    min-width:140px;background:rgba(255,255,255,.92)!important;border:2px solid #0066FF!important;border-radius:10px!important;
}
.lang-select [data-baseweb="select"] span{color:#0052CC!important;font-weight:700!important;font-size:.9rem!important}
.lang-select [data-baseweb="select"] svg{fill:#0052CC!important}
.lang-select label,.lang-select [data-testid="stWidgetLabel"] p{color:#0052CC!important;font-weight:700!important;font-size:.85rem!important}

/* ── Top Nav ── */
.topnav{
    display:flex;justify-content:space-between;align-items:center;
    background:linear-gradient(135deg,#0052CC 0%,#0066FF 50%,#00B4D8 100%);
    padding:.7rem 1.5rem;border-radius:14px;margin-bottom:1rem;
    box-shadow:0 4px 20px rgba(0,80,200,.22);
}
.topnav-brand{color:#fff;font-weight:700;font-size:1.12rem}
.topnav-right{display:flex;align-items:center;gap:.9rem}
.topnav-pill{background:rgba(255,255,255,.2);padding:.25rem .8rem;border-radius:20px;font-size:.8rem;font-weight:500;color:#fff!important}

/* ── Cards ── */
.card{background:#fff;border-radius:14px;padding:1.5rem 1.6rem;box-shadow:0 2px 12px rgba(0,0,0,.05);border:1px solid #e5e9f0;margin-bottom:1.1rem}
.card-title{font-size:1.12rem;font-weight:700;color:#1a1a2e!important;margin-bottom:.8rem;display:flex;align-items:center;gap:.4rem}

/* ── Prediction result ── */
.pred-card{border-radius:16px;padding:1.6rem 2rem;text-align:center;margin:1rem 0}
.pred-high{background:linear-gradient(135deg,#e53935,#ff6f61);color:#fff!important}
.pred-medium{background:linear-gradient(135deg,#f57c00,#ffb74d);color:#fff!important}
.pred-low{background:linear-gradient(135deg,#43a047,#81c784);color:#fff!important}
.pred-card *{color:#fff!important}
.pred-score{font-size:2.8rem;font-weight:800;margin:.3rem 0}
.pred-label{font-size:1.1rem;font-weight:600;opacity:.95}

/* ── Feature importance bars ── */
.fi-row{margin:.4rem 0}
.fi-name{font-size:.82rem;color:#444!important;margin-bottom:2px}
.fi-track{background:#e9ecef;border-radius:8px;height:20px;overflow:hidden}
.fi-fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#0066FF,#00B4D8);
    display:flex;align-items:center;padding-left:8px;font-size:.72rem;color:#fff!important;font-weight:600;min-width:28px}

/* ── Chat ── */
.chat-hdr{background:linear-gradient(135deg,#0052CC,#00B4D8);padding:.7rem 1.2rem;font-weight:700;font-size:.95rem;display:flex;align-items:center;gap:.5rem;border-radius:14px 14px 0 0}
.chat-hdr *{color:#fff!important}
.chat-dot{width:9px;height:9px;background:#4AFF8B;border-radius:50%;display:inline-block}
.msg-user{background:linear-gradient(135deg,#0066FF,#00B4D8);padding:.55rem 1rem;border-radius:16px 16px 4px 16px;margin:.35rem 0 .35rem 4rem;font-size:.88rem;word-wrap:break-word}
.msg-user *{color:#fff!important}
.msg-bot{background:#fff;padding:.55rem 1rem;border-radius:16px 16px 16px 4px;margin:.35rem 4rem .35rem 0;font-size:.88rem;box-shadow:0 1px 4px rgba(0,0,0,.06);word-wrap:break-word}
.msg-bot *{color:#333!important}

/* ── Metric cards ── */
.metric-card{text-align:center;background:#fff;border-radius:12px;padding:1rem;box-shadow:0 2px 10px rgba(0,0,0,.04);border:1px solid #e5e9f0}
.metric-val{font-size:1.7rem;font-weight:800}
.metric-lbl{font-size:.78rem;color:#666!important;margin-top:.2rem}

/* ── Patient row ── */
.patient-row{background:#fff;border-radius:10px;padding:.8rem 1.2rem;margin:.5rem 0;box-shadow:0 1px 6px rgba(0,0,0,.04);border:1px solid #e5e9f0;display:flex;align-items:center;gap:1rem;transition:box-shadow .2s}
.patient-row:hover{box-shadow:0 4px 16px rgba(0,80,200,.12)}
.risk-badge{padding:.2rem .7rem;border-radius:12px;font-size:.75rem;font-weight:700;color:#fff!important}
.risk-HIGH{background:#e53935}.risk-MEDIUM{background:#f57c00}.risk-LOW{background:#43a047}

/* ── Detail card ── */
.detail-card{background:#fff;border-radius:14px;padding:1.4rem 1.6rem;border:1px solid #e2e6ee;box-shadow:0 3px 14px rgba(0,0,0,.06);margin:.6rem 0}
.detail-card h4{color:#0052CC!important;margin:0 0 .6rem 0}
.detail-row{display:flex;justify-content:space-between;padding:.35rem 0;border-bottom:1px solid #f0f2f5}
.detail-label{font-weight:600;color:#555!important;font-size:.88rem}
.detail-value{color:#1a1a2e!important;font-weight:500;font-size:.88rem}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp{background:linear-gradient(135deg,#0052CC 0%,#0066FF 40%,#00B4D8 100%)!important}
        .login-area label,.login-area p,.login-area span,
        .login-area [data-testid="stWidgetLabel"] p{color:#fff!important}
        .stTextInput>div>div>input{border-radius:10px;border:2px solid rgba(255,255,255,.3);
            background:rgba(255,255,255,.95)!important;font-size:1rem;padding:.75rem 1rem;color:#1a1a2e!important}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h1 style='text-align:center;color:#fff;font-size:3.2rem;margin-top:4rem;margin-bottom:.3rem'>"
        "🏥 Smart Patient Triage</h1>"
        "<p style='text-align:center;color:#e0e7ff;font-size:1.2rem;margin-bottom:2.5rem'>"
        "AI-Powered Healthcare Management</p>",
        unsafe_allow_html=True,
    )

    if st.session_state.login_step == 1:
        st.markdown("<h3 style='text-align:center;color:#fff;margin-bottom:1.5rem'>Select Your Role</h3>", unsafe_allow_html=True)
        _, c, _ = st.columns([1.2, 3, 1.2])
        with c:
            r1, r2 = st.columns(2)
            with r1:
                if st.button("👤  Patient\n\nI need medical help", key="role_patient", use_container_width=True, type="primary"):
                    st.session_state.selected_role = "Patient"
                    st.session_state.login_step = 2
                    st.rerun()
            with r2:
                if st.button("🏨  Hospital Staff\n\nI manage patient care", key="role_hospital", use_container_width=True, type="primary"):
                    st.session_state.selected_role = "Hospital"
                    st.session_state.login_step = 2
                    st.rerun()
    else:
        st.markdown(
            f"<h3 style='text-align:center;color:#fff;margin-bottom:1rem'>Login as {st.session_state.selected_role}</h3>",
            unsafe_allow_html=True,
        )
        _, c, _ = st.columns([1, 2, 1])
        with c:
            st.markdown('<div class="login-area">', unsafe_allow_html=True)
            email = st.text_input("📧 Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="login_pw")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("⬅ Back", use_container_width=True, key="back_btn"):
                    st.session_state.login_step = 1
                    st.session_state.selected_role = None
                    st.rerun()
            with b2:
                if st.button("🔐 Login", use_container_width=True, type="primary", key="login_btn"):
                    if not email or "@" not in email or "." not in email:
                        st.error("Enter a valid email address")
                    elif not password or len(password) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.email = email
                        st.session_state.role = st.session_state.selected_role
                        st.rerun()

    st.markdown(
        "<div style='text-align:center;color:#fff;margin-top:3rem;opacity:.8'>"
        "<p>Smart Patient Triage v2.0</p>"
        "<p style='font-size:.85rem'>🔒 Secure &middot; HIPAA Compliant</p></div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
#  AUTHENTICATED APP
# ══════════════════════════════════════════════════════════════════════════════
else:
    # ── Resolve language FIRST so every widget below uses it ──────────────────
    lang = st.session_state.language
    if st.session_state.chatbot.language != lang:
        st.session_state.chatbot.language = lang

    # ── Top controls row ──────────────────────────────────────────────────────
    tc1, tc2, tc3, tc4 = st.columns([2.5, 3, 2, 1.5])

    with tc1:
        st.markdown('<div class="lang-select">', unsafe_allow_html=True)
        LANG_OPTIONS = ["English", "Spanish", "Hindi", "Tamil", "Telugu"]
        new_lang = st.selectbox(
            "🌍 " + utils.translate("language", lang),
            LANG_OPTIONS,
            index=LANG_OPTIONS.index(lang),
            key="lang_sel",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        # If user changed language, persist and rerun immediately
        if new_lang != lang:
            st.session_state.language = new_lang
            st.session_state.chatbot.language = new_lang
            st.rerun()
        lang = st.session_state.language          # final resolved language

    with tc2:
        st.markdown(f"<div style='padding-top:28px;font-size:.88rem;color:#333'>📧 <b>{st.session_state.email}</b></div>", unsafe_allow_html=True)
    with tc3:
        role_label = utils.translate("patient", lang) if st.session_state.role == "Patient" else utils.translate("hospital", lang)
        st.markdown(f"<div style='padding-top:28px;font-size:.88rem;color:#333'>🎭 <b>{role_label}</b></div>", unsafe_allow_html=True)
    with tc4:
        st.markdown("<div style='padding-top:20px'></div>", unsafe_allow_html=True)
        if st.button("🚪 " + utils.translate("logout", lang), key="logout_btn", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # Gradient nav banner
    st.markdown(
        '<div class="topnav">'
        '<div class="topnav-brand">🏥 Smart Patient Triage System</div>'
        '<div class="topnav-right">'
        f'<span class="topnav-pill">📧 {st.session_state.email}</span>'
        f'<span class="topnav-pill">🎭 {st.session_state.role}</span>'
        f'<span class="topnav-pill">🌍 {lang}</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  PATIENT ROLE
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.role == "Patient":
        st.markdown(
            f"<p style='text-align:center;color:#444;margin:.2rem 0 .7rem'>"
            f"{utils.translate('welcome', lang)}, <b>{st.session_state.email.split('@')[0].title()}</b></p>",
            unsafe_allow_html=True,
        )

        tab_form, tab_records, tab_chat = st.tabs([
            "📋 " + utils.translate("patient_info", lang),
            "📁 " + utils.translate("priority_queue", lang),
            "🤖 " + utils.translate("chat_assistant", lang),
        ])

        # ─── TAB 1: Patient Assessment ───────────────────────────────────────
        with tab_form:
            if not st.session_state.show_prediction:
                st.markdown('<div class="card"><div class="card-title">📋 ' + utils.translate("patient_info", lang) + '</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    age = st.number_input(utils.translate("age", lang), 1, 120, st.session_state.patient_age, key="age_in")
                    st.session_state.patient_age = age
                with c2:
                    g_opts = [utils.translate("male", lang), utils.translate("female", lang), utils.translate("other", lang)]
                    gender = st.selectbox(utils.translate("gender", lang), g_opts, key="gender_in")
                    g_map = {g_opts[0]: "Male", g_opts[1]: "Female", g_opts[2]: "Other"}
                    st.session_state.patient_gender = g_map.get(gender, "Male")
                st.markdown("</div>", unsafe_allow_html=True)

                # Vitals
                st.markdown('<div class="card"><div class="card-title">💓 ' + utils.translate("heart_rate", lang).split("(")[0].strip() + '</div>', unsafe_allow_html=True)
                uploaded = st.file_uploader(utils.translate("upload_ehr", lang), type=["pdf"], key="pdf_up")
                if uploaded:
                    try:
                        reader = PyPDF2.PdfReader(io.BytesIO(uploaded.read()))
                        text = "".join(p.extract_text() or "" for p in reader.pages)
                        st.session_state.vitals = utils.extract_vitals_from_pdf(text)
                        st.success("✅ PDF processed — vitals auto-filled")
                    except Exception as e:
                        st.error(f"PDF error: {e}")

                c1, c2 = st.columns(2)
                with c1:
                    hr = st.number_input(utils.translate("heart_rate", lang), 30.0, 250.0, float(st.session_state.vitals["heart_rate"]), 1.0, key="hr_in")
                    st.session_state.vitals["heart_rate"] = hr
                    bps = st.number_input(utils.translate("bp_systolic", lang), 60.0, 250.0, float(st.session_state.vitals["bp_systolic"]), 1.0, key="bps_in")
                    st.session_state.vitals["bp_systolic"] = bps
                with c2:
                    bpd = st.number_input(utils.translate("bp_diastolic", lang), 40.0, 150.0, float(st.session_state.vitals["bp_diastolic"]), 1.0, key="bpd_in")
                    st.session_state.vitals["bp_diastolic"] = bpd
                    temp = st.number_input(utils.translate("temperature", lang), 90.0, 110.0, float(st.session_state.vitals["temperature"]), 0.1, key="temp_in")
                    st.session_state.vitals["temperature"] = temp
                st.markdown("</div>", unsafe_allow_html=True)

                # Symptoms
                st.markdown('<div class="card"><div class="card-title">🩺 ' + utils.translate("symptoms", lang) + '</div>', unsafe_allow_html=True)
                sym_list = config.SYMPTOMS.get(lang, config.SYMPTOMS["English"])
                selected = st.multiselect(utils.translate("symptoms", lang), sym_list, default=st.session_state.selected_symptoms, key="sym_sel")
                st.session_state.selected_symptoms = selected
                if selected:
                    st.info(f"✅ {len(selected)} symptom(s) selected")
                st.markdown("</div>", unsafe_allow_html=True)

                # Submit
                st.markdown("<br>", unsafe_allow_html=True)
                _, bc, _ = st.columns([1, 2, 1])
                with bc:
                    if st.button("🤖 " + utils.translate("submit", lang), use_container_width=True, type="primary", key="predict"):
                        if not st.session_state.selected_symptoms:
                            st.error("Please select at least one symptom.")
                        else:
                            risk_score, risk_level, fi = utils.calculate_risk_score(
                                st.session_state.patient_age,
                                st.session_state.patient_gender,
                                st.session_state.vitals,
                                st.session_state.selected_symptoms,
                            )
                            patient_data = utils.format_patient_data(
                                len(st.session_state.patients) + 1,
                                st.session_state.email,
                                st.session_state.patient_age,
                                st.session_state.patient_gender,
                                st.session_state.vitals,
                                st.session_state.selected_symptoms,
                                risk_score, risk_level,
                            )
                            patient_data["feature_importance"] = fi
                            patient_data["confidence"] = utils.get_confidence_score(risk_score)
                            patient_data["full_symptoms"] = st.session_state.selected_symptoms

                            prediction = {
                                "risk_score": risk_score,
                                "risk_level": risk_level,
                                "feature_importance": fi,
                                "confidence": patient_data["confidence"],
                                "immediate": patient_data["Immediate"],
                                "position": len(st.session_state.patients) + 1,
                            }

                            pid = save_patient_to_db(patient_data, prediction)
                            if pid:
                                st.session_state.patients.append(patient_data)
                                st.session_state.show_prediction = True
                                st.session_state.last_prediction = prediction
                                st.rerun()

            else:
                # ── Prediction Results ────────────────────────────────────────
                pred = st.session_state.last_prediction
                rl = pred["risk_level"]
                rs = pred["risk_score"]
                conf = pred["confidence"]
                fi = pred["feature_importance"]

                cls = {"HIGH": "pred-high", "MEDIUM": "pred-medium"}.get(rl, "pred-low")
                icon = {"HIGH": "🔴", "MEDIUM": "🟡"}.get(rl, "🟢")

                st.markdown(
                    f'<div class="pred-card {cls}">'
                    f'<div style="font-size:.95rem;opacity:.9">{utils.translate("risk_level", lang).upper()}</div>'
                    f'<div class="pred-score">{rs:.0f}<span style="font-size:1.1rem">/100</span></div>'
                    f'<div class="pred-label">{icon} {utils.translate(rl.lower(), lang).upper()}</div>'
                    f'<div style="margin-top:.4rem;font-size:.88rem;opacity:.9">{utils.translate("ai_confidence", lang)}: {conf*100:.1f}%</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if pred["immediate"]:
                    st.error("🚨 **IMMEDIATE ATTENTION REQUIRED** — Critical indicators detected.")

                col_fi, col_chart = st.columns(2)
                with col_fi:
                    st.markdown('<div class="card"><div class="card-title">📊 ' + utils.translate("feature_importance", lang) + '</div>', unsafe_allow_html=True)
                    mx = max(fi.values()) if fi else 1
                    for feat, imp in sorted(fi.items(), key=lambda x: x[1], reverse=True):
                        pct = (imp / mx) * 100 if mx else 0
                        st.markdown(
                            f'<div class="fi-row"><div class="fi-name">{feat}</div>'
                            f'<div class="fi-track"><div class="fi-fill" style="width:{max(pct,8)}%">{imp:.1f}</div></div></div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_chart:
                    st.markdown('<div class="card"><div class="card-title">📈 Vitals vs Normal</div>', unsafe_allow_html=True)
                    vitals_df = pd.DataFrame({
                        "Vital": [utils.translate("heart_rate", lang), utils.translate("bp_systolic", lang),
                                  utils.translate("bp_diastolic", lang), utils.translate("temperature", lang)],
                        "Your Value": [
                            st.session_state.vitals["heart_rate"],
                            st.session_state.vitals["bp_systolic"],
                            st.session_state.vitals["bp_diastolic"],
                            st.session_state.vitals["temperature"],
                        ],
                        "Normal Max": [100, 120, 80, 99.0],
                    })
                    st.bar_chart(vitals_df.set_index("Vital"), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(
                    f'<div class="card" style="text-align:center">'
                    f'<div class="card-title" style="justify-content:center">✅ Saved</div>'
                    f'<p style="color:#555">Your triage has been recorded. Position <b>#{pred["position"]}</b> in queue.</p></div>',
                    unsafe_allow_html=True,
                )

                _, bc, _ = st.columns([1, 2, 1])
                with bc:
                    if st.button("🔄 " + utils.translate("back", lang), use_container_width=True, key="reset"):
                        st.session_state.show_prediction = False
                        st.session_state.last_prediction = None
                        st.session_state.selected_symptoms = []
                        st.session_state.vitals = {"heart_rate": 75.0, "bp_systolic": 120.0, "bp_diastolic": 80.0, "temperature": 98.6}
                        st.session_state.patient_age = 30
                        st.rerun()

        # ─── TAB 2: My Past Records + Analytics ──────────────────────────────
        with tab_records:
            all_records = load_patients_from_db()
            my_records = [r for r in all_records if r["Name"].lower() == st.session_state.email.split("@")[0].lower()]

            st.markdown('<div class="card"><div class="card-title">📁 ' + utils.translate("priority_queue", lang) + '</div>', unsafe_allow_html=True)

            if not my_records:
                st.info(utils.translate("submit", lang) + " — No past assessments found.")
            else:
                st.markdown(f"<p style='color:#555;margin-bottom:.8rem'>Showing <b>{len(my_records)}</b> past record(s)</p>", unsafe_allow_html=True)

                for i, rec in enumerate(my_records):
                    risk_color = {"HIGH": "#e53935", "MEDIUM": "#f57c00", "LOW": "#43a047"}.get(rec["Risk Level"], "#999")
                    st.markdown(
                        f'<div class="patient-row">'
                        f'<div style="flex:0 0 40px;font-weight:700;color:#0052CC">#{rec["ID"]}</div>'
                        f'<div style="flex:1"><b>{utils.translate("age", lang)}:</b> {rec["Age"]} &middot; <b>{utils.translate("gender", lang)}:</b> {rec["Gender"]}</div>'
                        f'<div style="flex:1"><b>HR</b> {rec["Heart Rate"]} &middot; <b>BP</b> {rec["BP"]} &middot; <b>T</b> {rec["Temp"]}°F</div>'
                        f'<div style="flex:1">{rec["Symptoms"]}</div>'
                        f'<div style="flex:0 0 80px;text-align:center"><span class="risk-badge risk-{rec["Risk Level"]}">{utils.translate(rec["Risk Level"].lower(), lang)}</span></div>'
                        f'<div style="flex:0 0 60px;text-align:right;font-weight:700;color:{risk_color}">{rec["Risk Score"]}/100</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    # Expandable detail for each patient record
                    with st.expander(f"🔍 View Full Details — Assessment #{rec['ID']}  ({rec['created_at']})", expanded=False):
                        dc1, dc2 = st.columns(2)
                        with dc1:
                            st.markdown(f"""
                            <div class="detail-card">
                                <h4>👤 {utils.translate("patient_info", lang)}</h4>
                                <div class="detail-row"><span class="detail-label">{utils.translate("age", lang)}</span><span class="detail-value">{rec['Age']}</span></div>
                                <div class="detail-row"><span class="detail-label">{utils.translate("gender", lang)}</span><span class="detail-value">{rec['Gender']}</span></div>
                                <div class="detail-row"><span class="detail-label">{utils.translate("heart_rate", lang)}</span><span class="detail-value">{rec['Heart Rate']} bpm</span></div>
                                <div class="detail-row"><span class="detail-label">{utils.translate("bp_systolic", lang)}</span><span class="detail-value">{rec['BP Systolic']} mmHg</span></div>
                                <div class="detail-row"><span class="detail-label">{utils.translate("bp_diastolic", lang)}</span><span class="detail-value">{rec['BP Diastolic']} mmHg</span></div>
                                <div class="detail-row"><span class="detail-label">{utils.translate("temperature", lang)}</span><span class="detail-value">{rec['Temp']} °F</span></div>
                                <div class="detail-row"><span class="detail-label">Department</span><span class="detail-value">{rec.get('department','N/A')}</span></div>
                                <div class="detail-row"><span class="detail-label">Date</span><span class="detail-value">{rec['created_at']}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                        with dc2:
                            st.markdown(f"""
                            <div class="detail-card">
                                <h4>🤖 AI Assessment</h4>
                                <div class="detail-row"><span class="detail-label">{utils.translate("risk_level", lang)}</span><span class="detail-value" style="color:{risk_color};font-weight:700">{utils.translate(rec['Risk Level'].lower(), lang)}</span></div>
                                <div class="detail-row"><span class="detail-label">Risk Score</span><span class="detail-value" style="font-weight:700">{rec['Risk Score']}/100</span></div>
                                <div class="detail-row"><span class="detail-label">{utils.translate("ai_confidence", lang)}</span><span class="detail-value">{rec.get('confidence',0)*100:.1f}%</span></div>
                                <div class="detail-row"><span class="detail-label">Immediate</span><span class="detail-value">{'🚨 Yes' if rec.get('Immediate') else '✅ No'}</span></div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Symptoms list
                            st.markdown(f"**🩺 {utils.translate('symptoms', lang)}:**")
                            for s in rec.get("full_symptoms", []):
                                st.write(f"• {s}")

                            # Feature importance
                            fi_data = rec.get("feature_importance", {})
                            if fi_data:
                                st.markdown(f"**📊 {utils.translate('feature_importance', lang)}:**")
                                fi_df = pd.DataFrame(list(fi_data.items()), columns=["Feature", "Score"]).sort_values("Score", ascending=True)
                                st.bar_chart(fi_df.set_index("Feature"), use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Analytics section ─────────────────────────────────────────────
            if my_records:
                st.markdown("---")
                st.markdown('<div class="card"><div class="card-title">📊 My Health Analytics</div>', unsafe_allow_html=True)

                ac1, ac2 = st.columns(2)
                with ac1:
                    st.markdown("**📈 Risk Score Trend**")
                    scores = [r["Risk Score"] for r in reversed(my_records)]
                    dates = [r.get("created_at", f"#{i+1}") for i, r in enumerate(reversed(my_records))]
                    trend_df = pd.DataFrame({"Assessment": dates, "Risk Score": scores})
                    st.line_chart(trend_df.set_index("Assessment"), use_container_width=True)

                with ac2:
                    st.markdown(f"**📊 {utils.translate('risk_level', lang)} Distribution**")
                    rc_data = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                    for r in my_records:
                        if r["Risk Level"] in rc_data:
                            rc_data[r["Risk Level"]] += 1
                    rdf = pd.DataFrame({"Level": list(rc_data.keys()), "Count": list(rc_data.values())})
                    rdf = rdf[rdf["Count"] > 0]
                    if not rdf.empty:
                        st.bar_chart(rdf.set_index("Level"), use_container_width=True)

                ac3, ac4 = st.columns(2)
                with ac3:
                    st.markdown("**🏥 Department Distribution**")
                    dept_c = {}
                    for r in my_records:
                        d = r.get("department", "General")
                        dept_c[d] = dept_c.get(d, 0) + 1
                    ddf = pd.DataFrame({"Dept": list(dept_c.keys()), "Count": list(dept_c.values())})
                    if not ddf.empty:
                        st.bar_chart(ddf.set_index("Dept"), use_container_width=True)

                with ac4:
                    st.markdown("**💓 Vitals Trend**")
                    hr_vals = [r["Heart Rate"] for r in reversed(my_records)]
                    bp_vals = [r["BP Systolic"] for r in reversed(my_records)]
                    vt_df = pd.DataFrame({"Heart Rate": hr_vals, "BP Systolic": bp_vals})
                    st.line_chart(vt_df, use_container_width=True)

                st.markdown("</div>", unsafe_allow_html=True)

        # ─── TAB 3: AI Chat ──────────────────────────────────────────────────
        with tab_chat:
            st.markdown(
                f'<div class="chat-hdr">🤖 {utils.translate("chat_assistant", lang)} <span class="chat-dot"></span></div>',
                unsafe_allow_html=True,
            )

            chat_wrap = st.container(height=380)
            with chat_wrap:
                if not st.session_state.chat_history:
                    st.markdown(
                        '<div class="msg-bot">👋 ' + utils.translate("chat_placeholder", lang) + '</div>',
                        unsafe_allow_html=True,
                    )
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="msg-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

            ci1, ci2 = st.columns([6, 1])
            with ci1:
                user_msg = st.text_input("msg", placeholder=utils.translate("chat_placeholder", lang),
                                         label_visibility="collapsed", key="chat_in")
            with ci2:
                send = st.button("➤", key="send_chat", type="primary", use_container_width=True)

            if send and user_msg:
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                resp = st.session_state.chatbot.get_response(user_msg)
                st.session_state.chat_history.append({"role": "bot", "content": resp})
                st.rerun()

            st.caption(utils.translate("medical_disclaimer", lang))

    # ══════════════════════════════════════════════════════════════════════════
    #  HOSPITAL ROLE — FULL DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.role == "Hospital":
        all_patients = load_patients_from_db()
        st.session_state.patients = all_patients

        st.markdown(
            f"<h2 style='text-align:center;margin:.4rem 0;color:#1a1a2e'>🏨 {utils.translate('welcome', lang)}</h2>"
            f"<p style='text-align:center;color:#555'>{utils.translate('hospital', lang)}: <b>{st.session_state.email.split('@')[0].title()}</b></p>",
            unsafe_allow_html=True,
        )

        total = len(all_patients)
        high = sum(1 for p in all_patients if p.get("Risk Level") == "HIGH")
        medium = sum(1 for p in all_patients if p.get("Risk Level") == "MEDIUM")
        low = sum(1 for p in all_patients if p.get("Risk Level") == "LOW")
        imm_count = sum(1 for p in all_patients if p.get("Immediate"))

        # Alert banner
        if imm_count > 0:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#c62828,#e53935);color:#fff;padding:.8rem 1.5rem;border-radius:12px;text-align:center;font-weight:700;margin-bottom:1rem;font-size:1rem">'
                f'🚨 ALERT: {imm_count} IMMEDIATE CASE(S) REQUIRE ATTENTION!</div>',
                unsafe_allow_html=True,
            )

        # Stat cards
        m1, m2, m3, m4, m5 = st.columns(5)
        stats = [
            (m1, "Total", total, "#0052CC"),
            (m2, utils.translate("high", lang), high, "#e53935"),
            (m3, utils.translate("medium", lang), medium, "#f57c00"),
            (m4, utils.translate("low", lang), low, "#43a047"),
            (m5, utils.translate("immediate", lang), imm_count, "#c62828"),
        ]
        for col, lbl, val, clr in stats:
            with col:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-val" style="color:{clr}">{val}</div>'
                    f'<div class="metric-lbl">{lbl}</div></div>',
                    unsafe_allow_html=True,
                )

        # Tabs
        h_tab_queue, h_tab_details, h_tab_analytics = st.tabs([
            "📋 " + utils.translate("priority_queue", lang),
            "🔍 Patient Details",
            "📊 Analytics",
        ])

        # ─── Hospital Tab 1: Patient Queue ───────────────────────────────────
        with h_tab_queue:
            if not all_patients:
                st.info("No patients in queue. Waiting for patient submissions...")
            else:
                sorted_p = sorted(all_patients, key=lambda x: x.get("Risk Score", 0), reverse=True)

                for rec in sorted_p:
                    risk_color = {"HIGH": "#e53935", "MEDIUM": "#f57c00", "LOW": "#43a047"}.get(rec["Risk Level"], "#999")
                    imm_badge = ' <span style="background:#c62828;color:#fff;padding:2px 8px;border-radius:8px;font-size:.7rem;font-weight:700;margin-left:6px">⚡ IMMEDIATE</span>' if rec.get("Immediate") else ""
                    st.markdown(
                        f'<div class="patient-row">'
                        f'<div style="flex:0 0 40px;font-weight:700;color:#0052CC">#{rec["ID"]}</div>'
                        f'<div style="flex:1.2"><b>{rec["Name"]}</b> &middot; {utils.translate("age", lang)} {rec["Age"]}, {rec["Gender"]}</div>'
                        f'<div style="flex:1"><b>HR</b> {rec["Heart Rate"]} &middot; <b>BP</b> {rec["BP"]} &middot; <b>T</b> {rec["Temp"]}°F</div>'
                        f'<div style="flex:1.2">{rec["Symptoms"]}</div>'
                        f'<div style="flex:0 0 90px;text-align:center"><span class="risk-badge risk-{rec["Risk Level"]}">{utils.translate(rec["Risk Level"].lower(), lang)}</span>{imm_badge}</div>'
                        f'<div style="flex:0 0 65px;text-align:right;font-weight:700;color:{risk_color}">{rec["Risk Score"]}/100</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # ─── Hospital Tab 2: Patient Details ─────────────────────────────────
        with h_tab_details:
            if not all_patients:
                st.info("No patient data available.")
            else:
                st.markdown(f"<p style='color:#555;margin-bottom:.5rem'>Select a patient to view complete details</p>", unsafe_allow_html=True)

                patient_names = [f"#{p['ID']} — {p['Name']} ({utils.translate(p['Risk Level'].lower(), lang)})" for p in all_patients]
                sel_idx = st.selectbox("Select Patient", range(len(patient_names)), format_func=lambda i: patient_names[i], key="hosp_patient_sel")

                rec = all_patients[sel_idx]
                risk_color = {"HIGH": "#e53935", "MEDIUM": "#f57c00", "LOW": "#43a047"}.get(rec["Risk Level"], "#999")

                dc1, dc2 = st.columns(2)
                with dc1:
                    st.markdown(f"""
                    <div class="detail-card">
                        <h4>👤 {utils.translate("patient_info", lang)}</h4>
                        <div class="detail-row"><span class="detail-label">Name</span><span class="detail-value">{rec['Name']}</span></div>
                        <div class="detail-row"><span class="detail-label">Email</span><span class="detail-value">{rec.get('email','N/A')}</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("age", lang)}</span><span class="detail-value">{rec['Age']}</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("gender", lang)}</span><span class="detail-value">{rec['Gender']}</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("heart_rate", lang)}</span><span class="detail-value">{rec['Heart Rate']} bpm</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("bp_systolic", lang)}</span><span class="detail-value">{rec['BP Systolic']} mmHg</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("bp_diastolic", lang)}</span><span class="detail-value">{rec['BP Diastolic']} mmHg</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("temperature", lang)}</span><span class="detail-value">{rec['Temp']} °F</span></div>
                        <div class="detail-row"><span class="detail-label">Department</span><span class="detail-value">{rec.get('department','N/A')}</span></div>
                        <div class="detail-row"><span class="detail-label">Date</span><span class="detail-value">{rec['created_at']}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                with dc2:
                    st.markdown(f"""
                    <div class="detail-card">
                        <h4>🤖 AI Assessment</h4>
                        <div class="detail-row"><span class="detail-label">{utils.translate("risk_level", lang)}</span><span class="detail-value" style="color:{risk_color};font-weight:800;font-size:1.1rem">{utils.translate(rec['Risk Level'].lower(), lang).upper()}</span></div>
                        <div class="detail-row"><span class="detail-label">Risk Score</span><span class="detail-value" style="font-weight:700;font-size:1.05rem">{rec['Risk Score']}/100</span></div>
                        <div class="detail-row"><span class="detail-label">{utils.translate("ai_confidence", lang)}</span><span class="detail-value">{rec.get('confidence',0)*100:.1f}%</span></div>
                        <div class="detail-row"><span class="detail-label">Immediate?</span><span class="detail-value">{'🚨 YES' if rec.get('Immediate') else '✅ No'}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                # Symptoms + Feature Importance side by side
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown(f'<div class="detail-card"><h4>🩺 {utils.translate("symptoms", lang)}</h4>', unsafe_allow_html=True)
                    for s in rec.get("full_symptoms", []):
                        st.markdown(f"<div style='padding:.25rem 0;color:#333'>• {s}</div>", unsafe_allow_html=True)
                    if not rec.get("full_symptoms"):
                        st.write("No symptoms recorded")
                    st.markdown("</div>", unsafe_allow_html=True)

                with sc2:
                    fi_data = rec.get("feature_importance", {})
                    if fi_data:
                        st.markdown(f'<div class="detail-card"><h4>📊 {utils.translate("feature_importance", lang)}</h4>', unsafe_allow_html=True)
                        mx = max(fi_data.values()) if fi_data else 1
                        for feat, imp in sorted(fi_data.items(), key=lambda x: x[1], reverse=True):
                            pct = (imp / mx) * 100 if mx else 0
                            st.markdown(
                                f'<div class="fi-row"><div class="fi-name">{feat}</div>'
                                f'<div class="fi-track"><div class="fi-fill" style="width:{max(pct,8)}%">{imp:.1f}</div></div></div>',
                                unsafe_allow_html=True,
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("No feature importance data available")

                # Vitals chart for selected patient
                st.markdown(f'<div class="card"><div class="card-title">📈 Vitals Comparison — {rec["Name"]}</div>', unsafe_allow_html=True)
                vcomp = pd.DataFrame({
                    "Vital": [utils.translate("heart_rate", lang), utils.translate("bp_systolic", lang),
                              utils.translate("bp_diastolic", lang), utils.translate("temperature", lang)],
                    "Patient": [rec["Heart Rate"], rec["BP Systolic"], rec["BP Diastolic"], rec["Temp"]],
                    "Normal Max": [100, 120, 80, 99.0],
                })
                st.bar_chart(vcomp.set_index("Vital"), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ─── Hospital Tab 3: Analytics ────────────────────────────────────────
        with h_tab_analytics:
            if not all_patients:
                st.info("No patient data for analytics.")
            else:
                st.markdown('<div class="card"><div class="card-title">📊 Hospital Analytics Dashboard</div>', unsafe_allow_html=True)

                ac1, ac2 = st.columns(2)
                with ac1:
                    st.markdown(f"**📊 {utils.translate('risk_level', lang)} Distribution**")
                    rdf = pd.DataFrame({
                        "Level": [utils.translate("high", lang), utils.translate("medium", lang), utils.translate("low", lang)],
                        "Count": [high, medium, low],
                    })
                    rdf = rdf[rdf["Count"] > 0]
                    if not rdf.empty:
                        st.bar_chart(rdf.set_index("Level"), use_container_width=True)

                with ac2:
                    st.markdown("**🏥 Department Distribution**")
                    dept_c = {}
                    for p in all_patients:
                        d = p.get("department", "General")
                        dept_c[d] = dept_c.get(d, 0) + 1
                    ddf = pd.DataFrame({"Department": list(dept_c.keys()), "Count": list(dept_c.values())})
                    if not ddf.empty:
                        st.bar_chart(ddf.set_index("Department"), use_container_width=True)

                ac3, ac4 = st.columns(2)
                with ac3:
                    st.markdown(f"**👤 {utils.translate('age', lang)} Distribution**")
                    ages = [p["Age"] for p in all_patients]
                    bins = [0, 18, 35, 50, 65, 120]
                    labels = ["0-17", "18-34", "35-49", "50-64", "65+"]
                    age_groups = pd.cut(ages, bins=bins, labels=labels, right=False)
                    age_df = pd.DataFrame({"Group": age_groups}).value_counts().reset_index()
                    age_df.columns = ["Age Group", "Count"]
                    age_df = age_df.sort_values("Age Group")
                    st.bar_chart(age_df.set_index("Age Group"), use_container_width=True)

                with ac4:
                    st.markdown("**📈 Risk Score Distribution**")
                    scores = [p["Risk Score"] for p in all_patients]
                    score_bins = [0, 30, 50, 70, 101]
                    score_labels = ["0-29 (Low)", "30-49 (Med)", "50-69 (High)", "70-100 (Critical)"]
                    score_groups = pd.cut(scores, bins=score_bins, labels=score_labels, right=True)
                    sdf = pd.DataFrame({"Group": score_groups}).value_counts().reset_index()
                    sdf.columns = ["Score Range", "Count"]
                    sdf = sdf.sort_values("Score Range")
                    st.bar_chart(sdf.set_index("Score Range"), use_container_width=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Second row of charts
                st.markdown('<div class="card"><div class="card-title">📈 Trends & Vitals</div>', unsafe_allow_html=True)

                tc1, tc2 = st.columns(2)
                with tc1:
                    st.markdown("**💓 Heart Rate Distribution**")
                    hrs = [p["Heart Rate"] for p in all_patients]
                    hr_df = pd.DataFrame({"Heart Rate": hrs})
                    st.bar_chart(hr_df["Heart Rate"].value_counts().sort_index(), use_container_width=True)

                with tc2:
                    st.markdown("**🩸 Blood Pressure Overview**")
                    bp_data = pd.DataFrame({
                        "Patient": [p["Name"][:10] for p in all_patients[:15]],
                        "Systolic": [p["BP Systolic"] for p in all_patients[:15]],
                        "Diastolic": [p["BP Diastolic"] for p in all_patients[:15]],
                    })
                    st.bar_chart(bp_data.set_index("Patient"), use_container_width=True)

                tc3, tc4 = st.columns(2)
                with tc3:
                    st.markdown("**🌡️ Temperature Distribution**")
                    temps = [p["Temp"] for p in all_patients]
                    temp_df = pd.DataFrame({"Temp": temps})
                    st.bar_chart(temp_df["Temp"].value_counts().sort_index(), use_container_width=True)

                with tc4:
                    st.markdown("**📋 Patients per Day**")
                    dates = [r.get("created_at", "")[:10] for r in all_patients if r.get("created_at")]
                    if dates:
                        date_df = pd.DataFrame({"Date": dates})
                        st.bar_chart(date_df["Date"].value_counts().sort_index(), use_container_width=True)
                    else:
                        st.info("No date data available")

                st.markdown("</div>", unsafe_allow_html=True)

                # Summary table
                st.markdown('<div class="card"><div class="card-title">📋 All Patients Summary</div>', unsafe_allow_html=True)
                summary_df = pd.DataFrame([{
                    "ID": p["ID"],
                    "Name": p["Name"],
                    utils.translate("age", lang): p["Age"],
                    utils.translate("gender", lang): p["Gender"],
                    "HR": p["Heart Rate"],
                    "BP": p["BP"],
                    "Temp": p["Temp"],
                    utils.translate("risk_level", lang): utils.translate(p["Risk Level"].lower(), lang),
                    "Score": p["Risk Score"],
                    "Dept": p.get("department", "—"),
                    "Date": p.get("created_at", "—"),
                } for p in all_patients])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
