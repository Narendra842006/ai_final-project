"""
Patient Portal - Step-by-Step Triage Wizard
Progressive disclosure interface with calm design
"""

import streamlit as st
import PyPDF2
import io
import utils
import config
import chatbot

# Apply custom CSS
st.markdown(config.PATIENT_CSS, unsafe_allow_html=True)

# Get language from session state
language = st.session_state.get('language', 'English')

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login first from the home page")
    st.stop()

if st.session_state.get('role') != 'Patient':
    st.error("This page is only accessible to patients")
    st.stop()

# Initialize wizard state
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1
    st.session_state.patient_age = 30
    st.session_state.patient_gender = 'Male'
    st.session_state.vitals_extracted = False
    st.session_state.vitals = {
        'heart_rate': 75.0,
        'bp_systolic': 120.0,
        'bp_diastolic': 80.0,
        'temperature': 98.6
    }
    st.session_state.selected_symptoms = []

# Render chatbot in sidebar
chatbot.render_chatbot(language)

# Page header
st.title(f"🏥 {utils.translate('patient', language)} Portal")
st.markdown(f"### {utils.translate('welcome', language)}, {st.session_state.email}!")

# Step indicator
st.markdown('<div class="step-indicator">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    step_class = "step active" if st.session_state.wizard_step == 1 else "step completed" if st.session_state.wizard_step > 1 else "step"
    st.markdown(f'<div class="{step_class}">📋 {utils.translate("step", language)} 1: {utils.translate("patient_info", language)}</div>', 
                unsafe_allow_html=True)
with col2:
    step_class = "step active" if st.session_state.wizard_step == 2 else "step completed" if st.session_state.wizard_step > 2 else "step"
    st.markdown(f'<div class="{step_class}">📄 {utils.translate("step", language)} 2: {utils.translate("upload_ehr", language)}</div>', 
                unsafe_allow_html=True)
with col3:
    step_class = "step active" if st.session_state.wizard_step == 3 else "step completed" if st.session_state.wizard_step > 3 else "step"
    st.markdown(f'<div class="{step_class}">🩺 {utils.translate("step", language)} 3: {utils.translate("symptoms", language)}</div>', 
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==================== STEP 1: Basic Information ====================
if st.session_state.wizard_step == 1:
    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    st.subheader(f"📋 {utils.translate('step', language)} 1: {utils.translate('patient_info', language)}")
    st.markdown("Please provide your basic information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input(
            utils.translate('age', language),
            min_value=1,
            max_value=120,
            value=st.session_state.patient_age,
            step=1,
            key='age_input'
        )
        st.session_state.patient_age = age
    
    with col2:
        gender_options = [
            utils.translate('male', language),
            utils.translate('female', language),
            utils.translate('other', language)
        ]
        gender = st.selectbox(
            utils.translate('gender', language),
            options=gender_options,
            index=0,
            key='gender_input'
        )
        # Map back to English for internal storage
        gender_map = {
            utils.translate('male', language): 'Male',
            utils.translate('female', language): 'Female',
            utils.translate('other', language): 'Other'
        }
        st.session_state.patient_gender = gender_map[gender]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button(f"➡️ {utils.translate('next', language)}", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()

# ==================== STEP 2: PDF Upload & Vitals ====================
elif st.session_state.wizard_step == 2:
    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    st.subheader(f"📄 {utils.translate('step', language)} 2: {utils.translate('upload_ehr', language)}")
    st.markdown("Upload your medical records or enter vitals manually")
    
    uploaded_file = st.file_uploader(
        utils.translate('upload_ehr', language),
        type=['pdf'],
        key='pdf_uploader'
    )
    
    if uploaded_file is not None:
        try:
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Extract vitals
            extracted_vitals = utils.extract_vitals_from_pdf(text)
            st.session_state.vitals = extracted_vitals
            st.session_state.vitals_extracted = True
            
            st.success("✅ PDF processed successfully! Vitals extracted.")
            st.info(f"📄 Extracted text preview: {text[:200]}...")
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
    
    st.markdown("---")
    st.subheader("Enter Vitals (Auto-filled from PDF or Manual Entry)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hr = st.number_input(
            utils.translate('heart_rate', language),
            min_value=30.0,
            max_value=250.0,
            value=float(st.session_state.vitals['heart_rate']),
            step=1.0,
            key='hr_input'
        )
        st.session_state.vitals['heart_rate'] = hr
        
        bp_sys = st.number_input(
            utils.translate('bp_systolic', language),
            min_value=60.0,
            max_value=250.0,
            value=float(st.session_state.vitals['bp_systolic']),
            step=1.0,
            key='bp_sys_input'
        )
        st.session_state.vitals['bp_systolic'] = bp_sys
    
    with col2:
        bp_dia = st.number_input(
            utils.translate('bp_diastolic', language),
            min_value=40.0,
            max_value=150.0,
            value=float(st.session_state.vitals['bp_diastolic']),
            step=1.0,
            key='bp_dia_input'
        )
        st.session_state.vitals['bp_diastolic'] = bp_dia
        
        temp = st.number_input(
            utils.translate('temperature', language),
            min_value=90.0,
            max_value=110.0,
            value=float(st.session_state.vitals['temperature']),
            step=0.1,
            key='temp_input'
        )
        st.session_state.vitals['temperature'] = temp
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button(f"⬅️ {utils.translate('back', language)}", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with col3:
        if st.button(f"➡️ {utils.translate('next', language)}", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()

# ==================== STEP 3: Symptom Selection ====================
elif st.session_state.wizard_step == 3:
    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    st.subheader(f"🩺 {utils.translate('step', language)} 3: {utils.translate('symptoms', language)}")
    st.markdown("Select all symptoms you are currently experiencing")
    
    # Get symptoms in selected language
    symptom_list = config.SYMPTOMS[language]
    
    selected = st.multiselect(
        utils.translate('symptoms', language),
        options=symptom_list,
        default=st.session_state.selected_symptoms if st.session_state.selected_symptoms else [],
        key='symptom_selector'
    )
    st.session_state.selected_symptoms = selected
    
    if len(selected) > 0:
        st.info(f"Selected {len(selected)} symptom(s)")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button(f"⬅️ {utils.translate('back', language)}", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()
    with col3:
        if st.button(f"✅ {utils.translate('submit', language)}", use_container_width=True, type="primary"):
            if len(st.session_state.selected_symptoms) == 0:
                st.error("Please select at least one symptom")
            else:
                # Calculate risk
                risk_score, risk_level, feature_importance = utils.calculate_risk_score(
                    st.session_state.patient_age,
                    st.session_state.patient_gender,
                    st.session_state.vitals,
                    st.session_state.selected_symptoms
                )
                
                # Format patient data
                patient_data = utils.format_patient_data(
                    len(st.session_state.patients) + 1,
                    st.session_state.email,
                    st.session_state.patient_age,
                    st.session_state.patient_gender,
                    st.session_state.vitals,
                    st.session_state.selected_symptoms,
                    risk_score,
                    risk_level
                )
                
                # Add feature importance and confidence
                patient_data['feature_importance'] = feature_importance
                patient_data['confidence'] = utils.get_confidence_score(risk_score)
                
                # Add to patient queue
                st.session_state.patients.append(patient_data)
                
                # Show success message
                st.success("✅ Your triage submission has been received!")
                st.balloons()
                
                st.info(f"""
                ### Triage Summary
                - **Risk Level**: {risk_level}
                - **Risk Score**: {risk_score:.1f}/100
                - **Position in Queue**: {len(st.session_state.patients)}
                
                Thank you for submitting your information. Medical staff will review your case based on priority.
                """)
                
                # Reset wizard
                st.session_state.wizard_step = 1
                st.session_state.selected_symptoms = []
