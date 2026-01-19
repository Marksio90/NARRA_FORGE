"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import type { Genre, JobType } from "@/types/api";

export default function NewJobPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    job_type: "short_story" as JobType,
    genre: "fantasy" as Genre,
    user_inspiration: "",
    target_word_count: 2000,
    budget_limit: 5.0,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const job = await apiClient.createJob(formData);
      router.push(`/jobs/${job.job_id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create job");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Utwórz Nowe Zlecenie
        </h1>
        <p className="text-gray-600">
          Skonfiguruj parametry dla nowego projektu literackiego AI
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-red-600 mt-0.5 mr-3"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-red-800">Błąd</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
        {/* Job Type */}
        <div className="mb-6">
          <label htmlFor="job_type" className="block text-sm font-medium text-gray-700 mb-2">
            Typ Zlecenia
          </label>
          <select
            id="job_type"
            value={formData.job_type}
            onChange={(e) =>
              setFormData({ ...formData, job_type: e.target.value as JobType })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          >
            <option value="short_story">Opowiadanie (Short Story)</option>
            <option value="novel_chapter">Rozdział Powieści (Novel Chapter)</option>
            <option value="scene">Scena (Scene)</option>
            <option value="character_study">Studium Postaci (Character Study)</option>
            <option value="world_building">World Building</option>
          </select>
        </div>

        {/* Genre */}
        <div className="mb-6">
          <label htmlFor="genre" className="block text-sm font-medium text-gray-700 mb-2">
            Gatunek
          </label>
          <select
            id="genre"
            value={formData.genre}
            onChange={(e) =>
              setFormData({ ...formData, genre: e.target.value as Genre })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          >
            <option value="fantasy">Fantasy</option>
            <option value="sci-fi">Sci-Fi</option>
            <option value="thriller">Thriller</option>
            <option value="literary">Literatura piękna</option>
            <option value="horror">Horror</option>
            <option value="mystery">Mystery</option>
            <option value="romance">Romans</option>
          </select>
        </div>

        {/* User Inspiration */}
        <div className="mb-6">
          <label htmlFor="user_inspiration" className="block text-sm font-medium text-gray-700 mb-2">
            Inspiracja / Temat <span className="text-red-500">*</span>
          </label>
          <textarea
            id="user_inspiration"
            value={formData.user_inspiration}
            onChange={(e) =>
              setFormData({ ...formData, user_inspiration: e.target.value })
            }
            rows={6}
            placeholder="Opisz temat, inspirację lub koncepcję dla utworu literackiego. Np: 'Opowiadanie o czarodzieju, który odkrywa zapomniane królestwo pod miastem'..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            required
            minLength={20}
            maxLength={1000}
          />
          <p className="text-xs text-gray-500 mt-1">
            Minimum 20 znaków, maksimum 1000 znaków
          </p>
        </div>

        {/* Target Word Count */}
        <div className="mb-6">
          <label htmlFor="target_word_count" className="block text-sm font-medium text-gray-700 mb-2">
            Docelowa Liczba Słów
          </label>
          <input
            type="number"
            id="target_word_count"
            value={formData.target_word_count}
            onChange={(e) =>
              setFormData({ ...formData, target_word_count: parseInt(e.target.value) })
            }
            min={500}
            max={50000}
            step={100}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            500 - 50,000 słów (opowiadanie: ~2000-5000 słów)
          </p>
        </div>

        {/* Budget Limit */}
        <div className="mb-8">
          <label htmlFor="budget_limit" className="block text-sm font-medium text-gray-700 mb-2">
            Limit Budżetu (USD)
          </label>
          <input
            type="number"
            id="budget_limit"
            value={formData.budget_limit}
            onChange={(e) =>
              setFormData({ ...formData, budget_limit: parseFloat(e.target.value) })
            }
            min={1}
            max={100}
            step={0.5}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Maksymalny koszt OpenAI API dla tego zlecenia ($1-$100)
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Tworzenie..." : "Utwórz Zlecenie"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            Anuluj
          </button>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-blue-600 mt-0.5 mr-3"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-blue-900 mb-1">
                Informacje o procesie
              </h4>
              <p className="text-sm text-blue-800">
                Po utworzeniu zlecenia, system automatycznie uruchomi wieloagentowy pipeline produkcji.
                Proces obejmuje 9 etapów: interpretację, world-building, tworzenie postaci, fabuły,
                prozy, stylizację, QA, dialogi i pakowanie. Możesz śledzić postęp w czasie rzeczywistym.
              </p>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
