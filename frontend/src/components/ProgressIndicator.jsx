export default function ProgressIndicator({ currentStep = 1, totalSteps = 6 }) {
  const steps = [
    { id: 1, title: 'Upload', icon: 'fa-cloud-upload-alt' },
    { id: 2, title: 'Summary', icon: 'fa-chart-bar' },
    { id: 3, title: 'Config', icon: 'fa-cogs' },
    { id: 4, title: 'Outliers', icon: 'fa-exclamation-triangle' },
    { id: 5, title: 'Weights', icon: 'fa-balance-scale' },
    { id: 6, title: 'Results', icon: 'fa-file-alt' }
  ]

  const getStepStatus = (stepId) => {
    if (stepId < currentStep) return 'completed'
    if (stepId === currentStep) return 'current'
    return 'pending'
  }

  return (
    <div className="progress-indicator" style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 16px',
      background: 'rgba(255,255,255,0.9)',
      borderRadius: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#2c3e50' }}>
        Step {currentStep} of {totalSteps}:
      </span>
      
      {steps.map((step, index) => {
        const status = getStepStatus(step.id)
        const isLast = index === steps.length - 1
        
        return (
          <div key={step.id} style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              background: status === 'completed' ? 'var(--success-500)' :
                         status === 'current' ? 'var(--primary-500)' : '#e9ecef',
              color: status === 'pending' ? '#6c757d' : '#fff',
              border: status === 'current' ? '2px solid var(--primary-600)' : 'none'
            }}>
              {status === 'completed' ? (
                <i className="fas fa-check"></i>
              ) : (
                <i className={`fas ${step.icon}`}></i>
              )}
            </div>
            
            {!isLast && (
              <div style={{
                width: '20px',
                height: '2px',
                background: status === 'completed' ? 'var(--success-500)' : '#e9ecef',
                margin: '0 4px'
              }}></div>
            )}
          </div>
        )
      })}
      
      <div style={{
        marginLeft: '12px',
        padding: '4px 8px',
        background: 'var(--gradient-primary)',
        color: '#fff',
        borderRadius: '12px',
        fontSize: '0.75rem',
        fontWeight: 'bold'
      }}>
        {Math.round((currentStep / totalSteps) * 100)}%
      </div>
    </div>
  )
}
