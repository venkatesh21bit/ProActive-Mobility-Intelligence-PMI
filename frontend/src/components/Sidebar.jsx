import { NavLink } from 'react-router-dom';
import { Home, Car, AlertTriangle, Calendar, Bell, BarChart, Activity, Settings } from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ isOpen, toggleSidebar }) {
  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/vehicles', icon: Car, label: 'Fleet Management' },
    { path: '/alerts', icon: AlertTriangle, label: 'Alerts' },
    { path: '/appointments', icon: Calendar, label: 'Service Appointments' },
    { path: '/notifications', icon: Bell, label: 'Notifications' },
    { path: '/analytics', icon: BarChart, label: 'Analytics' },
    { path: '/agents', icon: Activity, label: 'System Status' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={toggleSidebar} />}
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
            <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold', color: '#fff', marginBottom: '0.25rem' }}>Hero MotoCorp</h2>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8', fontWeight: '500', letterSpacing: '0.05em' }}>SERVICE CENTER PORTAL</p>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `nav-item ${isActive ? 'active' : ''}`
                }
                onClick={() => window.innerWidth < 768 && toggleSidebar()}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
