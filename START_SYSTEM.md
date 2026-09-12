# 🧬 Project Bhishma's 2.0 - Complete System Startup Guide

## 🚀 **Quick Start (All Services)**

```bash
# Make executable and run
chmod +x start_fixed.sh
./start_fixed.sh
```

## 📋 **What the Script Does:**

### 🔧 **Backend Setup:**
- Creates Python virtual environment
- Installs all dependencies (Flask, pandas, scikit-learn, etc.)
- Sets up BioBERT risk analysis system
- Creates database and directories
- Configures environment variables
- Starts Flask server on port 8000

### 🎨 **Frontend Setup:**
- Installs Node.js dependencies
- Configures Vite for React
- Sets up CORS for API communication
- Starts React dev server on port 3000

### 🧬 **BioBERT System:**
- Risk analysis endpoints
- Drug testing pipeline
- Clinical trial prediction
- Survival analysis models
- Protocol NLP processing

### 🔍 **Health Checks:**
- Backend API health
- BioBERT endpoints status
- Frontend accessibility
- Database connectivity

## 🌐 **Services Available:**

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React UI for clinical trials |
| Backend API | http://localhost:8000 | Flask REST API |
| Health Check | http://localhost:8000/health | System status |
| Risk Analysis | http://localhost:8000/api/risk-analysis/upload | BioBERT drug analysis |
| Drug Testing | http://localhost:8000/api/drug-testing/upload | Multi-step pipeline |

## 🧪 **Test BioBERT System:**

```bash
# Quick test
cd backend
python3 quick_test_biobert.py

# Comprehensive test
python3 test_with_real_data.py

# Web interface test
open test_risk_analysis_web.html
```

## 📊 **Features Ready:**

### 🧬 **BioBERT Analysis:**
- Toxicity assessment
- Efficacy evaluation
- Molecular property analysis
- Clinical risk stratification
- Success probability calculation

### 🔬 **Clinical Trial Features:**
- Survival analysis (Kaplan-Meier)
- Protocol NLP analysis
- Patient data security (HIPAA)
- Drug mechanism analysis
- Probabilistic forecasting

### 📈 **Data Processing:**
- CSV upload and validation
- Missing value analysis
- Statistical summaries
- Data quality scoring
- Privacy protection

## 🛑 **Stop All Services:**

```bash
# Press Ctrl+C in the terminal running start_fixed.sh
# Or kill processes manually:
pkill -f "python.*app.py"
pkill -f "vite"
pkill -f "npm.*dev"
```

## 📝 **Logs Location:**
- Backend: `backend/logs/backend.log`
- Frontend: `backend/logs/frontend.log`

## ✅ **System Status:**
- ✅ All critical security issues fixed
- ✅ BioBERT risk analysis working
- ✅ No external API dependencies
- ✅ Complete full-stack system
- ✅ Ready for clinical trial analysis

**Run `./start_fixed.sh` to start the complete BioBERT Clinical Trial System!**