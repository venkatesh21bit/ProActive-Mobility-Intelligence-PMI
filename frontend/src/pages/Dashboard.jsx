import { useState, useEffect } from 'react';
import { RefreshCw, AlertTriangle, Activity, Send, TrendingUp, Zap, Bell, Car } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getDashboardStats, getDashboardAlerts, getDashboardVehicles, getRecentPredictions, getAgentStatus } from '../utils/api';

export default function Dashboard() {
  const [stats, setStats] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [agentActivity, setAgentActivity] = useState([]);

  useEffect(() => {
    fetchDashboardData();
    fetchAgentActivity();
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchAgentActivity();
    }, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, alertsRes, vehiclesRes, predictionsRes] = await Promise.all([
        getDashboardStats(),
        getDashboardAlerts(),
        getDashboardVehicles(),
        getRecentPredictions()
      ]);
      setStats(statsRes.data);
      setAlerts(alertsRes.data || []);
      setVehicles(vehiclesRes.data || []);
      setPredictions(predictionsRes.data || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentActivity = async () => {
    try {
      const response = await getAgentStatus();
      // Transform backend agent data for dashboard display
      const iconMap = {
        'Data Ingestion Agent': Activity,
        'ML Prediction Agent': TrendingUp,
        'Alert Manager': AlertTriangle,
        'Notification Agent': Bell,
        'Scheduler Agent': Car,
        'Analytics Agent': Zap
      };
      
      const activities = response.data.agents.map(agent => ({
        agent: agent.name,
        action: agent.description,
        status: agent.status,
        icon: iconMap[agent.name] || Activity
      }));
      setAgentActivity(activities);
    } catch (error) {
      console.error('Error fetching agent activity:', error);
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        <RefreshCw size={48} className="spinning" />
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-page" style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Professional Header Banner */}
      <div style={{ 
        background: 'linear-gradient(135deg, #991b1b 0%, #dc2626 50%, #991b1b 100%)',
        borderRadius: '1rem',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 10px 40px rgba(220, 38, 38, 0.3)',
        border: '1px solid rgba(220, 38, 38, 0.5)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '2.5rem', fontWeight: '700', color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}>Service Center Dashboard</h1>
            <p style={{ color: 'rgba(255, 255, 255, 0.9)', marginTop: '0.5rem', fontSize: '1.1rem', fontWeight: '500' }}>Hero MotoCorp Predictive Maintenance System</p>
            <p style={{ color: 'rgba(255, 255, 255, 0.75)', marginTop: '0.25rem', fontSize: '0.875rem' }}>Real-time AI-powered fleet monitoring and service scheduling</p>
          </div>
          <button onClick={fetchDashboardData} style={{ 
            padding: '0.875rem 1.75rem', 
            background: 'rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)',
            color: '#fff', 
            border: '2px solid rgba(255, 255, 255, 0.3)', 
            borderRadius: '0.75rem', 
            cursor: 'pointer', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem',
            fontWeight: '600',
            fontSize: '1rem',
            transition: 'all 0.3s',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.3)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
          }}>
            <RefreshCw size={18} />
            Refresh Data
          </button>
        </div>
      </div>

      {/* Live Agent Activity */}
      <div style={{ background: 'linear-gradient(135deg, #991b1b 0%, #dc2626 100%)', borderRadius: '1rem', padding: '2rem', marginBottom: '2rem', color: '#fff', border: '2px solid #ef4444' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <AlertTriangle size={28} />
          <h2 style={{ margin: 0, fontSize: '1.5rem' }}>Live Agent Activity</h2>
          <span style={{ marginLeft: 'auto', background: 'rgba(239, 68, 68, 0.3)', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '600', border: '1px solid rgba(239, 68, 68, 0.5)' }}>
            <span style={{ display: 'inline-block', width: '8px', height: '8px', background: '#ef4444', borderRadius: '50%', marginRight: '0.5rem' }}></span>
            Systems Disabled - Billing Issue
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {agentActivity.length > 0 ? agentActivity.map((activity, idx) => {
            const Icon = activity.icon;
            return (
              <div key={idx} style={{ background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)', borderRadius: '0.75rem', padding: '1rem', border: '1px solid rgba(239, 68, 68, 0.3)', opacity: 0.6 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <Icon size={20} />
                  <span style={{ fontWeight: '600', fontSize: '0.9375rem' }}>{activity.agent}</span>
                </div>
                <p style={{ margin: 0, fontSize: '0.875rem', opacity: 0.9 }}>{activity.action}</p>
                <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ width: '6px', height: '6px', background: '#ef4444', borderRadius: '50%' }}></div>
                  Disabled
                </div>
              </div>
            );
          }) : (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '0.75rem' }}>
              <AlertTriangle size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>No Recent Alerts</p>
              <p style={{ fontSize: '0.875rem', opacity: 0.8 }}>All systems are operating normally.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="stat-card" style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#9ca3af' }}>Total Vehicles</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fff', margin: 0 }}>{stats.total_vehicles || 0}</p>
        </div>
        <div className="stat-card" style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#9ca3af' }}>Critical Alerts</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444', margin: 0 }}>{stats.critical_alerts || 0}</p>
        </div>
        <div className="stat-card" style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#9ca3af' }}>Pending Appointments</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b', margin: 0 }}>{stats.pending_appointments || 0}</p>
        </div>
        <div className="stat-card" style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#9ca3af' }}>Avg Health Score</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#22c55e', margin: 0 }}>{stats.avg_health_score || '0.0'}</p>
        </div>
      </div>

      {/* Alerts */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ margin: 0 }}>🚨 Recent Critical Alerts</h2>
          <Link to="/alerts" style={{ color: '#6366f1', textDecoration: 'none', fontSize: '0.9375rem' }}>View All →</Link>
        </div>
        <div style={{ background: '#1e293b', borderRadius: '0.75rem', padding: '1rem', border: '1px solid #2d3748' }}>
          {alerts && alerts.length > 0 ? (
            alerts.slice(0, 5).map((alert, idx) => (
              <div key={idx} style={{ padding: '1rem', borderBottom: idx < 4 ? '1px solid #2d3748' : 'none', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ 
                  width: '48px', 
                  height: '48px', 
                  borderRadius: '0.75rem', 
                  background: alert.severity === 'Critical' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                  border: `1px solid ${alert.severity === 'Critical' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <AlertTriangle size={24} color={alert.severity === 'Critical' ? '#ef4444' : '#f59e0b'} />
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ margin: 0, color: '#fff', fontWeight: '600', fontSize: '1rem' }}>
                    {alert.component || 'Component'} Failure Predicted
                  </p>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#9ca3af' }}>
                    Vehicle: {alert.vin || 'Unknown'} | 
                    Probability: {alert.failure_probability != null ? (alert.failure_probability * 100).toFixed(1) : 'N/A'}% | 
                    Severity: <span style={{ color: alert.severity === 'Critical' ? '#ef4444' : '#f59e0b' }}>{alert.severity || 'Unknown'}</span>
                  </p>
                </div>
                <Link to="/notifications" style={{ textDecoration: 'none' }}>
                  <button style={{ 
                    background: '#6366f1', 
                    color: '#fff', 
                    border: 'none', 
                    padding: '0.5rem 1rem', 
                    borderRadius: '0.5rem', 
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontSize: '0.875rem'
                  }}>
                    <Send size={14} />
                    Send Alert
                  </button>
                </Link>
              </div>
            ))
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
              <AlertTriangle size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>No critical alerts at this time</p>
            </div>
          )}
        </div>
      </div>

      {/* Vehicles */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ margin: 0 }}>🚗 Fleet Overview</h2>
          <Link to="/vehicles" style={{ color: '#6366f1', textDecoration: 'none', fontSize: '0.9375rem' }}>View All Vehicles →</Link>
        </div>
        <div style={{ overflowX: 'auto', background: '#1e293b', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2d3748' }}>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>VIN</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Model</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Health Score</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {vehicles && vehicles.length > 0 ? (
                vehicles.slice(0, 10).map((vehicle, idx) => (
                  <tr key={vehicle.vehicle_id} style={{ borderBottom: idx < 9 ? '1px solid #2d3748' : 'none' }}>
                    <td style={{ padding: '1rem', color: '#fff', fontFamily: 'monospace' }}>{vehicle.vin}</td>
                    <td style={{ padding: '1rem', color: '#fff' }}>{vehicle.make} {vehicle.model}</td>
                    <td style={{ padding: '1rem', color: '#fff' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ flex: 1, background: '#0f172a', borderRadius: '9999px', height: '8px', overflow: 'hidden' }}>
                          <div style={{ 
                            width: `${vehicle.health_score * 10}%`, 
                            height: '100%', 
                            background: vehicle.health_score >= 8 ? '#22c55e' : vehicle.health_score >= 5 ? '#f59e0b' : '#ef4444',
                            transition: 'width 0.3s'
                          }}></div>
                        </div>
                        <span style={{ fontSize: '0.875rem', minWidth: '30px' }}>{vehicle.health_score}/10</span>
                      </div>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        background: vehicle.health_score >= 8 ? 'rgba(34, 197, 94, 0.2)' : vehicle.health_score >= 5 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        color: vehicle.health_score >= 8 ? '#22c55e' : vehicle.health_score >= 5 ? '#f59e0b' : '#ef4444',
                        border: `1px solid ${vehicle.health_score >= 8 ? 'rgba(34, 197, 94, 0.3)' : vehicle.health_score >= 5 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
                      }}>
                        {vehicle.health_score >= 8 ? '✓ Healthy' : vehicle.health_score >= 5 ? '⚠ Warning' : '⚠ Critical'}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <Link to="/vehicles" style={{ color: '#6366f1', textDecoration: 'none', fontSize: '0.875rem' }}>
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
                    No vehicle data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
