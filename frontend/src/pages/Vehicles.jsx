import { useState, useEffect } from 'react';
import { Car, Search, Filter, RefreshCw, TrendingUp, TrendingDown, Eye } from 'lucide-react';
import { getDashboardVehicles } from '../utils/api';
import VehicleVisualization from '../components/VehicleVisualizationSimple';

export default function Vehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  useEffect(() => {
    fetchVehicles();
    const interval = setInterval(fetchVehicles, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      const response = await getDashboardVehicles();
      setVehicles(response.data || []);
    } catch (error) {
      console.error('Error fetching vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredVehicles = vehicles.filter(vehicle => {
    const matchesSearch = vehicle.vin?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vehicle.make?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vehicle.model?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (statusFilter === 'all') return matchesSearch;
    
    const status = vehicle.health_score >= 8 ? 'healthy' : 
                   vehicle.health_score >= 5 ? 'warning' : 'critical';
    return matchesSearch && status === statusFilter;
  });

  const getHealthStatus = (score) => {
    if (score >= 8) return { label: 'Healthy', color: '#22c55e', bg: 'rgba(34, 197, 94, 0.2)' };
    if (score >= 5) return { label: 'Warning', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.2)' };
    return { label: 'Critical', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.2)' };
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Professional Page Header */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
        borderRadius: '1rem',
        padding: '1.5rem 2rem',
        marginBottom: '2rem',
        border: '1px solid #475569',
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '2rem', margin: 0, fontWeight: '700' }}>Fleet Management</h1>
            <p style={{ color: '#94a3b8', marginTop: '0.5rem', fontSize: '0.95rem' }}>Monitor and manage all service center vehicles</p>
          </div>
          <button onClick={fetchVehicles} disabled={loading} style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem',
            background: loading ? '#475569' : '#dc2626', 
            color: '#fff', 
            border: 'none', 
            borderRadius: '0.75rem',
            cursor: loading ? 'not-allowed' : 'pointer', 
            fontSize: '0.9375rem', 
            fontWeight: '600',
            transition: 'all 0.3s',
            boxShadow: '0 2px 8px rgba(220, 38, 38, 0.3)'
          }}
          onMouseOver={(e) => !loading && (e.currentTarget.style.background = '#b91c1c')}
          onMouseOut={(e) => !loading && (e.currentTarget.style.background = '#dc2626')}>
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh Fleet
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Car size={24} style={{ color: '#3b82f6' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Total Vehicles</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{vehicles.length}</p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <TrendingUp size={24} style={{ color: '#22c55e' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Healthy</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#22c55e' }}>
            {vehicles.filter(v => v.health_score >= 8).length}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <TrendingDown size={24} style={{ color: '#f59e0b' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Warning</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#f59e0b' }}>
            {vehicles.filter(v => v.health_score >= 5 && v.health_score < 8).length}
          </p>
        </div>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <TrendingDown size={24} style={{ color: '#ef4444' }} />
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#9ca3af' }}>Critical</p>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#ef4444' }}>
            {vehicles.filter(v => v.health_score < 5).length}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', marginBottom: '2rem', border: '1px solid #2d3748' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1', minWidth: '250px', position: 'relative' }}>
            <Search size={20} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
            <input
              type="text"
              placeholder="Search by VIN, make, or model..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%', padding: '0.75rem 0.75rem 0.75rem 2.75rem', background: '#0f172a',
                border: '1px solid #2d3748', borderRadius: '0.5rem', color: '#fff', fontSize: '0.9375rem'
              }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={20} style={{ color: '#9ca3af' }} />
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{
              padding: '0.75rem', background: '#0f172a', border: '1px solid #2d3748',
              borderRadius: '0.5rem', color: '#fff', fontSize: '0.9375rem', cursor: 'pointer'
            }}>
              <option value="all">All Status</option>
              <option value="healthy">Healthy</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
      </div>

      {/* Vehicles Table */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem', color: '#9ca3af' }}>
          <RefreshCw size={32} className="spinning" />
        </div>
      ) : (
        <div style={{ overflowX: 'auto', background: '#1e293b', borderRadius: '0.75rem', border: '1px solid #2d3748' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2d3748' }}>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>VIN</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Make & Model</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Year</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Mileage</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Health Score</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#9ca3af', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredVehicles.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
                    No vehicles found
                  </td>
                </tr>
              ) : (
                filteredVehicles.map((vehicle, idx) => {
                  const status = getHealthStatus(vehicle.health_score);
                  return (
                    <tr key={vehicle.vehicle_id} style={{ borderBottom: idx < filteredVehicles.length - 1 ? '1px solid #2d3748' : 'none' }}>
                      <td style={{ padding: '1rem', color: '#fff', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                        {vehicle.vin}
                      </td>
                      <td style={{ padding: '1rem', color: '#fff' }}>
                        {vehicle.make} {vehicle.model}
                      </td>
                      <td style={{ padding: '1rem', color: '#fff' }}>
                        {vehicle.year || 'N/A'}
                      </td>
                      <td style={{ padding: '1rem', color: '#fff' }}>
                        {vehicle.mileage ? vehicle.mileage.toLocaleString() + ' mi' : 'N/A'}
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ 
                            width: '100px', height: '8px', background: '#0f172a', 
                            borderRadius: '9999px', overflow: 'hidden' 
                          }}>
                            <div style={{ 
                              width: `${vehicle.health_score * 10}%`, height: '100%', 
                              background: status.color, transition: 'width 0.3s' 
                            }} />
                          </div>
                          <span style={{ color: '#fff', fontWeight: '600' }}>
                            {vehicle.health_score.toFixed(1)}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <span style={{
                          padding: '0.375rem 0.75rem', borderRadius: '9999px', fontSize: '0.8125rem',
                          fontWeight: '600', background: status.bg, color: status.color
                        }}>
                          {status.label}
                        </span>
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <button
                          onClick={() => setSelectedVehicle({ id: vehicle.vehicle_id, type: vehicle.vehicle_type || 'Motorcycle' })}
                          style={{
                            display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                            background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '0.5rem',
                            cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500', transition: 'background 0.2s'
                          }}
                          onMouseOver={(e) => e.currentTarget.style.background = '#2563eb'}
                          onMouseOut={(e) => e.currentTarget.style.background = '#3b82f6'}
                        >
                          <Eye size={16} />
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {selectedVehicle && (
        <VehicleVisualization
          vehicleId={selectedVehicle.id}
          vehicleType={selectedVehicle.type}
          onClose={() => setSelectedVehicle(null)}
        />
      )}
    </div>
  );
}
