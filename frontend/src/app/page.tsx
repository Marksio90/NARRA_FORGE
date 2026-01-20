'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const genres = [
  { id: 'scifi', name: 'Science Fiction', icon: '🚀', color: 'from-blue-500 to-purple-600' },
  { id: 'fantasy', name: 'Fantasy', icon: '🐉', color: 'from-purple-500 to-pink-600' },
  { id: 'thriller', name: 'Thriller', icon: '🔪', color: 'from-red-500 to-orange-600' },
  { id: 'horror', name: 'Horror', icon: '👻', color: 'from-gray-700 to-red-900' },
  { id: 'romance', name: 'Romans', icon: '💕', color: 'from-pink-400 to-red-500' },
  { id: 'mystery', name: 'Kryminał', icon: '🔍', color: 'from-amber-600 to-yellow-500' },
  { id: 'drama', name: 'Dramat', icon: '🎭', color: 'from-indigo-500 to-blue-600' },
  { id: 'comedy', name: 'Komedia', icon: '😂', color: 'from-yellow-400 to-green-500' },
  { id: 'dystopia', name: 'Dystopia', icon: '🏚️', color: 'from-slate-600 to-zinc-800' },
  { id: 'historical', name: 'Historyczna', icon: '⚔️', color: 'from-amber-700 to-stone-600' },
];

export default function HomePage() {
  const router = useRouter();
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  const handleStart = async () => {
    if (!selectedGenre) return;

    setIsStarting(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/books/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ genre: selectedGenre }),
      });

      const book = await response.json();
      router.push(`/generate/${book.id}`);
    } catch (error) {
      console.error('Failed to start generation:', error);
      setIsStarting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="pt-12 pb-8 text-center">
        <h1 className="text-6xl font-bold bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
          🔥 NarraForge
        </h1>
        <p className="mt-4 text-xl text-slate-400">
          Kuźnia Bestsellerów AI
        </p>
      </header>

      {/* Genre Selection */}
      <main className="max-w-6xl mx-auto px-6 pb-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-semibold text-white mb-4">
            Wybierz gatunek
          </h2>
          <p className="text-slate-400">
            To jedyna decyzja, którą musisz podjąć. Resztę zostawę mi.
          </p>
        </div>

        {/* Genre Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-12">
          {genres.map((genre) => (
            <button
              key={genre.id}
              onClick={() => setSelectedGenre(genre.id)}
              className={`
                p-6 rounded-2xl transition-all duration-300 transform hover:scale-105
                ${selectedGenre === genre.id
                  ? `bg-gradient-to-br ${genre.color} shadow-lg shadow-${genre.color.split('-')[1]}-500/30 scale-105`
                  : 'bg-slate-800/50 hover:bg-slate-700/50'
                }
                border ${selectedGenre === genre.id ? 'border-transparent' : 'border-slate-700'}
              `}
            >
              <div className="text-4xl mb-2">{genre.icon}</div>
              <div className="text-sm font-semibold text-white">{genre.name}</div>
            </button>
          ))}
        </div>

        {/* Start Button */}
        {selectedGenre && (
          <div className="text-center">
            <button
              onClick={handleStart}
              disabled={isStarting}
              className={`
                px-12 py-4 text-xl font-bold rounded-full
                bg-gradient-to-r from-amber-500 to-orange-600
                hover:from-amber-400 hover:to-orange-500
                transform hover:scale-105 transition-all duration-300
                shadow-lg shadow-orange-500/30
                disabled:opacity-50 disabled:cursor-not-allowed
                text-white
              `}
            >
              {isStarting ? (
                <span className="flex items-center gap-3">
                  <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Rozpoczynam...
                </span>
              ) : (
                '🔥 Rozpal Kuźnię'
              )}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
