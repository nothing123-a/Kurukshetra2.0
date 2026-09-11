import { useState, useCallback } from 'react'
import { API_BASE_URL } from '../config.js'
import { 
  FiUpload, FiEye, FiEyeOff, FiDownload, FiShield, 
  FiFileText, FiCheck, FiX, FiLock, FiUnlock 
} from 'react-icons/fi'
import './DataEncryption.css'

export default function DataEncryption() {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [fileData, setFileData] = useState(null)
  const [columns, setColumns] = useState([])
  const [selectedColumns, setSelectedColumns] = useState([])
  const [encryptionMethod, setEncryptionMethod] = useState('aes')
  const [isProcessing, setIsProcessing] = useState(false)
  const [processedFile, setProcessedFile] = useState(null)
  const [error, setError] = useState(null)

  const handleFileUpload = useCallback(async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Please upload a CSV file')
      return
    }

    setUploadedFile(file)
    setError(null)
    setFileData(null)
    setColumns([])
    setSelectedColumns([])
    setProcessedFile(null)

    // First, let's read the file locally to get basic info
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const csvContent = e.target.result
        const lines = csvContent.split('\n')
        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
        
        // Set basic file info
        const basicFileData = {
          rows: lines.length - 1, // Subtract header row
          columns: headers.length,
          column_names: headers,
          file_size: (file.size / 1024 / 1024).toFixed(2)
        }
        
        setFileData(basicFileData)
        setColumns(headers)
        
        // Now upload to backend for processing
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${API_BASE_URL}/upload`, {
          method: 'POST',
          body: formData,
          credentials: 'include'
        })

        if (!response.ok) {
          throw new Error('Failed to upload file to server')
        }

        const serverData = await response.json()
        
        // Update with server data if available
        if (serverData.success && serverData.summary) {
          setFileData({
            rows: serverData.summary.rows || basicFileData.rows,
            columns: serverData.summary.columns || basicFileData.columns,
            column_names: serverData.summary.column_names || basicFileData.column_names,
            file_size: basicFileData.file_size
          })
          setColumns(serverData.summary.column_names || basicFileData.column_names)
        }
        
      } catch (err) {
        setError('Failed to process file: ' + err.message)
        // Keep the basic file info even if server upload fails
        if (!fileData) {
          const basicFileData = {
            rows: 0,
            columns: 0,
            column_names: [],
            file_size: (file.size / 1024 / 1024).toFixed(2)
          }
          setFileData(basicFileData)
        }
      }
    }
    
    reader.readAsText(file)
  }, [fileData])

  const toggleColumnSelection = useCallback((column) => {
    setSelectedColumns(prev => 
      prev.includes(column) 
        ? prev.filter(col => col !== column)
        : [...prev, column]
    )
  }, [])

  const selectAllColumns = useCallback(() => {
    setSelectedColumns([...columns])
  }, [columns])

  const deselectAllColumns = useCallback(() => {
    setSelectedColumns([])
  }, [])

  const processEncryption = useCallback(async () => {
    if (!uploadedFile || selectedColumns.length === 0) {
      setError('Please upload a file and select columns to encrypt')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', uploadedFile)
      formData.append('columns', JSON.stringify(selectedColumns))
      formData.append('method', encryptionMethod)

      const response = await fetch(`${API_BASE_URL}/encrypt-data`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to process encryption')
      }

      const blob = await response.blob()
      setProcessedFile(blob)
    } catch (err) {
      setError('Encryption failed: ' + err.message)
    } finally {
      setIsProcessing(false)
    }
  }, [uploadedFile, selectedColumns, encryptionMethod])

  const downloadEncryptedFile = useCallback(() => {
    if (!processedFile) return

    const url = URL.createObjectURL(processedFile)
    const a = document.createElement('a')
    a.href = url
    a.download = `encrypted_${uploadedFile.name}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [processedFile, uploadedFile])

  return (
    <div className="data-encryption-page">
      <div className="encryption-container">
        {/* Header */}
        <div className="encryption-header">
          <div className="header-content">
            <div className="header-icon">
              <FiShield size={48} />
            </div>
            <h1 className="header-title">Data Encryption Tool</h1>
            <p className="header-subtitle">
              Secure your sensitive data with advanced encryption algorithms
            </p>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="upload-section">
          <h3 className="section-title">
            <FiUpload size={24} />
            Upload CSV File
          </h3>
          <div className="upload-area">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="upload-label">
              <FiUpload size={32} />
              <span>Choose CSV file or drag and drop</span>
              <small>Maximum file size: 10MB</small>
            </label>
          </div>
          {uploadedFile && (
            <div className="file-info">
              <FiFileText size={20} />
              <span>{uploadedFile.name}</span>
              <span className="file-size">
                ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <FiX size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* File Preview */}
        {fileData && (
          <div className="preview-section">
            <h3 className="section-title">
              <FiEye size={24} />
              File Preview
            </h3>
            <div className="preview-stats">
              <div className="stat-item">
                <span className="stat-label">Rows:</span>
                <span className="stat-value">{fileData.rows?.toLocaleString() || '0'}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Columns:</span>
                <span className="stat-value">{fileData.columns || columns.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">File Size:</span>
                <span className="stat-value">
                  {fileData.file_size || (uploadedFile && (uploadedFile.size / 1024 / 1024).toFixed(2))} MB
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Column Selection */}
        {columns.length > 0 && (
          <div className="columns-section">
            <div className="section-header">
              <h3 className="section-title">
                <FiLock size={24} />
                Select Columns to Encrypt
              </h3>
              <div className="selection-actions">
                <button 
                  className="btn btn-outline-primary btn-sm"
                  onClick={selectAllColumns}
                >
                  Select All
                </button>
                <button 
                  className="btn btn-outline-secondary btn-sm"
                  onClick={deselectAllColumns}
                >
                  Deselect All
                </button>
              </div>
            </div>
            
            <div className="columns-grid">
              {columns.map((column) => {
                const isSelected = selectedColumns.includes(column)
                return (
                  <div 
                    key={column}
                    className={`column-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => toggleColumnSelection(column)}
                  >
                    <div className="column-icon">
                      {isSelected ? <FiLock size={16} /> : <FiUnlock size={16} />}
                    </div>
                    <div className="column-name">{column}</div>
                    <div className="selection-indicator">
                      {isSelected && <FiCheck size={16} />}
                    </div>
                  </div>
                )
              })}
            </div>
            
            {selectedColumns.length > 0 && (
              <div className="selection-summary">
                <p className="summary-text">
                  <strong>{selectedColumns.length}</strong> column(s) selected for encryption
                </p>
              </div>
            )}
          </div>
        )}

        {/* Encryption Settings */}
        {selectedColumns.length > 0 && (
          <div className="settings-section">
            <h3 className="section-title">
              <FiShield size={24} />
              Encryption Settings
            </h3>
            <div className="settings-grid">
              <div className="setting-card">
                <label className="setting-label">Encryption Method</label>
                <select 
                  className="setting-select"
                  value={encryptionMethod}
                  onChange={(e) => setEncryptionMethod(e.target.value)}
                >
                  <option value="aes">AES-256 (Recommended)</option>
                  <option value="des">DES</option>
                  <option value="blowfish">Blowfish</option>
                </select>
                <p className="setting-description">
                  Choose the encryption algorithm for your data. AES-256 is the most secure option.
                </p>
              </div>
              
              <div className="setting-card">
                <label className="setting-label">Selected Columns</label>
                <div className="selected-columns">
                  {selectedColumns.map(column => (
                    <span key={column} className="selected-column-tag">
                      {column}
                    </span>
                  ))}
                </div>
                <p className="setting-description">
                  {selectedColumns.length} column(s) will be encrypted. Other columns will remain unchanged.
                </p>
              </div>
            </div>
            
            <div className="encryption-info">
              <div className="info-item">
                <FiShield size={16} />
                <span>Your data will be encrypted using industry-standard algorithms</span>
              </div>
              <div className="info-item">
                <FiDownload size={16} />
                <span>Download the encrypted file immediately after processing</span>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-section">
          {selectedColumns.length > 0 && !processedFile && (
            <button 
              className="btn btn-primary process-button"
              onClick={processEncryption}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <div className="spinner"></div>
                  Processing...
                </>
              ) : (
                <>
                  <FiShield size={20} />
                  Encrypt Data
                </>
              )}
            </button>
          )}
          
          {processedFile && (
            <button 
              className="btn btn-success download-button"
              onClick={downloadEncryptedFile}
            >
              <FiDownload size={20} />
              Download Encrypted File
            </button>
          )}
        </div>

        {/* Success Message */}
        {processedFile && (
          <div className="success-message">
            <FiCheck size={20} />
            <span>Data encrypted successfully! You can now download the secure file.</span>
          </div>
        )}
      </div>
    </div>
  )
}
