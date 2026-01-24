import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Dashboard from './pages/Dashboard';
import ProjectCreator from './pages/ProjectCreator';
import ProjectView from './pages/ProjectView';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-900 text-white">
          <nav className="bg-gray-800 border-b border-gray-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold text-indigo-400">
                    📚 NARRAFORGE
                  </h1>
                  <p className="ml-4 text-sm text-gray-400">
                    Autonomiczna Kuźnia Literacka
                  </p>
                </div>
              </div>
            </div>
          </nav>

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<ProjectCreator />} />
            <Route path="/project/:id" element={<ProjectView />} />
          </Routes>
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
