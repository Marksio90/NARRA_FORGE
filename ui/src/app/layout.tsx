import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NARRA_FORGE - Autonomous Literary Production Platform",
  description: "AI-powered platform for autonomous literary content creation with multi-agent orchestration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pl">
      <body className="antialiased bg-gray-50 text-gray-900">
        <div className="min-h-screen flex flex-col">
          <header className="bg-white border-b border-gray-200 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">NF</span>
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900">NARRA_FORGE</h1>
                    <p className="text-sm text-gray-500">Autonomous Literary Platform</p>
                  </div>
                </div>
                <nav className="flex gap-6">
                  <a href="/" className="text-gray-600 hover:text-primary-600 font-medium transition-colors">
                    Dashboard
                  </a>
                  <a href="/jobs" className="text-gray-600 hover:text-primary-600 font-medium transition-colors">
                    Jobs
                  </a>
                  <a href="/docs" className="text-gray-600 hover:text-primary-600 font-medium transition-colors">
                    API Docs
                  </a>
                </nav>
              </div>
            </div>
          </header>
          <main className="flex-1">
            {children}
          </main>
          <footer className="bg-white border-t border-gray-200 mt-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <p className="text-center text-sm text-gray-500">
                NARRA_FORGE © 2026 | Powered by GPT-4o & Multi-Agent AI
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
