import { useState, useEffect } from 'react';
import { X, AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import { getVehicleDetails } from '../utils/api';

export default function VehicleVisualizationSimple({ vehicleId, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [hoveredComponent, setHoveredComponent] = useState(null);

  useEffect(() => {
    fetchData();
  }, [vehicleId]);

  const fetchData = async () => {
    try {
      const response = await getVehicleDetails(vehicleId);
      setData(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    if (status === 'critical') return <AlertTriangle size={18} />;
    if (status === 'warning') return <AlertCircle size={18} />;
    return <CheckCircle size={18} />;
  };

  const getComponentColor = (componentName) => {
    const component = data?.components?.[componentName];
    if (!component) return '#64748b';
    if (component.status === 'critical') return '#ef4444';
    if (component.status === 'warning') return '#f59e0b';
    return '#22c55e';
  };

  const getComponentOpacity = (componentName) => {
    if (!hoveredComponent) return 0.6;
    return hoveredComponent === componentName ? 0.9 : 0.3;
  };

  // Detect if vehicle is a motorcycle
  const isMotorcycle = data?.vehicle?.make?.toLowerCase().includes('hero') || 
                       data?.vehicle?.model?.toLowerCase().includes('bike') ||
                       data?.vehicle?.model?.toLowerCase().includes('motorcycle');

  // Component clickable areas mapped to vehicle parts
  const componentAreas = isMotorcycle ? {
    // Motorcycle component mapping
    engine: { x: 210, y: 110, width: 90, height: 80, label: 'Engine' },
    transmission: { x: 250, y: 130, width: 70, height: 60, label: 'Transmission' },
    brakes: { x: 60, y: 110, width: 60, height: 60, label: 'Brakes' },
    battery: { x: 180, y: 70, width: 60, height: 40, label: 'Battery' },
    cooling_system: { x: 290, y: 100, width: 60, height: 50, label: 'Cooling' },
    oil_system: { x: 200, y: 160, width: 70, height: 40, label: 'Oil System' },
    suspension: { x: 80, y: 80, width: 60, height: 50, label: 'Suspension' },
    tires: { x: 270, y: 110, width: 100, height: 70, label: 'Tires' },
    exhaust: { x: 250, y: 180, width: 100, height: 30, label: 'Exhaust' },
    fuel_system: { x: 330, y: 60, width: 60, height: 55, label: 'Fuel System' }
  } : {
    // Car component mapping
    engine: { x: 230, y: 70, width: 80, height: 60, label: 'Engine' },
    transmission: { x: 190, y: 100, width: 70, height: 50, label: 'Transmission' },
    brakes: { x: 100, y: 150, width: 60, height: 60, label: 'Brakes' },
    battery: { x: 70, y: 80, width: 50, height: 40, label: 'Battery' },
    cooling_system: { x: 400, y: 80, width: 60, height: 45, label: 'Cooling' },
    oil_system: { x: 270, y: 110, width: 50, height: 40, label: 'Oil System' },
    suspension: { x: 150, y: 165, width: 70, height: 40, label: 'Suspension' },
    tires: { x: 320, y: 160, width: 80, height: 50, label: 'Tires' },
    exhaust: { x: 40, y: 110, width: 60, height: 35, label: 'Exhaust' },
    fuel_system: { x: 330, y: 100, width: 60, height: 45, label: 'Fuel System' }
  };

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.85)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
          borderRadius: '1rem',
          padding: '2rem',
          maxWidth: '1100px',
          width: '95%',
          maxHeight: '90vh',
          overflow: 'auto',
          position: 'relative',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
          border: '1px solid #475569'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.5rem',
            right: '1.5rem',
            background: '#374151',
            border: 'none',
            borderRadius: '0.5rem',
            padding: '0.75rem',
            cursor: 'pointer',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = '#4b5563'}
          onMouseOut={(e) => e.currentTarget.style.background = '#374151'}
        >
          <X size={24} />
        </button>

        {loading && (
          <div style={{ color: '#fff', padding: '4rem', textAlign: 'center', fontSize: '1.2rem' }}>
            <div style={{ display: 'inline-block', width: '40px', height: '40px', border: '4px solid #475569', borderTopColor: '#3b82f6', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            <div style={{ marginTop: '1rem' }}>Loading vehicle data...</div>
          </div>
        )}
        
        {error && (
          <div style={{ color: '#fff', padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <AlertTriangle size={32} color="#ef4444" />
              <h3 style={{ margin: 0, fontSize: '1.5rem' }}>Error Loading Data</h3>
            </div>
            <p style={{ color: '#ef4444', background: '#7f1d1d', padding: '1rem', borderRadius: '0.5rem' }}>{error}</p>
          </div>
        )}

        {data && (
          <div style={{ color: '#fff' }}>
            {/* Header */}
            <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '2px solid #475569' }}>
              <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '2rem', fontWeight: '700' }}>
                {data.vehicle?.make} {data.vehicle?.model}
              </h2>
              <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', fontSize: '0.95rem', color: '#94a3b8' }}>
                <div><span style={{ color: '#64748b' }}>VIN:</span> <span style={{ color: '#e2e8f0' }}>{data.vehicle?.vin}</span></div>
                <div><span style={{ color: '#64748b' }}>Year:</span> <span style={{ color: '#e2e8f0' }}>{data.vehicle?.year}</span></div>
                <div><span style={{ color: '#64748b' }}>Mileage:</span> <span style={{ color: '#e2e8f0' }}>{data.vehicle?.mileage?.toLocaleString()} km</span></div>
              </div>
            </div>

            {/* Interactive Car Visualization */}
            <div style={{
              background: '#1e293b',
              padding: '2rem',
              borderRadius: '0.75rem',
              marginBottom: '2rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              border: '1px solid #334155'
            }}>
              <h3 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', textAlign: 'center' }}>
                Interactive Component Map - Click on highlighted areas
              </h3>
              <div style={{ position: 'relative' }}>
                {isMotorcycle ? (
                  // Motorcycle SVG
                  <svg width="500" height="300" viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id="motoBodyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style={{ stopColor: '#e2e8f0', stopOpacity: 1 }} />
                        <stop offset="50%" style={{ stopColor: '#f8fafc', stopOpacity: 1 }} />
                        <stop offset="100%" style={{ stopColor: '#cbd5e1', stopOpacity: 1 }} />
                      </linearGradient>

                      <linearGradient id="motoWindGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style={{ stopColor: '#0f172a', stopOpacity: 0.8 }} />
                        <stop offset="100%" style={{ stopColor: '#334155', stopOpacity: 0.6 }} />
                      </linearGradient>

                      <radialGradient id="motoRimGrad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                        <stop offset="0%" style={{ stopColor: '#94a3b8', stopOpacity: 1 }} />
                        <stop offset="100%" style={{ stopColor: '#475569', stopOpacity: 1 }} />
                      </radialGradient>
                      
                      <linearGradient id="engineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style={{ stopColor: '#475569', stopOpacity: 1 }} />
                        <stop offset="100%" style={{ stopColor: '#1e293b', stopOpacity: 1 }} />
                      </linearGradient>
                      
                      <filter id="motoGlow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>

                    <ellipse cx="250" cy="245" rx="180" ry="15" fill="#0f172a" opacity="0.4" />

                    <g transform="translate(50, 50)">
                      {/* Swing Arm */}
                      <path d="M 200,180 Q 250,200 350,180 L 360,160 L 340,160 Q 250,180 200,160 Z" fill="#64748b" />

                      {/* Rear Wheel */}
                      <g transform="translate(320, 160)">
                        <circle r="55" fill="#1e293b" />
                        <circle r="35" fill="url(#motoRimGrad)" stroke="#cbd5e1" strokeWidth="2" />
                        <circle r="15" fill="none" stroke="#cbd5e1" strokeWidth="3" strokeDasharray="5,5"/>
                        <circle r="8" fill="#1e293b" />
                      </g>

                      {/* Engine Block */}
                      <path d="M 160,110 L 280,120 L 260,180 L 180,170 Z" fill="url(#engineGrad)" stroke="#334155" />

                      {/* Body/Fuel Tank */}
                      <path d="M 340,110 
                               Q 360,100 380,105 L 320,160 L 260,150 
                               L 180,180 L 110,160 L 130,80  Q 140,60 180,65 L 240,70 Q 280,60 300,100 L 340,110 Z" 
                            fill="url(#motoBodyGrad)" stroke="#94a3b8" strokeWidth="1"/>

                      {/* Seat */}
                      <path d="M 290,95 Q 310,105 340,110 L 350,100 Q 320,90 295,90 Z" fill="#334155" />

                      {/* Windshield */}
                      <path d="M 135,75 Q 150,30 190,45 L 180,65 Z" fill="url(#motoWindGrad)" stroke="#94a3b8" strokeWidth="1"/>
                      
                      {/* Handlebars */}
                      <polyline points="170,70 190,60 210,65" fill="none" stroke="#334155" strokeWidth="3" strokeLinecap="round"/>

                      {/* Front Wheel and Fork */}
                      <g transform="translate(110, 160)">
                        <circle r="55" fill="#1e293b" />
                        <circle r="35" fill="url(#motoRimGrad)" stroke="#cbd5e1" strokeWidth="2" />
                        <circle r="20" fill="none" stroke="#cbd5e1" strokeWidth="3" strokeDasharray="5,5"/>
                        <circle r="8" fill="#1e293b" />
                        <rect x="-5" y="-60" width="10" height="60" fill="#cbd5e1" />
                      </g>

                      {/* Headlight */}
                      <ellipse cx="145" cy="68" rx="8" ry="5" fill="#38bdf8" filter="url(#motoGlow)" transform="rotate(-20 145 68)"/>
                      
                      {/* Taillight */}
                      <ellipse cx="375" cy="105" rx="5" ry="8" fill="#ef4444" filter="url(#motoGlow)" transform="rotate(-30 375 105)"/>

                      {/* Interactive Component Areas */}
                      {Object.entries(componentAreas).map(([name, area]) => (
                        <g key={name}>
                          <rect
                            x={area.x}
                            y={area.y}
                            width={area.width}
                            height={area.height}
                            fill={getComponentColor(name)}
                            opacity={getComponentOpacity(name)}
                            stroke={hoveredComponent === name ? 'white' : 'transparent'}
                            strokeWidth="3"
                            rx="6"
                            style={{
                              cursor: 'pointer',
                              transition: 'all 0.3s ease'
                            }}
                            onMouseEnter={() => setHoveredComponent(name)}
                            onMouseLeave={() => setHoveredComponent(null)}
                            onClick={() => setSelectedComponent(selectedComponent === name ? null : name)}
                          />
                          {hoveredComponent === name && (
                            <text
                              x={area.x + area.width / 2}
                              y={area.y - 8}
                              textAnchor="middle"
                              fill="white"
                              fontSize="14"
                              fontWeight="bold"
                              style={{ pointerEvents: 'none' }}
                            >
                              {area.label}
                            </text>
                          )}
                        </g>
                      ))}
                    </g>
                  </svg>
                ) : (
                  // Car SVG
                  <svg width="500" height="250" viewBox="0 0 500 250" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" style={{ stopColor: '#e2e8f0', stopOpacity: 1 }} />
                      <stop offset="50%" style={{ stopColor: '#f8fafc', stopOpacity: 1 }} />
                      <stop offset="100%" style={{ stopColor: '#cbd5e1', stopOpacity: 1 }} />
                    </linearGradient>

                    <linearGradient id="windowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" style={{ stopColor: '#0f172a', stopOpacity: 0.9 }} />
                      <stop offset="100%" style={{ stopColor: '#334155', stopOpacity: 0.8 }} />
                    </linearGradient>

                    <radialGradient id="rimGrad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                      <stop offset="0%" style={{ stopColor: '#94a3b8', stopOpacity: 1 }} />
                      <stop offset="100%" style={{ stopColor: '#475569', stopOpacity: 1 }} />
                    </radialGradient>
                    
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>

                  <ellipse cx="250" cy="195" rx="210" ry="15" fill="#0f172a" opacity="0.4" />

                  <g transform="translate(20, 40)">
                    {/* Car Body */}
                    <path d="M 10,110 
                             Q 10,80 40,75 
                             L 110,70 
                             L 150,30 
                             Q 170,10 280,10 
                             L 330,12 
                             Q 390,15 410,70 
                             L 440,75 
                             Q 460,80 460,110 
                             L 460,135 
                             Q 460,150 440,150 
                             L 395,150 
                             A 45,45 0 0,1 305,150 
                             L 165,150 
                             A 45,45 0 0,1 75,150 
                             L 30,150 
                             Q 10,150 10,130 Z" 
                          fill="url(#bodyGrad)" stroke="#94a3b8" strokeWidth="1"/>

                    {/* Window */}
                    <path d="M 155,35 
                             L 280,35 
                             L 330,37 
                             Q 370,40 385,70 
                             L 125,70 
                             Z" 
                          fill="url(#windowGrad)" stroke="#cbd5e1" strokeWidth="2"/>
                    
                    {/* Body Line */}
                    <path d="M 40,95 L 430,95" stroke="#94a3b8" strokeWidth="2" strokeOpacity="0.5"/>
                    
                    {/* Door Handle */}
                    <rect x="250" y="92" width="25" height="4" rx="2" fill="#94a3b8" />

                    {/* Headlight */}
                    <path d="M 435,78 Q 455,85 455,100 L 440,100 Z" fill="#38bdf8" filter="url(#glow)" />
                    
                    {/* Taillight */}
                    <path d="M 10,95 Q 10,80 25,80 L 25,105 Z" fill="#ef4444" filter="url(#glow)" />

                    {/* Front Wheel */}
                    <g transform="translate(120, 150)">
                      <circle r="40" fill="#1e293b" />
                      <circle r="25" fill="url(#rimGrad)" stroke="#cbd5e1" strokeWidth="2" />
                      <circle r="5" fill="#1e293b" />
                      <line x1="0" y1="-25" x2="0" y2="25" stroke="#1e293b" strokeWidth="4" />
                      <line x1="-22" y1="-12" x2="22" y2="12" stroke="#1e293b" strokeWidth="4" />
                      <line x1="22" y1="-12" x2="-22" y2="12" stroke="#1e293b" strokeWidth="4" />
                    </g>

                    {/* Rear Wheel */}
                    <g transform="translate(350, 150)">
                      <circle r="40" fill="#1e293b" />
                      <circle r="25" fill="url(#rimGrad)" stroke="#cbd5e1" strokeWidth="2" />
                      <circle r="5" fill="#1e293b" />
                      <line x1="0" y1="-25" x2="0" y2="25" stroke="#1e293b" strokeWidth="4" />
                      <line x1="-22" y1="-12" x2="22" y2="12" stroke="#1e293b" strokeWidth="4" />
                      <line x1="22" y1="-12" x2="-22" y2="12" stroke="#1e293b" strokeWidth="4" />
                    </g>

                    {/* Interactive Component Areas */}
                    {Object.entries(componentAreas).map(([name, area]) => (
                      <g key={name}>
                        <rect
                          x={area.x}
                          y={area.y}
                          width={area.width}
                          height={area.height}
                          fill={getComponentColor(name)}
                          opacity={getComponentOpacity(name)}
                          stroke={hoveredComponent === name ? 'white' : 'transparent'}
                          strokeWidth="3"
                          rx="6"
                          style={{
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                          }}
                          onMouseEnter={() => setHoveredComponent(name)}
                          onMouseLeave={() => setHoveredComponent(null)}
                          onClick={() => setSelectedComponent(selectedComponent === name ? null : name)}
                        />
                        {hoveredComponent === name && (
                          <text
                            x={area.x + area.width / 2}
                            y={area.y - 8}
                            textAnchor="middle"
                            fill="white"
                            fontSize="14"
                            fontWeight="bold"
                            style={{ pointerEvents: 'none' }}
                          >
                            {area.label}
                          </text>
                        )}
                      </g>
                      ))}
                    </g>
                  </svg>
                )}

                {/* Legend */}
                <div style={{
                  marginTop: '1rem',
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '1.5rem',
                  fontSize: '0.875rem',
                  color: '#94a3b8'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '20px', height: '20px', backgroundColor: '#22c55e', borderRadius: '3px', opacity: 0.7 }}></div>
                    <span>Healthy</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '20px', height: '20px', backgroundColor: '#f59e0b', borderRadius: '3px', opacity: 0.7 }}></div>
                    <span>Warning</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '20px', height: '20px', backgroundColor: '#ef4444', borderRadius: '3px', opacity: 0.7 }}></div>
                    <span>Critical</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Health Summary */}
            <div style={{ 
              background: data.health?.overall_status === 'critical' ? 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)' : 
                         data.health?.overall_status === 'warning' ? 'linear-gradient(135deg, #78350f 0%, #92400e 100%)' : 
                         'linear-gradient(135deg, #14532d 0%, #166534 100%)',
              padding: '1.5rem',
              borderRadius: '0.75rem',
              marginBottom: '2rem',
              border: `2px solid ${data.health?.overall_status === 'critical' ? '#ef4444' : 
                                    data.health?.overall_status === 'warning' ? '#f59e0b' : '#22c55e'}`
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    {getStatusIcon(data.health?.overall_status)}
                    <h3 style={{ margin: 0, fontSize: '1.5rem', textTransform: 'capitalize' }}>
                      {data.health?.overall_status} Status
                    </h3>
                  </div>
                  <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{data.health?.overall_score}%</div>
                </div>
                <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>{data.health?.critical_components}</div>
                    <div style={{ fontSize: '0.875rem', color: '#fca5a5' }}>Critical</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>{data.health?.warning_components}</div>
                    <div style={{ fontSize: '0.875rem', color: '#fbbf24' }}>Warning</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#22c55e' }}>{data.health?.healthy_components}</div>
                    <div style={{ fontSize: '0.875rem', color: '#86efac' }}>Healthy</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Components Grid */}
            <div>
              <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Component Health Status
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {data.components && Object.entries(data.components).map(([name, component]) => (
                  <div 
                    key={name}
                    onClick={() => setSelectedComponent(selectedComponent === name ? null : name)}
                    style={{
                      background: component.status === 'critical' ? 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)' : 
                                 component.status === 'warning' ? 'linear-gradient(135deg, #78350f 0%, #92400e 100%)' : 
                                 'linear-gradient(135deg, #14532d 0%, #166534 100%)',
                      padding: '1.25rem',
                      borderRadius: '0.75rem',
                      border: `2px solid ${component.status === 'critical' ? '#ef4444' : 
                                           component.status === 'warning' ? '#f59e0b' : '#22c55e'}`,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      transform: selectedComponent === name ? 'scale(1.02)' : 'scale(1)',
                      boxShadow: selectedComponent === name ? '0 8px 20px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.2)'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                    onMouseOut={(e) => e.currentTarget.style.transform = selectedComponent === name ? 'scale(1.02)' : 'scale(1)'}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <div style={{ fontWeight: 'bold', fontSize: '1.1rem', textTransform: 'capitalize' }}>
                        {name.replace(/_/g, ' ')}
                      </div>
                      {getStatusIcon(component.status)}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{component.health}%</div>
                      <div style={{ fontSize: '0.875rem', color: '#cbd5e1', textTransform: 'capitalize' }}>{component.status}</div>
                    </div>
                    {component.issues && component.issues.length > 0 && (
                      <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                        <div style={{ fontSize: '0.875rem', color: '#fca5a5', fontWeight: '600', marginBottom: '0.5rem' }}>
                          ⚠️ {component.issues.length} Issue{component.issues.length > 1 ? 's' : ''} Detected
                        </div>
                        {selectedComponent === name && component.issues.map((issue, idx) => (
                          <div key={idx} style={{ fontSize: '0.8rem', color: '#e2e8f0', marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '0.375rem' }}>
                            <div><strong>Probability:</strong> {issue.probability}</div>
                            <div><strong>Days to Failure:</strong> ~{issue.estimated_days}</div>
                            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                              Severity: {issue.severity}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Legend */}
            <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '0.5rem', display: 'flex', gap: '2rem', flexWrap: 'wrap', justifyContent: 'center', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '16px', height: '16px', background: '#22c55e', borderRadius: '3px' }}></div>
                <span>Healthy (≥80%)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '16px', height: '16px', background: '#f59e0b', borderRadius: '3px' }}></div>
                <span>Warning (50-79%)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '16px', height: '16px', background: '#ef4444', borderRadius: '3px' }}></div>
                <span>Critical (&lt;50%)</span>
              </div>
              <div style={{ color: '#94a3b8', marginLeft: 'auto' }}>Click components for details</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
