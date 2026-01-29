/**
 * TITAN Radar Chart Component for NarraForge 2.0
 *
 * Visualizes the 12-dimensional TITAN analysis as a radar/spider chart.
 */

import React, { useMemo } from 'react';

interface TITANDimension {
  name: string;
  score: number;
  description?: string;
}

interface TITANRadarChartProps {
  dimensions: TITANDimension[];
  size?: number;
  showLabels?: boolean;
  animated?: boolean;
  colorScheme?: 'purple' | 'blue' | 'green' | 'gold';
}

const TITANRadarChart: React.FC<TITANRadarChartProps> = ({
  dimensions,
  size = 300,
  showLabels = true,
  animated = true,
  colorScheme = 'purple'
}) => {
  const center = size / 2;
  const radius = size * 0.35;
  const labelRadius = size * 0.45;

  // Color schemes
  const colors = {
    purple: {
      fill: 'rgba(139, 92, 246, 0.3)',
      stroke: '#8B5CF6',
      point: '#A78BFA',
      grid: 'rgba(139, 92, 246, 0.2)',
    },
    blue: {
      fill: 'rgba(59, 130, 246, 0.3)',
      stroke: '#3B82F6',
      point: '#60A5FA',
      grid: 'rgba(59, 130, 246, 0.2)',
    },
    green: {
      fill: 'rgba(16, 185, 129, 0.3)',
      stroke: '#10B981',
      point: '#34D399',
      grid: 'rgba(16, 185, 129, 0.2)',
    },
    gold: {
      fill: 'rgba(245, 158, 11, 0.3)',
      stroke: '#F59E0B',
      point: '#FBBF24',
      grid: 'rgba(245, 158, 11, 0.2)',
    },
  };

  const currentColors = colors[colorScheme];

  // Short labels for dimensions
  const shortLabels: Record<string, string> = {
    SEMANTIC_DEPTH: 'Semantic',
    EMOTIONAL_RESONANCE: 'Emotion',
    TEMPORALITY: 'Time',
    SPATIAL_WORLD: 'Space',
    IMPLIED_CHARACTERS: 'Characters',
    CENTRAL_CONFLICT: 'Conflict',
    NARRATIVE_PROMISE: 'Promise',
    STYLE_TONE: 'Style',
    DEEP_PSYCHOLOGY: 'Psychology',
    INTERTEXTUALITY: 'Intertext',
    COMMERCIAL_POTENTIAL: 'Commercial',
    TRANSCENDENCE: 'Transcend',
  };

  // Calculate points for the radar chart
  const points = useMemo(() => {
    const numDimensions = dimensions.length || 12;
    const angleStep = (2 * Math.PI) / numDimensions;

    return dimensions.map((dim, index) => {
      const angle = index * angleStep - Math.PI / 2; // Start from top
      const value = dim.score * radius;
      return {
        x: center + Math.cos(angle) * value,
        y: center + Math.sin(angle) * value,
        labelX: center + Math.cos(angle) * labelRadius,
        labelY: center + Math.sin(angle) * labelRadius,
        angle,
        ...dim,
      };
    });
  }, [dimensions, center, radius, labelRadius]);

  // Generate polygon path
  const polygonPath = useMemo(() => {
    if (points.length === 0) return '';
    return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
  }, [points]);

  // Generate grid lines
  const gridLines = useMemo(() => {
    const levels = [0.2, 0.4, 0.6, 0.8, 1.0];
    const numDimensions = dimensions.length || 12;
    const angleStep = (2 * Math.PI) / numDimensions;

    return levels.map(level => {
      const gridPoints = Array.from({ length: numDimensions }, (_, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const r = level * radius;
        return {
          x: center + Math.cos(angle) * r,
          y: center + Math.sin(angle) * r,
        };
      });
      return gridPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
    });
  }, [dimensions.length, center, radius]);

  // Generate axis lines
  const axisLines = useMemo(() => {
    const numDimensions = dimensions.length || 12;
    const angleStep = (2 * Math.PI) / numDimensions;

    return Array.from({ length: numDimensions }, (_, i) => {
      const angle = i * angleStep - Math.PI / 2;
      return {
        x1: center,
        y1: center,
        x2: center + Math.cos(angle) * radius,
        y2: center + Math.sin(angle) * radius,
      };
    });
  }, [dimensions.length, center, radius]);

  if (dimensions.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-800/50 rounded-xl"
        style={{ width: size, height: size }}
      >
        <div className="text-gray-500">Waiting for TITAN analysis...</div>
      </div>
    );
  }

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="overflow-visible">
        {/* Grid circles */}
        {gridLines.map((path, index) => (
          <path
            key={`grid-${index}`}
            d={path}
            fill="none"
            stroke={currentColors.grid}
            strokeWidth="1"
          />
        ))}

        {/* Axis lines */}
        {axisLines.map((line, index) => (
          <line
            key={`axis-${index}`}
            x1={line.x1}
            y1={line.y1}
            x2={line.x2}
            y2={line.y2}
            stroke={currentColors.grid}
            strokeWidth="1"
          />
        ))}

        {/* Data polygon */}
        <path
          d={polygonPath}
          fill={currentColors.fill}
          stroke={currentColors.stroke}
          strokeWidth="2"
          className={animated ? 'animate-fadeIn' : ''}
          style={{
            filter: 'drop-shadow(0 0 10px rgba(139, 92, 246, 0.5))',
          }}
        />

        {/* Data points */}
        {points.map((point, index) => (
          <g key={`point-${index}`}>
            <circle
              cx={point.x}
              cy={point.y}
              r="5"
              fill={currentColors.point}
              className={animated ? 'animate-pulse' : ''}
              style={{ animationDelay: `${index * 100}ms` }}
            />
            {/* Tooltip area */}
            <circle
              cx={point.x}
              cy={point.y}
              r="15"
              fill="transparent"
              className="cursor-pointer"
            >
              <title>{`${point.name}: ${(point.score * 100).toFixed(0)}%`}</title>
            </circle>
          </g>
        ))}

        {/* Labels */}
        {showLabels && points.map((point, index) => {
          const shortLabel = shortLabels[point.name] || point.name;
          const isRight = point.labelX > center;
          const isBottom = point.labelY > center;

          return (
            <text
              key={`label-${index}`}
              x={point.labelX}
              y={point.labelY}
              textAnchor={isRight ? 'start' : point.labelX === center ? 'middle' : 'end'}
              dominantBaseline={isBottom ? 'hanging' : point.labelY === center ? 'middle' : 'auto'}
              className="fill-gray-400 text-xs"
              style={{ fontSize: '10px' }}
            >
              {shortLabel}
            </text>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute -bottom-8 left-0 right-0 flex justify-center">
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>0%</span>
          <div className="w-24 h-1 bg-gradient-to-r from-gray-700 via-purple-500 to-purple-300 rounded" />
          <span>100%</span>
        </div>
      </div>
    </div>
  );
};

// Dimension breakdown list
export const TITANDimensionList: React.FC<{
  dimensions: TITANDimension[];
  compact?: boolean;
}> = ({ dimensions, compact = false }) => {
  const dimensionIcons: Record<string, string> = {
    SEMANTIC_DEPTH: '📚',
    EMOTIONAL_RESONANCE: '💖',
    TEMPORALITY: '⏳',
    SPATIAL_WORLD: '🌍',
    IMPLIED_CHARACTERS: '👥',
    CENTRAL_CONFLICT: '⚔️',
    NARRATIVE_PROMISE: '🎭',
    STYLE_TONE: '🎨',
    DEEP_PSYCHOLOGY: '🧠',
    INTERTEXTUALITY: '🔗',
    COMMERCIAL_POTENTIAL: '💰',
    TRANSCENDENCE: '✨',
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-blue-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getBarColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-blue-500';
    if (score >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className={`space-y-${compact ? '2' : '3'}`}>
      {dimensions.map((dim) => (
        <div key={dim.name} className="group">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span>{dimensionIcons[dim.name] || '📊'}</span>
              <span className={`text-gray-300 ${compact ? 'text-xs' : 'text-sm'}`}>
                {dim.name.replace(/_/g, ' ')}
              </span>
            </div>
            <span className={`font-bold ${compact ? 'text-sm' : ''} ${getScoreColor(dim.score)}`}>
              {(dim.score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`${getBarColor(dim.score)} h-2 rounded-full transition-all duration-500`}
              style={{ width: `${dim.score * 100}%` }}
            />
          </div>
          {!compact && dim.description && (
            <p className="text-xs text-gray-500 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {dim.description}
            </p>
          )}
        </div>
      ))}
    </div>
  );
};

// Summary card
export const TITANSummaryCard: React.FC<{
  dimensions: TITANDimension[];
  complexity: number;
  suggestedGenre?: string;
}> = ({ dimensions, complexity, suggestedGenre }) => {
  const avgScore = dimensions.length > 0
    ? dimensions.reduce((sum, d) => sum + d.score, 0) / dimensions.length
    : 0;

  const topDimensions = [...dimensions]
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  const weakDimensions = [...dimensions]
    .sort((a, b) => a.score - b.score)
    .slice(0, 2);

  return (
    <div className="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 rounded-xl p-6 border border-purple-500/30">
      <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <span>🎯</span>
        TITAN Analysis Summary
      </h4>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-800/50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-400">
            {(complexity * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500">Overall Complexity</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {(avgScore * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500">Average Score</div>
        </div>
      </div>

      {suggestedGenre && (
        <div className="mb-4 p-3 bg-indigo-600/20 rounded-lg border border-indigo-500/30">
          <span className="text-gray-400 text-sm">Suggested Genre: </span>
          <span className="text-white font-semibold">{suggestedGenre}</span>
        </div>
      )}

      <div className="space-y-3">
        <div>
          <div className="text-xs text-gray-500 mb-1">Strongest Dimensions</div>
          <div className="flex flex-wrap gap-2">
            {topDimensions.map(d => (
              <span
                key={d.name}
                className="px-2 py-1 bg-green-600/30 text-green-400 rounded text-xs"
              >
                {d.name.replace(/_/g, ' ')} ({(d.score * 100).toFixed(0)}%)
              </span>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 mb-1">Areas to Develop</div>
          <div className="flex flex-wrap gap-2">
            {weakDimensions.map(d => (
              <span
                key={d.name}
                className="px-2 py-1 bg-yellow-600/30 text-yellow-400 rounded text-xs"
              >
                {d.name.replace(/_/g, ' ')} ({(d.score * 100).toFixed(0)}%)
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TITANRadarChart;
