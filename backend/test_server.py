#!/usr/bin/env python3
"""
Simple test server for drug testing routes
"""
from flask import Flask
from flask_cors import CORS
from drug_testing_routes import drug_testing_bp
import os

app = Flask(__name__)
CORS(app, origins=['*'])

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register blueprint
app.register_blueprint(drug_testing_bp)

@app.route('/')
def index():
    return {'message': 'Drug Testing API Server', 'status': 'running'}

if __name__ == '__main__':
    print("Starting test server on http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)