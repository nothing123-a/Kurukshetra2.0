import { useState } from 'react'
import { API_BASE_URL } from '../config.js'

export default function ApiTest() {
  const [testResults, setTestResults] = useState([])
  const [testing, setTesting] = useState(false)

  const runTests = async () => {
    setTesting(true)
    const results = []

    // Test 1: Health check
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      const data = await response.json()
      results.push({
        test: 'Health Check',
        status: response.ok ? 'PASS' : 'FAIL',
        details: `Status: ${response.status}, Data: ${JSON.stringify(data)}`
      })
    } catch (error) {
      results.push({
        test: 'Health Check',
        status: 'FAIL',
        details: `Error: ${error.message}`
      })
    }

    // Test 2: Auth check
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        credentials: 'include'
      })
      const data = await response.json()
      results.push({
        test: 'Auth Check',
        status: response.ok ? 'PASS' : 'FAIL',
        details: `Status: ${response.status}, Data: ${JSON.stringify(data)}`
      })
    } catch (error) {
      results.push({
        test: 'Auth Check',
        status: 'FAIL',
        details: `Error: ${error.message}`
      })
    }

    // Test 3: Dashboard API
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
        credentials: 'include'
      })
      const data = await response.json()
      results.push({
        test: 'Dashboard API',
        status: response.ok ? 'PASS' : 'FAIL',
        details: `Status: ${response.status}, Data: ${JSON.stringify(data)}`
      })
    } catch (error) {
      results.push({
        test: 'Dashboard API',
        status: 'FAIL',
        details: `Error: ${error.message}`
      })
    }

    setTestResults(results)
    setTesting(false)
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>API Connection Test</h1>
      <p>Backend URL: <code>{API_BASE_URL}</code></p>
      
      <button 
        onClick={runTests} 
        disabled={testing}
        style={{
          padding: '1rem 2rem',
          background: testing ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: testing ? 'not-allowed' : 'pointer',
          marginBottom: '2rem'
        }}
      >
        {testing ? 'Running Tests...' : 'Run API Tests'}
      </button>

      {testResults.length > 0 && (
        <div>
          <h2>Test Results</h2>
          {testResults.map((result, index) => (
            <div 
              key={index}
              style={{
                padding: '1rem',
                margin: '0.5rem 0',
                border: `2px solid ${result.status === 'PASS' ? '#28a745' : '#dc3545'}`,
                borderRadius: '4px',
                background: result.status === 'PASS' ? '#d4edda' : '#f8d7da'
              }}
            >
              <h3 style={{ margin: '0 0 0.5rem 0', color: result.status === 'PASS' ? '#155724' : '#721c24' }}>
                {result.test}: {result.status}
              </h3>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>
                {result.details}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}