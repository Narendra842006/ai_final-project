# Smart Medical Triage System - FastAPI Backend

## 🚀 Production-Ready Features

### ✅ Implemented Features

1. **AI-Powered Triage** (`/api/v1/predict`)
   - RandomForest ML model with rule-based fallback
   - SHAP explainability for transparent decisions
   - Risk level classification (Immediate, High, Medium, Low)
   - Department recommendation
   - Explainable medical advice linked to AI reasoning

2. **Real-Time Priority Queue** 
   - Max-Heap algorithm for O(log n) insertion/deletion
   - Dynamic priority re-ranking
   - Automatic high-risk patient prioritization
   - Priority score based on vitals + AI risk + age + symptoms

3. **Hospital Finder** (`/api/v1/hospitals/nearby`)
   - Google Maps API integration
   - Live occupancy simulation (0-100%)
   - Estimated wait time calculation
   - Distance and travel time estimates

4. **PDF Processing** (`/api/v1/upload-pdf`)
   - Extract vitals from medical records using pdfplumber
   - Regex-based vital sign detection
   - Optional auto-prediction after extraction

5. **Immutable Audit Trail** (`/api/v1/audit/{patient_id}`)
   - Complete history of all triage decisions
   - SHAP values logged for accountability
   - Timestamp + rationale for every action
   - Ensures medical compliance

6. **Database Support**
   - PostgreSQL for production
   - SQLite for development/prototyping
   - SQLAlchemy ORM with migrations
   - Tables: Patients, Hospital_Queue, Audit_Logs, Nearby_Hospitals

7. **Security Best Practices**
   - Environment variables for API keys (`.env` file)
   - CORS middleware for frontend integration
   - Input validation with Pydantic
   - SQL injection protection via ORM

## 📦 Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements_backend.txt
```

### 3. Configure Environment Variables
```bash
# Copy template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and add your Google Maps API key
# Get key from: https://console.cloud.google.com/google/maps-apis
```

### 4. Initialize Database
```bash
# Database tables will be created automatically on first run
python -m backend.main
```

## 🏃 Running the Server

### Development Mode (Auto-reload)
```bash
uvicorn backend.main:app --reload --port 8000
```

### Production Mode
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## 🔑 API Endpoints

### Triage & Prediction
- `POST /api/v1/predict` - Main triage assessment
- `GET /api/v1/queue` - View priority queue
- `GET /api/v1/queue/{patient_id}/position` - Get queue position
- `POST /api/v1/queue/{patient_id}/update-priority` - Dynamic re-ranking
- `DELETE /api/v1/queue/{patient_id}` - Remove from queue

### Hospital Finder
- `GET /api/v1/hospitals/nearby?latitude=X&longitude=Y` - Find nearby hospitals

### Documents
- `POST /api/v1/upload-pdf` - Upload and extract vitals from PDF

### Audit & Compliance
- `GET /api/v1/audit/{patient_id}` - Get immutable audit trail

### System
- `GET /health` - Health check
- `GET /` - API info

## 🧪 Example API Calls

### 1. Triage Prediction
```python
import requests

data = {
    "email": "patient@example.com",
    "age": 45,
    "gender": "Male",
    "vitals": {
        "heart_rate": 110,
        "bp_systolic": 165,
        "bp_diastolic": 95,
        "temperature": 101.5
    },
    "symptoms": ["chest pain", "shortness of breath"],
    "medical_history": ["hypertension"],
    "allergies": [],
    "current_medications": ["lisinopril"]
}

response = requests.post("http://localhost:8000/api/v1/predict", json=data)
print(response.json())
```

### 2. Find Nearby Hospitals
```python
response = requests.get(
    "http://localhost:8000/api/v1/hospitals/nearby",
    params={"latitude": 40.7128, "longitude": -74.0060, "radius_km": 5}
)
print(response.json())
```

### 3. Upload PDF
```python
with open("medical_record.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/v1/upload-pdf", files=files)
print(response.json())
```

## 🗄️ Database Schema

### Patients Table
- Patient demographics, vitals, symptoms
- AI predictions and confidence scores
- Feature importance (SHAP values)

### Hospital_Queue Table
- Real-time priority queue
- Priority score, risk level, department
- Arrival time, status tracking

### Audit_Logs Table
- **Immutable** - Never deleted or modified
- Complete triage decision history
- Rationale + SHAP values for accountability

### Nearby_Hospitals Table
- Cached hospital data from Google Maps
- Live occupancy and wait time simulations

## 🔒 Security Features

1. **Environment Variables** - Never hardcode API keys
2. **CORS Protection** - Only allow trusted origins
3. **Input Validation** - Pydantic models prevent injection
4. **Audit Logging** - Track every decision for compliance
5. **HTTPS Ready** - Deploy behind reverse proxy (nginx/traefik)

## 📊 Priority Score Algorithm

```
Priority Score = Base Score + Vital Severity + Age Factor + Symptom Severity

Base Scores:
- IMMEDIATE: 100
- HIGH: 70
- MEDIUM: 40
- LOW: 10

Vital Severity (0-20 points):
- Critical heart rate abnormalities: +10
- Severe hypertension/hypotension: +10
- High fever or hypothermia: +5

Age Factor (0-10 points):
- Elderly (>65): +5
- Pediatric (<5): +5
- Infant (<1): +10

Symptom Severity (0-10 points):
- Critical symptoms (chest pain, stroke, etc.): +5
```

## 🎯 Key Innovations

1. **Dynamic Re-ranking**: High-risk patients automatically moved ahead in queue
2. **Explainable Advice**: Medical advice directly linked to SHAP feature importance
3. **Live Occupancy**: Hospital wait times based on current queue status
4. **Audit Trail**: Immutable logging for medical accountability
5. **PDF Intelligence**: Automatic vital extraction from medical records

## 🔄 Integration with Streamlit Frontend

The FastAPI backend is designed to work seamlessly with your existing Streamlit app:

1. Add API calls to Streamlit pages using `requests` library
2. CORS is pre-configured for localhost:8501 and 8502
3. Use `/api/v1/predict` endpoint instead of local ML logic
4. Display queue position and hospital recommendations

## 📈 Production Deployment

### PostgreSQL Setup
```sql
CREATE DATABASE triage_db;
CREATE USER triage_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE triage_db TO triage_user;
```

### Update .env
```
DATABASE_URL=postgresql://triage_user:secure_password@localhost:5432/triage_db
```

### Run with Gunicorn (Production Server)
```bash
pip install gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧠 ML Model Training (Optional)

To replace the rule-based system with a trained model:

1. Collect labeled medical data
2. Train RandomForest classifier
3. Save model using joblib:
```python
import joblib
joblib.dump(model, 'models/triage_model.pkl')
```
4. Backend will automatically load it on startup

## 📞 Support

For issues or questions:
- Check API docs: http://localhost:8000/api/docs
- Review audit logs for debugging
- Check `/health` endpoint for system status

---

**Built with FastAPI, SQLAlchemy, SHAP, and Google Maps API**
**Version: 1.0.0**
