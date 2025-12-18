import { useState, useEffect } from 'react';
import { MessageSquare, Phone, Send, CheckCircle, XCircle, AlertTriangle, RefreshCw, Filter } from 'lucide-react';
import { 
  sendAlert, 
  getNotificationHistory, 
  getNotificationStats,
  autoSendCriticalAlerts,
  markNotificationRead 
} from '../utils/api';
import './Notifications.css';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [filter, setFilter] = useState({ channel: '', status: '' });
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [filter, page]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [historyRes, statsRes] = await Promise.all([
        getNotificationHistory({ ...filter, page, limit: 20 }),
        getNotificationStats()
      ]);
      setNotifications(historyRes.data.notifications || []);
      setStats(statsRes.data || {});
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendAlert = async (customerId, vehicleId, predictionId, channel) => {
    if (!confirm(`Send ${channel.toUpperCase()} alert for this prediction?`)) return;
    
    setSending(true);
    try {
      const response = await sendAlert({
        customer_id: customerId,
        vehicle_id: vehicleId,
        prediction_id: predictionId,
        channel: channel
      });
      
      alert(`${channel.toUpperCase()} sent successfully!\nNotification ID: ${response.data.notification_id}\nStatus: ${response.data.status}`);
      fetchData();
    } catch (error) {
      alert(`Failed to send ${channel}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSending(false);
    }
  };

  const handleAutoSendCritical = async () => {
    if (!confirm('Send SMS alerts to ALL critical predictions that haven\'t been notified yet?')) return;
    
    setSending(true);
    try {
      const response = await autoSendCriticalAlerts();
      alert(`Successfully sent ${response.data.notifications_sent} alerts!\nDetails:\n${JSON.stringify(response.data, null, 2)}`);
      fetchData();
    } catch (error) {
      alert(`Failed to auto-send: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSending(false);
    }
  };

  const handleMarkRead = async (notificationId) => {
    try {
      await markNotificationRead(notificationId);
      fetchData();
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'delivered':
        return <CheckCircle size={16} className="status-icon delivered" />;
      case 'failed':
        return <XCircle size={16} className="status-icon failed" />;
      case 'pending':
        return <AlertTriangle size={16} className="status-icon pending" />;
      default:
        return null;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="notifications-page">
      <div className="page-header">
        <h1>Notification Center</h1>
        <div className="header-actions">
          <button 
            onClick={handleAutoSendCritical} 
            disabled={sending}
            className="btn btn-primary"
          >
            <Send size={16} />
            Auto-Send Critical Alerts
          </button>
          <button onClick={fetchData} disabled={loading} className="btn btn-secondary">
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#3b82f6' }}>
            <Send size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Sent</p>
            <p className="stat-value">{stats.total_sent || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#10b981' }}>
            <MessageSquare size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">SMS Sent</p>
            <p className="stat-value">{stats.sms_sent || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#8b5cf6' }}>
            <Phone size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Voice Calls</p>
            <p className="stat-value">{stats.voice_calls || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#22c55e' }}>
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Delivered</p>
            <p className="stat-value">{stats.delivered || 0}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filters">
          <div className="filter-item">
            <label>
              <Filter size={16} />
              Channel
            </label>
            <select 
              value={filter.channel} 
              onChange={(e) => setFilter({ ...filter, channel: e.target.value })}
            >
              <option value="">All</option>
              <option value="sms">SMS</option>
              <option value="voice">Voice</option>
            </select>
          </div>

          <div className="filter-item">
            <label>Status</label>
            <select 
              value={filter.status} 
              onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            >
              <option value="">All</option>
              <option value="delivered">Delivered</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Notification History */}
      <div className="notifications-list">
        <h2>Notification History</h2>
        
        {loading ? (
          <div className="loading-state">
            <RefreshCw size={32} className="spinning" />
            <p>Loading notifications...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="empty-state">
            <AlertTriangle size={48} />
            <p>No notifications found</p>
            <p className="hint">Try sending an alert or adjusting filters</p>
          </div>
        ) : (
          <div className="notification-items">
            {notifications.map((notification) => (
              <div 
                key={notification.notification_id} 
                className={`notification-item ${!notification.read_status ? 'unread' : ''}`}
              >
                <div className="notification-header">
                  <div className="notification-meta">
                    <span className={`channel-badge ${notification.channel}`}>
                      {notification.channel === 'sms' ? <MessageSquare size={14} /> : <Phone size={14} />}
                      {notification.channel.toUpperCase()}
                    </span>
                    {getStatusIcon(notification.status)}
                    <span className="timestamp">{formatTimestamp(notification.sent_at)}</span>
                  </div>
                  {!notification.read_status && (
                    <button 
                      onClick={() => handleMarkRead(notification.notification_id)}
                      className="mark-read-btn"
                    >
                      Mark as Read
                    </button>
                  )}
                </div>

                <div className="notification-content">
                  <p className="message-preview">{notification.message}</p>
                  <div className="notification-details">
                    <span>Vehicle ID: {notification.vehicle_id}</span>
                    {notification.prediction_id && (
                      <span>Prediction ID: {notification.prediction_id}</span>
                    )}
                    {notification.twilio_sid && (
                      <span className="twilio-sid">SID: {notification.twilio_sid.substring(0, 20)}...</span>
                    )}
                  </div>
                </div>

                {notification.status === 'failed' && notification.error_message && (
                  <div className="error-message">
                    <XCircle size={14} />
                    {notification.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Send Test */}
      <div className="quick-send-section">
        <h2>Test Notification</h2>
        <p className="hint">Send test alerts using existing predictions</p>
        <div className="quick-send-actions">
          <button 
            onClick={() => handleSendAlert(1, 2, 30, 'sms')}
            disabled={sending}
            className="btn btn-success"
          >
            <MessageSquare size={16} />
            Send Test SMS
          </button>
          <button 
            onClick={() => handleSendAlert(1, 2, 30, 'voice')}
            disabled={sending}
            className="btn btn-warning"
          >
            <Phone size={16} />
            Make Test Call
          </button>
        </div>
        <p className="hint" style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
          Using Customer ID: 1, Vehicle ID: 2, Prediction ID: 30
        </p>
      </div>
    </div>
  );
}
