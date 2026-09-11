import { useState } from 'react'
import { useLocation } from 'react-router-dom'

import Upload from './Upload'
import Summary from './Summary'
import Configuration from './Configuration'
import Outliers from './Outliers'
import Weights from './Weights'
import Results from './Results'
import { 
  FiUpload, FiBarChart, FiSettings, FiAlertTriangle, 
  FiTarget, FiCheckCircle, FiDatabase 
} from 'react-icons/fi'

const cleaningSteps = [
  { 
    id: 'upload', 
    label: 'Upload Data', 
    icon: FiUpload,
    component: Upload,
    description: 'Upload your dataset'
  },
  { 
    id: 'summary', 
    label: 'Data Summary', 
    icon: FiBarChart,
    component: Summary,
    description: 'View data overview'
  },
  { 
    id: 'configuration', 
    label: 'Configuration', 
    icon: FiSettings,
    component: Configuration,
    description: 'Configure cleaning settings'
  },
  { 
    id: 'outliers', 
    label: 'Outlier Detection', 
    icon: FiAlertTriangle,
    component: Outliers,
    description: 'Detect and handle outliers'
  },
  { 
    id: 'weights', 
    label: 'Weights & Estimation', 
    icon: FiTarget,
    component: Weights,
    description: 'Apply weights and calculate estimates'
  },
  { 
    id: 'results', 
    label: 'Results & Reports', 
    icon: FiCheckCircle,
    component: Results,
    description: 'View results and generate reports'
  }
]

export default function DataCleaning() {
  const location = useLocation()
  const [activeStep, setActiveStep] = useState('upload')

  // Get active step from URL or default to upload
  const getCurrentStep = () => {
    const path = location.pathname
    if (path.includes('/summary')) return 'summary'
    if (path.includes('/configuration')) return 'configuration'
    if (path.includes('/outliers')) return 'outliers'
    if (path.includes('/weights')) return 'weights'
    if (path.includes('/results')) return 'results'
    return activeStep
  }

  const currentStep = getCurrentStep()
  const CurrentComponent = cleaningSteps.find(step => step.id === currentStep)?.component || Upload

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Enhanced Data Cleaning Navigation */}
      <div className="cleaning-navigation" style={{padding: '5px'}}>
        <div className="nav-container">
          <div className="nav-steps">
            {cleaningSteps.map((step) => {
              const Icon = step.icon
              const isActive = currentStep === step.id
              
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveStep(step.id)}
                  className={`nav-step ${isActive ? 'active' : ''}`}
                  title={step.description}
                >
                  <div className="step-icon">
                    <Icon size={20} />
                  </div>
                  <span className="step-label">{step.label}</span>
                  {isActive && <div className="active-indicator" />}
                </button>
              )
            })}
          </div>
        </div>
      </div>



      {/* Current Step Content */}
      <div className="step-content-area" style={{padding: '5px'}}>
        <CurrentComponent />
      </div>

      <style jsx="true">{`
        .cleaning-navigation {
          background: white;
          border-bottom: 1px solid var(--gray-200);
          padding: 1rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        
        @media (min-width: 640px) {
          .cleaning-navigation {
            padding: 1.5rem 2rem;
          }
        }

        .nav-container {
          max-width: 1200px;
          margin: 0 auto;
        }

        .nav-steps {
          display: flex;
          gap: 0.5rem;
          overflow-x: auto;
          scrollbar-width: none;
          -ms-overflow-style: none;
          padding: 0.5rem 0;
        }

        .nav-steps::-webkit-scrollbar {
          display: none;
        }

        .nav-step {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 1.5rem;
          border: none;
          border-radius: 12px;
          background: transparent;
          color: var(--gray-600);
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 0.875rem;
          font-weight: 500;
          white-space: nowrap;
          position: relative;
          min-width: fit-content;
        }

        .nav-step:hover {
          background: var(--gray-50);
          color: var(--gray-800);
          transform: translateY(-1px);
        }

        .nav-step.active {
          background: var(--primary-50);
          color: var(--primary-700);
          box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        }

        .step-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: var(--gray-100);
          transition: all 0.3s ease;
        }

        .nav-step.active .step-icon {
          background: var(--primary-100);
          color: var(--primary-600);
        }

        .active-indicator {
          position: absolute;
          bottom: -2px;
          left: 50%;
          transform: translateX(-50%);
          width: 20px;
          height: 3px;
          background: var(--primary-500);
          border-radius: 2px;
        }

        .progress-section {
          background: white;
          border-bottom: 1px solid var(--gray-200);
          padding: 2rem;
        }

        .progress-container {
          max-width: 1200px;
          margin: 0 auto;
        }

        .progress-track {
          display: flex;
          align-items: center;
          gap: 1rem;
          overflow-x: auto;
          scrollbar-width: none;
          -ms-overflow-style: none;
          padding: 1rem 0;
        }

        .progress-track::-webkit-scrollbar {
          display: none;
        }

        .progress-step-wrapper {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-shrink: 0;
        }

        .progress-step {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1.25rem 1.5rem;
          border-radius: 16px;
          background: var(--gray-50);
          border: 2px solid var(--gray-200);
          color: var(--gray-600);
          font-weight: 500;
          font-size: 0.875rem;
          cursor: pointer;
          transition: all 0.3s ease;
          min-width: 200px;
          position: relative;
        }

        .progress-step:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .progress-step.active {
          background: var(--primary-50);
          border-color: var(--primary-300);
          color: var(--primary-700);
          box-shadow: 0 8px 25px rgba(37, 99, 235, 0.15);
        }

        .progress-step.completed {
          background: var(--accent-green);
          border-color: var(--accent-green);
          color: white;
        }

        .step-number {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: var(--gray-400);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 700;
          flex-shrink: 0;
          transition: all 0.3s ease;
        }

        .step-number.active {
          background: var(--primary-600);
          box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        .step-number.completed {
          background: white;
          color: var(--accent-green);
        }

        .step-content {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex: 1;
        }

        .step-content .step-icon {
          color: inherit;
        }

        .step-title {
          font-weight: 600;
          white-space: nowrap;
        }

        .progress-connector {
          width: 3rem;
          height: 2px;
          background: var(--gray-300);
          border-radius: 1px;
          transition: all 0.3s ease;
        }

        .progress-connector.completed {
          background: var(--accent-green);
        }

        .step-content-area {
          min-height: calc(100vh - 300px);
          background: var(--gray-50);
          padding: 2rem;
        }

        @media (max-width: 768px) {
          .cleaning-navigation,
          .progress-section {
            padding: 1rem;
          }

          .nav-step,
          .progress-step {
            padding: 0.75rem 1rem;
            min-width: 160px;
          }

          .step-content {
            flex-direction: column;
            gap: 0.5rem;
            text-align: center;
          }

          .step-title {
            font-size: 0.75rem;
          }
        }
      `}</style>
    </div>
  )
}