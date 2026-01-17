"use client";

import { useContext } from "react";
import { AuthContext } from "@/contexts/AuthContext";

/**
 * Custom hook to consume AuthContext.
 *
 * Provides access to authentication state and methods:
 * - user: Current authenticated user or null
 * - loading: Whether auth state is being loaded
 * - login: Function to authenticate user
 * - register: Function to register new user
 * - logout: Function to log out user
 * - refreshAuth: Function to refresh authentication tokens
 *
 * @throws {Error} If used outside of AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
