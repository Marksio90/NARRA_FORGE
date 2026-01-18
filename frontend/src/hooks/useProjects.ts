"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/services/api";
import type { Project, ProjectListResponse } from "@/types/api";

interface UseProjectsOptions {
  page?: number;
  pageSize?: number;
  autoFetch?: boolean;
}

interface UseProjectsReturn {
  projects: Project[];
  total: number;
  totalPages: number;
  currentPage: number;
  loading: boolean;
  error: string | null;
  fetchProjects: (page?: number) => Promise<void>;
  createProject: (data: {
    name: string;
    description?: string;
    world_id?: string;
    default_genre?: string;
    default_production_type?: string;
  }) => Promise<Project>;
  updateProject: (id: string, data: Partial<Project>) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for managing projects.
 *
 * Provides methods to fetch, create, update, and delete projects
 * with loading and error states.
 */
export function useProjects(options: UseProjectsOptions = {}): UseProjectsReturn {
  const { page = 1, pageSize = 20, autoFetch = true } = options;

  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(page);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async (fetchPage?: number) => {
    const targetPage = fetchPage ?? currentPage;
    setLoading(true);
    setError(null);

    try {
      const response = await api.listProjects({ page: targetPage, pageSize });
      setProjects(response.projects);
      setTotal(response.total);
      setTotalPages(response.total_pages);
      setCurrentPage(response.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch projects");
      console.error("Error fetching projects:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize]);

  const createProject = useCallback(async (data: {
    name: string;
    description?: string;
    world_id?: string;
    default_genre?: string;
    default_production_type?: string;
  }) => {
    setError(null);
    try {
      const newProject = await api.createProject(data);
      await fetchProjects(1); // Refresh list, go to first page
      return newProject;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to create project";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [fetchProjects]);

  const updateProject = useCallback(async (id: string, data: Partial<Project>) => {
    setError(null);
    try {
      const updatedProject = await api.updateProject(id, data);
      // Update project in local state
      setProjects(prev =>
        prev.map(p => p.id === id ? updatedProject : p)
      );
      return updatedProject;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to update project";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const deleteProject = useCallback(async (id: string) => {
    setError(null);
    try {
      await api.deleteProject(id);
      // Remove project from local state
      setProjects(prev => prev.filter(p => p.id !== id));
      setTotal(prev => prev - 1);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to delete project";
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const refetch = useCallback(() => fetchProjects(currentPage), [fetchProjects, currentPage]);

  // Auto-fetch on mount if enabled
  useEffect(() => {
    if (autoFetch) {
      fetchProjects(page);
    }
  }, [autoFetch]); // Only run on mount

  return {
    projects,
    total,
    totalPages,
    currentPage,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    refetch,
  };
}
