import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NarraForge - AI Book Generation Platform',
  description: 'Multi-agent AI platform for autonomous book generation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">📚</span>
                <h1 className="text-2xl font-bold text-gray-900">NarraForge</h1>
              </div>
              <nav className="flex space-x-4">
                <a href="/" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </a>
                <a href="/jobs" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Jobs
                </a>
              </nav>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="bg-white border-t mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-sm text-gray-500">
              NarraForge v1.0.0 MVP - Built with ❤️ using Claude Code
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}
