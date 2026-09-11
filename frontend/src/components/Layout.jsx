import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function Layout({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(window.innerWidth <= 1024)
  const location = useLocation()
  const hideSidebar = ['/login', '/register'].includes(location.pathname)

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  return (
    <div className="app-container">
      <Navbar onToggleSidebar={toggleSidebar} />
      <div className="layout-container">
        {!hideSidebar && <Sidebar collapsed={sidebarCollapsed} onClose={() => setSidebarCollapsed(true)} />}
        <main className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          <div className="page-content">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}