import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  RefreshControl,
  SafeAreaView,
  TouchableOpacity,
  ActivityIndicator,
  StatusBar,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import config from './config';

// API base URL from environment config
const API_URL = config.apiUrl;

export default function App() {
  const [vehicles, setVehicles] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    total_vehicles: 0,
    critical_alerts: 0,
    scheduled_services: 0,
    healthy_vehicles: 0,
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Mock data for now - replace with actual API calls when backend is deployed
      setStats({
        total_vehicles: 150,
        critical_alerts: 8,
        scheduled_services: 23,
        healthy_vehicles: 119,
      });

      setAlerts([
        {
          id: 1,
          vehicle_id: 'VEHICLE001',
          vin: '1HGBH41JXMN109186',
          severity: 'critical',
          message: 'Oil pressure critically low',
          timestamp: new Date().toISOString(),
          status: 'pending',
        },
        {
          id: 2,
          vehicle_id: 'VEHICLE042',
          vin: '2FMDK3GC7DBA12345',
          severity: 'high',
          message: 'Engine temperature elevated',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          status: 'scheduled',
        },
        {
          id: 3,
          vehicle_id: 'VEHICLE089',
          vin: '5TDKK3DC9HS123456',
          severity: 'medium',
          message: 'Vibration level above normal',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          status: 'scheduled',
        },
      ]);

      setVehicles([
        {
          vehicle_id: 'VEHICLE001',
          vin: '1HGBH41JXMN109186',
          status: 'critical',
          health_score: 45,
          last_reading: new Date().toISOString(),
        },
        {
          vehicle_id: 'VEHICLE042',
          vin: '2FMDK3GC7DBA12345',
          status: 'warning',
          health_score: 68,
          last_reading: new Date(Date.now() - 600000).toISOString(),
        },
        {
          vehicle_id: 'VEHICLE089',
          vin: '5TDKK3DC9HS123456',
          status: 'healthy',
          health_score: 92,
          last_reading: new Date(Date.now() - 300000).toISOString(),
        },
      ]);

      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return '#ef4444';
      case 'high':
        return '#f97316';
      case 'medium':
        return '#eab308';
      case 'low':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'critical':
        return '#ef4444';
      case 'warning':
        return '#f97316';
      case 'healthy':
        return '#22c55e';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1e293b" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.logoContainer}>
            <Ionicons name="car-sport" size={28} color="#3b82f6" />
            <Text style={styles.headerTitle}>ProActive Mobility</Text>
          </View>
          <View style={styles.notificationBadge}>
            <Ionicons name="notifications" size={24} color="#f1f5f9" />
            {stats.critical_alerts > 0 && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{stats.critical_alerts}</Text>
              </View>
            )}
          </View>
        </View>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#3b82f6"
          />
        }
      >
        {/* Stats Cards */}
        <View style={styles.statsGrid}>
          <View style={[styles.statCard, { backgroundColor: '#1e40af' }]}>
            <Ionicons name="car" size={32} color="#fff" />
            <Text style={styles.statValue}>{stats.total_vehicles}</Text>
            <Text style={styles.statLabel}>Total Vehicles</Text>
          </View>

          <View style={[styles.statCard, { backgroundColor: '#dc2626' }]}>
            <Ionicons name="warning" size={32} color="#fff" />
            <Text style={styles.statValue}>{stats.critical_alerts}</Text>
            <Text style={styles.statLabel}>Critical Alerts</Text>
          </View>

          <View style={[styles.statCard, { backgroundColor: '#ea580c' }]}>
            <Ionicons name="calendar" size={32} color="#fff" />
            <Text style={styles.statValue}>{stats.scheduled_services}</Text>
            <Text style={styles.statLabel}>Scheduled</Text>
          </View>

          <View style={[styles.statCard, { backgroundColor: '#16a34a' }]}>
            <Ionicons name="checkmark-circle" size={32} color="#fff" />
            <Text style={styles.statValue}>{stats.healthy_vehicles}</Text>
            <Text style={styles.statLabel}>Healthy</Text>
          </View>
        </View>

        {/* Active Alerts */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Active Alerts</Text>
            <TouchableOpacity>
              <Text style={styles.viewAllButton}>View All</Text>
            </TouchableOpacity>
          </View>

          {alerts.map((alert) => (
            <View
              key={alert.id}
              style={[
                styles.alertCard,
                { borderLeftColor: getSeverityColor(alert.severity) },
              ]}
            >
              <View style={styles.alertHeader}>
                <View style={styles.alertTitleRow}>
                  <Ionicons
                    name="warning"
                    size={20}
                    color={getSeverityColor(alert.severity)}
                  />
                  <Text style={styles.alertVehicleId}>{alert.vehicle_id}</Text>
                </View>
                <View style={styles.alertTimeRow}>
                  <Ionicons name="time" size={16} color="#94a3b8" />
                  <Text style={styles.alertTime}>
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </Text>
                </View>
              </View>
              <Text style={styles.alertMessage}>{alert.message}</Text>
              <View style={styles.alertFooter}>
                <Text style={styles.alertVin}>VIN: {alert.vin}</Text>
                <View
                  style={[
                    styles.statusBadge,
                    {
                      backgroundColor:
                        alert.status === 'pending'
                          ? 'rgba(239, 68, 68, 0.2)'
                          : 'rgba(249, 115, 22, 0.2)',
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.statusBadgeText,
                      {
                        color:
                          alert.status === 'pending' ? '#ef4444' : '#f97316',
                      },
                    ]}
                  >
                    {alert.status}
                  </Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        {/* Fleet Status */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Fleet Status</Text>
          </View>

          {vehicles.map((vehicle) => (
            <View key={vehicle.vehicle_id} style={styles.vehicleCard}>
              <View style={styles.vehicleHeader}>
                <View style={styles.vehicleIdRow}>
                  <Ionicons name="car" size={20} color="#3b82f6" />
                  <Text style={styles.vehicleId}>{vehicle.vehicle_id}</Text>
                </View>
                <View
                  style={[
                    styles.vehicleStatusBadge,
                    { backgroundColor: `${getStatusColor(vehicle.status)}20` },
                  ]}
                >
                  <Text
                    style={[
                      styles.vehicleStatusText,
                      { color: getStatusColor(vehicle.status) },
                    ]}
                  >
                    {vehicle.status}
                  </Text>
                </View>
              </View>

              <Text style={styles.vehicleVin}>VIN: {vehicle.vin}</Text>

              <View style={styles.healthScoreContainer}>
                <Text style={styles.healthScoreLabel}>Health Score</Text>
                <View style={styles.healthBarContainer}>
                  <View style={styles.healthBar}>
                    <View
                      style={[
                        styles.healthBarFill,
                        {
                          width: `${vehicle.health_score}%`,
                          backgroundColor: getStatusColor(vehicle.status),
                        },
                      ]}
                    />
                  </View>
                  <Text style={styles.healthScoreValue}>
                    {vehicle.health_score}%
                  </Text>
                </View>
              </View>

              <Text style={styles.lastReading}>
                Last reading: {new Date(vehicle.last_reading).toLocaleString()}
              </Text>

              <TouchableOpacity style={styles.viewDetailsButton}>
                <Text style={styles.viewDetailsText}>View Details</Text>
                <Ionicons name="chevron-forward" size={16} color="#3b82f6" />
              </TouchableOpacity>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0f172a',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#94a3b8',
  },
  header: {
    backgroundColor: '#1e293b',
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#f1f5f9',
  },
  notificationBadge: {
    position: 'relative',
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#ef4444',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
  scrollView: {
    flex: 1,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 12,
    gap: 12,
  },
  statCard: {
    width: '48%',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    gap: 8,
  },
  statValue: {
    fontSize: 32,
    fontWeight: '700',
    color: '#fff',
  },
  statLabel: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
  },
  section: {
    marginHorizontal: 16,
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#f1f5f9',
  },
  viewAllButton: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
  },
  alertCard: {
    backgroundColor: '#1e293b',
    borderLeftWidth: 4,
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  alertTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  alertVehicleId: {
    fontSize: 16,
    fontWeight: '600',
    color: '#f1f5f9',
  },
  alertTimeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  alertTime: {
    fontSize: 13,
    color: '#94a3b8',
  },
  alertMessage: {
    fontSize: 15,
    color: '#e2e8f0',
    marginBottom: 12,
  },
  alertFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  alertVin: {
    fontSize: 12,
    color: '#94a3b8',
    fontFamily: 'monospace',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  vehicleCard: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  vehicleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  vehicleIdRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  vehicleId: {
    fontSize: 16,
    fontWeight: '600',
    color: '#f1f5f9',
  },
  vehicleStatusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  vehicleStatusText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  vehicleVin: {
    fontSize: 13,
    color: '#94a3b8',
    fontFamily: 'monospace',
    marginBottom: 12,
  },
  healthScoreContainer: {
    marginBottom: 12,
  },
  healthScoreLabel: {
    fontSize: 13,
    color: '#94a3b8',
    marginBottom: 6,
  },
  healthBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  healthBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#334155',
    borderRadius: 4,
    overflow: 'hidden',
  },
  healthBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  healthScoreValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#f1f5f9',
    width: 45,
    textAlign: 'right',
  },
  lastReading: {
    fontSize: 12,
    color: '#64748b',
    marginBottom: 12,
  },
  viewDetailsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    paddingVertical: 8,
  },
  viewDetailsText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
  },
});
