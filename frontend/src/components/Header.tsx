import './Header.css'

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <h1>ScrumFlow</h1>
        <div className="header-actions">
          <button className="btn-secondary">Profile</button>
        </div>
      </div>
    </header>
  )
}

export default Header
