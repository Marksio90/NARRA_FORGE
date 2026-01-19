/**
 * API Client for NARRA_FORGE Backend
 */

import type {
  CreateJobRequest,
  JobResponse,
  PipelineExecutionResponse,
  ArtifactSchema,
  CostSnapshot,
  BudgetCheckResponse,
  TaskStatusResponse,
  Statistics,
  ErrorResponse,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data: ErrorResponse | null
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = "APIError";
  }
}

async function fetchJSON<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorData: ErrorResponse | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Ignore JSON parse errors
    }
    throw new APIError(response.status, response.statusText, errorData);
  }

  return response.json();
}

export const apiClient = {
  // Health Check
  async health(): Promise<{ status: string; version: string }> {
    return fetchJSON("/health");
  },

  // Jobs
  async createJob(request: CreateJobRequest): Promise<JobResponse> {
    return fetchJSON("/api/v1/jobs", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  async getJob(jobId: string): Promise<JobResponse> {
    return fetchJSON(`/api/v1/jobs/${jobId}`);
  },

  async listJobs(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<JobResponse[]> {
    const query = new URLSearchParams();
    if (params?.skip) query.set("skip", params.skip.toString());
    if (params?.limit) query.set("limit", params.limit.toString());
    if (params?.status) query.set("status", params.status);

    const queryString = query.toString();
    return fetchJSON(`/api/v1/jobs${queryString ? `?${queryString}` : ""}`);
  },

  async cancelJob(jobId: string): Promise<{ message: string }> {
    return fetchJSON(`/api/v1/jobs/${jobId}/cancel`, {
      method: "POST",
    });
  },

  // Pipeline
  async executePipeline(jobId: string): Promise<PipelineExecutionResponse> {
    return fetchJSON(`/api/v1/pipeline/${jobId}/execute`, {
      method: "POST",
    });
  },

  async getPipelineStatus(jobId: string): Promise<PipelineExecutionResponse> {
    return fetchJSON(`/api/v1/pipeline/${jobId}/status`);
  },

  // Artifacts
  async getArtifacts(jobId: string): Promise<ArtifactSchema[]> {
    return fetchJSON(`/api/v1/jobs/${jobId}/artifacts`);
  },

  async getArtifact(artifactId: string): Promise<ArtifactSchema> {
    return fetchJSON(`/api/v1/artifacts/${artifactId}`);
  },

  // Cost Tracking
  async getCosts(jobId: string): Promise<CostSnapshot[]> {
    return fetchJSON(`/api/v1/jobs/${jobId}/costs`);
  },

  async checkBudget(jobId: string): Promise<BudgetCheckResponse> {
    return fetchJSON(`/api/v1/jobs/${jobId}/budget`);
  },

  // Tasks
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    return fetchJSON(`/api/v1/tasks/${taskId}`);
  },

  async cancelTask(taskId: string): Promise<{ message: string }> {
    return fetchJSON(`/api/v1/tasks/${taskId}/cancel`, {
      method: "POST",
    });
  },

  // Observability
  async getStatistics(): Promise<Statistics> {
    return fetchJSON("/api/v1/observability/statistics");
  },
};

export { APIError };
