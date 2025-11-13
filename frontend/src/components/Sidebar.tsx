import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

const Sidebar = () => {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Navigation</h2>
      </div>
      <nav className="sidebar-nav">
        <Link to="/" className={`nav-item ${isActive('/') ? 'active' : ''}`}>
          Dashboard
        </Link>
        <Link
          to="/projects"
          className={`nav-item ${isActive('/projects') ? 'active' : ''}`}
        >
          Projects
        </Link>
        <Link
          to="/board"
          className={`nav-item ${isActive('/board') ? 'active' : ''}`}
        >
          Board
        </Link>
        <Link
          to="/issues"
          className={`nav-item ${isActive('/issues') ? 'active' : ''}`}
        >
          Issues
        </Link>
      </nav>
    </aside>
  )
}

export default Sidebar
