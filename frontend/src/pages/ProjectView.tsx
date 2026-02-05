import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';

interface SimulationStep {
  step: number;
  name: string;
  description: string;
  estimated_tokens: number;
  estimated_cost: number;
  model_tier: number;
}

interface CharacterName {
  name: string;
  role: string;
  gender: string;
}

interface CulturalAnalysis {
  mythological_references?: string[];
  cultural_context?: string;
  symbolic_elements?: string[];
  archetypal_patterns?: string[];
}

interface MagicSystem {
  magic_type?: string;
  power_source?: string;
  limitations?: string;
  cost?: string;
  scope?: string;
}

interface SettingAnalysis {
  environment?: string;
  time_period?: string;
  emotional_landscape?: string;
  setting_role?: string;
  protagonist_relationship?: string;
}

interface ToneAndMaturity {
  tone?: string;
  maturity_level?: string;
  violence_level?: string;
  moral_complexity?: string;
  emotional_intensity?: string;
}

interface AntagonistPrediction {
  type?: string;
  motivation?: string;
  opposition_nature?: string;
}

interface Conflicts {
  external?: string | { description?: string; stakes?: string };
  internal?: string | { description?: string; false_belief?: string };
  philosophical?: string | { question?: string; both_sides?: string };
  moral?: string | { dilemma?: string; cost?: string };
  relational?: string | { description?: string; source?: string };
}

interface Subgenre {
  primary?: string;
  secondary?: string[];
  magic_level?: string;
  focus?: string;
}

interface ReaderExpectations {
  expected_scenes?: string[];
  emotional_journey?: string;
  tropes?: string[];
}

interface PacingSuggestions {
  overall_pace?: string;
  structure_type?: string;
  darkest_act?: string;
  tension_curve?: string;
}

interface SecondaryPlot {
  type?: string;
  description?: string;
  key_characters?: string[];
}

interface CharacterArc {
  starting_point?: string;
  midpoint_shift?: string;
  climax_challenge?: string;
  transformation?: string;
  arc_type?: string;
}

interface BackstorySignals {
  detected_hints?: string[];
  implied_trauma?: string;
  emotional_weight?: string;
  hidden_conflicts?: string[];
  secrets_implied?: string[];
}

interface BestsellerHook {
  emotional_hook?: string;
  intrigue_promise?: string;
  built_in_tension?: string;
  uniqueness?: string;
}

interface UniversalThemes {
  primary_theme?: string;
  secondary_themes?: string[];
  existential_question?: string;
  emotional_truth?: string;
}

interface TitleAnalysis {
  character_names: CharacterName[];
  themes: string[];
  setting_hints: string[];
  tone: string;
  focus: string;
  // New advanced analysis fields
  cultural_analysis?: CulturalAnalysis;
  magic_system?: MagicSystem;
  setting_analysis?: SettingAnalysis;
  tone_and_maturity?: ToneAndMaturity;
  antagonist_predictions?: AntagonistPrediction[];
  conflicts?: Conflicts;
  subgenre?: Subgenre;
  reader_expectations?: ReaderExpectations;
  pacing_suggestions?: PacingSuggestions;
  secondary_plots?: SecondaryPlot[];
  character_arc?: CharacterArc;
  // Bestseller-level analysis fields
  backstory_signals?: BackstorySignals;
  bestseller_hook?: BestsellerHook;
  universal_themes?: UniversalThemes;
}

interface AIDecisions {
  target_word_count: number;
  chapter_count: number;
  main_character_count: number;
  subplot_count: number;
  world_detail_level: string;
  style_complexity: string;
  title_analysis?: TitleAnalysis;
  title_suggestions?: {
    main_character_name?: string;
    main_character_gender?: string;
    add_subplots?: string[];
    world_setting?: string;
  };
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
  simulation_data?: Simulation | null;
  estimated_duration_minutes?: number;
}

const ProjectView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchProject();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, []);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/projects/${id}`);
      console.log('🔍 DEBUG: Received project:', response.data);
      console.log('🔍 DEBUG: Project status:', response.data.status);
      console.log('🔍 DEBUG: Simulation data from DB:', response.data.simulation_data);

      setProject(response.data);

      // If project has simulation_data persisted, load it into state
      if (response.data.simulation_data && !simulation) {
        console.log('📊 Loading persisted simulation data');
        setSimulation(response.data.simulation_data);
      }

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
      toast.success('Symulacja zakończona pomyślnie!');
      // Refresh project to get updated status
      await fetchProject();
    } catch (error) {
      console.error('Error simulating:', error);
      toast.error('Wystąpił błąd podczas symulacji');
    }
    setIsSimulating(false);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await axios.post(`http://localhost:8000/api/projects/${id}/start`);
      toast.info('Generowanie rozpoczęte...');

      // Clear any existing polling interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      // Start polling for updates
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/api/projects/${id}`);
          setProject(response.data);
          if (response.data.status === 'completed' || response.data.status === 'failed') {
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
            setIsGenerating(false);

            // Show appropriate toast
            if (response.data.status === 'completed') {
              toast.success('Generowanie zakończone pomyślnie!');
            } else {
              toast.error('Generowanie nie powiodło się');
            }
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 3000);
    } catch (error) {
      console.error('Error generating:', error);
      toast.error('Wystąpił błąd podczas generowania');
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
      link.setAttribute('download', `${project?.name}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting:', error);
      toast.error('Wystąpił błąd podczas eksportu');
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
        <h2 className="text-3xl font-bold text-white mb-2">{project.name}</h2>
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

      {/* Title Analysis Section */}
      {simulation && simulation.ai_decisions.title_analysis && (
        <div className="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-lg p-8 mb-8 border border-purple-500">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>🎯</span> Analiza Tytułu: "{project.name}"
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Character Names */}
            {simulation.ai_decisions.title_analysis.character_names &&
             simulation.ai_decisions.title_analysis.character_names.length > 0 && (
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-purple-300 font-semibold mb-2">Postacie z Tytułu</div>
                {simulation.ai_decisions.title_analysis.character_names.map((char, idx) => (
                  <div key={idx} className="text-white mb-1">
                    <span className="font-bold">{char.name}</span>
                    <span className="text-gray-400 text-sm ml-2">
                      ({char.role}, {char.gender})
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Themes */}
            {simulation.ai_decisions.title_analysis.themes &&
             simulation.ai_decisions.title_analysis.themes.length > 0 && (
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-purple-300 font-semibold mb-2">Wykryte Tematy</div>
                <div className="flex flex-wrap gap-2">
                  {simulation.ai_decisions.title_analysis.themes.map((theme, idx) => (
                    <span key={idx} className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm">
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Setting Hints */}
            {simulation.ai_decisions.title_analysis.setting_hints &&
             simulation.ai_decisions.title_analysis.setting_hints.length > 0 && (
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-purple-300 font-semibold mb-2">Sugestie Miejsca Akcji</div>
                <div className="flex flex-wrap gap-2">
                  {simulation.ai_decisions.title_analysis.setting_hints.map((hint, idx) => (
                    <span key={idx} className="px-3 py-1 bg-indigo-600 text-white rounded-full text-sm">
                      {hint}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Tone and Focus */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <div className="text-purple-300 font-semibold mb-2">Ton i Fokus</div>
              <div className="text-white">
                <div>Ton: <span className="text-purple-400">{simulation.ai_decisions.title_analysis.tone}</span></div>
                <div>Fokus: <span className="text-purple-400">{simulation.ai_decisions.title_analysis.focus}</span></div>
              </div>
            </div>
          </div>

          {/* ADVANCED ANALYSIS - Multi-dimensional Analysis */}
          <div className="mt-6 pt-6 border-t border-purple-700">
            <h4 className="text-lg font-bold text-white mb-4">🔮 Zaawansowana Analiza (13-Wymiarowa)</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Cultural/Mythological Depth */}
              {simulation.ai_decisions.title_analysis.cultural_analysis && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">🏛️ Głębia Kulturowa/Mitologiczna</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.cultural_analysis.cultural_context && (
                      <div><span className="text-gray-400">Kontekst:</span> {simulation.ai_decisions.title_analysis.cultural_analysis.cultural_context}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.cultural_analysis.mythological_references && simulation.ai_decisions.title_analysis.cultural_analysis.mythological_references.length > 0 && (
                      <div><span className="text-gray-400">Mitologia:</span> {simulation.ai_decisions.title_analysis.cultural_analysis.mythological_references.join(', ')}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.cultural_analysis.archetypal_patterns && simulation.ai_decisions.title_analysis.cultural_analysis.archetypal_patterns.length > 0 && (
                      <div><span className="text-gray-400">Archetypy:</span> {simulation.ai_decisions.title_analysis.cultural_analysis.archetypal_patterns.join(', ')}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Bestseller Hook */}
              {simulation.ai_decisions.title_analysis.bestseller_hook && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">🎯 Hook Bestsellerowy</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.bestseller_hook.emotional_hook && (
                      <div><span className="text-gray-400">Hook emocjonalny:</span> {simulation.ai_decisions.title_analysis.bestseller_hook.emotional_hook}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.bestseller_hook.intrigue_promise && (
                      <div><span className="text-gray-400">Obietnica intrygi:</span> {simulation.ai_decisions.title_analysis.bestseller_hook.intrigue_promise}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.bestseller_hook.built_in_tension && (
                      <div><span className="text-gray-400">Wbudowane napięcie:</span> {simulation.ai_decisions.title_analysis.bestseller_hook.built_in_tension}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.bestseller_hook.uniqueness && (
                      <div><span className="text-gray-400">Unikalność:</span> {simulation.ai_decisions.title_analysis.bestseller_hook.uniqueness}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Backstory Signals */}
              {simulation.ai_decisions.title_analysis.backstory_signals && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">💔 Sygnały Traumy/Backstory</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.backstory_signals.implied_trauma && (
                      <div><span className="text-gray-400">Domniemana trauma:</span> {simulation.ai_decisions.title_analysis.backstory_signals.implied_trauma}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.backstory_signals.emotional_weight && (
                      <div><span className="text-gray-400">Ciężar emocjonalny:</span> {simulation.ai_decisions.title_analysis.backstory_signals.emotional_weight}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.backstory_signals.detected_hints && simulation.ai_decisions.title_analysis.backstory_signals.detected_hints.length > 0 && (
                      <div><span className="text-gray-400">Wykryte sygnały:</span> {simulation.ai_decisions.title_analysis.backstory_signals.detected_hints.join(', ')}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.backstory_signals.hidden_conflicts && simulation.ai_decisions.title_analysis.backstory_signals.hidden_conflicts.length > 0 && (
                      <div><span className="text-gray-400">Ukryte konflikty:</span> {simulation.ai_decisions.title_analysis.backstory_signals.hidden_conflicts.join(', ')}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Universal Themes */}
              {simulation.ai_decisions.title_analysis.universal_themes && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">🌟 Uniwersalne Tematy</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.universal_themes.primary_theme && (
                      <div><span className="text-gray-400">Główny temat:</span> {simulation.ai_decisions.title_analysis.universal_themes.primary_theme}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.universal_themes.secondary_themes && simulation.ai_decisions.title_analysis.universal_themes.secondary_themes.length > 0 && (
                      <div><span className="text-gray-400">Tematy poboczne:</span> {simulation.ai_decisions.title_analysis.universal_themes.secondary_themes.join(', ')}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.universal_themes.existential_question && (
                      <div><span className="text-gray-400">Pytanie egzystencjalne:</span> {simulation.ai_decisions.title_analysis.universal_themes.existential_question}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.universal_themes.emotional_truth && (
                      <div><span className="text-gray-400">Prawda emocjonalna:</span> {simulation.ai_decisions.title_analysis.universal_themes.emotional_truth}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Magic System Analysis */}
              {simulation.ai_decisions.title_analysis.magic_system && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">✨ Analiza Systemu Magii</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.magic_system.magic_type && (
                      <div><span className="text-gray-400">Typ:</span> {simulation.ai_decisions.title_analysis.magic_system.magic_type}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.magic_system.power_source && (
                      <div><span className="text-gray-400">Źródło mocy:</span> {simulation.ai_decisions.title_analysis.magic_system.power_source}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.magic_system.limitations && (
                      <div><span className="text-gray-400">Ograniczenia:</span> {simulation.ai_decisions.title_analysis.magic_system.limitations}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.magic_system.scope && (
                      <div><span className="text-gray-400">Zasięg:</span> {simulation.ai_decisions.title_analysis.magic_system.scope}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Deep Setting Analysis */}
              {simulation.ai_decisions.title_analysis.setting_analysis && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">🌍 Głęboka Analiza Świata</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.setting_analysis.environment && (
                      <div><span className="text-gray-400">Środowisko:</span> {simulation.ai_decisions.title_analysis.setting_analysis.environment}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.setting_analysis.time_period && (
                      <div><span className="text-gray-400">Okres czasu:</span> {simulation.ai_decisions.title_analysis.setting_analysis.time_period}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.setting_analysis.emotional_landscape && (
                      <div><span className="text-gray-400">Klimat emocjonalny:</span> {simulation.ai_decisions.title_analysis.setting_analysis.emotional_landscape}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.setting_analysis.setting_role && (
                      <div><span className="text-gray-400">Rola świata:</span> {simulation.ai_decisions.title_analysis.setting_analysis.setting_role}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Tone & Maturity */}
              {simulation.ai_decisions.title_analysis.tone_and_maturity && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">🎭 Ton i Dojrzałość</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.tone_and_maturity.maturity_level && (
                      <div><span className="text-gray-400">Poziom dojrzałości:</span> {simulation.ai_decisions.title_analysis.tone_and_maturity.maturity_level}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.tone_and_maturity.violence_level && (
                      <div><span className="text-gray-400">Poziom przemocy:</span> {simulation.ai_decisions.title_analysis.tone_and_maturity.violence_level}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.tone_and_maturity.moral_complexity && (
                      <div><span className="text-gray-400">Złożoność moralna:</span> {simulation.ai_decisions.title_analysis.tone_and_maturity.moral_complexity}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.tone_and_maturity.emotional_intensity && (
                      <div><span className="text-gray-400">Intensywność emocjonalna:</span> {simulation.ai_decisions.title_analysis.tone_and_maturity.emotional_intensity}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Antagonist Predictions */}
              {simulation.ai_decisions.title_analysis.antagonist_predictions && simulation.ai_decisions.title_analysis.antagonist_predictions.length > 0 && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">⚔️ Predykcje Antagonisty</div>
                  <div className="text-white text-sm space-y-2">
                    {simulation.ai_decisions.title_analysis.antagonist_predictions.map((ant, idx) => (
                      <div key={idx} className="border-l-2 border-purple-500 pl-2">
                        {ant.type && <div><span className="text-gray-400">Typ:</span> {ant.type}</div>}
                        {ant.motivation && <div><span className="text-gray-400">Motywacja:</span> {ant.motivation}</div>}
                        {ant.opposition_nature && <div><span className="text-gray-400">Natura opozycji:</span> {ant.opposition_nature}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Multi-layered Conflicts */}
              {simulation.ai_decisions.title_analysis.conflicts && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">💥 Wielowarstwowe Konflikty</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.conflicts.external && (
                      <div>
                        <span className="text-gray-400">Zewnętrzny:</span>{' '}
                        {typeof simulation.ai_decisions.title_analysis.conflicts.external === 'string'
                          ? simulation.ai_decisions.title_analysis.conflicts.external
                          : `${simulation.ai_decisions.title_analysis.conflicts.external.description || ''}${simulation.ai_decisions.title_analysis.conflicts.external.stakes ? ` (Stawka: ${simulation.ai_decisions.title_analysis.conflicts.external.stakes})` : ''}`}
                      </div>
                    )}
                    {simulation.ai_decisions.title_analysis.conflicts.internal && (
                      <div>
                        <span className="text-gray-400">Wewnętrzny:</span>{' '}
                        {typeof simulation.ai_decisions.title_analysis.conflicts.internal === 'string'
                          ? simulation.ai_decisions.title_analysis.conflicts.internal
                          : `${simulation.ai_decisions.title_analysis.conflicts.internal.description || ''}${simulation.ai_decisions.title_analysis.conflicts.internal.false_belief ? ` (Kłamstwo: ${simulation.ai_decisions.title_analysis.conflicts.internal.false_belief})` : ''}`}
                      </div>
                    )}
                    {simulation.ai_decisions.title_analysis.conflicts.relational && (
                      <div>
                        <span className="text-gray-400">Relacyjny:</span>{' '}
                        {typeof simulation.ai_decisions.title_analysis.conflicts.relational === 'string'
                          ? simulation.ai_decisions.title_analysis.conflicts.relational
                          : `${simulation.ai_decisions.title_analysis.conflicts.relational.description || ''}${simulation.ai_decisions.title_analysis.conflicts.relational.source ? ` (Źródło: ${simulation.ai_decisions.title_analysis.conflicts.relational.source})` : ''}`}
                      </div>
                    )}
                    {simulation.ai_decisions.title_analysis.conflicts.philosophical && (
                      <div>
                        <span className="text-gray-400">Filozoficzny:</span>{' '}
                        {typeof simulation.ai_decisions.title_analysis.conflicts.philosophical === 'string'
                          ? simulation.ai_decisions.title_analysis.conflicts.philosophical
                          : `${simulation.ai_decisions.title_analysis.conflicts.philosophical.question || ''}${simulation.ai_decisions.title_analysis.conflicts.philosophical.both_sides ? ` (${simulation.ai_decisions.title_analysis.conflicts.philosophical.both_sides})` : ''}`}
                      </div>
                    )}
                    {simulation.ai_decisions.title_analysis.conflicts.moral && (
                      <div>
                        <span className="text-gray-400">Moralny:</span>{' '}
                        {typeof simulation.ai_decisions.title_analysis.conflicts.moral === 'string'
                          ? simulation.ai_decisions.title_analysis.conflicts.moral
                          : `${simulation.ai_decisions.title_analysis.conflicts.moral.dilemma || ''}${simulation.ai_decisions.title_analysis.conflicts.moral.cost ? ` (Koszt: ${simulation.ai_decisions.title_analysis.conflicts.moral.cost})` : ''}`}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Subgenre Detection */}
              {simulation.ai_decisions.title_analysis.subgenre && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">📚 Detekcja Podgatunku</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.subgenre.primary && (
                      <div><span className="text-gray-400">Główny:</span> {simulation.ai_decisions.title_analysis.subgenre.primary}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.subgenre.secondary && simulation.ai_decisions.title_analysis.subgenre.secondary.length > 0 && (
                      <div><span className="text-gray-400">Drugorzędne:</span> {simulation.ai_decisions.title_analysis.subgenre.secondary.join(', ')}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.subgenre.magic_level && (
                      <div><span className="text-gray-400">Poziom magii:</span> {simulation.ai_decisions.title_analysis.subgenre.magic_level}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.subgenre.focus && (
                      <div><span className="text-gray-400">Fokus:</span> {simulation.ai_decisions.title_analysis.subgenre.focus}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Pacing Suggestions */}
              {simulation.ai_decisions.title_analysis.pacing_suggestions && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">⏱️ Sugestie Tempa</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.pacing_suggestions.overall_pace && (
                      <div><span className="text-gray-400">Ogólne tempo:</span> {simulation.ai_decisions.title_analysis.pacing_suggestions.overall_pace}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.pacing_suggestions.structure_type && (
                      <div><span className="text-gray-400">Struktura:</span> {simulation.ai_decisions.title_analysis.pacing_suggestions.structure_type}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.pacing_suggestions.darkest_act && (
                      <div><span className="text-gray-400">Najciemniejszy akt:</span> {simulation.ai_decisions.title_analysis.pacing_suggestions.darkest_act}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.pacing_suggestions.tension_curve && (
                      <div><span className="text-gray-400">Krzywa napięcia:</span> {simulation.ai_decisions.title_analysis.pacing_suggestions.tension_curve}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Secondary Plot Threads */}
              {simulation.ai_decisions.title_analysis.secondary_plots && simulation.ai_decisions.title_analysis.secondary_plots.length > 0 && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-purple-300 font-semibold mb-2">🧵 Wątki Poboczne</div>
                  <div className="text-white text-sm space-y-2">
                    {simulation.ai_decisions.title_analysis.secondary_plots.map((plot, idx) => (
                      <div key={idx} className="border-l-2 border-purple-500 pl-2">
                        {plot.type && <div><span className="text-gray-400">Typ:</span> {plot.type}</div>}
                        {plot.description && <div><span className="text-gray-400">Opis:</span> {plot.description}</div>}
                        {plot.key_characters && plot.key_characters.length > 0 && (
                          <div><span className="text-gray-400">Kluczowe postacie:</span> {plot.key_characters.join(', ')}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Character Arc Predictions */}
              {simulation.ai_decisions.title_analysis.character_arc && (
                <div className="bg-gray-800/50 rounded-lg p-4 md:col-span-2">
                  <div className="text-purple-300 font-semibold mb-2">🎬 Predykcje Łuku Postaci</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.character_arc.starting_point && (
                      <div><span className="text-gray-400">Punkt startowy:</span> {simulation.ai_decisions.title_analysis.character_arc.starting_point}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.character_arc.midpoint_shift && (
                      <div><span className="text-gray-400">Zmiana w połowie:</span> {simulation.ai_decisions.title_analysis.character_arc.midpoint_shift}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.character_arc.climax_challenge && (
                      <div><span className="text-gray-400">Wyzwanie w klimaksie:</span> {simulation.ai_decisions.title_analysis.character_arc.climax_challenge}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.character_arc.transformation && (
                      <div><span className="text-gray-400">Transformacja:</span> {simulation.ai_decisions.title_analysis.character_arc.transformation}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.character_arc.arc_type && (
                      <div><span className="text-gray-400">Typ łuku:</span> {simulation.ai_decisions.title_analysis.character_arc.arc_type}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Reader Expectations */}
              {simulation.ai_decisions.title_analysis.reader_expectations && (
                <div className="bg-gray-800/50 rounded-lg p-4 md:col-span-2">
                  <div className="text-purple-300 font-semibold mb-2">📖 Oczekiwania Czytelnika</div>
                  <div className="text-white text-sm space-y-1">
                    {simulation.ai_decisions.title_analysis.reader_expectations.emotional_journey && (
                      <div><span className="text-gray-400">Emocjonalna podróż:</span> {simulation.ai_decisions.title_analysis.reader_expectations.emotional_journey}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.reader_expectations.expected_scenes && simulation.ai_decisions.title_analysis.reader_expectations.expected_scenes.length > 0 && (
                      <div><span className="text-gray-400">Oczekiwane sceny:</span> {simulation.ai_decisions.title_analysis.reader_expectations.expected_scenes.join(', ')}</div>
                    )}
                    {simulation.ai_decisions.title_analysis.reader_expectations.tropes && simulation.ai_decisions.title_analysis.reader_expectations.tropes.length > 0 && (
                      <div><span className="text-gray-400">Tropy:</span> {simulation.ai_decisions.title_analysis.reader_expectations.tropes.join(', ')}</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Title Suggestions */}
          {simulation.ai_decisions.title_suggestions && (
            <div className="mt-4 pt-4 border-t border-purple-700">
              <div className="text-purple-300 font-semibold mb-2">Sugestie AI na Podstawie Tytułu</div>
              <div className="text-white text-sm space-y-1">
                {simulation.ai_decisions.title_suggestions.main_character_name && (
                  <div>• Główna postać: <span className="font-bold text-purple-300">{simulation.ai_decisions.title_suggestions.main_character_name}</span></div>
                )}
                {simulation.ai_decisions.title_suggestions.world_setting && (
                  <div>• Świat akcji: <span className="font-bold text-purple-300">{simulation.ai_decisions.title_suggestions.world_setting}</span></div>
                )}
                {simulation.ai_decisions.title_suggestions.add_subplots &&
                 simulation.ai_decisions.title_suggestions.add_subplots.length > 0 && (
                  <div>• Dodatkowe wątki: <span className="font-bold text-purple-300">{simulation.ai_decisions.title_suggestions.add_subplots.join(', ')}</span></div>
                )}
              </div>
            </div>
          )}
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
                {(simulation.ai_decisions.target_word_count || 0).toLocaleString()}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Liczba Rozdziałów</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.chapter_count || 0}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Główni Bohaterowie</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.main_character_count || 0}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Wątki Poboczne</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.subplot_count || 0}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Poziom Detali Świata</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.world_detail_level || 'N/A'}
              </div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-sm mb-1">Złożoność Stylu</div>
              <div className="text-2xl font-bold text-white">
                {simulation.ai_decisions.style_complexity || 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cost Summary */}
      {simulation && (
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">
            Szacowany Koszt i Czas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-gray-200 text-sm mb-1">Całkowity Szacowany Koszt</div>
              <div className="text-4xl font-bold text-white">
                ${(simulation.estimated_total_cost || 0).toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-gray-200 text-sm mb-1">Szacowany Czas Generacji</div>
              <div className="text-4xl font-bold text-white">
                {simulation.estimated_duration_minutes || 0} min
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
      {simulation && (
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
                    <span className="text-indigo-400 font-bold">Krok {step.step || 0}</span>
                    <span className="text-white font-semibold">{step.name || 'Unknown'}</span>
                    <span className="px-2 py-1 bg-gray-600 text-gray-300 rounded text-xs">
                      Tier {step.model_tier || 0}
                    </span>
                  </div>
                  <div className="text-green-400 font-semibold">
                    ${(step.estimated_cost || 0).toFixed(4)}
                  </div>
                </div>
                <p className="text-gray-400 text-sm mb-2">{step.description || ''}</p>
                <div className="text-gray-500 text-xs">
                  Szacowane tokeny: {(step.estimated_tokens || 0).toLocaleString()}
                </div>
                {/* Show current activity with time for active step */}
                {project.status === 'generating' && project.current_step === step.step && project.current_activity && (
                  <div className="mt-3 pt-3 border-t border-yellow-600">
                    <div className="text-yellow-400 font-semibold text-sm">
                      🔄 {project.current_activity}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {project.status === 'generating' && project.current_step && (
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">Postęp Generacji</h3>
          <div className="w-full bg-gray-700 rounded-full h-4 mb-4">
            <div
              className="bg-gradient-to-r from-indigo-600 to-purple-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${(project.current_step / 15) * 100}%` }}
            />
          </div>
          <div className="flex items-center justify-between mb-2">
            <div className="text-gray-300 text-sm">
              Krok {project.current_step} z 15
            </div>
            <div className="text-green-400 text-sm font-semibold">
              Aktualny koszt: ${project.actual_cost?.toFixed(2) || '0.00'}
            </div>
          </div>
          {project.current_activity && (
            <div className="bg-gradient-to-r from-indigo-900 to-purple-900 rounded-lg p-4 mt-3 border border-indigo-600">
              <div className="text-white font-semibold text-base">
                {project.current_activity}
              </div>
            </div>
          )}
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
