import { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  AlertTriangle, 
  Car, 
  Activity, 
  Clock, 
  CheckCircle, 
  XCircle,
  Bell,
  Calendar,
  TrendingUp,
  RefreshCw
} from 'lucide-react'
import './App.css'

// API base URL from environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [vehicles, setVehicles] = useState([])
  const [alerts, setAlerts] = useState([])
  const [stats, setStats] = useState({
    total_vehicles: 0,
    critical_alerts: 0,
    scheduled_services: 0,
    healthy_vehicles: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    fetchDashboardData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      setError(null)
      
      // Fetch all dashboard data in parallel
      const [statsRes, alertsRes, vehiclesRes] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats`),
        axios.get(`${API_URL}/api/dashboard/alerts?limit=10`),
        axios.get(`${API_URL}/api/dashboard/vehicles?limit=20`)
      ])
      
      setStats(statsRes.data)
      setAlerts(alertsRes.data)
      setVehicles(vehiclesRes.data)
      setLastUpdate(new Date())
      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setError(error.response?.data?.detail || error.message || 'Failed to fetch data')
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#ef4444'
      case 'high': return '#f97316'
      case 'medium': return '#eab308'
      case 'low': return '#3b82f6'
      default: return '#6b7280'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'critical': return '#ef4444'
      case 'warning': return '#f97316'
      case 'healthy': return '#22c55e'
      default: return '#6b7280'
    }
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = Math.floor((now - date) / 1000 / 60) // minutes
    
    if (diff < 60) return `${diff}m ago`
    if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Activity className="loading-spinner" size={48} />
        <p>Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="loading-container">
        <XCircle size={48} style={{ color: '#ef4444' }} />
        <p style={{ color: '#ef4444' }}>Error: {error}</p>
        <button onClick={fetchDashboardData} className="btn-action" style={{ marginTop: '1rem' }}>
          <RefreshCw size={16} style={{ marginRight: '0.5rem' }} />
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Car size={32} />
            <h1>ProActive Mobility Intelligence</h1>
          </div>
          <div className="header-actions">
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginRight: '1rem' }}>
              Last updated: {formatTimestamp(lastUpdate)}
            </span>
            <button onClick={fetchDashboardData} className="btn-secondary" style={{ marginRight: '1rem' }}>
              <RefreshCw size={16} />
            </button>
            <Bell size={24} />
            {stats.critical_alerts > 0 && (
              <span className="badge">{stats.critical_alerts}</span>
            )}
          </div>
        </div>
      </header>

      <main className="main-content">
        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#3b82f6' }}>
              <Car size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Total Vehicles</p>
              <h2 className="stat-value">{stats.total_vehicles}</h2>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#ef4444' }}>
              <AlertTriangle size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Critical Alerts</p>
              <h2 className="stat-value">{stats.critical_alerts}</h2>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#f97316' }}>
              <Calendar size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Scheduled Services</p>
              <h2 className="stat-value">{stats.scheduled_services}</h2>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#22c55e' }}>
              <CheckCircle size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Healthy Vehicles</p>
              <h2 className="stat-value">{stats.healthy_vehicles}</h2>
            </div>
          </div>
        </div>

        {/* Alerts Section */}
        <div className="section">
          <div className="section-header">
            <h2>Active Alerts</h2>
            <button className="btn-secondary">View All</button>
          </div>
          <div className="alerts-list">
            {alerts.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                <CheckCircle size={48} style={{ margin: '0 auto 1rem', color: 'var(--success)' }} />
                <p>No critical alerts at this time</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div 
                  key={alert.id} 
                  className="alert-card" 
                  style={{ borderLeftColor: getSeverityColor(alert.severity) }}
                >
                  <div className="alert-header">
                    <div className="alert-title">
                      <AlertTriangle size={20} style={{ color: getSeverityColor(alert.severity) }} />
                      <span>{alert.vehicle_id}</span>
                    </div>
                    <div className="alert-time">
                      <Clock size={16} />
                      <span>{formatTimestamp(alert.timestamp)}</span>
                    </div>
                  </div>
                  <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>{alert.message}</p>
                  <div className="alert-footer">
                    <span className="alert-vin">VIN: {alert.vin}</span>
                    <span className={`status-badge ${alert.status}`}>
                      {alert.status === 'scheduled' ? (
                        <>
                          <Calendar size={12} />
                          {alert.status}
                        </>
                      ) : (
                        <>
                          <Clock size={12} />
                          {alert.status}
                        </>
                      )}
                    </span>
                  </div>
                  {alert.predicted_component && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Component: {alert.predicted_component.replace('_', ' ').toUpperCase()}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Fleet Status */}
        <div className="section">
          <div className="section-header">
            <h2>Fleet Status</h2>
            <button className="btn-secondary">Manage Fleet</button>
          </div>
          
          {vehicles.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Car size={48} style={{ margin: '0 auto 1rem' }} />
              <p>No vehicles found</p>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vehicle ID</th>
                  <th>VIN</th>
                  <th>Status</th>
                  <th>Health Score</th>
                  <th>Last Reading</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {vehicles.map((vehicle) => (
                  <tr key={vehicle.vehicle_id}>
                    <td>
                      <div className="vehicle-id">
                        <Car size={16} />
                        <span>{vehicle.vehicle_id}</span>
                      </div>
                    </td>
                    <td className="vin-cell">{vehicle.vin}</td>
                    <td>
                      <span className={`status-indicator ${vehicle.status}`}>
                        {vehicle.status === 'critical' && <XCircle size={16} />}
                        {vehicle.status === 'warning' && <AlertTriangle size={16} />}
                        {vehicle.status === 'healthy' && <CheckCircle size={16} />}
                        {vehicle.status}
                      </span>
                    </td>
                    <td>
                      <div className="health-score">
                        <span style={{ minWidth: '50px' }}>{vehicle.health_score}%</span>
                        <div className="health-bar">
                          <div 
                            className="health-fill"
                            style={{ 
                              width: `${vehicle.health_score}%`,
                              backgroundColor: getStatusColor(vehicle.status)
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td>{formatTimestamp(vehicle.last_reading)}</td>
                    <td>
                      <button className="btn-action">View Details</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
