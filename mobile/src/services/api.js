import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Update this with your backend URL
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'
  : 'https://api.reform.in/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
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
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await api.post('/auth/token/refresh/', {
            refresh_token: refreshToken,
          });

          const { access } = response.data;
          await AsyncStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
        // Navigate to login (you might want to use navigation here)
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  login: (mobile, password) => api.post('/auth/login/', { mobile, password }),
  register: (aadhaarNumber, mobile) =>
    api.post('/auth/aadhaar/initiate/', { aadhaar_number: aadhaarNumber, mobile }),
  verifyOTP: (sessionId, otp, email) =>
    api.post('/auth/aadhaar/verify/', { session_id: sessionId, otp, email }),
  setPassword: (password, confirmPassword) =>
    api.post('/auth/password/set/', { password, confirm_password: confirmPassword }),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me/'),
};

export const recordsAPI = {
  list: (params) => api.get('/records/', { params }),
  get: (id) => api.get(`/records/${id}/`),
  create: (data) => api.post('/records/', data),
  update: (id, data) => api.patch(`/records/${id}/`, data),
  delete: (id) => api.delete(`/records/${id}/`),
  share: (id, providerId, purpose, durationDays, allowDownload) =>
    api.post(`/records/${id}/share/`, {
      provider_id: providerId,
      purpose,
      duration_days: durationDays,
      allow_download: allowDownload,
    }),
};

export const providersAPI = {
  list: (params) => api.get('/providers/', { params }),
  get: (id) => api.get(`/providers/${id}/`),
};

export const insuranceAPI = {
  policies: {
    list: () => api.get('/policies/'),
    get: (id) => api.get(`/policies/${id}/`),
    create: (data) => api.post('/policies/', data),
  },
  claims: {
    list: () => api.get('/claims/'),
    get: (id) => api.get(`/claims/${id}/`),
    create: (data) => api.post('/claims/', data),
  },
};

export const notificationsAPI = {
  list: (params) => api.get('/notifications/', { params }),
  markRead: (id) => api.post(`/notifications/${id}/mark_read/`),
  markAllRead: () => api.post('/notifications/mark_all_read/'),
  unreadCount: () => api.get('/notifications/unread_count/'),
};

