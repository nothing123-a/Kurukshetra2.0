import { useState, useEffect } from 'react'
import { FiEye, FiDownload, FiBarChart, FiTrendingUp, FiCheckCircle, FiZap } from 'react-icons/fi'

const DataPreview = ({ originalData, augmentedData }) => {
  const [activeTab, setActiveTab] = useState('original')
  
  // Auto-switch to Production Ready tab when AI processes data
  useEffect(() => {
    if (augmentedData) {
      setActiveTab('augmented')
    }
  }, [augmentedData])

  const downloadCSV = (data, filename) => {
    if (!data || !data.length) return
    
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const renderTable = (data) => {
    if (!data || !data.length) return null

    const columns = Object.keys(data[0])
    const displayData = data.slice(0, 8)
    const displayColumns = columns.slice(0, 6)

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {displayColumns.map(column => (
                <th
                  key={column}
                  className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column.length > 12 ? column.substring(0, 12) + '...' : column}
                </th>
              ))}
              {columns.length > 6 && (
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  +{columns.length - 6} more
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {displayData.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {displayColumns.map(column => (
                  <td key={column} className="px-3 py-2 text-sm text-gray-900">
                    {typeof row[column] === 'number' 
                      ? Number(row[column]).toFixed(2)
                      : String(row[column]).length > 15
                        ? String(row[column]).substring(0, 15) + '...'
                        : String(row[column])
                    }
                  </td>
                ))}
                {columns.length > 6 && (
                  <td className="px-3 py-2 text-sm text-gray-400">...</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="px-4 py-3 bg-gray-50 text-sm text-gray-500 flex justify-between">
          <span>Showing {Math.min(8, data.length)} of {data.length.toLocaleString()} rows</span>
          <span>{columns.length} total columns</span>
        </div>
      </div>
    )
  }

  const renderStats = (data, isAugmented = false) => {
    if (!data || !data.length) return null

    const columns = Object.keys(data[0])
    const numericColumns = columns.filter(col => 
      typeof data[0][col] === 'number'
    )

    const expansionRate = isAugmented && originalData?.preview 
      ? Math.round((data.length / originalData.preview.length) * 100) 
      : 100

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-xl font-bold text-blue-600">{data.length.toLocaleString()}</div>
          <div className="text-xs text-blue-800">Total Rows</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-xl font-bold text-green-600">{columns.length}</div>
          <div className="text-xs text-green-800">Total Features</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-xl font-bold text-purple-600">{numericColumns.length}</div>
          <div className="text-xs text-purple-800">Numeric Features</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-xl font-bold text-orange-600">{expansionRate}%</div>
          <div className="text-xs text-orange-800">Data Expansion</div>
        </div>
      </div>
    )
  }

  const renderTechniques = (augmentedData) => {
    if (!augmentedData?.techniques_applied) return null

    return (
      <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
        <h4 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <FiZap className="h-4 w-4 mr-2 text-green-600" />
          Production-Ready Transformations Applied
        </h4>
        <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
          {augmentedData.techniques_applied.map((technique, index) => (
            <div key={index} className="flex items-start space-x-2 text-xs">
              <FiCheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700">{technique}</span>
            </div>
          ))}
        </div>
        
        {augmentedData.status && (
          <div className="mt-3 p-2 bg-green-100 rounded text-xs text-green-800 font-medium">
            ✅ {augmentedData.status}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('original')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'original'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <FiEye className="h-4 w-4" />
            <span>Original</span>
          </div>
        </button>
        
        {augmentedData && (
          <button
            onClick={() => setActiveTab('augmented')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'augmented'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center justify-center space-x-2">
              <FiTrendingUp className="h-4 w-4" />
              <span>Production-Ready</span>
            </div>
          </button>
        )}
      </div>

      {/* Content */}
      {activeTab === 'original' && originalData && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Original Dataset</h3>
            <button
              onClick={() => downloadCSV(originalData.preview || originalData.data, 'original_data.csv')}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <FiDownload className="h-4 w-4" />
              <span>Download CSV</span>
            </button>
          </div>
          
          {renderStats(originalData.preview || originalData.data)}
          
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            {renderTable(originalData.preview || originalData.data)}
          </div>
        </div>
      )}

      {activeTab === 'augmented' && augmentedData && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Production-Ready Dataset
            </h3>
            <button
              onClick={() => downloadCSV(augmentedData.data, 'production_ready_data.csv')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <FiDownload className="h-4 w-4" />
              <span>Download CSV</span>
            </button>
          </div>
          
          {renderTechniques(augmentedData)}
          {renderStats(augmentedData.data, true)}
          
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            {renderTable(augmentedData.data)}
          </div>
        </div>
      )}
    </div>
  )
}

export default DataPreview