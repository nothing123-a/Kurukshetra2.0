
import { useWorkflow } from '../hooks/useWorkflow.js'

export default function WorkflowLayout({ children }) {
  const { currentStep, toasts } = useWorkflow()

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }}>
      {/* Toast Notifications */}
      <div style={{
        position: 'fixed',
        top: '100px',
        right: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        zIndex: 1080
      }}>
        {toasts.map(t => (
          <div key={t.id} style={{
            background: 'white',
            borderLeft: `4px solid ${t.type === 'success' ? '#10b981' : '#ef4444'}`,
            borderRadius: '12px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
            padding: '16px 20px',
            minWidth: '320px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              background: t.type === 'success' ? '#10b981' : '#ef4444',
              fontSize: '14px'
            }}>
              <i className={`fas ${t.type === 'success' ? 'fa-check' : 'fa-exclamation-triangle'}`}></i>
            </div>
            <div style={{
              color: '#374151',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              {t.message}
            </div>
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div style={{ paddingTop: '80px' }}>
        {children}
      </div>
    </div>
  )
}
