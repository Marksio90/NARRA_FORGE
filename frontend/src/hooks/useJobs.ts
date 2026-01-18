"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/services/api";
import type { Job, JobListResponse, CreateJobRequest } from "@/types/api";
import { JobStatus } from "@/types/api";

interface UseJobsOptions {
  page?: number;
  pageSize?: number;
  projectId?: string;
  status?: string;
  autoFetch?: boolean;
  pollInterval?: number; // Poll for updates every N milliseconds
}

interface UseJobsReturn {
  jobs: Job[];
  total: number;
  totalPages: number;
  currentPage: number;
  loading: boolean;
  error: string | null;
  fetchJobs: (page?: number) => Promise<void>;
  createJob: (data: CreateJobRequest) => Promise<Job>;
  cancelJob: (id: string) => Promise<void>;
  resumeJob: (id: string) => Promise<Job>;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for managing generation jobs.
 *
 * Provides methods to fetch, create, cancel, and resume jobs
 * with loading and error states. Supports polling for real-time updates.
 */
export function useJobs(options: UseJobsOptions = {}): UseJobsReturn {
  const {
    page = 1,
    pageSize = 20,
    projectId,
    status,
    autoFetch = true,
    pollInterval,
  } = options;

  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(page);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async (fetchPage?: number) => {
    const targetPage = fetchPage ?? currentPage;
    setLoading(true);
    setError(null);

    try {
      const response = await api.listJobs({
        page: targetPage,
        pageSize,
        projectId,
        status,
      });
      setJobs(response.jobs);
      setTotal(response.total);
      setTotalPages(response.total_pages);
      setCurrentPage(response.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch jobs");
      console.error("Error fetching jobs:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, projectId, status]);

  const createJob = useCallback(async (data: CreateJobRequest) => {
    setError(null);
    try {
      const newJob = await api.createJob(data);
      await fetchJobs(1); // Refresh list, go to first page
      return newJob;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to create job";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [fetchJobs]);

  const cancelJob = useCallback(async (id: string) => {
    setError(null);
    try {
      await api.cancelJob(id);
      // Update job status in local state
      setJobs(prev =>
        prev.map(j => j.id === id ? { ...j, status: JobStatus.CANCELLED } : j)
      );
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to cancel job";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const resumeJob = useCallback(async (id: string) => {
    setError(null);
    try {
      const resumedJob = await api.resumeJob(id);
      // Update job in local state
      setJobs(prev =>
        prev.map(j => j.id === id ? resumedJob : j)
      );
      return resumedJob;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to resume job";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const refetch = useCallback(() => fetchJobs(currentPage), [fetchJobs, currentPage]);

  // Auto-fetch on mount if enabled
  useEffect(() => {
    if (autoFetch) {
      fetchJobs(page);
    }
  }, [autoFetch]); // Only run on mount

  // Polling for real-time updates
  useEffect(() => {
    if (!pollInterval || pollInterval <= 0) return;

    const interval = setInterval(() => {
      fetchJobs(currentPage);
    }, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval, fetchJobs, currentPage]);

  return {
    jobs,
    total,
    totalPages,
    currentPage,
    loading,
    error,
    fetchJobs,
    createJob,
    cancelJob,
    resumeJob,
    refetch,
  };
}
