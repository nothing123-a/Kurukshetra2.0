import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import WorkflowSteps from '../components/WorkflowSteps.jsx'
import { FiBarChart, FiTrendingUp, FiDatabase, FiFileText, FiArrowRight } from 'react-icons/fi'

const isNumericType = (t) => typeof t === 'string' && (t.includes('float') || t.includes('int'))

export default function Summary() {
  const { summary, nextStep } = useWorkflow()
  const navigate = useNavigate()

  const numericColumns = useMemo(() => {
    if (!summary || !summary.data_types || !summary.column_names) return []
    return summary.column_names.filter((c) => summary.data_types[c] && isNumericType(summary.data_types[c]))
  }, [summary])

  const handleContinue = () => {
    nextStep()
    navigate('/configuration')
  }

  if (!summary) {
    return (
      <WorkflowLayout>
        <div className="summary-page">
          <div className="no-data-container">
            <div className="no-data-card">
              <div className="no-data-icon">
                <FiDatabase size={64} />
              </div>
              <h2 className="no-data-title">No Data Available</h2>
              <p className="no-data-description">
                Please upload a file first to view the summary.
              </p>
            </div>
          </div>
        </div>
      </WorkflowLayout>
    )
  }

  return (
    <WorkflowLayout>
      <div className="summary-page">
        {/* Navigation Steps */}
        <WorkflowSteps />
        
        <div className="summary-container">
          {/* Enhanced Header */}
          <div className="summary-header">
            <div className="header-content">
              <div className="header-icon">
                <FiBarChart size={48} />
              </div>
              <h1 className="header-title">Data Summary</h1>
              <p className="header-subtitle">
                Overview of your uploaded survey data
              </p>
            </div>
          </div>

          {/* Key Statistics Cards */}
          <div className="stats-section">
            <h3 className="section-title">
              <FiTrendingUp size={24} />
              Key Statistics
            </h3>
            <div className="stats-grid">
              <div className="stat-card primary">
                <div className="stat-icon">
                  <FiDatabase size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{summary.rows.toLocaleString()}</div>
                  <div className="stat-label">Total Rows</div>
                </div>
              </div>
              
              <div className="stat-card secondary">
                <div className="stat-icon">
                  <FiFileText size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{summary.column_names.length}</div>
                  <div className="stat-label">Total Columns</div>
                </div>
              </div>
              
              <div className="stat-card success">
                <div className="stat-icon">
                  <FiBarChart size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{numericColumns.length}</div>
                  <div className="stat-label">Numeric Columns</div>
                </div>
              </div>
              
              <div className="stat-card warning">
                <div className="stat-icon">
                  <FiTrendingUp size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">
                    {((summary.rows * summary.column_names.length) / 1000).toFixed(1)}k
                  </div>
                  <div className="stat-label">Data Points</div>
                </div>
              </div>
            </div>
          </div>

          {/* Data Types Section */}
          <div className="data-types-section">
            <h3 className="section-title">
              <FiFileText size={24} />
              Data Types & Structure
            </h3>
            <div className="data-types-grid">
              {summary.column_names.map((column, index) => (
                <div key={index} className="data-type-card">
                  <div className="column-name">{column}</div>
                  <div className="data-type-badge">
                    {summary.data_types?.[column] || 'text'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Continue Button */}
          <div className="action-section">
            <button 
              className="btn btn-primary continue-button"
              onClick={handleContinue}
            >
              <span>Continue to Configuration</span>
              <FiArrowRight size={20} />
            </button>
          </div>
        </div>

        <style jsx="true">{`
          .summary-page {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
          }

          .summary-container {
            display: flex;
            flex-direction: column;
            gap: 2rem;
          }

          .summary-header {
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

          .stats-section,
          .data-types-section {
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

          .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
          }

          .stat-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1.5rem;
            border-radius: 16px;
            color: white;
            transition: all 0.3s ease;
          }

          .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
          }

          .stat-card.primary {
            background: var(--gradient-primary);
          }

          .stat-card.secondary {
            background: var(--gradient-text);
          }

          .stat-card.success {
            background: linear-gradient(135deg, var(--accent-green), #34d399);
          }

          .stat-card.warning {
            background: var(--gradient-gold);
          }

          .stat-icon {
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
          }

          .stat-content {
            flex: 1;
          }

          .stat-number {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
          }

          .stat-label {
            font-size: 0.875rem;
            font-weight: 500;
            opacity: 0.9;
          }

          .data-types-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
          }

          .data-type-card {
            background: var(--gray-50);
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 1rem;
            transition: all 0.3s ease;
          }

          .data-type-card:hover {
            background: var(--gray-100);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
          }

          .column-name {
            font-weight: 600;
            color: var(--gray-800);
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
          }

          .data-type-badge {
            background: var(--primary-100);
            color: var(--primary-700);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            display: inline-block;
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
            .summary-page {
              padding: 1rem;
            }

            .summary-header {
              padding: 2rem 1rem;
              border-radius: 16px;
            }

            .header-title {
              font-size: 2rem;
            }

            .stats-grid {
              grid-template-columns: 1fr;
              gap: 1rem;
            }

            .data-types-grid {
              grid-template-columns: 1fr;
            }

            .stat-card {
              padding: 1rem;
            }

            .stat-number {
              font-size: 1.5rem;
            }
          }
        `}</style>
      </div>
    </WorkflowLayout>
  )
}
