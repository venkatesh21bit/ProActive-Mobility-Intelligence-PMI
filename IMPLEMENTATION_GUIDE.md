# ProActive Mobility Intelligence - Advanced Dashboard Implementation Guide

## ✅ COMPLETED BACKEND ENHANCEMENTS

### 1. Twilio Integration (services/notification_service.py)
- ✅ NotificationService class with SMS and voice call capabilities
- ✅ Methods: send_failure_alert_sms(), send_maintenance_reminder_sms(), make_emergency_call()
- ✅ Notification history tracking in database
- ✅ Mark as read functionality

### 2. New API Endpoints

#### Notifications API (api/notifications.py)
- `POST /api/notifications/send-alert` - Send SMS or voice alert for failure
- `POST /api/notifications/send-reminder/{appointment_id}` - Send appointment reminder
- `GET /api/notifications/history` - Get notification history with filters  
- `PUT /api/notifications/{notification_id}/read` - Mark as read
- `GET /api/notifications/stats` - Get notification statistics
- `POST /api/notifications/auto-alert-critical` - Auto-send alerts for critical predictions

#### Appointments API (api/appointments.py)
- `POST /api/appointments/create` - Create new appointment
- `GET /api/appointments/list` - List with filters (status, customer, vehicle, dates)
- `GET /api/appointments/{id}` - Get appointment details
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment
- `GET /api/appointments/service-centers/available` - Get available centers for time slot

#### Analytics API (api/analytics.py)
- `GET /api/analytics/fleet-health-trend` - Fleet health over time
- `GET /api/analytics/component-failures` - Failure stats by component
- `GET /api/analytics/maintenance-costs` - Cost analysis by month
- `GET /api/analytics/prediction-accuracy` - ML model accuracy metrics
- `GET /api/analytics/vehicle-risk-scores` - Risk scores for all vehicles
- `GET /api/analytics/fleet-summary` - Comprehensive summary

### 3. Updated Main Service
- ✅ All routers registered in ingestion_service.py
- ✅ Twilio already in requirements.txt

## 📋 REQUIRED FRONTEND IMPLEMENTATION

### Project Structure Needed
```
frontend/src/
├── components/
│   ├── Sidebar.jsx                    # Navigation sidebar
│   ├── Header.jsx                     # Top navigation bar
│   ├── StatsCard.jsx                  # Reusable stat card
│   ├── VehicleCard.jsx                # Vehicle info card
│   ├── AlertCard.jsx                  # Alert display card
│   ├── NotificationItem.jsx           # Single notification
│   ├── AppointmentCard.jsx            # Appointment card
│   └── Modal.jsx                      # Reusable modal
├── pages/
│   ├── Dashboard.jsx                  # Main dashboard (move current App.jsx content)
│   ├── Vehicles.jsx                   # Vehicle management
│   ├── Alerts.jsx                     # Alert management
│   ├── Appointments.jsx               # Appointment scheduling
│   ├── Notifications.jsx              # Notification center with Twilio
│   ├── Analytics.jsx                  # Charts and insights
│   └── Settings.jsx                   # App settings
├── utils/
│   ├── api.js                         # Axios instance and API calls
│   ├── helpers.js                     # Utility functions
│   └── constants.js                   # Constants
├── App.jsx                            # ✅ DONE - Router setup
├── App.css                            # Enhanced styles needed
└── main.jsx                           # Entry point

```

### Key Components to Create

#### 1. Sidebar.jsx
```jsx
import { NavLink } from 'react-router-dom';
import { Home, Car, AlertTriangle, Calendar, Bell, BarChart, Settings } from 'lucide-react';

export default function Sidebar({ isOpen, toggleSidebar }) {
  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/vehicles', icon: Car, label: 'Vehicles' },
    { path: '/alerts', icon: AlertTriangle, label: 'Alerts' },
    { path: '/appointments', icon: Calendar, label: 'Appointments' },
    { path: '/notifications', icon: Bell, label: 'Notifications' },
    { path: '/analytics', icon: BarChart, label: 'Analytics' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      {/* Navigation items with active state */}
    </aside>
  );
}
```

#### 2. Dashboard.jsx (Main Page)
- Move current App.jsx content here
- Add stats cards, alerts list, vehicles table
- Auto-refresh every 30s
- Add interactive buttons

#### 3. Notifications.jsx (KEY PAGE - TWILIO)
```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { MessageSquare, Phone, Send, CheckCircle } from 'lucide-react';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [sending, setSending] = useState(false);

  // Fetch notification history
  useEffect(() => {
    fetchNotifications();
    fetchStats();
  }, []);

  const sendSMSAlert = async (customerId, vehicleId, predictionId) => {
    setSending(true);
    try {
      const res = await axios.post('/api/notifications/send-alert', {
        customer_id: customerId,
        vehicle_id: vehicleId,
        prediction_id: predictionId,
        channel: 'sms'
      });
      alert(`SMS sent successfully! Notification ID: ${res.data.notification_id}`);
      fetchNotifications(); // Refresh
    } catch (error) {
      alert('Failed to send SMS: ' + error.message);
    } finally {
      setSending(false);
    }
  };

  const makeVoiceCall = async (customerId, vehicleId, predictionId) => {
    // Similar to SMS but channel: 'voice'
  };

  return (
    <div className="page">
      <h1>Notification Center</h1>
      
      {/* Stats */}
      <div className="stats-grid">
        <StatsCard label="Total Sent" value={stats.total_sent} icon={Send} />
        <StatsCard label="SMS Sent" value={stats.sms_sent} icon={MessageSquare} />
        <StatsCard label="Voice Calls" value={stats.voice_calls} icon={Phone} />
        <StatsCard label="Delivered" value={stats.delivered} icon={CheckCircle} />
      </div>

      {/* Send Alert Section */}
      <section className="send-alert-section">
        <h2>Send Alert</h2>
        {/* Form to select vehicle and send SMS/call */}
      </section>

      {/* History */}
      <section className="notification-history">
        <h2>Notification History</h2>
        {notifications.map(notif => (
          <NotificationItem key={notif.notification_id} notification={notif} />
        ))}
      </section>
    </div>
  );
}
```

#### 4. Appointments.jsx
```jsx
import { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Plus } from 'lucide-react';
import axios from 'axios';

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [serviceCenters, setServiceCenters] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const createAppointment = async (appointmentData) => {
    const res = await axios.post('/api/appointments/create', appointmentData);
    alert('Appointment created!');
    fetchAppointments();
  };

  const cancelAppointment = async (id) => {
    await axios.delete(`/api/appointments/${id}`);
    fetchAppointments();
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Appointments</h1>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={16} /> New Appointment
        </button>
      </div>

      {/* Calendar view or list view */}
      {/* Appointment cards with status, vehicle, time */}
      {/* Modal for creating/editing appointments */}
    </div>
  );
}
```

#### 5. Analytics.jsx (CHARTS)
```jsx
import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

export default function Analytics() {
  const [fleetTrend, setFleetTrend] = useState([]);
  const [componentStats, setComponentStats] = useState([]);
  const [costAnalysis, setCostAnalysis] = useState([]);
  const [riskScores, setRiskScores] = useState([]);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    const [trend, comp, cost, risk] = await Promise.all([
      axios.get('/api/analytics/fleet-health-trend?days=30'),
      axios.get('/api/analytics/component-failures?days=90'),
      axios.get('/api/analytics/maintenance-costs?months=12'),
      axios.get('/api/analytics/vehicle-risk-scores?limit=20')
    ]);
    setFleetTrend(trend.data);
    setComponentStats(comp.data);
    setCostAnalysis(cost.data);
    setRiskScores(risk.data);
  };

  return (
    <div className="page">
      <h1>Analytics & Insights</h1>

      {/* Fleet Health Trend Line Chart */}
      <section className="chart-section">
        <h2>Fleet Health Trend (30 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={fleetTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="critical" stroke="#ef4444" />
            <Line type="monotone" dataKey="warning" stroke="#f97316" />
            <Line type="monotone" dataKey="healthy" stroke="#22c55e" />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* Component Failures Bar Chart */}
      <section className="chart-section">
        <h2>Component Failure Predictions</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={componentStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="component" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="prediction_count" fill="#3b82f6" />
            <Bar dataKey="critical_count" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Maintenance Costs */}
      <section className="chart-section">
        <h2>Maintenance Costs (12 Months)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={costAnalysis}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="parts_cost" fill="#8b5cf6" />
            <Bar dataKey="labor_cost" fill="#06b6d4" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Risk Scores Table */}
      <section>
        <h2>High-Risk Vehicles</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>VIN</th>
              <th>Model</th>
              <th>Risk Score</th>
              <th>Recent Failures</th>
              <th>Last Maintenance</th>
            </tr>
          </thead>
          <tbody>
            {riskScores.map(v => (
              <tr key={v.vehicle_id}>
                <td>{v.vin}</td>
                <td>{v.make} {v.model}</td>
                <td>
                  <span className="risk-badge" style={{
                    backgroundColor: v.risk_score >= 0.7 ? '#ef4444' : v.risk_score >= 0.5 ? '#f97316' : '#22c55e'
                  }}>
                    {(v.risk_score * 100).toFixed(1)}%
                  </span>
                </td>
                <td>{v.recent_failures}</td>
                <td>{v.last_maintenance || 'Never'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
```

## 🔧 DEPLOYMENT STEPS

### 1. Update Environment Variables
```bash
# Add to backend/.env (or GCP environment)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
```

**Get your Twilio credentials from:** https://console.twilio.com/

### 2. Deploy Backend
```bash
cd backend
gcloud builds submit --tag gcr.io/crested-polygon-451704-j6/pmi-backend:latest
gcloud run deploy pmi-backend \
  --image gcr.io/crested-polygon-451704-j6/pmi-backend:latest \
  --region us-central1 \
  --set-env-vars "TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN,TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER,DATABASE_URL=...,REDIS_URL=...,CORS_ORIGINS=*"
```

### 3. Build & Deploy Frontend
```bash
cd frontend
npm install  # Ensure all deps installed
npm run build
firebase deploy --only hosting
```

### 4. Test Twilio Integration
```bash
# Test SMS alert
curl -X POST https://pmi-backend-418022813675.us-central1.run.app/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "vehicle_id": 2, "prediction_id": 30, "channel": "sms"}'

# Test auto-send critical alerts
curl -X POST https://pmi-backend-418022813675.us-central1.run.app/api/notifications/auto-alert-critical
```

## 📊 FEATURES SUMMARY

### Backend (✅ Complete)
- ✅ Twilio SMS integration
- ✅ Twilio voice call integration
- ✅ Notification history tracking
- ✅ Appointment CRUD operations
- ✅ Service center availability
- ✅ Analytics endpoints (fleet health, component failures, costs, risk scores)
- ✅ All routers registered

### Frontend (⏳ Needs Implementation - Use Guide Above)
- ⏳ Multi-page React app with routing
- ⏳ Sidebar navigation
- ⏳ Dashboard page (stats, alerts, vehicles)
- ⏳ Vehicles management page
- ⏳ Alerts page with filtering
- ⏳ **Notifications page with send SMS/call buttons** ⭐
- ⏳ Appointments scheduling with calendar
- ⏳ Analytics page with charts (Recharts)
- ⏳ Settings page
- ⏳ Enhanced responsive CSS

## 🎨 UI/UX GUIDELINES

1. **Dark Theme**: Use existing CSS variables
2. **Interactive**: All buttons functional, not static HTML
3. **Real-time**: Auto-refresh dashboard, notifications
4. **Responsive**: Mobile-friendly layout
5. **Feedback**: Loading states, success/error messages
6. **Charts**: Use Recharts for all visualizations
7. **Forms**: Validation, error handling
8. **Modals**: For create/edit operations

## 🔐 TWILIO CREDENTIALS
- Account SID: Set as environment variable TWILIO_ACCOUNT_SID
- Auth Token: Set as environment variable TWILIO_AUTH_TOKEN
- Phone Number: Set as environment variable TWILIO_PHONE_NUMBER

**Note:** Get your credentials from https://console.twilio.com/

## ✅ NEXT STEPS

1. Create all frontend pages listed above
2. Create all components (Sidebar, Header, Cards, etc.)
3. Update App.css with enhanced styles
4. Add Twilio environment variables to GCP
5. Deploy backend with Twilio credentials
6. Deploy frontend to Firebase
7. Test end-to-end: Dashboard → Notifications → Send SMS → Receive real message!

The backend is complete and ready. Frontend structure is ready with routing. Now implement the 7 pages + components following the examples above.
