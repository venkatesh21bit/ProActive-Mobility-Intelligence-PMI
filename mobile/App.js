import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  StatusBar,
  Alert,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import config from './config';
import MotorcycleVisualization from './src/components/MotorcycleVisualization';

// API base URL from environment config
const API_URL = config.apiUrl;

export default function App() {
  // Authentication state
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [customer, setCustomer] = useState(null);
  const [loginEmail, setLoginEmail] = useState('');
  
  const [myVehicle, setMyVehicle] = useState(null);
  const [vehicleDetails, setVehicleDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'details', 'booking'
  const [showBooking, setShowBooking] = useState(false);
  const [selectedService, setSelectedService] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);

  useEffect(() => {
    // Auto-login for demo - remove in production
    const demoEmail = 'demo@pmi.com';
    const demoPassword = 'demo123';
    handleLogin(demoEmail, demoPassword);
  }, []);

  const handleLogin = async (email, password) => {
    try {
      setLoading(true);
      console.log('Logging in with:', email);
      
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email: email || loginEmail,
        password: password || 'demo123'
      }, {
        timeout: 15000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      console.log('✅ Login successful:', response.data);
      
      setCustomer(response.data);
      setIsLoggedIn(true);
      
      if (response.data.vehicle) {
        setMyVehicle(response.data.vehicle);
        // Fetch detailed vehicle info
        fetchVehicleDetails(response.data.vehicle.vehicle_id);
      } else {
        Alert.alert('No Vehicle', 'No vehicle registered to this account.');
      }
      
    } catch (error) {
      console.error('❌ Login error:', error.message);
      if (error.response?.status === 404) {
        Alert.alert('Login Failed', 'Customer not found. Please check your email.');
      } else {
        Alert.alert('Login Failed', 'Please check your internet connection and try again.');
      }
      setLoading(false);
    }
  };

  const fetchMyVehicle = async () => {
    try {
      setLoading(true);
      console.log('Fetching vehicles for customer:', customer?.customer_id);
      const response = await axios.get(`${API_URL}/api/fixes/vehicles-with-health/${customer?.customer_id}`, {
        timeout: 15000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      console.log('✅ Vehicles fetched successfully:', response.data);
      
      if (response.data && response.data.vehicles && response.data.vehicles.length > 0) {
        // Use first vehicle if customer has multiple
        const customerVehicle = response.data.vehicles[0];
        setMyVehicle(customerVehicle);
        // Auto-fetch details for the vehicle
        fetchVehicleDetails(customerVehicle.vehicle_id);
      } else {
        Alert.alert('Vehicle Not Found', 'Your vehicle is not registered in the system.');
      }
    } catch (error) {
      console.error('❌ Error fetching vehicle:', error.message);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      } else if (error.request) {
        console.error('No response received - possible network issue');
      } else {
        console.error('Request setup error:', error.message);
      }
      Alert.alert('Network Error', 'Failed to fetch your vehicle. Please check your internet connection.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchVehicleDetails = async (vehicleId) => {
    try {
      setLoading(true);
      console.log('Fetching details for vehicle:', vehicleId);
      const response = await axios.get(`${API_URL}/api/vehicles/${vehicleId}/details`, {
        timeout: 15000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      console.log('✅ Vehicle details fetched:', response.data?.vehicle_id);
      setVehicleDetails(response.data);
      setActiveTab('details');
    } catch (error) {
      console.error('❌ Error fetching vehicle details:', error.message);
      if (error.response) {
        console.error('Response status:', error.response.status);
      } else if (error.request) {
        console.error('No response received');
      }
      Alert.alert('Network Error', 'Failed to fetch vehicle details.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchMyVehicle();
  };

  const handleViewDetails = () => {
    setActiveTab('details');
  };

  const handleBackToHome = () => {
    setActiveTab('home');
    setShowBooking(false);
  };

  const handleBookService = () => {
    setShowBooking(true);
    setActiveTab('booking');
  };

  const handleSubmitBooking = async () => {
    if (!selectedService || !selectedDate || !selectedTime) {
      Alert.alert('Missing Information', 'Please fill in all fields to book your service.');
      return;
    }

    if (!customer || !myVehicle) {
      Alert.alert('Error', 'Please login first.');
      return;
    }

    try {
      setBookingLoading(true);
      console.log('Submitting booking...');
      
      const bookingData = {
        customer_id: customer.customer_id,
        vehicle_id: myVehicle.vehicle_id,
        service_type: selectedService,
        scheduled_date: selectedDate,
        scheduled_time: selectedTime
      };
      
      console.log('Booking data:', bookingData);
      
      const response = await axios.post(`${API_URL}/api/bookings/create`, bookingData, {
        timeout: 15000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      console.log('✅ Booking created:', response.data);
      
      Alert.alert(
        '✅ Booking Confirmed!',
        response.data.confirmation_message,
        [
          { 
            text: 'OK', 
            onPress: () => {
              // Reset form
              setSelectedService('');
              setSelectedDate('');
              setSelectedTime('');
              handleBackToHome();
            }
          }
        ]
      );
      
    } catch (error) {
      console.error('❌ Booking error:', error.message);
      if (error.response) {
        console.error('Response:', error.response.data);
      }
      Alert.alert(
        'Booking Failed',
        'Unable to create appointment. Please try again later.'
      );
    } finally {
      setBookingLoading(false);
    }
  };

  const getHealthColor = (score) => {
    if (score >= 8) return '#22c55e';
    if (score >= 5) return '#f59e0b';
    return '#ef4444';
  };

  const getHealthStatus = (score) => {
    if (score >= 8) return 'Healthy';
    if (score >= 5) return 'Warning';
    return 'Critical';
  };

  const serviceTypes = [
    { id: 'general', name: 'General Service', icon: 'construct' },
    { id: 'oil', name: 'Oil Change', icon: 'water' },
    { id: 'brake', name: 'Brake Service', icon: 'hand-left' },
    { id: 'inspection', name: 'Full Inspection', icon: 'search' },
    { id: 'repair', name: 'Repair Work', icon: 'build' },
  ];

  const availableDates = [
    'Tomorrow',
    new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toLocaleDateString(),
    new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toLocaleDateString(),
    new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toLocaleDateString(),
    new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toLocaleDateString(),
  ];

  const availableTimes = [
    '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
    '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM'
  ];

  if (loading && !refreshing) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
        <ActivityIndicator size="large" color="#dc2626" />
        <Text style={styles.loadingText}>Loading your motorcycle...</Text>
      </SafeAreaView>
    );
  }

  if (!myVehicle && !loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
        <View style={styles.emptyStateContainer}>
          <Ionicons name="bicycle-outline" size={100} color="#475569" />
          <Text style={styles.emptyStateTitle}>No Vehicle Found</Text>
          <Text style={styles.emptyStateText}>
            Your vehicle is not registered in the system.
          </Text>
          <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
      
      {/* Header */}
      <View style={styles.header}>
        {activeTab !== 'home' && (
          <TouchableOpacity onPress={handleBackToHome} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
        )}
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>
            {activeTab === 'home' ? 'My Motorcycle' : 
             activeTab === 'details' ? 'Vehicle Health' : 'Book Service'}
          </Text>
          <Text style={styles.headerSubtitle}>Hero MotoCorp</Text>
        </View>
        {activeTab === 'home' && (
          <TouchableOpacity onPress={onRefresh} style={styles.refreshButton}>
            <Ionicons name="refresh" size={24} color="#fff" />
          </TouchableOpacity>
        )}
      </View>

      {/* HOME TAB */}
      {activeTab === 'home' && myVehicle && (
        <ScrollView
          style={styles.content}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#dc2626"
              colors={['#dc2626']}
            />
          }
        >
          {/* Vehicle Card */}
          <View style={styles.mainVehicleCard}>
            <View style={styles.vehicleImagePlaceholder}>
              <Ionicons name="bicycle" size={80} color="#dc2626" />
            </View>
            
            <View style={styles.vehicleMainInfo}>
              <Text style={styles.vehicleMainName}>
                {myVehicle.make} {myVehicle.model}
              </Text>
              <Text style={styles.vehicleMainVin}>VIN: {myVehicle.vin}</Text>
              <View style={styles.vehicleMetaRow}>
                <View style={styles.vehicleMeta}>
                  <Ionicons name="calendar" size={16} color="#94a3b8" />
                  <Text style={styles.vehicleMetaText}>{myVehicle.year}</Text>
                </View>
                <View style={styles.vehicleMeta}>
                  <Ionicons name="speedometer" size={16} color="#94a3b8" />
                  <Text style={styles.vehicleMetaText}>
                    {myVehicle.mileage?.toLocaleString()} km
                  </Text>
                </View>
              </View>
            </View>

            {/* Health Score */}
            <View style={[
              styles.healthScoreCard,
              { backgroundColor: getHealthColor(myVehicle.health_score) + '15' }
            ]}>
              <Text style={styles.healthScoreLabel}>Health Score</Text>
              <Text style={[
                styles.healthScoreValue,
                { color: getHealthColor(myVehicle.health_score) }
              ]}>
                {myVehicle.health_score}/10
              </Text>
              <Text style={[
                styles.healthScoreStatus,
                { color: getHealthColor(myVehicle.health_score) }
              ]}>
                {getHealthStatus(myVehicle.health_score)}
              </Text>
            </View>
          </View>

          {/* Action Buttons */}
          <View style={styles.actionButtonsContainer}>
            <TouchableOpacity
              style={[styles.actionButton, styles.primaryButton]}
              onPress={handleViewDetails}
            >
              <Ionicons name="analytics" size={24} color="#fff" />
              <Text style={styles.actionButtonText}>View Health Details</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.actionButton, styles.secondaryButton]}
              onPress={handleBookService}
            >
              <Ionicons name="calendar" size={24} color="#dc2626" />
              <Text style={[styles.actionButtonText, { color: '#dc2626' }]}>
                Book Service
              </Text>
            </TouchableOpacity>
          </View>

          {/* Quick Stats */}
          <View style={styles.quickStatsContainer}>
            <Text style={styles.sectionTitle}>Quick Overview</Text>
            <View style={styles.quickStatsGrid}>
              <View style={styles.quickStatCard}>
                <Ionicons name="checkmark-circle" size={32} color="#22c55e" />
                <Text style={styles.quickStatLabel}>Last Service</Text>
                <Text style={styles.quickStatValue}>30 days ago</Text>
              </View>
              <View style={styles.quickStatCard}>
                <Ionicons name="construct" size={32} color="#3b82f6" />
                <Text style={styles.quickStatLabel}>Next Service</Text>
                <Text style={styles.quickStatValue}>Due Soon</Text>
              </View>
              <View style={styles.quickStatCard}>
                <Ionicons name="alert-circle" size={32} color="#f59e0b" />
                <Text style={styles.quickStatLabel}>Alerts</Text>
                <Text style={styles.quickStatValue}>
                  {vehicleDetails?.predictions?.filter(p => p.failure_probability > 0.5).length || 0}
                </Text>
              </View>
            </View>
          </View>

          {/* Service Centers */}
          <View style={styles.serviceCentersContainer}>
            <Text style={styles.sectionTitle}>Nearby Service Centers</Text>
            <View style={styles.serviceCenterCard}>
              <Ionicons name="location" size={24} color="#dc2626" />
              <View style={styles.serviceCenterInfo}>
                <Text style={styles.serviceCenterName}>Hero Service Center</Text>
                <Text style={styles.serviceCenterAddress}>
                  123 Main Road, Downtown - 2.5 km away
                </Text>
                <View style={styles.serviceCenterMeta}>
                  <Ionicons name="star" size={14} color="#f59e0b" />
                  <Text style={styles.serviceCenterRating}>4.8</Text>
                  <Text style={styles.serviceCenterHours}>• Open Now</Text>
                </View>
              </View>
              <TouchableOpacity style={styles.callButton}>
                <Ionicons name="call" size={20} color="#fff" />
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      )}

      {/* DETAILS TAB */}
      {activeTab === 'details' && (
        <ScrollView
          style={styles.content}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#dc2626"
              colors={['#dc2626']}
            />
          }
        >
          {vehicleDetails ? (
            <MotorcycleVisualization vehicleData={vehicleDetails} />
          ) : (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#dc2626" />
              <Text style={styles.loadingText}>Loading vehicle details...</Text>
            </View>
          )}
        </ScrollView>
      )}

      {/* BOOKING TAB */}
      {activeTab === 'booking' && (
        <ScrollView style={styles.content}>
          <View style={styles.bookingContainer}>
            <Text style={styles.bookingTitle}>Schedule Your Service</Text>
            <Text style={styles.bookingSubtitle}>
              Select service type, date, and time
            </Text>

            {/* Service Type Selection */}
            <View style={styles.bookingSection}>
              <Text style={styles.bookingSectionTitle}>Service Type</Text>
              {serviceTypes.map((service) => (
                <TouchableOpacity
                  key={service.id}
                  style={[
                    styles.serviceOption,
                    selectedService === service.name && styles.serviceOptionSelected
                  ]}
                  onPress={() => setSelectedService(service.name)}
                >
                  <Ionicons
                    name={service.icon}
                    size={24}
                    color={selectedService === service.name ? '#dc2626' : '#94a3b8'}
                  />
                  <Text style={[
                    styles.serviceOptionText,
                    selectedService === service.name && styles.serviceOptionTextSelected
                  ]}>
                    {service.name}
                  </Text>
                  {selectedService === service.name && (
                    <Ionicons name="checkmark-circle" size={24} color="#dc2626" />
                  )}
                </TouchableOpacity>
              ))}
            </View>

            {/* Date Selection */}
            <View style={styles.bookingSection}>
              <Text style={styles.bookingSectionTitle}>Select Date</Text>
              <View style={styles.dateGrid}>
                {availableDates.map((date) => (
                  <TouchableOpacity
                    key={date}
                    style={[
                      styles.dateOption,
                      selectedDate === date && styles.dateOptionSelected
                    ]}
                    onPress={() => setSelectedDate(date)}
                  >
                    <Text style={[
                      styles.dateOptionText,
                      selectedDate === date && styles.dateOptionTextSelected
                    ]}>
                      {date}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Time Selection */}
            <View style={styles.bookingSection}>
              <Text style={styles.bookingSectionTitle}>Select Time</Text>
              <View style={styles.timeGrid}>
                {availableTimes.map((time) => (
                  <TouchableOpacity
                    key={time}
                    style={[
                      styles.timeOption,
                      selectedTime === time && styles.timeOptionSelected
                    ]}
                    onPress={() => setSelectedTime(time)}
                  >
                    <Text style={[
                      styles.timeOptionText,
                      selectedTime === time && styles.timeOptionTextSelected
                    ]}>
                      {time}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Submit Button */}
            <TouchableOpacity
              style={[styles.submitBookingButton, bookingLoading && styles.submitBookingButtonDisabled]}
              onPress={handleSubmitBooking}
              disabled={bookingLoading}
            >
              {bookingLoading ? (
                <>
                  <ActivityIndicator size="small" color="#fff" />
                  <Text style={styles.submitBookingButtonText}>Creating Appointment...</Text>
                </>
              ) : (
                <>
                  <Text style={styles.submitBookingButtonText}>Confirm Booking</Text>
                  <Ionicons name="checkmark-circle" size={24} color="#fff" />
                </>
              )}
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Ionicons name="shield-checkmark" size={16} color="#64748b" />
        <Text style={styles.footerText}>Powered by AI Predictive Maintenance</Text>
      </View>
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
    backgroundColor: '#991b1b',
    borderBottomWidth: 2,
    borderBottomColor: '#dc2626',
    paddingHorizontal: 16,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  backButton: {
    marginRight: 12,
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 2,
  },
  refreshButton: {
    padding: 8,
  },
  content: {
    flex: 1,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    margin: 16,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
    color: '#fff',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderLeftWidth: 4,
    borderColor: '#334155',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#64748b',
    marginTop: 16,
  },
  vehicleCard: {
    backgroundColor: '#1e293b',
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  vehicleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  vehicleInfo: {
    flex: 1,
  },
  vehicleName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  vehicleVin: {
    fontSize: 13,
    color: '#94a3b8',
    marginBottom: 2,
  },
  vehicleMileage: {
    fontSize: 13,
    color: '#94a3b8',
  },
  healthBadge: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  healthText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  healthStatus: {
    fontSize: 11,
    fontWeight: '600',
    marginTop: 2,
  },
  viewDetailsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    paddingVertical: 10,
    backgroundColor: 'rgba(220, 38, 38, 0.1)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#dc2626',
  },
  viewDetailsText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#dc2626',
    marginRight: 4,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    backgroundColor: '#1e293b',
    borderTopWidth: 1,
    borderTopColor: '#334155',
    gap: 8,
  },
  footerText: {
    fontSize: 12,
    color: '#64748b',
  },
  // Empty state styles
  emptyStateContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#f1f5f9',
    marginTop: 24,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#94a3b8',
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: '#dc2626',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Main vehicle card styles
  mainVehicleCard: {
    margin: 16,
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#334155',
  },
  vehicleImagePlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#0f172a',
    borderRadius: 12,
    marginBottom: 16,
  },
  vehicleMainInfo: {
    marginBottom: 16,
  },
  vehicleMainName: {
    fontSize: 24,
    fontWeight: '700',
    color: '#f1f5f9',
    marginBottom: 8,
  },
  vehicleMainVin: {
    fontSize: 14,
    color: '#94a3b8',
    fontFamily: 'monospace',
    marginBottom: 12,
  },
  vehicleMetaRow: {
    flexDirection: 'row',
    gap: 16,
  },
  vehicleMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  vehicleMetaText: {
    fontSize: 14,
    color: '#94a3b8',
  },
  healthScoreCard: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  healthScoreLabel: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 8,
  },
  healthScoreValue: {
    fontSize: 48,
    fontWeight: '700',
    marginBottom: 4,
  },
  healthScoreStatus: {
    fontSize: 16,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  // Action buttons
  actionButtonsContainer: {
    paddingHorizontal: 16,
    gap: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#dc2626',
  },
  secondaryButton: {
    backgroundColor: '#1e293b',
    borderWidth: 2,
    borderColor: '#dc2626',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  // Quick stats
  quickStatsContainer: {
    padding: 16,
  },
  quickStatsGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  quickStatCard: {
    flex: 1,
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    gap: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  quickStatLabel: {
    fontSize: 12,
    color: '#94a3b8',
    textAlign: 'center',
  },
  quickStatValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#f1f5f9',
  },
  // Service centers
  serviceCentersContainer: {
    padding: 16,
  },
  serviceCenterCard: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    gap: 12,
    borderWidth: 1,
    borderColor: '#334155',
    alignItems: 'center',
  },
  serviceCenterInfo: {
    flex: 1,
  },
  serviceCenterName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#f1f5f9',
    marginBottom: 4,
  },
  serviceCenterAddress: {
    fontSize: 13,
    color: '#94a3b8',
    marginBottom: 6,
  },
  serviceCenterMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  serviceCenterRating: {
    fontSize: 13,
    color: '#f59e0b',
    fontWeight: '600',
  },
  serviceCenterHours: {
    fontSize: 13,
    color: '#22c55e',
  },
  callButton: {
    backgroundColor: '#dc2626',
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  // Booking styles
  bookingContainer: {
    padding: 16,
  },
  bookingTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#f1f5f9',
    marginBottom: 8,
  },
  bookingSubtitle: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 24,
  },
  bookingSection: {
    marginBottom: 24,
  },
  bookingSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#f1f5f9',
    marginBottom: 12,
  },
  serviceOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    gap: 12,
    borderWidth: 2,
    borderColor: '#334155',
  },
  serviceOptionSelected: {
    borderColor: '#dc2626',
    backgroundColor: '#dc262610',
  },
  serviceOptionText: {
    flex: 1,
    fontSize: 16,
    color: '#94a3b8',
  },
  serviceOptionTextSelected: {
    color: '#f1f5f9',
    fontWeight: '600',
  },
  dateGrid: {
    gap: 8,
  },
  dateOption: {
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#334155',
  },
  dateOptionSelected: {
    borderColor: '#dc2626',
    backgroundColor: '#dc262610',
  },
  dateOptionText: {
    fontSize: 15,
    color: '#94a3b8',
    textAlign: 'center',
  },
  dateOptionTextSelected: {
    color: '#f1f5f9',
    fontWeight: '600',
  },
  timeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  timeOption: {
    backgroundColor: '#1e293b',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#334155',
    width: '23%',
  },
  timeOptionSelected: {
    borderColor: '#dc2626',
    backgroundColor: '#dc262610',
  },
  timeOptionText: {
    fontSize: 14,
    color: '#94a3b8',
    textAlign: 'center',
  },
  timeOptionTextSelected: {
    color: '#f1f5f9',
    fontWeight: '600',
  },
  submitBookingButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#dc2626',
    padding: 18,
    borderRadius: 12,
    gap: 12,
    marginTop: 8,
  },
  submitBookingButtonDisabled: {
    backgroundColor: '#94a3b8',
    opacity: 0.6,
  },
  submitBookingButtonText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#fff',
  },
});
