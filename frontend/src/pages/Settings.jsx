export default function Settings() {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Settings</h1>
      <p style={{ color: '#9ca3af' }}>Application settings and configuration - Coming soon</p>
      <div style={{ background: '#1e293b', padding: '2rem', borderRadius: '0.75rem', marginTop: '2rem' }}>
        <h3>Twilio Configuration:</h3>
        <ul style={{ color: '#9ca3af', fontFamily: 'monospace', fontSize: '0.875rem' }}>
          <li>Account SID: [Configured securely]</li>
          <li>Phone Number: [Configured securely]</li>
          <li>Status: ✅ Active</li>
        </ul>
        
        <h3 style={{ marginTop: '2rem' }}>Features:</h3>
        <ul style={{ color: '#9ca3af' }}>
          <li>Notification preferences</li>
          <li>Alert thresholds</li>
          <li>User management</li>
          <li>API configuration</li>
        </ul>
      </div>
    </div>
  );
}
