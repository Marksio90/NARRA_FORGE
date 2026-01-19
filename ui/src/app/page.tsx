export default function HomePage() {
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to NarraForge
        </h2>
        <p className="text-lg text-gray-600 mb-6">
          Multi-agent AI platform for autonomous book generation using LangGraph and OpenAI.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="border rounded-lg p-4">
            <div className="text-3xl mb-2">🤖</div>
            <h3 className="font-semibold text-lg mb-2">Multi-Agent System</h3>
            <p className="text-sm text-gray-600">
              4 specialized AI agents orchestrated with LangGraph
            </p>
          </div>

          <div className="border rounded-lg p-4">
            <div className="text-3xl mb-2">🎭</div>
            <h3 className="font-semibold text-lg mb-2">3 Genres</h3>
            <p className="text-sm text-gray-600">
              Fantasy, Sci-Fi, and Thriller with genre-specific expertise
            </p>
          </div>

          <div className="border rounded-lg p-4">
            <div className="text-3xl mb-2">💰</div>
            <h3 className="font-semibold text-lg mb-2">Cost Tracking</h3>
            <p className="text-sm text-gray-600">
              Real-time monitoring of OpenAI API costs per stage
            </p>
          </div>
        </div>

        <div className="flex space-x-4">
          <a
            href="/jobs/new"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Create New Book
          </a>
          <a
            href="/jobs"
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            View Jobs
          </a>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-lg mb-2 text-blue-900">
          🚀 Getting Started
        </h3>
        <ol className="list-decimal list-inside space-y-2 text-blue-800">
          <li>Click "Create New Book" to start a generation job</li>
          <li>Choose a genre (Fantasy, Sci-Fi, or Thriller)</li>
          <li>Provide inspiration for your story</li>
          <li>Set a budget limit (default $10 USD)</li>
          <li>Monitor real-time progress with WebSocket updates</li>
          <li>Export your book in Markdown or JSON format</li>
        </ol>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold text-lg mb-4">Pipeline Stages</h3>
        <div className="space-y-3">
          {[
            { stage: '1. World Building', agent: 'World_Architect', desc: 'Create rich, consistent worlds' },
            { stage: '2. Character Creation', agent: 'Character_Smith', desc: 'Develop compelling characters' },
            { stage: '3. Plot Structure', agent: 'Plot_Master', desc: 'Design engaging storylines' },
            { stage: '4. Prose Generation', agent: 'Prose_Weaver', desc: 'Write beautiful prose' },
          ].map((item) => (
            <div key={item.stage} className="flex items-start space-x-3 border-l-4 border-blue-500 pl-4">
              <div className="flex-1">
                <div className="font-medium text-gray-900">{item.stage}</div>
                <div className="text-sm text-gray-600">
                  <span className="font-semibold">{item.agent}</span> - {item.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
