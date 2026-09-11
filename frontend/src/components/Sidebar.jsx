import { useState, useEffect, useContext } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  FiHome, FiEdit3, FiTrendingUp, FiClock, FiShield, FiX
} from 'react-icons/fi'
import { BsRobot } from 'react-icons/bs'
import { AuthContext } from '../context/AuthContext'

const getMenuSections = () => {
  return [
    {
      title: 'Platform Core',
      items: [
        { path: '/', icon: FiHome, label: 'Dashboard' },
        { path: '/ai-assistant', icon: BsRobot, label: 'AI Data Agent' }
      ]
    },
    {
      title: 'Data & Analytics',
      items: [
        { path: '/data-cleaning', icon: FiEdit3, label: 'Data Cleaning' },
        { path: '/analytics', icon: FiTrendingUp, label: 'Analytics & Charts' },
        { path: '/history', icon: FiClock, label: 'Analysis History' },
        { path: '/privacy-protection', icon: FiShield, label: 'Privacy & Security' }
      ]
    }
  ]
}

export default function Sidebar({ collapsed, onClose }) {
  const location = useLocation()
  const [isMobile, setIsMobile] = useState(false)
  const { user } = useContext(AuthContext)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 1024)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true
    if (path !== '/' && location.pathname.startsWith(path)) return true
    return false
  }

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Mobile close button */}
      {isMobile && !collapsed && (
        <div className="flex justify-end p-2 border-b border-[#E8DCC8]">
          <button
            onClick={onClose}
            className="p-1.5 text-[#5D504F] hover:text-[#2D2424] hover:bg-[#FAF7F0] rounded-lg transition"
            title="Close sidebar"
          >
            <FiX className="w-5 h-5" />
          </button>
        </div>
      )}

      <div className="py-3">
        {getMenuSections().map((section, sectionIndex) => (
          <div key={sectionIndex} className="sidebar-section">
            <div className="sidebar-title">{section.title}</div>
            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isActive(item.path)
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`sidebar-link ${active ? 'active' : ''}`}
                    onClick={() => {
                      if (isMobile && onClose) {
                        onClose()
                      }
                    }}
                  >
                    <Icon className="sidebar-icon" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}