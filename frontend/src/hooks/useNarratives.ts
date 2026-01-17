"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/services/api";
import type { Narrative, NarrativeListResponse } from "@/types/api";

interface UseNarrativesOptions {
  page?: number;
  pageSize?: number;
  projectId?: string;
  genre?: string;
  productionType?: string;
  autoFetch?: boolean;
}

interface UseNarrativesReturn {
  narratives: Narrative[];
  total: number;
  totalPages: number;
  currentPage: number;
  loading: boolean;
  error: string | null;
  fetchNarratives: (page?: number) => Promise<void>;
  deleteNarrative: (id: string) => Promise<void>;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for managing narratives.
 *
 * Provides methods to fetch and delete narratives
 * with loading and error states. Supports filtering by project, genre, and production type.
 */
export function useNarratives(options: UseNarrativesOptions = {}): UseNarrativesReturn {
  const {
    page = 1,
    pageSize = 20,
    projectId,
    genre,
    productionType,
    autoFetch = true,
  } = options;

  const [narratives, setNarratives] = useState<Narrative[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(page);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNarratives = useCallback(async (fetchPage?: number) => {
    const targetPage = fetchPage ?? currentPage;
    setLoading(true);
    setError(null);

    try {
      const response = await api.listNarratives({
        page: targetPage,
        pageSize,
        projectId,
        genre,
        productionType,
      });
      setNarratives(response.narratives);
      setTotal(response.total);
      setTotalPages(response.total_pages);
      setCurrentPage(response.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch narratives");
      console.error("Error fetching narratives:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, projectId, genre, productionType]);

  const deleteNarrative = useCallback(async (id: string) => {
    setError(null);
    try {
      await api.deleteNarrative(id);
      // Remove narrative from local state
      setNarratives(prev => prev.filter(n => n.id !== id));
      setTotal(prev => prev - 1);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to delete narrative";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const refetch = useCallback(() => fetchNarratives(currentPage), [fetchNarratives, currentPage]);

  // Auto-fetch on mount if enabled
  useEffect(() => {
    if (autoFetch) {
      fetchNarratives(page);
    }
  }, [autoFetch]); // Only run on mount

  return {
    narratives,
    total,
    totalPages,
    currentPage,
    loading,
    error,
    fetchNarratives,
    deleteNarrative,
    refetch,
  };
}
