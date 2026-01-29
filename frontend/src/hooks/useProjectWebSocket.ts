/**
 * WebSocket Hook for NarraForge 2.0 Live Preview
 *
 * Real-time streaming of book generation progress.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export type EventType =
  | 'titan_analysis_start'
  | 'titan_analysis_progress'
  | 'titan_analysis_complete'
  | 'parameters_generated'
  | 'character_born'
  | 'world_building_update'
  | 'chapter_start'
  | 'scene_start'
  | 'prose_stream'
  | 'scene_complete'
  | 'chapter_complete'
  | 'quality_check'
  | 'repair_attempt'
  | 'generation_complete'
  | 'error'
  | 'connection_established';

export interface TITANDimension {
  name: string;
  score: number;
  description: string;
}

export interface Character {
  name: string;
  role: string;
  archetype?: string;
  wound?: string;
  desire?: string;
}

export interface QualityResult {
  score: number;
  level: string;
  criteria: Record<string, number>;
  suggestions: string[];
}

export interface WebSocketEvent {
  type: EventType;
  data: any;
  timestamp: string;
  project_id: number;
}

export interface LivePreviewState {
  isConnected: boolean;
  currentPhase: string;
  titanAnalysis: {
    dimensions: TITANDimension[];
    overallComplexity: number;
    suggestedGenre?: string;
  } | null;
  characters: Character[];
  worldBuildingProgress: {
    aspect: string;
    content: string;
  }[];
  currentChapter: number;
  currentScene: number;
  proseBuffer: string;
  completedScenes: {
    chapter: number;
    scene: number;
    wordCount: number;
    qualityScore: number;
  }[];
  qualityChecks: QualityResult[];
  repairAttempts: {
    chapter: number;
    scene: number;
    attempt: number;
    reason: string;
  }[];
  errors: string[];
  generationComplete: boolean;
  finalResult: any | null;
}

const initialState: LivePreviewState = {
  isConnected: false,
  currentPhase: 'initializing',
  titanAnalysis: null,
  characters: [],
  worldBuildingProgress: [],
  currentChapter: 0,
  currentScene: 0,
  proseBuffer: '',
  completedScenes: [],
  qualityChecks: [],
  repairAttempts: [],
  errors: [],
  generationComplete: false,
  finalResult: null,
};

export function useProjectWebSocket(projectId: number | null) {
  const [state, setState] = useState<LivePreviewState>(initialState);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!projectId) return;

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://localhost:8000/ws/project/${projectId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected for project:', projectId);
      reconnectAttemptsRef.current = 0;
      setState(prev => ({ ...prev, isConnected: true }));
    };

    ws.onmessage = (event) => {
      try {
        const wsEvent: WebSocketEvent = JSON.parse(event.data);
        handleEvent(wsEvent);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setState(prev => ({
        ...prev,
        errors: [...prev.errors, 'WebSocket connection error']
      }));
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setState(prev => ({ ...prev, isConnected: false }));

      // Attempt reconnection
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000;
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++;
          connect();
        }, delay);
      }
    };

    wsRef.current = ws;
  }, [projectId]);

  const handleEvent = useCallback((event: WebSocketEvent) => {
    setState(prev => {
      switch (event.type) {
        case 'connection_established':
          return { ...prev, currentPhase: 'connected' };

        case 'titan_analysis_start':
          return {
            ...prev,
            currentPhase: 'titan_analysis',
            titanAnalysis: { dimensions: [], overallComplexity: 0 }
          };

        case 'titan_analysis_progress':
          return {
            ...prev,
            titanAnalysis: {
              ...prev.titanAnalysis!,
              dimensions: [
                ...(prev.titanAnalysis?.dimensions || []),
                event.data.dimension
              ]
            }
          };

        case 'titan_analysis_complete':
          return {
            ...prev,
            currentPhase: 'parameters',
            titanAnalysis: {
              dimensions: event.data.dimensions || prev.titanAnalysis?.dimensions || [],
              overallComplexity: event.data.overall_complexity || 0,
              suggestedGenre: event.data.suggested_genre
            }
          };

        case 'parameters_generated':
          return {
            ...prev,
            currentPhase: 'character_creation'
          };

        case 'character_born':
          return {
            ...prev,
            characters: [...prev.characters, event.data.character]
          };

        case 'world_building_update':
          return {
            ...prev,
            currentPhase: 'world_building',
            worldBuildingProgress: [
              ...prev.worldBuildingProgress,
              { aspect: event.data.aspect, content: event.data.content }
            ]
          };

        case 'chapter_start':
          return {
            ...prev,
            currentPhase: 'generation',
            currentChapter: event.data.chapter_number,
            currentScene: 0,
            proseBuffer: ''
          };

        case 'scene_start':
          return {
            ...prev,
            currentScene: event.data.scene_number,
            proseBuffer: ''
          };

        case 'prose_stream':
          return {
            ...prev,
            proseBuffer: prev.proseBuffer + (event.data.token || event.data.chunk || '')
          };

        case 'scene_complete':
          return {
            ...prev,
            completedScenes: [
              ...prev.completedScenes,
              {
                chapter: event.data.chapter_number,
                scene: event.data.scene_number,
                wordCount: event.data.word_count,
                qualityScore: event.data.quality_score
              }
            ],
            proseBuffer: ''
          };

        case 'chapter_complete':
          return {
            ...prev,
            currentPhase: `chapter_${event.data.chapter_number}_complete`
          };

        case 'quality_check':
          return {
            ...prev,
            qualityChecks: [...prev.qualityChecks, event.data.result]
          };

        case 'repair_attempt':
          return {
            ...prev,
            repairAttempts: [
              ...prev.repairAttempts,
              {
                chapter: event.data.chapter_number,
                scene: event.data.scene_number,
                attempt: event.data.attempt_number,
                reason: event.data.reason
              }
            ]
          };

        case 'generation_complete':
          return {
            ...prev,
            currentPhase: 'complete',
            generationComplete: true,
            finalResult: event.data
          };

        case 'error':
          return {
            ...prev,
            errors: [...prev.errors, event.data.message || 'Unknown error']
          };

        default:
          return prev;
      }
    });
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setState(initialState);
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  useEffect(() => {
    if (projectId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [projectId, connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    reset,
  };
}

export default useProjectWebSocket;
