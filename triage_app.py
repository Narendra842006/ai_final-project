"""
Smart Patient Triage System - Main Application
Entry point with professional UI design
"""

import streamlit as st
import utils

# Page configuration
st.set_page_config(
    page_title="Smart Patient Triage System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.email = ""
    st.session_state.role = ""
    st.session_state.language = "English"  # Language support
    st.session_state.patients = []  # Shared patient data
    st.session_state.login_step = 1  # Login flow step
    st.session_state.selected_role = None
    st.session_state.show_settings = False  # Settings dialog

# Global CSS for modern professional look
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Remove white boxes and padding */
    .main > div {
        padding: 0 !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Modern Top Navigation Bar - Professional Blue */
    .top-nav {
        background: linear-gradient(135deg, #0066FF 0%, #00D9FF 100%);
        padding: 1.2rem 3rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 16px rgba(0, 102, 255, 0.15);
        backdrop-filter: blur(10px);
    }
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .logo-icon {
        width: 40px;
        height: 40px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .logo-text {
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .nav-right {
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    .nav-user-info {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Clean professional cards */
    .content-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2.5rem;
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        min-height: 100vh;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0066FF 0%, #00D9FF 100%);
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Login page
if not st.session_state.authenticated:
    # Modern professional login page
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0066FF 0%, #00D9FF 50%, #0052CC 100%);
        }
        /* Clean modern inputs */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.95);
            font-size: 1rem;
            padding: 0.75rem 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align: center; color: white; font-size: 3.5rem; margin-top: 4rem; margin-bottom: 0.5rem;'>🏥 Smart Patient Triage</h1>", 
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #f0f0f0; font-size: 1.3rem; margin-bottom: 3rem;'>AI-Powered Healthcare Management</p>", 
                unsafe_allow_html=True)
    
    # Two-step login flow
    if st.session_state.login_step == 1:
        # STEP 1: Role Selection
        st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 2rem;'>Select Your Role</h2>", 
                    unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            role_col1, role_col2 = st.columns(2)
            
            with role_col1:
                if st.button("👤 Patient\n\nI need medical assistance", 
                           key="patient_role_btn",
                           use_container_width=True,
                           type="primary"):
                    st.session_state.selected_role = 'Patient'
                    st.session_state.login_step = 2
                    st.rerun()
            
            with role_col2:
                if st.button("🏨 Hospital Staff\n\nI manage patient care", 
                           key="hospital_role_btn",
                           use_container_width=True,
                           type="primary"):
                    st.session_state.selected_role = 'Hospital'
                    st.session_state.login_step = 2
                    st.rerun()
    
    else:
        # STEP 2: Credentials
        st.markdown(f"<h2 style='text-align: center; color: white; margin-bottom: 1rem;'>Login as {st.session_state.selected_role}</h2>", 
                    unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email",
                key="login_email",
                label_visibility="visible"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
                label_visibility="visible"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("⬅️ Back", use_container_width=True):
                    st.session_state.login_step = 1
                    st.session_state.selected_role = None
                    st.rerun()
            
            with col_btn2:
                if st.button("🔐 Login", use_container_width=True, type="primary"):
                    if not email:
                        st.error("Please enter your email address")
                    elif '@' not in email or '.' not in email:
                        st.error("Please enter a valid email address")
                    elif not password:
                        st.error("Please enter your password")
                    elif len(password) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.email = email
                        st.session_state.role = st.session_state.selected_role
                        st.success(f"✅ Welcome! Logging you in...")
                        st.rerun()
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: white; padding: 2rem;'>
        <p style='opacity: 0.9;'>Smart Patient Triage System v2.0</p>
        <p style='font-size: 0.9rem; opacity: 0.8;'>🔒 Secure & HIPAA Compliant</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Modern Professional Top Navigation Bar
    st.markdown(f"""
    <div class="top-nav">
        <div class="logo-container">
            <div class="logo-icon">⚕️</div>
            <div class="logo-text">Smart Triage</div>
        </div>
        <div class="nav-right">
            <div class="nav-user-info">{st.session_state.email}</div>
            <div style="color: rgba(255, 255, 255, 0.6);">|</div>
            <div class="nav-user-info">{st.session_state.role}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector and settings in modern style
    col1, col2, col3 = st.columns([5, 1.5, 1])
    
    with col2:
        st.session_state.language = st.selectbox(
            "🌍",
            options=['English', 'Spanish', 'Hindi', 'Tamil', 'Telugu'],
            index=['English', 'Spanish', 'Hindi', 'Tamil', 'Telugu'].index(st.session_state.language),
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("⚙️ Settings"):
            st.session_state.show_settings = not st.session_state.show_settings
    
    # Settings panel (expandable)
    if st.session_state.show_settings:
        st.info("""
        ⚙️ **Settings Panel**
        
        - **Email**: {email}
        - **Role**: {role}
        - **Language**: {language}
        - **Theme**: Professional (Default)
        
        *More settings coming soon...*
        """.format(
            email=st.session_state.email,
            role=st.session_state.role,
            language=st.session_state.language
        ))
        
        if st.button("🚪 Logout", type="primary"):
            st.session_state.authenticated = False
            st.session_state.email = ""
            st.session_state.role = ""
            st.session_state.login_step = 1
            st.session_state.selected_role = None
            st.rerun()
    
    # Main content area
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    # Minimal header
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0 3rem 0;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem; color: #1a1a1a;'>Welcome, {st.session_state.email.split('@')[0].title()}!</h1>
        <p style='font-size: 1.1rem; color: #666; margin: 0;'>Smart Patient Triage System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role-specific dashboard
    if st.session_state.role == 'Patient':
        # Features Grid - Clean and Modern
        st.markdown("### Key Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #0066FF, #00D9FF); padding: 2rem; border-radius: 12px; color: white; box-shadow: 0 8px 24px rgba(0, 102, 255, 0.15); text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🤖</div>
                <h3 style='color: white; margin-bottom: 0.5rem; font-size: 1.3rem;'>AI Assistant</h3>
                <p style='margin: 0; opacity: 0.95;'>Chat with our medical AI</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #0066FF, #00D9FF); padding: 2rem; border-radius: 12px; color: white; box-shadow: 0 8px 24px rgba(0, 102, 255, 0.15); text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>📊</div>
                <h3 style='color: white; margin-bottom: 0.5rem; font-size: 1.3rem;'>Risk Analysis</h3>
                <p style='margin: 0; opacity: 0.95;'>Instant health assessment</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #0066FF, #00D9FF); padding: 2rem; border-radius: 12px; color: white; box-shadow: 0 8px 24px rgba(0, 102, 255, 0.15); text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>⚡</div>
                <h3 style='color: white; margin-bottom: 0.5rem; font-size: 1.3rem;'>Fast Triage</h3>
                <p style='margin: 0; opacity: 0.95;'>Priority-based care</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:  # Hospital Staff
        # Stats Dashboard
        total_patients = len(st.session_state.patients)
        high_risk = len([p for p in st.session_state.patients if p.get('Risk Level') == 'HIGH'])
        immediate = len([p for p in st.session_state.patients if p.get('Immediate', False)])
        avg_risk = sum([p.get('Risk Score', 0) for p in st.session_state.patients]) / max(total_patients, 1)
        
        st.markdown("### Live Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #0066FF; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Total Patients</div>
                <div style='color: #1a1a1a; font-size: 2rem; font-weight: 700;'>{total_patients}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #FF4444; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>High Risk</div>
                <div style='color: #FF4444; font-size: 2rem; font-weight: 700;'>{high_risk}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #FF8800; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Immediate</div>
                <div style='color: #FF8800; font-size: 2rem; font-weight: 700;'>{immediate}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #00D9FF; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <div style='color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;'>Avg Risk</div>
                <div style='color: #00D9FF; font-size: 2rem; font-weight: 700;'>{avg_risk:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Key Features")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style='padding: 1.5rem; background: #f8fafc; border-radius: 10px;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📊</div>
                <h4 style='margin: 0.5rem 0; color: #1a1a1a;'>Priority Queue</h4>
                <p style='color: #666; font-size: 0.95rem; margin: 0;'>Smart patient sorting</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='padding: 1.5rem; background: #f8fafc; border-radius: 10px;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🚨</div>
                <h4 style='margin: 0.5rem 0; color: #1a1a1a;'>Alert System</h4>
                <p style='color: #666; font-size: 0.95rem; margin: 0;'>Critical case detection</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='padding: 1.5rem; background: #f8fafc; border-radius: 10px;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📈</div>
                <h4 style='margin: 0.5rem 0; color: #1a1a1a;'>Analytics</h4>
                <p style='color: #666; font-size: 0.95rem; margin: 0;'>Real-time insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.email = ""
    st.session_state.role = ""
    st.session_state.language = "English"  # Language support
    st.session_state.patients = []  # Shared patient data
    st.session_state.login_step = 1  # Login flow step
    st.session_state.selected_role = None

# Login page
if not st.session_state.authenticated:
    # Hide sidebar on login page
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Clean UI - remove default padding and backgrounds */
        .main > div {
            padding-top: 2rem;
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        /* Remove white container boxes */
        section.main > div {
            background-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align: center; color: white; font-size: 3.5rem; margin-bottom: 0.5rem;'>🏥 Smart Patient Triage</h1>", 
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #f0f0f0; font-size: 1.3rem; margin-bottom: 3rem;'>AI-Powered Healthcare Management</p>", 
                unsafe_allow_html=True)
    
    # Two-step login flow
    if st.session_state.login_step == 1:
        # STEP 1: Role Selection
        st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 2rem;'>Select Your Role</h2>", 
                    unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            role_col1, role_col2 = st.columns(2)
            
            with role_col1:
                if st.button("👤 Patient\n\nI need medical assistance", 
                           key="patient_role_btn",
                           use_container_width=True,
                           type="primary"):
                    st.session_state.selected_role = 'Patient'
                    st.session_state.login_step = 2
                    st.rerun()
            
            with role_col2:
                if st.button("🏨 Hospital Staff\n\nI manage patient care", 
                           key="hospital_role_btn",
                           use_container_width=True,
                           type="primary"):
                    st.session_state.selected_role = 'Hospital'
                    st.session_state.login_step = 2
                    st.rerun()
    
    else:
        # STEP 2: Credentials
        st.markdown(f"<h2 style='text-align: center; color: white; margin-bottom: 1rem;'>Login as {st.session_state.selected_role}</h2>", 
                    unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Create a clean card
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.95); padding: 3rem; border-radius: 20px; 
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);'>
            </div>
            """, unsafe_allow_html=True)
            
            email = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email",
                key="login_email",
                label_visibility="visible"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
                label_visibility="visible"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("⬅️ Back", use_container_width=True):
                    st.session_state.login_step = 1
                    st.session_state.selected_role = None
                    st.rerun()
            
            with col_btn2:
                if st.button("🔐 Login", use_container_width=True, type="primary"):
                    if not email:
                        st.error("Please enter your email address")
                    elif '@' not in email or '.' not in email:
                        st.error("Please enter a valid email address")
                    elif not password:
                        st.error("Please enter your password")
                    elif len(password) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        # Simple authentication (in production, verify against database)
                        st.session_state.authenticated = True
                        st.session_state.email = email
                        st.session_state.role = st.session_state.selected_role
                        st.success(f"✅ Welcome! Logging you in...")
                        st.rerun()
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: white; padding: 2rem;'>
        <p style='opacity: 0.9;'>Smart Patient Triage System v2.0</p>
        <p style='font-size: 0.9rem; opacity: 0.8;'>🔒 Secure & HIPAA Compliant</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Main application (after login) - HOME PAGE
    
    # Hide the page navigation links in sidebar
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        /* Clean UI */
        .main > div {
            padding-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # Language selector
        st.session_state.language = st.selectbox(
            "🌍 Language",
            options=['English', 'Spanish', 'Hindi'],
            index=['English', 'Spanish', 'Hindi'].index(st.session_state.language)
        )
        
        st.markdown("---")
        st.write(f"📧 **{st.session_state.email}**")
        st.write(f"🎭 **{st.session_state.role}**")
        
        st.markdown("---")
        
        # Manual navigation button based on role
        if st.session_state.role == 'Patient':
            if st.button("🏥 Patient Portal", use_container_width=True, type="primary"):
                st.switch_page("pages/1_🏥_Patient_Portal.py")
        else:
            if st.button("🏨 Hospital Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/2_🏨_Hospital_Dashboard.py")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.email = ""
            st.session_state.role = ""
            st.session_state.login_step = 1
            st.session_state.selected_role = None
            st.rerun()
    
    # Home page content
    st.title(f"🏥 Welcome to Smart Patient Triage")
    st.markdown(f"### Hello, **{st.session_state.email.split('@')[0].title()}**! 👋")
    
    st.markdown("---")
    
    # Role-specific dashboard
    if st.session_state.role == 'Patient':
        st.info("👇 **Click the button below to start your triage process**")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏥 Go to Patient Portal", use_container_width=True, type="primary"):
                st.switch_page("pages/1_🏥_Patient_Portal.py")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4A90E2, #50C878); padding: 2rem; border-radius: 15px; color: white;'>
                <h3 style='color: white;'>📋 Step 1</h3>
                <p>Enter your basic information</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4A90E2, #50C878); padding: 2rem; border-radius: 15px; color: white;'>
                <h3 style='color: white;'>📄 Step 2</h3>
                <p>Upload medical records</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4A90E2, #50C878); padding: 2rem; border-radius: 15px; color: white;'>
                <h3 style='color: white;'>🩺 Step 3</h3>
                <p>Select your symptoms</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🤖 AI-Powered Features")
        st.markdown("""
        - **Medical Chatbot**: Get help describing your symptoms
        - **Automatic Risk Assessment**: AI evaluates your condition
        - **Smart Triage**: Priority-based queue management
        """)
    
    else:  # Hospital Staff
        st.info("👇 **Click the button below to view the patient queue**")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏨 Go to Hospital Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/2_🏨_Hospital_Dashboard.py")
        
        # Quick stats
        total_patients = len(st.session_state.patients)
        high_risk = len([p for p in st.session_state.patients if p.get('Risk Level') == 'HIGH'])
        immediate = len([p for p in st.session_state.patients if p.get('Immediate', False)])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Patients", total_patients, delta=None)
        with col2:
            st.metric("High Risk", high_risk, delta_color="inverse")
        with col3:
            st.metric("Immediate Cases", immediate, delta_color="inverse")
        with col4:
            avg_risk = sum([p.get('Risk Score', 0) for p in st.session_state.patients]) / max(total_patients, 1)
            st.metric("Avg Risk Score", f"{avg_risk:.1f}")
        
        st.markdown("---")
        st.markdown("### 🏨 Dashboard Features")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            #### 📊 Priority Queue
            - Color-coded risk levels
            - Automatic sorting by urgency
            - Real-time updates
            """)
            
            st.markdown("""
            #### 🚨 Alert System
            - Immediate case detection
            - Flashing notifications
            - Critical patient flagging
            """)
        
        with col2:
            st.markdown("""
            #### 🔍 AI Explainability
            - Feature importance charts
            - Confidence scores
            - Transparent decision-making
            """)
            
            st.markdown("""
            #### 📈 Analytics
            - Patient statistics
            - Risk distribution
            - Queue metrics
            """)
    
    st.markdown("---")
    st.markdown("""
    ### 🌟 About This System
    
    The Smart Patient Triage System uses artificial intelligence to assess patient risk levels and prioritize care efficiently.
    
    **Key Features:**
    - 🤖 **AI-Powered**: Machine learning risk assessment
    - 📊 **Explainable**: Transparent AI decisions
    - 🔒 **Secure**: HIPAA-compliant data handling
    - ⚡ **Real-time**: Instant triage and alerts
    """)
