import axios from 'axios';

// Backend API URL
const API_BASE_URL = 'https://pmi-backend-418022813675.us-central1.run.app';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard APIs
export const getDashboardStats = () => api.get('/api/dashboard/stats');
export const getDashboardAlerts = () => api.get('/api/dashboard/alerts');
export const getDashboardVehicles = () => api.get('/api/dashboard/vehicles');
export const getRecentPredictions = () => api.get('/api/dashboard/predictions/recent');

// Notification APIs
export const sendAlert = (data) => api.post('/api/notifications/send-alert', data);
export const sendReminder = (appointmentId) => api.post(`/api/notifications/send-reminder/${appointmentId}`);
export const getNotificationHistory = (params) => api.get('/api/notifications/history', { params });
export const markNotificationRead = (notificationId) => api.put(`/api/notifications/${notificationId}/read`);
export const getNotificationStats = () => api.get('/api/notifications/stats');
export const autoSendCriticalAlerts = () => api.post('/api/notifications/auto-alert-critical');

// Appointment APIs
export const createAppointment = (data) => api.post('/api/appointments/create', data);
export const getAppointments = (params) => api.get('/api/appointments/list', { params });
export const getAppointment = (id) => api.get(`/api/appointments/${id}`);
export const updateAppointment = (id, data) => api.put(`/api/appointments/${id}`, data);
export const cancelAppointment = (id) => api.delete(`/api/appointments/${id}`);
export const getAvailableCenters = (params) => api.get('/api/appointments/service-centers/available', { params });

// Analytics APIs
export const getFleetHealthTrend = (days = 30) => api.get(`/api/analytics/fleet-health-trend?days=${days}`);
export const getComponentFailures = (days = 90) => api.get(`/api/analytics/component-failures?days=${days}`);
export const getMaintenanceCosts = (months = 12) => api.get(`/api/analytics/maintenance-costs?months=${months}`);
export const getPredictionAccuracy = (days = 90) => api.get(`/api/analytics/prediction-accuracy?days=${days}`);
export const getVehicleRiskScores = (limit = 50, minRisk = 0.5) => api.get(`/api/analytics/vehicle-risk-scores?limit=${limit}&min_risk=${minRisk}`);
export const getFleetSummary = () => api.get('/api/analytics/fleet-summary');

// Agent Workflow APIs
export const getAgentStatus = () => api.get('/api/agent-workflow/status');
export const getActivityLogs = (limit = 20) => api.get(`/api/agent-workflow/activity-logs?limit=${limit}`);

// Vehicle Details APIs
export const getVehicleDetails = (vehicleId) => api.get(`/api/vehicles/${vehicleId}/details`);

export default api;
