# 🚀 Refinify 2.0 - AI-Powered Data Processing Platform

[![GitHub](https://img.shields.io/badge/GitHub-Refinify--2.0-blue?logo=github)](https://github.com/Darshan1814/Refinify-2.0)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.2-000000?logo=flask)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-4285F4?logo=google)](https://ai.google.dev/)
[![Apache Airflow](https://img.shields.io/badge/Apache-Airflow-017CEE?logo=apache-airflow)](https://airflow.apache.org/)

> **Advanced AI-powered data cleaning, augmentation, and processing pipeline with real-time voice commands, natural language processing, and automated workflows.**

## ✨ Features

### 🤖 AI-Powered Processing
- **Real-Time Augmentation** with Gemini AI integration
- **Voice Command Processing** for natural data manipulation
- **Multi-Model Typo Correction** (Gemini AI, T5, BERT, HuggingFace)
- **Natural Language Data Queries** and processing

### 📊 Data Processing
- **CSV/Excel File Upload** with intelligent parsing
- **Automated Data Cleaning** and validation
- **Missing Value Imputation** (Mean, Median, KNN)
- **Outlier Detection** (IQR, Z-Score, Isolation Forest)
- **Synthetic Data Generation** for augmentation

### 🔄 Automation & Pipeline
- **Apache Airflow Integration** for automated workflows
- **Scheduled Data Processing** with monitoring
- **Real-time Health Checks** and status monitoring
- **Automated Report Generation** (PDF/HTML)

### 🎨 Modern UI/UX
- **React 19** with latest features
- **Full-Screen Layouts** with no white space issues
- **Beautiful Gradient Designs** and animations
- **Responsive Grid Layouts** for all screen sizes
- **Real-time Chat Interface** with AI assistant

### 🔒 Security & Privacy
- **Data Encryption** with enterprise-grade protection
- **Privacy-Preserving Processing** with PBKDF2
- **Secure File Handling** and validation
- **Role-based Access Control** with admin dashboard

## 🛠️ Tech Stack

### Frontend
- **React 19** - Latest React with concurrent features
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Router DOM** - Client-side routing
- **React Icons** - Beautiful icon library

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Gemini AI** - Google's advanced AI model
- **Pandas & NumPy** - Data processing libraries
- **Apache Airflow** - Workflow orchestration

### AI & ML
- **Gemini 1.5 Flash** - Advanced language model
- **HuggingFace Transformers** - Pre-trained models
- **Scikit-learn** - Machine learning algorithms
- **T5 Large** - Text-to-text transformer

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18 or higher)
- **Python 3.9+**
- **npm** or **yarn**
- **Git**

### One-Command Setup
```bash
git clone https://github.com/Darshan1814/Refinify-2.0.git
cd Refinify-2.0
chmod +x start_all_services.sh
./start_all_services.sh
```

### Manual Setup

#### 1. Clone Repository
```bash
git clone https://github.com/Darshan1814/Refinify-2.0.git
cd Refinify-2.0
```

#### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### 4. Apache Airflow (Optional)
```bash
cd backend
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow users create --username admin --password admin123 --firstname Admin --lastname User --role Admin --email admin@refinify.com
airflow webserver --port 8080 --daemon
airflow scheduler --daemon
```

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **Airflow UI** | http://localhost:8080 | Workflow management |
| **Health Check** | http://localhost:8000/health | System status |

## 🎯 Key Pages & Features

### 📊 Real-Time Augmentation (`/augmentation`)
- Upload CSV/Excel files
- Voice command processing
- Gemini AI integration
- Real-time data transformation
- Download processed results

### ✏️ AI Typo Correction (`/typo-correction`)
- Multiple AI models (Gemini, T5, BERT)
- Batch text processing
- Comprehensive comparison
- Export corrected text

### 🤖 AI Data Assistant (`/ai-assistant`)
- Natural language queries
- Interactive data exploration
- Smart recommendations
- Export capabilities

### 📈 Analytics Dashboard (`/analytics`)
- Data visualization
- Statistical analysis
- Custom chart generation
- Performance metrics

## 🔧 Configuration

### Environment Variables

#### Backend (`.env`)
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
UPLOAD_FOLDER=uploads
```

#### Frontend (`.env`)
```env
VITE_APP_NAME=Refinify
VITE_APP_VERSION=2.0.0
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_DESCRIPTION=AI-Powered Data Processing Platform
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - User logout

### Data Processing
- `POST /api/augmentation/upload` - Upload dataset
- `POST /api/augmentation/process-command` - Process with AI
- `POST /api/typo/correct` - Correct text with AI
- `POST /clean` - Clean and process data

### Analytics
- `POST /api/analytics/generate` - Generate analytics
- `POST /api/analytics/custom-chart` - Create custom charts
- `GET /api/analytics/user-datasets` - Get user datasets

## 🧪 Testing

### Test Gemini AI Integration
```bash
cd backend
source venv/bin/activate
python -c "
import requests
api_key = 'your_api_key'
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
response = requests.post(url, json={'contents': [{'parts': [{'text': 'Hello'}]}]})
print('✅ API Working' if response.status_code == 200 else '❌ API Error')
"
```

### Test Frontend
1. Go to http://localhost:3000/augmentation
2. Upload a CSV file
3. Type: "fix negative ages"
4. Click "Send to AI"
5. Should show "Analyzing..." then complete

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill processes on specific ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8080 | xargs kill -9  # Airflow
```

#### Python Virtual Environment Issues
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Node.js Dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🔄 Recent Updates (v2.0)

### ✅ Fixed Issues
- **Layout Spacing**: Fixed white space between sidebar and main content
- **JSX Runtime**: Resolved React JSX boolean attribute errors
- **Error Handling**: Added proper null checks and error boundaries
- **Gemini Integration**: Improved API integration and error handling
- **Data Processing**: Enhanced CSV processing with real data

### 🆕 New Features
- **Apache Airflow**: Complete workflow automation
- **Voice Commands**: Real-time voice processing
- **Enhanced UI**: Full-screen layouts with beautiful gradients
- **Better Error Handling**: Comprehensive error boundaries
- **Improved Performance**: Optimized data processing

## 📊 Project Structure

```
Refinify-2.0/
├── frontend/                 # React 19 + Vite frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── context/        # React Context
│   │   └── config.js       # Configuration
│   ├── package.json
│   └── vite.config.js
├── backend/                 # Flask backend
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── airflow_dags/       # Airflow DAG files
│   └── uploads/            # File upload directory
├── start_all_services.sh   # Complete startup script
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Look at the logs in `backend.log` and `frontend.log`
3. Verify all services are running with health checks
4. Open an issue on GitHub with detailed information

## 🌟 Acknowledgments

- **Google Gemini AI** for advanced language processing
- **HuggingFace** for transformer models
- **Apache Airflow** for workflow orchestration
- **React Team** for the amazing framework
- **Tailwind CSS** for beautiful styling

---

**Built with ❤️ for AI-powered data processing**

[![GitHub stars](https://img.shields.io/github/stars/Darshan1814/Refinify-2.0?style=social)](https://github.com/Darshan1814/Refinify-2.0/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Darshan1814/Refinify-2.0?style=social)](https://github.com/Darshan1814/Refinify-2.0/network/members)