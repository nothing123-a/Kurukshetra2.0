import { useState, useEffect } from 'react'
import { FiShield, FiEye, FiEyeOff, FiSettings, FiPlay, FiCheckCircle, FiLock, FiUpload, FiDatabase } from 'react-icons/fi'
import { API_BASE_URL } from '../config'

export default function PrivacyProtection() {
  const [config, setConfig] = useState({
    protection_level: 'medium',
    custom_pii_columns: {
      email: [],
      phone: [],
      name: [],
      address: [],
      ssn: [],
      credit_card: []
    }
  })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [dataColumns, setDataColumns] = useState([])
  const [dataPreview, setDataPreview] = useState(null)
  const [uploadLoading, setUploadLoading] = useState(false)

  const protectionLevels = [
    { 
      key: 'low', 
      label: 'Basic Protection', 
      desc: 'Simple masking of detected PII',
      color: 'yellow'
    },
    { 
      key: 'medium', 
      label: 'Standard Protection', 
      desc: 'Hash anonymization + light differential privacy',
      color: 'blue'
    },
    { 
      key: 'high', 
      label: 'Maximum Protection', 
      desc: 'Full anonymization + strong differential privacy + k-anonymity',
      color: 'red'
    }
  ]

  const piiTypes = [
    { key: 'email', label: 'Email Addresses', icon: '📧' },
    { key: 'phone', label: 'Phone Numbers', icon: '📱' },
    { key: 'name', label: 'Personal Names', icon: '👤' },
    { key: 'address', label: 'Addresses', icon: '🏠' },
    { key: 'ssn', label: 'Social Security Numbers', icon: '🆔' },
    { key: 'credit_card', label: 'Credit Card Numbers', icon: '💳' }
  ]

  const handleProtect = async () => {
    if (!uploadedFile) {
      setError('Please upload a dataset first')
      return
    }
    
    if (!dataColumns.length) {
      setError('No data columns available. Please re-upload your file.')
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/privacy-protection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ config })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setResults(data)
      } else {
        setError(data.error || 'Privacy protection failed')
      }
    } catch (err) {
      setError('Network error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handlePiiColumnChange = (piiType, columnName) => {
    setConfig(prev => ({
      ...prev,
      custom_pii_columns: {
        ...prev.custom_pii_columns,
        [piiType]: columnName ? [columnName] : []
      }
    }))
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setUploadLoading(true)
    setError('')
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setUploadedFile(file)
        setDataColumns(data.summary.column_names || [])
        setDataPreview({
          rows: data.summary.rows,
          columns: data.summary.columns,
          data_types: data.summary.data_types
        })
        
        autoDetectPIIColumns(data.summary.column_names || [])
      } else {
        setError(data.error || 'File upload failed')
      }
    } catch (err) {
      setError('Network error during file upload')
    } finally {
      setUploadLoading(false)
    }
  }

  const autoDetectPIIColumns = (columns) => {
    const detectedPII = {
      email: [],
      phone: [],
      name: [],
      address: [],
      ssn: [],
      credit_card: []
    }

    columns.forEach(col => {
      const colLower = col.toLowerCase()
      
      if (colLower.includes('email') || colLower.includes('mail')) {
        detectedPII.email.push(col)
      }
      else if (colLower.includes('phone') || colLower.includes('mobile') || colLower.includes('tel')) {
        detectedPII.phone.push(col)
      }
      else if (colLower.includes('name') || colLower.includes('first') || colLower.includes('last')) {
        detectedPII.name.push(col)
      }
      else if (colLower.includes('address') || colLower.includes('street') || colLower.includes('city')) {
        detectedPII.address.push(col)
      }
      else if (colLower.includes('ssn') || colLower.includes('social')) {
        detectedPII.ssn.push(col)
      }
      else if (colLower.includes('card') || colLower.includes('credit')) {
        detectedPII.credit_card.push(col)
      }
    })

    setConfig(prev => ({
      ...prev,
      custom_pii_columns: {
        email: detectedPII.email.slice(0, 1),
        phone: detectedPII.phone.slice(0, 1),
        name: detectedPII.name.slice(0, 1),
        address: detectedPII.address.slice(0, 1),
        ssn: detectedPII.ssn.slice(0, 1),
        credit_card: detectedPII.credit_card.slice(0, 1)
      }
    }))
  }

  const getProtectionLevelColor = (level) => {
    const colors = {
      low: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      medium: 'bg-blue-50 border-blue-200 text-blue-800',
      high: 'bg-red-50 border-red-200 text-red-800'
    }
    return colors[level] || colors.medium
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl p-8 mb-8 text-white">
          <div className="flex items-center gap-4 mb-4">
            <FiShield className="text-4xl" />
            <h1 className="text-4xl font-bold">Privacy Protection</h1>
          </div>
          <p className="text-xl opacity-90">
            Enterprise-grade privacy protection with PII detection and anonymization
          </p>
        </div>

        {/* File Upload Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
            <FiUpload className="text-red-600" />
            Upload Dataset for Privacy Protection
          </h2>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-red-400 transition-colors duration-200">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              className="hidden"
              id="privacy-file-upload"
              disabled={uploadLoading}
            />
            <label htmlFor="privacy-file-upload" className="cursor-pointer">
              <FiUpload className="mx-auto text-4xl text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                {uploadLoading ? 'Uploading...' : 'Upload your dataset'}
              </p>
              <p className="text-sm text-gray-500">
                Supports CSV, Excel (.xlsx, .xls) files
              </p>
            </label>
          </div>
          
          {uploadedFile && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 text-green-800">
                <FiCheckCircle />
                <span className="font-medium">File uploaded: {uploadedFile.name}</span>
              </div>
              {dataPreview && (
                <div className="mt-2 text-sm text-green-700">
                  Dataset: {dataPreview.rows.toLocaleString()} rows × {dataPreview.columns} columns
                </div>
              )}
            </div>
          )}
        </div>

        {/* Configuration Panel */}
        {dataColumns.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
              <FiSettings className="text-red-600" />
              Privacy Configuration
            </h2>
          
          {/* Protection Level */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Protection Level</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {protectionLevels.map((level) => (
                <div
                  key={level.key}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                    config.protection_level === level.key
                      ? getProtectionLevelColor(level.key)
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setConfig(prev => ({ ...prev, protection_level: level.key }))}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <input
                      type="radio"
                      name="protection_level"
                      checked={config.protection_level === level.key}
                      onChange={() => {}}
                      className="w-4 h-4"
                    />
                    <h4 className="font-semibold">{level.label}</h4>
                  </div>
                  <p className="text-sm opacity-80">{level.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Custom PII Columns */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Custom PII Column Mapping</h3>
            <p className="text-sm text-gray-600 mb-4">
              Specify column names that contain specific types of PII data (optional - auto-detection will be used if not specified)
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {piiTypes.map((piiType) => (
                <div key={piiType.key} className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg">
                  <span className="text-2xl">{piiType.icon}</span>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {piiType.label}
                    </label>
                    <select
                      value={config.custom_pii_columns[piiType.key][0] || ''}
                      onChange={(e) => handlePiiColumnChange(piiType.key, e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    >
                      <option value="">Select column (auto-detect if empty)</option>
                      {dataColumns.map((col) => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                    {config.custom_pii_columns[piiType.key][0] && (
                      <div className="mt-1 text-xs text-green-600">
                        ✓ Selected: {config.custom_pii_columns[piiType.key][0]}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          </div>
        )}

        {/* Data Preview Section */}
        {dataPreview && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
              <FiDatabase className="text-red-600" />
              Dataset Preview
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-1">Total Rows</h4>
                <p className="text-2xl font-bold text-blue-700">{dataPreview.rows.toLocaleString()}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-1">Total Columns</h4>
                <p className="text-2xl font-bold text-green-700">{dataPreview.columns}</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-semibold text-purple-900 mb-1">PII Detected</h4>
                <p className="text-2xl font-bold text-purple-700">
                  {Object.values(config.custom_pii_columns).filter(arr => arr.length > 0).length}
                </p>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">Available Columns</h4>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {dataColumns.map((col) => {
                  const isPII = Object.values(config.custom_pii_columns).some(arr => arr.includes(col))
                  return (
                    <span
                      key={col}
                      className={`px-3 py-1 text-sm rounded-full ${
                        isPII 
                          ? 'bg-red-100 text-red-800 border border-red-200' 
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {isPII && '🔒 '}{col}
                    </span>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* Action Button */}
        {dataColumns.length > 0 && (
          <div className="text-center mb-6">
            <button
              onClick={handleProtect}
              disabled={loading || !uploadedFile}
              className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl font-semibold text-lg hover:shadow-lg transition-all duration-200 disabled:opacity-50 mx-auto"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Protecting...
                </>
              ) : (
                <>
                  <FiPlay />
                  Apply Privacy Protection
                </>
              )}
            </button>
            <p className="text-sm text-gray-600 mt-2">
              {Object.values(config.custom_pii_columns).filter(arr => arr.length > 0).length} PII columns selected for protection
            </p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Instructions for new users */}
        {!uploadedFile && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
            <FiShield className="mx-auto text-4xl text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold text-blue-900 mb-2">
              Get Started with Privacy Protection
            </h3>
            <p className="text-blue-700 mb-4">
              Upload your dataset to automatically detect PII columns and apply enterprise-grade privacy protection.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-white rounded-lg p-4">
                <div className="text-2xl mb-2">📤</div>
                <div className="font-semibold">1. Upload Data</div>
                <div className="text-gray-600">CSV or Excel files</div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-2xl mb-2">🔍</div>
                <div className="font-semibold">2. Auto-Detect PII</div>
                <div className="text-gray-600">AI identifies sensitive columns</div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-2xl mb-2">🛡️</div>
                <div className="font-semibold">3. Apply Protection</div>
                <div className="text-gray-600">Anonymize & secure data</div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
              <FiCheckCircle className="text-green-600" />
              Privacy Protection Results
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-red-50 rounded-lg p-4">
                <h4 className="font-semibold text-red-900 mb-2">Protection Level</h4>
                <p className="text-red-700 capitalize">{results.protection_level}</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2">Data Shape</h4>
                <p className="text-blue-700">
                  {results.data_shape.rows.toLocaleString()} rows × {results.data_shape.columns} columns
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">Privacy Protection Log</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {results.privacy_log.map((log, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <FiLock className="text-red-500 flex-shrink-0" />
                    <span className="text-gray-700">{log}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}