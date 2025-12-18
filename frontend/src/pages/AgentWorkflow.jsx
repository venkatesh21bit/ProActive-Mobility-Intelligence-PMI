import { useState, useEffect } from 'react';
import { Activity, TrendingUp, AlertTriangle, Bell, Calendar, Database, Cpu, MessageSquare, Phone, CheckCircle, ArrowRight } from 'lucide-react';
import { getAgentStatus, getActivityLogs } from '../utils/api';

export default function AgentWorkflow() {
  const [activeStep, setActiveStep] = useState(0);
  const [agentLogs, setAgentLogs] = useState([]);
  const [workflow, setWorkflow] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Icon mapping for agents
  const iconMap = {
    'Data Ingestion Agent': Database,
    'ML Prediction Agent': Cpu,
    'Alert Manager': AlertTriangle,
    'Notification Agent': MessageSquare,
    'Scheduler Agent': Calendar,
    'Analytics Agent': TrendingUp
  };

  // Color mapping for agents
  const colorMap = {
    'Data Ingestion Agent': '#3b82f6',
    'ML Prediction Agent': '#8b5cf6',
    'Alert Manager': '#ef4444',
    'Notification Agent': '#10b981',
    'Scheduler Agent': '#f59e0b',
    'Analytics Agent': '#06b6d4'
  };

  // Fetch agent status and activity logs from backend
  const fetchData = async () => {
    try {
      const [statusResponse, logsResponse] = await Promise.all([
        getAgentStatus(),
        getActivityLogs(15)
      ]);

      console.log('Full logs response:', logsResponse);
      console.log('Logs data type:', typeof logsResponse.data);
      console.log('Logs data is array:', Array.isArray(logsResponse.data));
      console.log('Logs data:', logsResponse.data);

      // Transform backend data to workflow format
      const transformedWorkflow = statusResponse.data.agents.map((agent, idx) => ({
        id: idx + 1,
        name: agent.name.replace(' Agent', ''),
        agent: agent.name,
        icon: iconMap[agent.name] || Activity,
        description: agent.description,
        status: agent.status,
        metrics: agent.metrics,
        color: colorMap[agent.name] || '#64748b'
      }));

      setWorkflow(transformedWorkflow);
      
      // Set logs directly from the response
      const logsArray = Array.isArray(logsResponse.data) ? logsResponse.data : [];
      console.log('Setting logs array:', logsArray);
      console.log('Logs array length:', logsArray.length);
      
      setAgentLogs(logsArray);
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching agent data:', err);
      console.error('Error details:', err.response);
      setError('Failed to load agent workflow data');
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Cycle through workflow steps
    const stepInterval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % (workflow.length || 6));
    }, 3000);

    // Refresh data every 10 seconds
    const dataInterval = setInterval(fetchData, 10000);

    return () => {
      clearInterval(stepInterval);
      clearInterval(dataInterval);
    };
  }, [workflow.length]);

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', margin: 0 }}>🤖 Agent Workflow Visualization</h1>
        <p style={{ color: '#9ca3af', marginTop: '0.5rem' }}>
          Real-time view of how AI agents work together to predict and prevent vehicle failures
        </p>
      </div>

      {/* Workflow Pipeline */}
      <div style={{ 
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', 
        borderRadius: '1rem', 
        padding: '2rem', 
        marginBottom: '2rem',
        border: '1px solid #2d3748'
      }}>
        <h2 style={{ margin: '0 0 2rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Activity size={28} />
          Multi-Agent Pipeline
        </h2>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', overflowX: 'auto', paddingBottom: '1rem' }}>
          {workflow.map((step, idx) => {
            const Icon = step.icon;
            const isActive = idx === activeStep;
            return (
              <div key={step.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div
                  style={{
                    minWidth: '280px',
                    background: isActive ? `linear-gradient(135deg, ${step.color}20, ${step.color}10)` : '#1e293b',
                    border: isActive ? `2px solid ${step.color}` : '1px solid #2d3748',
                    borderRadius: '1rem',
                    padding: '1.5rem',
                    transition: 'all 0.3s',
                    transform: isActive ? 'scale(1.05)' : 'scale(1)',
                    boxShadow: isActive ? `0 0 30px ${step.color}40` : 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                    <div style={{ 
                      width: '48px', 
                      height: '48px', 
                      borderRadius: '0.75rem', 
                      background: `${step.color}20`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Icon size={24} color={step.color} />
                    </div>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '1rem', color: step.color }}>{step.name}</h3>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: '#9ca3af' }}>{step.agent}</p>
                    </div>
                  </div>
                  
                  <p style={{ fontSize: '0.875rem', color: '#e5e7eb', marginBottom: '1rem', minHeight: '60px' }}>
                    {step.description}
                  </p>
                  
                  <div style={{ 
                    background: '#0f172a', 
                    borderRadius: '0.5rem', 
                    padding: '0.75rem',
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '0.5rem'
                  }}>
                    {Object.entries(step.metrics).map(([key, value]) => (
                      <div key={key}>
                        <p style={{ margin: 0, fontSize: '0.75rem', color: '#9ca3af', textTransform: 'capitalize' }}>
                          {key.replace('_', ' ')}
                        </p>
                        <p style={{ margin: '0.25rem 0 0 0', fontSize: '1rem', fontWeight: '600', color: '#fff' }}>
                          {value}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ 
                      width: '8px', 
                      height: '8px', 
                      borderRadius: '50%', 
                      background: step.status === 'active' ? '#22c55e' : '#f59e0b',
                      animation: step.status === 'active' ? 'pulse 2s infinite' : 'none'
                    }}></div>
                    <span style={{ fontSize: '0.75rem', color: step.status === 'active' ? '#22c55e' : '#f59e0b', textTransform: 'uppercase', fontWeight: '600' }}>
                      {step.status}
                    </span>
                  </div>
                </div>
                
                {idx < workflow.length - 1 && (
                  <ArrowRight size={32} color="#4b5563" style={{ flexShrink: 0 }} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Agent Logs */}
      <div style={{ 
        background: '#1e293b', 
        borderRadius: '1rem', 
        padding: '2rem',
        border: '1px solid #2d3748',
        marginBottom: '2rem'
      }}>
        <h2 style={{ margin: '0 0 1.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Activity size={24} />
          Live Agent Activity Logs
          <span style={{ fontSize: '0.875rem', color: '#9ca3af', fontWeight: 'normal' }}>
            (Last 15)
          </span>
          <span style={{ 
            marginLeft: 'auto', 
            background: 'rgba(34, 197, 94, 0.2)', 
            padding: '0.25rem 0.75rem', 
            borderRadius: '9999px', 
            fontSize: '0.875rem',
            color: '#22c55e',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span style={{ width: '6px', height: '6px', background: '#22c55e', borderRadius: '50%', animation: 'pulse 1.5s infinite' }}></span>
            Live
          </span>
        </h2>
        
        <div style={{ 
          background: '#0f172a', 
          borderRadius: '0.75rem', 
          padding: '1rem',
          maxHeight: '400px',
          overflowY: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.875rem'
        }}>
          {agentLogs.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
              <p>Waiting for agent activity...</p>
              <p style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>
                Logs count: {agentLogs.length}
              </p>
            </div>
          ) : (
            agentLogs.map((log, idx) => (
              <div 
                key={idx} 
                style={{ 
                  padding: '0.75rem',
                  borderBottom: idx < agentLogs.length - 1 ? '1px solid #1e293b' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  animation: idx === 0 ? 'slideIn 0.3s ease-out' : 'none'
                }}
              >
                <span style={{ color: '#6b7280', minWidth: '80px' }}>{log.timestamp}</span>
                <span style={{ 
                  color: log.type === 'warning' ? '#f59e0b' : '#6366f1',
                  fontWeight: '600',
                  minWidth: '200px'
                }}>
                  [{log.agent}]
                </span>
                <span style={{ color: '#e5e7eb' }}>{log.message}</span>
                <CheckCircle size={16} color="#22c55e" style={{ marginLeft: 'auto' }} />
              </div>
            ))
          )}
        </div>
      </div>

      {/* Agent Architecture */}
      <div style={{ 
        background: '#1e293b', 
        borderRadius: '1rem', 
        padding: '2rem',
        border: '1px solid #2d3748'
      }}>
        <h2 style={{ margin: '0 0 1.5rem 0' }}>🏗️ System Architecture</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div style={{ background: '#0f172a', borderRadius: '0.75rem', padding: '1.5rem', border: '1px solid #2d3748' }}>
            <h3 style={{ color: '#3b82f6', marginBottom: '1rem' }}>Data Layer</h3>
            <ul style={{ color: '#9ca3af', fontSize: '0.875rem', lineHeight: '1.8' }}>
              <li>PostgreSQL - Vehicle & telemetry data</li>
              <li>Redis - Real-time caching</li>
              <li>MinIO - ML model storage</li>
            </ul>
          </div>
          
          <div style={{ background: '#0f172a', borderRadius: '0.75rem', padding: '1.5rem', border: '1px solid #2d3748' }}>
            <h3 style={{ color: '#8b5cf6', marginBottom: '1rem' }}>AI/ML Layer</h3>
            <ul style={{ color: '#9ca3af', fontSize: '0.875rem', lineHeight: '1.8' }}>
              <li>MLflow - Model tracking</li>
              <li>Ray - Distributed ML training</li>
              <li>TensorFlow/PyTorch models</li>
            </ul>
          </div>
          
          <div style={{ background: '#0f172a', borderRadius: '0.75rem', padding: '1.5rem', border: '1px solid #2d3748' }}>
            <h3 style={{ color: '#10b981', marginBottom: '1rem' }}>Integration Layer</h3>
            <ul style={{ color: '#9ca3af', fontSize: '0.875rem', lineHeight: '1.8' }}>
              <li>Twilio - SMS & Voice alerts</li>
              <li>FastAPI - REST APIs</li>
              <li>Google Cloud Run - Deployment</li>
            </ul>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}
