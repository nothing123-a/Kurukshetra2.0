#!/usr/bin/env python3
"""
Augmentation API Routes for Refinify
"""

from flask import request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
from datetime import datetime

def register_augmentation_routes(app, augmentation_service, set_cors_headers, allowed_file, current_user, ActivityHistory, db):
    """Register augmentation routes with the Flask app"""
    
    @app.route('/api/augmentation/upload', methods=['POST', 'OPTIONS'])
    def augmentation_upload():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response = set_cors_headers(response)
            return response
        
        if not augmentation_service:
            return jsonify({'error': 'Augmentation service not available'}), 503
        
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
                
                # Load data using pandas
                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                # Basic cleaning
                df = df.dropna(how='all').dropna(axis=1, how='all')
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                if df.empty:
                    return jsonify({'error': 'No valid data found'}), 400
                
                # Convert to safe format
                safe_data = []
                for _, row in df.iterrows():
                    record = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            record[str(col)] = None
                        elif isinstance(value, (int, float)):
                            record[str(col)] = float(value) if not np.isnan(value) else None
                        else:
                            record[str(col)] = str(value)
                    safe_data.append(record)
                
                return jsonify({
                    "filename": filename,
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
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
        
        if not augmentation_service:
            return jsonify({'error': 'Augmentation service not available'}), 503
        
        data = request.json
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            result = augmentation_service.smart_augmentation(data['data'])
            
            return jsonify({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/augmentation/process-command', methods=['POST', 'OPTIONS'])
    def process_augmentation_command():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response = set_cors_headers(response)
            return response
        
        if not augmentation_service:
            return jsonify({'error': 'Augmentation service not available'}), 503
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        command = data.get('command', '')
        columns = data.get('columns', [])
        dataset = data.get('data', [])
        
        if not command:
            return jsonify({'error': 'Command is required'}), 400
        
        try:
            result = augmentation_service.process_command(command, columns, dataset)
            
            # Save processed data to CSV if processing was successful
            if result.get('processed_data'):
                try:
                    processed_df = pd.DataFrame(result['processed_data'])
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    csv_filename = f'processed_data_{timestamp}.csv'
                    csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
                    processed_df.to_csv(csv_filepath, index=False)
                    
                    result['csv_saved'] = True
                    result['csv_filename'] = csv_filename
                    result['csv_path'] = csv_filepath
                    
                except Exception as csv_error:
                    print(f"CSV save error: {csv_error}")
                    result['csv_saved'] = False
            
            return jsonify({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500