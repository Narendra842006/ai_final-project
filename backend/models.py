"""
Pydantic Models for API Request/Response Validation
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    IMMEDIATE = "IMMEDIATE"


class Department(str, Enum):
    """Hospital department enumeration"""
    EMERGENCY = "Emergency"
    CARDIOLOGY = "Cardiology"
    GENERAL = "General Medicine"
    PEDIATRICS = "Pediatrics"
    SURGERY = "Surgery"
    ICU = "Intensive Care"


class VitalSigns(BaseModel):
    """Vital signs data model"""
    heart_rate: float = Field(..., ge=30, le=250, description="Heart rate in BPM")
    bp_systolic: float = Field(..., ge=60, le=250, description="Systolic blood pressure")
    bp_diastolic: float = Field(..., ge=40, le=150, description="Diastolic blood pressure")
    temperature: float = Field(..., ge=90, le=110, description="Temperature in Fahrenheit")
    oxygen_saturation: Optional[float] = Field(None, ge=0, le=100, description="SpO2 percentage")
    respiratory_rate: Optional[float] = Field(None, ge=8, le=60, description="Breaths per minute")
    
    @validator('bp_systolic', 'bp_diastolic')
    def validate_bp(cls, v, field):
        if field.name == 'bp_systolic' and v < 70:
            raise ValueError("Systolic BP critically low")
        if field.name == 'bp_diastolic' and v > v:
            raise ValueError("Diastolic BP cannot exceed systolic")
        return v


class PatientInput(BaseModel):
    """Patient input for triage assessment"""
    email: EmailStr
    age: int = Field(..., ge=0, le=120, description="Patient age")
    gender: str = Field(..., description="Patient gender")
    vitals: VitalSigns
    symptoms: List[str] = Field(..., min_items=1, description="List of symptoms")
    medical_history: Optional[List[str]] = Field(default=[], description="Previous conditions")
    allergies: Optional[List[str]] = Field(default=[], description="Known allergies")
    current_medications: Optional[List[str]] = Field(default=[], description="Current medications")


class TriageResponse(BaseModel):
    """Triage system response"""
    patient_id: str
    risk_level: RiskLevel
    priority_score: float = Field(..., ge=0, le=100, description="Calculated priority score")
    department: Department
    estimated_wait_time: int = Field(..., description="Estimated wait in minutes")
    position_in_queue: int
    ai_confidence: float = Field(..., ge=0, le=1, description="AI confidence score")
    feature_importance: Dict[str, float] = Field(..., description="SHAP feature importance")
    medical_advice: str = Field(..., description="Explainable medical advice")
    immediate_action_required: bool
    timestamp: datetime


class QueueEntry(BaseModel):
    """Priority queue entry"""
    patient_id: str
    email: EmailStr
    priority_score: float
    risk_level: RiskLevel
    department: Department
    arrival_time: datetime
    vitals_summary: str
    immediate: bool


class HospitalInfo(BaseModel):
    """Nearby hospital information"""
    name: str
    address: str
    distance_km: float
    travel_time_minutes: int
    live_occupancy: float = Field(..., ge=0, le=100, description="Occupancy percentage")
    estimated_wait_time: int
    has_emergency: bool
    has_icu: bool
    phone: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)


class AuditLogEntry(BaseModel):
    """Immutable audit log for accountability"""
    log_id: str
    patient_id: str
    timestamp: datetime
    action: str
    risk_level: RiskLevel
    priority_score: float
    rationale: str
    feature_importance: Dict[str, float]
    user_email: str
    system_version: str


class PDFUploadResponse(BaseModel):
    """Response from PDF upload endpoint"""
    extracted_vitals: VitalSigns
    extracted_text: str
    confidence: float
    triage_result: Optional[TriageResponse] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    database_connected: bool
    ml_model_loaded: bool
