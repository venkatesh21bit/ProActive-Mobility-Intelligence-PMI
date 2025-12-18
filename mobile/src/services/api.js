/**
 * Production-grade API Service
 * Handles authentication, token management, retries, and error handling
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import config from '../../config';

const API_URL = config.apiUrl;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
});

// Token management
const TOKEN_KEY = '@auth_token';
const REFRESH_TOKEN_KEY = '@refresh_token';
const USER_KEY = '@user_data';

export const authStorage = {
  async saveTokens(accessToken, refreshToken) {
    try {
      await AsyncStorage.multiSet([
        [TOKEN_KEY, accessToken],
        [REFRESH_TOKEN_KEY, refreshToken],
      ]);
    } catch (error) {
      console.error('Error saving tokens:', error);
    }
  },

  async getAccessToken() {
    try {
      return await AsyncStorage.getItem(TOKEN_KEY);
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  },

  async getRefreshToken() {
    try {
      return await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Error getting refresh token:', error);
      return null;
    }
  },

  async saveUser(userData) {
    try {
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(userData));
    } catch (error) {
      console.error('Error saving user data:', error);
    }
  },

  async getUser() {
    try {
      const userData = await AsyncStorage.getItem(USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  },

  async clearAll() {
    try {
      await AsyncStorage.multiRemove([TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY]);
    } catch (error) {
      console.error('Error clearing storage:', error);
    }
  },
};

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await authStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await authStorage.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          await authStorage.saveTokens(access_token, refresh_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        await authStorage.clearAll();
        // Navigate to login screen (implement based on your navigation setup)
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API service methods
export const authService = {
  async register(email, password, firstName, lastName, phone, address = null) {
    try {
      const response = await apiClient.post('/api/auth/register', {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone,
        address,
      });

      const { access_token, refresh_token, ...userData } = response.data;
      await authStorage.saveTokens(access_token, refresh_token);
      await authStorage.saveUser(userData);

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async login(email, password) {
    try {
      const response = await apiClient.post('/api/auth/login', {
        email,
        password,
      });

      const { access_token, refresh_token, ...userData } = response.data;
      await authStorage.saveTokens(access_token, refresh_token);
      await authStorage.saveUser(userData);

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async logout() {
    try {
      await apiClient.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await authStorage.clearAll();
    }
  },

  async getCurrentUser() {
    try {
      const response = await apiClient.get('/api/auth/me');
      await authStorage.saveUser(response.data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export const vehicleService = {
  async getMyVehicles() {
    try {
      const response = await apiClient.get('/api/auth/me');
      return response.data.vehicles || [];
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async getVehicleDetails(vehicleId) {
    try {
      const response = await apiClient.get(`/api/dashboard/vehicle/${vehicleId}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export const bookingService = {
  async createBooking(customerId, vehicleId, serviceType, preferredDate, preferredTime) {
    try {
      const response = await apiClient.post('/api/bookings/create', {
        customer_id: customerId,
        vehicle_id: vehicleId,
        service_type: serviceType,
        preferred_date: preferredDate,
        preferred_time: preferredTime,
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async getMyBookings(customerId) {
    try {
      const response = await apiClient.get(`/api/bookings/customer/${customerId}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async cancelBooking(appointmentId) {
    try {
      const response = await apiClient.post(`/api/bookings/cancel/${appointmentId}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// Error handling helper
function handleApiError(error) {
  if (error.response) {
    // Server responded with error
    const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
    return new Error(message);
  } else if (error.request) {
    // Network error
    return new Error('Network error. Please check your connection.');
  } else {
    // Other errors
    return new Error(error.message || 'An unexpected error occurred');
  }
}

export default apiClient;
