import { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw, Bell, Filter, MessageSquare, Phone } from 'lucide-react';
import { getDashboardAlerts, sendAlert } from '../utils/api';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await getDashboardAlerts();
      setAlerts(response.data || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendNotification = async (alert, channel) => {
    if (!confirm(`Send ${channel.toUpperCase()} notification for ${alert.component} failure?`)) return;
    
    setSending(true);
    try {
      await sendAlert({
        customer_id: 1,
        vehicle_id: alert.vehicle_id,
        prediction_id: alert.prediction_id,
        channel: channel
      });
      alert(`${channel.toUpperCase()} notification sent successfully!`);
    } catch (error) {
      alert(`Failed to send notification: ${error.message}`);
    } finally {
      setSending(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return { bg: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', icon: '🔴' };
      case 'high': return { bg: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b', icon: '🟠' };
      case 'medium': return { bg: 'rgba(234, 179, 8, 0.2)', color: '#eab308', icon: '🟡' };
      case 'low': return { bg: 'rgba(34, 197, 94, 0.2)', color: '#22c55e', icon: '🟢' };
      default: return { bg: 'rgba(156, 163, 175, 0.2)', color: '#9ca3af', icon: '⚪' };
    }
  };

  const filteredAlerts = alerts.filter(alert => 
    severityFilter === 'all' || alert.severity?.toLowerCase() === severityFilter
  );

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Professional Page Header */}
      <div style={{
        background: 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)',
        borderRadius: '1rem',
        padding: '1.5rem 2rem',
        marginBottom: '2rem',
        border: '1px solid rgba(220, 38, 38, 0.3)',
        boxShadow: '0 4px 20px rgba(220, 38, 38, 0.2)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <AlertTriangle size={32} style={{ color: '#fef2f2' }} />
              <h1 style={{ fontSize: '2rem', margin: 0, fontWeight: '700', color: '#fff' }}>Critical Alerts</h1>
            </div>
            <p style={{ color: 'rgba(255, 255, 255, 0.85)', marginTop: '0.25rem', fontSize: '0.95rem' }}>Monitor and respond to predictive maintenance alerts</p>
          </div>
          <button onClick={fetchAlerts} disabled={loading} style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem',
            background: 'rgba(255, 255, 255, 0.2)', 
            backdropFilter: 'blur(10px)',
            color: '#fff', 
            border: '2px solid rgba(255, 255, 255, 0.3)', 
            borderRadius: '0.75rem',
            cursor: loading ? 'not-allowed' : 'pointer', 
            fontSize: '0.9375rem', 
            fontWeight: '600',
            transition: 'all 0.3s'
          }}
          onMouseOver={(e) => !loading && (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)')}
          onMouseOut={(e) => !loading && (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)')}>
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh Alerts
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <AlertTriangle size={24} style={{ color: '#ef4444' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Total Alerts</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{alerts.length}</p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Critical</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#ef4444' }}>
            {alerts.filter(a => a.severity?.toLowerCase() === 'critical').length}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>High</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#f59e0b' }}>
            {alerts.filter(a => a.severity?.toLowerCase() === 'high').length}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Medium/Low</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#eab308' }}>
            {alerts.filter(a => ['medium', 'low'].includes(a.severity?.toLowerCase())).length}
          </p>
        </div>
      </div>

      {/* Filter */}
      <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', marginBottom: '2rem', border: '1px solid #2d3748' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Filter size={20} style={{ color: '#9ca3af' }} />
          <label style={{ color: '#9ca3af', fontSize: '0.9375rem' }}>Filter by Severity:</label>
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)} style={{
            padding: '0.5rem', background: '#0f172a', border: '1px solid #2d3748',
            borderRadius: '0.5rem', color: '#fff', fontSize: '0.9375rem', cursor: 'pointer'
          }}>
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Alerts List */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem', color: '#9ca3af' }}>
          <RefreshCw size={32} className="spinning" />
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div style={{ background: '#1e293b', padding: '3rem', borderRadius: '0.75rem', textAlign: 'center', border: '1px solid #2d3748' }}>
          <Bell size={48} style={{ color: '#4b5563', margin: '0 auto 1rem' }} />
          <p style={{ color: '#9ca3af', margin: 0 }}>No alerts found</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {filteredAlerts.map((alert, idx) => {
            const severity = getSeverityColor(alert.severity);
            return (
              <div key={idx} style={{
                background: '#1e293b', border: '1px solid #2d3748', borderLeft: `4px solid ${severity.color}`,
                borderRadius: '0.75rem', padding: '1.5rem', transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = severity.color}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#2d3748'}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '1.5rem' }}>{severity.icon}</span>
                      <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#fff' }}>
                        {alert.component} Failure Prediction
                      </h3>
                      <span style={{
                        padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem',
                        fontWeight: '600', background: severity.bg, color: severity.color
                      }}>
                        {alert.severity}
                      </span>
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', color: '#9ca3af', fontSize: '0.875rem' }}>
                      <span>🚗 VIN: <strong style={{ color: '#fff', fontFamily: 'monospace' }}>{alert.vin}</strong></span>
                      <span>📊 Probability: <strong style={{ color: severity.color }}>
                        {alert.failure_probability ? (alert.failure_probability * 100).toFixed(1) : 'N/A'}%
                      </strong></span>
                      <span>📅 Predicted: <strong style={{ color: '#fff' }}>
                        {alert.predicted_failure_date ? new Date(alert.predicted_failure_date).toLocaleDateString() : 'N/A'}
                      </strong></span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <button
                      onClick={() => handleSendNotification(alert, 'sms')}
                      disabled={sending}
                      style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                        background: '#10b981', color: '#fff', border: 'none', borderRadius: '0.5rem',
                        cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500'
                      }}
                    >
                      <MessageSquare size={16} />
                      Send SMS
                    </button>
                    <button
                      onClick={() => handleSendNotification(alert, 'voice')}
                      disabled={sending}
                      style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                        background: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '0.5rem',
                        cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500'
                      }}
                    >
                      <Phone size={16} />
                      Call
                    </button>
                  </div>
                </div>
                {alert.recommendation && (
                  <div style={{ 
                    background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.3)',
                    borderRadius: '0.5rem', padding: '1rem', marginTop: '1rem'
                  }}>
                    <p style={{ margin: 0, color: '#9ca3af', fontSize: '0.875rem' }}>
                      💡 <strong style={{ color: '#6366f1' }}>Recommendation:</strong> {alert.recommendation}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
