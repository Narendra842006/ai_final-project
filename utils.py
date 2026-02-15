"""
Utility functions for Smart Patient Triage System
Includes translations, risk prediction, PDF extraction, and SHAP-like visualizations
"""

import re
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import config

# ============= TRANSLATIONS =============

TRANSLATIONS = {
    'English': {
        'welcome': 'Welcome to Smart Patient Triage',
        'login': 'Login',
        'username': 'Username',
        'role': 'Select Your Role',
        'patient': 'Patient',
        'hospital': 'Hospital Staff',
        'logout': 'Logout',
        'language': 'Language',
        'step': 'Step',
        'next': 'Next',
        'back': 'Back',
        'submit': 'Submit',
        'age': 'Age',
        'gender': 'Gender',
        'male': 'Male',
        'female': 'Female',
        'other': 'Other',
        'upload_ehr': 'Upload EHR/EMR (PDF)',
        'symptoms': 'Select Your Symptoms',
        'heart_rate': 'Heart Rate (bpm)',
        'bp_systolic': 'Blood Pressure Systolic',
        'bp_diastolic': 'Blood Pressure Diastolic',
        'temperature': 'Temperature (°F)',
        'patient_info': 'Patient Information',
        'risk_level': 'Risk Level',
        'high': 'HIGH',
        'medium': 'MEDIUM',
        'low': 'LOW',
        'immediate': 'IMMEDIATE',
        'priority_queue': 'Priority Queue',
        'ai_confidence': 'AI Confidence Score',
        'feature_importance': 'Feature Importance',
        'chat_assistant': 'AI Chat Assistant',
        'chat_placeholder': 'Describe your symptoms...',
        'medical_disclaimer': '⚠️ This is an AI assistant for guidance only. Seek professional medical help for emergencies.',
    },
    'Spanish': {
        'welcome': 'Bienvenido al Triaje Inteligente de Pacientes',
        'login': 'Iniciar Sesión',
        'username': 'Nombre de Usuario',
        'role': 'Seleccione su Rol',
        'patient': 'Paciente',
        'hospital': 'Personal del Hospital',
        'logout': 'Cerrar Sesión',
        'language': 'Idioma',
        'step': 'Paso',
        'next': 'Siguiente',
        'back': 'Atrás',
        'submit': 'Enviar',
        'age': 'Edad',
        'gender': 'Género',
        'male': 'Masculino',
        'female': 'Femenino',
        'other': 'Otro',
        'upload_ehr': 'Subir EHR/EMR (PDF)',
        'symptoms': 'Seleccione sus Síntomas',
        'heart_rate': 'Frecuencia Cardíaca (lpm)',
        'bp_systolic': 'Presión Arterial Sistólica',
        'bp_diastolic': 'Presión Arterial Diastólica',
        'temperature': 'Temperatura (°F)',
        'patient_info': 'Información del Paciente',
        'risk_level': 'Nivel de Riesgo',
        'high': 'ALTO',
        'medium': 'MEDIO',
        'low': 'BAJO',
        'immediate': 'INMEDIATO',
        'priority_queue': 'Cola de Prioridad',
        'ai_confidence': 'Puntuación de Confianza de IA',
        'feature_importance': 'Importancia de Características',
        'chat_assistant': 'Asistente de Chat IA',
        'chat_placeholder': 'Describa sus síntomas...',
        'medical_disclaimer': '⚠️ Este es un asistente de IA solo para orientación. Busque ayuda médica profesional en emergencias.',
    },
    'Hindi': {
        'welcome': 'स्मार्ट रोगी ट्राइएज में आपका स्वागत है',
        'login': 'लॉगिन',
        'username': 'उपयोगकर्ता नाम',
        'role': 'अपनी भूमिका चुनें',
        'patient': 'रोगी',
        'hospital': 'अस्पताल कर्मचारी',
        'logout': 'लॉगआउट',
        'language': 'भाषा',
        'step': 'चरण',
        'next': 'अगला',
        'back': 'पीछे',
        'submit': 'जमा करें',
        'age': 'आयु',
        'gender': 'लिंग',
        'male': 'पुरुष',
        'female': 'महिला',
        'other': 'अन्य',
        'upload_ehr': 'EHR/EMR अपलोड करें (PDF)',
        'symptoms': 'अपने लक्षण चुनें',
        'heart_rate': 'हृदय गति (बीपीएम)',
        'bp_systolic': 'रक्तचाप सिस्टोलिक',
        'bp_diastolic': 'रक्तचाप डायस्टोलिक',
        'temperature': 'तापमान (°F)',
        'patient_info': 'रोगी की जानकारी',
        'risk_level': 'जोखिम स्तर',
        'high': 'उच्च',
        'medium': 'मध्यम',
        'low': 'कम',
        'immediate': 'तत्काल',
        'priority_queue': 'प्राथमिकता कतार',
        'ai_confidence': 'AI विश्वास स्कोर',
        'feature_importance': 'फीचर महत्व',
        'chat_assistant': 'AI चैट सहायक',
        'chat_placeholder': 'अपने लक्षणों का वर्णन करें...',
        'medical_disclaimer': '⚠️ यह केवल मार्गदर्शन के लिए एक AI सहायक है। आपातकाल के लिए पेशेवर चिकित्सा सहायता लें।',
    },
    'Tamil': {
        'welcome': 'ஸ்மார்ட் நோயாளி முன்னுரிமைக்கு வரவேற்கிறோம்',
        'login': 'உள்நுழைய',
        'username': 'பயனர் பெயர்',
        'role': 'உங்கள் பாத்திரத்தைத் தேர்ந்தெடுக்கவும்',
        'patient': 'நோயாளி',
        'hospital': 'மருத்துவமனை ஊழியர்',
        'logout': 'வெளியேறு',
        'language': 'மொழி',
        'step': 'படி',
        'next': 'அடுத்தது',
        'back': 'பின்',
        'submit': 'சமர்ப்பிக்கவும்',
        'age': 'வயது',
        'gender': 'பாலினம்',
        'male': 'ஆண்',
        'female': 'பெண்',
        'other': 'மற்றவை',
        'upload_ehr': 'EHR/EMR பதிவேற்றவும் (PDF)',
        'symptoms': 'உங்கள் அறிகுறிகளைத் தேர்ந்தெடுக்கவும்',
        'heart_rate': 'இதய துடிப்பு (bpm)',
        'bp_systolic': 'இரத்த அழுத்தம் சிஸ்டாலிக்',
        'bp_diastolic': 'இரத்த அழுத்தம் டயாஸ்டாலிக்',
        'temperature': 'வெப்பநிலை (°F)',
        'patient_info': 'நோயாளி தகவல்',
        'risk_level': 'ஆபத்து நிலை',
        'high': 'உயர்',
        'medium': 'நடுத்தர',
        'low': 'குறைவு',
        'immediate': 'உடனடி',
        'priority_queue': 'முன்னுரிமை வரிசை',
        'ai_confidence': 'AI நம்பிக்கை மதிப்பெண்',
        'feature_importance': 'அம்ச முக்கியத்துவம்',
        'chat_assistant': 'AI அரட்டை உதவியாளர்',
        'chat_placeholder': 'உங்கள் அறிகுறிகளை விவரிக்கவும்...',
        'medical_disclaimer': '⚠️ இது வழிகாட்டுதலுக்கான AI உதவியாளர் மட்டுமே. அவசர சிகிச்சைக்கு தொழில்முறை மருத்துவ உதவியை நாடவும்.',
    },
    'Telugu': {
        'welcome': 'స్మార్ట్ పేషెంట్ ట్రియాజ్‌కు స్వాగతం',
        'login': 'లాగిన్',
        'username': 'యూజర్ పేరు',
        'role': 'మీ పాత్రను ఎంచుకోండి',
        'patient': 'రోగి',
        'hospital': 'ఆసుపత్రి సిబ్బంది',
        'logout': 'లాగౌట్',
        'language': 'భాష',
        'step': 'దశ',
        'next': 'తదుపరి',
        'back': 'వెనుకకు',
        'submit': 'సమర్పించండి',
        'age': 'వయస్సు',
        'gender': 'లింగం',
        'male': 'పురుషుడు',
        'female': 'స్త్రీ',
        'other': 'ఇతర',
        'upload_ehr': 'EHR/EMR అప్‌లోడ్ చేయండి (PDF)',
        'symptoms': 'మీ లక్షణాలను ఎంచుకోండి',
        'heart_rate': 'గుండె స్పందన రేటు (bpm)',
        'bp_systolic': 'రక్తపోటు సిస్టాలిక్',
        'bp_diastolic': 'రక్తపోటు డయాస్టాలిక్',
        'temperature': 'ఉష్ణోగ్రత (°F)',
        'patient_info': 'రోగి సమాచారం',
        'risk_level': 'ప్రమాద స్థాయి',
        'high': 'అధికం',
        'medium': 'మధ్యస్థం',
        'low': 'తక్కువ',
        'immediate': 'తక్షణం',
        'priority_queue': 'ప్రాధాన్యత క్యూ',
        'ai_confidence': 'AI విశ్వాస స్కోరు',
        'feature_importance': 'లక్షణ ప్రాముఖ్యత',
        'chat_assistant': 'AI చాట్ అసిస్టెంట్',
        'chat_placeholder': 'మీ లక్షణాలను వివరించండి...',
        'medical_disclaimer': '⚠️ ఇది మార్గదర్శకత్వం కోసం మాత్రమే AI అసిస్టెంట్. అత్యవసర పరిస్థితుల్లో వృత్తిపరమైన వైద్య సహాయం పొందండి.',
    }
}

def translate(key: str, language: str = 'English') -> str:
    """Get translated text for a given key and language"""
    return TRANSLATIONS.get(language, TRANSLATIONS['English']).get(key, key)


# ============= PDF EXTRACTION =============

def extract_vitals_from_pdf(pdf_text: str) -> Dict[str, float]:
    """
    Extract vital signs from PDF text using pattern matching
    Returns dictionary with heart_rate, bp_systolic, bp_diastolic, temperature
    """
    vitals = {
        'heart_rate': 75.0,
        'bp_systolic': 120.0,
        'bp_diastolic': 80.0,
        'temperature': 98.6
    }
    
    # Pattern matching for common EHR formats
    hr_pattern = r'(?:heart rate|hr|pulse)[:\s]+(\d+)'
    bp_pattern = r'(?:blood pressure|bp)[:\s]+(\d+)/(\d+)'
    temp_pattern = r'(?:temperature|temp)[:\s]+(\d+\.?\d*)'
    
    # Extract heart rate
    hr_match = re.search(hr_pattern, pdf_text.lower())
    if hr_match:
        vitals['heart_rate'] = float(hr_match.group(1))
    
    # Extract blood pressure
    bp_match = re.search(bp_pattern, pdf_text.lower())
    if bp_match:
        vitals['bp_systolic'] = float(bp_match.group(1))
        vitals['bp_diastolic'] = float(bp_match.group(2))
    
    # Extract temperature
    temp_match = re.search(temp_pattern, pdf_text.lower())
    if temp_match:
        vitals['temperature'] = float(temp_match.group(1))
    
    return vitals


# ============= RISK PREDICTION =============

def calculate_risk_score(age: int, gender: str, vitals: Dict[str, float], 
                        symptoms: List[str]) -> Tuple[float, str, Dict[str, float]]:
    """
    Mock ML model: Calculate risk score based on patient data
    Returns: (risk_score, risk_level, feature_importance)
    """
    risk_score = 0.0
    feature_importance = {}
    
    # Age factor (0-25 points)
    if age > 65:
        age_contribution = 25
    elif age > 45:
        age_contribution = 15
    else:
        age_contribution = 5
    risk_score += age_contribution
    feature_importance['Age'] = age_contribution
    
    # Heart rate factor (0-20 points)
    hr = vitals.get('heart_rate', 75)
    if hr > 130 or hr < 50:
        hr_contribution = 20
    elif hr > 100 or hr < 60:
        hr_contribution = 10
    else:
        hr_contribution = 0
    risk_score += hr_contribution
    feature_importance['Heart Rate'] = hr_contribution
    
    # Blood pressure factor (0-25 points)
    bp_sys = vitals.get('bp_systolic', 120)
    if bp_sys > 160 or bp_sys < 90:
        bp_contribution = 25
    elif bp_sys > 140 or bp_sys < 100:
        bp_contribution = 15
    else:
        bp_contribution = 0
    risk_score += bp_contribution
    feature_importance['Blood Pressure'] = bp_contribution
    
    # Temperature factor (0-15 points)
    temp = vitals.get('temperature', 98.6)
    if temp > 102 or temp < 95:
        temp_contribution = 15
    elif temp > 100:
        temp_contribution = 8
    else:
        temp_contribution = 0
    risk_score += temp_contribution
    feature_importance['Temperature'] = temp_contribution
    
    # Symptom factor (0-15 points)
    symptom_contribution = min(len(symptoms) * 2, 15)
    risk_score += symptom_contribution
    feature_importance['Symptom Count'] = symptom_contribution
    
    # Normalize to 0-100
    risk_score = min(risk_score, 100)
    
    # Determine risk level
    if risk_score >= config.RISK_THRESHOLDS['high']:
        risk_level = 'HIGH'
    elif risk_score >= config.RISK_THRESHOLDS['medium']:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    return risk_score, risk_level, feature_importance


def check_immediate_alert(vitals: Dict[str, float], symptoms: List[str]) -> bool:
    """
    Red Flag Engine: Check if patient requires immediate attention
    Logic: (Chest Pain + BP > 160) OR (Heart Rate > 130)
    """
    chest_pain = any('chest' in s.lower() for s in symptoms)
    bp_high = vitals.get('bp_systolic', 120) > 160
    hr_critical = vitals.get('heart_rate', 75) > 130
    
    return (chest_pain and bp_high) or hr_critical


# ============= SHAP-LIKE VISUALIZATION =============

def create_feature_importance_chart(feature_importance: Dict[str, float]) -> pd.DataFrame:
    """
    Create a DataFrame for feature importance visualization
    Simulates SHAP values for explainability
    """
    # Sort by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    df = pd.DataFrame(sorted_features, columns=['Feature', 'Importance'])
    return df


def get_confidence_score(risk_score: float) -> float:
    """
    Calculate AI confidence score based on risk prediction
    Higher confidence for extreme values, lower for borderline cases
    """
    # Distance from borderline thresholds
    if risk_score >= 70 or risk_score <= 30:
        confidence = 0.85 + random.uniform(0, 0.10)  # High confidence
    elif risk_score >= 60 or risk_score <= 40:
        confidence = 0.70 + random.uniform(0, 0.10)  # Medium confidence
    else:
        confidence = 0.50 + random.uniform(0, 0.15)  # Lower confidence for borderline
    
    return min(confidence, 0.99)


# ============= DATA FORMATTING =============

def format_patient_data(patient_id: int, name: str, age: int, gender: str,
                       vitals: Dict[str, float], symptoms: List[str],
                       risk_score: float, risk_level: str) -> Dict:
    """Format patient data for hospital dashboard"""
    return {
        'ID': patient_id,
        'Name': name,
        'Age': age,
        'Gender': gender,
        'Heart Rate': int(vitals.get('heart_rate', 75)),
        'BP': f"{int(vitals.get('bp_systolic', 120))}/{int(vitals.get('bp_diastolic', 80))}",
        'Temp (°F)': round(vitals.get('temperature', 98.6), 1),
        'Symptoms': ', '.join(symptoms[:3]) + ('...' if len(symptoms) > 3 else ''),
        'Risk Score': round(risk_score, 1),
        'Risk Level': risk_level,
        'Immediate': check_immediate_alert(vitals, symptoms)
    }
