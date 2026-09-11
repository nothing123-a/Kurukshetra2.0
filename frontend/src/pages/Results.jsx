import { useCallback, useState } from 'react'
import { useWorkflow } from '../hooks/useWorkflow.js'
import { API_BASE_URL } from '../config.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import WorkflowSteps from '../components/WorkflowSteps.jsx'

export default function Results() {
  const { 
    summary, 
    config, 
    datasetId, 
    results, 
    setResults, 
    notify 
  } = useWorkflow()
  const [busy, setBusy] = useState(false)

  const startProcessing = useCallback(async () => {
    setBusy(true)
    setResults(null)
    const payload = {
      config: {
        imputation: { 
          method: config.imputation.method, 
          columns: config.imputation.columns.length ? config.imputation.columns : null 
        },
        outliers: { 
          detection_method: config.outliers.detection_method, 
          handling_method: config.outliers.handling_method, 
          columns: config.outliers.columns.length ? config.outliers.columns : null 
        },
        weights: { 
          column: config.weights.column || null 
        },
        estimate_columns: config.estimate_columns.length ? config.estimate_columns : null
      }
    }
    if (datasetId) payload.dataset_id = datasetId
    
    try {
      const res = await fetch(`${API_BASE_URL}/clean`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify(payload), 
        credentials: 'include' 
      })
      const data = await res.json()
      if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`)
      setResults(data)
      notify('success', 'Processing completed successfully')
    } catch (e) {
      notify('error', `Processing failed: ${e.message}`)
    } finally {
      setBusy(false)
    }
  }, [config, datasetId, setResults, notify])

  const generateReport = useCallback(async (format) => {
    try {
      const res = await fetch(`${API_BASE_URL}/report`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ dataset_id: datasetId, format }), 
        credentials: 'include' 
      })
      
      if (format === 'pdf') {
        if (!res.ok) {
          const errorText = await res.text()
          throw new Error(errorText || `HTTP ${res.status}`)
        }
        
        const contentType = res.headers.get('content-type') || ''
        if (!contentType.includes('application/pdf')) {
          console.warn('Expected PDF but got:', contentType)
        }
        
        const blob = await res.blob()
        if (blob.size === 0) {
          throw new Error('Received empty PDF file')
        }
        
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `bhishma_dataset_report_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        notify('success', 'PDF report downloaded successfully')
      } else {
        const data = await res.json()
        if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`)
        const w = window.open()
        w.document.write(data.html_content)
        w.document.close()
      }
    } catch (e) {
      console.error('Report generation error:', e)
      notify('error', `Report failed: ${e.message}`)
    }
  }, [notify, datasetId])

  const downloadData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/download_data`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ dataset_id: datasetId }), 
        credentials: 'include' 
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `processed_data_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.csv`
      a.click()
      notify('success', 'Processed data downloaded successfully')
    } catch (e) {
      notify('error', `Download failed: ${e.message}`)
    }
  }, [notify, datasetId])

  return (
    <WorkflowLayout>
      <div className="results-page" style={{ 
        padding: '20px',
        minHeight: '100vh',
        background: '#f8f9fa'
      }}>
        {/* Navigation Steps */}
        <WorkflowSteps />
        
        <div className="container-fluid">
          <div className="main-container" style={{
            background: 'rgba(255,255,255,.95)', 
            borderRadius: 20, 
            margin: 20, 
            padding: 30, 
            boxShadow: '0 20px 40px rgba(0,0,0,.1)'
          }}>
            {/* Header */}
            <div className="header position-relative" style={{
              textAlign: 'center', 
              marginBottom: 40, 
              padding: 20, 
              background: 'linear-gradient(135deg,#2c3e50,#3498db)', 
              color: '#fff', 
              borderRadius: 15
            }}>
              <h1><i className="fas fa-file-alt"></i> Results & Reports</h1>
              <p>View processing results and generate reports</p>
            </div>

            {/* Processing Status */}
            {!results && (
              <div className="processing-section" style={{
                background: '#fff', 
                borderRadius: 15, 
                padding: 25, 
                marginBottom: 25, 
                boxShadow: '0 10px 30px rgba(0,0,0,.1)', 
                borderLeft: '5px solid #3498db'
              }}>
                <h3 style={{ marginBottom: '20px', color: '#2c3e50' }}>
                  <i className="fas fa-cogs me-2"></i> Start Processing
                </h3>
                <p className="text-muted mb-4">
                  Click the button below to start processing your data with the configured settings.
                </p>
                <div className="text-center">
                  <button 
                    className="btn btn-primary btn-lg" 
                    onClick={startProcessing} 
                    disabled={busy || !summary}
                  >
                    <i className="fas fa-play me-2"></i>
                    {busy ? 'Processing...' : 'Start Processing'}
                  </button>
                  {!summary && (
                    <p className="text-warning mt-2">
                      <i className="fas fa-exclamation-triangle me-1"></i>
                      Please upload data first to start processing
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Results Display */}
            {results && (
              <>
                {/* Processing Log */}
                {results.cleaning_log && results.cleaning_log.length > 0 && (
                  <div className="results-section" style={{
                    background: '#fff', 
                    borderRadius: 15, 
                    padding: 25, 
                    marginBottom: 25, 
                    boxShadow: '0 10px 30px rgba(0,0,0,.1)', 
                    borderLeft: '5px solid #27ae60'
                  }}>
                    <h3 style={{ marginBottom: '20px', color: '#2c3e50' }}>
                      <i className="fas fa-check-circle me-2"></i> Processing Log
                    </h3>
                    <ul className="list-unstyled">
                      {results.cleaning_log.map((log, idx) => (
                        <li key={idx} className="mb-2">
                          <i className="fas fa-check text-success me-2"></i>{log}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Statistical Estimates */}
                {results.estimates && Object.keys(results.estimates).length > 0 && (
                  <div className="estimates-section" style={{
                    background: '#fff', 
                    borderRadius: 15, 
                    padding: 25, 
                    marginBottom: 25, 
                    boxShadow: '0 10px 30px rgba(0,0,0,.1)'
                  }}>
                    <h3 style={{ marginBottom: '20px', color: '#2c3e50' }}>
                      <i className="fas fa-chart-line me-2"></i> Statistical Estimates
                    </h3>
                    <div className="row">
                      {Object.entries(results.estimates).map(([column, stats]) => {
                        const data = stats.weighted || stats.unweighted || stats;
                        return (
                          <div key={column} className="col-md-6 mb-3">
                            <div className="card">
                              <div className="card-header">
                                <h6 className="mb-0">{column}</h6>
                              </div>
                              <div className="card-body">
                                <div className="row">
                                  <div className="col-6">
                                    <small className="text-muted">Mean</small>
                                    <div className="fw-bold">{data?.mean?.toFixed(2) || 'N/A'}</div>
                                  </div>
                                  <div className="col-6">
                                    <small className="text-muted">Std Dev</small>
                                    <div className="fw-bold">{data?.std?.toFixed(2) || 'N/A'}</div>
                                  </div>
                                </div>
                                <div className="row mt-2">
                                  <div className="col-6">
                                    <small className="text-muted">SE</small>
                                    <div className="fw-bold">{data?.se?.toFixed(4) || 'N/A'}</div>
                                  </div>
                                  <div className="col-6">
                                    <small className="text-muted">95% CI</small>
                                    <div className="fw-bold" style={{fontSize: '0.8rem'}}>
                                      [{data?.ci_95_lower?.toFixed(2) || 'N/A'}, {data?.ci_95_upper?.toFixed(2) || 'N/A'}]
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Next Steps Navigation */}
                <div className="next-steps-section" style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                  borderRadius: 15, 
                  padding: 25, 
                  marginBottom: 25, 
                  boxShadow: '0 10px 30px rgba(0,0,0,.1)',
                  color: 'white'
                }}>
                  <h3 style={{ marginBottom: '20px', color: 'white' }}>
                    <i className="fas fa-route me-2"></i> Choose Your Next Step
                  </h3>
                  <p style={{ marginBottom: '20px', opacity: 0.9 }}>
                    Data processing completed successfully! What would you like to do next?
                  </p>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="card text-center" style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)' }}>
                        <div className="card-body">
                          <i className="fas fa-chart-line" style={{ fontSize: '2rem', color: '#fff', marginBottom: '10px' }}></i>
                          <h5 style={{ color: 'white' }}>Data Analysis</h5>
                          <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.9rem' }}>Explore interactive charts and detailed analytics</p>
                          <button 
                            className="btn btn-light" 
                            onClick={() => window.location.href = '/analytics'}
                          >
                            <i className="fas fa-analytics me-2"></i>Go to Analytics
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="card text-center" style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)' }}>
                        <div className="card-body">
                          <i className="fas fa-file-alt" style={{ fontSize: '2rem', color: '#fff', marginBottom: '10px' }}></i>
                          <h5 style={{ color: 'white' }}>Generate Reports</h5>
                          <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.9rem' }}>Create comprehensive PDF/HTML reports</p>
                          <button 
                            className="btn btn-light" 
                            onClick={() => document.querySelector('.reports-section').scrollIntoView({ behavior: 'smooth' })}
                          >
                            <i className="fas fa-file-download me-2"></i>Create Reports
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Report Generation */}
                <div className="reports-section" style={{
                  background: '#fff', 
                  borderRadius: 15, 
                  padding: 25, 
                  marginBottom: 25, 
                  boxShadow: '0 10px 30px rgba(0,0,0,.1)'
                }}>
                  <h3 style={{ marginBottom: '20px', color: '#2c3e50' }}>
                    <i className="fas fa-file-alt me-2"></i> Generate Reports
                  </h3>
                  <p className="text-muted mb-4">
                    Generate comprehensive reports with encrypted data samples, AI analysis, and visualizations.
                  </p>
                  <div className="row">
                    <div className="col-md-4">
                      <div className="card text-center">
                        <div className="card-body">
                          <i className="fas fa-file-pdf" style={{ fontSize: '2rem', color: '#e74c3c', marginBottom: '10px' }}></i>
                          <h5>PDF Report</h5>
                          <p className="text-muted">Download a comprehensive PDF report</p>
                          <button 
                            className="btn btn-outline-danger" 
                            onClick={() => generateReport('pdf')}
                          >
                            <i className="fas fa-download me-2"></i>Download PDF
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="card text-center">
                        <div className="card-body">
                          <i className="fas fa-file-code" style={{ fontSize: '2rem', color: '#3498db', marginBottom: '10px' }}></i>
                          <h5>HTML Report</h5>
                          <p className="text-muted">View interactive HTML report</p>
                          <button 
                            className="btn btn-outline-primary" 
                            onClick={() => generateReport('html')}
                          >
                            <i className="fas fa-eye me-2"></i>View HTML
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="card text-center">
                        <div className="card-body">
                          <i className="fas fa-download" style={{ fontSize: '2rem', color: '#27ae60', marginBottom: '10px' }}></i>
                          <h5>Processed Data</h5>
                          <p className="text-muted">Download cleaned dataset</p>
                          <button 
                            className="btn btn-outline-success" 
                            onClick={downloadData}
                          >
                            <i className="fas fa-download me-2"></i>Download CSV
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Summary Stats */}
            {summary && (
              <div className="summary-stats" style={{
                background: '#fff', 
                borderRadius: 15, 
                padding: 25, 
                boxShadow: '0 10px 30px rgba(0,0,0,.1)'
              }}>
                <h3 style={{ marginBottom: '20px', color: '#2c3e50' }}>
                  <i className="fas fa-info-circle me-2"></i> Dataset Summary
                </h3>
                <div className="row">
                  <div className="col-md-3">
                    <div className="text-center">
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3498db' }}>
                        {summary.rows?.toLocaleString() || 0}
                      </div>
                      <div className="text-muted">Total Records</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="text-center">
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#27ae60' }}>
                        {summary.column_names?.length || summary.columns || 0}
                      </div>
                      <div className="text-muted">Variables</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="text-center">
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f39c12' }}>
                        {summary.missing_values?.length || 0}
                      </div>
                      <div className="text-muted">Missing Data Columns</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="text-center">
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#e74c3c' }}>
                        {results ? '✓' : '⏳'}
                      </div>
                      <div className="text-muted">Processing Status</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </WorkflowLayout>
  )
}
