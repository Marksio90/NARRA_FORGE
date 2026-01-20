'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useWebSocket } from '@/hooks/useWebSocket';

interface Progress {
  phase: string;
  message: string;
  progress: number;
}

interface Cost {
  total: number;
  breakdown: Record<string, number>;
}

interface AgentState {
  agent: string;
  status: 'idle' | 'working' | 'completed' | 'repairing';
  message: string;
}

const phaseLabels: Record<string, string> = {
  concept: '🎨 Koncepcja',
  writing: '✍️ Pisanie',
  polishing: '✨ Szlify',
  publishing: '📚 Publikacja',
  saving: '💾 Zapis',
};

export default function GeneratePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [progress, setProgress] = useState<Progress>({ phase: '', message: '', progress: 0 });
  const [cost, setCost] = useState<Cost>({ total: 0, breakdown: {} });
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [chapters, setChapters] = useState<Array<{ num: number; preview: string }>>([]);
  const [isCompleted, setIsCompleted] = useState(false);

  // WebSocket connection
  const { lastMessage } = useWebSocket(`/ws/${id}`);

  useEffect(() => {
    if (!lastMessage) return;

    switch (lastMessage.type) {
      case 'progress':
        setProgress(lastMessage.data);
        break;
      case 'cost':
        setCost(lastMessage.data);
        break;
      case 'agent_status':
        setAgents((prev) => ({
          ...prev,
          [lastMessage.data.agent]: {
            agent: lastMessage.data.agent,
            status: lastMessage.data.status,
            message: lastMessage.data.details?.message || '',
          },
        }));
        break;
      case 'chapter_preview':
        setChapters((prev) => [
          ...prev,
          { num: lastMessage.data.chapter, preview: lastMessage.data.preview },
        ]);
        break;
      case 'completed':
        setIsCompleted(true);
        break;
    }
  }, [lastMessage]);

  const getPhaseOrder = (phase: string): number => {
    const order = ['concept', 'writing', 'polishing', 'publishing', 'saving'];
    return order.indexOf(phase);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      {/* Header */}
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-white">
          🔥 NarraForge
        </h1>
        <p className="text-slate-400 mt-2">
          {isCompleted ? '✅ Książka gotowa!' : 'Trwa generowanie...'}
        </p>
      </header>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Progress & Agents */}
        <div className="lg:col-span-2 space-y-6">
          {/* Main Progress Bar */}
          <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
            {/* Phase Label */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">
                {phaseLabels[progress.phase] || progress.phase}
              </h2>
              <span className="text-2xl font-bold text-amber-400">
                {Math.round(progress.progress)}%
              </span>
            </div>

            {/* Progress Bar */}
            <div className="h-4 bg-slate-700 rounded-full overflow-hidden mb-4">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-orange-600 transition-all duration-500 ease-out"
                style={{ width: `${progress.progress}%` }}
              />
            </div>

            {/* Message */}
            <p className="text-slate-400 text-sm">
              {progress.message}
            </p>

            {/* Phase Indicators */}
            <div className="flex justify-between mt-6">
              {Object.entries(phaseLabels).map(([key, label]) => {
                const isActive = progress.phase === key;
                const isPast = getPhaseOrder(progress.phase) > getPhaseOrder(key);

                return (
                  <div
                    key={key}
                    className={`flex flex-col items-center ${
                      isActive ? 'text-amber-400' : isPast ? 'text-green-400' : 'text-slate-600'
                    }`}
                  >
                    <div
                      className={`w-3 h-3 rounded-full mb-1 ${
                        isActive
                          ? 'bg-amber-400 animate-pulse'
                          : isPast
                          ? 'bg-green-400'
                          : 'bg-slate-600'
                      }`}
                    />
                    <span className="text-xs">{label.split(' ')[0]}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Agent Status Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { key: 'world', name: '🌍 Architekt Świata' },
              { key: 'character', name: '👥 Kreator Dusz' },
              { key: 'plot', name: '📖 Mistrz Fabuły' },
              { key: 'prose', name: '✍️ Mistrz Słowa' },
              { key: 'consistency', name: '🔗 Strażnik' },
              { key: 'director', name: '🎬 Reżyser' },
            ].map((agent) => {
              const state = agents[agent.key];
              const statusColor = state?.status === 'completed' ? 'green' :
                                 state?.status === 'working' ? 'amber' :
                                 state?.status === 'repairing' ? 'red' : 'slate';

              return (
                <div
                  key={agent.key}
                  className="bg-slate-800/50 rounded-xl p-4 border border-slate-700"
                >
                  <div className="text-center">
                    <div className={`text-2xl mb-2 ${state?.status === 'working' ? 'animate-bounce' : ''}`}>
                      {agent.name.split(' ')[0]}
                    </div>
                    <div className="text-xs font-semibold text-slate-400">
                      {agent.name.split(' ').slice(1).join(' ')}
                    </div>
                    <div className={`mt-2 w-2 h-2 rounded-full mx-auto bg-${statusColor}-400`} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Chapter Previews */}
          {chapters.length > 0 && (
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">
                📚 Podgląd rozdziałów
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {chapters.map((chapter) => (
                  <div
                    key={chapter.num}
                    className="bg-slate-900/50 rounded-lg p-4 border border-slate-700"
                  >
                    <div className="text-sm font-semibold text-amber-400 mb-2">
                      Rozdział {chapter.num}
                    </div>
                    <div className="text-sm text-slate-400 line-clamp-3">
                      {chapter.preview}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Cost Tracker */}
        <div>
          <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
            {/* Total Cost */}
            <div className="text-center mb-6">
              <p className="text-slate-400 text-sm mb-1">Całkowity koszt</p>
              <p className="text-4xl font-bold text-white">
                ${cost.total.toFixed(4)}
              </p>
            </div>

            {/* Breakdown */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
                Podział kosztów
              </h3>

              {Object.entries(cost.breakdown).map(([key, value]) => {
                const maxCost = Math.max(...Object.values(cost.breakdown), 0.01);
                const percentage = (value / maxCost) * 100;

                return (
                  <div key={key}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-slate-300">{key}</span>
                      <span className="text-slate-400">${value.toFixed(4)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Completion Modal */}
      {isCompleted && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl p-8 max-w-md text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Książka gotowa!
            </h2>
            <p className="text-slate-400 mb-6">
              Twój bestseller czeka na Ciebie.
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => router.push(`/book/${id}`)}
                className="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 rounded-full text-white font-semibold hover:from-amber-400 hover:to-orange-500 transition"
              >
                📖 Zobacz książkę
              </button>
              <button
                onClick={() => router.push('/')}
                className="px-6 py-3 bg-slate-700 rounded-full text-white font-semibold hover:bg-slate-600 transition"
              >
                🏠 Strona główna
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
