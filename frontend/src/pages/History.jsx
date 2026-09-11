import { useState, useEffect } from 'react'
import { API_BASE_URL } from '../config.js'
import { 
  FiClock, FiDownload, FiTrash2, FiFilter, FiSearch, 
  FiFileText, FiShield, FiDatabase, FiBarChart, FiEye,
  FiCalendar, FiUser, FiActivity, FiFile, FiCheckCircle,
  FiAlertCircle, FiPlay, FiPause, FiRefreshCw
} from 'react-icons/fi'
import './History.css'

export default function History() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pagination, setPagination] = useState({})
  const [filters, setFilters] = useState({
    activity_type: '',
    page: 1,
    per_page: 10
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [downloading, setDownloading] = useState({})
  const [deleting, setDeleting] = useState({})

  const activityTypes = [
    { value: '', label: 'All Activities' },
    { value: 'data_cleaning', label: 'Data Cleaning' },
    { value: 'report_generation', label: 'Report Generation' },
    { value: 'data_encryption', label: 'Data Encryption' },
    { value: 'typo_correction', label: 'Typo Correction' }
  ]

  const getActivityIcon = (activityType) => {
    switch (activityType) {
      case 'data_cleaning':
        return <FiDatabase className="activity-icon cleaning" />
      case 'report_generation':
        return <FiBarChart className="activity-icon report" />
      case 'data_encryption':
        return <FiShield className="activity-icon encryption" />
      case 'typo_correction':
        return <FiFileText className="activity-icon typo" />
      default:
        return <FiActivity className="activity-icon default" />
    }
  }

  const getActivityLabel = (activityType) => {
    switch (activityType) {
      case 'data_cleaning':
        return 'Data Cleaning'
      case 'report_generation':
        return 'Report Generation'
      case 'data_encryption':
        return 'Data Encryption'
      case 'typo_correction':
        return 'Typo Correction'
      default:
        return activityType
    }
  }

  const getFileTypeIcon = (activityType, activityDetails) => {
    if (activityType === 'report_generation') {
      const format = activityDetails?.format || 'pdf'
      return format === 'pdf' ? <FiFile className="file-icon pdf" /> : <FiFile className="file-icon html" />
    }
    return <FiFile className="file-icon csv" />
  }

  const getFileTypeLabel = (activityType, activityDetails) => {
    if (activityType === 'report_generation') {
      const format = activityDetails?.format || 'pdf'
      return format.toUpperCase()
    }
    return 'CSV'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    const now = new Date()
    const diffInMs = now - date
    const diffInSeconds = Math.floor(diffInMs / 1000)
    const diffInMinutes = Math.floor(diffInSeconds / 60)
    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)
    const diffInWeeks = Math.floor(diffInDays / 7)
    const diffInMonths = Math.floor(diffInDays / 30)
    const diffInYears = Math.floor(diffInDays / 365)
    
    // Just now (less than 1 minute)
    if (diffInSeconds < 60) {
      return 'Just now'
    }
    // Minutes ago
    else if (diffInMinutes < 60) {
      return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`
    }
    // Hours ago (with minutes precision)
    else if (diffInHours < 24) {
      const remainingMinutes = diffInMinutes % 60
      if (remainingMinutes === 0) {
        return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`
      } else {
        return `${diffInHours}h ${remainingMinutes}m ago`
      }
    }
    // Days ago
    else if (diffInDays < 7) {
      return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`
    }
    // Weeks ago
    else if (diffInWeeks < 4) {
      return `${diffInWeeks} week${diffInWeeks !== 1 ? 's' : ''} ago`
    }
    // Months ago
    else if (diffInMonths < 12) {
      return `${diffInMonths} month${diffInMonths !== 1 ? 's' : ''} ago`
    }
    // Years ago
    else if (diffInYears < 10) {
      return `${diffInYears} year${diffInYears !== 1 ? 's' : ''} ago`
    }
    // Very old - show exact date and time
    else {
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit'
      })
    }
  }

  // Enhanced time display with tooltip showing exact date/time
  const formatDateWithTooltip = (dateString) => {
    if (!dateString) return { display: 'N/A', tooltip: '' }
    
    const date = new Date(dateString)
    const display = formatDate(dateString)
    const tooltip = date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
    
    return { display, tooltip }
  }

  const fetchHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params = new URLSearchParams({
        page: filters.page,
        per_page: filters.per_page,
        ...(filters.activity_type && { activity_type: filters.activity_type })
      })

      const response = await fetch(`${API_BASE_URL}/api/history?${params}`, {
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to fetch history')
      }

      const data = await response.json()
      
      if (data.success) {
        setHistory(data.history)
        setPagination(data.pagination)
      } else {
        throw new Error(data.error || 'Failed to fetch history')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const downloadFile = async (historyId, fileName, fileType = 'file') => {
    try {
      setDownloading(prev => ({ ...prev, [`${historyId}_${fileType}`]: true }))
      
      const response = await fetch(`${API_BASE_URL}/api/history/${historyId}/download`, {
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to download file')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers.get('content-disposition')
      let downloadName = fileName || 'download'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          downloadName = filenameMatch[1].replace(/['"]/g, '')
        }
      }
      
      a.download = downloadName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      // Show success message
      setError(null)
    } catch (err) {
      setError(`Download failed: ${err.message}`)
    } finally {
      setDownloading(prev => ({ ...prev, [`${historyId}_${fileType}`]: false }))
    }
  }

  const deleteHistoryItem = async (historyId) => {
    if (!window.confirm('Are you sure you want to delete this history item? This action cannot be undone.')) {
      return
    }

    try {
      setDeleting(prev => ({ ...prev, [historyId]: true }))
      
      const response = await fetch(`${API_BASE_URL}/api/history/${historyId}`, {
        method: 'DELETE',
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to delete history item')
      }

      const data = await response.json()
      
      if (data.success) {
        // Refresh the history list
        fetchHistory()
        setError(null)
      } else {
        throw new Error(data.error || 'Failed to delete history item')
      }
    } catch (err) {
      setError(`Delete failed: ${err.message}`)
    } finally {
      setDeleting(prev => ({ ...prev, [historyId]: false }))
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filters change
    }))
  }

  const handlePageChange = (page) => {
    setFilters(prev => ({ ...prev, page }))
  }

  const filteredHistory = history.filter(item => {
    if (!searchTerm) return true
    
    const searchLower = searchTerm.toLowerCase()
    return (
      item.file_name?.toLowerCase().includes(searchLower) ||
      item.original_file_name?.toLowerCase().includes(searchLower) ||
      getActivityLabel(item.activity_type).toLowerCase().includes(searchLower)
    )
  })

  useEffect(() => {
    fetchHistory()
  }, [filters])

  // Auto-update time display every minute
  useEffect(() => {
    const interval = setInterval(() => {
      // Force re-render to update time displays
      setHistory(prev => [...prev])
    }, 60000) // Update every minute

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="history-page">
      <div className="history-container">
        {/* Header */}
        <div className="history-header">
          <div className="header-content">
            <div className="header-icon">
              <FiClock size={48} />
            </div>
            <h1 className="header-title">Activity History</h1>
            <p className="header-subtitle">
              Track and manage your data processing activities. Download reports and cleaned datasets anytime.
            </p>
                         <div className="header-stats">
               <div className="stat-item">
                 <FiActivity size={20} />
                 <span>{pagination.total || 0} Total Activities</span>
               </div>
               <div className="stat-item">
                 <FiCheckCircle size={20} />
                 <span>{history.filter(item => item.status === 'completed').length} Completed</span>
               </div>
               <div className="stat-item live-indicator">
                 <FiClock size={20} />
                 <span>Live Time</span>
               </div>
             </div>
          </div>
        </div>

        {/* Download Info Section */}
        <div className="download-info-section">
          <div className="download-info-content">
            <div className="download-info-icon">
              <FiDownload size={32} />
            </div>
            <div className="download-info-text">
              <h3>Download Your Files</h3>
              <p>Click the specific download buttons on any history item to download your processed files:</p>
                             <div className="download-types">
                 <div className="download-type">
                   <FiBarChart size={16} />
                   <span>Download Report</span>
                 </div>
                 <div className="download-type">
                   <FiDatabase size={16} />
                   <span>Download Clean CSV</span>
                 </div>
                 <div className="download-type">
                   <FiShield size={16} />
                   <span>Download Encrypted File</span>
                 </div>
                 <div className="download-type">
                   <FiFileText size={16} />
                   <span>Download Typo Results</span>
                 </div>
                 <div className="download-type">
                   <FiDownload size={16} />
                   <span>Universal Download</span>
                 </div>
               </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="filters-section">
          <div className="filters-row">
            <div className="search-box">
              <FiSearch size={20} />
              <input
                type="text"
                placeholder="Search files and activities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            
            <div className="filter-controls">
              <div className="filter-group">
                <FiFilter size={16} />
                <select
                  value={filters.activity_type || ''}
                  onChange={(e) => handleFilterChange('activity_type', e.target.value)}
                  className="filter-select"
                >
                  {activityTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <select
                  value={filters.per_page || 10}
                  onChange={(e) => handleFilterChange('per_page', parseInt(e.target.value))}
                  className="filter-select"
                >
                  <option value={5}>5 per page</option>
                  <option value={10}>10 per page</option>
                  <option value={20}>20 per page</option>
                  <option value={50}>50 per page</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <FiAlertCircle size={20} />
            <span>{error}</span>
            <button 
              className="error-close"
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        )}

        {/* History List */}
        <div className="history-list">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading your activity history...</p>
            </div>
          ) : filteredHistory.length === 0 ? (
            <div className="empty-state">
              <FiClock size={64} />
              <h3>No activities found</h3>
              <p>Start processing your data to see your activity history here.</p>
              <div className="empty-actions">
                <button className="btn btn-primary" onClick={() => window.location.href = '/data-cleaning'}>
                  <FiDatabase size={16} />
                  Start Data Cleaning
                </button>
                <button className="btn btn-outline-primary" onClick={() => window.location.href = '/analytics'}>
                  <FiBarChart size={16} />
                  Generate Report
                </button>
              </div>
            </div>
          ) : (
            <>
              {filteredHistory.map((item) => (
                <div key={item.id} className="history-item">
                  <div className="item-header">
                    <div className="activity-info">
                      {getActivityIcon(item.activity_type)}
                      <div className="activity-details">
                        <h4 className="activity-title">
                          {getActivityLabel(item.activity_type)}
                        </h4>
                        <p className="activity-file">
                          {item.file_name || item.original_file_name || 'No file name'}
                        </p>
                        <div className="file-type-badge">
                          {getFileTypeIcon(item.activity_type, item.activity_details)}
                          <span>{getFileTypeLabel(item.activity_type, item.activity_details)}</span>
                        </div>
                      </div>
                    </div>
                    
                                         <div className="item-actions">
                       {/* Download Buttons - Always Show */}
                       <>
                         {/* Data Cleaning - Download CSV */}
                         {item.activity_type === 'data_cleaning' && (
                           <button
                             className={`btn btn-success download-btn ${downloading[`${item.id}_csv`] ? 'loading' : ''}`}
                             onClick={() => downloadFile(item.id, item.file_name, 'csv')}
                             title="Download cleaned CSV file"
                             disabled={downloading[`${item.id}_csv`]}
                           >
                             {downloading[`${item.id}_csv`] ? (
                               <FiRefreshCw size={16} className="spinning" />
                             ) : (
                               <FiDatabase size={16} />
                             )}
                             {downloading[`${item.id}_csv`] ? 'Downloading...' : 'Download CSV'}
                           </button>
                         )}
                         
                         {/* Report Generation - Download Report */}
                         {item.activity_type === 'report_generation' && (
                           <button
                             className={`btn btn-info download-btn ${downloading[`${item.id}_report`] ? 'loading' : ''}`}
                             onClick={() => downloadFile(item.id, item.file_name, 'report')}
                             title="Download report"
                             disabled={downloading[`${item.id}_report`]}
                           >
                             {downloading[`${item.id}_report`] ? (
                               <FiRefreshCw size={16} className="spinning" />
                             ) : (
                               <FiBarChart size={16} />
                             )}
                             {downloading[`${item.id}_report`] ? 'Downloading...' : 'Download Report'}
                           </button>
                         )}
                         
                         {/* Data Encryption - Download Encrypted */}
                         {item.activity_type === 'data_encryption' && (
                           <button
                             className={`btn btn-warning download-btn ${downloading[`${item.id}_encrypted`] ? 'loading' : ''}`}
                             onClick={() => downloadFile(item.id, item.file_name, 'encrypted')}
                             title="Download encrypted file"
                             disabled={downloading[`${item.id}_encrypted`]}
                           >
                             {downloading[`${item.id}_encrypted`] ? (
                               <FiRefreshCw size={16} className="spinning" />
                             ) : (
                               <FiShield size={16} />
                             )}
                             {downloading[`${item.id}_encrypted`] ? 'Downloading...' : 'Download Encrypted'}
                           </button>
                         )}
                         
                         {/* Typo Correction - Download Results */}
                         {item.activity_type === 'typo_correction' && (
                           <button
                             className={`btn btn-primary download-btn ${downloading[`${item.id}_typo`] ? 'loading' : ''}`}
                             onClick={() => downloadFile(item.id, item.file_name, 'typo')}
                             title="Download typo correction results"
                             disabled={downloading[`${item.id}_typo`]}
                           >
                             {downloading[`${item.id}_typo`] ? (
                               <FiRefreshCw size={16} className="spinning" />
                             ) : (
                               <FiFileText size={16} />
                             )}
                             {downloading[`${item.id}_typo`] ? 'Downloading...' : 'Download Results'}
                           </button>
                         )}
                       </>
                       
                                               {/* Download Clean CSV Button - Show for data cleaning and other CSV activities */}
                        {(item.activity_type === 'data_cleaning' || 
                          item.activity_type === 'data_encryption' || 
                          item.activity_type === 'typo_correction') && (
                          <button
                            className={`btn btn-success download-btn ${downloading[`${item.id}_clean_csv`] ? 'loading' : ''}`}
                            onClick={() => downloadFile(item.id, item.file_name, 'clean_csv')}
                            title="Download clean CSV file"
                            disabled={downloading[`${item.id}_clean_csv`]}
                          >
                            {downloading[`${item.id}_clean_csv`] ? (
                              <FiRefreshCw size={16} className="spinning" />
                            ) : (
                              <FiDatabase size={16} />
                            )}
                            {downloading[`${item.id}_clean_csv`] ? 'Downloading...' : 'Download Clean CSV'}
                          </button>
                        )}
                        
                        {/* Universal Download Button - Always Show */}
                        <button
                          className={`btn btn-primary download-btn ${downloading[`${item.id}_universal`] ? 'loading' : ''}`}
                          onClick={() => downloadFile(item.id, item.file_name, 'universal')}
                          title="Download file"
                          disabled={downloading[`${item.id}_universal`]}
                        >
                          {downloading[`${item.id}_universal`] ? (
                            <FiRefreshCw size={16} className="spinning" />
                          ) : (
                            <FiDownload size={16} />
                          )}
                          {downloading[`${item.id}_universal`] ? 'Downloading...' : 'Download'}
                        </button>
                       
                       {/* Delete Button */}
                       <button
                         className={`btn btn-outline-danger btn-sm ${deleting[item.id] ? 'loading' : ''}`}
                         onClick={() => deleteHistoryItem(item.id)}
                         title="Delete history item"
                         disabled={deleting[item.id]}
                       >
                         {deleting[item.id] ? (
                           <FiRefreshCw size={16} className="spinning" />
                         ) : (
                           <FiTrash2 size={16} />
                         )}
                       </button>
                     </div>
                  </div>
                  
                  <div className="item-details">
                                         <div className="detail-row">
                       <div className="detail-item">
                         <FiCalendar size={14} />
                         <span 
                           title={formatDateWithTooltip(item.created_at).tooltip}
                           className="time-display"
                         >
                           {formatDateWithTooltip(item.created_at).display}
                         </span>
                       </div>
                      <div className="detail-item">
                        <FiUser size={14} />
                        <span className={`status-badge ${item.status}`}>
                          {item.status === 'completed' && <FiCheckCircle size={12} />}
                          {item.status === 'failed' && <FiAlertCircle size={12} />}
                          {item.status === 'processing' && <FiPlay size={12} />}
                          {item.status}
                        </span>
                      </div>
                    </div>
                    
                    {item.activity_details && (
                      <div className="activity-summary">
                        {item.activity_type === 'data_cleaning' && (
                          <div className="summary-item">
                            <span className="summary-badge">
                              <FiDatabase size={12} />
                              Columns: {item.activity_details.cleaning_log?.length || 0}
                            </span>
                            {item.activity_details.plots_count && (
                              <span className="summary-badge">
                                <FiBarChart size={12} />
                                Plots: {item.activity_details.plots_count}
                              </span>
                            )}
                            {item.activity_details.rows_processed && (
                              <span className="summary-badge">
                                <FiFile size={12} />
                                Rows: {item.activity_details.rows_processed}
                              </span>
                            )}
                          </div>
                        )}
                        {item.activity_type === 'data_encryption' && (
                          <div className="summary-item">
                            <span className="summary-badge">
                              <FiShield size={12} />
                              Method: {item.activity_details.method}
                            </span>
                            <span className="summary-badge">
                              <FiDatabase size={12} />
                              Columns: {item.activity_details.columns_encrypted?.length || 0}
                            </span>
                            {item.activity_details.rows_processed && (
                              <span className="summary-badge">
                                <FiFile size={12} />
                                Rows: {item.activity_details.rows_processed}
                              </span>
                            )}
                          </div>
                        )}
                        {item.activity_type === 'report_generation' && (
                          <div className="summary-item">
                            <span className="summary-badge">
                              <FiFileText size={12} />
                              Format: {item.activity_details.format?.toUpperCase() || 'PDF'}
                            </span>
                            {item.activity_details.sections && (
                              <span className="summary-badge">
                                <FiBarChart size={12} />
                                Sections: {item.activity_details.sections}
                              </span>
                            )}
                          </div>
                        )}
                        {item.activity_type === 'typo_correction' && (
                          <div className="summary-item">
                            {item.activity_details.corrected_count && (
                              <span className="summary-badge">
                                <FiCheckCircle size={12} />
                                Corrected: {item.activity_details.corrected_count}
                              </span>
                            )}
                            {item.activity_details.total_words && (
                              <span className="summary-badge">
                                <FiFileText size={12} />
                                Total: {item.activity_details.total_words}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>

        {/* Pagination */}
        {pagination && pagination.pages > 1 && (
          <div className="pagination-section">
            <div className="pagination-info">
              Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
              {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
              {pagination.total} items
            </div>
            
            <div className="pagination-controls">
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={!pagination.has_prev}
              >
                Previous
              </button>
              
              <div className="page-numbers">
                {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                  const pageNum = i + 1
                  return (
                    <button
                      key={pageNum}
                      className={`btn btn-sm ${pageNum === pagination.page ? 'btn-primary' : 'btn-outline-secondary'}`}
                      onClick={() => handlePageChange(pageNum)}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>
              
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={!pagination.has_next}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}