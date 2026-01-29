/**
 * LivePreview Component for NarraForge 2.0
 *
 * Real-time visualization of book generation progress.
 */

import React, { useMemo } from 'react';
import { LivePreviewState, TITANDimension } from '../hooks/useProjectWebSocket';

interface LivePreviewProps {
  state: LivePreviewState;
  projectName: string;
}

// TITAN Dimension visualization
const TITANVisualization: React.FC<{ dimensions: TITANDimension[]; complexity: number }> = ({
  dimensions,
  complexity
}) => {
  const dimensionColors: Record<string, string> = {
    SEMANTIC_DEPTH: 'bg-blue-500',
    EMOTIONAL_RESONANCE: 'bg-pink-500',
    TEMPORALITY: 'bg-purple-500',
    SPATIAL_WORLD: 'bg-green-500',
    IMPLIED_CHARACTERS: 'bg-yellow-500',
    CENTRAL_CONFLICT: 'bg-red-500',
    NARRATIVE_PROMISE: 'bg-indigo-500',
    STYLE_TONE: 'bg-cyan-500',
    DEEP_PSYCHOLOGY: 'bg-orange-500',
    INTERTEXTUALITY: 'bg-teal-500',
    COMMERCIAL_POTENTIAL: 'bg-emerald-500',
    TRANSCENDENCE: 'bg-amber-500',
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 border border-purple-500/30">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-bold text-white flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          TITAN Analysis
        </h4>
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">Complexity:</span>
          <span className="text-purple-400 font-bold text-lg">{(complexity * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {dimensions.map((dim, index) => (
          <div
            key={dim.name}
            className="bg-gray-800/50 rounded-lg p-3 transform transition-all duration-300 hover:scale-105"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400 truncate">
                {dim.name.replace(/_/g, ' ')}
              </span>
              <span className="text-sm font-bold text-white">
                {(dim.score * 100).toFixed(0)}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`${dimensionColors[dim.name] || 'bg-purple-500'} h-2 rounded-full transition-all duration-500`}
                style={{ width: `${dim.score * 100}%` }}
              />
            </div>
            {dim.description && (
              <p className="text-xs text-gray-500 mt-1 line-clamp-2">{dim.description}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Character birth visualization
const CharacterCard: React.FC<{ character: any; index: number }> = ({ character, index }) => {
  const roleColors: Record<string, string> = {
    protagonist: 'from-blue-600 to-purple-600',
    antagonist: 'from-red-600 to-orange-600',
    mentor: 'from-green-600 to-teal-600',
    ally: 'from-cyan-600 to-blue-600',
    love_interest: 'from-pink-600 to-rose-600',
    supporting: 'from-gray-600 to-gray-700',
  };

  return (
    <div
      className={`bg-gradient-to-br ${roleColors[character.role] || 'from-gray-600 to-gray-700'} rounded-lg p-4 transform transition-all duration-500 animate-fadeIn`}
      style={{ animationDelay: `${index * 200}ms` }}
    >
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-2xl">
          {character.role === 'protagonist' ? '👤' :
           character.role === 'antagonist' ? '👿' :
           character.role === 'mentor' ? '🧙' :
           character.role === 'love_interest' ? '💕' : '👥'}
        </div>
        <div>
          <h5 className="text-white font-bold">{character.name}</h5>
          <p className="text-white/70 text-sm capitalize">{character.role?.replace('_', ' ')}</p>
        </div>
      </div>
      {character.archetype && (
        <div className="mt-2 text-xs text-white/60">
          Archetype: {character.archetype}
        </div>
      )}
      {character.wound && (
        <div className="mt-1 text-xs text-white/60">
          Wound: {character.wound}
        </div>
      )}
    </div>
  );
};

// Prose streaming visualization
const ProseStream: React.FC<{ content: string; chapter: number; scene: number }> = ({
  content,
  chapter,
  scene
}) => {
  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-indigo-500/30">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-bold text-white flex items-center gap-2">
          <span className="text-2xl">✍️</span>
          Live Writing
        </h4>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-indigo-600 rounded text-xs text-white">
            Chapter {chapter}
          </span>
          <span className="px-2 py-1 bg-purple-600 rounded text-xs text-white">
            Scene {scene}
          </span>
        </div>
      </div>
      <div className="bg-gray-800 rounded-lg p-4 max-h-64 overflow-y-auto font-serif text-gray-200 leading-relaxed">
        {content || (
          <span className="text-gray-500 italic">Waiting for content...</span>
        )}
        <span className="inline-block w-2 h-4 bg-indigo-500 ml-1 animate-pulse" />
      </div>
      <div className="mt-2 text-xs text-gray-500">
        {content.split(' ').filter(w => w).length} words
      </div>
    </div>
  );
};

// Progress timeline
const ProgressTimeline: React.FC<{ phase: string; completedScenes: any[] }> = ({
  phase,
  completedScenes
}) => {
  const phases = [
    { key: 'titan_analysis', label: 'TITAN', icon: '🎯' },
    { key: 'parameters', label: 'Parameters', icon: '⚙️' },
    { key: 'character_creation', label: 'Characters', icon: '👥' },
    { key: 'world_building', label: 'World', icon: '🌍' },
    { key: 'generation', label: 'Writing', icon: '✍️' },
    { key: 'complete', label: 'Complete', icon: '✅' },
  ];

  const currentIndex = phases.findIndex(p =>
    phase === p.key || phase.startsWith(p.key)
  );

  return (
    <div className="bg-gray-800/50 rounded-xl p-4">
      <div className="flex items-center justify-between">
        {phases.map((p, index) => (
          <React.Fragment key={p.key}>
            <div className={`flex flex-col items-center ${
              index <= currentIndex ? 'opacity-100' : 'opacity-40'
            }`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                index < currentIndex ? 'bg-green-600' :
                index === currentIndex ? 'bg-indigo-600 animate-pulse' :
                'bg-gray-700'
              }`}>
                {index < currentIndex ? '✓' : p.icon}
              </div>
              <span className="text-xs text-gray-400 mt-1">{p.label}</span>
            </div>
            {index < phases.length - 1 && (
              <div className={`flex-1 h-1 mx-2 rounded ${
                index < currentIndex ? 'bg-green-600' : 'bg-gray-700'
              }`} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

// Quality check visualization
const QualityMeter: React.FC<{ checks: any[] }> = ({ checks }) => {
  const latestCheck = checks[checks.length - 1];
  if (!latestCheck) return null;

  const levelColors: Record<string, string> = {
    MASTERPIECE: 'from-yellow-400 to-amber-500',
    BESTSELLER: 'from-green-400 to-emerald-500',
    PROFESSIONAL: 'from-blue-400 to-indigo-500',
    COMPETENT: 'from-gray-400 to-gray-500',
    NEEDS_WORK: 'from-red-400 to-red-600',
  };

  return (
    <div className="bg-gray-800/50 rounded-xl p-4">
      <h4 className="text-sm font-bold text-gray-400 mb-3">Quality Assessment</h4>
      <div className="flex items-center gap-4">
        <div className={`text-4xl font-bold bg-gradient-to-r ${levelColors[latestCheck.level] || 'from-gray-400 to-gray-500'} bg-clip-text text-transparent`}>
          {latestCheck.score}
        </div>
        <div>
          <div className="text-white font-semibold">{latestCheck.level}</div>
          <div className="text-xs text-gray-500">
            {latestCheck.suggestions?.[0] || 'Meeting quality standards'}
          </div>
        </div>
      </div>
    </div>
  );
};

// Main LivePreview component
const LivePreview: React.FC<LivePreviewProps> = ({ state, projectName }) => {
  const {
    isConnected,
    currentPhase,
    titanAnalysis,
    characters,
    worldBuildingProgress,
    currentChapter,
    currentScene,
    proseBuffer,
    completedScenes,
    qualityChecks,
    repairAttempts,
    errors,
    generationComplete,
  } = state;

  const totalWords = useMemo(() => {
    return completedScenes.reduce((sum, s) => sum + s.wordCount, 0);
  }, [completedScenes]);

  return (
    <div className="space-y-6">
      {/* Connection status */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-white">
          Live Preview: {projectName}
        </h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
          isConnected ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
        }`}>
          <span className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
          }`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Progress timeline */}
      <ProgressTimeline phase={currentPhase} completedScenes={completedScenes} />

      {/* TITAN Analysis visualization */}
      {titanAnalysis && titanAnalysis.dimensions.length > 0 && (
        <TITANVisualization
          dimensions={titanAnalysis.dimensions}
          complexity={titanAnalysis.overallComplexity}
        />
      )}

      {/* Characters born */}
      {characters.length > 0 && (
        <div>
          <h4 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
            <span>👥</span>
            Characters ({characters.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {characters.map((char, index) => (
              <CharacterCard key={char.name} character={char} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* World building progress */}
      {worldBuildingProgress.length > 0 && (
        <div className="bg-gray-800/50 rounded-xl p-4">
          <h4 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
            <span>🌍</span>
            World Building
          </h4>
          <div className="space-y-2">
            {worldBuildingProgress.map((item, index) => (
              <div key={index} className="bg-gray-700/50 rounded p-3">
                <span className="text-indigo-400 font-semibold">{item.aspect}:</span>
                <span className="text-gray-300 ml-2">{item.content}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live prose streaming */}
      {currentPhase === 'generation' && (
        <ProseStream
          content={proseBuffer}
          chapter={currentChapter}
          scene={currentScene}
        />
      )}

      {/* Stats and quality */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Progress stats */}
        <div className="bg-gray-800/50 rounded-xl p-4">
          <h4 className="text-sm font-bold text-gray-400 mb-3">Progress</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-500">Scenes Completed</span>
              <span className="text-white font-bold">{completedScenes.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Total Words</span>
              <span className="text-white font-bold">{totalWords.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Repair Attempts</span>
              <span className="text-yellow-400 font-bold">{repairAttempts.length}</span>
            </div>
          </div>
        </div>

        {/* Quality meter */}
        {qualityChecks.length > 0 && (
          <QualityMeter checks={qualityChecks} />
        )}

        {/* Errors */}
        {errors.length > 0 && (
          <div className="bg-red-900/20 rounded-xl p-4 border border-red-500/30">
            <h4 className="text-sm font-bold text-red-400 mb-3">Errors ({errors.length})</h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {errors.map((error, index) => (
                <div key={index} className="text-xs text-red-300">{error}</div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Generation complete */}
      {generationComplete && (
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-6 text-center">
          <div className="text-4xl mb-2">🎉</div>
          <h4 className="text-2xl font-bold text-white mb-2">Generation Complete!</h4>
          <p className="text-white/80">
            Your book has been successfully generated with {totalWords.toLocaleString()} words
            across {completedScenes.length} scenes.
          </p>
        </div>
      )}
    </div>
  );
};

export default LivePreview;
