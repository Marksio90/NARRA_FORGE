import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

// Lazy-loaded pages for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ProjectCreator = lazy(() => import('./pages/ProjectCreator'));
const ProjectView = lazy(() => import('./pages/ProjectView'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400 mx-auto mb-4" />
        <p className="text-gray-400">Wczytywanie...</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-900 text-white">
          <nav className="bg-gray-800 border-b border-gray-700" role="navigation" aria-label="Main navigation">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold text-indigo-400">
                    NARRAFORGE
                  </h1>
                  <p className="ml-4 text-sm text-gray-400">
                    Autonomiczna Kuźnia Literacka
                  </p>
                </div>
              </div>
            </div>
          </nav>

          <main role="main">
            <Suspense fallback={<LoadingFallback />}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/create" element={<ProjectCreator />} />
                <Route path="/project/:id" element={<ProjectView />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </Router>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </ErrorBoundary>
  );
}

export default App;
