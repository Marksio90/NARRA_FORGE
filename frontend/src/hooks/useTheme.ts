"use client";

import { useContext } from "react";
import { ThemeContext } from "@/contexts/ThemeContext";

/**
 * Custom hook to consume ThemeContext.
 *
 * Provides access to theme state and methods:
 * - theme: Current theme ("light" or "dark")
 * - setTheme: Function to set specific theme
 * - toggleTheme: Function to toggle between light and dark
 *
 * @throws {Error} If used outside of ThemeProvider
 */
export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }

  return context;
}
