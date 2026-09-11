import { useState, useEffect, useContext } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { 
  FiMenu, FiUser, FiLogOut, FiLogIn, FiUserPlus, FiSettings,
  FiActivity, FiGlobe, FiDatabase, FiBarChart, FiTrendingUp, FiUsers, FiCalendar, FiHeart
} from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'
import { BsRobot } from 'react-icons/bs'
import { API_BASE_URL } from '../config'
import { AuthContext } from '../context/AuthContext'

export default function Navbar({ onToggleSidebar }) {
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user: authUser } = useContext(AuthContext)

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        credentials: 'include'
      })
      const data = await response.json()
      
      if (data.is_authenticated && data.user) {
        setIsAuthenticated(true)
        setUser(data.user)
      } else {
        setIsAuthenticated(false)
        setUser(null)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      setIsAuthenticated(false)
      setUser(null)
    }
  }

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
      setIsAuthenticated(false)
      setUser(null)
      setShowUserMenu(false)
      navigate('/')
      window.location.reload()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }



  // Get user initials for avatar
  const getUserInitials = (user) => {
    if (!user || !user.username) return 'U'
    return user.username.charAt(0).toUpperCase()
  }

  return (
    <nav className="navbar">
      {/* Left Section - Brand and Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Sidebar Toggle Button */}
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              border: '1px solid #E8DCC8',
              background: '#FAF7F0',
              color: '#5D504F',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            title="Toggle Sidebar"
            aria-label="Toggle Sidebar"
          >
            <FiMenu size={18} />
          </button>
        )}

        {/* Brand */}
        <Link to="/" className="navbar-brand">
          <div style={{
            width: '40px',
            height: '40px',
            background: 'var(--gradient-primary)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)'
          }}>
            <BsRobot style={{ color: 'white', fontSize: '20px' }} />
          </div>
          <span style={{ fontWeight: '700', letterSpacing: '-0.02em' }}>Bhishma's AI</span>
        </Link>

        {/* Navigation Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: location.pathname === '/' ? 'var(--primary-600)' : 'var(--text-secondary)',
            textDecoration: 'none',
            fontWeight: '600',
            padding: '0.5rem 0.8rem',
            borderRadius: '8px',
            transition: 'all 0.2s ease'
          }}>
            Dashboard
          </Link>
          <Link to="/ai-assistant" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: location.pathname === '/ai-assistant' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(59, 130, 246, 0.08)',
            color: 'var(--primary-600)',
            textDecoration: 'none',
            fontWeight: '700',
            padding: '0.5rem 1rem',
            borderRadius: '10px',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            transition: 'all 0.2s ease'
          }}>
            <HiSparkles style={{ color: '#F59E0B' }} />
            AI Agent
          </Link>
          <Link to="/data-cleaning" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: location.pathname === '/data-cleaning' || location.pathname === '/trial-data' ? 'var(--primary-600)' : 'var(--text-secondary)',
            textDecoration: 'none',
            fontWeight: '500',
            padding: '0.5rem 0.8rem',
            borderRadius: '8px',
            transition: 'all 0.2s ease'
          }}>
            Clean Data
          </Link>
          <Link to="/outliers" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: location.pathname === '/outliers' ? 'var(--primary-600)' : 'var(--text-secondary)',
            textDecoration: 'none',
            fontWeight: '500',
            padding: '0.5rem 0.8rem',
            borderRadius: '8px',
            transition: 'all 0.2s ease'
          }}>
            Anomalies
          </Link>
          <Link to="/analytics" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: location.pathname === '/analytics' ? 'var(--primary-600)' : 'var(--text-secondary)',
            textDecoration: 'none',
            fontWeight: '500',
            padding: '0.5rem 0.8rem',
            borderRadius: '8px',
            transition: 'all 0.2s ease'
          }}>
            <FiTrendingUp size={16} />
            Analytics
          </Link>
          <Link to="/results" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: location.pathname === '/results' ? 'var(--primary-600)' : 'var(--text-secondary)',
            textDecoration: 'none',
            fontWeight: '500',
            padding: '0.5rem 0.8rem',
            borderRadius: '8px',
            transition: 'all 0.2s ease'
          }}>
            Reports
          </Link>
        </div>
      </div>



      {/* Right Section - Authentication */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {isAuthenticated && user ? (
          // Authenticated User Menu
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                background: 'white',
                border: '2px solid var(--primary-300)',
                borderRadius: '12px',
                padding: '0.5rem 1rem',
                color: 'var(--primary-700)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'var(--gradient-primary)'
                e.target.style.color = 'white'
                e.target.style.borderColor = 'var(--primary-600)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'white'
                e.target.style.color = 'var(--primary-700)'
                e.target.style.borderColor = 'var(--primary-300)'
              }}
            >
              {/* User Avatar */}
              <div style={{
                width: '32px',
                height: '32px',
                background: 'var(--gradient-primary)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '0.8rem',
                fontWeight: '700'
              }}>
                {user.profile_image ? (
                  <img 
                    src={`${API_BASE_URL}${user.profile_image}`} 
                    alt="Profile"
                    style={{
                      width: '100%',
                      height: '100%',
                      borderRadius: '50%',
                      objectFit: 'cover'
                    }}
                  />
                ) : (
                  getUserInitials(user)
                )}
              </div>
              <span>{user.username}</span>
            </button>
            
            {showUserMenu && (
              <div style={{
                position: 'absolute',
                top: '60px',
                right: 0,
                background: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '16px',
                minWidth: '220px',
                overflow: 'hidden',
                zIndex: 1001,
                boxShadow: '0 20px 40px rgba(18, 17, 17, 0.25)'
              }}>
                {/* User Info Header */}
                <div style={{
                  padding: '16px 20px',
                  borderBottom: '1px solid #e5e7eb',
                  background: '#f9fafb'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      background: 'var(--gradient-primary)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '1rem',
                      fontWeight: '700'
                    }}>
                      {user.profile_image ? (
                        <img 
                          src={`${API_BASE_URL}${user.profile_image}`} 
                          alt="Profile"
                          style={{
                            width: '100%',
                            height: '100%',
                            borderRadius: '50%',
                            objectFit: 'cover'
                          }}
                        />
                      ) : (
                        getUserInitials(user)
                      )}
                    </div>
                    <div>
                      <div style={{
                        fontWeight: '600',
                        color: 'var(--text-primary)',
                        fontSize: '0.9rem'
                      }}>
                        {user.username}
                      </div>
                      {user.email && (
                        <div style={{
                          color: 'var(--text-muted)',
                          fontSize: '0.8rem'
                        }}>
                          {user.email}
                        </div>
                      )}
                      {user.role && (
                        <div style={{
                          display: 'inline-block',
                          background: user.role === 'admin' ? 'var(--gradient-gold)' : 'var(--primary-100)',
                          color: user.role === 'admin' ? 'white' : 'var(--primary-700)',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '0.7rem',
                          fontWeight: '600',
                          marginTop: '4px'
                        }}>
                          {user.role.toUpperCase()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <Link
                  to="/profile"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '16px 20px',
                    textDecoration: 'none',
                    color: 'var(--text-secondary)',
                    transition: 'all 0.3s ease',
                    borderBottom: '1px solid var(--gray-200)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = 'var(--gray-100)'
                    e.target.style.color = 'var(--text-primary)'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'transparent'
                    e.target.style.color = 'var(--text-secondary)'
                  }}
                  onClick={() => setShowUserMenu(false)}
                >
                  <FiUser size={16} />
                  Profile Settings
                </Link>

                <Link
                  to="/admin"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '16px 20px',
                    textDecoration: 'none',
                    color: 'var(--text-secondary)',
                    transition: 'all 0.3s ease',
                    borderBottom: '1px solid var(--gray-200)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = '#3b82f6'
                    e.target.style.color = 'white'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'transparent'
                    e.target.style.color = 'var(--text-secondary)'
                  }}
                  onClick={() => setShowUserMenu(false)}
                >
                  <FiSettings size={16} />
                  Admin Panel
                </Link>
                
                <button
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '16px 20px',
                    width: '100%',
                    border: 'none',
                    background: 'transparent',
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = '#fef2f2'
                    e.target.style.color = '#ef4444'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'transparent'
                    e.target.style.color = 'var(--text-secondary)'
                  }}
                  onClick={handleLogout}
                >
                  <FiLogOut size={16} />
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          // Not Authenticated - Login/Register Buttons
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Link
              to="/login"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                color: 'var(--primary-700)',
                textDecoration: 'none',
                borderRadius: '12px',
                transition: 'all 0.3s ease',
                fontWeight: '500',
                border: '2px solid var(--primary-300)',
                background: 'transparent'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'var(--gradient-primary)'
                e.target.style.color = 'white'
                e.target.style.borderColor = 'var(--primary-600)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'transparent'
                e.target.style.color = 'var(--primary-700)'
                e.target.style.borderColor = 'var(--primary-300)'
              }}
            >
              <FiLogIn size={16} />
              Login
            </Link>
            
            <Link
              to="/register"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                background: 'var(--gradient-primary)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '12px',
                transition: 'all 0.3s ease',
                fontWeight: '500',
                boxShadow: '0 2px 10px rgba(59, 130, 246, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-1px)'
                e.target.style.boxShadow = '0 4px 15px rgba(59, 130, 246, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 2px 10px rgba(59, 130, 246, 0.3)'
              }}
            >
              <FiUserPlus size={16} />
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </nav>
  )
}