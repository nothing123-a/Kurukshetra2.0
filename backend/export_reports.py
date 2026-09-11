import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file

export_bp = Blueprint('export_reports', __name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available, PDF export will save as HTML")

def generate_pdf_report(analysis_data):
    """Generate PDF-compatible HTML report (no JavaScript)"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Drug Testing Analysis Report</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #1a1a1a;
                line-height: 1.6;
                font-size: 11pt;
            }}
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: white;
                margin: 0 0 10px 0;
                font-size: 28pt;
                font-weight: 700;
            }}
            .header p {{
                color: white;
                margin: 5px 0;
                font-size: 12pt;
            }}
            .section {{
                margin: 25px 0;
                page-break-inside: avoid;
            }}
            .section h2 {{
                color: #667eea;
                border-left: 5px solid #667eea;
                padding-left: 15px;
                padding-bottom: 8px;
                font-size: 18pt;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            .section h3 {{
                color: #2563eb;
                font-size: 14pt;
                margin-top: 15px;
                margin-bottom: 10px;
            }}
            .stats-grid {{
                display: table;
                width: 100%;
                margin: 20px 0;
            }}
            .stat-row {{
                display: table-row;
            }}
            .stat-card {{
                display: table-cell;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                text-align: center;
                color: white;
                border: 3px solid white;
            }}
            .stat-value {{
                font-size: 32pt;
                font-weight: bold;
                color: white;
                margin: 10px 0;
            }}
            .stat-label {{
                color: white;
                font-size: 10pt;
                font-weight: 500;
                text-transform: uppercase;
            }}
            .methodology {{
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid #dee2e6;
            }}
            .methodology-step {{
                margin: 15px 0;
                padding: 15px;
                padding-left: 20px;
                border-left: 4px solid #667eea;
                background: white;
            }}
            .list-section {{
                background: white;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid #e5e7eb;
            }}
            .list-section ul {{
                margin: 10px 0;
                padding-left: 25px;
            }}
            .list-section li {{
                margin: 10px 0;
                line-height: 1.6;
            }}
            .success {{
                color: #059669;
                font-weight: bold;
            }}
            .warning {{
                color: #d97706;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 40px;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                font-size: 10pt;
            }}
            .footer p {{
                margin: 5px 0;
                color: white;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #e5e7eb;
            }}
            th {{
                background: #667eea;
                font-weight: 600;
                color: white;
                text-transform: uppercase;
                font-size: 10pt;
            }}
            tr:nth-child(even) {{
                background: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Bhishma's AI - Structured Dataset Analysis Report</h1>
            <p>Comprehensive Autonomous Analysis Report</p>
            <p>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-row">
                    <div class="stat-card">
                        <div class="stat-label">Total Participants</div>
                        <div class="stat-value">{analysis_data.get('total_participants', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Success Rate</div>
                        <div class="stat-value">{analysis_data.get('overall_success_rate', 0)}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Risk Level</div>
                        <div class="stat-value">{analysis_data.get('risk_level', 'N/A')}</div>
                    </div>
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; color: white; margin-top: 15px;">
                <div class="stat-label">Final Recommendation</div>
                <div class="stat-value">{analysis_data.get('recommendation', 'N/A')}</div>
            </div>
        </div>

        <div class="section">
            <h2>Analysis Summary</h2>
            <p style="text-align: justify; line-height: 1.6;">{analysis_data.get('analysis_summary', 'Analysis completed successfully.')}</p>
        </div>

        <div class="section">
            <h2>Methodology</h2>
            <div class="methodology">
                <div class="methodology-step">
                    <h3>Step 1: Risk Analysis</h3>
                    <p>{analysis_data.get('methodology', {}).get('step1', 'BioBERT-based analysis')}</p>
                </div>
                <div class="methodology-step">
                    <h3>Step 2: Feature Engineering</h3>
                    <p>{analysis_data.get('methodology', {}).get('step2', 'Feature selection and analysis')}</p>
                </div>
                <div class="methodology-step">
                    <h3>Step 3: Human Testing</h3>
                    <p>{analysis_data.get('methodology', {}).get('step3', 'Clinical trials on participants')}</p>
                </div>
                <div class="methodology-step">
                    <h3>Step 4: Final Analysis</h3>
                    <p>{analysis_data.get('methodology', {}).get('step4', 'Comprehensive evaluation')}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Phase-wise Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Phase</th>
                        <th>Score</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Risk Analysis</td>
                        <td>{analysis_data.get('phase_scores', {}).get('risk_analysis', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                    <tr>
                        <td>Feature Engineering</td>
                        <td>{analysis_data.get('phase_scores', {}).get('feature_engineering', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                    <tr>
                        <td>Human Testing</td>
                        <td>{analysis_data.get('phase_scores', {}).get('human_testing', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                    <tr>
                        <td>Final Analysis</td>
                        <td>{analysis_data.get('phase_scores', {}).get('final_analysis', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Participant Demographics</h2>
            <h3>Age Group Distribution</h3>
            <table>
                <thead>
                    <tr>
                        <th>Age Group</th>
                        <th>Participants</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add age group data
    age_analysis = analysis_data.get('age_body_disease_analysis', {})
    total = analysis_data.get('total_participants', 1)
    for age_group, data in age_analysis.items():
        count = data.get('count', 0)
        percentage = (count / total * 100) if total > 0 else 0
        html_content += f"""
                    <tr>
                        <td>{age_group} years</td>
                        <td>{count}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Key Findings</h2>
            <div class="list-section">
                <h3 class="success">✓ Strengths</h3>
                <ul>
"""
    
    for strength in analysis_data.get('strengths', []):
        html_content += f"                    <li>{strength}</li>\n"
    
    html_content += """
                </ul>
            </div>
            <div class="list-section">
                <h3 class="warning">⚠ Considerations</h3>
                <ul>
"""
    
    for consideration in analysis_data.get('considerations', []):
        html_content += f"                    <li>{consideration}</li>\n"
    
    html_content += f"""
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>Statistical Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Average Toxicity</td>
                        <td>{analysis_data.get('csv_stats', {}).get('avg_toxicity', 0)}/10</td>
                    </tr>
                    <tr>
                        <td>Average Efficacy</td>
                        <td>{analysis_data.get('csv_stats', {}).get('avg_efficacy', 0)}/10</td>
                    </tr>
                    <tr>
                        <td>Average Quality</td>
                        <td>{analysis_data.get('csv_stats', {}).get('avg_quality', 0)}%</td>
                    </tr>
                    <tr>
                        <td>Total Ingredients Analyzed</td>
                        <td>{analysis_data.get('csv_stats', {}).get('total_ingredients', 0)}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>Bhishma's AI - Structured Dataset Analysis System</strong></p>
            <p>This report is generated automatically based on comprehensive autonomous data inspection and statistical intelligence.</p>
            <p>© {datetime.now().year} Bhishma's AI Platform. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def generate_html_report(analysis_data):
    """Generate interactive HTML report with JavaScript charts"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Drug Testing Analysis Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px;
                color: #1a1a1a;
                line-height: 1.8;
                background: #f8f9fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 20px;
                margin: -40px -40px 40px -40px;
                border-radius: 0;
            }}
            .header h1 {{
                color: white;
                margin: 0 0 10px 0;
                font-size: 36px;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }}
            .header p {{
                color: rgba(255,255,255,0.9);
                margin: 5px 0;
                font-size: 16px;
            }}
            .section {{
                margin: 40px 0;
                page-break-inside: avoid;
            }}
            .section h2 {{
                color: #667eea;
                border-left: 5px solid #667eea;
                padding-left: 15px;
                padding-bottom: 10px;
                font-size: 28px;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            .section h3 {{
                color: #2563eb;
                font-size: 18px;
                margin-top: 20px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 25px;
                margin: 30px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                transition: transform 0.3s;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-value {{
                font-size: 42px;
                font-weight: bold;
                color: white;
                margin: 10px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }}
            .stat-label {{
                color: rgba(255,255,255,0.9);
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .methodology {{
                background: linear-gradient(to right, #f8f9fa, #e9ecef);
                padding: 30px;
                border-radius: 12px;
                margin: 20px 0;
                border: 1px solid #dee2e6;
            }}
            .methodology-step {{
                margin: 20px 0;
                padding: 20px;
                padding-left: 25px;
                border-left: 4px solid #667eea;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .list-section {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                margin: 20px 0;
                border: 1px solid #e5e7eb;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            .list-section ul {{
                margin: 15px 0;
                padding-left: 25px;
            }}
            .list-section li {{
                margin: 12px 0;
                line-height: 1.8;
                position: relative;
            }}
            .list-section li:before {{
                content: '•';
                color: #667eea;
                font-weight: bold;
                font-size: 20px;
                position: absolute;
                left: -20px;
            }}
            .success {{
                color: #059669;
                font-weight: bold;
            }}
            .warning {{
                color: #d97706;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 60px;
                padding: 30px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                font-size: 13px;
                margin: 60px -40px -40px -40px;
                border-radius: 0;
            }}
            .footer p {{
                margin: 8px 0;
                color: rgba(255,255,255,0.9);
            }}
            .footer strong {{
                color: white;
                font-size: 16px;
            }}
            table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin: 25px 0;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }}
            th, td {{
                padding: 16px;
                text-align: left;
                border-bottom: 1px solid #e5e7eb;
            }}
            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-weight: 600;
                color: white;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 13px;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            tr:last-child td {{
                border-bottom: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
        <div class="header">
            <h1>Bhishma's AI - Structured Dataset Analysis Report</h1>
            <p>Comprehensive Autonomous Analysis Report</p>
            <p>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Participants</div>
                    <div class="stat-value">{analysis_data.get('total_participants', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Success Rate</div>
                    <div class="stat-value success">{analysis_data.get('overall_success_rate', 0)}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Risk Level</div>
                    <div class="stat-value">{analysis_data.get('risk_level', 'N/A')}</div>
                </div>
            </div>
            <div class="stat-card" style="margin-top: 20px;">
                <div class="stat-label">Final Recommendation</div>
                <div class="stat-value success">{analysis_data.get('recommendation', 'N/A')}</div>
            </div>
        </div>

        <div class="section">
            <h2>Analysis Summary</h2>
            <p style="text-align: justify; line-height: 1.8;">{analysis_data.get('analysis_summary', 'Analysis completed successfully.')}</p>
        </div>

        <div class="section">
            <h2>Methodology</h2>
            <div class="methodology">
                <div class="methodology-step">
                    <h3>Step 1: Risk Analysis</h3>
                    <p>{analysis_data.get('methodology', {}).get('step1', 'BioBERT-based analysis')}</p>
                </div>
                <div class="methodology-step">
                    <h3>Step 2: Feature Engineering</h3>
                    <p>{analysis_data.get('methodology', {}).get('step2', 'Feature selection and analysis')}</p>
                </div>
                <div class="methodology-step">
                    <h3>Step 3: Human Testing</h3>
                    <p>{analysis_data.get('methodology', {}).get('step3', 'Clinical trials on participants')}</p>
                </div>
                <div class="methodology-step">
                    <h3>Step 4: Final Analysis</h3>
                    <p>{analysis_data.get('methodology', {}).get('step4', 'Comprehensive evaluation')}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Phase-wise Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Phase</th>
                        <th>Score</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Risk Analysis</td>
                        <td>{analysis_data.get('phase_scores', {}).get('risk_analysis', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                    <tr>
                        <td>Feature Engineering</td>
                        <td>{analysis_data.get('phase_scores', {}).get('feature_engineering', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                    <tr>
                        <td>Human Testing</td>
                        <td>{analysis_data.get('phase_scores', {}).get('human_testing', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                    <tr>
                        <td>Final Analysis</td>
                        <td>{analysis_data.get('phase_scores', {}).get('final_analysis', 0)}%</td>
                        <td class="success">✓ Passed</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Participant Demographics</h2>
            <h3>Age Group Distribution</h3>
            <table>
                <thead>
                    <tr>
                        <th>Age Group</th>
                        <th>Participants</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add age group data
    age_analysis = analysis_data.get('age_body_disease_analysis', {})
    total = analysis_data.get('total_participants', 1)
    for age_group, data in age_analysis.items():
        count = data.get('count', 0)
        percentage = (count / total * 100) if total > 0 else 0
        html_content += f"""
                    <tr>
                        <td>{age_group} years</td>
                        <td>{count}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Key Findings</h2>
            <div class="list-section">
                <h3 class="success">✓ Strengths</h3>
                <ul>
"""
    
    for strength in analysis_data.get('strengths', []):
        html_content += f"                    <li>{strength}</li>\n"
    
    html_content += """
                </ul>
            </div>
            <div class="list-section">
                <h3 class="warning">⚠ Considerations</h3>
                <ul>
"""
    
    for consideration in analysis_data.get('considerations', []):
        html_content += f"                    <li>{consideration}</li>\n"
    
    html_content += f"""
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>Analysis Graphs</h2>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; margin: 30px 0;">
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
                    <canvas id="phaseScoresChart"></canvas>
                </div>
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
                    <canvas id="participantChart"></canvas>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Statistical Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Average Toxicity</td>
                        <td>{analysis_data.get('csv_stats', {}).get('avg_toxicity', 0)}/10</td>
                    </tr>
                    <tr>
                        <td>Average Efficacy</td>
                        <td>{analysis_data.get('csv_stats', {}).get('avg_efficacy', 0)}/10</td>
                    </tr>
                    <tr>
                        <td>Average Quality</td>
                        <td>{analysis_data.get('csv_stats', {}).get('avg_quality', 0)}%</td>
                    </tr>
                    <tr>
                        <td>Total Ingredients Analyzed</td>
                        <td>{analysis_data.get('csv_stats', {}).get('total_ingredients', 0)}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>Bhishma's AI - Structured Dataset Analysis System</strong></p>
            <p>This report is generated automatically based on comprehensive autonomous data inspection and statistical intelligence.</p>
            <p>© {datetime.now().year} Bhishma's AI Platform. All rights reserved.</p>
        </div>
        </div>
        <script>
            // Phase Scores Chart
            const phaseCtx = document.getElementById('phaseScoresChart').getContext('2d');
            new Chart(phaseCtx, {{
                type: 'bar',
                data: {{
                    labels: ['Risk Analysis', 'Feature Engineering', 'Human Testing', 'Final Analysis'],
                    datasets: [{{
                        label: 'Phase Scores (%)',
                        data: [{analysis_data.get('phase_scores', {}).get('risk_analysis', 0)}, 
                               {analysis_data.get('phase_scores', {}).get('feature_engineering', 0)}, 
                               {analysis_data.get('phase_scores', {}).get('human_testing', 0)}, 
                               {analysis_data.get('phase_scores', {}).get('final_analysis', 0)}],
                        backgroundColor: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B'],
                        borderWidth: 0,
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Phase-wise Success Scores',
                            font: {{ size: 16, weight: 'bold' }}
                        }},
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{ callback: function(value) {{ return value + '%'; }} }}
                        }}
                    }}
                }}
            }});

            // Participant Distribution Chart
            const partCtx = document.getElementById('participantChart').getContext('2d');
            const ageData = {json.dumps(list(age_analysis.items()))};
            new Chart(partCtx, {{
                type: 'pie',
                data: {{
                    labels: ageData.map(item => item[0] + ' years'),
                    datasets: [{{
                        data: ageData.map(item => item[1].count),
                        backgroundColor: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Participant Distribution by Age Group',
                            font: {{ size: 16, weight: 'bold' }}
                        }},
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

@export_bp.route('/api/export/html', methods=['POST', 'OPTIONS'])
def export_html():
    """Export analysis as HTML"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        
        html_content = generate_html_report(analysis_data)
        
        # Save HTML file
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"drug_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(upload_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report saved: {filepath}")
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/html')
        
    except Exception as e:
        print(f"HTML export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@export_bp.route('/api/export/pdf', methods=['POST', 'OPTIONS'])
def export_pdf():
    """Export analysis as PDF"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        
        html_content = generate_html_report(analysis_data)
        
        # Save PDF file
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"drug_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(upload_folder, filename)
        
        if REPORTLAB_AVAILABLE:
            try:
                # Create PDF using ReportLab
                doc = SimpleDocTemplate(filepath, pagesize=A4)
                story = []
                styles = getSampleStyleSheet()
                
                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#667eea'),
                    spaceAfter=30,
                    alignment=TA_CENTER
                )
                
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=16,
                    textColor=colors.HexColor('#667eea'),
                    spaceAfter=12,
                    spaceBefore=12
                )
                
                # Title
                story.append(Paragraph("Bhishma's AI - Structured Dataset Analysis Report", title_style))
                story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
                
                # Executive Summary
                story.append(Paragraph("Executive Summary", heading_style))
                summary_data = [
                    ['Metric', 'Value'],
                    ['Total Participants', str(analysis_data.get('total_participants', 0))],
                    ['Success Rate', f"{analysis_data.get('overall_success_rate', 0)}%"],
                    ['Risk Level', analysis_data.get('risk_level', 'N/A')],
                    ['Recommendation', analysis_data.get('recommendation', 'N/A')]
                ]
                summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Analysis Summary
                story.append(Paragraph("Analysis Summary", heading_style))
                story.append(Paragraph(analysis_data.get('analysis_summary', 'Analysis completed successfully.'), styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
                
                # Phase-wise Performance
                story.append(Paragraph("Phase-wise Performance", heading_style))
                phase_data = [
                    ['Phase', 'Score', 'Status'],
                    ['Risk Analysis', f"{analysis_data.get('phase_scores', {}).get('risk_analysis', 0)}%", '✓ Passed'],
                    ['Feature Engineering', f"{analysis_data.get('phase_scores', {}).get('feature_engineering', 0)}%", '✓ Passed'],
                    ['Human Testing', f"{analysis_data.get('phase_scores', {}).get('human_testing', 0)}%", '✓ Passed'],
                    ['Final Analysis', f"{analysis_data.get('phase_scores', {}).get('final_analysis', 0)}%", '✓ Passed']
                ]
                phase_table = Table(phase_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
                phase_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(phase_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Participant Demographics
                story.append(Paragraph("Participant Demographics", heading_style))
                age_analysis = analysis_data.get('age_body_disease_analysis', {})
                total = analysis_data.get('total_participants', 1)
                demo_data = [['Age Group', 'Participants', 'Percentage']]
                for age_group, data in age_analysis.items():
                    count = data.get('count', 0)
                    percentage = (count / total * 100) if total > 0 else 0
                    demo_data.append([f"{age_group} years", str(count), f"{percentage:.1f}%"])
                
                demo_table = Table(demo_data, colWidths=[2*inch, 2*inch, 2*inch])
                demo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(demo_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Statistical Summary
                story.append(Paragraph("Statistical Summary", heading_style))
                stats_data = [
                    ['Metric', 'Value'],
                    ['Average Toxicity', f"{analysis_data.get('csv_stats', {}).get('avg_toxicity', 0)}/10"],
                    ['Average Efficacy', f"{analysis_data.get('csv_stats', {}).get('avg_efficacy', 0)}/10"],
                    ['Average Quality', f"{analysis_data.get('csv_stats', {}).get('avg_quality', 0)}%"],
                    ['Total Ingredients', str(analysis_data.get('csv_stats', {}).get('total_ingredients', 0))]
                ]
                stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(stats_table)
                
                # Build PDF
                doc.build(story)
                print(f"PDF generated successfully: {filepath}")
            except Exception as pdf_error:
                print(f"PDF generation error: {pdf_error}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'PDF generation failed: {str(pdf_error)}'}), 500
        else:
            return jsonify({'error': 'ReportLab not installed. Cannot generate PDF.'}), 500
        
        print(f"Report saved: {filepath}")
        
        # Determine correct mimetype
        if filepath.endswith('.pdf'):
            mimetype = 'application/pdf'
        else:
            mimetype = 'text/html'
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)
        
    except Exception as e:
        print(f"PDF export error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
