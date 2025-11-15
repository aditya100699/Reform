import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('access_token');
      const storedUser = await AsyncStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (mobile, password) => {
    try {
      const response = await api.post('/auth/login/', { mobile, password });
      const { user, tokens } = response.data;
      
      await AsyncStorage.setItem('access_token', tokens.access);
      await AsyncStorage.setItem('refresh_token', tokens.refresh);
      await AsyncStorage.setItem('user', JSON.stringify(user));
      
      setToken(tokens.access);
      setUser(user);
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed'
      };
    }
  };

  const register = async (aadhaarNumber, mobile, email) => {
    try {
      // Step 1: Initiate Aadhaar auth
      const initiateResponse = await api.post('/auth/aadhaar/initiate/', {
        aadhaar_number: aadhaarNumber,
        mobile: mobile
      });
      
      return {
        success: true,
        sessionId: initiateResponse.data.session_id,
        expiresIn: initiateResponse.data.expires_in
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed'
      };
    }
  };

  const verifyOTP = async (sessionId, otp, email) => {
    try {
      const response = await api.post('/auth/aadhaar/verify/', {
        session_id: sessionId,
        otp: otp,
        email: email
      });
      
      const { user, tokens, requires_password } = response.data;
      
      await AsyncStorage.setItem('access_token', tokens.access);
      await AsyncStorage.setItem('refresh_token', tokens.refresh);
      await AsyncStorage.setItem('user', JSON.stringify(user));
      
      setToken(tokens.access);
      setUser(user);
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      
      return {
        success: true,
        requiresPassword: requires_password
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'OTP verification failed'
      };
    }
  };

  const setPassword = async (password, confirmPassword) => {
    try {
      await api.post('/auth/password/set/', {
        password,
        confirm_password: confirmPassword
      });
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to set password'
      };
    }
  };

  const logout = async () => {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh_token: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
      setToken(null);
      setUser(null);
      delete api.defaults.headers.common['Authorization'];
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        verifyOTP,
        setPassword,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

