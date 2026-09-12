# 🚀 **Refinify-AI Startup Guide**

## 📋 **Available Startup Scripts**

### **1. `start_all_services.bat` - RECOMMENDED**
**Interactive menu with all options:**
- Start Everything (Backend + Frontend + Airflow + Windows Automation)
- Start individual services
- Check service status
- Stop all services

**Usage:** Double-click `start_all_services.bat`

### **2. `start_services.bat` - Start Everything**
**Automatically starts all services:**
- Flask Backend (Port 8000)
- React Frontend (Port 3000)
- Apache Airflow (Port 8080)
- Windows Automation System

**Usage:** Double-click `start_services.bat`

### **3. `backend/start_airflow_windows.bat` - Airflow Only**
**Starts Apache Airflow services:**
- Webserver (Port 8080)
- Scheduler
- Worker

**Usage:** Double-click `backend/start_airflow_windows.bat`

### **4. `backend/start_windows_automation.bat` - Windows Automation Only**
**Starts the Windows automation system**

**Usage:** Double-click `backend/start_windows_automation.bat`

## 🌐 **Service URLs & Ports**

| Service | Port | URL | Login |
|---------|------|-----|-------|
| **Backend** | 8000 | http://localhost:8000 | admin/admin123 |
| **Frontend** | 3000 | http://localhost:3000 | admin/admin123 |
| **Airflow** | 8080 | http://localhost:8080 | admin/admin |
| **Health Check** | 8000 | http://localhost:8000/health | - |

## 🎯 **Quick Start Options**

### **Option A: Start Everything (Recommended)**
```bash
# Double-click this file:
start_all_services.bat
# Then choose option 1
```

### **Option B: Start Services Individually**
```bash
# 1. Start Backend
cd backend
python start_simple.py

# 2. Start Frontend (in new terminal)
cd frontend
npm run dev

# 3. Start Airflow (in new terminal)
cd backend
start_airflow_windows.bat
```

### **Option C: Use Docker (if available)**
```bash
docker-compose -f docker-compose.airflow.yml up -d
```

## ⚠️ **Prerequisites**

### **Required Software:**
- ✅ Python 3.12+
- ✅ Node.js & npm
- ✅ Apache Airflow (if using Airflow features)

### **Required Packages:**
```bash
cd backend
pip install -r requirements.txt
```

### **First Time Setup:**
```bash
cd backend
python airflow_setup.py
```

## 🔧 **Troubleshooting**

### **Port Already in Use:**
```bash
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3000
netstat -ano | findstr :8080

# Kill the process
taskkill /PID <PID> /F
```

### **Service Not Starting:**
1. Check if Python/Node.js is in PATH
2. Verify all packages are installed
3. Check firewall settings
4. Ensure no other services are using the ports

### **Airflow Issues:**
1. Run `python airflow_setup.py` first
2. Check if Airflow is installed: `pip show apache-airflow`
3. Verify environment variables are set

## 📱 **Mobile Access**

### **Local Network Access:**
- Find your IP: `ipconfig`
- Access from other devices: `http://YOUR_IP:3000`

### **Port Forwarding (for external access):**
- Backend: 8000
- Frontend: 3000
- Airflow: 8080

## 🎉 **Success Indicators**

### **Backend Running:**
- ✅ http://localhost:8000/health returns status
- ✅ No error messages in terminal

### **Frontend Running:**
- ✅ http://localhost:3000 loads React app
- ✅ npm shows "Local:" in terminal

### **Airflow Running:**
- ✅ http://localhost:8080 shows login page
- ✅ Can login with admin/admin
- ✅ DAGs are visible

### **Windows Automation:**
- ✅ `automation.log` file is created
- ✅ No error messages in terminal

## 🚨 **Emergency Stop**

### **Stop All Services:**
```bash
# Use the menu option 9, or manually:
taskkill /f /im python.exe
taskkill /f /im node.exe
```

### **Stop Specific Service:**
```bash
# Find process
netstat -ano | findstr :8000
# Kill by PID
taskkill /PID <PID> /F
```

---

**💡 Pro Tip:** Use `start_all_services.bat` for the best experience - it gives you a menu to choose exactly what you want to start!
