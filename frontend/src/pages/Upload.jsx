import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import { API_BASE_URL } from '../config.js'
import { FiUpload, FiFile, FiShield, FiInfo } from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

export default function Upload() {
  const { setDatasetId, setSummary, notify, nextStep } = useWorkflow()
  const [busy, setBusy] = useState(false)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const uploadFile = useCallback(async (file) => {
    const form = new FormData()
    form.append('file', file)
    setBusy(true)
    
    try {
      const res = await fetch(`${API_BASE_URL}/upload`, { 
        method: 'POST', 
        body: form, 
        credentials: 'include' 
      })
      const text = await res.text()
      const data = (() => { 
        try { 
          return JSON.parse(text) 
        } catch { 
          return { success: false, error: text } 
        } 
      })()
      
      if (!res.ok || !data.success) {
        throw new Error(data.error || `HTTP ${res.status}`)
      }
      
      setSummary(data.summary)
      setDatasetId(data.dataset.id)
      notify('success', 'File uploaded successfully')
      nextStep()
      navigate('/summary')
    } catch (e) {
      notify('error', `Upload failed: ${e.message}`)
    } finally {
      setBusy(false)
    }
  }, [setDatasetId, setSummary, notify, nextStep, navigate])

  const handleDrop = useCallback(async (evt) => {
    evt.preventDefault()
    const file = evt.dataTransfer?.files?.[0]
    if (!file) return
    await uploadFile(file)
  }, [uploadFile])

  return (
    <div className="upload-page fade-in-up">
      <div className="upload-container">
        {/* Enhanced Header */}
        {/* <div className="upload-header">
          <div className="header-content">
            <div className="header-icon">
              <HiSparkles />
            </div>
            <h1 className="header-title">Upload Your Data</h1>
            <p className="header-subtitle">
              Start your data cleaning journey by uploading your dataset
            </p>
          </div>
        </div> */}

        {/* Enhanced Upload Area */}
        <div className="upload-card">
          <div
            className="upload-area"
            onDragOver={(e) => { e.preventDefault() }}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="upload-icon">
              <FiUpload size={64} />
            </div>
            <h2 className="upload-title">Drag & Drop your data file here</h2>
            <p className="upload-description">
              Supports CSV, Excel (.xlsx, .xls) files up to 16MB
            </p>
            <button className="btn btn-primary upload-button">
              <FiFile size={20} />
              Choose File
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) uploadFile(file)
              }}
              style={{ display: 'none' }}
            />
          </div>
        </div>

        {/* Enhanced Features Section */}
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <FiShield size={24} />
            </div>
            <h3 className="feature-title">Secure Upload</h3>
            <p className="feature-description">
              Your data is encrypted and processed securely
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <FiInfo size={24} />
            </div>
            <h3 className="feature-title">Smart Processing</h3>
            <p className="feature-description">
              AI-powered data cleaning and analysis
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <FiFile size={24} />
            </div>
            <h3 className="feature-title">Multiple Formats</h3>
            <p className="feature-description">
              Support for CSV, Excel, and other formats
            </p>
          </div>
        </div>

        {/* Loading State */}
        {busy && (
          <div className="loading-overlay">
            <div className="loading-content">
              <div className="loading-spinner"></div>
              <p className="loading-text">Processing your file...</p>
            </div>
          </div>
        )}
      </div>

      <style jsx="true">{`
        .upload-page {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem;
        }

        .upload-container {
          position: relative;
        }

        .upload-header {
          background: var(--gradient-hero);
          border-radius: 24px;
          padding: 3rem 2rem;
          margin-bottom: 2rem;
          text-align: center;
          position: relative;
          overflow: hidden;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .header-content {
          position: relative;
          z-index: 10;
        }

        .header-icon {
          font-size: 4rem;
          color: var(--primary-400);
          margin-bottom: 1rem;
          opacity: 0.8;
        }

        .header-title {
          font-size: 2.5rem;
          font-weight: 800;
          margin-bottom: 1rem;
          background: var(--gradient-text);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .header-subtitle {
          font-size: 1.125rem;
          color: var(--gray-600);
          max-width: 500px;
          margin: 0 auto;
          line-height: 1.6;
        }

        .upload-card {
          background: white;
          border-radius: 20px;
          padding: 3rem;
          margin-bottom: 2rem;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
          border: 1px solid var(--gray-200);
          transition: all 0.3s ease;
        }

        .upload-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .upload-area {
          border: 3px dashed var(--primary-300);
          border-radius: 16px;
          padding: 4rem 2rem;
          text-align: center;
          background: var(--primary-50);
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
        }

        .upload-area:hover {
          border-color: var(--primary-500);
          background: var(--primary-100);
          transform: scale(1.02);
        }

        .upload-icon {
          color: var(--primary-500);
          margin-bottom: 1.5rem;
          margin-left: 263px;
        }

        .upload-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--gray-800);
          margin-bottom: 0.75rem;
        }

        .upload-description {
          color: var(--gray-600);
          margin-bottom: 2rem;
          font-size: 1rem;
        }

        .upload-button {
          padding: 1rem 2rem;
          font-size: 1.125rem;
          border-radius: 12px;
          box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        }

        .upload-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 12px 35px rgba(59, 130, 246, 0.4);
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }

        .feature-card {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          text-align: center;
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
          border: 1px solid var(--gray-200);
          transition: all 0.3s ease;
        }

        .feature-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        }

        .feature-icon {
          width: 64px;
          height: 64px;
          background: var(--primary-100);
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          color: var(--primary-600);
          transition: all 0.3s ease;
        }

        .feature-card:hover .feature-icon {
          background: var(--primary-200);
          transform: scale(1.1);
        }

        .feature-title {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--gray-800);
          margin-bottom: 0.75rem;
        }

        .feature-description {
          color: var(--gray-600);
          line-height: 1.6;
        }

        .loading-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          backdrop-filter: blur(8px);
        }

        .loading-content {
          background: white;
          border-radius: 20px;
          padding: 3rem;
          text-align: center;
          box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
        }

        .loading-spinner {
          width: 48px;
          height: 48px;
          border: 4px solid var(--gray-200);
          border-top: 4px solid var(--primary-500);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        .loading-text {
          color: var(--gray-700);
          font-size: 1.125rem;
          font-weight: 500;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .upload-page {
            padding: 1rem;
          }

          .upload-header {
            padding: 2rem 1rem;
            border-radius: 16px;
          }

          .header-title {
            font-size: 2rem;
          }

          .upload-card {
            padding: 2rem 1rem;
            border-radius: 16px;
          }

          .upload-area {
            padding: 2rem 1rem;
          }

          .features-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
        }
      `}</style>
    </div>
  )
}
