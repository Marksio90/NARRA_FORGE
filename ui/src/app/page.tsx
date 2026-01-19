import Link from "next/link";

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Autonomiczna Platforma Produkcji Literackiej
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Wieloagentowy system AI do automatycznej tworzenia treści literackich
          z kontrolą jakości, kosztów i pełną obserwowalnoś cią.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/jobs/new"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Utwórz Nowe Zlecenie
          </Link>
          <Link
            href="/jobs"
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            Przeglądaj Zlecenia
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">7 Agentów AI</h3>
          <p className="text-gray-600">
            Interpreter, WorldArchitect, CharacterArchitect, PlotCreator, ProseGenerator, QAAgent, StylePolish
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Bramki Jakości</h3>
          <p className="text-gray-600">
            Automatyczna walidacja logiki, psychologii postaci i spójności fabularnej
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Kontrola Kosztów</h3>
          <p className="text-gray-600">
            Śledzenie kosztów OpenAI w czasie rzeczywistym z budżetem i alertami
          </p>
        </div>
      </div>

      {/* Pipeline Stages */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Pipeline Produkcji</h2>
        <div className="grid md:grid-cols-9 gap-2">
          {[
            { name: "INTERPRET", color: "bg-blue-500" },
            { name: "WORLD", color: "bg-green-500" },
            { name: "CHARACTER", color: "bg-yellow-500" },
            { name: "PLOT", color: "bg-purple-500" },
            { name: "PROSE", color: "bg-pink-500" },
            { name: "STYLE", color: "bg-indigo-500" },
            { name: "QA", color: "bg-red-500" },
            { name: "DIALOG", color: "bg-orange-500" },
            { name: "PACKAGE", color: "bg-teal-500" },
          ].map((stage, idx) => (
            <div key={stage.name} className="text-center">
              <div className={`${stage.color} text-white rounded-lg py-3 px-2 mb-2 font-medium text-sm`}>
                {idx + 1}
              </div>
              <div className="text-xs text-gray-600 font-medium">{stage.name}</div>
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-500 mt-6 text-center">
          Każdy etap wykorzystuje specjalizowany model AI (gpt-4o lub gpt-4o-mini) z dedykowanym budżetem tokenów
        </p>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-4 gap-6 mt-12">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">99%</div>
          <div className="text-sm text-gray-600">Test Coverage</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">264</div>
          <div className="text-sm text-gray-600">Unit Tests</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">2</div>
          <div className="text-sm text-gray-600">AI Models</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm text-center">
          <div className="text-3xl font-bold text-primary-600 mb-1">7</div>
          <div className="text-sm text-gray-600">AI Agents</div>
        </div>
      </div>
    </div>
  );
}
