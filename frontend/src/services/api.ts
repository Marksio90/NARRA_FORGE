/**
 * API Client for NARRA_FORGE
 */

import type {
  User,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  Project,
  GenerationJob,
  Narrative,
  CreateProjectRequest,
  CreateJobRequest,
  PaginatedResponse,
  HealthStatus,
} from "@/types/api";

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: "An error occurred",
      }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    const body: LoginRequest = { email, password };
    return this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  async register(
    email: string,
    password: string,
    fullName?: string
  ): Promise<AuthResponse> {
    const body: RegisterRequest = {
      email,
      password,
      full_name: fullName,
    };
    return this.request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  // Project endpoints
  async getProjects(
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<Project>> {
    return this.request<PaginatedResponse<Project>>(
      `/projects?page=${page}&page_size=${pageSize}`
    );
  }

  async listProjects(params: {
    page?: number;
    pageSize?: number;
  }): Promise<{
    projects: Project[];
    total: number;
    total_pages: number;
    page: number;
  }> {
    const { page = 1, pageSize = 20 } = params;
    const response = await this.request<PaginatedResponse<Project>>(
      `/projects?page=${page}&page_size=${pageSize}`
    );

    return {
      projects: response.items,
      total: response.total,
      total_pages: response.total_pages,
      page: response.page,
    };
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/projects/${id}`);
  }

  async createProject(data: CreateProjectRequest): Promise<Project> {
    return this.request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateProject(
    id: string,
    data: Partial<CreateProjectRequest>
  ): Promise<Project> {
    return this.request<Project>(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteProject(id: string): Promise<void> {
    return this.request<void>(`/projects/${id}`, {
      method: "DELETE",
    });
  }

  // Job endpoints
  async getJobs(
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<GenerationJob>> {
    return this.request<PaginatedResponse<GenerationJob>>(
      `/jobs?page=${page}&page_size=${pageSize}`
    );
  }

  async listJobs(params: {
    page?: number;
    pageSize?: number;
    projectId?: string;
    status?: string;
  }): Promise<{
    jobs: GenerationJob[];
    total: number;
    total_pages: number;
    page: number;
  }> {
    const { page = 1, pageSize = 20, projectId, status } = params;
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (projectId) queryParams.append("project_id", projectId);
    if (status) queryParams.append("status", status);

    const response = await this.request<PaginatedResponse<GenerationJob>>(
      `/jobs?${queryParams.toString()}`
    );

    return {
      jobs: response.items,
      total: response.total,
      total_pages: response.total_pages,
      page: response.page,
    };
  }

  async getJob(id: string): Promise<GenerationJob> {
    return this.request<GenerationJob>(`/jobs/${id}`);
  }

  async createJob(data: CreateJobRequest): Promise<GenerationJob> {
    return this.request<GenerationJob>("/jobs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async cancelJob(id: string): Promise<GenerationJob> {
    return this.request<GenerationJob>(`/jobs/${id}/cancel`, {
      method: "POST",
    });
  }

  async resumeJob(id: string): Promise<GenerationJob> {
    return this.request<GenerationJob>(`/jobs/${id}/resume`, {
      method: "POST",
    });
  }

  // Narrative endpoints
  async getNarratives(
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<Narrative>> {
    return this.request<PaginatedResponse<Narrative>>(
      `/narratives?page=${page}&page_size=${pageSize}`
    );
  }

  async listNarratives(params: {
    page?: number;
    pageSize?: number;
    projectId?: string;
  }): Promise<{
    narratives: Narrative[];
    total: number;
    total_pages: number;
    page: number;
  }> {
    const { page = 1, pageSize = 20, projectId } = params;
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (projectId) queryParams.append("project_id", projectId);

    const response = await this.request<PaginatedResponse<Narrative>>(
      `/narratives?${queryParams.toString()}`
    );

    return {
      narratives: response.items,
      total: response.total,
      total_pages: response.total_pages,
      page: response.page,
    };
  }

  async getNarrative(id: string): Promise<Narrative> {
    return this.request<Narrative>(`/narratives/${id}`);
  }

  async deleteNarrative(id: string): Promise<void> {
    return this.request<void>(`/narratives/${id}`, {
      method: "DELETE",
    });
  }

  async downloadNarrative(id: string, format: "txt" | "pdf" | "docx" = "txt"): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/narratives/${id}/download?format=${format}`,
      {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.blob();
  }

  // Health endpoint
  async getHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>("/health");
  }
}

export const api = new ApiClient();
