/**
 * API Type Definitions for NARRA_FORGE
 */

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  role: string;
  created_at: string;
  monthly_generations_used: number;
  monthly_generation_limit: number;
  monthly_cost_used_usd: number;
  monthly_cost_limit_usd: number;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  world_id?: string;
  default_genre?: string;
  default_production_type?: string;
  narrative_count: number;
  total_word_count: number;
  total_cost_usd: number;
  created_at: string;
  updated_at: string;
}

export interface GenerationJob {
  id: string;
  user_id: string;
  project_id?: string;
  status: JobStatus;
  production_brief: ProductionBrief;
  progress_percentage: number;
  current_stage?: string;
  completed_stages: string[];
  estimated_cost_usd: number;
  actual_cost_usd: number;
  tokens_used: number;
  output?: any;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  can_resume: boolean;
  created_at: string;
  updated_at: string;
}

export enum JobStatus {
  PENDING = "PENDING",
  RUNNING = "RUNNING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
  CANCELLED = "CANCELLED",
}

export interface ProductionBrief {
  production_type: ProductionType;
  genre: Genre;
  subject: string;
  style_instructions?: string;
  character_count?: number;
  target_length: number;
  world_id?: string;
}

export enum ProductionType {
  SHORT_STORY = "SHORT_STORY",
  NOVELLA = "NOVELLA",
  NOVEL = "NOVEL",
  EPIC_SAGA = "EPIC_SAGA",
}

export enum Genre {
  FANTASY = "FANTASY",
  SCI_FI = "SCI_FI",
  HORROR = "HORROR",
  THRILLER = "THRILLER",
  MYSTERY = "MYSTERY",
  DRAMA = "DRAMA",
  ROMANCE = "ROMANCE",
  HYBRID = "HYBRID",
}

export interface Narrative {
  id: string;
  user_id: string;
  project_id?: string;
  job_id: string;
  title: string;
  production_type: string;
  genre: string;
  narrative_text: string;
  summary?: string; // Optional narrative summary
  word_count: number;
  narrative_metadata?: any;
  quality_metrics?: any;
  overall_quality_score: number;
  quality_score?: number; // Alias for overall_quality_score
  generation_cost_usd: number;
  tokens_used: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
}

export interface CreateJobRequest {
  project_id?: string;
  production_brief: ProductionBrief;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  request_id?: string;
  error_type?: string;
}

export interface HealthStatus {
  status: string;
  database: string;
  redis: string;
  celery: string;
  timestamp: string;
}
