import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Genre {
  value: string;
  label: string;
  description: string;
  icon: string;
  gradient: string;
}

const genres: Genre[] = [
  {
    value: 'sci_fi',
    label: 'Sci-Fi',
    description: 'Eksploracja przyszłości, technologii i kosmosu',
    icon: '🚀',
    gradient: 'from-blue-500 to-cyan-500'
  },
  {
    value: 'fantasy',
    label: 'Fantasy',
    description: 'Magiczne światy pełne cudów i legend',
    icon: '⚔️',
    gradient: 'from-purple-500 to-pink-500'
  },
  {
    value: 'thriller',
    label: 'Thriller',
    description: 'Napięcie, akcja i nieoczekiwane zwroty akcji',
    icon: '🔥',
    gradient: 'from-red-500 to-orange-500'
  },
  {
    value: 'horror',
    label: 'Horror',
    description: 'Mroczne opowieści budzące lęk i dreszcz',
    icon: '👻',
    gradient: 'from-gray-700 to-gray-900'
  },
  {
    value: 'romance',
    label: 'Romans',
    description: 'Historie miłosne pełne emocji',
    icon: '💕',
    gradient: 'from-pink-400 to-rose-500'
  },
  {
    value: 'drama',
    label: 'Dramat',
    description: 'Głębokie relacje międzyludzkie i dylematy',
    icon: '🎭',
    gradient: 'from-indigo-500 to-purple-600'
  },
  {
    value: 'comedy',
    label: 'Komedia',
    description: 'Humor, radość i pozytywna energia',
    icon: '😄',
    gradient: 'from-yellow-400 to-orange-400'
  },
  {
    value: 'mystery',
    label: 'Kryminał',
    description: 'Tajemnice czekające na rozwiązanie',
    icon: '🔍',
    gradient: 'from-emerald-500 to-teal-600'
  }
];

const ProjectCreator: React.FC = () => {
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [projectTitle, setProjectTitle] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const navigate = useNavigate();

  const handleCreateProject = async () => {
    if (!selectedGenre || !projectTitle.trim()) {
      alert('Proszę wybrać gatunek i podać tytuł projektu');
      return;
    }

    setIsCreating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/projects', {
        title: projectTitle,
        genre: selectedGenre
      });

      const projectId = response.data.id;

      // Navigate to project view
      navigate(`/project/${projectId}`);
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Wystąpił błąd podczas tworzenia projektu');
      setIsCreating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Stwórz Nową Książkę</h2>
        <p className="text-gray-400">
          Wybierz gatunek literacki - AI zadecyduje o wszystkim innym
        </p>
      </div>

      {/* Project Title Input */}
      <div className="mb-8">
        <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-2">
          Tytuł Projektu
        </label>
        <input
          type="text"
          id="title"
          value={projectTitle}
          onChange={(e) => setProjectTitle(e.target.value)}
          placeholder="np. Moja Pierwsza Powieść"
          className="w-full max-w-xl px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Genre Selection */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-300 mb-4">
          Wybierz Gatunek Literacki
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {genres.map((genre) => (
            <button
              key={genre.value}
              onClick={() => setSelectedGenre(genre.value)}
              className={`relative p-6 rounded-xl transition-all duration-200 ${
                selectedGenre === genre.value
                  ? 'ring-4 ring-white scale-105'
                  : 'hover:scale-105'
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${genre.gradient} rounded-xl opacity-90`} />
              <div className="relative z-10">
                <div className="text-4xl mb-2">{genre.icon}</div>
                <h3 className="text-xl font-bold text-white mb-1">{genre.label}</h3>
                <p className="text-sm text-gray-100">{genre.description}</p>
              </div>
              {selectedGenre === genre.value && (
                <div className="absolute top-2 right-2 bg-white rounded-full p-1">
                  <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Create Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 text-gray-400 hover:text-white transition-colors"
        >
          ← Powrót
        </button>
        <button
          onClick={handleCreateProject}
          disabled={!selectedGenre || !projectTitle.trim() || isCreating}
          className={`px-8 py-3 rounded-lg font-semibold transition-all ${
            selectedGenre && projectTitle.trim() && !isCreating
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isCreating ? 'Tworzenie...' : 'Stwórz Projekt i Symuluj →'}
        </button>
      </div>
    </div>
  );
};

export default ProjectCreator;
