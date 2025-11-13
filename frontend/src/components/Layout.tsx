import { ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="app">
      <Sidebar />
      <div className="main-content">
        <Header />
        <main className="content">{children}</main>
      </div>
    </div>
  )
}

export default Layout
