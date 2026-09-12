# BioBERT Risk Analysis System

## Overview
The BioBERT Risk Analysis system provides comprehensive biomedical data analysis with AI-powered insights and interactive visualizations.

## Features

### 🧬 BioBERT Analysis Engine
- **Biomedical Entity Detection**: Automatically identifies toxicity, efficacy, quality, and other clinical parameters
- **Risk Stratification**: LOW, MEDIUM, or HIGH risk classification
- **Success Probability**: Calculated based on multiple biomedical factors
- **Comprehensive Metrics**: Detailed statistics for all detected parameters

### 📊 Graph Generation
All parameters are evaluated and visualized:

1. **Toxicity Distribution** (Bar Chart)
   - Mean, max, min, standard deviation
   - Sample-by-sample toxicity levels
   - Safety profile assessment

2. **Efficacy Profile** (Line Chart)
   - Therapeutic potential analysis
   - Efficacy trends across samples
   - Statistical metrics

3. **Quality Assessment** (Bar Chart)
   - Quality scores per sample
   - Mean and standard deviation
   - Quality control insights

4. **Data Completeness** (Bar Chart)
   - Missing data per column
   - Overall completeness percentage
   - Data quality indicators

5. **Risk Overview** (Radar Chart)
   - Multi-dimensional risk assessment
   - Success probability
   - Safety, efficacy, and quality scores
   - Comprehensive risk profile

### 🔬 BioBERT Evaluation Parameters

#### Detected Biomedical Entities:
- **Toxicity**: toxic, tox, safety, adverse, ld50, cytotox
- **Efficacy**: efficacy, effect, potency, activity, ic50, ec50
- **Molecular**: molecular, weight, mass, mw, formula
- **Bioavailability**: bioavail, absorption, uptake, adme
- **Quality**: quality, purity, grade, assay
- **Dosage**: dose, dosage, concentration, mg, ml, molar
- **Clinical**: phase, trial, patient, outcome, endpoint

#### Risk Factors Assessed:
- Cytotoxicity levels
- Therapeutic efficacy
- Data completeness
- Sample size adequacy
- Quality standards
- Missing data percentage

#### Recommendations Generated:
- Safety profile assessment
- Therapeutic potential evaluation
- Data quality improvements
- Clinical protocol suggestions
- Biomarker monitoring advice

## API Endpoints

### 1. Status Check
```bash
GET /api/risk-analysis/status
```

**Response:**
```json
{
  "success": true,
  "status": "ready",
  "message": "BioBERT risk analysis service is ready",
  "analysis_engine": "biobert_biomedical"
}
```

### 2. Upload & Analyze
```bash
POST /api/risk-analysis/upload
Content-Type: multipart/form-data
```

**Request:**
- `file`: CSV file with biomedical data

**Response:**
```json
{
  "success": true,
  "filename": "compounds.csv",
  "data_stats": {
    "rows": 10,
    "columns": 6,
    "column_names": ["compound_id", "toxicity", "efficacy", "pIC50", "quality", "SMILES"],
    "completeness": 100.0
  },
  "biobert_analysis": {
    "risk_level": "MEDIUM",
    "success_probability": 45,
    "bio_metrics": {
      "toxicity_avg": 2.37,
      "toxicity_max": 3.5,
      "toxicity_min": 1.7,
      "toxicity_std": 0.61,
      "efficacy_avg": 7.56,
      "efficacy_max": 8.8,
      "efficacy_min": 5.9,
      "efficacy_std": 0.94,
      "quality_avg": 92.28,
      "quality_std": 3.88,
      "completeness": 100.0
    },
    "graphs": {
      "toxicity": {
        "type": "bar",
        "title": "BioBERT Toxicity Distribution",
        "data": [2.1, 3.2, 1.8, 2.5, 1.9, 3.5, 2.2, 1.7, 2.8, 2.0],
        "labels": ["Sample 1", "Sample 2", ...],
        "stats": {"mean": 2.37, "max": 3.5, "min": 1.7, "std": 0.61}
      },
      "efficacy": {
        "type": "line",
        "title": "BioBERT Efficacy Profile",
        "data": [7.8, 6.5, 8.2, 7.1, 8.5, 5.9, 7.9, 8.8, 6.8, 8.1],
        "labels": ["Sample 1", "Sample 2", ...],
        "stats": {"mean": 7.56, "max": 8.8, "min": 5.9, "std": 0.94}
      },
      "quality": {
        "type": "bar",
        "title": "BioBERT Quality Assessment",
        "data": [95.2, 88.5, 92.1, 90.3, 96.8, 85.4, 93.7, 97.2, 89.1, 94.5],
        "labels": ["Sample 1", "Sample 2", ...],
        "stats": {"mean": 92.28, "std": 3.88}
      },
      "risk_overview": {
        "type": "radar",
        "title": "BioBERT Comprehensive Risk Assessment",
        "data": [45, 100, 76.3, 75.6, 92.28],
        "labels": ["Success Probability", "Data Completeness", "Safety Profile", "Efficacy", "Quality"]
      }
    },
    "risk_factors": [
      "BioBERT: Moderate toxicity concern (avg: 2.4)",
      "Small sample size: 10 records"
    ],
    "recommendations": [
      "BioBERT: Moderate efficacy profile (7.6)",
      "Excellent data completeness"
    ],
    "biobert_analysis": "BioBERT indicates moderate risk-benefit profile"
  },
  "message": "BioBERT risk analysis completed successfully",
  "analysis_type": "biobert_biomedical"
}
```

## Testing

### Quick Test
```bash
python3 quick_test_biobert.py
```

### Comprehensive Test with Graphs
```bash
python3 test_biobert_graphs.py
```

### Manual cURL Test
```bash
# Create test file
cat > test_compounds.csv << EOF
compound_id,toxicity,efficacy,pIC50,quality,SMILES
COMP001,2.1,7.8,6.5,95.2,CCO
COMP002,3.2,6.5,5.8,88.5,CCC
COMP003,1.8,8.2,7.2,92.1,CCCO
EOF

# Upload and analyze
curl -X POST http://localhost:8000/api/risk-analysis/upload \
  -F "file=@test_compounds.csv" | python3 -m json.tool
```

## CSV Format Requirements

### Required Columns (at least one):
- Toxicity-related: `toxicity`, `tox`, `safety`, `adverse`, `ld50`, `cytotox`
- Efficacy-related: `efficacy`, `effect`, `potency`, `activity`, `ic50`, `ec50`
- Quality-related: `quality`, `purity`, `grade`, `assay`

### Example CSV:
```csv
compound_id,toxicity,efficacy,pIC50,quality,SMILES
COMP001,2.1,7.8,6.5,95.2,CCO
COMP002,3.2,6.5,5.8,88.5,CCC
COMP003,1.8,8.2,7.2,92.1,CCCO
```

## Risk Level Classification

- **LOW**: Success probability > 80%
  - Favorable safety profile
  - Strong therapeutic potential
  - High data quality

- **MEDIUM**: Success probability 35-80%
  - Moderate risk-benefit profile
  - Acceptable safety and efficacy
  - Standard monitoring required

- **HIGH**: Success probability < 35%
  - Significant safety concerns
  - Suboptimal efficacy
  - Enhanced monitoring needed

## Integration with Frontend

The frontend can use the graph data to render interactive charts:

```javascript
// Example: Render toxicity chart
const toxicityGraph = analysis.graphs.toxicity;
renderChart({
  type: toxicityGraph.type,
  title: toxicityGraph.title,
  data: toxicityGraph.data,
  labels: toxicityGraph.labels
});
```

## Notes

- Maximum file size: 5MB
- Supported format: CSV only
- First 50 samples are used for graph generation
- All numeric columns are analyzed for statistics
- BioBERT automatically detects biomedical entities
