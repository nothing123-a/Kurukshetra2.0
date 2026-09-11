import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { 
  FiUpload, FiBarChart, FiSettings, FiAlertTriangle, 
  FiTarget, FiCheckCircle, FiShield, FiTrendingUp 
} from 'react-icons/fi'
import { RiLightbulbFlashLine } from 'react-icons/ri'
import { HiSparkles } from 'react-icons/hi'
import { BsRobot } from 'react-icons/bs'

const features = [
  {
    icon: FiUpload,
    title: 'Smart Data Upload',
    description: 'Upload CSV, Excel files with automatic format detection',
    color: '#10b981'
  },
  {
    icon: BsRobot,
    title: 'AI-Powered Cleaning',
    description: 'Detect and fix typos, normalize inconsistent labels',
    color: '#3b82f6'
  },
  {
    icon: FiAlertTriangle,
    title: 'Outlier Detection',
    description: 'Advanced algorithms to identify data anomalies',
    color: '#ef4444'
  },
  {
    icon: FiTarget,
    title: 'Missing Value Imputation',
    description: 'Fill gaps with KNN, mean, median methods',
    color: '#8b5cf6'
  },
  {
    icon: RiLightbulbFlashLine,
    title: 'Synthetic Data Generation',
    description: 'Create samples for rare classes and edge cases',
    color: '#f59e0b'
  },
  {
    icon: FiShield,
    title: 'Privacy Preserved',
    description: 'Secure processing with data privacy protection',
    color: '#06b6d4'
  }
]

const stats = [
  { number: '99.9%', label: 'Data Accuracy', icon: FiTrendingUp },
  { number: '10x', label: 'Faster Processing', icon: RiLightbulbFlashLine },
  { number: '100%', label: 'Privacy Protected', icon: FiShield },
  { number: '24/7', label: 'AI Monitoring', icon: BsRobot }
]

export default function Home() {
  return (
    <Layout>
      <div className="fade-in-up" style={{ padding: '20px' }}>
        {/* Hero Section */}
        <div className="main-container" style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{
            background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
            borderRadius: '20px',
            padding: '60px 40px',
            color: 'white',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              opacity: 0.1,
              fontSize: '120px'
            }}>
              <HiSparkles />
            </div>
            
            <div style={{ position: 'relative', zIndex: 1 }}>
              <h1 style={{ 
                fontSize: '3.5rem', 
                fontWeight: '800', 
                margin: '0 0 20px 0',
                textShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                Refinify
              </h1>
              <p style={{ 
                fontSize: '1.5rem', 
                margin: '0 0 30px 0',
                opacity: 0.9,
                fontWeight: '300'
              }}>
                AI-Powered Data Cleaning & Augmentation Pipeline
              </p>
              <p style={{ 
                fontSize: '1.1rem', 
                margin: '0 0 40px 0',
                opacity: 0.8,
                maxWidth: '600px',
                marginLeft: 'auto',
                marginRight: 'auto',
                lineHeight: '1.6'
              }}>
                Transform raw, messy, incomplete data into clean, consistent, and enriched datasets ready for machine learning & business insights
              </p>
              
              <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <Link 
                  to="/upload" 
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '2px solid rgba(255, 255, 255, 0.3)',
                    color: 'white',
                    padding: '16px 32px',
                    borderRadius: '12px',
                    textDecoration: 'none',
                    fontWeight: '600',
                    fontSize: '1.1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'all 0.3s ease',
                    backdropFilter: 'blur(10px)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.3)'
                    e.target.style.transform = 'translateY(-2px)'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.2)'
                    e.target.style.transform = 'translateY(0)'
                  }}
                >
                  <FiUpload size={20} />
                  Start Processing
                </Link>
                
                <button style={{
                  background: 'transparent',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  color: 'white',
                  padding: '16px 32px',
                  borderRadius: '12px',
                  fontWeight: '600',
                  fontSize: '1.1rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.1)'
                  e.target.style.transform = 'translateY(-2px)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'transparent'
                  e.target.style.transform = 'translateY(0)'
                }}>
                  Learn More
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px', 
          marginBottom: '40px' 
        }}>
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div key={index} className="stats-card" style={{
                background: 'linear-gradient(135deg, var(--secondary-color), var(--accent-color))',
                padding: '30px',
                borderRadius: '16px',
                textAlign: 'center',
                color: 'white'
              }}>
                <Icon size={32} style={{ marginBottom: '12px', opacity: 0.9 }} />
                <div className="stats-number" style={{ fontSize: '2.5rem', fontWeight: '800' }}>
                  {stat.number}
                </div>
                <div style={{ fontSize: '1rem', opacity: 0.9 }}>{stat.label}</div>
              </div>
            )
          })}
        </div>

        {/* Features Section */}
        <div className="main-container">
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: '700', 
              margin: '0 0 16px 0',
              background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Powerful AI Features
            </h2>
            <p style={{ 
              fontSize: '1.2rem', 
              color: '#64748b', 
              margin: 0,
              maxWidth: '600px',
              marginLeft: 'auto',
              marginRight: 'auto'
            }}>
              Advanced algorithms and AI techniques to ensure your data is clean, consistent, and ready for analysis
            </p>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '24px' 
          }}>
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="feature-card">
                  <Icon 
                    className="feature-icon" 
                    style={{ 
                      fontSize: '3rem', 
                      color: feature.color,
                      marginBottom: '16px'
                    }} 
                  />
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* CTA Section */}
        <div className="main-container" style={{ 
          textAlign: 'center',
          background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)',
          border: '1px solid #e2e8f0'
        }}>
          <h2 style={{ 
            fontSize: '2rem', 
            fontWeight: '700', 
            margin: '0 0 16px 0',
            color: 'var(--text-color)'
          }}>
            Ready to Transform Your Data?
          </h2>
          <p style={{ 
            fontSize: '1.1rem', 
            color: '#64748b', 
            margin: '0 0 32px 0',
            maxWidth: '500px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            Start your AI-powered data cleaning journey today. Upload your dataset and see the magic happen.
          </p>
          
          <Link 
            to="/upload" 
            className="btn-primary"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '1.1rem',
              padding: '16px 32px',
              textDecoration: 'none'
            }}
          >
            <FiUpload size={20} />
            Get Started Now
          </Link>
        </div>
      </div>
    </Layout>
  )
}