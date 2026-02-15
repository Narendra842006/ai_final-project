"""
Hospital Dashboard - Priority Queue & Patient Management
Efficiency-focused interface with real-time alerts and explainability
"""

import streamlit as st
import pandas as pd
import utils
import config
from backend.database import init_db, SessionLocal, Patient

init_db()

# Apply custom CSS
st.markdown(config.HOSPITAL_CSS, unsafe_allow_html=True)

# Hide sidebar
st.markdown("""
<style>
section[data-testid="stSidebar"]{display:none!important}
[data-testid="collapsedControl"]{display:none!important}
</style>
""", unsafe_allow_html=True)

# Get language from session state
language = st.session_state.get('language', 'English')

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login first from the home page")
    st.stop()

if st.session_state.get('role') != 'Hospital':
    st.error("This page is only accessible to hospital staff")
    st.stop()

# Load patients from database
def _load_patients_from_db():
    db = SessionLocal()
    try:
        records = db.query(Patient).order_by(Patient.created_at.desc()).all()
        patients = []
        for r in records:
            symptoms_list = r.symptoms if isinstance(r.symptoms, list) else []
            vitals_dict = r.vitals if isinstance(r.vitals, dict) else {}
            patients.append({
                "ID": len(patients) + 1,
                "Name": r.email.split("@")[0].title(),
                "Age": r.age,
                "Gender": r.gender,
                "Heart Rate": int(vitals_dict.get("heart_rate", 75)),
                "BP": f"{int(vitals_dict.get('bp_systolic', 120))}/{int(vitals_dict.get('bp_diastolic', 80))}",
                "Temp (°F)": round(vitals_dict.get("temperature", 98.6), 1),
                "Symptoms": ", ".join(symptoms_list[:3]) + ("..." if len(symptoms_list) > 3 else ""),
                "Risk Score": round(r.priority_score, 1),
                "Risk Level": r.risk_level,
                "Immediate": r.priority_score >= 70 and any("chest" in s.lower() for s in symptoms_list),
                "confidence": r.ai_confidence,
                "feature_importance": r.feature_importance if isinstance(r.feature_importance, dict) else {},
                "full_symptoms": symptoms_list,
            })
        return patients
    finally:
        db.close()

st.session_state.patients = _load_patients_from_db()

# Page header
st.title(f"🏨 Hospital Dashboard")
st.markdown(f"### {utils.translate('welcome', language)}, {st.session_state.email}!")

# Check for immediate cases
immediate_cases = [p for p in st.session_state.get('patients', []) if p.get('Immediate', False)]

if len(immediate_cases) > 0:
    st.markdown(f"""
    <div class="alert-banner">
        🚨 ALERT: {len(immediate_cases)} IMMEDIATE CASE(S) REQUIRE ATTENTION!
    </div>
    """, unsafe_allow_html=True)

# Priority Queue Section
st.markdown("---")
st.subheader(f"📊 {utils.translate('priority_queue', language)}")

if len(st.session_state.get('patients', [])) == 0:
    st.info("No patients in queue. Waiting for patient submissions...")
else:
    # Convert to DataFrame
    patients_df = pd.DataFrame(st.session_state.patients)
    
    # Sort by Immediate first, then by Risk Score
    patients_df['Immediate_Sort'] = patients_df['Immediate'].astype(int)
    patients_df = patients_df.sort_values(['Immediate_Sort', 'Risk Score'], ascending=[False, False])
    
    # Display table with color coding
    st.markdown("#### Patient Queue (Sorted by Priority)")
    
    # Create styled dataframe
    def color_risk_level(val):
        if val == 'HIGH' or val == utils.translate('high', language):
            return 'background-color: #E74C3C; color: white; font-weight: bold;'
        elif val == 'MEDIUM' or val == utils.translate('medium', language):
            return 'background-color: #F39C12; color: white; font-weight: bold;'
        elif val == 'LOW' or val == utils.translate('low', language):
            return 'background-color: #2ECC71; color: white; font-weight: bold;'
        return ''
    
    def highlight_immediate(row):
        if row['Immediate']:
            return ['background-color: #FFCCCC' for _ in row]
        return ['' for _ in row]
    
    # Select columns for display
    display_df = patients_df[['ID', 'Name', 'Age', 'Gender', 'Heart Rate', 'BP', 
                               'Temp (°F)', 'Symptoms', 'Risk Score', 'Risk Level']]
    
    # Apply styling
    styled_df = display_df.style.applymap(color_risk_level, subset=['Risk Level'])
    styled_df = styled_df.apply(highlight_immediate, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Patient selection for explainability
    st.markdown("---")
    st.subheader("🔍 Patient Details & Explainability")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_patient_id = st.selectbox(
            "Select Patient to View Details",
            options=patients_df['ID'].tolist(),
            format_func=lambda x: f"Patient #{x} - {patients_df[patients_df['ID']==x]['Name'].values[0]}"
        )
    
    # Get selected patient data
    selected_patient = st.session_state.patients[selected_patient_id - 1]
    
    # Two-column layout for details
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="explain-panel">', unsafe_allow_html=True)
        st.markdown("#### Patient Information")
        st.write(f"**Name:** {selected_patient['Name']}")
        st.write(f"**Age:** {selected_patient['Age']}")
        st.write(f"**Gender:** {selected_patient['Gender']}")
        st.write(f"**Heart Rate:** {selected_patient['Heart Rate']} bpm")
        st.write(f"**Blood Pressure:** {selected_patient['BP']} mmHg")
        st.write(f"**Temperature:** {selected_patient['Temp (°F)']} °F")
        
        st.markdown("---")
        st.markdown("#### Symptoms")
        # Get full symptom list from patient data
        full_symptoms = st.session_state.patients[selected_patient_id - 1].get('full_symptoms', 
                        selected_patient['Symptoms'].split(', '))
        for symptom in full_symptoms:
            st.write(f"• {symptom}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="explain-panel">', unsafe_allow_html=True)
        st.markdown("#### AI Risk Assessment")
        
        # Risk level with color
        risk_level = selected_patient['Risk Level']
        risk_score = selected_patient['Risk Score']
        
        if risk_level == 'HIGH':
            st.error(f"### 🔴 {utils.translate('high', language)} RISK")
        elif risk_level == 'MEDIUM':
            st.warning(f"### 🟡 {utils.translate('medium', language)} RISK")
        else:
            st.success(f"### 🟢 {utils.translate('low', language)} RISK")
        
        st.metric(utils.translate('risk_level', language), f"{risk_score}/100")
        
        # Confidence score
        confidence = selected_patient.get('confidence', 0.85)
        st.metric(utils.translate('ai_confidence', language), f"{confidence*100:.1f}%")
        
        # Immediate flag
        if selected_patient['Immediate']:
            st.error("🚨 **IMMEDIATE ATTENTION REQUIRED**")
        
        st.markdown("---")
        st.markdown(f"#### {utils.translate('feature_importance', language)}")
        st.caption("SHAP-like Feature Importance (Contributing Factors)")
        
        # Get feature importance
        feature_importance = selected_patient.get('feature_importance', {})
        
        if feature_importance:
            # Create bar chart using Streamlit
            importance_df = pd.DataFrame(
                list(feature_importance.items()),
                columns=['Feature', 'Importance']
            ).sort_values('Importance', ascending=True)
            
            st.bar_chart(importance_df.set_index('Feature'), use_container_width=True)
            
            # Show detailed values
            st.markdown("**Detailed Breakdown:**")
            for feature, importance in sorted(feature_importance.items(), 
                                            key=lambda x: x[1], reverse=True):
                st.write(f"• **{feature}**: {importance:.1f} points")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistics
    st.markdown("---")
    st.subheader("📈 Queue Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(st.session_state.patients))
    
    with col2:
        high_risk = len([p for p in st.session_state.patients if p['Risk Level'] == 'HIGH'])
        st.metric("High Risk", high_risk, delta_color="inverse")
    
    with col3:
        medium_risk = len([p for p in st.session_state.patients if p['Risk Level'] == 'MEDIUM'])
        st.metric("Medium Risk", medium_risk)
    
    with col4:
        low_risk = len([p for p in st.session_state.patients if p['Risk Level'] == 'LOW'])
        st.metric("Low Risk", low_risk, delta_color="normal")

# Footer
st.markdown("---")
st.caption("Dashboard updates in real-time as new patients are triaged")
