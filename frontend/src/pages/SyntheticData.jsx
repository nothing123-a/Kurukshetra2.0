import { useState } from 'react'
import { BsRobot } from 'react-icons/bs'
import { FiDatabase, FiCheckCircle, FiSettings, FiPlay, FiTrendingUp } from 'react-icons/fi'
import { API_BASE_URL } from '../config'

export default function SyntheticData() {
  const [config, setConfig] = useState({
    target_column: '',
    target_size: 2000,
    methods: ['smote', 'gaussian_noise', 'bootstrap']
  })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const availableMethods = [
    { key: 'smote', label: 'SMOTE Oversampling', desc: 'Synthetic Minority Oversampling Technique' },
    { key: 'gaussian_noise', label: 'Gaussian Noise', desc: 'Add statistical noise for augmentation' },
    { key: 'bootstrap', label: 'Bootstrap Sampling', desc: 'Stratified resampling technique' },
    { key: 'mixup', label: 'Mixup Augmentation', desc: 'Advanced data mixing technique' },
    { key: 'permutation', label: 'Feature Permutation', desc: 'Permute feature values for variation' }
  ]

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/synthetic-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ config })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setResults(data)
      } else {
        setError(data.error || 'Synthetic data generation failed')
      }
    } catch (err) {
      setError('Network error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleMethodToggle = (method) => {
    setConfig(prev => ({
      ...prev,
      methods: prev.methods.includes(method)
        ? prev.methods.filter(m => m !== method)
        : [...prev.methods, method]
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 mb-8 text-white">
          <div className="flex items-center gap-4 mb-4">
            <BsRobot className="text-4xl" />
            <h1 className="text-4xl font-bold">Synthetic Data Generation</h1>
          </div>
          <p className="text-xl opacity-90">
            Generate high-quality synthetic data using advanced AI techniques
          </p>
        </div>

        {/* Configuration Panel */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="flex items-center gap-3 text-xl font-semibold text-gray-900 mb-6">
            <FiSettings className="text-indigo-600" />
            Generation Configuration
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Column (Optional)
              </label>
              <input
                type="text"
                value={config.target_column}
                onChange={(e) => setConfig(prev => ({ ...prev, target_column: e.target.value }))}
                placeholder="e.g., target, label, class"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty for unsupervised augmentation</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Dataset Size
              </label>
              <input
                type="number"
                value={config.target_size}
                onChange={(e) => setConfig(prev => ({ ...prev, target_size: parseInt(e.target.value) }))}
                min="100"
                max="100000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">Final number of samples after augmentation</p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Augmentation Methods</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {availableMethods.map((method) => (
                <div key={method.key} className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg">
                  <input
                    type="checkbox"
                    id={method.key}
                    checked={config.methods.includes(method.key)}
                    onChange={() => handleMethodToggle(method.key)}
                    className="mt-1 w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                  />
                  <div className="flex-1">
                    <label htmlFor={method.key} className="font-medium text-gray-900 cursor-pointer">
                      {method.label}
                    </label>
                    <p className="text-sm text-gray-600 mt-1">{method.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="text-center mb-6">
          <button
            onClick={handleGenerate}
            disabled={loading || config.methods.length === 0}
            className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold text-lg hover:shadow-lg transition-all duration-200 disabled:opacity-50 mx-auto"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Generating...
              </>
            ) : (
              <>
                <FiPlay />
                Generate Synthetic Data
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
              Generation Results
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2">Original Size</h4>
                <p className="text-2xl font-bold text-blue-700">
                  {results.original_size.toLocaleString()}
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">Augmented Size</h4>
                <p className="text-2xl font-bold text-green-700">
                  {results.augmented_size.toLocaleString()}
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-semibold text-purple-900 mb-2">Augmentation Ratio</h4>
                <p className="text-2xl font-bold text-purple-700">
                  {results.augmentation_ratio.toFixed(1)}x
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">Generation Log</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {results.generation_log.map((log, index) => (
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