import { useState, useEffect } from 'react';
import { Calendar, Plus, RefreshCw, Clock, MapPin, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { getAppointments, cancelAppointment } from '../utils/api';

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchAppointments();
    const interval = setInterval(fetchAppointments, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const response = await getAppointments({ status: statusFilter === 'all' ? undefined : statusFilter });
      setAppointments(response.data || []);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (id) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    
    try {
      await cancelAppointment(id);
      alert('Appointment cancelled successfully');
      fetchAppointments();
    } catch (error) {
      alert('Failed to cancel appointment: ' + error.message);
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed': return <CheckCircle size={20} style={{ color: '#22c55e' }} />;
      case 'pending': return <Clock size={20} style={{ color: '#f59e0b' }} />;
      case 'completed': return <CheckCircle size={20} style={{ color: '#3b82f6' }} />;
      case 'cancelled': return <XCircle size={20} style={{ color: '#ef4444' }} />;
      default: return <AlertCircle size={20} style={{ color: '#9ca3af' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed': return { bg: 'rgba(34, 197, 94, 0.2)', color: '#22c55e' };
      case 'pending': return { bg: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b' };
      case 'completed': return { bg: 'rgba(59, 130, 246, 0.2)', color: '#3b82f6' };
      case 'cancelled': return { bg: 'rgba(239, 68, 68, 0.2)', color: '#ef4444' };
      default: return { bg: 'rgba(156, 163, 175, 0.2)', color: '#9ca3af' };
    }
  };

  const filteredAppointments = appointments.filter(apt =>
    statusFilter === 'all' || apt.status?.toLowerCase() === statusFilter
  );

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Professional Page Header */}
      <div style={{
        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
        borderRadius: '1rem',
        padding: '1.5rem 2rem',
        marginBottom: '2rem',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        boxShadow: '0 4px 20px rgba(59, 130, 246, 0.2)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <Calendar size={32} style={{ color: '#dbeafe' }} />
              <h1 style={{ fontSize: '2rem', margin: 0, fontWeight: '700', color: '#fff' }}>Service Appointments</h1>
            </div>
            <p style={{ color: 'rgba(255, 255, 255, 0.85)', marginTop: '0.25rem', fontSize: '0.95rem' }}>Schedule and manage customer service appointments</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button onClick={fetchAppointments} disabled={loading} style={{
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
              Refresh
            </button>
            <button style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem',
              background: '#fff', color: '#1e40af', border: 'none', borderRadius: '0.75rem',
              cursor: 'pointer', fontSize: '0.9375rem', fontWeight: '600',
              transition: 'all 0.3s',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#f0f9ff';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = '#fff';
              e.currentTarget.style.transform = 'translateY(0)';
            }}>
              <Plus size={16} />
              New Appointment
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Calendar size={24} style={{ color: '#3b82f6' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Total</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{appointments.length}</p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Pending</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#f59e0b' }}>
            {appointments.filter(a => a.status?.toLowerCase() === 'pending').length}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Confirmed</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#22c55e' }}>
            {appointments.filter(a => a.status?.toLowerCase() === 'confirmed').length}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Completed</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#3b82f6' }}>
            {appointments.filter(a => a.status?.toLowerCase() === 'completed').length}
          </p>
        </div>
      </div>

      {/* Filter */}
      <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', marginBottom: '2rem', border: '1px solid #2d3748' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <label style={{ color: '#9ca3af', fontSize: '0.9375rem' }}>Filter by Status:</label>
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); fetchAppointments(); }} style={{
            padding: '0.5rem', background: '#0f172a', border: '1px solid #2d3748',
            borderRadius: '0.5rem', color: '#fff', fontSize: '0.9375rem', cursor: 'pointer'
          }}>
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Appointments List */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem', color: '#9ca3af' }}>
          <RefreshCw size={32} className="spinning" />
        </div>
      ) : filteredAppointments.length === 0 ? (
        <div style={{ background: '#1e293b', padding: '3rem', borderRadius: '0.75rem', textAlign: 'center', border: '1px solid #2d3748' }}>
          <Calendar size={48} style={{ color: '#4b5563', margin: '0 auto 1rem' }} />
          <p style={{ color: '#9ca3af', margin: 0 }}>No appointments found</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
          {filteredAppointments.map((appointment) => {
            const status = getStatusColor(appointment.status);
            return (
              <div key={appointment.appointment_id} style={{
                background: '#1e293b', border: '1px solid #2d3748', borderRadius: '0.75rem',
                padding: '1.5rem', transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = '#4b5563'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#2d3748'}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {getStatusIcon(appointment.status)}
                    <span style={{
                      padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem',
                      fontWeight: '600', background: status.bg, color: status.color
                    }}>
                      {appointment.status}
                    </span>
                  </div>
                  <span style={{ color: '#9ca3af', fontSize: '0.8125rem' }}>
                    #{appointment.appointment_id}
                  </span>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <Calendar size={16} style={{ color: '#9ca3af' }} />
                    <span style={{ color: '#fff', fontWeight: '500' }}>
                      {appointment.scheduled_time ? new Date(appointment.scheduled_time).toLocaleDateString('en-US', {
                        weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
                      }) : 'N/A'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <Clock size={16} style={{ color: '#9ca3af' }} />
                    <span style={{ color: '#fff' }}>
                      {appointment.scheduled_time ? new Date(appointment.scheduled_time).toLocaleTimeString('en-US', {
                        hour: '2-digit', minute: '2-digit'
                      }) : 'N/A'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <MapPin size={16} style={{ color: '#9ca3af' }} />
                    <span style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                      Service Center #{appointment.service_center_id || 'N/A'}
                    </span>
                  </div>
                </div>

                <div style={{ 
                  background: '#0f172a', borderRadius: '0.5rem', padding: '0.75rem',
                  marginBottom: '1rem', fontSize: '0.875rem'
                }}>
                  <p style={{ margin: '0 0 0.25rem 0', color: '#9ca3af' }}>Vehicle</p>
                  <p style={{ margin: 0, color: '#fff', fontFamily: 'monospace' }}>
                    ID: {appointment.vehicle_id}
                  </p>
                </div>

                {appointment.status?.toLowerCase() === 'confirmed' && (
                  <button
                    onClick={() => handleCancelAppointment(appointment.appointment_id)}
                    style={{
                      width: '100%', padding: '0.625rem', background: 'rgba(239, 68, 68, 0.1)',
                      color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)',
                      borderRadius: '0.5rem', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500'
                    }}
                  >
                    Cancel Appointment
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
