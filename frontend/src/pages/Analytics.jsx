import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement, ScatterController, PointElement as ScatterPointElement } from 'chart.js';
import { Bar, Line, Pie, Doughnut, Scatter } from 'react-chartjs-2';
import { FiBarChart2, FiTrendingUp, FiPieChart, FiRefreshCw, FiUpload, FiDownload, FiSettings, FiEye, FiEyeOff } from 'react-icons/fi';
import { API_BASE_URL } from '../config.js';
import { toast } from 'react-toastify';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement, 
  PointElement, 
  Title, 
  Tooltip, 
  Legend, 
  ArcElement,
  ScatterController,
  ScatterPointElement
);

const Analytics = () => {
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedChart, setSelectedChart] = useState('bar');
  const [dataSource, setDataSource] = useState('upload'); // 'upload' or 'fetch'
  const [file, setFile] = useState(null);
  const [uploadedData, setUploadedData] = useState(null);
  const [customChartConfig, setCustomChartConfig] = useState({
    xAxis: '',
    yAxis: '',
    chartType: 'bar',
    title: ''
  });
  const [showCustomChart, setShowCustomChart] = useState(false);
  const [availableColumns, setAvailableColumns] = useState([]);
  const [numericColumns, setNumericColumns] = useState([]);
  const [categoricalColumns, setCategoricalColumns] = useState([]);
  const [generatingChart, setGeneratingChart] = useState(false);
  const [userDatasets, setUserDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [loadingDatasets, setLoadingDatasets] = useState(false);

  useEffect(() => {
    if (uploadedData) {
      generateCharts();
    }
  }, [uploadedData]);

  useEffect(() => {
    if (dataSource === 'fetch') {
      fetchUserDatasets();
    }
  }, [dataSource]);

  const handleFileUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        setUploadedData(data);
        setDatasetInfo(data.summary);
        
        // Extract column information
        if (data.summary && data.summary.column_names) {
          const columns = data.summary.column_names;
          setAvailableColumns(columns);
          
          // Separate numeric and categorical columns
          const numeric = [];
          const categorical = [];
          
          columns.forEach((col, index) => {
            const dataType = data.summary.data_types[col];
            if (dataType && (dataType.includes('int') || dataType.includes('float') || dataType.includes('number'))) {
              numeric.push(col);
            } else {
              categorical.push(col);
            }
          });
          
          setNumericColumns(numeric);
          setCategoricalColumns(categorical);
          
          // Set default custom chart config
          if (numeric.length > 0 && categorical.length > 0) {
            setCustomChartConfig(prev => ({
              ...prev,
              xAxis: categorical[0],
              yAxis: numeric[0]
            }));
          }
        }
        
        // Show success message
        toast.success('Dataset uploaded successfully! You can now generate custom charts.');
      } else {
        const errorData = await response.json();
        toast.error(`Upload failed: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('Upload failed. Please check your connection and try again.');
    }
    setLoading(false);
  };

  const generateCharts = async () => {
    if (!uploadedData) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/generate`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCharts(data.charts || []);
      } else {
        const errorData = await response.json();
        console.error('Error generating charts:', errorData.error);
      }
    } catch (error) {
      console.error('Error generating charts:', error);
    }
    setLoading(false);
  };

  const generateCustomChart = async () => {
    if (!customChartConfig.xAxis || !customChartConfig.yAxis) {
      toast.warning('Please select both X and Y axes');
      return;
    }

    if (!uploadedData || !uploadedData.summary) {
      toast.info('No data available. Please upload a dataset first.');
      return;
    }

    setGeneratingChart(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/custom-chart`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          xAxis: customChartConfig.xAxis,
          yAxis: customChartConfig.yAxis,
          chartType: customChartConfig.chartType,
          title: customChartConfig.title
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.chart) {
          setCharts([data.chart]);
          setShowCustomChart(true);
          
          // Update the selected chart type to match the custom chart
          setSelectedChart(data.chart.chartType);
        } else {
          toast.error('Failed to generate custom chart');
        }
      } else {
        const errorData = await response.json();
        toast.error(`Chart generation failed: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error generating custom chart:', error);
      toast.error('Failed to generate custom chart. Please try again.');
    }
    setGeneratingChart(false);
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: { display: true }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  const renderChart = (chartData, type) => {
    const chartConfig = {
      data: {
        labels: chartData.labels,
        datasets: chartData.datasets
      },
      options: { 
        ...chartOptions, 
        plugins: { 
          ...chartOptions.plugins, 
          title: { 
            display: true, 
            text: chartData.title 
          } 
        } 
      } 
    };
    
    switch (type) {
      case 'bar': return <Bar {...chartConfig} />;
      case 'line': return <Line {...chartConfig} />;
      case 'pie': return <Pie {...chartConfig} />;
      case 'doughnut': return <Doughnut {...chartConfig} />;
      case 'scatter': return <Scatter {...chartConfig} />;
      default: return <Bar {...chartConfig} />;
    }
  };

  const downloadData = async () => {
    if (!uploadedData) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/download_data`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics_data_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading data:', error);
      toast.error('Download failed. Please try again.');
    }
  };

  const exportChart = (chartIndex = 0) => {
    if (charts.length === 0) return;
    
    const chart = charts[chartIndex];
    const canvas = document.querySelector(`canvas[data-chart-id="${chartIndex}"]`);
    
    if (canvas) {
      const url = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url;
      a.download = `${chart.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().split('T')[0]}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const generateQuickChart = (template) => {
    if (!uploadedData || !availableColumns.length) return;
    
    let xAxis, yAxis, chartType, title;
    
    switch (template) {
      case 'distribution':
        if (numericColumns.length > 0) {
          xAxis = numericColumns[0];
          yAxis = numericColumns[0];
          chartType = 'bar';
          title = `Distribution of ${xAxis}`;
        }
        break;
      case 'correlation':
        if (numericColumns.length >= 2) {
          xAxis = numericColumns[0];
          yAxis = numericColumns[1];
          chartType = 'scatter';
          title = `${yAxis} vs ${xAxis} Correlation`;
        }
        break;
      case 'trend':
        if (categoricalColumns.length > 0 && numericColumns.length > 0) {
          xAxis = categoricalColumns[0];
          yAxis = numericColumns[0];
          chartType = 'line';
          title = `${yAxis} Trend by ${xAxis}`;
        }
        break;
      case 'composition':
        if (categoricalColumns.length > 0) {
          xAxis = categoricalColumns[0];
          yAxis = categoricalColumns[0];
          chartType = 'pie';
          title = `Composition of ${xAxis}`;
        }
        break;
      default:
        return;
    }
    
    if (xAxis && yAxis) {
      setCustomChartConfig({
        xAxis,
        yAxis,
        chartType,
        title
      });
      // Auto-generate the chart
      setTimeout(() => generateCustomChart(), 100);
    }
  };

  const fetchUserDatasets = async () => {
    setLoadingDatasets(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/user-datasets`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUserDatasets(data.datasets);
        } else {
          console.error('Failed to fetch datasets:', data.error);
          toast.error(`Failed to fetch datasets: ${data.error}`);
        }
      } else {
        console.error('Failed to fetch datasets');
        if (response.status === 401) {
          toast.info('Please log in to access your datasets');
        } else if (response.status === 500) {
          toast.error('Server error. Please try again later.');
        } else {
          toast.error('Failed to fetch datasets. Please check your connection.');
        }
      }
    } catch (error) {
      console.error('Error fetching datasets:', error);
      toast.error('Network error. Please check your connection and try again.');
    }
    setLoadingDatasets(false);
  };

  const loadExistingDataset = async (datasetId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/load-dataset/${datasetId}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUploadedData(data);
          setDatasetInfo(data.summary);
          setSelectedDataset(data.dataset);
          
          // Extract column information
          if (data.summary && data.summary.column_names) {
            const columns = data.summary.column_names;
            setAvailableColumns(columns);
            
            // Separate numeric and categorical columns
            const numeric = [];
            const categorical = [];
            
            columns.forEach((col, index) => {
              const dataType = data.summary.data_types[col];
              if (dataType && (dataType.includes('int') || dataType.includes('float') || dataType.includes('number'))) {
                numeric.push(col);
              } else {
                categorical.push(col);
              }
            });
            
            setNumericColumns(numeric);
            setCategoricalColumns(categorical);
            
            // Set default custom chart config
            if (numeric.length > 0 && categorical.length > 0) {
              setCustomChartConfig(prev => ({
                ...prev,
                xAxis: categorical[0],
                yAxis: numeric[0]
              }));
            }
          }
          
          toast.success(`Dataset "${data.dataset.filename}" loaded successfully! You can now generate charts.`);
        } else {
          toast.error(`Failed to load dataset: ${data.error}`);
        }
      } else {
        const errorData = await response.json();
        toast.error(`Failed to load dataset: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error loading dataset:', error);
      toast.error('Failed to load dataset. Please try again.');
    }
    setLoading(false);
  };

  const clearCurrentDataset = () => {
    setUploadedData(null);
    setDatasetInfo(null);
    setCharts([]);
    setAvailableColumns([]);
    setNumericColumns([]);
    setCategoricalColumns([]);
    setSelectedDataset(null);
    setCustomChartConfig({
      xAxis: '',
      yAxis: '',
      chartType: 'bar',
      title: ''
    });
    setShowCustomChart(false);
  };

  const handleDataSourceChange = (newSource) => {
    if (newSource !== dataSource) {
      clearCurrentDataset();
      setDataSource(newSource);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics Dashboard</h1>
            <p className="text-gray-600 mt-2">Upload new datasets or analyze your previously cleaned data with interactive charts</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={generateCharts}
              disabled={loading || !uploadedData}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <FiRefreshCw className={loading ? 'animate-spin' : ''} />
              {loading ? 'Generating...' : 'Refresh Charts'}
            </button>
            {uploadedData && (
              <button
                onClick={downloadData}
                className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                <FiDownload />
                Download Data
              </button>
            )}
          </div>
        </div>

        {/* Data Source Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FiUpload />
            Data Source & Upload
          </h2>
          
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => handleDataSourceChange('upload')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                dataSource === 'upload' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Upload New Dataset
            </button>
            <button
              onClick={() => handleDataSourceChange('fetch')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                dataSource === 'fetch' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Use Existing Data
            </button>
          </div>
          
          {dataSource === 'upload' && (
            <div className="space-y-4">
              <div className="flex gap-4 items-center">
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleFileUpload}
                  disabled={!file || loading}
                  className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <FiUpload />
                  {loading ? 'Uploading...' : 'Upload & Analyze'}
                </button>
              </div>
              
              <div className="text-sm text-gray-600">
                <p>Supported formats: CSV, Excel (.xlsx, .xls)</p>
                <p>Maximum file size: 16MB</p>
              </div>
            </div>
          )}
          
          {dataSource === 'fetch' && (
            <div className="space-y-4">
              {loadingDatasets ? (
                <div className="flex justify-center items-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Loading your datasets...</span>
                </div>
              ) : userDatasets.length > 0 ? (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div className="text-gray-700">
                      <p className="font-medium mb-2">Select a dataset to analyze:</p>
                      <p className="text-sm text-gray-500">These are datasets you've previously uploaded for data cleaning</p>
                    </div>
                    <button
                      onClick={fetchUserDatasets}
                      disabled={loadingDatasets}
                      className="text-blue-600 hover:text-blue-700 transition-colors flex items-center gap-2 text-sm"
                    >
                      <FiRefreshCw className={loadingDatasets ? 'animate-spin' : ''} />
                      Refresh
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {userDatasets.map((dataset) => (
                      <div
                        key={dataset.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                          selectedDataset && selectedDataset.id === dataset.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedDataset(dataset)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900 truncate" title={dataset.filename}>
                            {dataset.filename}
                          </h4>
                          {selectedDataset && selectedDataset.id === dataset.id && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>Rows: {dataset.rows?.toLocaleString() || 'N/A'}</p>
                          <p>Columns: {dataset.columns || 'N/A'}</p>
                          <p>Uploaded: {dataset.uploaded_at ? new Date(dataset.uploaded_at).toLocaleDateString() : 'N/A'}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {selectedDataset && (
                    <div className="flex gap-3 pt-2">
                      <button
                        onClick={() => loadExistingDataset(selectedDataset.id)}
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                      >
                        {loading ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            Loading...
                          </>
                        ) : (
                          <>
                            <FiEye />
                            Load & Analyze Dataset
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => setSelectedDataset(null)}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                      >
                        Clear Selection
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No datasets found</h3>
                  <p className="text-gray-600 mb-4">
                    You haven't uploaded any datasets yet, or they may have been removed.
                  </p>
                  <button
                    onClick={() => handleDataSourceChange('upload')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Upload Your First Dataset
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Dataset Overview */}
        {datasetInfo && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Dataset Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{datasetInfo.rows}</div>
                <div className="text-sm text-gray-600">Total Rows</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{datasetInfo.columns}</div>
                <div className="text-sm text-gray-600">Total Columns</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{numericColumns.length}</div>
                <div className="text-sm text-gray-600">Numeric Columns</div>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{datasetInfo.missing_values || 0}</div>
                <div className="text-sm text-gray-600">Missing Values</div>
              </div>
            </div>
            
            {availableColumns.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium mb-3">Available Columns</h3>
                <div className="flex flex-wrap gap-2">
                  {availableColumns.map((col, index) => (
                    <span
                      key={index}
                      className={`px-3 py-1 rounded-full text-sm ${
                        numericColumns.includes(col)
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {col} {numericColumns.includes(col) && '(Numeric)'}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Custom Chart Configuration */}
        {uploadedData && availableColumns.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <FiSettings />
              Custom Chart Configuration
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">X-Axis (Category)</label>
                <select
                  value={customChartConfig.xAxis}
                  onChange={(e) => setCustomChartConfig(prev => ({ ...prev, xAxis: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select X-Axis</option>
                  {categoricalColumns.map((col, index) => (
                    <option key={index} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Y-Axis (Value)</label>
                <select
                  value={customChartConfig.yAxis}
                  onChange={(e) => setCustomChartConfig(prev => ({ ...prev, yAxis: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Y-Axis</option>
                  {numericColumns.map((col, index) => (
                    <option key={index} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Chart Type</label>
                <select
                  value={customChartConfig.chartType}
                  onChange={(e) => setCustomChartConfig(prev => ({ ...prev, chartType: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="bar">Bar Chart</option>
                  <option value="line">Line Chart</option>
                  <option value="pie">Pie Chart</option>
                  <option value="doughnut">Doughnut Chart</option>
                  <option value="scatter">Scatter Plot</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Chart Title</label>
                <input
                  type="text"
                  value={customChartConfig.title || ''}
                  onChange={(e) => setCustomChartConfig(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter chart title"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mb-4">
              <button
                onClick={generateCustomChart}
                disabled={!customChartConfig.xAxis || !customChartConfig.yAxis || generatingChart}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                {generatingChart ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <FiEye />
                    Generate Custom Chart
                  </>
                )}
              </button>
              
              {charts.length > 0 && (
                <button
                  onClick={() => exportChart(0)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                >
                  <FiDownload />
                  Export Chart
                </button>
              )}
            </div>

            {/* Quick Chart Templates */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-lg font-medium mb-3">Quick Chart Templates</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => generateQuickChart('distribution')}
                  disabled={numericColumns.length === 0}
                  className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 disabled:opacity-50 transition-colors text-sm"
                >
                  Distribution Analysis
                </button>
                <button
                  onClick={() => generateQuickChart('correlation')}
                  disabled={numericColumns.length < 2}
                  className="px-4 py-2 bg-green-100 text-green-800 rounded-lg hover:bg-green-200 disabled:opacity-50 transition-colors text-sm"
                >
                  Correlation Plot
                </button>
                <button
                  onClick={() => generateQuickChart('trend')}
                  disabled={categoricalColumns.length === 0 || numericColumns.length === 0}
                  className="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 disabled:opacity-50 transition-colors text-sm"
                >
                  Trend Analysis
                </button>
                <button
                  onClick={() => generateQuickChart('composition')}
                  disabled={categoricalColumns.length === 0}
                  className="px-4 py-2 bg-purple-100 text-purple-800 rounded-lg hover:bg-purple-200 disabled:opacity-50 transition-colors text-sm"
                >
                  Composition Chart
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Chart Type Selection */}
        <div className="flex gap-4 mb-6">
          {[
            { type: 'bar', icon: FiBarChart2, label: 'Bar Chart' },
            { type: 'line', icon: FiTrendingUp, label: 'Line Chart' },
            { type: 'pie', icon: FiPieChart, label: 'Pie Chart' },
            { type: 'doughnut', icon: FiPieChart, label: 'Doughnut' },
            { type: 'scatter', icon: FiTrendingUp, label: 'Scatter Plot' }
          ].map(({ type, icon: Icon, label }) => (
            <button
              key={type}
              onClick={() => setSelectedChart(type)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                selectedChart === type 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <Icon />
              {label}
            </button>
          ))}
        </div>

        {/* Charts Display */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Chart Summary */}
            {charts.length > 0 && charts[0].summary && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 className="text-lg font-semibold mb-4">Chart Summary & Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{charts[0].dataPoints}</div>
                    <div className="text-sm text-gray-600">Data Points</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{charts[0].summary.xAxisUnique}</div>
                    <div className="text-sm text-gray-600">Unique X Values</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">{charts[0].summary.yAxisMean.toFixed(2)}</div>
                    <div className="text-sm text-gray-600">Y-Axis Mean</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{charts[0].summary.yAxisStd.toFixed(2)}</div>
                    <div className="text-sm text-gray-600">Y-Axis Std Dev</div>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-700 mb-2">Y-Axis Range</h4>
                    <p className="text-sm text-gray-600">
                      Min: {charts[0].summary.yAxisMin.toFixed(2)} | 
                      Max: {charts[0].summary.yAxisMax.toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-700 mb-2">Chart Configuration</h4>
                    <p className="text-sm text-gray-600">
                      X: {charts[0].xAxis} | Y: {charts[0].yAxis} | Type: {charts[0].chartType}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {charts.map((chart, index) => (
                <div key={index} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">{chart.title}</h3>
                    <button
                      onClick={() => exportChart(index)}
                      className="text-gray-500 hover:text-gray-700 transition-colors"
                      title="Export Chart"
                    >
                      <FiDownload size={18} />
                    </button>
                  </div>
                  <div className="h-80">
                    <div data-chart-id={index}>
                      {renderChart(chart, selectedChart)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* No Data State */}
        {!loading && charts.length === 0 && (
          <div className="text-center py-12">
            <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No charts available</h3>
            <p className="mt-1 text-sm text-gray-500">
              {!uploadedData 
                ? 'Upload a dataset above to start analyzing your data' 
                : 'Click "Generate Custom Chart" or "Refresh Charts" to create visualizations'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;