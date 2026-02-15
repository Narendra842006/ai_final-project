"""
Configuration file for Smart Patient Triage System
Contains color schemes, symptom lists, and styling
"""

# Color Palettes
PATIENT_COLORS = {
    'primary': '#4A90E2',      # Calm blue
    'secondary': '#50C878',    # Emerald green
    'background': '#F0F4F8',   # Light gray-blue
    'text': '#2C3E50',         # Dark blue-gray
    'card': '#FFFFFF'
}

HOSPITAL_COLORS = {
    'high': '#E74C3C',         # Red
    'medium': '#F39C12',       # Orange/Yellow
    'low': '#2ECC71',          # Green
    'immediate': '#C0392B',    # Dark red
    'background': '#ECF0F1',
    'text': '#34495E'
}

# Risk Thresholds
RISK_THRESHOLDS = {
    'high': 70,
    'medium': 40,
    'low': 0
}

# Vital Sign Ranges
VITAL_RANGES = {
    'heart_rate': {'normal': (60, 100), 'critical': (130, 300)},
    'bp_systolic': {'normal': (90, 120), 'critical': (160, 250)},
    'bp_diastolic': {'normal': (60, 80), 'critical': (100, 150)},
    'temperature': {'normal': (97.0, 99.0), 'critical': (102.0, 106.0)}
}

# Symptoms in multiple languages
SYMPTOMS = {
    'English': [
        'Fever', 'Cough', 'Shortness of Breath', 'Chest Pain',
        'Headache', 'Fatigue', 'Nausea', 'Vomiting',
        'Diarrhea', 'Abdominal Pain', 'Dizziness', 'Confusion',
        'Rapid Heartbeat', 'Weakness', 'Loss of Appetite'
    ],
    'Spanish': [
        'Fiebre', 'Tos', 'Dificultad para Respirar', 'Dolor de Pecho',
        'Dolor de Cabeza', 'Fatiga', 'Náuseas', 'Vómitos',
        'Diarrea', 'Dolor Abdominal', 'Mareos', 'Confusión',
        'Ritmo Cardíaco Rápido', 'Debilidad', 'Pérdida de Apetito'
    ],
    'Hindi': [
        'बुखार', 'खांसी', 'सांस लेने में कठिनाई', 'छाती में दर्द',
        'सिरदर्द', 'थकान', 'जी मिचलाना', 'उल्टी',
        'दस्त', 'पेट दर्द', 'चक्कर आना', 'भ्रम',
        'तेज़ दिल की धड़कन', 'कमज़ोरी', 'भूख में कमी'
    ]
}

# Custom CSS for Patient Portal (Calm Design)
PATIENT_CSS = """
<style>
    /* Main container styling */
    .main {
        background-color: #F0F4F8;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .step {
        flex: 1;
        text-align: center;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 500;
        color: #95a5a6;
    }
    
    .step.active {
        color: #4A90E2;
        border-bottom: 3px solid #4A90E2;
    }
    
    .step.completed {
        color: #50C878;
    }
    
    /* Card styling */
    .patient-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #4A90E2, #50C878);
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74,144,226,0.4);
    }
    
    /* Input fields */
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        font-size: 1.1rem;
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #E3F2FD;
        margin-left: 2rem;
    }
    
    .bot-message {
        background-color: #F0F4F8;
        margin-right: 2rem;
    }
</style>
"""

# Custom CSS for Hospital Dashboard
HOSPITAL_CSS = """
<style>
    /* Dashboard container */
    .main {
        background-color: #ECF0F1;
    }
    
    /* Alert banner */
    .alert-banner {
        background: linear-gradient(135deg, #C0392B, #E74C3C);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1.3rem;
        font-weight: 700;
        text-align: center;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(192,57,43,0.4);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    /* Priority indicators */
    .priority-high {
        background-color: #E74C3C;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .priority-medium {
        background-color: #F39C12;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .priority-low {
        background-color: #2ECC71;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Explainability panel */
    .explain-panel {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Feature importance bars */
    .feature-bar {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
    }
    
    .feature-label {
        width: 150px;
        font-weight: 500;
    }
    
    .feature-value {
        margin-left: 1rem;
        font-weight: 600;
        color: #4A90E2;
    }
</style>
"""
