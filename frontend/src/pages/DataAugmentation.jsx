import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import { FiDatabase, FiTrendingUp, FiArrowRight, FiShield, FiZap } from 'react-icons/fi'
import { BsRobot } from 'react-icons/bs'

export default function DataAugmentation() {
  const { config, setConfig, nextStep } = useWorkflow()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const handleContinue = () => {
    nextStep()
    navigate('/privacy-security')
  }

  return (
    <WorkflowLayout>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '2rem'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '24px',
          padding: '3rem',
          textAlign: 'center',
          color: 'white',
          marginBottom: '2rem',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            opacity: 0.1,
            fontSize: '8rem'
          }}>
            <BsRobot />
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <FiZap style={{ fontSize: '3rem' }} />
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: '800',
              margin: 0
            }}>
              Data Augmentation
            </h1>
          </div>
          <p style={{
            fontSize: '1.2rem',
            opacity: 0.9,
            margin: 0
          }}>
            Enhance your dataset with AI-powered synthetic data generation
          </p>
        </div>

        {/* Augmentation Options */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '2rem',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
          border: '1px solid #e5e7eb',
          marginBottom: '2rem'
        }}>
          <h3 style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#1f2937',
            marginBottom: '1.5rem',
            paddingBottom: '1rem',
            borderBottom: '2px solid #f3f4f6'
          }}>
            <FiTrendingUp style={{ color: '#667eea' }} />
            Augmentation Settings
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '1.5rem'
          }}>
            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '1.5rem',
              transition: 'all 0.3s ease'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '0.75rem',
                fontSize: '1rem'
              }}>
                Enable Data Augmentation
              </label>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                marginBottom: '0.75rem'
              }}>
                <input
                  type="checkbox"
                  id="enableAugmentation"
                  checked={config.augmentation?.enabled || false}
                  onChange={(e) => setConfig(c => ({
                    ...c,
                    augmentation: { ...c.augmentation, enabled: e.target.checked }
                  }))}
                  style={{
                    width: '20px',
                    height: '20px',
                    accentColor: '#667eea'
                  }}
                />
                <label htmlFor="enableAugmentation" style={{
                  color: '#6b7280',
                  fontSize: '0.95rem'
                }}>
                  Generate synthetic data to balance your dataset
                </label>
              </div>
              <p style={{
                color: '#6b7280',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                margin: 0
              }}>
                Uses AI algorithms like SMOTE and clustering to create realistic synthetic samples
              </p>
            </div>

            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '1.5rem',
              transition: 'all 0.3s ease'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '0.75rem',
                fontSize: '1rem'
              }}>
                Augmentation Method
              </label>
              <select 
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  border: '2px solid #d1d5db',
                  borderRadius: '12px',
                  background: 'white',
                  color: '#374151',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.3s ease',
                  marginBottom: '0.75rem'
                }}
                value={config.augmentation?.method || 'smote'}
                onChange={(e) => setConfig(c => ({
                  ...c,
                  augmentation: { ...c.augmentation, method: e.target.value }
                }))}
                disabled={!config.augmentation?.enabled}
              >
                <option value="smote">SMOTE (Recommended)</option>
                <option value="basic">Basic Augmentation</option>
                <option value="advanced">Advanced SMOTE</option>
                <option value="ensemble">Ensemble Methods</option>
              </select>
              <p style={{
                color: '#6b7280',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                margin: 0
              }}>
                Choose the augmentation technique based on your data characteristics
              </p>
            </div>

            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '1.5rem',
              transition: 'all 0.3s ease'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '0.75rem',
                fontSize: '1rem'
              }}>
                Target Balance Ratio
              </label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={config.augmentation?.balanceRatio || 0.5}
                onChange={(e) => setConfig(c => ({
                  ...c,
                  augmentation: { ...c.augmentation, balanceRatio: parseFloat(e.target.value) }
                }))}
                disabled={!config.augmentation?.enabled}
                style={{
                  width: '100%',
                  marginBottom: '0.5rem',
                  accentColor: '#667eea'
                }}
              />
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.875rem',
                color: '#6b7280',
                marginBottom: '0.75rem'
              }}>
                <span>Conservative</span>
                <span>{((config.augmentation?.balanceRatio || 0.5) * 100).toFixed(0)}%</span>
                <span>Aggressive</span>
              </div>
              <p style={{
                color: '#6b7280',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                margin: 0
              }}>
                Controls how much synthetic data to generate relative to minority classes
              </p>
            </div>
          </div>
        </div>

        {/* Benefits Section */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '2rem',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
          border: '1px solid #e5e7eb',
          marginBottom: '2rem'
        }}>
          <h3 style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#1f2937',
            marginBottom: '1.5rem'
          }}>
            <FiDatabase style={{ color: '#667eea' }} />
            Augmentation Benefits
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem'
          }}>
            {[
              { title: 'Balance Classes', desc: 'Automatically detect and balance minority classes in your dataset' },
              { title: 'Improve ML Performance', desc: 'Better model training with balanced, representative data' },
              { title: 'Preserve Patterns', desc: 'Synthetic data maintains statistical relationships from original data' },
              { title: 'Privacy Safe', desc: 'Generated data doesn\'t expose individual records from original dataset' }
            ].map((benefit, index) => (
              <div key={index} style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '12px',
                border: '1px solid #e2e8f0'
              }}>
                <h4 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: '#374151',
                  margin: '0 0 0.5rem 0'
                }}>
                  {benefit.title}
                </h4>
                <p style={{
                  color: '#6b7280',
                  fontSize: '0.875rem',
                  margin: 0,
                  lineHeight: '1.4'
                }}>
                  {benefit.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Continue Button */}
        <div style={{
          textAlign: 'center',
          marginTop: '3rem'
        }}>
          <button
            onClick={handleContinue}
            disabled={loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '12px',
              padding: '1rem 2rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
              opacity: loading ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)'
                e.target.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.6)'
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)'
              }
            }}
          >
            {loading ? 'Processing...' : 'Continue to Privacy & Security'}
            <FiArrowRight size={20} />
          </button>
        </div>
      </div>
    </WorkflowLayout>
  )
}