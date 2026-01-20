import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Dashboard</h2>
        <p className="text-gray-400">
          Witaj w NarraForge - Autonomicznej Kuźni Literackiej
        </p>
      </div>

      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-8 mb-8">
        <h3 className="text-2xl font-bold text-white mb-4">
          Stwórz swoją pierwszą książkę
        </h3>
        <Link
          to="/create"
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-white hover:bg-indigo-50"
        >
          Utwórz Nowy Projekt
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
