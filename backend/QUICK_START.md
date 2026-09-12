# BioBERT Risk Analysis - Quick Start Guide

## ✅ System Status: OPERATIONAL

### Quick Test (30 seconds)
```bash
cd backend
python3 quick_test_biobert.py
```

Expected output:
```
✅ Status: BioBERT risk analysis service is ready
✅ Engine: biobert_biomedical
✅ Risk Level: MEDIUM
✅ Success Rate: 45%
✅ BioBERT Working!
```

### Comprehensive Test with Graphs
```bash
python3 test_biobert_graphs.py
```

Expected output:
```
📊 Bio Metrics: 8 parameters evaluated
📈 Graphs Generated: 4 charts
   ✓ toxicity: bar chart
   ✓ efficacy: line chart
   ✓ quality: bar chart
   ✓ risk_overview: radar chart
```

## API Endpoints

### 1. Check Status
```bash
curl http://localhost:8000/api/risk-analysis/status
```

### 2. Analyze CSV File
```bash
curl -X POST http://localhost:8000/api/risk-analysis/upload \
  -F "file=@your_data.csv"
```

## Sample CSV Format
```csv
compound_id,toxicity,efficacy,pIC50,quality,SMILES
COMP001,2.1,7.8,6.5,95.2,CCO
COMP002,3.2,6.5,5.8,88.5,CCC
COMP003,1.8,8.2,7.2,92.1,CCCO
```

## Response Structure
```json
{
  "biobert_analysis": {
    "risk_level": "MEDIUM",
    "success_probability": 45,
    "bio_metrics": {
      "toxicity_avg": 2.37,
      "efficacy_avg": 7.56,
      "quality_avg": 92.28
    },
    "graphs": {
      "toxicity": { "type": "bar", "data": [...] },
      "efficacy": { "type": "line", "data": [...] },
      "quality": { "type": "bar", "data": [...] },
      "risk_overview": { "type": "radar", "data": [...] }
    }
  }
}
```

## Graph Types

| Parameter | Chart Type | Use Case |
|-----------|------------|----------|
| Toxicity | Bar | Safety assessment |
| Efficacy | Line | Therapeutic trends |
| Quality | Bar | QC standards |
| Risk Overview | Radar | Multi-dimensional view |

## Frontend Integration

```javascript
// Fetch analysis
const formData = new FormData();
formData.append('file', csvFile);

const response = await fetch('http://localhost:8000/api/risk-analysis/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
const analysis = JSON.parse(data.biobert_analysis);

// Render graphs
renderBarChart(analysis.graphs.toxicity);
renderLineChart(analysis.graphs.efficacy);
renderRadarChart(analysis.graphs.risk_overview);
```

## Troubleshooting

### Backend not running?
```bash
cd backend
python3 app.py
```

### Port 8000 in use?
```bash
lsof -i :8000
kill -9 <PID>
```

### Test failing?
```bash
# Check server status
curl http://localhost:8000/health

# Check risk analysis status
curl http://localhost:8000/api/risk-analysis/status
```

## Documentation

- **Full Docs**: `BIOBERT_RISK_ANALYSIS.md`
- **Summary**: `RISK_ANALYSIS_SUMMARY.md`
- **This Guide**: `QUICK_START.md`

## Support

All endpoints tested and verified ✅
Ready for production use 🚀
