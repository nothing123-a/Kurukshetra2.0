import { useState, useRef } from 'react'
import { FiMenu } from 'react-icons/fi'
import { API_BASE_URL } from '../config.js'
import { FiUpload, FiZap, FiDownload, FiMic, FiPlay, FiLoader, FiSend, FiMicOff, FiVolume2 } from 'react-icons/fi'
import { BsRobot } from 'react-icons/bs'
import DataPreview from '../components/DataPreview.jsx'
import AugmentationPanel from '../components/AugmentationPanel.jsx'

export default function Augmentation() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [file, setFile] = useState(null)
  const [data, setData] = useState(null)
  const [augmentedData, setAugmentedData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [command, setCommand] = useState('')
  const [commandResult, setCommandResult] = useState(null)
  const [commandLoading, setCommandLoading] = useState(false)
  
  // AI Chatbot states
  const [messages, setMessages] = useState([])
  const [textInput, setTextInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  
  // Voice Assistant states
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState(null)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const handleFileUpload = async (event) => {
    const selectedFile = event.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setLoading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_BASE_URL}/api/augmentation/upload`, {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      
      if (response.ok) {
        setData(result)
      } else {
        setError(result.error || 'Upload failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAugment = async () => {
    if (!data) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/api/augmentation/augment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          data: data.data
        })
      })

      const result = await response.json()
      
      if (response.ok) {
        setAugmentedData(result.result)
      } else {
        setError(result.error || 'Augmentation failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleProcessCommand = async () => {
    if (!command.trim() || !data) return

    setCommandLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/api/augmentation/process-command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          command: command,
          columns: data.columns,
          data: data.data
        })
      })

      const result = await response.json()
      
      if (response.ok) {
        setCommandResult(result.result)
      } else {
        setError(result.error || 'Command processing failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setCommandLoading(false)
    }
  }

  const downloadData = (dataToDownload, filename) => {
    const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // AI Chatbot functions
  const addMessage = (sender, text, actionData = null) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString(),
      actionData
    }])
  }

  const convertToCSV = (data) => {
    if (!data || data.length === 0) return ''
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n')
    return csvContent
  }

  const downloadCSV = (data, filename) => {
    const csv = convertToCSV(data)
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const submitToGemini = async (command) => {
    if (!data || !data.columns || !data.data) {
      addMessage('bot', 'Please upload a valid dataset first')
      return
    }

    setIsProcessing(true)
    addMessage('bot', '🤖 Analyzing your data with AI...')

    try {
      // Debug: Log what we're sending
      console.log('Sending to Gemini:', {
        command: command,
        columns: data.columns || [],
        dataLength: data.data ? data.data.length : 0,
        sampleData: data.data ? data.data.slice(0, 3) : []
      })
      
      // Send actual CSV data to AI for processing
      const response = await fetch(`${API_BASE_URL}/api/augmentation/process-command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: command,
          columns: data.columns || [],
          data: data.data || [],
          filename: data.filename || 'data.csv',
          sample_data: data.preview || [] // Send preview for context
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      
      // Debug: Log the response
      console.log('Gemini response:', result)
      
      if (result.success && result.result) {
        // Show AI response
        const message = result.result.message || 'Data processed successfully!'
        addMessage('bot', `✅ **Analysis Complete!**\n\n${message}`)
        
        // If data was processed, update and offer download
        if (result.result.processed_data && Array.isArray(result.result.processed_data) && result.result.processed_data.length > 0) {
          const processedData = {
            data: result.result.processed_data,
            original_size: data.data ? data.data.length : 0,
            processed_size: result.result.processed_data.length,
            changes_made: result.result.changes_made || ['Data processed successfully']
          }
          
          setAugmentedData(processedData)
          
          // UPDATE THE MAIN DATA STATE WITH PROCESSED DATA
          setData(prevData => ({
            ...prevData,
            data: result.result.processed_data,
            preview: result.result.processed_data.slice(0, 10) // Update preview too
          }))
          
          // Add download message with button
          const originalRows = data.data ? data.data.length : 0
          const processedRows = result.result.processed_data.length
          const changes = result.result.changes_made || ['Data processed']
          
          addMessage('bot', `📦 **Data Processing Complete!**\n\n• Original rows: ${originalRows}\n• Processed rows: ${processedRows}\n• Changes: ${changes.join(', ')}\n\n💾 Ready for download!`, { 
            type: 'download', 
            data: result.result.processed_data,
            filename: `ai_processed_${data.filename || 'data'}.csv`,
            changes: changes
          })
        } else {
          addMessage('bot', 'ℹ️ Analysis completed. No changes were needed for your data.')
        }
      } else {
        const errorMsg = result.error || 'Processing completed with some issues.'
        addMessage('bot', `⚠️ ${errorMsg}`)
      }
    } catch (error) {
      console.error('API Error:', error)
      addMessage('bot', '❌ Connection error. Please check your internet connection and try again.')
    }
    
    setIsProcessing(false)
  }

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      addMessage('user', textInput)
      setTextInput('')
    }
  }

  // Voice Assistant functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const formData = new FormData()
        formData.append('audio', audioBlob, 'recording.wav')

        try {
          const response = await fetch(`${API_BASE_URL}/api/augmentation/transcribe`, {
            method: 'POST',
            body: formData
          })
          const result = await response.json()
          const transcribed = result.text
          
          addMessage('user', transcribed)
        } catch (error) {
          addMessage('bot', 'Error transcribing audio')
        }
      }

      mediaRecorderRef.current.start()
      setIsListening(true)
    } catch (error) {
      addMessage('bot', 'Microphone access denied')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsListening(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-1.5">
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl sm:rounded-2xl p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 opacity-10">
              <FiZap className="text-4xl sm:text-6xl lg:text-8xl" />
            </div>
            
            <div className="flex items-center justify-between flex-wrap gap-4 sm:gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-2 sm:gap-4 mb-2 sm:mb-4">
                  <FiZap className="text-2xl sm:text-3xl lg:text-4xl" />
                  <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
                    Real Time Augmentation
                  </h1>
                </div>
                <p className="text-sm sm:text-lg lg:text-xl opacity-90 max-w-2xl">
                  Real-time data augmentation with Gemini AI voice commands, natural language processing, and intelligent data transformation.
                </p>
              </div>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-8">
            <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-900">
              <FiUpload className="mr-3 text-purple-600" />
              Upload Dataset
            </h2>
          
            <div className="border-2 border-dashed border-purple-300 rounded-xl p-12 text-center bg-gradient-to-br from-purple-50 to-blue-50 hover:from-purple-100 hover:to-blue-100 transition-all duration-200">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
                <div className="bg-purple-100 p-4 rounded-full mb-4">
                  <FiUpload className="h-12 w-12 text-purple-600" />
                </div>
                <span className="text-xl font-semibold text-gray-700 mb-2">
                  Choose a file to upload
                </span>
                <span className="text-gray-500">
                  Supports CSV, Excel (.xlsx, .xls) files up to 16MB
                </span>
            </label>
            </div>

            {loading && (
              <div className="mt-6 flex items-center justify-center bg-blue-50 p-4 rounded-lg">
                <FiLoader className="animate-spin mr-3 text-blue-600" size={20} />
                <span className="text-blue-800 font-medium">Processing file...</span>
              </div>
            )}
          </div>

        {/* Data Preview */}
        {data && data.columns && data.preview && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-8">
            <h2 className="text-xl font-semibold mb-6 text-gray-900">Dataset Preview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-1">File Name</h3>
                <p className="text-blue-600">{data.filename || 'Unknown'}</p>
              </div>
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-1">Rows</h3>
                <p className="text-2xl font-bold text-green-600">{data.shape ? data.shape[0].toLocaleString() : 'N/A'}</p>
              </div>
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-1">Columns</h3>
                <p className="text-2xl font-bold text-purple-600">{data.shape ? data.shape[1] : data.columns.length}</p>
              </div>
            </div>
            
            <div className="overflow-x-auto bg-gray-50 rounded-lg">
              <table className="min-w-full table-auto">
                <thead>
                  <tr className="bg-gradient-to-r from-gray-100 to-gray-200">
                    {data.columns.map((col, idx) => (
                      <th key={idx} className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.preview.slice(0, 5).map((row, idx) => (
                    <tr key={idx} className="border-t hover:bg-white transition-colors">
                      {data.columns.map((col, colIdx) => (
                        <td key={colIdx} className="px-6 py-3 text-sm text-gray-600">
                          {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-gray-400 italic">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* AI Assistant Section */}
        {data && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-4 sm:mb-6">
            {/* AI Chatbot */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center mb-4">
                <BsRobot className="h-5 w-5 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">AI Assistant</h3>
              </div>

              <div className="h-64 overflow-y-auto space-y-2 mb-4 border rounded-lg p-3 bg-gray-50">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <BsRobot className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="font-medium mb-2">🤖 AI Assistant Ready</p>
                    <p className="text-sm mb-1">Try commands like:</p>
                    <div className="text-xs space-y-1">
                      <p>• "Fix negative ages in age column"</p>
                      <p>• "Replace zero emails with dummy@email.com"</p>
                      <p>• "Clean invalid phone numbers"</p>
                      <p>• "Remove duplicate entries"</p>
                    </div>
                  </div>
                ) : (
                  messages.map(msg => (
                    <div key={msg.id} className="mb-3">
                      {msg.sender === 'user' ? (
                        <div>
                          <div className="bg-blue-100 text-blue-800 p-2 rounded mb-2">
                            <div className="font-medium text-sm">Your Command:</div>
                            <div className="text-sm">{msg.text}</div>
                          </div>
                          <button
                            onClick={() => submitToGemini(msg.text)}
                            disabled={isProcessing}
                            className="w-full px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 text-sm font-medium flex items-center justify-center gap-2"
                          >
                            {isProcessing ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                Processing...
                              </>
                            ) : (
                              <>
                                <BsRobot className="w-4 h-4" />
                                Send to AI
                              </>
                            )}
                          </button>
                        </div>
                      ) : (
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 p-3 rounded-lg">
                          <div className="font-semibold text-sm text-blue-800 mb-1">🤖 AI Assistant:</div>
                          <div className="text-sm text-blue-900 whitespace-pre-line leading-relaxed">{msg.text}</div>
                          {msg.actionData?.type === 'download' && (
                            <div className="mt-3 space-y-2">
                              <button
                                onClick={() => downloadCSV(msg.actionData.data, msg.actionData.filename)}
                                className="w-full px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 text-sm font-semibold flex items-center justify-center gap-2 transition-all duration-200"
                              >
                                📥 Download Processed Data
                              </button>
                              {msg.actionData.changes && msg.actionData.changes.length > 0 && (
                                <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                                  <strong>Changes made:</strong> {msg.actionData.changes.join(', ')}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
                {isProcessing && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 p-3 rounded-lg text-sm">
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <div className="font-medium text-blue-800">🤖 AI Assistant</div>
                    </div>
                    <div className="text-blue-700 mt-1">Analyzing your data...</div>
                  </div>
                )}
              </div>

              <div className="flex space-x-2">
                <input
                  type="text"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
                  placeholder="Type your command..."
                  className="flex-1 px-3 py-2 border rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleTextSubmit}
                  disabled={!textInput.trim() || isProcessing}
                  className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  <FiSend className="h-4 w-4" />
                </button>
                <button
                  onClick={isListening ? stopRecording : startRecording}
                  className={`px-3 py-2 rounded ${
                    isListening 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {isListening ? <FiMicOff className="h-4 w-4" /> : <FiMic className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Voice Assistant */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center mb-4">
                <FiVolume2 className="h-5 w-5 text-purple-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">Voice Assistant</h3>
              </div>

              <div className="text-center mb-4">
                <div className="mb-3">
                  <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center ${
                    isListening ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    {isListening ? (
                      <div className="animate-pulse">
                        <FiMic className="h-6 w-6" />
                      </div>
                    ) : (
                      <FiMicOff className="h-6 w-6" />
                    )}
                  </div>
                </div>

                <button
                  onClick={isListening ? stopRecording : startRecording}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors text-sm ${
                    isListening
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-purple-600 hover:bg-purple-700 text-white'
                  }`}
                >
                  {isListening ? 'Stop Voice' : 'Start Voice'}
                </button>
              </div>
              
              {isListening && currentTranscript && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="text-sm font-medium text-yellow-800 mb-1">Speaking...</div>
                  <div className="text-sm text-yellow-700">{currentTranscript}</div>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Voice Commands Examples:</h4>
                <div className="space-y-1 text-xs text-gray-600">
                  <p>• "Fix negative ages in the dataset"</p>
                  <p>• "Replace zero emails with dummy emails"</p>
                  <p>• "Clean invalid dates"</p>
                  <p>• "Remove duplicate entries"</p>
                  <p>• "Process all data issues"</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Augmentation Section */}
        {data && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center text-gray-900">
              <FiZap className="mr-2 text-blue-600" />
              Smart Data Augmentation
            </h2>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-3">
                Automatically applies 12+ advanced augmentation techniques including:
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs text-gray-500 mb-4">
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Voice Command Processing
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Constraint Validation
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Missing Data Imputation
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Age Validation
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Date Format Cleaning
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Data Type Optimization
                </div>
              </div>
            </div>

            <button
              onClick={handleAugment}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <FiLoader className="animate-spin mr-2" />
                  Applying Augmentation Techniques...
                </>
              ) : (
                <>
                  <FiZap className="mr-2" />
                  Augment Data
                </>
              )}
            </button>
          </div>
        )}

        {/* Results Section */}
        {augmentedData && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Augmentation Results</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-blue-800">Original Size</h3>
                <p className="text-2xl font-bold text-blue-600">{augmentedData.original_size}</p>
                <p className="text-sm text-blue-600">rows</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-medium text-green-800">Processed Size</h3>
                <p className="text-2xl font-bold text-green-600">{augmentedData.processed_size || augmentedData.augmented_size || 0}</p>
                <p className="text-sm text-green-600">rows</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-medium text-purple-800">Changes Made</h3>
                <p className="text-2xl font-bold text-purple-600">{augmentedData.changes_made ? augmentedData.changes_made.length : 0}</p>
                <p className="text-sm text-purple-600">modifications</p>
              </div>
            </div>

            <div className="mb-4">
              <h3 className="font-medium text-gray-800 mb-2">Techniques Applied:</h3>
              <div className="space-y-1">
                {augmentedData.techniques_applied && augmentedData.techniques_applied.length > 0 ? (
                  augmentedData.techniques_applied.map((technique, idx) => (
                    <p key={idx} className="text-sm text-gray-600">{technique}</p>
                  ))
                ) : (
                  <p className="text-sm text-gray-600">Data processing completed</p>
                )}
              </div>
            </div>

            <button
              onClick={() => downloadData(augmentedData.data, 'augmented_data.json')}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 flex items-center"
            >
              <FiDownload className="mr-2" />
              Download Augmented Data
            </button>
          </div>
        )}

        {/* Data Preview Section */}
        {(data || augmentedData) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-8">
            <h2 className="text-xl font-semibold mb-6 text-gray-900">Data Preview & Results</h2>
            {data && data.columns && data.preview ? (
              <DataPreview 
                originalData={data} 
                augmentedData={augmentedData}
              />
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No data preview available</p>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}