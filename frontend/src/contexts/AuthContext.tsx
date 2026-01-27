/**
 * Authentication Context for NarraForge
 * Manages user authentication state, tokens, and user data
 */

import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios, { AxiosError } from 'axios';

// Types
export type SubscriptionTier = 'FREE' | 'PRO' | 'PREMIUM';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  subscription_tier: SubscriptionTier;
  credits_remaining: number;
  books_generated: number;
  total_words_generated: number;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Token storage keys
const ACCESS_TOKEN_KEY = 'narraforge_access_token';
const REFRESH_TOKEN_KEY = 'narraforge_refresh_token';
const USER_KEY = 'narraforge_user';

// Helper functions for token storage
const storeTokens = (tokens: AuthTokens) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
};

const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

const getStoredAccessToken = (): string | null => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

const getStoredRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

const storeUser = (user: User) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

const getStoredUser = (): User | null => {
  const userStr = localStorage.getItem(USER_KEY);
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

// Create axios instance with auth interceptor
const createAuthAxios = (token: string | null) => {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  return instance;
};

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(getStoredUser());
  const [tokens, setTokens] = useState<AuthTokens | null>(() => {
    const accessToken = getStoredAccessToken();
    const refreshToken = getStoredRefreshToken();
    if (accessToken && refreshToken) {
      return {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: 0,
      };
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!tokens?.access_token && !!user;

  // Fetch current user data
  const fetchUser = useCallback(async (token: string): Promise<User | null> => {
    try {
      const response = await createAuthAxios(token).get('/auth/me');
      return response.data;
    } catch (err) {
      console.error('Failed to fetch user:', err);
      return null;
    }
  }, []);

  // Refresh access token
  const refreshAccessToken = useCallback(async (): Promise<AuthTokens | null> => {
    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) return null;

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });
      const newTokens: AuthTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      };
      storeTokens(newTokens);
      return newTokens;
    } catch (err) {
      console.error('Token refresh failed:', err);
      return null;
    }
  }, []);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      const accessToken = getStoredAccessToken();

      if (accessToken) {
        // Try to fetch user with stored token
        let userData = await fetchUser(accessToken);

        if (!userData) {
          // Token might be expired, try to refresh
          const newTokens = await refreshAccessToken();
          if (newTokens) {
            setTokens(newTokens);
            userData = await fetchUser(newTokens.access_token);
          }
        }

        if (userData) {
          setUser(userData);
          storeUser(userData);
        } else {
          // All attempts failed, clear auth
          clearTokens();
          setTokens(null);
          setUser(null);
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, [fetchUser, refreshAccessToken]);

  // Login function
  const login = async (email: string, password: string): Promise<void> => {
    setError(null);
    setIsLoading(true);

    try {
      // OAuth2 password flow requires form data
      const formData = new FormData();
      formData.append('username', email); // OAuth2 uses 'username' field
      formData.append('password', password);

      const response = await axios.post(`${API_BASE_URL}/auth/login`, formData);

      const newTokens: AuthTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      };

      const userData: User = response.data.user;

      storeTokens(newTokens);
      storeUser(userData);
      setTokens(newTokens);
      setUser(userData);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      const errorMessage = axiosError.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (
    email: string,
    username: string,
    password: string,
    fullName?: string
  ): Promise<void> => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email,
        username,
        password,
        full_name: fullName,
      });

      const newTokens: AuthTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      };

      const userData: User = response.data.user;

      storeTokens(newTokens);
      storeUser(userData);
      setTokens(newTokens);
      setUser(userData);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      const errorMessage = axiosError.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = useCallback(() => {
    clearTokens();
    setTokens(null);
    setUser(null);
    setError(null);
  }, []);

  // Refresh user data
  const refreshUser = async (): Promise<void> => {
    if (!tokens?.access_token) return;

    const userData = await fetchUser(tokens.access_token);
    if (userData) {
      setUser(userData);
      storeUser(userData);
    }
  };

  // Clear error
  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Hook to get auth headers for API calls
export const useAuthHeaders = () => {
  const { tokens } = useAuth();

  return {
    headers: tokens?.access_token
      ? { Authorization: `Bearer ${tokens.access_token}` }
      : {},
  };
};

// Axios instance with auth
export const useAuthAxios = () => {
  const { tokens, logout } = useAuth();

  const authAxios = axios.create({
    baseURL: API_BASE_URL,
    headers: tokens?.access_token
      ? { Authorization: `Bearer ${tokens.access_token}` }
      : {},
  });

  // Add response interceptor to handle 401 errors
  authAxios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        logout();
      }
      return Promise.reject(error);
    }
  );

  return authAxios;
};

export default AuthContext;
