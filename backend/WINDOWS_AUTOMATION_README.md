# 🚀 Windows Automation System for Refinify-AI

## Overview
This is a **Windows-native automation system** that provides the same core functionality as Apache Airflow but works perfectly on Windows without compatibility issues.

## ✨ Features
- **Automated Data Processing** - Every 6 hours
- **Quality Monitoring** - Tracks accuracy and quality
- **Automatic Backups** - Daily backups at 2:00 AM
- **Data Cleaning** - Removes duplicates, handles missing values
- **Outlier Detection** - Identifies statistical outliers
- **Accuracy Thresholds** - Configurable quality standards
- **Detailed Logging** - Complete audit trail
- **Report Generation** - JSON reports for each cycle

## 🎯 How It Works
1. **Monitors** your `uploads/` directory for new data files
2. **Processes** CSV and Excel files automatically
3. **Cleans** data and detects outliers
4. **Tracks** accuracy and quality metrics
5. **Creates** backups before processing
6. **Generates** detailed reports
7. **Alerts** when manual review is needed

## 🚀 Quick Start

### Step 1: Install Required Packages
```bash
pip install pandas numpy schedule
```

### Step 2: Start the Automation
**Option A: Use the batch file (Recommended)**
```bash
# Double-click this file or run from command line:
start_windows_automation.bat
```

**Option B: Run directly with Python**
```bash
python windows_automation.py
```

### Step 3: Add Data Files
Place your data files (CSV or Excel) in the `uploads/` directory:
```
uploads/
├── survey_data.csv
├── customer_data.xlsx
└── analysis_results.csv
```

## 📊 Accuracy Thresholds

| Task | Threshold | Action |
|------|-----------|---------|
| Data Cleaning | 95% | Continue processing |
| Outlier Detection | 90% | Continue processing |
| Manual Review | 80% | Alert user |
| Stop Automation | <70% | Halt processing |

## ⚙️ Configuration

Edit `automation_config.json` to customize:

```json
{
  "data_processing_interval_hours": 6,    // How often to process data
  "backup_interval_hours": 24,            // How often to backup
  "quality_check_interval_hours": 12,     // Quality check frequency
  "max_backup_size_gb": 10,              // Maximum backup size
  "enable_email_alerts": false,           // Email notifications
  "admin_email": "admin@refinify-ai.com" // Admin email
}
```

## 📁 Directory Structure

```
backend/
├── windows_automation.py          # Main automation script
├── start_windows_automation.bat   # Windows startup script
├── automation_config.json         # Configuration file
├── uploads/                       # Place data files here
├── backups/                       # Automatic backups
├── logs/                          # Log files
├── reports/                       # Generated reports
└── automation.log                 # Main log file
```

## 🔍 Monitoring & Logs

### Real-time Monitoring
The system runs continuously and shows:
- Processing status
- Accuracy scores
- Files processed
- Errors and warnings
- Backup status

### Log Files
- **`automation.log`** - Main activity log
- **`reports/`** - JSON reports for each cycle
- **Console output** - Real-time status updates

## 📋 Usage Examples

### 1. Start Automation
```bash
# Double-click the batch file
start_windows_automation.bat

# Or run manually
python windows_automation.py
```

### 2. Add Data for Processing
```bash
# Copy your data files to uploads directory
copy "C:\MyData\survey_results.csv" "uploads\"
```

### 3. Monitor Progress
Watch the console output for:
- Processing status
- Accuracy scores
- File counts
- Error messages

### 4. Check Results
```bash
# View generated files
dir "uploads\*_cleaned.csv"
dir "uploads\*_outliers.csv"
dir "reports\"
```

## 🛡️ Safety Features

### Automatic Backups
- Creates backup before processing
- Includes database, config files, and uploads
- Timestamped backup directories
- Configurable size limits

### Quality Control
- Accuracy monitoring
- Data integrity checks
- Automatic rollback on failures
- Manual review triggers

### Error Handling
- Graceful failure handling
- Detailed error logging
- Automatic retry logic
- Circuit breaker pattern

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install pandas numpy schedule
```

**2. Permission errors**
- Run as Administrator
- Check file permissions

**3. Port conflicts**
- The system doesn't use network ports
- No conflicts with other services

**4. Memory issues**
- Check available disk space
- Monitor backup directory size

### Debug Mode
```bash
# Check logs
type automation.log

# Check configuration
type automation_config.json

# Check directory structure
dir /s
```

## 📈 Performance Tips

### Optimization
- **Batch Size**: Process multiple files together
- **Backup Cleanup**: Regularly clean old backups
- **Log Rotation**: Monitor log file sizes
- **Resource Usage**: Check disk space regularly

### Monitoring
- Watch accuracy scores over time
- Monitor processing times
- Check backup sizes
- Review error patterns

## 🔄 Integration with Your Project

### Works With
- Your existing `data_analyzer.py`
- Your existing `data_augmenter.py`
- Your existing `enhanced_typo_correction.py`
- Your Flask backend (`app.py`)

### Extends Functionality
- Automated data processing
- Quality monitoring
- Safety backups
- Performance tracking

## 🎉 Benefits Over Airflow

| Feature | Airflow | Windows Automation |
|---------|---------|-------------------|
| Windows Support | ❌ Limited | ✅ Full Support |
| Installation | 🟡 Complex | ✅ Simple |
| Dependencies | 🟡 Many | ✅ Few |
| Performance | 🟡 Good | ✅ Excellent |
| Maintenance | 🟡 High | ✅ Low |
| Learning Curve | 🟡 Steep | ✅ Gentle |

## 🚀 Next Steps

1. **Start the automation**: Run `start_windows_automation.bat`
2. **Add your data**: Place files in `uploads/` directory
3. **Monitor progress**: Watch console output
4. **Customize settings**: Edit `automation_config.json`
5. **Scale up**: Add more processing tasks

## 📞 Support

### Getting Help
1. Check the logs in `automation.log`
2. Review generated reports in `reports/` directory
3. Check console output for error messages
4. Verify file permissions and paths

### Customization
- Modify accuracy thresholds in the code
- Add new data processing tasks
- Customize backup strategies
- Extend reporting capabilities

---

**🎯 This system gives you the automation power of Airflow with the simplicity and reliability of native Windows applications!**
