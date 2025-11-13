import { useEffect, useState } from 'react'
import { api } from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const [apiStatus, setApiStatus] = useState<string>('checking...')

  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await api.get('/health')
        setApiStatus(`Connected - ${response.data.status}`)
      } catch (error) {
        setApiStatus('Disconnected')
        console.error('API connection error:', error)
      }
    }
    checkApi()
  }, [])

  return (
    <div className="dashboard">
      <h1>Welcome to ScrumFlow</h1>
      <p className="subtitle">
        Lightweight Scrum management for sprint planning and team collaboration
      </p>

      <div className="dashboard-cards">
        <div className="card">
          <h3>Projects</h3>
          <p className="card-value">0</p>
          <p className="card-description">Active projects</p>
        </div>

        <div className="card">
          <h3>Issues</h3>
          <p className="card-value">0</p>
          <p className="card-description">Open issues</p>
        </div>

        <div className="card">
          <h3>API Status</h3>
          <p className="card-value">{apiStatus}</p>
          <p className="card-description">Backend connection</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
