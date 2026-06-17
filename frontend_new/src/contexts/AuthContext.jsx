import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/authApi';
import apiClient from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Validate storage token expiration if any
    const storedToken = localStorage.getItem('token');
    const storedEmail = localStorage.getItem('userEmail');
    if (storedToken) {
      setToken(storedToken);
      setUserEmail(storedEmail);
      // Ensure API client has token on load
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const data = await authApi.login(email, password);
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userEmail', data.email);
        setToken(data.access_token);
        setUserEmail(data.email);
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
        return { success: true };
      }
      return { success: false, error: 'Authentication failed' };
    } catch (err) {
      console.error('Login error:', err);
      const msg = err.response?.data?.detail || 'Invalid email or password';
      return { success: false, error: msg };
    }
  };

  const register = async (email, password) => {
    try {
      const data = await authApi.register(email, password);
      if (data.status === 'success') {
        return { success: true };
      }
      return { success: false, error: 'Registration failed' };
    } catch (err) {
      console.error('Registration error:', err);
      const msg = err.response?.data?.detail || 'Registration failed';
      return { success: false, error: msg };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    setToken(null);
    setUserEmail(null);
    delete apiClient.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ token, userEmail, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
