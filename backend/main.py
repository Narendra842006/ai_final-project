"""
FastAPI Main Application
Production-ready medical triage backend with security, audit trails, and CORS
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import pdfplumber
from io import BytesIO

from .database import init_db, get_db, Patient, HospitalQueue, AuditLog
from .models import (
    PatientInput, TriageResponse, QueueEntry, HospitalInfo,
    PDFUploadResponse, HealthCheckResponse, RiskLevel, Department,
    AuditLogEntry
)
from .priority_queue import global_queue
from .ml_service import ml_service
from .hospital_service import hospital_service
from . import __version__

# Initialize FastAPI app
app = FastAPI(
    title="Smart Medical Triage System API",
    description="AI-powered triage system with priority queue and hospital finder",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:8502", "*"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    init_db()
    print("🚀 FastAPI server started successfully")
    print(f"📊 API Version: {__version__}")
    print(f"🤖 ML Model Status: {'Loaded' if ml_service.model else 'Rule-based fallback'}")


# ==================== HEALTH CHECK ====================
@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify system status
    """
    try:
        # Check database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_connected = True
    except:
        db_connected = False
    
    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        version=__version__,
        timestamp=datetime.utcnow(),
        database_connected=db_connected,
        ml_model_loaded=ml_service.model is not None
    )


# ==================== TRIAGE PREDICTION ====================
@app.post("/api/v1/predict", response_model=TriageResponse, tags=["Triage"])
async def predict_triage(
    patient_input: PatientInput,
    db: Session = Depends(get_db)
):
    """
    **Main Triage Endpoint**
    
    Performs AI-powered risk assessment and returns:
    - Risk level classification
    - Priority score for queue placement
    - Department recommendation
    - Explainable medical advice (linked to SHAP values)
    - Position in queue
    
    **Features:**
    - RandomForest ML model (or rule-based fallback)
    - SHAP explainability for transparency
    - Dynamic priority queue insertion
    - Immutable audit logging
    """
    try:
        # Generate unique patient ID
        patient_id = str(uuid.uuid4())
        
        # 1. ML Inference
        risk_level, ai_confidence, feature_importance = ml_service.predict_risk(patient_input)
        department = ml_service.predict_department(patient_input, risk_level)
        
        # 2. Calculate Priority Score
        priority_score = global_queue.calculate_priority_score(
            risk_level=risk_level,
            heart_rate=patient_input.vitals.heart_rate,
            bp_systolic=patient_input.vitals.bp_systolic,
            bp_diastolic=patient_input.vitals.bp_diastolic,
            temperature=patient_input.vitals.temperature,
            age=patient_input.age,
            symptoms=patient_input.symptoms
        )
        
        # 3. Generate Explainable Medical Advice
        medical_advice = ml_service.generate_medical_advice(
            risk_level, feature_importance, patient_input.symptoms
        )
        
        # 4. Add to Priority Queue
        queue_entry = QueueEntry(
            patient_id=patient_id,
            email=patient_input.email,
            priority_score=priority_score,
            risk_level=risk_level,
            department=department,
            arrival_time=datetime.utcnow(),
            vitals_summary=f"HR:{patient_input.vitals.heart_rate} BP:{patient_input.vitals.bp_systolic}/{patient_input.vitals.bp_diastolic}",
            immediate=risk_level == RiskLevel.IMMEDIATE
        )
        position = global_queue.add_patient(queue_entry)
        
        # 5. Save to Database
        db_patient = Patient(
            id=patient_id,
            email=patient_input.email,
            age=patient_input.age,
            gender=patient_input.gender,
            vitals=patient_input.vitals.dict(),
            symptoms=patient_input.symptoms,
            medical_history=patient_input.medical_history,
            allergies=patient_input.allergies,
            current_medications=patient_input.current_medications,
            risk_level=risk_level.value,
            priority_score=priority_score,
            department=department.value,
            ai_confidence=ai_confidence,
            feature_importance=feature_importance
        )
        db.add(db_patient)
        
        # 6. Add to hospital queue table
        db_queue = HospitalQueue(
            patient_id=patient_id,
            email=patient_input.email,
            priority_score=priority_score,
            risk_level=risk_level.value,
            department=department.value,
            vitals_summary=queue_entry.vitals_summary,
            immediate=queue_entry.immediate
        )
        db.add(db_queue)
        
        # 7. Create Audit Log (Immutable)
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            action="triage_assessment",
            risk_level=risk_level.value,
            priority_score=priority_score,
            rationale=medical_advice,
            feature_importance=feature_importance,
            user_email=patient_input.email,
            system_version=__version__
        )
        db.add(audit_log)
        
        db.commit()
        
        # 8. Calculate estimated wait time
        estimated_wait = position * 15  # Assume 15 min per patient
        
        # 9. Return response
        return TriageResponse(
            patient_id=patient_id,
            risk_level=risk_level,
            priority_score=priority_score,
            department=department,
            estimated_wait_time=estimated_wait,
            position_in_queue=position,
            ai_confidence=ai_confidence,
            feature_importance=feature_importance,
            medical_advice=medical_advice,
            immediate_action_required=risk_level == RiskLevel.IMMEDIATE,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage prediction error: {str(e)}")


# ==================== PRIORITY QUEUE MANAGEMENT ====================
@app.get("/api/v1/queue", response_model=List[QueueEntry], tags=["Queue"])
async def get_queue(limit: int = 20):
    """
    Get current priority queue
    
    Returns patients sorted by priority (highest first)
    """
    queue_entries = global_queue.peek_queue(limit=limit)
    return queue_entries


@app.get("/api/v1/queue/{patient_id}/position", tags=["Queue"])
async def get_queue_position(patient_id: str):
    """Get patient's current position in queue"""
    position = global_queue.get_position(patient_id)
    if position == -1:
        raise HTTPException(status_code=404, detail="Patient not found in queue")
    
    return {"patient_id": patient_id, "position": position, "queue_size": global_queue.get_queue_size()}


@app.post("/api/v1/queue/{patient_id}/update-priority", tags=["Queue"])
async def update_patient_priority(
    patient_id: str,
    new_priority_score: float,
    db: Session = Depends(get_db)
):
    """
    **Dynamic Priority Re-ranking**
    
    Update patient priority in real-time (e.g., if vitals worsen)
    High-risk patients automatically move ahead of medium-risk
    """
    try:
        new_position = global_queue.update_priority(patient_id, new_priority_score)
        
        # Update database
        queue_entry = db.query(HospitalQueue).filter(HospitalQueue.patient_id == patient_id).first()
        if queue_entry:
            queue_entry.priority_score = new_priority_score
            db.commit()
        
        # Audit log
        audit = AuditLog(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            action="priority_update",
            risk_level=queue_entry.risk_level if queue_entry else "UNKNOWN",
            priority_score=new_priority_score,
            rationale=f"Priority dynamically updated to {new_priority_score}",
            feature_importance={},
            user_email="system",
            system_version=__version__
        )
        db.add(audit)
        db.commit()
        
        return {"patient_id": patient_id, "new_position": new_position, "new_priority": new_priority_score}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/v1/queue/{patient_id}", tags=["Queue"])
async def remove_from_queue(patient_id: str, db: Session = Depends(get_db)):
    """Remove patient from queue (after treatment)"""
    entry = global_queue.remove_patient(patient_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Patient not in queue")
    
    # Update database
    db.query(HospitalQueue).filter(HospitalQueue.patient_id == patient_id).update({"status": "completed"})
    db.commit()
    
    return {"message": "Patient removed from queue", "patient_id": patient_id}


# ==================== HOSPITAL FINDER ====================
@app.get("/api/v1/hospitals/nearby", response_model=List[HospitalInfo], tags=["Hospitals"])
async def get_nearby_hospitals(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    limit: int = 5
):
    """
    **Find Nearby Hospitals**
    
    Uses Google Maps API to find hospitals within radius
    
    Returns:
    - Hospital name, address, distance
    - Live occupancy percentage (simulated)
    - Estimated wait time based on queue status
    - Travel time estimate
    """
    hospitals = hospital_service.get_nearby_hospitals(latitude, longitude, radius_km, limit)
    return hospitals


# ==================== PDF PROCESSING ====================
@app.post("/api/v1/upload-pdf", response_model=PDFUploadResponse, tags=["Documents"])
async def upload_medical_pdf(
    file: UploadFile = File(...),
    auto_predict: bool = False
):
    """
    **Upload Medical Record PDF**
    
    Extracts vital signs from PDF using pdfplumber
    Optionally runs automatic triage prediction
    
    Supports standard medical record formats
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF
        pdf_content = await file.read()
        pdf_file = BytesIO(pdf_content)
        
        # Extract text using pdfplumber
        extracted_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"
        
        # Extract vitals using regex
        vitals = extract_vitals_from_pdf_text(extracted_text)
        
        response = PDFUploadResponse(
            extracted_vitals=vitals,
            extracted_text=extracted_text[:500],  # First 500 chars
            confidence=0.85  # Placeholder
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")


def extract_vitals_from_pdf_text(text: str):
    """Extract vital signs from PDF text using regex"""
    import re
    from .models import VitalSigns
    
    # Default values
    vitals_data = {
        'heart_rate': 75.0,
        'bp_systolic': 120.0,
        'bp_diastolic': 80.0,
        'temperature': 98.6
    }
    
    # Pattern matching
    hr_pattern = r'(?:heart rate|hr|pulse)[:\s]+(\d+)'
    bp_pattern = r'(?:blood pressure|bp)[:\s]+(\d+)/(\d+)'
    temp_pattern = r'(?:temperature|temp)[:\s]+(\d+\.?\d*)'
    
    hr_match = re.search(hr_pattern, text.lower())
    if hr_match:
        vitals_data['heart_rate'] = float(hr_match.group(1))
    
    bp_match = re.search(bp_pattern, text.lower())
    if bp_match:
        vitals_data['bp_systolic'] = float(bp_match.group(1))
        vitals_data['bp_diastolic'] = float(bp_match.group(2))
    
    temp_match = re.search(temp_pattern, text.lower())
    if temp_match:
        vitals_data['temperature'] = float(temp_match.group(1))
    
    return VitalSigns(**vitals_data)


# ==================== AUDIT TRAIL ====================
@app.get("/api/v1/audit/{patient_id}", response_model=List[AuditLogEntry], tags=["Audit"])
async def get_audit_trail(patient_id: str, db: Session = Depends(get_db)):
    """
    **Immutable Audit Trail**
    
    Retrieve complete audit history for a patient
    Ensures medical accountability and transparency
    """
    logs = db.query(AuditLog).filter(AuditLog.patient_id == patient_id).order_by(AuditLog.created_at.desc()).all()
    
    return [
        AuditLogEntry(
            log_id=log.id,
            patient_id=log.patient_id,
            timestamp=log.created_at,
            action=log.action,
            risk_level=RiskLevel(log.risk_level),
            priority_score=log.priority_score,
            rationale=log.rationale,
            feature_importance=log.feature_importance,
            user_email=log.user_email,
            system_version=log.system_version
        )
        for log in logs
    ]


# ==================== ROOT ====================
@app.get("/", tags=["System"])
async def root():
    """API Root - Welcome message"""
    return {
        "message": "Smart Medical Triage System API",
        "version": __version__,
        "docs": "/api/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
