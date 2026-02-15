"""
Database Configuration and Models using SQLAlchemy
Supports both PostgreSQL (production) and SQLite (development)
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./triage_system.db"  # Fallback to SQLite for development
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Database Models
class Patient(Base):
    """Patient records table"""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    
    # Vitals (stored as JSON for flexibility)
    vitals = Column(JSON, nullable=False)
    symptoms = Column(JSON, nullable=False)
    medical_history = Column(JSON, default=[])
    allergies = Column(JSON, default=[])
    current_medications = Column(JSON, default=[])
    
    # Triage results
    risk_level = Column(String, nullable=False)
    priority_score = Column(Float, nullable=False)
    department = Column(String, nullable=False)
    ai_confidence = Column(Float, nullable=False)
    feature_importance = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HospitalQueue(Base):
    """Real-time priority queue table"""
    __tablename__ = "hospital_queue"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False)
    
    priority_score = Column(Float, nullable=False, index=True)
    risk_level = Column(String, nullable=False, index=True)
    department = Column(String, nullable=False)
    
    arrival_time = Column(DateTime, default=datetime.utcnow)
    vitals_summary = Column(String, nullable=False)
    immediate = Column(Boolean, default=False, index=True)
    
    # Status tracking
    status = Column(String, default="waiting")  # waiting, in_treatment, completed
    assigned_to = Column(String, nullable=True)  # Staff member ID
    
    created_at = Column(DateTime, default=datetime.utcnow)


class NearbyHospital(Base):
    """Cache for nearby hospitals data"""
    __tablename__ = "nearby_hospitals"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    distance_km = Column(Float, nullable=False)
    travel_time_minutes = Column(Integer, nullable=False)
    
    # Simulated live data
    live_occupancy = Column(Float, default=50.0)
    estimated_wait_time = Column(Integer, default=30)
    
    # Facilities
    has_emergency = Column(Boolean, default=True)
    has_icu = Column(Boolean, default=False)
    phone = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    
    # Cache metadata
    last_updated = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Immutable audit trail for medical accountability"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    action = Column(String, nullable=False)  # e.g., "triage_assessment", "queue_entry", "priority_update"
    risk_level = Column(String, nullable=False)
    priority_score = Column(Float, nullable=False)
    
    rationale = Column(Text, nullable=False)  # Explainable AI reasoning
    feature_importance = Column(JSON, nullable=False)  # SHAP values
    
    user_email = Column(String, nullable=False)
    system_version = Column(String, nullable=False)
    
    # Make immutable
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
