import { useState } from 'react'
import { FiZap, FiPlay, FiLoader, FiCheckCircle } from 'react-icons/fi'

const AugmentationPanel = ({ data, onAugmented }) => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleAugment = async () => {
    setLoading(true)
    setResult(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/augmentation/augment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: data.data || data.preview
        })
      })
      
      const responseData = await response.json()
      
      if (responseData.success) {
        setResult(responseData.result)
        onAugmented(responseData.result)
      } else {
        alert(`Augmentation failed: ${responseData.error}`)
      }
    } catch (error) {
      console.error('Augmentation failed:', error)
      alert(`Augmentation failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-4">
        <FiZap className="h-5 w-5 text-blue-600" />
        <h3 className="text-lg font-semibold">Smart Data Augmentation</h3>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-3">
          Automatically applies 15+ advanced augmentation techniques including:
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Voice Command Processing</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Constraint Validation</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Missing Data Imputation</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Age Validation</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Date Format Cleaning</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Data Type Optimization</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Privacy Preserving</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Intelligent Filling</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Production Ready Output</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiCheckCircle className="h-3 w-3 text-green-500" />
            <span>Quality Validation</span>
          </div>
        </div>
      </div>

      {result && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <h4 className="text-sm font-medium text-green-800 mb-2">Augmentation Complete!</h4>
          <div className="text-xs text-green-700 space-y-1">
            <p>Original size: <strong>{result.original_size}</strong> rows</p>
            <p>Processed size: <strong>{result.augmented_size}</strong> rows</p>
            <p>Quality: <strong>{Math.round((result.augmented_size / result.original_size) * 100)}%</strong></p>
          </div>
        </div>
      )}

      <button
        onClick={handleAugment}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 py-3"
      >
        {loading ? (
          <>
            <FiLoader className="h-5 w-5 animate-spin" />
            <span>Applying 12+ Techniques...</span>
          </>
        ) : (
          <>
            <FiPlay className="h-5 w-5" />
            <span>Augment Data</span>
          </>
        )}
      </button>

      {loading && (
        <div className="mt-3 text-xs text-gray-500 text-center">
          <p>Processing: Data validation, cleaning, and optimization...</p>
        </div>
      )}
    </div>
  )
}

export default AugmentationPanel