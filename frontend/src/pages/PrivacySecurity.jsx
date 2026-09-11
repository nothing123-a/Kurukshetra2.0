import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkflow } from '../hooks/useWorkflow.js'
import WorkflowLayout from '../components/WorkflowLayout.jsx'
import { FiShield, FiLock, FiEye, FiEyeOff, FiArrowRight, FiAlertTriangle } from 'react-icons/fi'
import { BsShieldCheck } from 'react-icons/bs'

export default function PrivacySecurity() {
  const { summary, config, setConfig, nextStep } = useWorkflow()
  const navigate = useNavigate()
  const [selectedColumns, setSelectedColumns] = useState([])
  const [loading, setLoading] = useState(false)

  const availableColumns = summary?.column_names || []

  useEffect(() => {
    // Auto-detect sensitive columns
    const sensitiveColumns = availableColumns.filter(col => {
      const colLower = col.toLowerCase()
      return ['name', 'email', 'phone', 'address', 'ssn', 'id', 'account', 'card'].some(keyword => 
        colLower.includes(keyword)
      )
    })
    setSelectedColumns(sensitiveColumns)
    
    // Update config with detected columns
    setConfig(c => ({
      ...c,
      privacy: {
        ...c.privacy,
        enabled: sensitiveColumns.length > 0,
        columns: sensitiveColumns,
        method: 'hash'
      }
    }))
  }, [availableColumns, setConfig])

  const handleColumnToggle = (column) => {
    const newSelected = selectedColumns.includes(column)
      ? selectedColumns.filter(col => col !== column)
      : [...selectedColumns, column]
    
    setSelectedColumns(newSelected)
    setConfig(c => ({
      ...c,
      privacy: {
        ...c.privacy,
        columns: newSelected,
        enabled: newSelected.length > 0
      }
    }))
  }

  const handleContinue = () => {
    nextStep()
    navigate('/outliers')
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
          background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
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
            <BsShieldCheck />
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <FiShield style={{ fontSize: '3rem' }} />
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: '800',
              margin: 0
            }}>
              Privacy & Security
            </h1>
          </div>
          <p style={{
            fontSize: '1.2rem',
            opacity: 0.9,
            margin: 0
          }}>
            Protect sensitive data with enterprise-grade privacy controls
          </p>
        </div>

        {/* Privacy Settings */}
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
            <FiLock style={{ color: '#dc2626' }} />
            Privacy Protection Settings
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '1.5rem',
            marginBottom: '2rem'
          }}>
            <div style={{
              background: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '16px',
              padding: '1.5rem'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '0.75rem',
                fontSize: '1rem'
              }}>
                Enable Privacy Protection
              </label>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                marginBottom: '0.75rem'
              }}>
                <input
                  type="checkbox"
                  id="enablePrivacy"
                  checked={config.privacy?.enabled || false}
                  onChange={(e) => setConfig(c => ({
                    ...c,
                    privacy: { ...c.privacy, enabled: e.target.checked }
                  }))}
                  style={{
                    width: '20px',
                    height: '20px',
                    accentColor: '#dc2626'
                  }}
                />
                <label htmlFor="enablePrivacy" style={{
                  color: '#6b7280',
                  fontSize: '0.95rem'
                }}>
                  Apply privacy protection to selected columns
                </label>
              </div>
              <p style={{
                color: '#6b7280',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                margin: 0
              }}>
                Automatically detected {selectedColumns.length} potentially sensitive columns
              </p>
            </div>

            <div style={{
              background: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '16px',
              padding: '1.5rem'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '0.75rem',
                fontSize: '1rem'
              }}>
                Protection Method
              </label>
              <select 
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  border: '2px solid #fecaca',
                  borderRadius: '12px',
                  background: 'white',
                  color: '#374151',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.3s ease',
                  marginBottom: '0.75rem'
                }}
                value={config.privacy?.method || 'hash'}
                onChange={(e) => setConfig(c => ({
                  ...c,
                  privacy: { ...c.privacy, method: e.target.value }
                }))}
                disabled={!config.privacy?.enabled}
              >
                <option value="hash">Hash Encryption (Recommended)</option>
                <option value="mask">Partial Masking</option>
                <option value="remove">Remove Columns</option>
              </select>
              <p style={{
                color: '#6b7280',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                margin: 0
              }}>
                Hash encryption provides the strongest protection while preserving data utility
              </p>
            </div>
          </div>

          {/* Column Selection */}
          {availableColumns.length > 0 && (
            <div>
              <h4 style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <FiEye />
                Select Columns to Protect
              </h4>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: '0.75rem',
                marginBottom: '1rem'
              }}>
                {availableColumns.map((column) => {
                  const isSelected = selectedColumns.includes(column)
                  const isSensitive = ['name', 'email', 'phone', 'address', 'ssn', 'id', 'account', 'card']
                    .some(keyword => column.toLowerCase().includes(keyword))
                  
                  return (
                    <div
                      key={column}
                      onClick={() => handleColumnToggle(column)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.75rem',
                        background: isSelected ? '#fef2f2' : '#f9fafb',
                        border: `2px solid ${isSelected ? '#fecaca' : '#e5e7eb'}`,
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = isSelected ? '#fecaca' : '#f3f4f6'
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = isSelected ? '#fef2f2' : '#f9fafb'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                        style={{
                          accentColor: '#dc2626'
                        }}
                      />
                      <span style={{
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        color: '#374151'
                      }}>
                        {column}
                      </span>
                      {isSensitive && (
                        <FiAlertTriangle 
                          size={14} 
                          style={{ color: '#f59e0b' }}
                          title="Potentially sensitive column"
                        />
                      )}
                    </div>
                  )
                })}
              </div>
              
              <p style={{
                color: '#6b7280',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                margin: 0
              }}>
                Selected {selectedColumns.length} of {availableColumns.length} columns for privacy protection.
                Columns with ⚠️ are automatically detected as potentially sensitive.
              </p>
            </div>
          )}
        </div>

        {/* Security Features */}
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
            <BsShieldCheck style={{ color: '#dc2626' }} />
            Security Features
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem'
          }}>
            {[
              { title: 'PBKDF2 Encryption', desc: 'Industry-standard encryption with salt for maximum security' },
              { title: 'Automatic Detection', desc: 'AI-powered detection of sensitive data patterns' },
              { title: 'Compliance Ready', desc: 'Meets GDPR, HIPAA, and other privacy regulations' },
              { title: 'Audit Trail', desc: 'Complete logging of all privacy protection actions' }
            ].map((feature, index) => (
              <div key={index} style={{
                background: '#fef2f2',
                padding: '1rem',
                borderRadius: '12px',
                border: '1px solid #fecaca'
              }}>
                <h4 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: '#374151',
                  margin: '0 0 0.5rem 0'
                }}>
                  {feature.title}
                </h4>
                <p style={{
                  color: '#6b7280',
                  fontSize: '0.875rem',
                  margin: 0,
                  lineHeight: '1.4'
                }}>
                  {feature.desc}
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
              background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(220, 38, 38, 0.4)',
              opacity: loading ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)'
                e.target.style.boxShadow = '0 8px 25px rgba(220, 38, 38, 0.6)'
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 4px 15px rgba(220, 38, 38, 0.4)'
              }
            }}
          >
            {loading ? 'Processing...' : 'Continue to Outlier Detection'}
            <FiArrowRight size={20} />
          </button>
        </div>
      </div>
    </WorkflowLayout>
  )
}