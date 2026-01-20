import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

interface SimulationStep {
  step: number;
  name: string;
  description: string;
  estimated_tokens: number;
  estimated_cost: number;
  model_tier: number;
}

interface AIDecisions {
  target_word_count: number;
  chapter_count: number;
  main_character_count: number;
  subplot_count: number;
  world_detail_level: string;
  style_complexity: string;
}

interface Simulation {
  estimated_total_cost: number;
  estimated_duration_minutes: number;
  ai_decisions: AIDecisions;
  estimated_steps: SimulationStep[];
}

interface Project {
  id: number;
  name: string;
  genre: string;
  status: string;
  created_at: string;
  parameters: AIDecisions;
  estimated_cost: number;
  actual_cost: number;
  current_step: number;
  progress_percentage: number;
  current_activity?: string;
}

const ProjectView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    fetchProject();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/projects/${id}`);
      setProject(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching project:', error);
      setLoading(false);
    }
  };

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const response = await axios.post(`http://localhost:8000/api/projects/${id}/simulate`);
      setSimulation(response.data);
      // Refresh project to get updated status
      await fetchProject();
    } catch (error) {
      console.error('Error simulating:', error);
      alert('Wystąpił błąd podczas symulacji');
    }
    setIsSimulating(false);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await axios.post(`http://localhost:8000/api/projects/${id}/start`);
      // Start polling for updates
      const interval = setInterval(async () => {
        const response = await axios.get(`http://localhost:8000/api/projects/${id}`);
        setProject(response.data);
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval);
          setIsGenerating(false);
        }
      }, 3000);
    } catch (error) {
      console.error('Error generating:', error);
      alert('Wystąpił błąd podczas generowania');
      setIsGenerating(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/projects/${id}/export/${format}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project?.title}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting:', error);
      alert('Wystąpił błąd podczas eksportu');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-white text-center">Ładowanie...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-white text-center">Projekt nie znaleziony</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="text-gray-400 hover:text-white mb-4 flex items-center"
        >
          ← Powrót do Dashboard
        </button>
        <h2 className="text-3xl font-bold text-white mb-2">{project.title}</h2>
        <div className="flex items-center gap-4">
          <span className="px-3 py-1 bg-indigo-600 text-white rounded-full text-sm">
            {project.genre}
          </span>
          <span className={`px-3 py-1 rounded-full text-sm ${
            project.status === 'completed' ? 'bg-green-600 text-white' :
            project.status === 'generating' ? 'bg-yellow-600 text-white' :
            project.status === 'failed' ? 'bg-red-600 text-white' :
            'bg-gray-600 text-white'
          }`}>
            {project.status}
          </span>
        </div>
      </div>

      {/* Simulation Section */}
      {!simulation && project.status === 'initializing' && (
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">
            Symulacja Inteligentna
          </h3>
          <p className="text-gray-400 mb-6">
            AI przeanalizuje wybrany gatunek i podejmie wszystkie decyzje dotyczące struktury książki,
            następnie przedstawi szczegółową symulację kosztów dla wszystkich 15 kroków procesu generacji.
          </p>
          <button
            onClick={handleSimulate}
            disabled={isSimulating}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50"
          >
            {isSimulating ? 'Symulowanie...' : 'Uruchom Symulację AI'}
          </button>
        </div>
      )}

      {/* AI Decisions */}
      {simulation && (
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-6">
            Decyzje AI dla Gatunku: {project.genre}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Docelowa Liczba Słów</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.target_word_count.toLocaleString()}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Liczba Rozdziałów</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.chapter_count}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Główni Bohaterowie</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.main_character_count}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Wątki Poboczne</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.subplot_count}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Poziom Detali Świata</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.world_detail_level}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Złożoność Stylu</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.style_complexity}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cost Summary */}
      {project.simulation && (
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">
            Szacowany Koszt i Czas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-gray-200 text-sm mb-1">Całkowity Szacowany Koszt</div>
              <div className="text-4xl font-bold text-white">
                ${simulation.estimated_total_cost.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-gray-200 text-sm mb-1">Szacowany Czas Generacji</div>
              <div className="text-4xl font-bold text-white">
                {simulation.estimated_duration_minutes} min
              </div>
            </div>
          </div>
          {project.status === 'simulating' && (
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="mt-6 px-8 py-3 bg-white text-indigo-700 rounded-lg font-semibold hover:bg-gray-100 disabled:opacity-50"
            >
              {isGenerating ? 'Generowanie...' : 'Zatwierdź i Rozpocznij Generację'}
            </button>
          )}
        </div>
      )}

      {/* Pipeline Steps */}
      {project.simulation && (
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-6">
            15 Kroków Pipeline - Szczegółowa Symulacja
          </h3>
          <div className="space-y-4">
            {simulation.estimated_steps.map((step) => (
              <div
                key={step.step}
                className={`bg-gray-700 rounded-lg p-4 ${
                  project.current_step && step.step === project.current_step
                    ? 'ring-2 ring-yellow-500'
                    : project.current_step && step.step < project.current_step
                    ? 'opacity-60'
                    : ''
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-indigo-400 font-bold">Krok {step.step}</span>
                    <span className="text-white font-semibold">{step.name}</span>
                    <span className="px-2 py-1 bg-gray-600 text-gray-300 rounded text-xs">
                      Tier {step.model_tier}
                    </span>
                  </div>
                  <div className="text-green-400 font-semibold">
                    ${step.estimated_cost.toFixed(4)}
                  </div>
                </div>
                <p className="text-gray-400 text-sm mb-2">{step.description}</p>
                <div className="text-gray-500 text-xs">
                  Szacowane tokeny: {step.estimated_tokens.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {project.status === 'generating' && project.current_step && (
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">Postęp Generacji</h3>
          <div className="w-full bg-gray-700 rounded-full h-4 mb-2">
            <div
              className="bg-gradient-to-r from-indigo-600 to-purple-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${(project.current_step / 15) * 100}%` }}
            />
          </div>
          <div className="text-gray-400 text-sm">
            Krok {project.current_step} z 15 • Aktualny koszt: ${project.total_cost?.toFixed(2) || '0.00'}
          </div>
        </div>
      )}

      {/* Export Options */}
      {project.status === 'completed' && (
        <div className="bg-gray-800 rounded-lg p-8">
          <h3 className="text-xl font-bold text-white mb-4">Eksport Książki</h3>
          <div className="flex gap-4">
            <button
              onClick={() => handleExport('docx')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            >
              Pobierz DOCX
            </button>
            <button
              onClick={() => handleExport('epub')}
              className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
            >
              Pobierz EPUB
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700"
            >
              Pobierz PDF
            </button>
            <button
              onClick={() => handleExport('md')}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700"
            >
              Pobierz Markdown
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectView;
