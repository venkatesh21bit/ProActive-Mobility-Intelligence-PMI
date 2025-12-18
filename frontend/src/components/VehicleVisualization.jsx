import { useState, useEffect } from 'react';
import { X, AlertTriangle, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { getVehicleDetails } from '../utils/api';
import './VehicleVisualization.css';

export default function VehicleVisualization({ vehicleId, vehicleType, onClose }) {
  const [vehicleData, setVehicleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [hoveredComponent, setHoveredComponent] = useState(null);

  useEffect(() => {
    fetchVehicleDetails();
    const interval = setInterval(fetchVehicleDetails, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [vehicleId]);

  const fetchVehicleDetails = async () => {
    try {
      const response = await getVehicleDetails(vehicleId);
      console.log('✅ Vehicle Details Response:', response.data);
      console.log('✅ Components:', response.data?.components);
      console.log('✅ Component Keys:', Object.keys(response.data?.components || {}));
      setVehicleData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('❌ Error fetching vehicle details:', error);
      console.error('❌ Error details:', error.response?.data);
      setVehicleData({ error: true, message: error.message });
      setLoading(false);
    }
  };

  const getComponentColor = (component) => {
    if (!component) return '#64748b';
    if (component.status === 'critical') return '#ef4444';
    if (component.status === 'warning') return '#f59e0b';
    return '#22c55e';
  };

  const getStatusIcon = (status) => {
    if (status === 'critical') return <AlertTriangle size={20} color="#ef4444" />;
    if (status === 'warning') return <AlertCircle size={20} color="#f59e0b" />;
    return <CheckCircle size={20} color="#22c55e" />;
  };

  // Component positions for realistic motorcycle visualization
  const motorcycleComponents = {
    engine: { x: 200, y: 160, width: 70, height: 55, label: 'Engine' },
    transmission: { x: 155, y: 190, width: 50, height: 40, label: 'Transmission' },
    brakes: { x: 85, y: 245, width: 45, height: 35, label: 'Front Brake' },
    battery: { x: 230, y: 120, width: 45, height: 35, label: 'Battery' },
    cooling_system: { x: 185, y: 115, width: 50, height: 35, label: 'Cooling' },
    oil_system: { x: 160, y: 225, width: 50, height: 30, label: 'Oil System' },
    suspension: { x: 95, y: 270, width: 65, height: 35, label: 'Suspension' },
    tires: { x: 70, y: 285, width: 40, height: 40, label: 'Front Tire' },
    exhaust: { x: 255, y: 200, width: 75, height: 30, label: 'Exhaust' },
    fuel_system: { x: 265, y: 155, width: 55, height: 40, label: 'Fuel Tank' }
  };

  // Component positions for scooter visualization
  const scooterComponents = {
    engine: { x: 180, y: 200, width: 70, height: 50, label: 'Engine' },
    transmission: { x: 160, y: 230, width: 50, height: 35, label: 'Transmission' },
    brakes: { x: 90, y: 250, width: 45, height: 25, label: 'Brakes' },
    battery: { x: 220, y: 150, width: 45, height: 35 },
    cooling_system: { x: 180, y: 130, width: 55, height: 35 },
    oil_system: { x: 160, y: 250, width: 45, height: 25 },
    suspension: { x: 110, y: 280, width: 60, height: 35 },
    tires: { x: 70, y: 290, width: 35, height: 35 },
    exhaust: { x: 230, y: 230, width: 70, height: 25 },
    fuel_system: { x: 240, y: 180, width: 55, height: 35 }
  };

  const componentPositions = vehicleType === 'Scooter' ? scooterComponents : motorcycleComponents;

  if (loading) {
    return (
      <div className="vehicle-viz-modal">
        <div className="vehicle-viz-content">
          <div className="loading-spinner">Loading vehicle data...</div>
        </div>
      </div>
    );
  }

  if (!vehicleData || !vehicleData.vehicle || !vehicleData.health || !vehicleData.components) {
    console.error('❌ Invalid vehicle data structure:', {
      hasVehicleData: !!vehicleData,
      hasVehicle: !!vehicleData?.vehicle,
      hasHealth: !!vehicleData?.health,
      hasComponents: !!vehicleData?.components,
      componentKeys: Object.keys(vehicleData?.components || {}),
      actualData: vehicleData
    });
    return (
      <div className="vehicle-viz-modal" onClick={onClose}>
        <div className="vehicle-viz-content" onClick={(e) => e.stopPropagation()}>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
          <div style={{ padding: '2rem', color: '#fff' }}>
            <h3>Failed to load vehicle data</h3>
            <p style={{ marginTop: '1rem', fontSize: '14px', color: '#9ca3af' }}>
              {vehicleData?.error ? `Error: ${vehicleData.message}` : 'Missing required data fields'}
            </p>
            <details style={{ marginTop: '1rem' }}>
              <summary style={{ cursor: 'pointer', color: '#60a5fa' }}>View Debug Info</summary>
              <pre style={{ fontSize: '10px', marginTop: '0.5rem', maxHeight: '300px', overflow: 'auto', background: '#0f172a', padding: '1rem', borderRadius: '0.5rem' }}>
                {JSON.stringify(vehicleData, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      </div>
    );
  }

  console.log('✅ About to render visualization with:', {
    vehicleId: vehicleData.vehicle.vehicle_id,
    vin: vehicleData.vehicle.vin,
    status: vehicleData.health.overall_status,
    componentCount: Object.keys(vehicleData.components).length
  });

  // Render the visualization
  try {
    return (
    <div className="vehicle-viz-modal" onClick={onClose}>
      <div className="vehicle-viz-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>
          <X size={24} />
        </button>

        <div className="vehicle-viz-header">
          <h2>Vehicle Component Health: {vehicleData.vehicle.make} {vehicleData.vehicle.model}</h2>
          <p className="vin-info">VIN: {vehicleData.vehicle.vin}</p>
          <div className="health-summary">
            <div className={`health-score ${vehicleData.health.overall_status || 'unknown'}`}>
              <span className="score-label">Overall Health</span>
              <span className="score-value">{vehicleData.health.overall_score}%</span>
              <span className={`status-badge ${vehicleData.health.overall_status || 'unknown'}`}>
                {(vehicleData.health.overall_status || 'unknown').toString().toUpperCase()}
              </span>
            </div>
            <div className="component-counts">
              <div className="count-item critical">
                <AlertTriangle size={16} />
                <span>{vehicleData.health.critical_components || 0} Critical</span>
              </div>
              <div className="count-item warning">
                <AlertCircle size={16} />
                <span>{vehicleData.health.warning_components || 0} Warnings</span>
              </div>
              <div className="count-item healthy">
                <CheckCircle size={16} />
                <span>{vehicleData.health.healthy_components || 0} Healthy</span>
              </div>
            </div>
          </div>
        </div>

        <div className="vehicle-viz-body">
          <div className="vehicle-svg-container">
            <svg viewBox="0 0 400 350" className="vehicle-svg">
              {/* Background vehicle silhouette */}
              <g className="vehicle-outline">
                {vehicleType === 'Scooter' ? (
                  <>
                    {/* Scooter body outline */}
                    <path d="M 100 150 Q 120 130 160 130 L 250 130 Q 280 130 290 160 L 300 200 Q 300 220 280 230 L 200 240 Q 180 250 160 250 L 100 250 Q 80 250 70 230 Q 60 210 70 190 Z" 
                          fill="#1e293b" stroke="#475569" strokeWidth="2" opacity="0.3"/>
                    {/* Wheels */}
                    <circle cx="100" cy="280" r="30" fill="#1e293b" stroke="#475569" strokeWidth="2" opacity="0.3"/>
                    <circle cx="280" cy="280" r="30" fill="#1e293b" stroke="#475569" strokeWidth="2" opacity="0.3"/>
                  </>
                ) : (
                  <>
                    {/* Motorcycle - Realistic Hero MotoCorp Structure */}
                    {/* Fuel tank */}
                    <ellipse cx="260" cy="160" rx="50" ry="35" fill="#1e293b" stroke="#475569" strokeWidth="2.5" opacity="0.4"/>
                    {/* Seat */}
                    <path d="M 220 170 Q 240 165 260 170 L 280 180 Q 285 185 280 190 L 230 195 Q 220 190 220 180 Z" 
                          fill="#1e293b" stroke="#475569" strokeWidth="2" opacity="0.4"/>
                    {/* Engine block */}
                    <rect x="180" y="155" width="75" height="60" rx="8" fill="#1e293b" stroke="#475569" strokeWidth="2.5" opacity="0.4"/>
                    {/* Frame */}
                    <path d="M 100 150 L 180 150 L 220 140 L 280 150 L 310 200 L 290 260" 
                          fill="none" stroke="#475569" strokeWidth="3" opacity="0.5"/>
                    <path d="M 180 180 L 150 240 L 100 280" fill="none" stroke="#475569" strokeWidth="3" opacity="0.5"/>
                    {/* Exhaust pipe */}
                    <path d="M 250 210 Q 280 210 300 220 L 320 225" fill="none" stroke="#475569" strokeWidth="4" opacity="0.4"/>
                    {/* Front fork */}
                    <line x1="110" y1="180" x2="95" y2="260" stroke="#475569" strokeWidth="3" opacity="0.5"/>
                    {/* Wheels with spokes */}
                    <circle cx="100" cy="285" r="38" fill="#0f172a" stroke="#475569" strokeWidth="3" opacity="0.5"/>
                    <circle cx="100" cy="285" r="25" fill="none" stroke="#475569" strokeWidth="1.5" opacity="0.4"/>
                    <circle cx="290" cy="285" r="38" fill="#0f172a" stroke="#475569" strokeWidth="3" opacity="0.5"/>
                    <circle cx="290" cy="285" r="25" fill="none" stroke="#475569" strokeWidth="1.5" opacity="0.4"/>
                    {/* Headlight */}
                    <circle cx="85" cy="210" r="8" fill="#fef08a" stroke="#475569" strokeWidth="1.5" opacity="0.6"/>
                  </>
                )}
              </g>

              {/* Component overlay areas */}
              {Object.entries(componentPositions).map(([componentName, pos]) => {
                const component = vehicleData.components[componentName];
                const color = getComponentColor(component);
                const isHovered = hoveredComponent === componentName;
                const isSelected = selectedComponent === componentName;

                return (
                  <g key={componentName}>
                    <rect
                      x={pos.x}
                      y={pos.y}
                      width={pos.width}
                      height={pos.height}
                      fill={color}
                      opacity={isHovered || isSelected ? 0.8 : 0.5}
                      stroke={isSelected ? '#fff' : color}
                      strokeWidth={isSelected ? 3 : 1}
                      rx="5"
                      className="component-area"
                      onMouseEnter={() => setHoveredComponent(componentName)}
                      onMouseLeave={() => setHoveredComponent(null)}
                      onClick={() => setSelectedComponent(selectedComponent === componentName ? null : componentName)}
                      style={{ cursor: 'pointer' }}
                    />
                    {(isHovered || isSelected) && (
                      <text
                        x={pos.x + pos.width / 2}
                        y={pos.y - 5}
                        textAnchor="middle"
                        fill="#fff"
                        fontSize="11"
                        fontWeight="600"
                        style={{ pointerEvents: 'none' }}
                      >
                        {pos.label || componentName.replace('_', ' ').toUpperCase()}
                      </text>
                    )}
                    {(isHovered || isSelected) && (
                      <text
                        x={pos.x + pos.width / 2}
                        y={pos.y + pos.height / 2}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill="#fff"
                        fontSize="10"
                        fontWeight="bold"
                        style={{ pointerEvents: 'none', textTransform: 'capitalize' }}
                      >
                        {componentName.replace('_', ' ')}
                      </text>
                    )}
                  </g>
                );
              })}
            </svg>

            <div className="legend">
              <div className="legend-item">
                <div className="legend-color" style={{ background: '#22c55e' }}></div>
                <span>Healthy</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ background: '#f59e0b' }}></div>
                <span>Warning</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ background: '#ef4444' }}></div>
                <span>Critical</span>
              </div>
            </div>
          </div>

          <div className="component-details-panel">
            <h3>Component Details</h3>
            <div className="component-list">
              {Object.entries(vehicleData.components).map(([name, component]) => {
                const isActive = selectedComponent === name || hoveredComponent === name;
                return (
                  <div
                    key={name}
                    className={`component-item ${isActive ? 'active' : ''}`}
                    onClick={() => setSelectedComponent(selectedComponent === name ? null : name)}
                    onMouseEnter={() => setHoveredComponent(name)}
                    onMouseLeave={() => setHoveredComponent(null)}
                  >
                    <div className="component-header">
                      <div className="component-name">
                        {getStatusIcon(component.status)}
                        <span>{name.replace('_', ' ').toUpperCase()}</span>
                      </div>
                      <span className={`health-percentage ${component.status}`}>
                        {component.health}%
                      </span>
                    </div>
                    {component.issues && component.issues.length > 0 && (
                      <div className="component-issues">
                        {component.issues.map((issue, idx) => (
                          <div key={idx} className="issue-item">
                            <Info size={14} />
                            <span>{issue}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {component.status === 'healthy' && (
                      <div className="component-healthy-msg">
                        ✓ Operating within normal parameters
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {vehicleData.latest_telemetry && (
          <div className="telemetry-footer">
            <h4>Latest Telemetry Data</h4>
            <div className="telemetry-grid">
              <div className="telemetry-item">
                <span className="label">Engine Temp:</span>
                <span className="value">{vehicleData.latest_telemetry.engine_temperature}°C</span>
              </div>
              <div className="telemetry-item">
                <span className="label">Oil Pressure:</span>
                <span className="value">{vehicleData.latest_telemetry.oil_pressure} PSI</span>
              </div>
              <div className="telemetry-item">
                <span className="label">Battery:</span>
                <span className="value">{vehicleData.latest_telemetry.battery_voltage}V</span>
              </div>
              <div className="telemetry-item">
                <span className="label">Vibration:</span>
                <span className="value">{vehicleData.latest_telemetry.vibration_level}</span>
              </div>
              <div className="telemetry-item">
                <span className="label">RPM:</span>
                <span className="value">{vehicleData.latest_telemetry.rpm}</span>
              </div>
              <div className="telemetry-item">
                <span className="label">Speed:</span>
                <span className="value">{vehicleData.latest_telemetry.speed} km/h</span>
              </div>
            </div>
            <p className="timestamp">
              Last updated: {new Date(vehicleData.timestamp).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
  } catch (error) {
    console.error('Error rendering vehicle visualization:', error);
    return (
      <div className="vehicle-viz-modal">
        <div className="vehicle-viz-content">
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
          <div style={{ padding: '2rem', color: '#fff' }}>
            <p>Error rendering vehicle visualization</p>
            <p style={{ fontSize: '12px', marginTop: '1rem', color: '#ef4444' }}>
              {error.toString()}
            </p>
          </div>
        </div>
      </div>
    );
  }
}
