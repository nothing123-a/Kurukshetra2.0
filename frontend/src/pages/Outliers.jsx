import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import WorkflowSteps from '../components/WorkflowSteps.jsx'
import { FiAlertTriangle, FiSearch, FiBarChart, FiArrowRight, FiDatabase } from 'react-icons/fi'

const isNumericType = (t) => typeof t === 'string' && (t.includes('float') || t.includes('int'))

export default function Outliers() {
  const { summary, config, setConfig, nextStep } = useWorkflow()
  const navigate = useNavigate()

  const numericColumns = useMemo(() => {
    if (!summary) return []
    return summary.column_names.filter((c) => isNumericType(summary.data_types[c]))
  }, [summary])

  const handleContinue = () => {
    nextStep()
    navigate('/weights')
  }

  if (!summary) {
    return (
      <WorkflowLayout>
        <div className="outliers-page">
          <div className="no-data-container">
            <div className="no-data-card">
              <div className="no-data-icon">
                <FiDatabase size={64} />
              </div>
              <h2 className="no-data-title">No Data Available</h2>
              <p className="no-data-description">
                Please upload a file first to configure outlier detection.
              </p>
            </div>
          </div>
        </div>
      </WorkflowLayout>
    )
  }

  return (
    <WorkflowLayout>
      <div className="outliers-page">
        {/* Navigation Steps */}
        <WorkflowSteps />
        
        <div className="outliers-container">
          {/* Enhanced Header */}
          <div className="outliers-header">
            <div className="header-content">
              <div className="header-icon">
                <FiAlertTriangle size={48} />
              </div>
              <h1 className="header-title">Outlier Detection & Handling</h1>
              <p className="header-subtitle">
                Configure outlier detection methods and handling strategies
              </p>
            </div>
          </div>

          {/* Detection Methods Section */}
          <div className="detection-section">
            <h3 className="section-title">
              <FiSearch size={24} />
              Detection Methods
            </h3>
            <div className="detection-grid">
              <div className="detection-card">
                <label className="detection-label">Detection Method</label>
                <select 
                  className="detection-select"
                  value={config.outliers.detection_method} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    outliers: { ...c.outliers, detection_method: e.target.value }
                  }))}
                >
                  <option value="iqr">Interquartile Range (IQR)</option>
                  <option value="zscore">Z-Score</option>
                  <option value="isolation_forest">Isolation Forest</option>
                  <option value="local_outlier_factor">Local Outlier Factor</option>
                </select>
                <p className="detection-description">
                  Choose the statistical method for detecting outliers
                </p>
              </div>

              <div className="detection-card">
                <label className="detection-label">Sensitivity Level</label>
                <select 
                  className="detection-select"
                  value={config.outliers.sensitivity} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    outliers: { ...c.outliers, sensitivity: e.target.value }
                  }))}
                >
                  <option value="low">Low (Conservative)</option>
                  <option value="medium">Medium (Balanced)</option>
                  <option value="high">High (Aggressive)</option>
                </select>
                <p className="detection-description">
                  Adjust how sensitive the detection algorithm should be
                </p>
              </div>

              <div className="detection-card">
                <label className="detection-label">Threshold Value</label>
                <input
                  type="number"
                  className="detection-input"
                  value={config.outliers.threshold} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    outliers: { ...c.outliers, threshold: parseFloat(e.target.value) }
                  }))}
                  min="1.5"
                  max="3.0"
                  step="0.1"
                  placeholder="2.0"
                />
                <p className="detection-description">
                  Set the threshold multiplier for outlier detection
                </p>
              </div>
            </div>
          </div>

          {/* Handling Strategies Section */}
          <div className="handling-section">
            <h3 className="section-title">
              <FiBarChart size={24} />
              Handling Strategies
            </h3>
            <div className="handling-grid">
              <div className="handling-card">
                <label className="handling-label">Outlier Handling</label>
                <select 
                  className="handling-select"
                  value={config.outliers.handling_strategy} 
                  onChange={(e) => setConfig(c => ({
                    ...c, 
                    outliers: { ...c.outliers, handling_strategy: e.target.value }
                  }))}
                >
                  <option value="remove">Remove Outliers</option>
                  <option value="cap">Cap at Threshold</option>
                  <option value="transform">Transform Values</option>
                  <option value="keep">Keep as Is</option>
                </select>
                <p className="handling-description">
                  Choose how to handle detected outliers
                </p>
              </div>

              <div className="handling-card">
                <label className="handling-label">Generate Report</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="generateReport"
                    checked={config.outliers.generate_report}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      outliers: { ...c.outliers, generate_report: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="generateReport" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="handling-description">
                  Generate detailed outlier analysis report
                </p>
              </div>

              <div className="handling-card">
                <label className="handling-label">Visualize Results</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="visualizeResults"
                    checked={config.outliers.visualize_results}
                    onChange={(e) => setConfig(c => ({
                      ...c,
                      outliers: { ...c.outliers, visualize_results: e.target.checked }
                    }))}
                    className="toggle-input"
                  />
                  <label htmlFor="visualizeResults" className="toggle-label">
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="handling-description">
                  Create visual charts and graphs for outliers
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
              <span>Continue to Weights & Estimation</span>
              <FiArrowRight size={20} />
            </button>
          </div>
        </div>

        <style jsx="true">{`
          .outliers-page {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
          }

          .outliers-container {
            display: flex;
            flex-direction: column;
            gap: 2rem;
          }

          .outliers-header {
            background: var(--gradient-hero);
            border-radius: 24px;
            padding: 3rem 2rem;
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
            color: var(--primary-500);
            margin-bottom: 1rem;
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

          .no-data-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
          }

          .no-data-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--gray-200);
            max-width: 400px;
          }

          .no-data-icon {
            color: var(--gray-400);
            margin-bottom: 1.5rem;
          }

          .no-data-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: 1rem;
          }

          .no-data-description {
            color: var(--gray-600);
            line-height: 1.6;
          }

          .detection-section,
          .handling-section {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--gray-200);
          }

          .section-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--gray-100);
          }

          .section-title svg {
            color: var(--primary-500);
          }

          .detection-grid,
          .handling-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
          }

          .detection-card,
          .handling-card {
            background: var(--gray-50);
            border: 1px solid var(--gray-200);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
          }

          .detection-card:hover,
          .handling-card:hover {
            background: var(--gray-100);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
          }

          .detection-label,
          .handling-label {
            display: block;
            font-weight: 600;
            color: var(--gray-800);
            margin-bottom: 0.75rem;
            font-size: 1rem;
          }

          .detection-select,
          .handling-select {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--gray-300);
            border-radius: 12px;
            background: white;
            color: var(--gray-800);
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-bottom: 0.75rem;
          }

          .detection-select:focus,
          .handling-select:focus {
            outline: none;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }

          .detection-input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--gray-300);
            border-radius: 12px;
            background: white;
            color: var(--gray-800);
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-bottom: 0.75rem;
          }

          .detection-input:focus {
            outline: none;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }

          .detection-description,
          .handling-description {
            color: var(--gray-600);
            font-size: 0.875rem;
            line-height: 1.5;
            margin: 0;
          }

          .toggle-container {
            position: relative;
            margin-bottom: 0.75rem;
          }

          .toggle-input {
            opacity: 0;
            width: 0;
            height: 0;
          }

          .toggle-label {
            display: inline-block;
            width: 60px;
            height: 32px;
            background: var(--gray-300);
            border-radius: 16px;
            cursor: pointer;
            position: relative;
            transition: all 0.3s ease;
          }

          .toggle-slider {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 28px;
            height: 28px;
            background: white;
            border-radius: 50%;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          }

          .toggle-input:checked + .toggle-label {
            background: var(--primary-500);
          }

          .toggle-input:checked + .toggle-label .toggle-slider {
            transform: translateX(28px);
          }

          .action-section {
            text-align: center;
            padding: 2rem;
          }

          .continue-button {
            padding: 1.25rem 2.5rem;
            font-size: 1.125rem;
            border-radius: 16px;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
          }

          .continue-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(59, 130, 246, 0.4);
          }

          @media (max-width: 768px) {
            .outliers-page {
              padding: 1rem;
            }

            .outliers-header {
              padding: 2rem 1rem;
              border-radius: 16px;
            }

            .header-title {
              font-size: 2rem;
            }

            .detection-grid,
            .handling-grid {
              grid-template-columns: 1fr;
              gap: 1rem;
            }

            .detection-card,
            .handling-card {
              padding: 1rem;
            }
          }
        `}</style>
      </div>
    </WorkflowLayout>
  )
}
