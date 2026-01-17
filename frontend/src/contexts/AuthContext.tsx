"use client";

import React, { createContext, useState, useEffect, useCallback } from "react";
import { api } from "@/services/api";
import type { User, AuthResponse } from "@/types/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    api.setToken(null);
    setUser(null);
  }, []);

  const refreshAuth = useCallback(async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      logout();
      return;
    }

    try {
      const response = await api.refreshToken(refreshToken);
      saveAuthData(response);
    } catch (error) {
      logout();
      throw error;
    }
  }, [logout]);

  // Load user from localStorage on mount
  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");
    const storedUser = localStorage.getItem("user");

    if (accessToken && storedUser) {
      api.setToken(accessToken);
      setUser(JSON.parse(storedUser));
    } else if (refreshToken) {
      // Try to refresh token
      refreshAuth().catch(() => logout());
    }

    setLoading(false);
  }, [refreshAuth, logout]);

  const saveAuthData = (response: AuthResponse) => {
    localStorage.setItem("access_token", response.access_token);
    localStorage.setItem("refresh_token", response.refresh_token);
    localStorage.setItem("user", JSON.stringify(response.user));
    api.setToken(response.access_token);
    setUser(response.user);
  };

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    saveAuthData(response);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const response = await api.register(email, password, fullName);
    saveAuthData(response);
  };


  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshAuth }}>
      {children}
    </AuthContext.Provider>
  );
}
