import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { RefreshCw, TrendingUp, DollarSign, Target, AlertTriangle } from 'lucide-react';
import { getFleetHealthTrend, getComponentFailures, getMaintenanceCosts, getFleetSummary } from '../utils/api';

export default function Analytics() {
  const [fleetTrend, setFleetTrend] = useState([]);
  const [componentFailures, setComponentFailures] = useState([]);
  const [maintenanceCosts, setMaintenanceCosts] = useState([]);
  const [fleetSummary, setFleetSummary] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [trendRes, failuresRes, costsRes, summaryRes] = await Promise.all([
        getFleetHealthTrend(30),
        getComponentFailures(90),
        getMaintenanceCosts(6),
        getFleetSummary()
      ]);
      setFleetTrend(trendRes.data || []);
      setComponentFailures(failuresRes.data || []);
      setMaintenanceCosts(costsRes.data || []);
      setFleetSummary(summaryRes.data || {});
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#ef4444', '#f97316', '#22c55e'];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <RefreshCw size={48} className="spinning" style={{ color: '#9ca3af' }} />
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h1 style={{ fontSize: '2rem', margin: 0 }}>Analytics & Insights</h1>
        <button onClick={fetchAnalytics} disabled={loading} style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.625rem 1.25rem',
          background: '#374151', color: '#fff', border: 'none', borderRadius: '0.5rem',
          cursor: 'pointer', fontSize: '0.9375rem', fontWeight: '500'
        }}>
          <RefreshCw size={16} className={loading ? 'spinning' : ''} />
          Refresh
        </button>
      </div>

      {/* Summary Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <TrendingUp size={24} style={{ color: '#22c55e' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Avg Health Score</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#22c55e' }}>
            {fleetSummary.avg_health_score?.toFixed(1) || '0.0'}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <AlertTriangle size={24} style={{ color: '#ef4444' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Active Alerts</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>
            {fleetSummary.total_alerts || 0}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Target size={24} style={{ color: '#3b82f6' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Predictions</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>
            {fleetSummary.total_predictions || 0}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <DollarSign size={24} style={{ color: '#f59e0b' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Appointments</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>
            {fleetSummary.total_appointments || 0}
          </p>
        </div>
      </div>

      {/* Fleet Health Trend */}
      <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', marginBottom: '2rem', border: '1px solid #2d3748' }}>
        <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem' }}>Fleet Health Trend (30 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={fleetTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
            <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '0.875rem' }} />
            <YAxis stroke="#9ca3af" style={{ fontSize: '0.875rem' }} />
            <Tooltip 
              contentStyle={{ background: '#1e293b', border: '1px solid #2d3748', borderRadius: '0.5rem' }}
              labelStyle={{ color: '#fff' }}
            />
            <Legend />
            <Line type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2} name="Critical" />
            <Line type="monotone" dataKey="warning" stroke="#f97316" strokeWidth={2} name="Warning" />
            <Line type="monotone" dataKey="healthy" stroke="#22c55e" strokeWidth={2} name="Healthy" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Two Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '2rem' }}>
        {/* Component Failures */}
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem' }}>Component Failure Predictions</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={componentFailures}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis dataKey="component" stroke="#9ca3af" style={{ fontSize: '0.75rem' }} angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '0.875rem' }} />
              <Tooltip 
                contentStyle={{ background: '#1e293b', border: '1px solid #2d3748', borderRadius: '0.5rem' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Bar dataKey="prediction_count" fill="#3b82f6" name="Total Predictions" />
              <Bar dataKey="critical_count" fill="#ef4444" name="Critical" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Maintenance Costs */}
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem' }}>Maintenance Costs (6 Months)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={maintenanceCosts}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis dataKey="period" stroke="#9ca3af" style={{ fontSize: '0.875rem' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '0.875rem' }} />
              <Tooltip 
                contentStyle={{ background: '#1e293b', border: '1px solid #2d3748', borderRadius: '0.5rem' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Bar dataKey="parts_cost" stackId="a" fill="#8b5cf6" name="Parts Cost" />
              <Bar dataKey="labor_cost" stackId="a" fill="#06b6d4" name="Labor Cost" />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ marginTop: '1rem', padding: '1rem', background: '#0f172a', borderRadius: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#9ca3af', fontSize: '0.875rem' }}>
              <span>Total Parts:</span>
              <span style={{ color: '#8b5cf6', fontWeight: '600' }}>
                ${maintenanceCosts.reduce((sum, m) => sum + (m.parts_cost || 0), 0).toLocaleString()}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#9ca3af', fontSize: '0.875rem', marginTop: '0.5rem' }}>
              <span>Total Labor:</span>
              <span style={{ color: '#06b6d4', fontWeight: '600' }}>
                ${maintenanceCosts.reduce((sum, m) => sum + (m.labor_cost || 0), 0).toLocaleString()}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#fff', fontSize: '1rem', fontWeight: '600', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid #2d3748' }}>
              <span>Grand Total:</span>
              <span style={{ color: '#22c55e' }}>
                ${maintenanceCosts.reduce((sum, m) => sum + (m.total_cost || 0), 0).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
