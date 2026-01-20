/**
 * TypeScript type definitions for NarraForge frontend.
 */

export interface Genre {
  id: string;
  name: string;
  description: string;
  typical_length: string;
  complexity: number;
}

export interface Book {
  id: string;
  genre: string;
  status: 'draft' | 'generating' | 'completed' | 'failed' | 'archived';
  title: string | null;
  subtitle: string | null;
  tagline: string | null;
  blurb: string | null;
  word_count: number;
  chapter_count: number;
  cost_total: number;
  created_at: string;
  completed_at: string | null;
}

export interface Chapter {
  id: string;
  number: number;
  title: string | null;
  content: string;
  word_count: number;
}

export interface Progress {
  phase: string;
  message: string;
  progress: number;
  chapter_progress?: {
    current: number;
    total: number;
  };
}

export interface Cost {
  total: number;
  breakdown: Record<string, number>;
}

export interface AgentStatus {
  agent: string;
  status: 'idle' | 'working' | 'completed' | 'repairing';
  message: string;
}

export interface WebSocketMessage {
  type: 'progress' | 'cost' | 'agent_status' | 'chapter_preview' | 'completed';
  data: any;
}
