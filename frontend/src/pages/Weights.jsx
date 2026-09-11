import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import WorkflowSteps from '../components/WorkflowSteps.jsx'
import { FiTarget, FiBarChart, FiTrendingUp, FiArrowRight, FiDatabase, FiSettings } from 'react-icons/fi'
import './Weights.css'

const isNumericType = (t) => typeof t === 'string' && (t.includes('float') || t.includes('int'))

export default function Weights() {
  const { summary, config, setConfig, nextStep } = useWorkflow()
  const navigate = useNavigate()

  // Ensure config has default values to prevent controlled/uncontrolled input warnings
  const safeConfig = config || {
    weights: { column: '', normalization: 'none' },
    estimation: { 
      confidence_level: 0.95, 
      bootstrap_samples: 1000, 
      finite_population_correction: false, 
      stratification: false 
    },
    advanced: {
      generate_variance_estimates: false,
      design_effects: false
    }
  }

  const numericColumns = useMemo(() => {
    if (!summary) return []
    return summary.column_names.filter((c) => isNumericType(summary.data_types[c]))
  }, [summary])

  const handleContinue = () => {
    nextStep()
    navigate('/results')
  }

  if (!summary) {
    return (
      <WorkflowLayout>
        <div className="weights-page">
          <div className="no-data-container">
            <div className="no-data-card">
              <div className="no-data-icon">
                <FiDatabase size={64} />
              </div>
              <h2 className="no-data-title">No Data Available</h2>
              <p className="no-data-description">
                Please upload a file first to configure survey weights.
              </p>
            </div>
          </div>
        </div>
      </WorkflowLayout>
    )
  }

  return (
    <WorkflowLayout>
      <div className="weights-page">
        {/* Navigation Steps */}
        <WorkflowSteps />
        
        <div className="weights-container">
          {/* Enhanced Header */}
          <div className="weights-header">
            <div className="header-content">
              <div className="header-icon">
                <FiTarget size={48} />
              </div>
              <h1 className="header-title">Survey Weights & Estimation</h1>
              <p className="header-subtitle">
                Configure survey weights and statistical estimation parameters
              </p>
            </div>
          </div>

          {/* Weight Configuration Section */}
          <div className="weights-section">
            <h3 className="section-title">
              <FiBarChart size={24} />
              Weight Configuration
            </h3>
            <div className="weights-grid">
              <div className="weights-card">
                <label className="weights-label">Weight Column</label>
                <select 
                  className="weights-select"
                  value={safeConfig.weights.column} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    weights: { column: e.target.value }
                  }))}
                >
                  <option value="">No weights (Simple Random Sampling)</option>
                  {numericColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
                <p className="weights-description">
                  Select a column containing survey weights, or leave empty for unweighted analysis
                </p>
              </div>

              <div className="weights-card">
                <label className="weights-label">Weight Normalization</label>
                <select 
                  className="weights-select"
                  value={safeConfig.weights.normalization} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    weights: { ...c.weights, normalization: e.target.value }
                  }))}
                >
                  <option value="none">No Normalization</option>
                  <option value="sum">Sum to Sample Size</option>
                  <option value="mean">Mean = 1</option>
                  <option value="total">Sum to Population Size</option>
                </select>
                <p className="weights-description">
                  Choose how to normalize the survey weights
                </p>
              </div>
            </div>
          </div>

          {/* Estimation Parameters Section */}
          <div className="estimation-section">
            <h3 className="section-title">
              <FiSettings size={24} />
              Estimation Parameters
            </h3>
            <div className="estimation-grid">
              <div className="estimation-card">
                <label className="estimation-label">Confidence Level</label>
                <select 
                  className="estimation-select"
                  value={safeConfig.estimation.confidence_level} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    estimation: { ...c.estimation, confidence_level: parseFloat(e.target.value) }
                  }))}
                >
                  <option value={0.90}>90%</option>
                  <option value={0.95}>95%</option>
                  <option value={0.99}>99%</option>
                </select>
                <p className="estimation-description">
                  Set the confidence level for confidence intervals
                </p>
              </div>

              <div className="estimation-card">
                <label className="estimation-label">Bootstrap Samples</label>
                <input
                  type="number"
                  className="estimation-input"
                  value={safeConfig.estimation.bootstrap_samples} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    estimation: { ...c.estimation, bootstrap_samples: parseInt(e.target.value) }
                  }))}
                  min="100"
                  max="10000"
                  step="100"
                  placeholder="1000"
                />
                <p className="estimation-description">
                  Number of bootstrap samples for variance estimation
                </p>
              </div>

              <div className="estimation-card">
                <label className="estimation-label">Finite Population Correction</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="finitePopulationCorrection"
                    checked={safeConfig.estimation.finite_population_correction}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      estimation: { ...c.estimation, finite_population_correction: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="finitePopulationCorrection" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="estimation-description">
                  Apply finite population correction factor
                </p>
              </div>

              <div className="estimation-card">
                <label className="estimation-label">Stratification</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="stratification"
                    checked={safeConfig.estimation.stratification}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      estimation: { ...c.estimation, stratification: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="stratification" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="estimation-description">
                  Account for stratified sampling design
                </p>
              </div>
            </div>
          </div>

          {/* Advanced Options Section */}
          <div className="advanced-section">
            <h3 className="section-title">
              <FiTrendingUp size={24} />
              Advanced Options
            </h3>
            <div className="advanced-grid">
              <div className="advanced-card">
                <label className="advanced-label">Generate Variance Estimates</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="generateVarianceEstimates"
                    checked={safeConfig.advanced.generate_variance_estimates}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      advanced: { ...c.advanced, generate_variance_estimates: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="generateVarianceEstimates" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="advanced-description">
                  Calculate standard errors and confidence intervals
                </p>
              </div>

              <div className="advanced-card">
                <label className="advanced-label">Design Effects</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="designEffects"
                    checked={safeConfig.advanced.design_effects}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      advanced: { ...c.advanced, design_effects: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="designEffects" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="advanced-description">
                  Calculate design effects for complex survey designs
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
              <span>Continue to Results & Reports</span>
              <FiArrowRight size={20} />
            </button>
          </div>
        </div>
      </div>
    </WorkflowLayout>
  )
}
