import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import WorkflowSteps from '../components/WorkflowSteps.jsx'
import { FiSettings, FiDatabase, FiTrendingUp, FiArrowRight, FiCheckCircle } from 'react-icons/fi'
import './Configuration.css'

export default function Configuration() {
  const { summary, config, setConfig, nextStep } = useWorkflow()
  const navigate = useNavigate()

  // Filter columns for imputation
  const availableColumns = useMemo(() => {
    if (!summary) return []
    return summary.column_names
  }, [summary])

  const handleContinue = () => {
    nextStep()
    navigate('/data-augmentation')
  }

  if (!summary) {
    return (
      <WorkflowLayout>
        <div className="configuration-page">
          <div className="no-data-container">
            <div className="no-data-card">
              <div className="no-data-icon">
                <FiDatabase size={64} />
              </div>
              <h2 className="no-data-title">No Data Available</h2>
              <p className="no-data-description">
                Please upload a file first to configure processing settings.
              </p>
            </div>
          </div>
        </div>
      </WorkflowLayout>
    )
  }

  return (
    <WorkflowLayout>
      <div className="configuration-page">
        {/* Navigation Steps */}
        <WorkflowSteps />
        
        <div className="configuration-container">
          {/* Enhanced Header */}
          <div className="configuration-header">
            <div className="header-content">
              <div className="header-icon">
                <FiSettings size={48} />
              </div>
              <h1 className="header-title">Processing Configuration</h1>
              <p className="header-subtitle">
                Configure data processing settings and parameters
              </p>
            </div>
          </div>

          {/* Missing Value Imputation Section */}
          <div className="config-section">
            <h3 className="section-title">
              <FiDatabase size={24} />
              Missing Value Imputation
            </h3>
            <div className="config-grid">
              <div className="config-card">
                <label className="config-label">Imputation Method</label>
                <select 
                  className="config-select"
                  value={config.imputation.method} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    imputation: { ...c.imputation, method: e.target.value }
                  }))}
                >
                  <option value="mean">Mean</option>
                  <option value="median">Median</option>
                  <option value="mode">Mode</option>
                  <option value="drop">Drop Rows</option>
                </select>
                <p className="config-description">
                  Choose how to handle missing values in numeric columns
                </p>
              </div>

              <div className="config-card">
                <label className="config-label">Text Imputation</label>
                <select 
                  className="config-select"
                  value={config.imputation.textMethod} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    imputation: { ...c.imputation, textMethod: e.target.value }
                  }))}
                >
                  <option value="mode">Mode (Most Common)</option>
                  <option value="drop">Drop Rows</option>
                  <option value="fill">Fill with "Unknown"</option>
                </select>
                <p className="config-description">
                  Choose how to handle missing values in text columns
                </p>
              </div>
            </div>
          </div>

          {/* Data Cleaning Options */}
          <div className="config-section">
            <h3 className="section-title">
              <FiTrendingUp size={24} />
              Data Cleaning Options
            </h3>
            <div className="config-grid">
              <div className="config-card">
                <label className="config-label">Remove Duplicates</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="removeDuplicates"
                    checked={config.cleaning.removeDuplicates}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      cleaning: { ...c.cleaning, removeDuplicates: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="removeDuplicates" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="config-description">
                  Remove duplicate rows from the dataset
                </p>
              </div>

              <div className="config-card">
                <label className="config-label">Standardize Text</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="standardizeText"
                    checked={config.cleaning.standardizeText}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      cleaning: { ...c.cleaning, standardizeText: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="standardizeText" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="config-description">
                  Convert text to lowercase and trim whitespace
                </p>
              </div>

              <div className="config-card">
                <label className="config-label">Handle Outliers</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="handleOutliers"
                    checked={config.cleaning.handleOutliers}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      cleaning: { ...c.cleaning, handleOutliers: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="handleOutliers" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="config-description">
                  Detect and handle outliers in numeric columns
                </p>
              </div>

              <div className="config-card">
                <label className="config-label">Data Validation</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="dataValidation"
                    checked={config.cleaning.dataValidation}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      cleaning: { ...c.cleaning, dataValidation: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="dataValidation" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="config-description">
                  Validate data types and ranges
                </p>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <div className="action-section">
            <button 
              className="btn btn-primary continue-button"
              onClick={handleContinue}
            >
              <span>Continue to Data Augmentation</span>
              <FiArrowRight size={20} />
            </button>
          </div>
        </div>
      </div>
    </WorkflowLayout>
  )
}
