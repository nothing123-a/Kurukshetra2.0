import { useWorkflow } from '../hooks/useWorkflow.js'
import { useNavigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { FiCheck, FiArrowRight } from 'react-icons/fi'
import './WorkflowSteps.css'

export default function WorkflowSteps() {
  const { currentStep, goToStep, setCurrentStep } = useWorkflow()
  const navigate = useNavigate()
  const location = useLocation()

  const steps = [
    { id: 1, title: 'Data Summary', path: '/summary', icon: '📊' },
    { id: 2, title: 'Configuration', path: '/configuration', icon: '⚙️' },
    { id: 3, title: 'Outlier Detection', path: '/outliers', icon: '🔍' },
    { id: 4, title: 'Weights & Estimation', path: '/weights', icon: '⚖️' },
    { id: 5, title: 'Results & Reports', path: '/results', icon: '📈' }
  ]

  // Sync current step with current route
  useEffect(() => {
    const currentPath = location.pathname
    const currentStepIndex = steps.findIndex(step => step.path === currentPath)
    if (currentStepIndex !== -1 && currentStepIndex + 1 !== currentStep) {
      setCurrentStep(currentStepIndex + 1)
    }
  }, [location.pathname, currentStep, setCurrentStep, steps])

  const handleStepClick = (stepId, path) => {
    if (stepId <= currentStep) {
      goToStep(stepId)
      navigate(path)
    }
  }

  return (
    // <div 
    //   className="workflow-steps1"
    //   style={{ '--current-step': currentStep }}
    // >
    //   <div className="steps-container">
    //     {steps.map((step, index) => {
    //       const isActive = step.id === currentStep
    //       const isCompleted = step.id < currentStep
    //       const isClickable = step.id <= currentStep

    //       return (
    //         <div key={step.id} className="step-item">
    //           {/* Step Circle */}
    //           <div 
    //             className={`step-circle ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
    //             onClick={() => handleStepClick(step.id, step.path)}
    //             style={{ cursor: isClickable ? 'pointer' : 'default' }}
    //           >
    //             {isCompleted ? (
    //               <FiCheck size={16} />
    //             ) : (
    //               <span className="step-number">{step.id}</span>
    //             )}
    //             <span className="step-icon">{step.icon}</span>
    //           </div>

    //           {/* Step Title */}
    //           <div className="step-title">
    //             <span className={`title-text ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
    //               {step.title}
    //             </span>
    //           </div>

    //           {/* Connector Line */}
    //           {index < steps.length - 1 && (
    //             <div className={`step-connector ${isCompleted ? 'completed' : ''}`}>
    //               <FiArrowRight size={12} />
    //             </div>
    //           )}
    //         </div>
    //       )
    //     })}
    //   </div>
    // </div>
    <div></div>
  )
}
