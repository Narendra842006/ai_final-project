# 🏥 Smart Medical Triage System - Installation Guide

## 📦 Quick Installation

### For Streamlit Frontend Only:
```bash
pip install -r requirements.txt
```

### For FastAPI Backend Only:
```bash
pip install -r requirements_backend.txt
```

### For Complete System (Both Frontend + Backend):
```bash
pip install -r requirements.txt
pip install -r requirements_backend.txt
```

---

## 📋 Detailed Installation Steps

### **Option 1: Streamlit Frontend Only (Recommended for Quick Start)**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**
   ```bash
   streamlit run triage_app.py
   ```

3. **Access the App**
   - Open browser: http://localhost:8502
   - Login as Patient or Hospital Staff

**Dependencies Installed:**
- `streamlit` - Web framework
- `PyPDF2` - PDF processing
- `pandas` - Data manipulation
- `numpy` - Numerical operations

---

### **Option 2: FastAPI Backend (For Advanced Features)**

1. **Install Backend Dependencies**
   ```bash
   pip install -r requirements_backend.txt
   ```

2. **Run the Backend**
   ```bash
   # Option A: Using batch script (Windows)
   start_backend.bat

   # Option B: Manual start
   uvicorn backend.main:app --reload --port 8000
   ```

3. **Test the API**
   ```bash
   python test_backend.py
   ```

4. **View API Docs**
   - Swagger UI: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health

**Dependencies Installed:**
- `fastapi` - REST API framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `pdfplumber` - Advanced PDF extraction
- `googlemaps` - Hospital finder
- `scikit-learn` - Machine learning
- `shap` - AI explainability
- And more...

---

### **Option 3: Complete System (Frontend + Backend)**

1. **Install All Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_backend.txt
   ```

2. **Start Backend (Terminal 1)**
   ```bash
   start_backend.bat
   # Wait for: "🚀 FastAPI server started successfully"
   ```

3. **Start Frontend (Terminal 2)**
   ```bash
   streamlit run triage_app.py
   ```

4. **Access**
   - Frontend: http://localhost:8502
   - Backend API: http://localhost:8000/api/docs

---

## 🔧 System Requirements

- **Python**: 3.8 or higher (Python 3.10+ recommended)
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB
- **Storage**: 500MB free space

---

## ✅ Installation Verification

### Check Python Version:
```bash
python --version
# Should show: Python 3.8.x or higher
```

### Check pip:
```bash
pip --version
```

### Verify Streamlit Installation:
```bash
streamlit --version
```

### Verify FastAPI Installation:
```bash
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "pip not found"
**Solution:**
```bash
# Windows
python -m pip install --upgrade pip

# Mac/Linux
python3 -m pip install --upgrade pip
```

### Issue 2: "Permission denied"
**Solution:**
```bash
# Add --user flag
pip install --user -r requirements.txt
```

### Issue 3: "Module not found" errors
**Solution:**
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Issue 4: "Port already in use"
**Solution:**
```bash
# For Streamlit (change port)
streamlit run triage_app.py --server.port 8503

# For FastAPI (change port)
uvicorn backend.main:app --port 8001
```

### Issue 5: "SQLAlchemy errors" (Backend only)
**Solution:**
The backend uses SQLite by default (no setup needed).
For PostgreSQL, install:
```bash
pip install psycopg2-binary
```

---

## 📚 Optional: Virtual Environment (Recommended)

### Create Virtual Environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install in Virtual Environment:
```bash
pip install -r requirements.txt
pip install -r requirements_backend.txt
```

### Deactivate:
```bash
deactivate
```

---

## 🎯 What to Install Based on Your Needs:

| Use Case | Install | Run |
|----------|---------|-----|
| **Just want to test the app** | `requirements.txt` | `streamlit run triage_app.py` |
| **Want to use AI features** | Both files | Backend first, then frontend |
| **Want to customize API** | `requirements_backend.txt` | `start_backend.bat` |
| **Production deployment** | Both + PostgreSQL | See backend/README.md |

---

## 📖 Next Steps After Installation:

1. **Frontend Only**:
   - Run: `streamlit run triage_app.py`
   - Login with any email
   - Try patient triage workflow

2. **Backend Only**:
   - Run: `start_backend.bat`
   - Visit: http://localhost:8000/api/docs
   - Try API endpoints in Swagger UI

3. **Full System**:
   - Start backend first
   - Then start frontend
   - Use integrated AI features
   - Test hospital finder
   - Try PDF upload

---

## 🔑 API Keys (Optional)

For hospital finder to work with real Google Maps data:

1. Get API key: https://console.cloud.google.com/google/maps-apis
2. Edit `.env` file:
   ```
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   ```

**Note:** App works fine without API key (uses fallback hospital data)

---

## 📞 Getting Help

- **Check logs** for error messages
- **Run test script**: `python test_backend.py`
- **Health check**: http://localhost:8000/health
- **Streamlit debug**: Run with `--logger.level=debug`

---

**Ready to Start! 🚀**

1. Install: `pip install -r requirements.txt`
2. Run: `streamlit run triage_app.py`
3. Enjoy! 🎉
