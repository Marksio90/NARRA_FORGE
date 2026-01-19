/**
 * API Types - matches backend Pydantic schemas
 */

// Job Types
export type JobStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export type JobType =
  | "short_story"
  | "novel_chapter"
  | "scene"
  | "character_study"
  | "world_building";

export type Genre =
  | "fantasy"
  | "sci-fi"
  | "thriller"
  | "literary"
  | "horror"
  | "mystery"
  | "romance";

// Pipeline Stages
export type PipelineStage =
  | "STRUCTURE"
  | "PLAN"
  | "QA"
  | "PROSE"
  | "STYLE"
  | "DIALOG"
  | "CHARACTER_PROFILE"
  | "WORLD"
  | "PACKAGE";

// Job Request/Response
export interface CreateJobRequest {
  job_type: JobType;
  user_inspiration: string;
  genre?: Genre;
  target_word_count?: number;
  budget_limit?: number;
  constraints?: Record<string, any>;
}

export interface JobResponse {
  job_id: string;
  job_type: JobType;
  genre: Genre;
  status: JobStatus;
  user_inspiration: string;
  target_word_count: number;
  budget_limit: number;
  current_cost: number | null;
  progress: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error_message?: string;
}

// Pipeline Execution
export interface PipelineExecutionResponse {
  job_id: string;
  status: string;
  current_stage?: PipelineStage;
  completed_stages: PipelineStage[];
  progress: number;
  total_cost: number;
  artifacts_created: number;
  started_at: string;
  estimated_completion?: string;
}

// Artifacts
export type ArtifactType =
  | "world_spec"
  | "character_spec"
  | "plot_outline"
  | "prose_segment"
  | "qa_report"
  | "style_guide";

export interface ArtifactSchema {
  artifact_id: string;
  job_id: string;
  type: ArtifactType;
  data: Record<string, any>;
  version: number;
  created_at: string;
  metadata?: Record<string, any>;
}

// Cost Tracking
export interface CostSnapshot {
  snapshot_id: string;
  job_id: string;
  agent_name: string;
  model: string;
  tokens_input: number;
  tokens_output: number;
  cost_usd: number;
  created_at: string;
}

export interface BudgetCheckResponse {
  job_id: string;
  budget_limit: number;
  current_cost: number;
  remaining_budget: number;
  budget_exceeded: boolean;
  warning_threshold: number;
}

// Task Status
export interface TaskStatusResponse {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  result?: any;
  error?: string;
  started_at?: string;
  completed_at?: string;
}

// QA Results
export interface QAScore {
  logic_score: number;
  psychology_score: number;
  timeline_score: number;
}

export interface QAResult {
  passed: boolean;
  scores: QAScore;
  critical_errors: string[];
  warnings: string[];
}

// Statistics
export interface Statistics {
  traces: {
    total_count: number;
    by_name: Record<string, {
      count: number;
      total_duration: number;
      avg_duration: number;
      min_duration: number;
      max_duration: number;
    }>;
  };
  metrics: Record<string, {
    count: number;
    total: number;
    avg: number;
    min: number;
    max: number;
  }>;
  events: {
    total_count: number;
    by_name: Record<string, number>;
  };
}

// Error Response
export interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp?: string;
}
