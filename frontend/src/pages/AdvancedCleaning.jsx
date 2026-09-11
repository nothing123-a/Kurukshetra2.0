import { useState } from 'react'
import { HiSparkles } from 'react-icons/hi'
import { FiDatabase, FiCheckCircle, FiSettings, FiPlay, FiDownload } from 'react-icons/fi'
import { API_BASE_URL } from '../config'

export default function AdvancedCleaning() {
  const [config, setConfig] = useState({
    remove_duplicates: true,
    fix_labels: true,
    impute_missing: true,
    handle_outliers: true,
    normalize_types: true
  })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const handleClean = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/advanced-cleaning`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ config })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setResults(data)
      } else {
        setError(data.error || 'Advanced cleaning failed')
      }
    } catch (err) {
      setError('Network error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-8 mb-8 text-white">
          <div className="flex items-center gap-4 mb-4">
            <HiSparkles className="text-4xl" />
            <h1 className="text-4xl font-bold">Advanced Data Cleaning</h1>
          </div>
          <p className="text-xl opacity-90">
            AI-powered comprehensive data cleaning with intelligent algorithms
          </p>
        </div>

        {/* Configuration Panel */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
            <FiSettings className="text-blue-600" />
            Cleaning Configuration
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              { key: 'remove_duplicates', label: 'Remove Duplicates', desc: 'Intelligent duplicate detection and removal' },
              { key: 'fix_labels', label: 'Fix Inconsistent Labels', desc: 'Normalize categorical values using fuzzy matching' },
              { key: 'impute_missing', label: 'Impute Missing Values', desc: 'Advanced imputation using regression and clustering' },
              { key: 'handle_outliers', label: 'Handle Outliers', desc: 'Detect and cap outliers using Isolation Forest' },
              { key: 'normalize_types', label: 'Normalize Data Types', desc: 'Optimize data types for memory efficiency' }
            ].map((option) => (
              <div key={option.key} className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg">
                <input
                  type="checkbox"
                  id={option.key}
                  checked={config[option.key]}
                  onChange={(e) => setConfig(prev => ({ ...prev, [option.key]: e.target.checked }))}
                  className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <label htmlFor={option.key} className="font-medium text-gray-900 cursor-pointer">
                    {option.label}
                  </label>
                  <p className="text-sm text-gray-600 mt-1">{option.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <div className="text-center mb-6">
          <button
            onClick={handleClean}
            disabled={loading}
            className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold text-lg hover:shadow-lg transition-all duration-200 disabled:opacity-50 mx-auto"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Processing...
              </>
            ) : (
              <>
                <FiPlay />
                Start Advanced Cleaning
              </>
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
              <FiCheckCircle className="text-green-600" />
              Cleaning Results
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2">Data Shape</h4>
                <p className="text-blue-700">
                  {results.data_shape.rows.toLocaleString()} rows × {results.data_shape.columns} columns
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">Processing Steps</h4>
                <p className="text-green-700">{results.cleaning_log.length} operations completed</p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">Cleaning Log</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {results.cleaning_log.map((log, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <FiCheckCircle className="text-green-500 flex-shrink-0" />
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