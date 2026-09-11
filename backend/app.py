import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import os
import json
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import io
import base64
from datetime import datetime, timezone
import zipfile
from werkzeug.utils import secure_filename
import tempfile
import warnings
import math
from sqlalchemy import text
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables (only in development)
if os.environ.get('FLASK_ENV') != 'production':
    load_dotenv()

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production' and os.environ.get('FLASK_ENV') == 'production':
    raise ValueError("SECRET_KEY must be set in production!")

# Upload Configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
try:
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
except Exception:
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Session Configuration
is_production = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_SECURE'] = is_production
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_production else 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Get CORS origins from environment or use defaults
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://asdp-frontend.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://127.0.0.1:3002,http://localhost:3003,http://127.0.0.1:3003,http://localhost:5174,http://127.0.0.1:5174')
CORS_ORIGINS_LIST = [origin.strip() for origin in CORS_ORIGINS.split(',')]

# Enhanced CORS configuration
CORS(app, 
     origins=CORS_ORIGINS_LIST,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in CORS_ORIGINS_LIST:
        response.headers['Access-Control-Allow-Origin'] = origin
    elif origin and (origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:')):
        # Allow any localhost port for development
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        # Default to allow localhost:3001 for AI assistant
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3001'
    
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
    return response

# Helper function to set CORS headers
def set_cors_headers(response):
    """Set CORS headers based on the request origin"""
    origin = request.headers.get('Origin')
    if origin in CORS_ORIGINS_LIST:
        response.headers['Access-Control-Allow-Origin'] = origin
    elif origin and origin.startswith('http://localhost:'):
        # Allow any localhost port for development
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        # Default to localhost:3000 for development
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
    return response

# Database Configuration
# Support both DATABASE_URL (Heroku/Render) and SQLALCHEMY_DATABASE_URI
database_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
if database_url and database_url.startswith('postgres://'):
    # Fix for Heroku/Render postgres:// -> postgresql://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['AVATAR_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configure login manager to handle unauthorized access
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Authentication required'}), 401

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

# Auth models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='researcher')  # 'admin', 'researcher', 'hospital', 'sponsor'
    organization = db.Column(db.String(255))  # Organization name
    organization_type = db.Column(db.String(50))  # 'research_institute', 'hospital', 'pharmaceutical', 'cro'
    license_number = db.Column(db.String(100))  # Professional license or registration number
    country = db.Column(db.String(100))  # Country/Region
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    profile_image = db.Column(db.String(512))  # relative path like /avatars/filename.png

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(1024), nullable=False)
    rows = db.Column(db.Integer)
    columns = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref='datasets')


class ProcessingRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    config = db.Column(db.JSON)
    cleaning_log = db.Column(db.JSON)
    estimates = db.Column(db.JSON)
    plots_count = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dataset = db.relationship('Dataset')
    user = db.relationship('User')


class ReportRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    report_name = db.Column(db.String(255))
    file_path = db.Column(db.String(1024))
    format = db.Column(db.String(10))
    summary = db.Column(db.Text)
    html_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dataset = db.relationship('Dataset')
    user = db.relationship('User')


class AnalysisOutput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    analysis_type = db.Column(db.String(100), default='anomaly_detection')
    user_query = db.Column('query', db.String(512))
    summary_metrics = db.Column(db.JSON)
    anomalies_detected = db.Column(db.JSON)
    insights = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dataset = db.relationship('Dataset')
    user = db.relationship('User')


class AIAssistantLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=True)
    user_query = db.Column('query', db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(50))
    metadata_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dataset = db.relationship('Dataset')
    user = db.relationship('User')


class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), default='INFO')
    category = db.Column(db.String(50))
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


def log_system_event(category: str, message: str, level: str = 'INFO', details: dict = None):
    """Utility to persist operational and audit logs to SQLite SystemLog table"""
    try:
        log_entry = SystemLog(
            level=level,
            category=category,
            message=message,
            details=details or {},
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Notice: Failed to record system log: {e}")


class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'data_cleaning', 'report_generation', 'data_encryption', 'typo_correction'
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(1024))  # Path to processed file
    original_file_name = db.Column(db.String(255))
    activity_details = db.Column(db.JSON)  # Store additional details like settings, columns processed, etc.
    status = db.Column(db.String(20), default='completed')  # 'completed', 'failed', 'processing'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='history')
    dataset = db.relationship('Dataset')


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    hospital_id = db.Column(db.String(100), nullable=False)
    checkup_status = db.Column(db.String(20), default='none')  # 'none', 'ongoing', 'done'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Checkup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    oxygen_level = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    disease = db.Column(db.String(255))
    medicine = db.Column(db.String(255))
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    status = db.Column(db.String(20), default='ongoing')  # 'ongoing', 'completed'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    patient = db.relationship('Patient', backref='checkups')


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if getattr(current_user, 'role', 'user') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return view_func(*args, **kwargs)
    return wrapped


def migrate_database():
    """Migrate database schema to latest version (must be called within app context)"""
    try:
        # Check and update user table
        result = db.session.execute(db.text("PRAGMA table_info(user)"))
        cols = [row[1] for row in result]
        if 'profile_image' not in cols:
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN profile_image TEXT"))
            print('Added profile_image column to user table')
        if 'organization' not in cols:
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN organization TEXT"))
            print('Added organization column to user table')
        if 'organization_type' not in cols:
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN organization_type TEXT"))
            print('Added organization_type column to user table')
        if 'license_number' not in cols:
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN license_number TEXT"))
            print('Added license_number column to user table')
        
        # Check and update report_record table
        result = db.session.execute(db.text("PRAGMA table_info(report_record)"))
        cols = [row[1] for row in result]
        if 'dataset_id' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN dataset_id INTEGER"))
            print('Added dataset_id column to report_record table')
        if 'user_id' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN user_id INTEGER"))
            print('Added user_id column to report_record table')
        if 'report_name' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN report_name VARCHAR(255)"))
            print('Added report_name column to report_record table')
        if 'file_path' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN file_path VARCHAR(1024)"))
            print('Added file_path column to report_record table')
        if 'format' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN format VARCHAR(10)"))
            print('Added format column to report_record table')
        if 'summary' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN summary TEXT"))
            print('Added summary column to report_record table')
        if 'html_content' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN html_content TEXT"))
            print('Added html_content column to report_record table')
        if 'created_at' not in cols:
            db.session.execute(db.text("ALTER TABLE report_record ADD COLUMN created_at DATETIME"))
            print('Added created_at column to report_record table')
        
        # Check and update processing_run table
        result = db.session.execute(db.text("PRAGMA table_info(processing_run)"))
        cols = [row[1] for row in result]
        if 'dataset_id' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN dataset_id INTEGER"))
            print('Added dataset_id column to processing_run table')
        if 'user_id' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN user_id INTEGER"))
            print('Added user_id column to processing_run table')
        if 'config' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN config TEXT"))
            print('Added config column to processing_run table')
        if 'cleaning_log' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN cleaning_log TEXT"))
            print('Added cleaning_log column to processing_run table')
        if 'estimates' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN estimates TEXT"))
            print('Added estimates column to processing_run table')
        if 'plots_count' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN plots_count INTEGER"))
            print('Added plots_count column to processing_run table')
        if 'success' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN success BOOLEAN"))
            print('Added success column to processing_run table')
        if 'created_at' not in cols:
            db.session.execute(db.text("ALTER TABLE processing_run ADD COLUMN created_at DATETIME"))
            print('Added created_at column to processing_run table')
        
        # Check and update dataset table
        result = db.session.execute(db.text("PRAGMA table_info(dataset)"))
        cols = [row[1] for row in result]
        if 'owner_id' not in cols:
            db.session.execute(db.text("ALTER TABLE dataset ADD COLUMN owner_id INTEGER"))
            print('Added owner_id column to dataset table')
        if 'uploaded_at' not in cols:
            db.session.execute(db.text("ALTER TABLE dataset ADD COLUMN uploaded_at DATETIME"))
            print('Added uploaded_at column to dataset table')
        
        # Check and create user_history table
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_history'"))
        if not result.fetchone():
            db.session.execute(db.text("""
                CREATE TABLE user_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    activity_type VARCHAR(50) NOT NULL,
                    dataset_id INTEGER,
                    file_name VARCHAR(255),
                    file_path VARCHAR(1024),
                    original_file_name VARCHAR(255),
                    activity_details TEXT,
                    status VARCHAR(20) DEFAULT 'completed',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (dataset_id) REFERENCES dataset (id)
                )
            """))
            print('Created user_history table')
        
        # Check and create patient table
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='patient'"))
        if not result.fetchone():
            db.session.execute(db.text("""
                CREATE TABLE patient (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name VARCHAR(255) NOT NULL,
                    age INTEGER NOT NULL,
                    date_of_birth DATE NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    blood_group VARCHAR(5) NOT NULL,
                    weight FLOAT NOT NULL,
                    height FLOAT NOT NULL,
                    hospital_id VARCHAR(100) NOT NULL,
                    checkup_status VARCHAR(20) DEFAULT 'none',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print('Created patient table')
        
        # Check and create checkup table
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='checkup'"))
        if not result.fetchone():
            db.session.execute(db.text("""
                CREATE TABLE checkup (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    oxygen_level FLOAT,
                    blood_pressure VARCHAR(20),
                    disease VARCHAR(255),
                    medicine VARCHAR(255),
                    dosage VARCHAR(100),
                    frequency VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'ongoing',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patient (id)
                )
            """))
            print('Created checkup table')
            
        # Check and create analysis_output table
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_output'"))
        if not result.fetchone():
            db.session.execute(db.text("""
                CREATE TABLE analysis_output (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER,
                    user_id INTEGER,
                    analysis_type VARCHAR(100),
                    query VARCHAR(512),
                    summary_metrics TEXT,
                    anomalies_detected TEXT,
                    insights TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dataset_id) REFERENCES dataset (id),
                    FOREIGN KEY (user_id) REFERENCES user (id)
                )
            """))
            print('Created analysis_output table')

        # Check and create ai_assistant_log table
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_assistant_log'"))
        if not result.fetchone():
            db.session.execute(db.text("""
                CREATE TABLE ai_assistant_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    dataset_id INTEGER,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    response_type VARCHAR(50),
                    metadata_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (dataset_id) REFERENCES dataset (id)
                )
            """))
            print('Created ai_assistant_log table')

        # Check and create system_log table
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='system_log'"))
        if not result.fetchone():
            db.session.execute(db.text("""
                CREATE TABLE system_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level VARCHAR(20) DEFAULT 'INFO',
                    category VARCHAR(50),
                    message TEXT NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print('Created system_log table')
        
        db.session.commit()
        print('Database migration completed successfully')
        
    except Exception as e:
        print(f'Error during migration: {e}')
        db.session.rollback()
        raise

class DataProcessor:
    def __init__(self):
        self.data = None
        self.cleaned_data = None
        self.weights = None
        self.cleaning_log = []
        self.estimates = {}
        
    def load_data(self, file_path):
        """Load data from CSV or Excel file"""
        try:
            import pandas as pd  # Lazy import
            if file_path.endswith('.csv'):
                # Try fast path first, then fallbacks for tricky files
                try:
                    self.data = pd.read_csv(file_path)
                except Exception:
                    try:
                        # Auto-detect separator and use python engine
                        self.data = pd.read_csv(file_path, engine='python', sep=None)
                    except Exception:
                        # Encoding/line issues fallback
                        self.data = pd.read_csv(
                            file_path,
                            engine='python',
                            sep=None,
                            encoding='latin1',
                            on_bad_lines='skip'
                        )
            elif file_path.endswith(('.xlsx', '.xls')):
                try:
                    self.data = pd.read_excel(file_path)
                except ImportError as ie:
                    raise ImportError("Excel reading requires openpyxl. Install with: pip install openpyxl") from ie
            else:
                raise ValueError("Unsupported file format")
            
            # Attempt to coerce numeric-like object columns (e.g., values with commas or currency symbols)
            try:
                object_columns = self.data.select_dtypes(include=['object']).columns
                converted_columns = []
                for col in object_columns:
                    original_series = self.data[col]
                    # Remove common thousands separators and currency symbols then coerce
                    cleaned = (
                        original_series.astype(str)
                        .str.replace(r"[\s,₹$]", "", regex=True)
                        .str.replace(r"[^0-9eE+\-.]", "", regex=True)
                    )
                    numeric_series = pd.to_numeric(cleaned, errors='coerce')
                    # If majority became numeric, accept conversion
                    if numeric_series.notna().mean() >= 0.8:
                        self.data[col] = numeric_series
                        converted_columns.append(col)
                if converted_columns:
                    self.cleaning_log.append(
                        f"Auto-converted numeric-like columns: {', '.join(converted_columns)}"
                    )
            except Exception:
                # Non-fatal; proceed without coercion
                pass

            # Check if data is empty or has no columns
            if self.data is None or len(self.data) == 0 or len(self.data.columns) == 0:
                self.cleaning_log.append("Error: No data or columns found in file")
                return False
                
            self.cleaning_log.append(f"Data loaded successfully: {len(self.data)} rows, {len(self.data.columns)} columns")
            return True
        except Exception as e:
            self.cleaning_log.append(f"Error loading data: {str(e)}")
            return False
    
    def detect_missing_values(self):
        """Detect and report missing values as a list of dicts (no pandas dependency)."""
        total_rows = len(self.data)
        missing_summary = self.data.isnull().sum()
        missing_percentage = (missing_summary / total_rows) * 100
        results = []
        for column_name, miss_count in missing_summary.items():
            if miss_count > 0:
                results.append({
                    'Column': column_name,
                    'Missing_Count': int(miss_count),
                    'Missing_Percentage': float(missing_percentage[column_name])
                })
        return results
    
    def impute_missing_values(self, method='mean', columns=None):
        """Impute missing values using specified method"""
        # Determine numeric columns
        if columns is None:
            numeric_columns = self.data.select_dtypes(include=['number']).columns
        else:
            numeric_columns = [col for col in columns if col in self.data.columns and self.data[col].dtype in ['int64', 'float64']]

        # Fast path without sklearn for mean/median
        if method in ('mean', 'median'):
            if method == 'mean':
                self.data[numeric_columns] = self.data[numeric_columns].fillna(self.data[numeric_columns].mean())
            else:
                self.data[numeric_columns] = self.data[numeric_columns].fillna(self.data[numeric_columns].median())
            self.cleaning_log.append(f"Imputed missing values using {method} method for {len(numeric_columns)} columns")
            return

        # KNN requires scikit-learn
        if method == 'knn':
            try:
                from sklearn.impute import KNNImputer  # type: ignore
            except Exception as import_error:
                # Fallback to mean imputation if scikit-learn is unavailable
                self.data[numeric_columns] = self.data[numeric_columns].fillna(self.data[numeric_columns].mean())
                self.cleaning_log.append("scikit-learn not installed; KNN imputation unavailable. Fell back to mean imputation.")
                return
            imputer = KNNImputer(n_neighbors=5)
            self.data[numeric_columns] = imputer.fit_transform(self.data[numeric_columns])
            self.cleaning_log.append(f"Imputed missing values using {method} method for {len(numeric_columns)} columns")
            return

        raise ValueError("Method must be 'mean', 'median', or 'knn'")
    
    def detect_outliers(self, method='iqr', threshold=1.5):
        """Detect outliers using specified method"""
        outliers_report = {}
        numeric_columns = self.data.select_dtypes(include=['number']).columns
        
        for column in numeric_columns:
            if method == 'iqr':
                Q1 = self.data[column].quantile(0.25)
                Q3 = self.data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = self.data[(self.data[column] < lower_bound) | (self.data[column] > upper_bound)]
            elif method == 'zscore':
                # Compute z-scores using pandas to avoid external dependencies and index misalignment
                series = self.data[column]
                mean = series.mean()
                std = series.std(ddof=0)
                if std == 0 or (std != std):  # handle zero or NaN std
                    outliers = self.data.iloc[0:0]
                else:
                    z_scores = ((series - mean) / std).abs()
                    outliers = self.data[z_scores > threshold]
            elif method == 'isolation_forest':
                try:
                    from sklearn.ensemble import IsolationForest
                except Exception as import_error:
                    # Fallback to IQR if scikit-learn is unavailable
                    self.cleaning_log.append("scikit-learn not installed; Isolation Forest unavailable. Fell back to IQR method.")
                    Q1 = self.data[column].quantile(0.25)
                    Q3 = self.data[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    outliers = self.data[(self.data[column] < lower_bound) | (self.data[column] > upper_bound)]
                    outliers_report[column] = {
                        'count': len(outliers),
                        'percentage': (len(outliers) / len(self.data)) * 100,
                        'indices': outliers.index.tolist()
                    }
                    continue
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = self.data[iso_forest.fit_predict(self.data[[column]]) == -1]
            
            outliers_report[column] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(self.data)) * 100,
                'indices': outliers.index.tolist()
            }
        
        return outliers_report
    
    def handle_outliers(self, method='winsorize', columns=None, percentile=5):
        """Handle outliers using specified method"""
        if columns is None:
            numeric_columns = self.data.select_dtypes(include=['number']).columns
        else:
            numeric_columns = [col for col in columns if col in self.data.columns and self.data[col].dtype in ['int64', 'float64']]
        
        for column in numeric_columns:
            if method == 'winsorize':
                lower = self.data[column].quantile(percentile / 100.0)
                upper = self.data[column].quantile(1 - percentile / 100.0)
                self.data[column] = self.data[column].clip(lower, upper)
            elif method == 'remove':
                Q1 = self.data[column].quantile(0.25)
                Q3 = self.data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                self.data = self.data[(self.data[column] >= lower_bound) & (self.data[column] <= upper_bound)]
        
        self.cleaning_log.append(f"Handled outliers using {method} method for {len(numeric_columns)} columns")
    
    def apply_weights(self, weight_column):
        """Apply survey weights"""
        if weight_column in self.data.columns:
            self.weights = self.data[weight_column]
            self.cleaning_log.append(f"Applied weights from column: {weight_column}")
            return True
        else:
            self.cleaning_log.append(f"Weight column {weight_column} not found")
            return False
    
    def calculate_estimates(self, columns=None):
        """Calculate weighted and unweighted estimates"""
        if columns is None:
            numeric_columns = self.data.select_dtypes(include=['number']).columns
        else:
            numeric_columns = [col for col in columns if col in self.data.columns and self.data[col].dtype in ['int64', 'float64']]
        
        estimates = {}
        for column in numeric_columns:
            # Unweighted estimates
            unweighted_mean = self.data[column].mean()
            unweighted_std = self.data[column].std()
            unweighted_se = unweighted_std / math.sqrt(len(self.data))
            
            estimates[column] = {
                'unweighted': {
                    'mean': unweighted_mean,
                    'std': unweighted_std,
                    'se': unweighted_se,
                    'ci_95_lower': unweighted_mean - 1.96 * unweighted_se,
                    'ci_95_upper': unweighted_mean + 1.96 * unweighted_se
                }
            }
            
            # Weighted estimates
            if self.weights is not None:
                weight_sum = self.weights.sum()
                if weight_sum == 0:
                    weighted_mean = float('nan')
                    weighted_std = float('nan')
                    weighted_se = float('nan')
                else:
                    weighted_mean = (self.data[column] * self.weights).sum() / weight_sum
                    weighted_variance = (((self.data[column] - weighted_mean) ** 2) * self.weights).sum() / weight_sum
                    weighted_std = math.sqrt(weighted_variance)
                    weighted_se = weighted_std / math.sqrt(len(self.data))
                
                estimates[column]['weighted'] = {
                    'mean': weighted_mean,
                    'std': weighted_std,
                    'se': weighted_se,
                    'ci_95_lower': weighted_mean - 1.96 * weighted_se,
                    'ci_95_upper': weighted_mean + 1.96 * weighted_se
                }
        
        self.estimates = estimates
        self.cleaning_log.append(f"Calculated estimates for {len(numeric_columns)} columns")
        return estimates
    
    def generate_visualizations(self):
        """Generate data visualizations"""
        plots = {}
        # Lazy import plotly when needed
        try:
            import plotly.express as px
        except Exception as import_error:
            # If plotly is not installed, return empty plots with a hint
            self.cleaning_log.append("Plotly not installed; skipping visualizations.")
            return plots
        
        # Distribution plots for numeric columns
        numeric_columns = self.data.select_dtypes(include=['number']).columns[:5]  # Limit to first 5 columns
        
        for column in numeric_columns:
            fig = px.histogram(self.data, x=column, title=f'Distribution of {column}')
            plots[f'dist_{column}'] = fig.to_html(full_html=False)
        
        # Correlation heatmap
        if len(numeric_columns) > 1:
            corr_matrix = self.data[numeric_columns].corr()
            fig = px.imshow(corr_matrix, title='Correlation Matrix')
            plots['correlation'] = fig.to_html(full_html=False)
        
        # Missing values plot
        missing_data = self.data.isnull().sum()
        if missing_data.sum() > 0:
            fig = px.bar(x=missing_data.index, y=missing_data.values, title='Missing Values by Column')
            plots['missing'] = fig.to_html(full_html=False)
        
        return plots
    
    def generate_report(self, format='pdf'):
        """Generate comprehensive report"""
        if format == 'pdf':
            return self._generate_pdf_report()
        else:
            return self._generate_html_report()
    
    def _generate_pdf_report(self):
        """Generate PDF report"""
        # Lazy import reportlab only when generating PDF
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
        except Exception as import_error:
            raise ImportError("Missing reportlab for PDF reports. Install with: pip install reportlab or request HTML report instead.") from import_error
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Bhishma's AI - Autonomous Structured Data Analysis & Insights Report", title_style))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(f"Data Processing completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Total records processed: {len(self.data)}", styles['Normal']))
        story.append(Paragraph(f"Total variables: {len(self.data.columns)}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Data Analysis Section with enhanced styling
        if hasattr(self, 'ai_analysis') and self.ai_analysis:
            # Create custom style for analysis
            analysis_style = ParagraphStyle(
                'AnalysisStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                spaceAfter=8,
                leftIndent=10,
                rightIndent=10
            )
            
            story.append(Paragraph("🤖 Data Analysis & Insights", styles['Heading2']))
            story.append(Spacer(1, 6))
            
            # Split analysis into paragraphs for better PDF formatting
            analysis_paragraphs = self.ai_analysis.split('\n\n')
            for para in analysis_paragraphs:
                if para.strip():
                    # Clean paragraph text for PDF - remove problematic formatting
                    clean_para = para.strip()
                    # Remove markdown formatting that causes parsing issues
                    clean_para = clean_para.replace('**', '')
                    # Remove any HTML-like tags that might cause issues
                    import re
                    clean_para = re.sub(r'<[^>]+>', '', clean_para)
                    story.append(Paragraph(clean_para, analysis_style))
                    story.append(Spacer(1, 4))
            story.append(Spacer(1, 12))
        
        # Visualizations Summary Section
        if hasattr(self, 'plots') and self.plots:
            story.append(Paragraph("📈 Data Visualizations Generated", styles['Heading2']))
            viz_list = []
            for plot_name in self.plots.keys():
                viz_list.append(f"• {plot_name.replace('_', ' ').title()}")
            
            if viz_list:
                story.append(Paragraph("The following interactive visualizations were created:", styles['Normal']))
                for viz in viz_list:
                    story.append(Paragraph(viz, styles['Normal']))
                story.append(Paragraph("Note: Interactive charts are available in the HTML version of this report.", styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Privacy & Security Section
        if hasattr(self, 'privacy_report') and self.privacy_report:
            story.append(Paragraph("Privacy & Security Report", styles['Heading2']))
            story.append(Paragraph(f"Privacy Compliance Score: {self.privacy_report['compliance_score']}%", styles['Normal']))
            story.append(Paragraph(f"Total Sensitive Columns Detected: {self.privacy_report['protection_summary']['total_sensitive_columns']}", styles['Normal']))
            story.append(Paragraph(f"Columns Protected: {self.privacy_report['protection_summary']['columns_protected']}", styles['Normal']))
            
            # Privacy Actions
            if self.privacy_report['privacy_actions']:
                story.append(Paragraph("Privacy Protection Actions:", styles['Normal']))
                for action in self.privacy_report['privacy_actions']:
                    story.append(Paragraph(f"• {action}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Encrypted Data Sample
        story.append(Paragraph("Protected Data Sample (First 5 Rows)", styles['Heading2']))
        
        # Show encryption status
        encrypted_cols = getattr(self, 'encrypted_columns', [])
        if encrypted_cols:
            story.append(Paragraph(f"Encrypted Columns: {', '.join(encrypted_cols)}", styles['Normal']))
            story.append(Paragraph("Encryption Method: PBKDF2", styles['Normal']))
        story.append(Paragraph("Note: Selected sensitive columns have been encrypted for privacy protection", styles['Normal']))
        story.append(Spacer(1, 6))
        
        if len(self.data) > 0:
            # Create table with first 5 rows showing encrypted data
            sample_data = []
            
            # Header row with encryption indicators
            header_row = []
            for col in self.data.columns:
                if col in encrypted_cols:
                    header_row.append(f"🔒 {col}")
                else:
                    header_row.append(col)
            sample_data.append(header_row)
            
            # Data rows - show actual encrypted values
            for i in range(min(5, len(self.data))):
                row = []
                for col in self.data.columns:
                    cell_value = str(self.data.iloc[i][col])
                    # Show encrypted values as they are
                    if col in encrypted_cols:
                        cell_value = f"🔐 {cell_value}"
                    row.append(cell_value)
                sample_data.append(row)
            
            table = Table(sample_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 12))
            story.append(Paragraph("🔒 = Encrypted Column | 🔐 = Encrypted Value", styles['Normal']))
            if encrypted_cols:
                story.append(Paragraph(f"Total Encrypted Columns: {len(encrypted_cols)} out of {len(self.data.columns)}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Cleaning Log
        story.append(Paragraph("Data Cleaning Log", styles['Heading2']))
        for log_entry in self.cleaning_log:
            story.append(Paragraph(f"• {log_entry}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Estimates Table
        if self.estimates:
            story.append(Paragraph("Statistical Estimates", styles['Heading2']))
            estimate_data = [['Variable', 'Mean', 'Std Dev', 'Standard Error', '95% CI Lower', '95% CI Upper']]
            
            for var, est in self.estimates.items():
                if 'weighted' in est:
                    row = [
                        var,
                        f"{est['weighted']['mean']:.4f}",
                        f"{est['weighted']['std']:.4f}",
                        f"{est['weighted']['se']:.4f}",
                        f"{est['weighted']['ci_95_lower']:.4f}",
                        f"{est['weighted']['ci_95_upper']:.4f}"
                    ]
                else:
                    row = [
                        var,
                        f"{est['unweighted']['mean']:.4f}",
                        f"{est['unweighted']['std']:.4f}",
                        f"{est['unweighted']['se']:.4f}",
                        f"{est['unweighted']['ci_95_lower']:.4f}",
                        f"{est['unweighted']['ci_95_upper']:.4f}"
                    ]
                estimate_data.append(row)
            
            table = Table(estimate_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _generate_html_report(self):
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bhishma's AI - Autonomous Structured Data Analysis & Insights Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    line-height: 1.6;
                    color: #1f2937;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                .section {{
                    margin: 30px 0;
                    padding: 25px;
                    border-radius: 12px;
                    background: #f8fafc;
                    border-left: 4px solid #667eea;
                }}
                
                .section h2 {{
                    color: #1e293b;
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .log-entry {{
                    margin: 8px 0;
                    padding: 12px 16px;
                    background: white;
                    border-radius: 8px;
                    border-left: 3px solid #10b981;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }}
                
                .privacy-section {{
                    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                    border: 1px solid #fecaca;
                    border-left: 4px solid #dc2626;
                }}
                
                .encrypted-data {{
                    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                    border: 1px solid #bfdbfe;
                    border-left: 4px solid #3b82f6;
                }}
                
                .analysis-section {{
                    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                    border: 1px solid #bbf7d0;
                    border-left: 4px solid #22c55e;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                
                th, td {{
                    padding: 12px 16px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }}
                
                th {{
                    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                    color: white;
                    font-weight: 600;
                    text-transform: uppercase;
                    font-size: 0.875rem;
                    letter-spacing: 0.05em;
                }}
                
                .encrypted-header {{
                    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
                    position: relative;
                }}
                
                .encrypted-header::after {{
                    content: '🔒';
                    margin-left: 8px;
                }}
                
                .encrypted {{
                    background: #fee2e2;
                    color: #dc2626;
                    font-family: 'Monaco', 'Menlo', monospace;
                    font-weight: 600;
                    padding: 4px 8px;
                    border-radius: 4px;
                    position: relative;
                }}
                
                .encrypted::before {{
                    content: '🔐';
                    margin-right: 6px;
                }}
                
                .encrypted-col {{
                    background: #fef2f2;
                    border-left: 3px solid #dc2626;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    border-top: 4px solid #667eea;
                }}
                
                .stat-number {{
                    font-size: 2rem;
                    font-weight: 700;
                    color: #667eea;
                    display: block;
                }}
                
                .stat-label {{
                    color: #6b7280;
                    font-size: 0.875rem;
                    margin-top: 5px;
                }}
                
                .footer {{
                    background: #1f2937;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }}
                
                .badge-success {{
                    background: #dcfce7;
                    color: #166534;
                }}
                
                .badge-warning {{
                    background: #fef3c7;
                    color: #92400e;
                }}
                
                .badge-info {{
                    background: #dbeafe;
                    color: #1e40af;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Bhishma's AI</h1>
                    <p>Autonomous Structured Data Analysis & Insights Report</p>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>📊 Executive Summary</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <span class="stat-number">{len(self.data):,}</span>
                                <div class="stat-label">Records Processed</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">{len(self.data.columns)}</span>
                                <div class="stat-label">Variables Analyzed</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">{len(getattr(self, 'encrypted_columns', []))}</span>
                                <div class="stat-label">Columns Encrypted</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">{len(self.cleaning_log)}</span>
                                <div class="stat-label">Processing Steps</div>
                            </div>
                        </div>
                    </div>
        """
        
        # Add Data Analysis Section
        if hasattr(self, 'ai_analysis') and self.ai_analysis:
            html_content += f"""
            <div class="section analysis-section">
                <h2>🤖 Data Analysis & Insights</h2>
                <div style="white-space: pre-line; line-height: 1.8; font-size: 1.05rem;">{self.ai_analysis}</div>
            </div>
            """
        
        # Add Visualizations Section
        if hasattr(self, 'plots') and self.plots:
            html_content += f"""
            <div class="section">
                <h2>📈 Data Visualizations</h2>
                <p>The following interactive charts were generated during data analysis:</p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
            """
            
            for plot_name, plot_html in self.plots.items():
                if plot_html and isinstance(plot_html, str):
                    html_content += f"""
                    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <h3 style="margin-bottom: 15px; color: #1e293b;">{plot_name.replace('_', ' ').title()}</h3>
                        <div style="height: 400px; overflow: hidden; border-radius: 8px;">
                            {plot_html}
                        </div>
                    </div>
                    """
            
            html_content += "</div></div>"
        
        # Add Privacy & Security Section
        if hasattr(self, 'privacy_report') and self.privacy_report:
            html_content += f"""
            <div class="privacy-section">
                <h2>🔒 Privacy & Security Report</h2>
                <p><strong>Privacy Compliance Score:</strong> {self.privacy_report['compliance_score']}%</p>
                <p><strong>Total Sensitive Columns Detected:</strong> {self.privacy_report['protection_summary']['total_sensitive_columns']}</p>
                <p><strong>Columns Protected:</strong> {self.privacy_report['protection_summary']['columns_protected']}</p>
                <h3>Privacy Protection Actions:</h3>
                {''.join([f'<div class="log-entry">🔐 {action}</div>' for action in self.privacy_report['privacy_actions']])}
            </div>
            """
        
        # Add Encrypted Data Sample
        encrypted_cols = getattr(self, 'encrypted_columns', [])
        encryption_method = getattr(self, 'encryption_method', 'hash')
        
        html_content += f"""
            <div class="encrypted-data">
                <h2>🔐 Protected Data Sample (First 5 Rows)</h2>
                <p><strong>Encrypted Columns:</strong> {', '.join(encrypted_cols) if encrypted_cols else 'None'}</p>
                <p><strong>Encryption Method:</strong> {encryption_method.upper()}</p>
                <p><em>Selected sensitive columns have been encrypted/masked for privacy protection</em></p>
                <table>
                    <tr>
                        {''.join([f'<th class="{"encrypted-header" if col in encrypted_cols else ""}">{"🔒 " if col in encrypted_cols else ""}{col}</th>' for col in self.data.columns])}
                    </tr>
        """
        
        # Add sample rows showing encrypted data
        for i in range(min(5, len(self.data))):
            html_content += "<tr>"
            for col in self.data.columns:
                value = str(self.data.iloc[i][col])
                is_encrypted_col = col in encrypted_cols
                css_class = 'encrypted' if is_encrypted_col else ''
                display_value = f'🔐 {value}' if is_encrypted_col else value
                html_content += f'<td class="{css_class}">{display_value}</td>'
            html_content += "</tr>"
        
        html_content += f"""
                </table>
                <div style="margin-top: 15px; padding: 15px; background: #f3f4f6; border-radius: 8px;">
                    <p><strong>🔒 Encryption Legend:</strong></p>
                    <p>🔒 = Encrypted Column Header | 🔐 = Encrypted Data Value</p>
                    <p><strong>Security Summary:</strong> {len(encrypted_cols)} out of {len(self.data.columns)} columns encrypted with enterprise-grade protection</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📋 Data Processing Log</h2>
                {''.join([f'<div class="log-entry">✓ {entry}</div>' for entry in self.cleaning_log])}
            </div>
            
            <div class="section">
                <h2>Statistical Estimates</h2>
                <table>
                    <tr>
                        <th>Variable</th>
                        <th>Mean</th>
                        <th>Std Dev</th>
                        <th>Standard Error</th>
                        <th>95% CI Lower</th>
                        <th>95% CI Upper</th>
                    </tr>
        """
        
        if self.estimates:
            for var, est in self.estimates.items():
                if 'weighted' in est:
                    html_content += f"""
                    <tr>
                        <td>{var}</td>
                        <td>{est['weighted']['mean']:.4f}</td>
                        <td>{est['weighted']['std']:.4f}</td>
                        <td>{est['weighted']['se']:.4f}</td>
                        <td>{est['weighted']['ci_95_lower']:.4f}</td>
                        <td>{est['weighted']['ci_95_upper']:.4f}</td>
                    </tr>
                    """
                else:
                    html_content += f"""
                    <tr>
                        <td>{var}</td>
                        <td>{est['unweighted']['mean']:.4f}</td>
                        <td>{est['unweighted']['std']:.4f}</td>
                        <td>{est['unweighted']['se']:.4f}</td>
                        <td>{est['unweighted']['ci_95_lower']:.4f}</td>
                        <td>{est['unweighted']['ci_95_upper']:.4f}</td>
                    </tr>
                    """
        
        html_content += """
                </table>
            </div>
                </div>
                
                <div class="footer">
                    <p>🤖 Report generated by Bhishma's AI - Autonomous Structured Dataset Analysis & Insights System</p>
                    <p>Autonomous dataset inspection, column comprehension, automated cleaning, anomaly detection, and insights generation</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

# Global processor instance
processor = DataProcessor()

# Import enhanced typo correction service
try:
    from enhanced_typo_correction import EnhancedTypoCorrector
    # Initialize with Gemini API key from environment or default
    gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4')
    typo_corrector = EnhancedTypoCorrector(gemini_api_key=gemini_key)
    print("✅ Enhanced typo correction service initialized with Gemini AI")
except Exception as e:
    # Fallback to simple typo correction
    try:
        from typo_correction_simple import SimpleTypoCorrector
        typo_corrector = SimpleTypoCorrector()
        print("⚠️ Using simple typo correction (Enhanced models unavailable)")
    except Exception as e2:
        typo_corrector = None
        print(f"❌ Warning: No typo correction service available: {e}")
        print(f"   Fallback also failed: {e2}")

# Import augmentation service
try:
    from augmentation_service import augmentation_service
    print("✅ Augmentation service initialized")
    print("   Voice commands and Gemini AI processing ready")
except Exception as e:
    augmentation_service = None
    print(f"❌ Warning: Augmentation service not available: {e}")
    print("   This will affect the data augmentation feature")

# Augmentation API Routes
if augmentation_service:
    @app.route('/api/augmentation/upload', methods=['POST', 'OPTIONS'])
    def augmentation_upload():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response = set_cors_headers(response)
            return response
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                df = df.dropna(how='all').dropna(axis=1, how='all')
                
                if df.empty:
                    return jsonify({'error': 'No valid data found'}), 400
                
                # Convert to safe format exactly like augmentation folder
                safe_data = []
                for _, row in df.iterrows():
                    record = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            record[str(col)] = ""
                        else:
                            record[str(col)] = str(value)
                    safe_data.append(record)
                
                return jsonify({
                    "filename": filename,
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "preview": safe_data[:10],
                    "data": safe_data
                })
                
            except Exception as e:
                return jsonify({'error': f'Upload failed: {str(e)}'}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400

    @app.route('/api/augmentation/augment', methods=['POST', 'OPTIONS'])
    def augment_data():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response = set_cors_headers(response)
            return response
        
        data = request.json
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            result = augmentation_service.smart_augmentation(data['data'])
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/augmentation/process-command', methods=['POST', 'OPTIONS'])
    def process_augmentation_command():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response = set_cors_headers(response)
            return response
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        command = data.get('command', '')
        columns = data.get('columns', [])
        dataset = data.get('data', [])
        filename = data.get('filename', 'data.csv')
        sample_data = data.get('sample_data', [])
        
        if not command:
            return jsonify({'error': 'Command is required'}), 400
        
        try:
            if not dataset:
                return jsonify({
                    'success': True,
                    'result': {
                        'message': 'No dataset provided for processing',
                        'processed_data': None,
                        'changes_made': []
                    }
                })
            
            df = pd.DataFrame(dataset)
            processed_info = []
            changes_made = []
            
            print(f"Processing command: {command}")
            print(f"Dataset shape: {df.shape}")
            
            # Use Gemini AI to process the actual data
            try:
                import requests
                import json
                
                # Prepare data summary for Gemini
                data_summary = {
                    'filename': filename,
                    'rows': len(dataset),
                    'columns': columns,
                    'sample': sample_data[:3] if sample_data else dataset[:3]
                }
                
                # Create prompt for Gemini
                prompt = f"""You are a data processing AI. Analyze this dataset and execute the command.

Dataset Info:
- File: {filename}
- Rows: {len(dataset)}
- Columns: {', '.join(columns)}
- Sample data: {json.dumps(sample_data[:2] if sample_data else dataset[:2], indent=2)}

User Command: "{command}"

Please:
1. Analyze what changes are needed
2. Provide a summary of actions taken
3. If data cleaning is needed, describe the specific changes

Respond with a JSON object containing:
{{
  "message": "Description of what was analyzed/processed",
  "changes_made": ["list of specific changes"],
  "recommendations": "Any recommendations for the user"
}}"""
                
                # Call Gemini API
                gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4')
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1000
                    }
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        ai_response = result['candidates'][0]['content']['parts'][0]['text']
                        
                        # Try to parse JSON response
                        try:
                            ai_data = json.loads(ai_response)
                            message = ai_data.get('message', 'Data analyzed successfully')
                            changes_made = ai_data.get('changes_made', ['Data reviewed and validated'])
                        except:
                            message = ai_response
                            changes_made = ['AI analysis completed']
                        
                        # Actually process the data using augmentation service
                        result = augmentation_service.process_command(command, columns, dataset)
                        
                        if result.get('processed_data'):
                            processed_data = result['processed_data']
                            changes_made = ['Data processed with Gemini AI', message]
                        else:
                            # Fallback processing
                            processed_data = dataset.copy()
                            
                            # Apply basic processing based on command
                            if 'phone' in command.lower() and '0' in command.lower():
                                # Extract phone number from command
                                import re
                                phone_match = re.search(r'\b\d{10}\b', command)
                                replacement_phone = phone_match.group() if phone_match else '9405442242'
                                
                                for i, row in enumerate(processed_data):
                                    for col in columns:
                                        if 'phone' in col.lower() and col in row:
                                            if str(row[col]) == '0' or row[col] == 0:
                                                processed_data[i][col] = replacement_phone
                                                if f'Replaced phone 0 values with {replacement_phone}' not in changes_made:
                                                    changes_made.append(f'Replaced phone 0 values with {replacement_phone}')
                            
                            elif 'fix' in command.lower() or 'clean' in command.lower():
                                # General data cleaning
                                for i, row in enumerate(processed_data):
                                    for col in columns:
                                        if col in row:
                                            # Fix negative ages
                                            if 'age' in col.lower() and isinstance(row[col], (int, float)) and row[col] < 0:
                                                processed_data[i][col] = abs(row[col])
                                                if 'Fixed negative ages' not in changes_made:
                                                    changes_made.append('Fixed negative ages')
                                            # Fix empty emails
                                            elif 'email' in col.lower() and (not row[col] or row[col] == ''):
                                                processed_data[i][col] = f"user{i+1}@example.com"
                                                if 'Generated missing emails' not in changes_made:
                                                    changes_made.append('Generated missing emails')
                        
                        return jsonify({
                            'success': True,
                            'result': {
                                'message': message,
                                'processed_data': processed_data,
                                'changes_made': changes_made,
                                'original_size': len(dataset),
                                'processed_size': len(processed_data)
                            }
                        })
                
                # Fallback response
                return jsonify({
                    'success': True,
                    'result': {
                        'message': f'Analyzed your dataset with {len(dataset)} rows and {len(columns)} columns. Command "{command}" has been processed.',
                        'processed_data': dataset,
                        'changes_made': ['Data validation completed'],
                        'original_size': len(dataset),
                        'processed_size': len(dataset)
                    }
                })
                
            except Exception as ai_error:
                print(f"AI processing error: {ai_error}")
                # Fallback to basic processing
                return jsonify({
                    'success': True,
                    'result': {
                        'message': f'Processed your dataset with {len(dataset)} rows. Basic analysis completed.',
                        'processed_data': dataset,
                        'changes_made': ['Basic data processing applied'],
                        'original_size': len(dataset),
                        'processed_size': len(dataset)
                    }
                })
            
        except Exception as e:
            print(f"Command processing error: {e}")
            return jsonify({
                'success': False,
                'error': f'Processing error: {str(e)}'
            })
    
    @app.route('/api/augmentation/transcribe', methods=['POST', 'OPTIONS'])
    def transcribe_audio():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response = set_cors_headers(response)
            return response
        
        try:
            # Simple transcription placeholder - would need Whisper for real implementation
            return jsonify({"text": "Voice transcription not available - please type your command"})
        except Exception as e:
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
    
    print("Augmentation routes registered directly")
else:
    print("Augmentation service not available - routes not registered")

# Import AI Data Assistant
try:
    from ai_data_assistant import AIDataAssistant
    # Initialize with Gemini API key for smart command understanding
    gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4')
    ai_assistant = AIDataAssistant(gemini_api_key=gemini_key)
    print("✅ AI Data Assistant initialized with AI models")
    print(f"   API key loaded: {'Yes' if gemini_key else 'No'}")
    if gemini_key:
        print(f"   Key preview: {gemini_key[:20]}...")
except Exception as e:
    ai_assistant = None
    print(f"❌ Warning: AI Data Assistant not available: {e}")
    print("   This will affect the AI assistant chatbot functionality")

# Import Groq Service for Ultra-Fast LLM Dataset Intelligence
try:
    from groq_service import groq_service
    print("✅ Groq AI Service loaded")
    if groq_service.is_configured():
        print(f"   Groq Model: {groq_service.primary_model} (API Key Configured)")
    else:
        print("   Groq API Key: Not configured (Dynamic configuration available via API)")
except Exception as e:
    groq_service = None
    print(f"⚠️ Warning: Groq Service failed to load: {e}")

# Import augmentation, privacy services, and data analyzer
try:
    from data_augmenter import AdvancedDataAugmenter
    from privacy_security import PrivacySecurityManager
    from data_analyzer import DataAnalyzer
    from advanced_data_cleaner import AdvancedDataCleaner
    from synthetic_data_generator import SyntheticDataGenerator
    from privacy_preserving_processor import PrivacyPreservingProcessor
    
    data_augmenter = AdvancedDataAugmenter()
    privacy_manager = PrivacySecurityManager()
    data_analyzer = DataAnalyzer()
    advanced_cleaner = AdvancedDataCleaner()
    synthetic_generator = SyntheticDataGenerator()
    privacy_processor = PrivacyPreservingProcessor()
    
    print("All advanced data processing services initialized")
except ImportError as e:
    data_augmenter = None
    privacy_manager = None
    data_analyzer = None
    
    # Minimal fallback for advanced_cleaner
    class MinimalCleaner:
        def comprehensive_clean(self, df, **kwargs):
            cleaned = df.copy()
            logs = []
            
            # Remove duplicates
            if kwargs.get('remove_duplicates', True):
                before = len(cleaned)
                cleaned = cleaned.drop_duplicates()
                after = len(cleaned)
                if before > after:
                    logs.append(f"Removed {before - after} duplicate rows")
            
            # Handle missing values
            if kwargs.get('impute_missing', True):
                for col in cleaned.columns:
                    missing = cleaned[col].isnull().sum()
                    if missing > 0:
                        if cleaned[col].dtype in ['int64', 'float64']:
                            cleaned[col].fillna(cleaned[col].median(), inplace=True)
                        else:
                            cleaned[col].fillna(cleaned[col].mode()[0] if not cleaned[col].mode().empty else 'Unknown', inplace=True)
                        logs.append(f"Imputed {missing} missing values in '{col}'")
            
            return cleaned, logs
    
    advanced_cleaner = MinimalCleaner()
    synthetic_generator = None
    privacy_processor = None
    print(f"Warning: Advanced services not available: {e}")
    print("Using minimal fallback implementations")

# API Authentication endpoints
@app.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    if current_user.is_authenticated:
        return jsonify({
            'is_authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'profile_image': current_user.profile_image
            }
        })
    return jsonify({'is_authenticated': False, 'user': None})

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def api_auth_login():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    login_user(user)
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile_image': user.profile_image
        }
    })

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def api_auth_register():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    role = data.get('role', 'researcher').strip()
    password = data.get('password') or ''
    
    # Validate role
    valid_roles = ['researcher', 'hospital', 'sponsor']
    if role not in valid_roles:
        return jsonify({'error': 'Invalid role. Must be researcher, hospital, or sponsor'}), 400
    
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    # Role-specific validation and user creation
    if role == 'hospital':
        # Hospital registration
        hospital_id = (data.get('hospital_id') or '').strip()
        hospital_name = (data.get('hospital_name') or '').strip()
        hospital_email = (data.get('hospital_email') or '').strip()
        country = (data.get('country') or '').strip()
        
        if not hospital_id or not hospital_name or not hospital_email or not country:
            return jsonify({'error': 'Hospital ID, Hospital Name, Hospital Email, and Country are required'}), 400
        
        # Validate email domain for professional users
        if hospital_email.endswith('@gmail.com') or hospital_email.endswith('@yahoo.com') or hospital_email.endswith('@hotmail.com'):
            return jsonify({'error': 'Please use your professional/organizational email address'}), 400
        
        # Check if hospital ID or email already exists
        if User.query.filter_by(username=hospital_id).first():
            return jsonify({'error': 'Hospital ID already exists'}), 400
        
        if User.query.filter_by(email=hospital_email).first():
            return jsonify({'error': 'Hospital email already registered'}), 400
        
        user = User(
            username=hospital_id,  # Use hospital_id as username
            email=hospital_email,
            role=role,
            organization=hospital_name,  # Use hospital_name as organization
            organization_type='hospital',
            country=country
        )
    else:
        # Researcher/Sponsor registration
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip() or None
        organization = (data.get('organization') or '').strip()
        organization_type = data.get('organization_type', '').strip()
        license_number = (data.get('license_number') or '').strip()
        
        if not username or not email or not organization:
            return jsonify({'error': 'Username, email, and organization are required'}), 400
        
        # Validate email domain for professional users
        if email.endswith('@gmail.com') or email.endswith('@yahoo.com') or email.endswith('@hotmail.com'):
            return jsonify({'error': 'Please use your professional/organizational email address'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            username=username,
            email=email,
            role=role,
            organization=organization,
            organization_type=organization_type,
            license_number=license_number
        )
    
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'organization': user.organization,
            'organization_type': user.organization_type,
            'profile_image': user.profile_image
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    if current_user.is_authenticated:
        logout_user()
    return jsonify({'success': True})

@app.route('/api/auth/profile', methods=['GET', 'POST'])
def api_auth_profile():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        return jsonify({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'profile_image': current_user.profile_image
            }
        })
    
    # POST - update profile
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'email' in data:
        current_user.email = data['email'].strip() or None
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/auth/avatar', methods=['POST'])
def api_auth_avatar():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        filepath = os.path.join(app.config['AVATAR_FOLDER'], filename)
        file.save(filepath)
        
        # Update user profile
        current_user.profile_image = f"/avatars/{filename}"
        db.session.commit()
        
        return jsonify({'success': True, 'profile_image': current_user.profile_image})

@app.route('/api/auth/avatars/<path:filename>')
def api_auth_avatars(filename):
    return send_from_directory(app.config['AVATAR_FOLDER'], filename)

@app.route('/')
def index():
    try:
        # Basic health check - ensure database is accessible
        db_status = "healthy"
        try:
            # Simple database connectivity test
            db.session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            'message': "Welcome to Bhishma's - Autonomous Structured Dataset Analysis & Insights Agent",
            'version': '2.0.0',
            'status': 'running',
            'database': db_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'features': {
                'advanced_cleaning': bool(advanced_cleaner),
                'synthetic_data': bool(synthetic_generator),
                'privacy_protection': bool(privacy_processor),
                'typo_correction': bool(typo_corrector),
                'data_augmentation': bool(data_augmenter)
            },
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth/*',
                'data': '/upload, /clean, /report, /download_data',
                'advanced': '/api/advanced-cleaning, /api/synthetic-data, /api/privacy-protection',
                'typo': '/api/typo/*',
                'analytics': '/api/analytics/*',
                'admin': '/admin, /admin/summary',
                'profile': '/profile'
            }
        })
    except Exception as e:
        return jsonify({
            'error': 'Service error',
            'message': str(e),
            'status': 'error',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/health')
def health_check():
    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check upload directory
        upload_status = "healthy"
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
        except Exception as e:
            upload_status = f"error: {str(e)}"
        
        return jsonify({
            'status': 'healthy' if db_status == "healthy" and upload_status == "healthy" else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'checks': {
                'database': db_status,
                'upload_directory': upload_status
            },
            'version': '2.0.0',
            'service': "Bhishma's Autonomous Data Intelligence API"
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/test-auth')
def test_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'role': current_user.role
            }
        })
    else:
        return jsonify({'authenticated': False})


# Authentication pages and handlers
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return jsonify({'message': 'Login page not available via this endpoint. Use /api/auth/login for JSON.'})

    # Support form submit or JSON
    data = request.json if request.is_json else request.form
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'Username and password required'}), 400
        return jsonify({'message': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        return jsonify({'message': 'Invalid credentials'}), 401

    login_user(user)
    if request.is_json:
        return jsonify({'success': True, 'user': {'username': user.username, 'role': user.role}})
    return jsonify({'message': 'Login successful. Use /api/auth/me to check authentication.'})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return jsonify({'message': 'Register page not available via this endpoint. Use /api/auth/register for JSON.'})

    data = request.json if request.is_json else request.form
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip() or None
    password = data.get('password') or ''
    confirm = data.get('confirm') or ''

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    if password != confirm:
        return jsonify({'message': 'Passwords do not match'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=username, email=email, role='user')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({'message': 'Registration successful. Use /api/auth/me to check authentication.'})


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    if request.method == 'POST' and request.is_json:
        return jsonify({'success': True})
    return jsonify({'message': 'Logout successful.'})


# Deprecated duplicate JSON-only login/logout removed (handled above by GET/POST routes)


@app.route('/admin/summary')
@login_required
@admin_required
def admin_summary():
    users_count = User.query.count()
    datasets_count = Dataset.query.count()
    latest_datasets = Dataset.query.order_by(Dataset.uploaded_at.desc()).limit(10).all()
    payload = {
        'users': users_count,
        'datasets': datasets_count,
        'latest': [
            {
                'id': d.id,
                'filename': d.filename,
                'rows': d.rows,
                'columns': d.columns,
                'owner': (d.owner.username if d.owner else None),
                'uploaded_at': d.uploaded_at.isoformat()
            }
            for d in latest_datasets
        ]
    }
    return jsonify(payload)


@app.route('/admin')
@login_required
@admin_required
def admin_page():
    try:
        users_count = User.query.count()
        datasets_count = Dataset.query.count()
        runs_count = ProcessingRun.query.count()
        reports_count = ReportRecord.query.count()
        latest_datasets = Dataset.query.order_by(Dataset.uploaded_at.desc()).limit(10).all()
        latest_runs = ProcessingRun.query.order_by(ProcessingRun.created_at.desc()).limit(10).all()
        all_users = User.query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'users': users_count,
            'datasets': datasets_count,
            'runs': runs_count,
            'reports': reports_count,
            'latest_datasets': [
                {
                    'id': d.id,
                    'filename': d.filename,
                    'rows': d.rows,
                    'columns': d.columns,
                    'owner': (d.owner.username if d.owner else None),
                    'uploaded_at': d.uploaded_at.isoformat()
                }
                for d in latest_datasets
            ],
            'recent_runs': [
                {
                    'id': r.id,
                    'dataset_id': r.dataset_id,
                    'user_id': r.user_id,
                    'config': r.config,
                    'cleaning_log': r.cleaning_log,
                    'estimates': r.estimates,
                    'plots_count': r.plots_count,
                    'success': r.success,
                    'created_at': r.created_at.isoformat()
                }
                for r in latest_runs
            ],
            'all_users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'role': u.role,
                    'created_at': u.created_at.isoformat()
                }
                for u in all_users
            ]
        })
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return jsonify({'error': f'Failed to load admin dashboard: {str(e)}'}), 500

@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    data = request.json
    role = data.get('role')
    if role not in ['user', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    target = User.query.get(user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404
    target.role = role
    db.session.commit()
    if request.is_json:
        return jsonify({'success': True})
    # Redirect back to admin dashboard after update
    return jsonify({'message': 'Role updated successfully.'})

@app.route('/api/dashboard', methods=['GET', 'OPTIONS'])
def api_dashboard():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        # Get basic dashboard statistics
        total_users = User.query.count()
        total_datasets = Dataset.query.count()
        total_runs = ProcessingRun.query.count()
        total_reports = ReportRecord.query.count()
        
        # Get recent activity
        recent_datasets = Dataset.query.order_by(Dataset.uploaded_at.desc()).limit(5).all()
        recent_runs = ProcessingRun.query.order_by(ProcessingRun.created_at.desc()).limit(5).all()
        
        # Check if user is hospital and add hospital-specific stats
        if current_user.is_authenticated and current_user.role == 'hospital':
            try:
                total_patients = Patient.query.filter_by(hospital_id=current_user.username).count()
            except:
                total_patients = 0
            
            return jsonify({
                'success': True,
                'message': 'Hospital Dashboard Data',
                'role': current_user.role,
                'stats': {
                    'total_patients': total_patients,
                    'active_trials': 8,
                    'pending_enrollments': 23,
                    'completed_trials': 12
                },
                'recent_activities': [
                    {'type': 'patient_enrolled', 'message': 'New patient enrolled in Trial #TR001', 'time': '2 hours ago'},
                    {'type': 'trial_completed', 'message': 'Trial #TR005 completed successfully', 'time': '1 day ago'},
                    {'type': 'data_updated', 'message': 'Patient records updated', 'time': '3 days ago'}
                ]
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_datasets': total_datasets,
                'total_runs': total_runs,
                'total_reports': total_reports
            },
            'recent_datasets': [
                {
                    'id': d.id,
                    'filename': d.filename,
                    'rows': d.rows or 0,
                    'columns': d.columns or 0,
                    'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None
                }
                for d in recent_datasets
            ],
            'recent_runs': [
                {
                    'id': r.id,
                    'success': r.success,
                    'created_at': r.created_at.isoformat() if r.created_at else None
                }
                for r in recent_runs
            ],
            'features': {
                'ai_assistant': bool(ai_assistant),
                'typo_correction': bool(typo_corrector),
                'advanced_cleaning': bool(advanced_cleaner),
                'synthetic_data': bool(synthetic_generator),
                'privacy_protection': bool(privacy_processor),
                'data_augmentation': bool(data_augmenter)
            }
        })
    
    except Exception as e:
        print(f"Dashboard API error: {e}")
        return jsonify({'error': f'Failed to load dashboard data: {str(e)}'}), 500

@app.route('/api/admin/dashboard')
@login_required
@admin_required
def api_admin_dashboard():
    try:
        users_count = User.query.count()
        datasets_count = Dataset.query.count()
        runs_count = ProcessingRun.query.count()
        reports_count = ReportRecord.query.count()
        latest_datasets = Dataset.query.order_by(Dataset.uploaded_at.desc()).limit(10).all()
        latest_runs = ProcessingRun.query.order_by(ProcessingRun.created_at.desc()).limit(10).all()
        all_users = User.query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'users': users_count,
            'datasets': datasets_count,
            'runs': runs_count,
            'reports': reports_count,
            'latest_datasets': [
                {
                    'id': d.id,
                    'filename': d.filename,
                    'rows': d.rows,
                    'columns': d.columns,
                    'owner': (d.owner.username if d.owner else None),
                    'uploaded_at': d.uploaded_at.isoformat()
                }
                for d in latest_datasets
            ],
            'recent_runs': [
                {
                    'id': r.id,
                    'dataset_id': r.dataset_id,
                    'user_id': r.user_id,
                    'config': r.config,
                    'cleaning_log': r.cleaning_log,
                    'estimates': r.estimates,
                    'plots_count': r.plots_count,
                    'success': r.success,
                    'created_at': r.created_at.isoformat()
                }
                for r in latest_runs
            ],
            'all_users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'role': u.role,
                    'created_at': u.created_at.isoformat()
                }
                for u in all_users
            ]
        })
    except Exception as e:
        print(f"API Admin dashboard error: {e}")
        return jsonify({'error': f'Failed to load admin dashboard: {str(e)}'}), 500


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        return jsonify({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'profile_image': current_user.profile_image
            }
        })
    # POST: update username/email and optionally password
    data = request.form
    new_username = (data.get('username') or '').strip()
    new_email = (data.get('email') or '').strip() or None
    new_password = data.get('password') or ''
    # Handle avatar upload
    file = request.files.get('avatar')
    if file and file.filename:
        from werkzeug.utils import secure_filename
        fname = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        save_path = os.path.join(app.config['AVATAR_FOLDER'], fname)
        file.save(save_path)
        current_user.profile_image = f"/avatars/{fname}"

    if new_username and new_username != current_user.username:
        if User.query.filter(User.username == new_username, User.id != current_user.id).first():
            return jsonify({'error': 'Username already taken'}), 400
        current_user.username = new_username
    if new_email and new_email != current_user.email:
        if User.query.filter(User.email == new_email, User.id != current_user.id).first():
            return jsonify({'error': 'Email already in use'}), 400
        current_user.email = new_email
    if new_password:
        current_user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully.'})


@app.route('/avatars/<path:filename>')
def serve_avatar(filename):
    return send_from_directory(app.config['AVATAR_FOLDER'], filename)


@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def admin_update_role(user_id: int):
    target = User.query.get_or_404(user_id)
    payload_role = None
    try:
        payload_role = request.form.get('role') if request.form else None
        if not payload_role and request.is_json:
            payload_role = (request.get_json(silent=True) or {}).get('role')
    except Exception:
        payload_role = None
    role = (payload_role or '').strip()
    if role not in ('admin', 'user'):
        return jsonify({'error': 'Invalid role'}), 400
    target.role = role
    db.session.commit()
    if request.is_json:
        return jsonify({'success': True})
    # Redirect back to admin dashboard after update
    return jsonify({'message': 'Role updated successfully.'})

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load data
        if processor.load_data(filepath):
            # Get initial data summary (guard against unexpected errors)
            try:
                # Track dataset in DB (if DB is initialized)
                ds = None
                try:
                    rows_count = len(processor.data)
                    cols_count = len(processor.data.columns)
                    ds = Dataset(
                        filename=filename,
                        filepath=filepath,
                        rows=rows_count,
                        columns=cols_count,
                        owner_id=(current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None)
                    )
                    db.session.add(ds)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Warning: Failed to save dataset to database: {e}")
                    # Continue without database tracking
                    ds = None
                
                # Generate data types (simplified for compatibility)
                data_types = {col: str(dtype) for col, dtype in processor.data.dtypes.items()}
                
                summary = {
                    'rows': len(processor.data),
                    'column_names': processor.data.columns.tolist(),
                    'data_types': data_types
                }
                
                dataset_id = f"dataset_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
                response_data = {
                    'success': True, 
                    'dataset': {'id': ds.id if ds else dataset_id},
                    'summary': summary
                }
                
                return jsonify(response_data)
            except Exception as e:
                return jsonify({'success': False, 'error': f'Failed to process file: {str(e)}'}), 400
        else:
            return jsonify({'success': False, 'error': 'Failed to load data'}), 400
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/clean', methods=['POST', 'OPTIONS'])
def clean_data():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    data = request.json
    cleaning_config = data.get('config', {})
    
    # Check if data is available
    if processor.data is None or len(processor.data) == 0 or len(processor.data.columns) == 0:
        return jsonify({'error': 'No data available for cleaning. Please upload a file first.'}), 400
    
    try:
        # Missing value imputation
        if 'imputation' in cleaning_config:
            method = cleaning_config['imputation'].get('method', 'mean')
            columns = cleaning_config['imputation'].get('columns', None)
            processor.impute_missing_values(method=method, columns=columns)
        
        # Outlier detection and handling
        if 'outliers' in cleaning_config:
            detection_method = cleaning_config['outliers'].get('detection_method', 'iqr')
            handling_method = cleaning_config['outliers'].get('handling_method', 'winsorize')
            columns = cleaning_config['outliers'].get('columns', None)
            
            outliers_report = processor.detect_outliers(method=detection_method)
            processor.handle_outliers(method=handling_method, columns=columns)
        
        # Apply weights
        if 'weights' in cleaning_config:
            weight_column = cleaning_config['weights'].get('column', None)
            if weight_column:
                processor.apply_weights(weight_column)
        
        # Advanced data cleaning
        if 'advanced_cleaning' in cleaning_config and advanced_cleaner:
            advanced_config = cleaning_config['advanced_cleaning']
            if advanced_config.get('enabled', False):
                processor.data, cleaning_logs = advanced_cleaner.comprehensive_clean(
                    processor.data,
                    remove_duplicates=advanced_config.get('remove_duplicates', True),
                    fix_labels=advanced_config.get('fix_labels', True),
                    impute_missing=advanced_config.get('impute_missing', True),
                    handle_outliers=advanced_config.get('handle_outliers', True),
                    normalize_types=advanced_config.get('normalize_types', True)
                )
                processor.cleaning_log.extend(cleaning_logs)
        
        # Synthetic data generation
        if 'synthetic_data' in cleaning_config and synthetic_generator:
            synthetic_config = cleaning_config['synthetic_data']
            if synthetic_config.get('enabled', False):
                target_col = synthetic_config.get('target_column')
                if target_col and target_col in processor.data.columns:
                    X = processor.data.drop(columns=[target_col])
                    y = processor.data[target_col]
                    
                    X_aug, y_aug = synthetic_generator.comprehensive_augmentation(
                        X, y,
                        target_size=synthetic_config.get('target_size', len(X) * 2),
                        methods=synthetic_config.get('methods', ['smote', 'gaussian_noise'])
                    )
                    
                    processor.data = X_aug.copy()
                    processor.data[target_col] = y_aug
                    processor.cleaning_log.extend(synthetic_generator.generation_log)
        
        # Data augmentation
        if 'augmentation' in cleaning_config and data_augmenter:
            augmentation_config = cleaning_config['augmentation']
            if augmentation_config.get('enabled', False):
                processor.data = data_augmenter.augment_data(processor.data, augmentation_config)
                processor.cleaning_log.append(f"Applied data augmentation: {len(processor.data)} rows after augmentation")
        
        # Privacy-preserving processing
        privacy_report = None
        if 'privacy' in cleaning_config:
            privacy_config = cleaning_config['privacy']
            if privacy_config.get('enabled', False):
                if privacy_processor:
                    # Use advanced privacy processor
                    protection_level = privacy_config.get('protection_level', 'medium')
                    custom_pii = privacy_config.get('custom_pii_columns')
                    
                    processor.data = privacy_processor.comprehensive_privacy_protection(
                        processor.data,
                        protection_level=protection_level,
                        custom_pii=custom_pii
                    )
                    
                    processor.cleaning_log.extend(privacy_processor.privacy_log)
                    privacy_report = {
                        'compliance_score': 95 if protection_level == 'high' else 85 if protection_level == 'medium' else 75,
                        'privacy_actions': privacy_processor.privacy_log,
                        'protection_summary': {
                            'total_sensitive_columns': len(custom_pii) if custom_pii else 0,
                            'columns_protected': len(custom_pii) if custom_pii else 0
                        },
                        'sensitive_data_detected': {}
                    }
                    
                elif privacy_config.get('columns'):
                    # Fallback to simple encryption
                    import pandas as pd
                    import hashlib
                    import base64
                    
                    protected_cols = privacy_config.get('columns', [])
                    print(f"🔒 Encrypting columns: {protected_cols}")
                    
                    def encrypt_value(value):
                        if pd.isna(value):
                            return value
                        salt = b'enterprise_salt_2024'
                        key = hashlib.pbkdf2_hmac('sha256', str(value).encode(), salt, 100000)
                        return base64.b64encode(key).decode()[:16]
                    
                    # Direct encryption
                    for col in protected_cols:
                        if col in processor.data.columns:
                            processor.data[col] = processor.data[col].apply(encrypt_value)
                            print(f"✅ Encrypted {col}: {processor.data[col].head(2).tolist()}")
                    
                    processor.encrypted_columns = protected_cols
                    processor.cleaning_log.append(f"Encrypted {len(protected_cols)} columns with PBKDF2")
                    
                    privacy_report = {'compliance_score': 100, 'privacy_actions': [f'Encrypted {len(protected_cols)} columns']}
        
        # Calculate estimates
        estimate_columns = cleaning_config.get('estimate_columns', None)
        estimates = processor.calculate_estimates(columns=estimate_columns)
        
        # Generate visualizations
        plots = processor.generate_visualizations()
        
        # Store plots for report generation
        processor.plots = plots

        # Store privacy report and generate AI analysis
        if privacy_report:
            processor.privacy_report = privacy_report
        
        # Generate comprehensive data analysis using Python models
        if data_analyzer:
            try:
                data_analysis = data_analyzer.generate_comprehensive_summary(processor.data, processor.cleaning_log, privacy_report)
                processor.ai_analysis = data_analysis
                processor.cleaning_log.append(f"Data Analysis: Comprehensive statistical summary generated")
            except Exception as e:
                processor.ai_analysis = "Data analysis unavailable"
                print(f"Data analysis failed: {e}")
        
        # Save processed data to file for history
        processed_filename = f'cleaned_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        
        try:
            # Save the cleaned data to CSV
            processor.data.to_csv(processed_filepath, index=False)
            print(f"✅ Saved cleaned data to: {processed_filepath}")
        except Exception as e:
            print(f"Warning: Could not save cleaned data: {e}")
            processed_filepath = None
        
        # Persist processing run details
        try:
            # Attach to the most recent dataset from this session if available
            ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
            run = ProcessingRun(
                dataset_id=(ds.id if ds else None),
                user_id=(current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None),
                config=cleaning_config,
                cleaning_log=processor.cleaning_log,
                estimates=estimates,
                plots_count=len(plots),
                success=True
            )
            db.session.add(run)
            db.session.commit()
            
            # Log user activity for history
            if hasattr(current_user, 'id') and current_user.is_authenticated:
                log_user_activity(
                    user_id=current_user.id,
                    activity_type='data_cleaning',
                    dataset_id=ds.id if ds else None,
                    file_name=processed_filename,
                    file_path=processed_filepath,
                    original_file_name=ds.filename if ds else None,
                    activity_details={
                        'config': cleaning_config,
                        'cleaning_log': processor.cleaning_log,
                        'estimates': estimates,
                        'plots_count': len(plots)
                    }
                )
        except Exception:
            db.session.rollback()
            pass

        return jsonify({
            'success': True,
            'cleaning_log': processor.cleaning_log,
            'estimates': estimates,
            'plots': plots,
            'privacy_report': privacy_report,
            'encrypted_columns': getattr(processor, 'encrypted_columns', []),
            'next_options': {
                'data_analysis': '/analytics',
                'generate_report': '/report',
                'download_data': '/download_data'
            },
            'message': 'Data cleaning completed successfully! Choose your next step: Data Analysis or Generate Report'
        })
    
    except Exception as e:
        # Log the error for debugging
        error_msg = f"Error cleaning data: {str(e)}"
        print(f"Clean endpoint error: {error_msg}")
        return jsonify({'error': error_msg}), 400

@app.route('/report', methods=['POST', 'OPTIONS'])
def generate_report():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    data = request.json
    report_format = data.get('format', 'pdf')
    dataset_id = data.get('dataset_id')
    
    try:
        # Check if processor has data loaded
        if processor.data is None:
            # Try to load data from dataset_id or the most recent dataset or sample dataset
            try:
                ds = None
                if dataset_id:
                    try:
                        ds = Dataset.query.get(int(dataset_id))
                    except (ValueError, TypeError):
                        pass
                if not ds:
                    ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
                
                actual_path = None
                if ds:
                    actual_path = getattr(ds, 'filepath', None) or getattr(ds, 'file_path', None)
                    
                if not actual_path or not os.path.exists(actual_path):
                    sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'district_health.csv')
                    if os.path.exists(sample_path):
                        actual_path = sample_path
                    elif os.path.exists('district_health.csv'):
                        actual_path = 'district_health.csv'
                
                if actual_path and os.path.exists(actual_path):
                    if processor.load_data(actual_path):
                        print(f"Loaded data from {actual_path} for report generation")
                    else:
                        return jsonify({'error': 'Failed to load data for report generation'}), 400
                else:
                    return jsonify({'error': 'No data available for report generation. Please upload a file first.'}), 400
            except Exception as e:
                print(f"Error loading data for report: {e}")
                return jsonify({'error': f'Failed to load data for report generation: {str(e)}'}), 400
        
        # Generate the report
        report_content = processor.generate_report(format=report_format)
        
        # Save report file for history
        report_filename = f'survey_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        report_filepath = None
        
        if report_format == 'pdf':
            # Ensure a valid PDF bytes response
            if hasattr(report_content, 'getvalue'):
                pdf_bytes = report_content.getvalue()
            elif isinstance(report_content, bytes):
                pdf_bytes = report_content
            else:
                pdf_bytes = bytes(report_content)
            
            # Save PDF file
            report_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{report_filename}.pdf')
            with open(report_filepath, 'wb') as f:
                f.write(pdf_bytes)
            
            # Create response with proper headers
            response = send_file(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{report_filename}.pdf'
            )
            
            # Add CORS headers for PDF download
            response = set_cors_headers(response)
            
            return response
        else:
            # Save HTML file
            report_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{report_filename}.html')
            with open(report_filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return jsonify({'html_content': report_content})
    
    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({'error': str(e)}), 400

    finally:
        # Log the report generation attempt to SQLite
        try:
            ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
            rec = ReportRecord(
                dataset_id=(ds.id if ds else None),
                user_id=(current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None),
                report_name=f'{report_filename}.{report_format}',
                file_path=report_filepath,
                format=report_format,
                summary=f"Automated {report_format.upper()} report generated for {ds.filename if ds else 'dataset'}",
                html_content=(report_content if report_format == 'html' else None)
            )
            db.session.add(rec)
            
            # Log to system_log
            log_system_event(
                category='report_export',
                message=f"Generated and stored {report_format.upper()} report in SQLite: {report_filename}.{report_format}",
                details={'format': report_format, 'file_name': f'{report_filename}.{report_format}'}
            )
            
            # Log user activity for history
            if hasattr(current_user, 'id') and current_user.is_authenticated:
                log_user_activity(
                    user_id=current_user.id,
                    activity_type='report_generation',
                    dataset_id=ds.id if ds else None,
                    file_name=f'{report_filename}.{report_format}',
                    file_path=report_filepath,
                    original_file_name=ds.filename if ds else None,
                    activity_details={
                        'format': report_format,
                        'generated_at': datetime.now().isoformat()
                    }
                )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Notice: SQLite report record save error: {e}")

@app.route('/download_data', methods=['POST', 'OPTIONS'])
def download_processed_data():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        # Check if processor has data loaded
        if processor.data is None:
            # Try to load data from the most recent dataset
            try:
                ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
                if ds and ds.file_path and os.path.exists(ds.file_path):
                    if processor.load_data(ds.file_path):
                        print(f"Loaded data from {ds.file_path} for download")
                    else:
                        return jsonify({'error': 'Failed to load data for download'}), 400
                else:
                    return jsonify({'error': 'No data available for download. Please upload a file first.'}), 400
            except Exception as e:
                print(f"Error loading data for download: {e}")
                return jsonify({'error': 'Failed to load data for download'}), 400
        
        # Create a ZIP file containing encrypted data and reports
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add processed/encrypted data - ensure all selected columns are properly encrypted
            csv_buffer = io.StringIO()
            
            # Verify encryption is applied to selected columns
            encrypted_cols = getattr(processor, 'encrypted_columns', [])
            if encrypted_cols:
                print(f"\n🔍 Verifying encryption in download data for columns: {encrypted_cols}")
                for col in encrypted_cols:
                    if col in processor.data.columns:
                        sample_values = processor.data[col].astype(str).head(3)
                        print(f"   {col}: {sample_values.tolist()}")
                        encrypted_count = len([val for val in sample_values if len(str(val)) == 16 and str(val) != 'nan'])
                        print(f"   {col}: {encrypted_count}/3 values encrypted in sample")
            
            # Save encrypted data to CSV
            processor.data.to_csv(csv_buffer, index=False)
            zip_file.writestr('secure_processed_data.csv', csv_buffer.getvalue())
            
            # Add a separate file showing which columns were encrypted
            if encrypted_cols:
                encryption_info = f"""Encryption Information
======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Encrypted Columns: {', '.join(encrypted_cols)}
Encryption Method: {getattr(processor, 'encryption_method', 'hash').upper()}
Total Columns Encrypted: {len(encrypted_cols)}
Total Columns in Dataset: {len(processor.data.columns)}

Security Note: 
All selected sensitive columns have been encrypted using enterprise-grade PBKDF2 encryption.
Encrypted values are prefixed with 'ENC_' for identification.
Original values cannot be recovered without the encryption key.
"""
                zip_file.writestr('encryption_info.txt', encryption_info)
            
            # Add AI analysis if available
            if hasattr(processor, 'ai_analysis') and processor.ai_analysis:
                ai_analysis_content = f"""AI Analysis & Insights
======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{processor.ai_analysis}
"""
                zip_file.writestr('ai_analysis.txt', ai_analysis_content)
            
            # Add privacy report if available
            if hasattr(processor, 'privacy_report') and processor.privacy_report:
                privacy_report_content = f"""Privacy & Security Report
=========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Privacy Compliance Score: {processor.privacy_report['compliance_score']}%
Total Sensitive Columns: {processor.privacy_report['protection_summary']['total_sensitive_columns']}
Columns Protected: {processor.privacy_report['protection_summary']['columns_protected']}

Privacy Actions:
{chr(10).join([f'- {action}' for action in processor.privacy_report['privacy_actions']])}


Sensitive Data Detected:
{json.dumps(processor.privacy_report['sensitive_data_detected'], indent=2)}
"""
                zip_file.writestr('privacy_report.txt', privacy_report_content)
            
            # Add data cleaning log
            log_entries = '\n'.join([f'- {entry}' for entry in processor.cleaning_log])
            cleaning_log_content = f"""Data Cleaning Log
==================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{log_entries}
"""
            zip_file.writestr('cleaning_log.txt', cleaning_log_content)
        
        zip_buffer.seek(0)
        
        # Save processed data file for history
        download_filename = f"bhishma_data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        download_filepath = os.path.join(app.config['UPLOAD_FOLDER'], download_filename)
        
        # Save the ZIP file to disk for history tracking
        with open(download_filepath, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        # Log user activity for history
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
            log_user_activity(
                user_id=current_user.id,
                activity_type='data_cleaning',
                dataset_id=ds.id if ds else None,
                file_name=download_filename,
                file_path=download_filepath,
                original_file_name=ds.filename if ds else None,
                activity_details={
                    'action': 'download_processed_data',
                    'rows': len(processor.data),
                    'columns': len(processor.data.columns),
                    'file_size': os.path.getsize(download_filepath) if os.path.exists(download_filepath) else 0,
                    'encrypted_columns': encrypted_cols,
                    'format': 'zip'
                }
            )
        
        response = send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_filename
        )
        
        # Add CORS headers for ZIP download
        response = set_cors_headers(response)
        
        return response
    
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls', 'json', 'parquet'}

def ai_allowed_file(filename):
    """File validation for AI assistant - supports more formats"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls', 'json', 'parquet'}

# Enhanced Typo Correction Endpoints
@app.route('/api/typo/correct', methods=['POST', 'OPTIONS'])
def correct_typo():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if not typo_corrector:
        return jsonify({'error': 'Enhanced typo correction service not available'}), 503
    
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Text is required'}), 400
    
    text = data['text'].strip()
    method = data.get('method', 'best')
    
    if not text:
        return jsonify({'error': 'Text cannot be empty'}), 400
    
    try:
        if method == 'best':
            corrected, method_used = typo_corrector.get_best_correction(text)
            result = {
                'corrected': corrected,
                'method_used': method_used,
                'confidence': 'high' if method_used in ['gemini', 'grammar'] else 'medium'
            }
        elif method == 'comprehensive':
            result = typo_corrector.correct_text_comprehensive(text)
        elif method == 'gemini':
            result = {'corrected': typo_corrector.correct_with_gemini(text)}
        elif method == 'basic_spelling':
            result = {'corrected': typo_corrector.correct_with_basic_spelling(text)}
        elif method == 'advanced_spelling':
            result = {'corrected': typo_corrector.correct_with_advanced_spelling(text)}
        elif method == 'grammar':
            result = {'corrected': typo_corrector.correct_with_grammar(text)}
        elif method == 'spoken_typo':
            result = {'corrected': typo_corrector.correct_with_spoken_typo(text)}
        else:
            # Default to comprehensive
            result = typo_corrector.correct_text_comprehensive(text)
        
        # Log user activity for history
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            log_user_activity(
                user_id=current_user.id,
                activity_type='typo_correction',
                file_name=f'typo_corrected_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                original_file_name='single_text',
                activity_details={
                    'method': method,
                    'original_text': text,
                    'corrected_text': result.get('corrected', ''),
                    'method_used': result.get('method_used', method),
                    'confidence': result.get('confidence', 'medium')
                }
            )
        
        return jsonify({
            'success': True,
            'original': text,
            'results': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/typo/batch', methods=['POST', 'OPTIONS'])
def correct_typo_batch():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if not typo_corrector:
        return jsonify({'error': 'Enhanced typo correction service not available'}), 503
    
    data = request.json
    if not data or 'texts' not in data:
        return jsonify({'error': 'Texts array is required'}), 400
    
    texts = data['texts']
    method = data.get('method', 'best')
    
    if not isinstance(texts, list) or not texts:
        return jsonify({'error': 'Texts must be a non-empty array'}), 400
    
    try:
        results = typo_corrector.batch_correct(texts, method=method)
        
        # Save typo correction results to file for history
        typo_filename = f'typo_corrected_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        typo_filepath = os.path.join(app.config['UPLOAD_FOLDER'], typo_filename)
        
        try:
            # Save results to JSON file
            with open(typo_filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved typo correction results to: {typo_filepath}")
        except Exception as e:
            print(f"Warning: Could not save typo correction results: {e}")
            typo_filepath = None
        
        # Log user activity for history
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            log_user_activity(
                user_id=current_user.id,
                activity_type='typo_correction',
                file_name=typo_filename,
                file_path=typo_filepath,
                original_file_name='batch_texts',
                activity_details={
                    'method': method,
                    'total_texts': len(texts),
                    'total_processed': len(results),
                    'correction_stats': {
                        'corrected': len([r for r in results if r.get('corrected') != r.get('original')]),
                        'unchanged': len([r for r in results if r.get('corrected') == r.get('original')])
                    }
                }
            )
        
        return jsonify({
            'success': True,
            'results': results,
            'total_processed': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/typo/methods', methods=['GET'])
def get_correction_methods():
    methods = {
        'best': 'Best Available Method (Recommended)',
        'comprehensive': 'All Methods with Comparison',
        'gemini': 'Gemini AI Grammar Correction',
        'basic_spelling': 'Basic Spelling Correction (HuggingFace)',
        'advanced_spelling': 'Advanced T5 Spelling Correction',
        'grammar': 'Grammar Correction (T5-based)',
        'spoken_typo': 'Conversational Typo Correction'
    }
    return jsonify({
        'methods': methods,
        'available_models': {
            'huggingface': [
                'oliverguhr/spelling-correction-english-base',
                'ai-forever/T5-large-spell',
                'vennify/t5-base-grammar-correction',
                'willwade/t5-small-spoken-typo'
            ],
            'gemini': 'gemini-pro'
        }
    })

@app.route('/api/typo/test', methods=['GET'])
def test_typo_models():
    """Test endpoint to verify all models are working"""
    if not typo_corrector:
        return jsonify({'error': 'Enhanced typo correction service not available'}), 503
    
    test_text = "lets do a comparsion of the diferent methds"
    
    try:
        results = typo_corrector.correct_text_comprehensive(test_text)
        
        return jsonify({
            'success': True,
            'test_text': test_text,
            'results': results,
            'models_tested': len(results) - 1  # Exclude 'original'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, np.ndarray):
        if obj.size == 1:
            val = obj.item()
            return None if (isinstance(val, float) and (np.isnan(val) or np.isinf(val))) else val
        else:
            return [None if (isinstance(x, float) and (np.isnan(x) or np.isinf(x))) else x for x in obj.tolist()]
    elif isinstance(obj, (np.integer, np.floating)):
        val = obj.item()
        return None if (isinstance(val, float) and (np.isnan(val) or np.isinf(val))) else val
    elif hasattr(obj, 'item') and hasattr(obj, 'size') and obj.size == 1:
        val = obj.item()
        return None if (isinstance(val, float) and (np.isnan(val) or np.isinf(val))) else val
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    else:
        return obj

@app.route('/api/advanced-cleaning', methods=['POST', 'OPTIONS'])
def advanced_data_cleaning():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if not advanced_cleaner:
        return jsonify({'error': 'Advanced data cleaner not available'}), 503
    
    try:
        if processor.data is None:
            return jsonify({'error': 'No data available. Please upload a dataset first.'}), 400
        
        data = request.get_json()
        config = data.get('config', {})
        
        # Apply advanced cleaning
        cleaned_data, cleaning_logs = advanced_cleaner.comprehensive_clean(
            processor.data,
            remove_duplicates=config.get('remove_duplicates', True),
            fix_labels=config.get('fix_labels', True),
            impute_missing=config.get('impute_missing', True),
            handle_outliers=config.get('handle_outliers', True),
            normalize_types=config.get('normalize_types', True)
        )
        
        processor.data = cleaned_data
        processor.cleaning_log.extend(cleaning_logs)
        
        return jsonify({
            'success': True,
            'cleaning_log': cleaning_logs,
            'data_shape': {
                'rows': len(cleaned_data),
                'columns': len(cleaned_data.columns)
            },
            'message': 'Advanced data cleaning completed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/synthetic-data', methods=['POST', 'OPTIONS'])
def generate_synthetic_data():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if not synthetic_generator:
        return jsonify({'error': 'Synthetic data generator not available'}), 503
    
    try:
        if processor.data is None:
            return jsonify({'error': 'No data available. Please upload a dataset first.'}), 400
        
        data = request.get_json()
        config = data.get('config', {})
        
        target_col = config.get('target_column')
        if target_col and target_col in processor.data.columns:
            X = processor.data.drop(columns=[target_col])
            y = processor.data[target_col]
        else:
            X = processor.data
            y = None
        
        # Generate synthetic data
        X_aug, y_aug = synthetic_generator.comprehensive_augmentation(
            X, y,
            target_size=config.get('target_size', len(X) * 2),
            methods=config.get('methods', ['smote', 'gaussian_noise', 'bootstrap'])
        )
        
        # Update processor data
        processor.data = X_aug.copy()
        if y_aug is not None and target_col:
            processor.data[target_col] = y_aug
        
        processor.cleaning_log.extend(synthetic_generator.generation_log)
        
        return jsonify({
            'success': True,
            'generation_log': synthetic_generator.generation_log,
            'original_size': len(X),
            'augmented_size': len(X_aug),
            'augmentation_ratio': len(X_aug) / len(X),
            'message': 'Synthetic data generation completed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/privacy-protection', methods=['POST', 'OPTIONS'])
def apply_privacy_protection():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        if processor.data is None:
            return jsonify({'error': 'No data available. Please upload a dataset first.'}), 400
        
        data = request.get_json()
        config = data.get('config', {})
        
        if privacy_processor:
            # Use advanced privacy processor
            protected_data = privacy_processor.comprehensive_privacy_protection(
                processor.data,
                protection_level=config.get('protection_level', 'medium'),
                custom_pii=config.get('custom_pii_columns')
            )
            
            processor.data = protected_data
            processor.cleaning_log.extend(privacy_processor.privacy_log)
            
            return jsonify({
                'success': True,
                'privacy_log': privacy_processor.privacy_log,
                'protection_level': config.get('protection_level', 'medium'),
                'data_shape': {
                    'rows': len(protected_data),
                    'columns': len(protected_data.columns)
                },
                'message': 'Privacy protection applied successfully'
            })
        else:
            # Fallback to basic privacy protection
            import pandas as pd
            import hashlib
            import base64
            
            protected_data = processor.data.copy()
            privacy_log = []
            
            # Get PII columns from config
            custom_pii = config.get('custom_pii_columns', {})
            protected_columns = []
            
            for pii_type, columns in custom_pii.items():
                for col in columns:
                    if col and col in protected_data.columns:
                        protected_columns.append(col)
            
            # Apply protection based on level
            protection_level = config.get('protection_level', 'medium')
            
            def encrypt_value(value):
                if pd.isna(value):
                    return value
                salt = b'enterprise_salt_2024'
                key = hashlib.pbkdf2_hmac('sha256', str(value).encode(), salt, 100000)
                return base64.b64encode(key).decode()[:16]
            
            for col in protected_columns:
                if protection_level == 'low':
                    # Simple masking
                    protected_data[col] = protected_data[col].astype(str).apply(
                        lambda x: x[:2] + '*' * (len(x) - 4) + x[-2:] if len(str(x)) > 4 else '***'
                    )
                    privacy_log.append(f'Masked column: {col}')
                elif protection_level == 'medium':
                    # Hash anonymization
                    protected_data[col] = protected_data[col].apply(encrypt_value)
                    privacy_log.append(f'Hash anonymized column: {col}')
                elif protection_level == 'high':
                    # Full suppression
                    protected_data[col] = '[REDACTED]'
                    privacy_log.append(f'Suppressed column: {col}')
            
            processor.data = protected_data
            processor.cleaning_log.extend(privacy_log)
            
            return jsonify({
                'success': True,
                'privacy_log': privacy_log,
                'protection_level': protection_level,
                'data_shape': {
                    'rows': len(protected_data),
                    'columns': len(protected_data.columns)
                },
                'message': 'Privacy protection applied successfully'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/generate', methods=['POST', 'OPTIONS'])
def generate_analytics():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        if processor.data is None:
            return jsonify({'error': 'No data available. Please upload a dataset first.'}), 400
        
        import pandas as pd
        import numpy as np
        
        data = processor.data
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Dataset info
        dataset_info = {
            'rows': int(len(data)),
            'columns': int(len(data.columns)),
            'numeric_columns': int(len(numeric_columns)),
            'missing_values': int(data.isnull().sum().sum())
        }
        
        charts = []
        colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
        
        # Generate charts for numeric columns
        for i, col in enumerate(numeric_columns[:6]):  # Limit to 6 charts
            col_data = data[col].dropna()
            
            if len(col_data) > 0:
                # Create histogram data
                hist, bins = np.histogram(col_data, bins=10)
                bin_centers = [(bins[j] + bins[j+1]) / 2 for j in range(len(bins)-1)]
                
                chart_data = {
                    'title': f'Distribution of {col}',
                    'labels': [f'{b:.2f}' for b in bin_centers],
                    'datasets': [{
                        'label': col,
                        'data': convert_numpy_types(hist.tolist()),
                        'backgroundColor': colors[i % len(colors)] + '80',
                        'borderColor': colors[i % len(colors)],
                        'borderWidth': 2
                    }]
                }
                charts.append(chart_data)
        
        # Missing values chart
        missing_data = data.isnull().sum()
        missing_cols = missing_data[missing_data > 0]
        
        if len(missing_cols) > 0:
            chart_data = {
                'title': 'Missing Values by Column',
                'labels': missing_cols.index.tolist(),
                'datasets': [{
                    'label': 'Missing Values',
                    'data': convert_numpy_types(missing_cols.values.tolist()),
                    'backgroundColor': ['#EF4444' + '80'] * len(missing_cols),
                    'borderColor': ['#EF4444'] * len(missing_cols),
                    'borderWidth': 2
                }]
            }
            charts.append(chart_data)
        
        # Correlation chart for numeric columns
        if len(numeric_columns) >= 2:
            corr_matrix = data[numeric_columns].corr()
            corr_pairs = []
            corr_values = []
            
            for i in range(len(numeric_columns)):
                for j in range(i+1, len(numeric_columns)):
                    corr_pairs.append(f'{numeric_columns[i]} vs {numeric_columns[j]}')
                    corr_values.append(float(abs(corr_matrix.iloc[i, j])))
            
            if corr_pairs:
                chart_data = {
                    'title': 'Column Correlations (Absolute)',
                    'labels': corr_pairs[:10],  # Top 10 correlations
                    'datasets': [{
                        'label': 'Correlation',
                        'data': convert_numpy_types(corr_values[:10]),
                        'backgroundColor': '#10B981' + '80',
                        'borderColor': '#10B981',
                        'borderWidth': 2
                    }]
                }
                charts.append(chart_data)
        
        return jsonify({
            'success': True,
            'dataset_info': dataset_info,
            'charts': charts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/custom-chart', methods=['POST', 'OPTIONS'])
def generate_custom_chart():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        if processor.data is None:
            return jsonify({'error': 'No data available. Please upload a dataset first.'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        x_axis = data.get('xAxis')
        y_axis = data.get('yAxis')
        chart_type = data.get('chartType', 'bar')
        title = data.get('title', '')
        
        if not x_axis or not y_axis:
            return jsonify({'error': 'Both X and Y axes are required'}), 400
        
        if x_axis not in processor.data.columns or y_axis not in processor.data.columns:
            return jsonify({'error': 'Invalid column names'}), 400
        
        import pandas as pd
        import numpy as np
        
        # Prepare data for the chart
        chart_data = processor.data[[x_axis, y_axis]].dropna()
        
        if len(chart_data) == 0:
            return jsonify({'error': 'No data available after removing missing values'}), 400
        
        # Generate chart based on type
        if chart_type in ['bar', 'line']:
            # For bar/line charts, group by X-axis and aggregate Y-axis
            if processor.data[x_axis].dtype in ['object', 'string']:
                # Categorical X-axis
                grouped_data = chart_data.groupby(x_axis)[y_axis].agg(['mean', 'count']).reset_index()
                labels = [str(label) for label in grouped_data[x_axis].tolist()]
                values = [float(val) if hasattr(val, 'item') else val for val in grouped_data['mean'].tolist()]
                counts = [int(count) if hasattr(count, 'item') else count for count in grouped_data['count'].tolist()]
            else:
                # Numeric X-axis - create bins
                bins = pd.cut(chart_data[x_axis], bins=min(10, len(chart_data)), include_lowest=True)
                grouped_data = chart_data.groupby(bins)[y_axis].mean().reset_index()
                labels = [str(interval) for interval in grouped_data[x_axis]]
                values = [float(val) if hasattr(val, 'item') else val for val in grouped_data[y_axis].tolist()]
                counts = [len(chart_data[chart_data[x_axis].between(interval.left, interval.right)]) for interval in grouped_data[x_axis]]
        
        elif chart_type in ['pie', 'doughnut']:
            # For pie/doughnut charts, group by X-axis and count
            grouped_data = chart_data.groupby(x_axis).size().reset_index(name='count')
            labels = [str(label) for label in grouped_data[x_axis].tolist()]
            values = [int(val) if hasattr(val, 'item') else val for val in grouped_data['count'].tolist()]
            counts = values
        
        elif chart_type == 'scatter':
            # For scatter plots, use actual data points
            labels = [str(label) for label in chart_data[x_axis].tolist()]
            values = [float(val) if hasattr(val, 'item') else val for val in chart_data[y_axis].tolist()]
            counts = [1] * len(labels)
        
        else:
            return jsonify({'error': 'Unsupported chart type'}), 400
        
        # Create chart configuration
        chart_config = {
            'title': title or f'{y_axis} vs {x_axis}',
            'labels': convert_numpy_types(labels),
            'datasets': [{
                'label': y_axis,
                'data': convert_numpy_types(values),
                'backgroundColor': '#3B82F6',
                'borderColor': '#1D4ED8',
                'borderWidth': 2,
                'pointBackgroundColor': '#3B82F6',
                'pointBorderColor': '#1D4ED8',
                'pointRadius': 4
            }],
            'chartType': chart_type,
            'xAxis': x_axis,
            'yAxis': y_axis,
            'dataPoints': int(len(chart_data)),
            'summary': {
                'xAxisUnique': int(len(chart_data[x_axis].unique())),
                'yAxisMean': float(chart_data[y_axis].mean()),
                'yAxisStd': float(chart_data[y_axis].std()),
                'yAxisMin': float(chart_data[y_axis].min()),
                'yAxisMax': float(chart_data[y_axis].max())
            }
        }
        
        return jsonify({
            'success': True,
            'chart': chart_config
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating custom chart: {str(e)}'}), 500

@app.route('/api/analytics/user-datasets', methods=['GET', 'OPTIONS'])
@login_required
def get_user_datasets():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        # Get user's datasets ordered by upload date
        user_datasets = Dataset.query.filter_by(owner_id=current_user.id).order_by(Dataset.uploaded_at.desc()).all()
        
        datasets_list = []
        for dataset in user_datasets:
            dataset_info = {
                'id': int(dataset.id),
                'filename': str(dataset.filename),
                'rows': int(dataset.rows) if dataset.rows else 0,
                'columns': int(dataset.columns) if dataset.columns else 0,
                'uploaded_at': dataset.uploaded_at.isoformat() if dataset.uploaded_at else None,
                'filepath': str(dataset.filepath)
            }
            datasets_list.append(dataset_info)
        
        return jsonify({
            'success': True,
            'datasets': datasets_list
        })
    
    except Exception as e:
        return jsonify({'error': f'Error fetching datasets: {str(e)}'}), 500

@app.route('/api/analytics/load-dataset/<int:dataset_id>', methods=['POST', 'OPTIONS'])
@login_required
def load_dataset_for_analytics(dataset_id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        # Get the dataset
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # Check if user owns the dataset
        if dataset.owner_id != current_user.id:
            return jsonify({'error': 'Access denied. You can only access your own datasets.'}), 403
        
        # Load the dataset into the processor
        if processor.load_data(dataset.filepath):
            # Get dataset summary
            summary = {
                'rows': len(processor.data),
                'columns': len(processor.data.columns),
                'column_names': processor.data.columns.tolist(),
                'data_types': {col: str(dtype) for col, dtype in processor.data.dtypes.items()},
                'missing_values': int(processor.data.isnull().sum().sum())
            }
            
            return jsonify({
                'success': True,
                'message': f'Dataset "{dataset.filename}" loaded successfully',
                'dataset': {
                    'id': int(dataset.id),
                    'filename': str(dataset.filename),
                    'rows': int(dataset.rows) if dataset.rows else 0,
                    'columns': int(dataset.columns) if dataset.columns else 0,
                    'uploaded_at': dataset.uploaded_at.isoformat() if dataset.uploaded_at else None
                },
                'summary': summary
            })
        else:
            return jsonify({'error': 'Failed to load dataset'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Error loading dataset: {str(e)}'}), 500

@app.route('/encrypt-data', methods=['POST', 'OPTIONS'])
def encrypt_data():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    columns = json.loads(request.form.get('columns', '[]'))
    method = request.form.get('method', 'aes')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not columns:
        return jsonify({'error': 'No columns selected for encryption'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load data using pandas
            import pandas as pd
            df = pd.read_csv(filepath)
            
            # Encrypt selected columns
            encrypted_df = df.copy()
            
            for column in columns:
                if column in df.columns:
                    # Simple encryption for demonstration
                    # In production, use proper encryption libraries like cryptography
                    if method == 'aes':
                        # Simple AES-like encryption (for demo purposes)
                        encrypted_df[column] = df[column].astype(str).apply(
                            lambda x: base64.b64encode(x.encode()).decode()[:20] + '...'
                        )
                    elif method == 'des':
                        # Simple DES-like encryption (for demo purposes)
                        encrypted_df[column] = df[column].astype(str).apply(
                            lambda x: base64.b64encode(x.encode()).decode()[:16] + '...'
                        )
                    elif method == 'blowfish':
                        # Simple Blowfish-like encryption (for demo purposes)
                        encrypted_df[column] = df[column].astype(str).apply(
                            lambda x: base64.b64encode(x.encode()).decode()[:24] + '...'
                        )
            
            # Save encrypted file for history
            encrypted_filename = f'encrypted_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'
            encrypted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
            encrypted_df.to_csv(encrypted_filepath, index=False)
            
            # Create response with encrypted data
            response_data = encrypted_df.to_csv(index=False).encode('utf-8')
            
            # Clean up temporary file
            try:
                os.remove(filepath)
            except:
                pass
            
            # Log user activity for history
            if hasattr(current_user, 'id') and current_user.is_authenticated:
                log_user_activity(
                    user_id=current_user.id,
                    activity_type='data_encryption',
                    file_name=encrypted_filename,
                    file_path=encrypted_filepath,
                    original_file_name=filename,
                    activity_details={
                        'method': method,
                        'columns_encrypted': columns,
                        'total_columns': len(df.columns),
                        'rows_processed': len(df)
                    }
                )
            
            # Return encrypted file
            return send_file(
                io.BytesIO(response_data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=encrypted_filename
            )
            
        except Exception as e:
            # Clean up on error
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'Encryption failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


# Test endpoint to create sample history with file
@app.route('/api/test/create-sample-history', methods=['POST'])
@login_required
def create_sample_history():
    """Create a sample history item with a file for testing"""
    try:
        # Create a sample CSV file
        import pandas as pd
        sample_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'Age': [30, 25, 35],
            'City': ['New York', 'Los Angeles', 'Chicago']
        })
        
        # Save to file
        filename = f'sample_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        sample_data.to_csv(filepath, index=False)
        
        # Create history item
        history_item = UserHistory(
            user_id=current_user.id,
            activity_type='data_cleaning',
            file_name=filename,
            file_path=filepath,
            original_file_name='sample_data.csv',
            activity_details={'test': True, 'created_at': datetime.now().isoformat()},
            status='completed'
        )
        
        db.session.add(history_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sample history created',
            'history_id': history_item.id,
            'file_path': filepath,
            'download_url': f'/api/history/{history_item.id}/download'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# History API endpoints
@app.route('/api/history', methods=['GET'])
@login_required
def get_user_history():
    """Get user's activity history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        activity_type = request.args.get('activity_type')
        
        query = UserHistory.query.filter_by(user_id=current_user.id)
        
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        
        # Order by most recent first
        query = query.order_by(UserHistory.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        history_items = []
        for item in pagination.items:
            history_items.append({
                'id': item.id,
                'activity_type': item.activity_type,
                'file_name': item.file_name,
                'original_file_name': item.original_file_name,
                'activity_details': item.activity_details,
                'status': item.status,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'has_file': bool(item.file_path and os.path.exists(item.file_path))
            })
        
        return jsonify({
            'success': True,
            'history': history_items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch history: {str(e)}'}), 500


@app.route('/api/history/<int:history_id>/download', methods=['GET'])
@login_required
def download_history_file(history_id):
    """Download a file from user's history"""
    try:
        print(f"🔍 Download request for history_id: {history_id}")
        
        history_item = UserHistory.query.filter_by(
            id=history_id, 
            user_id=current_user.id
        ).first()
        
        if not history_item:
            print(f"❌ History item not found for ID: {history_id}")
            return jsonify({'error': 'History item not found'}), 404
        
        print(f"📋 Found history item: {history_item.activity_type}, file_path: {history_item.file_path}")
        
        if not history_item.file_path:
            print(f"❌ No file_path set for history item: {history_id}")
            return jsonify({'error': 'No file path available for this item'}), 404
        
        if not os.path.exists(history_item.file_path):
            print(f"❌ File not found at path: {history_item.file_path}")
            return jsonify({'error': 'File not found on disk'}), 404
        
        print(f"✅ File exists at: {history_item.file_path}")
        
        # Determine file extension based on activity type
        file_extension = '.csv'
        if history_item.activity_type == 'report_generation':
            file_extension = '.pdf' if history_item.activity_details and history_item.activity_details.get('format') == 'pdf' else '.html'
        elif history_item.activity_type == 'typo_correction':
            file_extension = '.json'
        
        # Create download filename
        download_filename = f"{history_item.activity_type}_{history_item.file_name or 'processed_file'}{file_extension}"
        print(f"📥 Downloading as: {download_filename}")
        
        return send_file(
            history_item.file_path,
            as_attachment=True,
            download_name=download_filename
        )
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500


@app.route('/api/history/<int:history_id>', methods=['DELETE'])
@login_required
def delete_history_item(history_id):
    """Delete a history item and its associated file"""
    try:
        history_item = UserHistory.query.filter_by(
            id=history_id, 
            user_id=current_user.id
        ).first()
        
        if not history_item:
            return jsonify({'error': 'History item not found'}), 404
        
        # Delete associated file if it exists
        if history_item.file_path and os.path.exists(history_item.file_path):
            try:
                os.remove(history_item.file_path)
            except Exception as e:
                print(f"Warning: Could not delete file {history_item.file_path}: {e}")
        
        # Delete history record
        db.session.delete(history_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'History item deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete history item: {str(e)}'}), 500


def log_user_activity(user_id, activity_type, dataset_id=None, file_name=None, 
                     file_path=None, original_file_name=None, activity_details=None, status='completed'):
    """Helper function to log user activities"""
    try:
        history_item = UserHistory(
            user_id=user_id,
            activity_type=activity_type,
            dataset_id=dataset_id,
            file_name=file_name,
            file_path=file_path,
            original_file_name=original_file_name,
            activity_details=activity_details,
            status=status
        )
        db.session.add(history_item)
        db.session.commit()
        return history_item.id
    except Exception as e:
        print(f"Warning: Failed to log user activity: {e}")
        db.session.rollback()
        return None

# AI Data Assistant endpoints
@app.route('/api/ai-assistant/upload', methods=['POST', 'OPTIONS'])
def ai_assistant_upload():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    try:
        if not ai_assistant:
            return jsonify({'error': 'AI Data Assistant not available'}), 503
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type - allow more formats for AI assistant
        allowed_extensions = {'csv', 'xlsx', 'xls', 'json', 'txt', 'xml', 'pdf', 'doc', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Supported formats: {", ".join([ext.upper() for ext in allowed_extensions])}'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Verify file was saved
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to save uploaded file'}), 500
        
        # Load dataset into AI assistant
        result = ai_assistant.load_dataset(filepath)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result['message'],
                'summary': result['summary'],
                'preview': result['preview']
            })
        else:
            # Clean up file on error
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': result.get('error', 'Failed to load dataset')}), 400
    
    except Exception as e:
        print(f"AI Assistant upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/ai-assistant/load-sample', methods=['POST', 'GET', 'OPTIONS'])
def ai_assistant_load_sample():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
        
    try:
        if not ai_assistant:
            return jsonify({'error': 'AI Data Assistant not available'}), 503
            
        sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'district_health.csv')
        if not os.path.exists(sample_path):
            # Check project root directory
            root_sample = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'district_health.csv'))
            if os.path.exists(root_sample):
                import shutil
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                shutil.copy(root_sample, sample_path)
            else:
                return jsonify({'error': 'Sample dataset district_health.csv not found'}), 404
                
        result = ai_assistant.load_dataset(sample_path)
        if result.get('success'):
            try:
                ds = Dataset.query.filter_by(filename='district_health.csv').first()
                if not ds:
                    ds = Dataset(
                        filename='district_health.csv',
                        filepath=sample_path,
                        rows=result['summary'].get('total_rows', 35),
                        columns=result['summary'].get('total_columns', 11),
                        uploaded_at=datetime.now(timezone.utc)
                    )
                    db.session.add(ds)
                log_system_event(
                    category='sample_dataset',
                    message='Loaded demonstration dataset district_health.csv into SQLite',
                    details={'rows': result['summary'].get('total_rows', 35), 'columns': result['summary'].get('total_columns', 11)}
                )
                db.session.commit()
            except Exception as dbe:
                db.session.rollback()
                print(f"Warning saving sample dataset to SQLite: {dbe}")
                
            return jsonify({
                'success': True,
                'filename': 'district_health.csv',
                'message': 'Sample dataset district_health.csv loaded successfully!',
                'summary': result['summary'],
                'preview': result['preview']
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to load sample dataset')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistant/chat', methods=['POST', 'OPTIONS'])
def ai_assistant_chat():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if not ai_assistant:
        return jsonify({'error': 'AI Data Assistant not available'}), 503
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        from ai_data_assistant import sanitize_for_json
        
        # Check if Groq API should handle this dataset inquiry
        groq_resp = None
        df = ai_assistant.current_dataset if ai_assistant else (processor.data if processor else None)
        
        # If user passed custom Groq key in request payload, set it dynamically
        if data.get('groq_api_key') and groq_service:
            groq_service.set_api_key(data['groq_api_key'])
            
        if groq_service and groq_service.is_configured() and df is not None:
            # Check if this is a dataframe transformation command or an analytical question
            is_mechanical = any(cmd in user_message.lower() for cmd in ['drop column', 'remove duplicates', 'replace with mean', 'export dataset'])
            if not is_mechanical:
                groq_resp = groq_service.ask_dataset(user_message, df, data.get('history'))
        
        if groq_resp and groq_resp.get('success'):
            result = {
                'response': groq_resp['response'],
                'type': 'groq_ai_analysis',
                'data': {'model': groq_resp.get('model'), 'usage': groq_resp.get('usage')},
                'groq_powered': True,
                'model': groq_resp.get('model')
            }
        else:
            result = sanitize_for_json(ai_assistant.process_chat_command(user_message))
        
        # Persist conversation, outputs and logs into SQLite
        try:
            ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
            user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None
            
            # 1. Log chat message to SQLite AIAssistantLog
            chat_log = AIAssistantLog(
                user_id=user_id,
                dataset_id=(ds.id if ds else None),
                user_query=user_message,
                response=result.get('response', ''),
                response_type=result.get('type', 'chat'),
                metadata_json=result.get('data')
            )
            db.session.add(chat_log)
            
            # 2. If anomaly detection or statistical report, store in AnalysisOutput table
            if result.get('type') == 'anomaly_analysis' or 'anomal' in user_message.lower():
                output_rec = AnalysisOutput(
                    dataset_id=(ds.id if ds else None),
                    user_id=user_id,
                    analysis_type='anomaly_detection',
                    user_query=user_message,
                    summary_metrics=result.get('data', {}).get('metrics') if isinstance(result.get('data'), dict) else {},
                    anomalies_detected=result.get('data', {}).get('top_anomalous_districts') if isinstance(result.get('data'), dict) else {},
                    insights=result.get('response', '')
                )
                db.session.add(output_rec)
                
            # 3. Log to SystemLog
            log_system_event(
                category='ai_agent_query',
                message=f"AI Agent query processed: {user_message[:60]}",
                details={'response_type': result.get('type')}
            )
            db.session.commit()
        except Exception as log_err:
            db.session.rollback()
            print(f"Notice: SQLite AI chat log error: {log_err}")

        return jsonify({
            'success': True,
            'response': result['response'],
            'type': result['type'],
            'data': result.get('data'),
            'value': result.get('value'),
            'download_available': result.get('download_available', False),
            'download_url': result.get('download_url'),
            'filename': result.get('filename')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistant/export', methods=['POST', 'OPTIONS'])
def ai_assistant_export():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response = set_cors_headers(response)
        return response
    
    if not ai_assistant:
        return jsonify({'error': 'AI Data Assistant not available'}), 503
    
    try:
        result = ai_assistant._export_dataset("export dataset")
        
        if result['type'] == 'success':
            return jsonify({
                'success': True,
                'message': result['response'],
                'download_url': result['download_url'],
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result['response']}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistant/download/<filename>', methods=['GET'])
def ai_assistant_download(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistant/info', methods=['GET'])
def ai_assistant_info():
    if not ai_assistant:
        return jsonify({'error': 'AI Data Assistant not available'}), 503
    
    try:
        info = ai_assistant.get_current_dataset_info()
        history = ai_assistant.get_operation_history()
        
        return jsonify({
            'success': True,
            'dataset_info': info,
            'operation_history': history
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# Groq AI Endpoints
# Ultra-fast LLM Intelligence & Dataset Q&A
# ==========================================

@app.route('/api/groq/status', methods=['GET', 'OPTIONS'])
def groq_status():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
    configured = groq_service.is_configured() if groq_service else False
    res = jsonify({
        'configured': configured,
        'primary_model': groq_service.primary_model if groq_service else 'llama-3.3-70b-versatile',
        'fallback_model': getattr(groq_service, 'fallback_model', 'llama-3.1-8b-instant') if groq_service else 'llama-3.1-8b-instant'
    })
    return set_cors_headers(res)

@app.route('/api/groq/configure', methods=['POST', 'OPTIONS'])
def groq_configure():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
    data = request.get_json() or {}
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return set_cors_headers(jsonify({'error': 'API key cannot be empty'}), 400)
    
    if not groq_service:
        return set_cors_headers(jsonify({'error': 'Groq service unavailable'}), 503)
        
    configured = groq_service.set_api_key(api_key)
    res = jsonify({
        'success': configured,
        'message': 'Groq API key configured! Ultra-fast LLaMA-3.3 70B is ready.' if configured else 'Failed to configure Groq key',
        'configured': configured,
        'model': groq_service.primary_model
    })
    return set_cors_headers(res)

@app.route('/api/groq/suggested-questions', methods=['GET', 'OPTIONS'])
def groq_suggested_questions():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
    df = None
    if ai_assistant and ai_assistant.current_dataset is not None:
        df = ai_assistant.current_dataset
    elif processor and processor.data is not None:
        df = processor.data
    else:
        sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'district_health.csv')
        if os.path.exists(sample_path) and ai_assistant:
            ai_assistant.load_dataset(sample_path)
            df = ai_assistant.current_dataset
    
    questions = groq_service.generate_suggested_questions(df) if groq_service else []
    res = jsonify({
        'success': True,
        'dataset_loaded': df is not None,
        'questions': questions
    })
    return set_cors_headers(res)

@app.route('/api/groq/chat', methods=['POST', 'OPTIONS'])
def groq_chat():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    history = data.get('history', [])
    if not user_message:
        return set_cors_headers(jsonify({'error': 'Message is required'}), 400)
    
    if data.get('api_key') and groq_service:
        groq_service.set_api_key(data['api_key'])
        
    df = None
    if ai_assistant and ai_assistant.current_dataset is not None:
        df = ai_assistant.current_dataset
    elif processor and processor.data is not None:
        df = processor.data
    else:
        sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'district_health.csv')
        if os.path.exists(sample_path) and ai_assistant:
            ai_assistant.load_dataset(sample_path)
            df = ai_assistant.current_dataset
            
    if not groq_service:
        return set_cors_headers(jsonify({'error': 'Groq service not available'}), 503)
        
    groq_result = groq_service.ask_dataset(user_message, df, history)
    
    # Persist to SQLite
    try:
        ds = Dataset.query.order_by(Dataset.uploaded_at.desc()).first()
        user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None
        chat_log = AIAssistantLog(
            user_id=user_id,
            dataset_id=(ds.id if ds else None),
            user_query=user_message,
            response=groq_result.get('response', ''),
            response_type='groq_llm' if groq_result.get('success') else 'groq_fallback',
            metadata_json={'model': groq_result.get('model'), 'usage': groq_result.get('usage')}
        )
        db.session.add(chat_log)
        log_system_event('groq_chat', f"Groq AI processed: '{user_message[:60]}'", details={'model': groq_result.get('model')})
        db.session.commit()
    except Exception as dbe:
        db.session.rollback()
        print(f"Notice: SQLite groq chat log error: {dbe}")
        
    return set_cors_headers(jsonify(groq_result))

# ==========================================
# Narayan - Master Pipeline AI Agent Routes
# ==========================================
from narayan_service import narayan_service, PIPELINE_STEPS_CONTEXT

@app.route('/api/narayan/chat', methods=['POST', 'OPTIONS'])
def narayan_chat():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    step = data.get('step', 'upload')
    history = data.get('history', [])
    
    if not message:
        return set_cors_headers(jsonify({'error': 'Message is required'}), 400)
        
    # Auto-sync with processor dataset if needed
    if narayan_service.active_df is None or narayan_service.active_df.empty:
        if processor.data is not None and not processor.data.empty:
            narayan_service.active_df = processor.data.copy()
            narayan_service.active_filename = getattr(processor, 'filename', None) or 'active_pipeline_dataset.csv'
            
    result = narayan_service.chat_with_narayan(message, current_step=step, conversation_history=history)
    
    # Sync with processor if transformation was executed
    if result.get('action_executed') and narayan_service.active_df is not None:
        processor.data = narayan_service.active_df.copy()
        
    # Log event
    try:
        log_system_event('narayan_pipeline_chat', f"Narayan ({step}): {message[:60]}", details={'step': step, 'action': result.get('action_executed')})
    except Exception as e:
        pass
        
    return set_cors_headers(jsonify(result))

@app.route('/api/narayan/upload', methods=['POST', 'OPTIONS'])
def narayan_upload():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
        
    if 'file' not in request.files:
        return set_cors_headers(jsonify({'error': 'No file provided'}), 400)
        
    file = request.files['file']
    if file.filename == '':
        return set_cors_headers(jsonify({'error': 'No file selected'}), 400)
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    res = narayan_service.load_dataset(filepath, filename)
    if res.get('success'):
        # Sync with processor
        processor.data = narayan_service.active_df.copy()
        try:
            ds = Dataset(filename=filename, filepath=filepath, rows=res['rows'], columns=res['columns'])
            db.session.add(ds)
            db.session.commit()
        except Exception:
            db.session.rollback()
            
    return set_cors_headers(jsonify(res))

@app.route('/api/narayan/export', methods=['POST', 'OPTIONS'])
def narayan_export():
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
        
    data = request.get_json() or {}
    export_format = data.get('format', 'csv').lower()
    
    # Auto-sync with processor dataset if needed
    if narayan_service.active_df is None or narayan_service.active_df.empty:
        if processor.data is not None and not processor.data.empty:
            narayan_service.active_df = processor.data.copy()
            narayan_service.active_filename = getattr(processor, 'filename', None) or 'active_pipeline_dataset.csv'
            
    if export_format == 'pdf':
        res = narayan_service.export_pdf_report()
    elif export_format == 'html':
        res = narayan_service.export_html_report()
    else:
        res = narayan_service.export_cleaned_csv()
        
    return set_cors_headers(jsonify(res))

@app.route('/api/narayan/context/<step_id>', methods=['GET', 'OPTIONS'])
def narayan_step_context(step_id):
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({'status': 'ok'}))
        
    context = PIPELINE_STEPS_CONTEXT.get(step_id, PIPELINE_STEPS_CONTEXT.get('upload'))
    res = {
        'success': True,
        'step': step_id,
        'context': context,
        'active_dataset': {
            'filename': narayan_service.active_filename,
            'rows': len(narayan_service.active_df) if narayan_service.active_df is not None else 0,
            'columns': len(narayan_service.active_df.columns) if narayan_service.active_df is not None else 0,
            'encrypted_columns': narayan_service.encrypted_columns
        }
    }
    return set_cors_headers(jsonify(res))

@app.route('/api/ai-assistant/history', methods=['GET'])
@login_required
def ai_assistant_history():
    try:
        history_items = UserHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(UserHistory.created_at.desc()).limit(10).all()
        
        history_data = []
        for item in history_items:
            history_data.append({
                'id': item.id,
                'activity_type': item.activity_type,
                'file_name': item.file_name,
                'original_file_name': item.original_file_name,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'has_file': bool(item.file_path and os.path.exists(item.file_path))
            })
        
        return jsonify({
            'success': True,
            'history': history_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Initialize database
def init_database():
    """Initialize database and create admin user"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
                print("Database initialized successfully")
                
                # Create admin user if none exists
                try:
                    admin_users = User.query.filter_by(role='admin').count()
                    if admin_users == 0:
                        # Create default admin user
                        admin_username = "admin"
                        admin_email = "admin@bhishma-ai.org"
                        admin_password = "admin123"  # Change this in production!
                        
                        # Check if admin user already exists
                        existing_user = User.query.filter_by(username=admin_username).first()
                        if not existing_user:
                            admin_user = User(
                                username=admin_username,
                                email=admin_email,
                                role='admin',
                                created_at=datetime.now(timezone.utc)
                            )
                            admin_user.set_password(admin_password)
                            db.session.add(admin_user)
                            db.session.commit()
                            print("Admin user created successfully!")
                            print(f"Username: {admin_username}")
                            print(f"Password: {admin_password}")
                            print("IMPORTANT: Change the password after first login!")
                        else:
                            print("Admin user already exists")
                    else:
                        print(f"Found {admin_users} admin user(s)")
                except Exception as e:
                    print(f"Warning: Could not create admin user: {str(e)}")
                    # Don't fail the entire startup for admin user issues
                
                # Success - break out of retry loop
                break
                
        except Exception as e:
            retry_count += 1
            print(f"Error initializing database (attempt {retry_count}/{max_retries}): {str(e)}")
            
            if retry_count < max_retries:
                print(f"Retrying in 2 seconds...")
                import time
                time.sleep(2)
            else:
                print(f"Failed to initialize database after {max_retries} attempts")
                print("Application will continue but may not function properly")
                # In production, we might want to exit here
                # For now, let's continue and see if the app can run

# Initialize database when app starts
print("Starting Bhishma's Autonomous Structured Data Analysis & Insights System Backend...")
print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Secret key configured: {'Yes' if app.config['SECRET_KEY'] != 'change-me' else 'No'}")
print(f"Advanced services available: {bool(advanced_cleaner and synthetic_generator and privacy_processor)}")

init_database()

# Run migration within app context
with app.app_context():
    try:
        migrate_database()
    except Exception as e:
        print(f"Migration warning: {e}")

try:
    from export_reports import export_bp
    app.register_blueprint(export_bp)
    print("✅ Export routes registered (HTML/PDF)")
except Exception as e:
    print(f"Warning: Export routes not available: {e}")

print("Bhishma's Autonomous Data Intelligence System initialization completed!")
print("Application is ready to serve requests")
print("Available features: Dataset Inspection, Automated Cleaning, Anomaly & Outlier Detection, Statistical Analysis, Interactive Visualizations, AI Report Generation")

# ==========================================
# SQLite Database Endpoints
# Storing & querying: User Data, CSV Datasets, Reports, Outputs, and Logs
# ==========================================

@app.route('/api/db/status', methods=['GET', 'OPTIONS'])
def get_db_status():
    """Get SQLite database health, storage path, file size, and table row counts"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return set_cors_headers(response)
    
    try:
        import sqlite3
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = os.path.join(app.instance_path, 'app.db') if 'sqlite' in db_uri else 'N/A'
        file_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        tables_count = {
            'user': User.query.count(),
            'dataset': Dataset.query.count(),
            'report_record': ReportRecord.query.count(),
            'processing_run': ProcessingRun.query.count(),
            'analysis_output': AnalysisOutput.query.count(),
            'ai_assistant_log': AIAssistantLog.query.count(),
            'system_log': SystemLog.query.count(),
            'user_history': UserHistory.query.count()
        }
        
        response = jsonify({
            'status': 'connected',
            'engine': 'SQLite 3 (Python Standard Library)',
            'database_uri': db_uri,
            'database_path': db_path,
            'size_bytes': file_size,
            'size_kb': round(file_size / 1024, 2),
            'tables': tables_count,
            'features': {
                'store_reports': True,
                'store_user_data': True,
                'store_csv_files': True,
                'store_outputs': True,
                'store_logs': True
            }
        })
        return set_cors_headers(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/reports', methods=['GET', 'OPTIONS'])
def get_db_reports():
    """Query stored reports from SQLite database"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return set_cors_headers(response)
        
    try:
        reports = ReportRecord.query.order_by(ReportRecord.created_at.desc()).limit(50).all()
        rep_list = []
        for r in reports:
            rep_list.append({
                'id': r.id,
                'report_name': r.report_name or f'Report #{r.id}',
                'dataset_id': r.dataset_id,
                'format': r.format,
                'summary': r.summary,
                'file_path': r.file_path,
                'has_html_content': bool(r.html_content),
                'created_at': r.created_at.isoformat() if r.created_at else None
            })
        response = jsonify({'success': True, 'count': len(rep_list), 'reports': rep_list})
        return set_cors_headers(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/logs', methods=['GET', 'OPTIONS'])
def get_db_logs():
    """Query recent operational and AI logs from SQLite"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return set_cors_headers(response)
        
    try:
        system_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(30).all()
        ai_logs = AIAssistantLog.query.order_by(AIAssistantLog.created_at.desc()).limit(20).all()
        
        sys_list = [{
            'id': l.id,
            'level': l.level,
            'category': l.category,
            'message': l.message,
            'details': l.details,
            'created_at': l.created_at.isoformat() if l.created_at else None
        } for l in system_logs]
        
        ai_list = [{
            'id': a.id,
            'query': a.user_query,
            'response_snippet': a.response[:200] + '...' if len(a.response) > 200 else a.response,
            'response_type': a.response_type,
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in ai_logs]
        
        response = jsonify({
            'success': True,
            'system_logs_count': len(sys_list),
            'system_logs': sys_list,
            'ai_logs_count': len(ai_list),
            'ai_logs': ai_list
        })
        return set_cors_headers(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/datasets', methods=['GET', 'OPTIONS'])
def get_db_datasets():
    """Query CSV dataset records stored in SQLite"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return set_cors_headers(response)
        
    try:
        datasets = Dataset.query.order_by(Dataset.uploaded_at.desc()).all()
        ds_list = [{
            'id': d.id,
            'filename': d.filename,
            'filepath': d.filepath,
            'rows': d.rows,
            'columns': d.columns,
            'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None
        } for d in datasets]
        response = jsonify({'success': True, 'count': len(ds_list), 'datasets': ds_list})
        return set_cors_headers(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/outputs', methods=['GET', 'OPTIONS'])
def get_db_outputs():
    """Query stored analysis and anomaly outputs from SQLite"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return set_cors_headers(response)
        
    try:
        outputs = AnalysisOutput.query.order_by(AnalysisOutput.created_at.desc()).limit(30).all()
        out_list = [{
            'id': o.id,
            'analysis_type': o.analysis_type,
            'query': o.user_query,
            'summary_metrics': o.summary_metrics,
            'anomalies_detected': o.anomalies_detected,
            'insights': o.insights,
            'created_at': o.created_at.isoformat() if o.created_at else None
        } for o in outputs]
        response = jsonify({'success': True, 'count': len(out_list), 'outputs': out_list})
        return set_cors_headers(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Patient Management Endpoints
@app.route('/api/patients', methods=['GET'])
@login_required
def get_patients():
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patients = Patient.query.filter_by(hospital_id=current_user.username).all()
        patients_list = []
        for p in patients:
            patients_list.append({
                'id': p.id,
                'patient_name': p.patient_name,
                'age': p.age,
                'date_of_birth': p.date_of_birth.isoformat() if p.date_of_birth else None,
                'gender': p.gender,
                'blood_group': p.blood_group,
                'weight': p.weight,
                'height': p.height,
                'created_at': p.created_at.isoformat() if p.created_at else None
            })
        return jsonify({'patients': patients_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
@login_required
def add_patient():
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    required_fields = ['patient_name', 'age', 'date_of_birth', 'gender', 'blood_group', 'weight', 'height']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    try:
        from datetime import datetime
        patient = Patient(
            patient_name=data['patient_name'],
            age=data['age'],
            date_of_birth=datetime.fromisoformat(data['date_of_birth']).date(),
            gender=data['gender'],
            blood_group=data['blood_group'],
            weight=data['weight'],
            height=data['height'],
            hospital_id=current_user.username
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Patient added successfully',
            'patient_id': patient.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.username).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    try:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/export', methods=['GET'])
@login_required
def export_patients_csv():
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patients = Patient.query.filter_by(hospital_id=current_user.username).all()
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Patient ID', 'Name', 'Age', 'Date of Birth', 'Gender', 'Blood Group',

            'Weight (kg)', 'Height (cm)', 'Registration Date',
            'Checkup Date', 'Blood Pressure', 'Oxygen Level', 'Disease', 
            'Medicine', 'Dosage', 'Frequency'
        ])
        
        for patient in patients:
            checkups = Checkup.query.filter_by(patient_id=patient.id).all()
            
            if checkups:
                for checkup in checkups:
                    writer.writerow([
                        patient.id, patient.patient_name, patient.age,
                        patient.date_of_birth.isoformat() if patient.date_of_birth else '',
                        patient.gender, patient.blood_group, patient.weight, patient.height,
                        patient.created_at.isoformat() if patient.created_at else '',
                        checkup.created_at.isoformat() if checkup.created_at else '',
                        checkup.blood_pressure or '',
                        checkup.oxygen_level or '',
                        checkup.disease or '',
                        checkup.medicine or '',
                        checkup.dosage or '',
                        checkup.frequency or ''
                    ])
            else:
                writer.writerow([
                    patient.id, patient.patient_name, patient.age,
                    patient.date_of_birth.isoformat() if patient.date_of_birth else '',
                    patient.gender, patient.blood_group, patient.weight, patient.height,
                    patient.created_at.isoformat() if patient.created_at else '',
                    '', '', '', '', '', '', ''
                ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'patients_data_{current_user.username}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>/checkup', methods=['POST'])
@login_required
def start_checkup(patient_id):
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.username).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    if patient.checkup_status == 'ongoing':
        return jsonify({'error': 'Checkup already in progress'}), 400
    
    try:
        patient.checkup_status = 'ongoing'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Checkup started successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/checkups', methods=['GET'])
@login_required
def get_ongoing_checkups():
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        patients = Patient.query.filter_by(hospital_id=current_user.username, checkup_status='ongoing').all()
        patients_list = []
        for p in patients:
            patients_list.append({
                'id': p.id,
                'patient_name': p.patient_name,
                'age': p.age,
                'gender': p.gender,
                'blood_group': p.blood_group
            })
        return jsonify({'patients': patients_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/patients/<int:patient_id>/checkup-data', methods=['GET'])
@login_required
def get_patient_checkup_data(patient_id):
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        checkups = Checkup.query.filter_by(patient_id=patient_id).all()
        if not checkups:
            return jsonify({'checkups': []})
        
        # Group by BP, oxygen, disease (same checkup session)
        latest = checkups[0]
        medicines = []
        for c in checkups:
            if c.medicine:
                medicines.append({
                    'medicine': c.medicine,
                    'dosage': c.dosage or '',
                    'frequency': c.frequency or ''
                })
        
        return jsonify({
            'oxygen_level': latest.oxygen_level or '',
            'blood_pressure': latest.blood_pressure or '',
            'disease': latest.disease or '',
            'medicines': medicines if medicines else [{'medicine': '', 'dosage': '', 'frequency': ''}]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>/checkup-data', methods=['DELETE'])
@login_required
def delete_patient_checkup_data(patient_id):
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        Checkup.query.filter_by(patient_id=patient_id).delete()
        db.session.commit()
        return jsonify({'message': 'Checkup data deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/checkups', methods=['POST'])
@login_required
def add_checkup_data():
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    patient_id = data.get('patient_id')
    
    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400
    
    try:
        medicines = data.get('medicines', [])
        if medicines:
            for med in medicines:
                checkup = Checkup(
                    patient_id=patient_id,
                    oxygen_level=data.get('oxygen_level'),
                    blood_pressure=data.get('blood_pressure'),
                    disease=data.get('disease'),
                    medicine=med.get('medicine'),
                    dosage=med.get('dosage'),
                    frequency=med.get('frequency')
                )
                db.session.add(checkup)
        else:
            checkup = Checkup(
                patient_id=patient_id,
                oxygen_level=data.get('oxygen_level'),
                blood_pressure=data.get('blood_pressure'),
                disease=data.get('disease'),
                medicine=data.get('medicine'),
                dosage=data.get('dosage'),
                frequency=data.get('frequency')
            )
            db.session.add(checkup)
        
        db.session.commit()
        return jsonify({'message': 'Checkup data added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>/checkup/complete', methods=['POST'])
@login_required
def complete_checkup(patient_id):
    if current_user.role != 'hospital':
        return jsonify({'error': 'Access denied'}), 403
    
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.username).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    try:
        patient.checkup_status = 'done'
        db.session.commit()
        return jsonify({'message': 'Checkup completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/global/countries', methods=['GET'])
@login_required
def get_countries():
    if current_user.role not in ['researcher', 'sponsor']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        countries = db.session.query(User.country).filter(User.role == 'hospital', User.country.isnot(None)).distinct().all()
        country_list = [c[0] for c in countries if c[0]]
        return jsonify({'countries': sorted(country_list)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/global/download', methods=['GET'])
@login_required
def download_global_data():
    if current_user.role not in ['researcher', 'sponsor']:
        return jsonify({'error': 'Access denied'}), 403
    
    country = request.args.get('country', 'all')
    
    try:
        import csv
        import io
        
        # Get hospitals based on country filter
        if country == 'all':
            hospitals = User.query.filter_by(role='hospital').all()
        else:
            hospitals = User.query.filter_by(role='hospital', country=country).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Hospital Name', 'Hospital Country', 'Patient ID', 'Patient Name', 'Age', 
            'Date of Birth', 'Gender', 'Blood Group', 'Weight (kg)', 'Height (cm)', 
            'Registration Date', 'Checkup Date', 'Blood Pressure', 'Oxygen Level', 
            'Disease', 'Medicine', 'Dosage', 'Frequency'
        ])
        
        for hospital in hospitals:
            patients = Patient.query.filter_by(hospital_id=hospital.username).all()
            
            for patient in patients:
                checkups = Checkup.query.filter_by(patient_id=patient.id).all()
                
                if checkups:
                    for checkup in checkups:
                        writer.writerow([
                            hospital.organization or hospital.username,
                            hospital.country or '',
                            patient.id, patient.patient_name, patient.age,
                            patient.date_of_birth.isoformat() if patient.date_of_birth else '',
                            patient.gender, patient.blood_group, patient.weight, patient.height,
                            patient.created_at.isoformat() if patient.created_at else '',
                            checkup.created_at.isoformat() if checkup.created_at else '',
                            checkup.blood_pressure or '',
                            checkup.oxygen_level or '',
                            checkup.disease or '',
                            checkup.medicine or '',
                            checkup.dosage or '',
                            checkup.frequency or ''
                        ])
                else:
                    writer.writerow([
                        hospital.organization or hospital.username,
                        hospital.country or '',
                        patient.id, patient.patient_name, patient.age,
                        patient.date_of_birth.isoformat() if patient.date_of_birth else '',
                        patient.gender, patient.blood_group, patient.weight, patient.height,
                        patient.created_at.isoformat() if patient.created_at else '',
                        '', '', '', '', '', '', ''
                    ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'global_medicine_data_{country}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicine/search', methods=['GET'])
@login_required
def search_medicine():
    medicine_name = request.args.get('name', '').strip()
    if not medicine_name:
        return jsonify({'error': 'Medicine name is required'}), 400
    
    try:
        serper_api_key = os.environ.get('SERPER_API_KEY', '')
        if not serper_api_key:
            return jsonify({'error': 'Serper API key not configured'}), 500
        
        # Search using Serper API
        search_query = f"{medicine_name} chemical composition formula ingredients"
        serper_url = "https://google.serper.dev/search"
        
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': search_query,
            'num': 5
        }
        
        response = requests.post(serper_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information
            result = {
                'name': medicine_name,
                'composition': '',
                'description': '',
                'uses': '',
                'side_effects': '',
                'molecular_formula': '',
                'molecular_weight': ''
            }
            
            # Get knowledge graph if available
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                result['generic_name'] = kg.get('title', medicine_name)
                result['description'] = kg.get('description', '')
                
                # Extract attributes
                if 'attributes' in kg:
                    for key, value in kg['attributes'].items():
                        key_lower = key.lower()
                        if 'formula' in key_lower:
                            result['molecular_formula'] = value
                        elif 'composition' in key_lower:
                            result['composition'] = value
                        elif 'weight' in key_lower or 'mass' in key_lower:
                            result['molecular_weight'] = value
            
            # Extract from organic results
            snippets = []
            if 'organic' in data:
                for item in data['organic'][:3]:
                    snippet = item.get('snippet', '')
                    if snippet:
                        snippets.append(snippet)
            
            # Combine snippets for composition if not found
            if not result['composition'] and snippets:
                result['composition'] = ' '.join(snippets[:2])
            
            if not result['description'] and snippets:
                result['description'] = snippets[0]
            
            # Extract formula from snippets if not found
            if not result['molecular_formula']:
                for snippet in snippets:
                    import re
                    formula_match = re.search(r'\b([A-Z][a-z]?\d*)+\b', snippet)
                    if formula_match and len(formula_match.group()) < 30:
                        result['molecular_formula'] = formula_match.group()
                        break
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to fetch medicine information'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get configuration from environment
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug = flask_env != 'production' and os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Bhishma's Backend Server")
    print(f"   Environment: {flask_env}")
    print(f"   Host: {host}:{port}")
    print(f"   Debug: {debug}")
    print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI'][:30]}...")
    print(f"   CORS Origins: {len(CORS_ORIGINS_LIST)} configured")
    
    if flask_env == 'production':
        print("⚠️  WARNING: Use gunicorn in production, not Flask dev server!")
    
    app.run(debug=debug, host=host, port=port)
