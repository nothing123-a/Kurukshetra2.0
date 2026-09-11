import { useState } from 'react'
import { API_BASE_URL } from '../config.js'
import { FiEdit3, FiSettings, FiZap, FiInfo, FiCheck, FiCopy, FiFileText, FiStar, FiMessageCircle, FiGlobe, FiAlertCircle, FiMenu } from 'react-icons/fi'

export default function TypoCorrection() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [inputText, setInputText] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedMethod, setSelectedMethod] = useState('best')
  const [error, setError] = useState('')

  const methods = {
    'best': 'Best Available Method (Recommended)',
    'comprehensive': 'All Methods Combined',
    'gemini': 'AI Grammar Correction',
    'basic_spelling': 'Basic Spelling Correction (HuggingFace)',
    'advanced_spelling': 'T5 Large Spell Correction',
    'grammar': 'Grammar Correction (T5-based)',
    'spoken_typo': 'Conversational Typo Correction'
  }

  const handleCorrect = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to correct')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/typo/correct`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          method: selectedMethod
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setResults(data.results)
      } else {
        setError(data.error || 'Failed to correct text')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hamburger Menu */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed top-4 left-4 z-50 p-3 bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
      >
        <FiMenu className="w-6 h-6 text-gray-700" />
      </button>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black bg-opacity-50" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-80 bg-white shadow-xl z-50 transform transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Navigation</h2>
          <nav className="space-y-2">
            <a href="/" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</a>
            <a href="/data-cleaning" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Data Cleaning</a>
            <a href="/augmentation" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Augmentation</a>
            <a href="/analytics" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Analytics</a>
            <a href="/ai-assistant" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">AI Data Chat</a>
            <a href="/typo-correction" className="block px-4 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium">AI Typo Fix</a>
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-4 sm:py-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl sm:rounded-2xl p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 opacity-10">
              <FiEdit3 className="text-4xl sm:text-6xl lg:text-8xl" />
            </div>
            
            <div className="flex items-center justify-between flex-wrap gap-4 sm:gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-2 sm:gap-4 mb-2 sm:mb-4">
                  <FiEdit3 className="text-2xl sm:text-3xl lg:text-4xl" />
                  <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
                    AI Typo Correction
                  </h1>
                </div>
                <p className="text-sm sm:text-lg lg:text-xl opacity-90 max-w-2xl">
                  Advanced AI models including T5, BERT, and specialized correction algorithms for professional text enhancement.
                </p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8 mb-4 sm:mb-6 lg:mb-8">
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <label className="block text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FiEdit3 className="text-blue-600" />
                  Enter text to correct:
                </label>
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="w-full h-40 p-4 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 resize-none"
                    placeholder="Type or paste your text here... Try: 'teh quick brown fox jumps over teh lazy dog'"
                  />
                </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <label className="block text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FiSettings className="text-purple-600" />
                  Correction Method:
                </label>
                  <select
                    value={selectedMethod}
                    onChange={(e) => setSelectedMethod(e.target.value)}
                    className="w-full p-4 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-lg"
                  >
                    {Object.entries(methods).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleCorrect}
                  disabled={loading || !inputText.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 text-lg font-semibold flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Correcting...
                    </>
                  ) : (
                    <>
                      <FiZap className="w-5 h-5" />
                      Correct Text
                    </>
                  )}
                </button>
              </div>

            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FiInfo className="text-green-600" />
                  Available AI Models
                </h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <div>
                        <p className="font-medium text-gray-800">AI Grammar</p>
                        <p className="text-sm text-gray-600">Advanced grammar & style correction</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <div>
                        <p className="font-medium text-gray-800">T5 Large Spell</p>
                        <p className="text-sm text-gray-600">High-accuracy spell correction</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                      <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                      <div>
                        <p className="font-medium text-gray-800">Grammar Correction</p>
                        <p className="text-sm text-gray-600">Sentence structure & grammar</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                      <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                      <div>
                        <p className="font-medium text-gray-800">Conversational Fix</p>
                        <p className="text-sm text-gray-600">Chat-style text correction</p>
                      </div>
                    </div>
                  </div>
                </div>
                
              {error && (
                <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg">
                  <div className="flex items-center gap-2">
                    <FiAlertCircle className="w-5 h-5" />
                    <span className="font-medium">Error</span>
                  </div>
                  <p className="mt-1">{error}</p>
                </div>
              )}
            </div>
          </div>

          {results && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mt-8">
              <div className="text-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">🎯 Correction Results</h2>
                <p className="text-gray-600">Compare different AI correction methods</p>
              </div>
                
                {selectedMethod === 'comprehensive' ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {Object.entries(results).map(([method, text]) => (
                      <div key={method} className={`rounded-xl p-6 border-2 ${
                        method === 'original' ? 'bg-gray-50 border-gray-200' :
                        method === 'gemini' ? 'bg-blue-50 border-blue-200' :
                        method === 'basic_spelling' ? 'bg-green-50 border-green-200' :
                        method === 't5_spell' ? 'bg-purple-50 border-purple-200' :
                        'bg-orange-50 border-orange-200'
                      }`}>
                        <div className="flex justify-between items-center mb-4">
                          <h3 className="font-bold text-lg flex items-center gap-2">
                            {method === 'original' ? (
                              <><FiFileText className="text-gray-600" /> Original Text</>
                            ) : method === 'gemini' ? (
                              <><FiZap className="text-blue-600" /> AI Grammar</>
                            ) : method === 'basic_spelling' ? (
                              <><FiCheck className="text-green-600" /> Basic Spelling</>
                            ) : method === 't5_spell' ? (
                              <><FiStar className="text-purple-600" /> T5 Spell</>
                            ) : (
                              <><FiMessageCircle className="text-orange-600" /> {method}</>
                            )}
                          </h3>
                          {method !== 'original' && (
                            <button
                              onClick={() => copyToClipboard(text)}
                              className="flex items-center gap-1 px-3 py-1 bg-white rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium"
                            >
                              <FiCopy className="w-4 h-4" />
                              Copy
                            </button>
                          )}
                        </div>
                        <div className="bg-white p-4 rounded-lg border text-gray-800 leading-relaxed">
                          {text}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-8 border-2 border-green-200">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="font-bold text-xl text-gray-800 flex items-center gap-2">
                        <FiCheck className="text-green-600" />
                        Corrected Text
                      </h3>
                      <button
                        onClick={() => copyToClipboard(results.corrected)}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                      >
                        <FiCopy className="w-4 h-4" />
                        Copy Result
                      </button>
                    </div>
                    <div className="bg-white p-6 rounded-lg border-2 border-green-100 text-gray-800 text-lg leading-relaxed">
                      {results.corrected}
                    </div>
                  </div>
                )}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center">
              <FiZap className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h4 className="font-semibold text-lg text-gray-900 mb-2">AI-Powered</h4>
              <p className="text-gray-600">Multiple advanced AI models working together</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center">
              <FiCheck className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h4 className="font-semibold text-lg text-gray-900 mb-2">High Accuracy</h4>
              <p className="text-gray-600">State-of-the-art correction algorithms</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center">
              <FiGlobe className="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <h4 className="font-semibold text-lg text-gray-900 mb-2">Multi-Language</h4>
              <p className="text-gray-600">Support for various text types and styles</p>
            </div>
        </div>
      </div>
    </div>
  )
}