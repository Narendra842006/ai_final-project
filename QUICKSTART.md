# 🚀 Quick Start Guide

## For the Impatient (2 Steps):

### **Option 1: Just run the app (Recommended)**
```bash
1. Double-click: install.bat
2. Double-click: run.bat (or type: streamlit run triage_app.py)
3. Open: http://localhost:8502
```

### **Option 2: Full system with API backend**
```bash
1. Double-click: install_all.bat
2. Open 2 terminals:
   - Terminal 1: start_backend.bat
   - Terminal 2: streamlit run triage_app.py
3. Open: http://localhost:8502
```

---

## 📦 What Files to Install:

| File | What it does | Required? |
|------|-------------|-----------|
| **requirements.txt** | Streamlit frontend deps | ✅ **YES** |
| **requirements_backend.txt** | FastAPI backend deps | ⚪ Optional (for advanced features) |

---

## 🎯 Simple Installation (3 Commands):

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run triage_app.py

# 3. Open browser (automatic)
# http://localhost:8502
```

---

## 🔧 What Gets Installed:

### Frontend Only (`requirements.txt`):
- ✅ `streamlit` - Web framework
- ✅ `pandas` - Data processing
- ✅ `numpy` - Math operations
- ✅ `PyPDF2` - PDF reading

**Total size:** ~200MB  
**Install time:** 1-2 minutes

### Backend (`requirements_backend.txt`) - Optional:
- ✅ `fastapi` - REST API
- ✅ `uvicorn` - Web server
- ✅ `sqlalchemy` - Database
- ✅ `scikit-learn` - Machine learning
- ✅ `pdfplumber` - Advanced PDF processing
- ✅ `googlemaps` - Hospital finder
- ✅ Plus 20+ more packages

**Total size:** ~800MB  
**Install time:** 3-5 minutes

---

## ✅ Verification:

After installation, run:
```bash
python -c "import streamlit; print('Streamlit OK')"
python -c "import pandas; print('Pandas OK')"
```

Should see:
```
Streamlit OK
Pandas OK
```

---

## 🎓 Sample Usage:

1. **Run the app**
   ```bash
   streamlit run triage_app.py
   ```

2. **Login** (use any email)
   - Email: `test@example.com`
   - Password: `password`
   - Role: Patient or Hospital Staff

3. **Try features**:
   - Patient Portal → Enter symptoms → Get risk assessment
   - Hospital Dashboard → View patient queue
   - AI Chatbot → Ask medical questions (5 languages!)

---

## 🐛 Troubleshooting:

### "Command not found: streamlit"
```bash
pip install streamlit
```

### "Port 8502 already in use"
```bash
streamlit run triage_app.py --server.port 8503
```

### "Module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📱 Quick Reference:

| Action | Command |
|--------|---------|
| Install | `pip install -r requirements.txt` |
| Run | `streamlit run triage_app.py` |
| Stop | Press `Ctrl+C` in terminal |
| Reinstall | `pip install -r requirements.txt --force-reinstall` |
| Check version | `streamlit --version` |

---

**That's it! You're ready to go! 🎉**

See `INSTALLATION.md` for detailed instructions.
