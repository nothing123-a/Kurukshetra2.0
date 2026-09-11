# Analytics Page User Guide

## Overview
The Analytics page provides a comprehensive data visualization platform where users can upload datasets and create custom charts with X vs Y axis selection capabilities.

## Features

### 1. Data Upload
- **Supported Formats**: CSV, Excel (.xlsx, .xls)
- **File Size Limit**: 16MB maximum
- **Upload Methods**: 
  - Upload new datasets for immediate analysis
  - Use previously uploaded and cleaned datasets from your data cleaning workflow
  - Drag & Drop interface for new files
  - File browser selection

### 2. Dataset Overview
After uploading, the system automatically analyzes your data and displays:
- Total rows and columns
- Number of numeric vs categorical columns
- Missing values count
- Complete column list with data type indicators

### 3. Custom Chart Configuration
Users can create personalized visualizations by selecting:
- **X-Axis**: Choose categorical columns (e.g., categories, names, dates)
- **Y-Axis**: Choose numeric columns (e.g., values, counts, measurements)
- **Chart Type**: Bar, Line, Pie, Doughnut, or Scatter plots
- **Custom Title**: Add descriptive chart titles

### 4. Quick Chart Templates
Pre-built templates for common analysis patterns:
- **Distribution Analysis**: Shows data distribution patterns
- **Correlation Plot**: Reveals relationships between numeric variables
- **Trend Analysis**: Displays trends across categories
- **Composition Chart**: Shows parts of a whole

### 5. Chart Types Available
- **Bar Charts**: Best for comparing categories
- **Line Charts**: Ideal for showing trends over time
- **Pie/Doughnut Charts**: Perfect for showing composition
- **Scatter Plots**: Excellent for correlation analysis

### 6. Export & Download
- **Chart Export**: Download charts as PNG images
- **Data Download**: Export processed data as CSV
- **Chart Summary**: View detailed statistics and insights

## How to Use

### Step 1: Choose Your Data Source
**Option A: Upload New Dataset**
1. Click "Upload New Dataset"
2. Select your CSV or Excel file
3. Click "Upload & Analyze"
4. Wait for the system to process your data

**Option B: Use Existing Data**
1. Click "Use Existing Data"
2. Browse your previously uploaded datasets
3. Select a dataset from your data cleaning workflow
4. Click "Load & Analyze Dataset"
5. The system will load your cleaned data for analysis

### Step 2: Explore Your Data
- Review the dataset overview
- Check column types and missing values
- Identify numeric and categorical columns

### Step 3: Create Custom Charts
1. Select X-Axis (category column)
2. Select Y-Axis (value column)
3. Choose chart type
4. Add custom title (optional)
5. Click "Generate Custom Chart"

### Step 4: Use Quick Templates
- Click any quick chart template button
- The system automatically configures axes and chart type
- Charts are generated instantly

### Step 5: Export Results
- Use the export button on each chart
- Download processed data
- Save charts as images

## Best Practices

### For X-Axis Selection
- **Categorical Data**: Names, categories, dates, groups
- **Limited Values**: Choose columns with fewer unique values for clearer charts
- **Meaningful Order**: Consider logical ordering for better visualization

### For Y-Axis Selection
- **Numeric Data**: Values, counts, percentages, measurements
- **Continuous Variables**: Use for trend and distribution analysis
- **Aggregated Data**: Consider using means, sums, or counts

### Chart Type Selection
- **Bar Charts**: Compare values across categories
- **Line Charts**: Show trends and changes over time
- **Pie Charts**: Display composition and proportions
- **Scatter Plots**: Reveal correlations and patterns

## Troubleshooting

### Common Issues
1. **"No data available"**: Upload a dataset first
2. **"Invalid column names"**: Check that selected columns exist in your data
3. **"Chart generation failed"**: Ensure your data has the required column types
4. **Empty charts**: Check for missing values in selected columns

### Data Requirements
- **Minimum Data**: At least 2 columns with data
- **Numeric Columns**: Required for Y-axis and calculations
- **Categorical Columns**: Best for X-axis grouping
- **Data Quality**: Clean data produces better visualizations

## Benefits of Using Existing Data

### Workflow Integration
- **Seamless Analysis**: Continue analysis on datasets you've already cleaned
- **Data Consistency**: Use the same cleaned data across different analysis sessions
- **Time Savings**: Skip re-uploading and re-processing steps
- **Version Control**: Access your latest cleaned datasets automatically

### Data Quality
- **Pre-cleaned Data**: Work with datasets that have already been processed
- **Missing Value Handling**: Use data that has been cleaned for missing values
- **Outlier Treatment**: Analyze data that has been processed for outliers
- **Standardized Format**: Consistent data structure across sessions

## Technical Notes

### Backend API Endpoints
- `/upload`: File upload and processing
- `/api/analytics/generate`: Auto-generated charts
- `/api/analytics/custom-chart`: Custom chart generation
- `/api/analytics/user-datasets`: Fetch user's existing datasets
- `/api/analytics/load-dataset/<id>`: Load specific dataset for analysis
- `/download_data`: Data export

### Data Processing
- Automatic data type detection
- Missing value handling
- Statistical calculations
- Chart data preparation

### Performance
- Optimized for datasets up to 16MB
- Efficient chart rendering
- Responsive UI design
- Real-time data processing

## Support

For technical support or feature requests, please contact the development team or refer to the main project documentation.
