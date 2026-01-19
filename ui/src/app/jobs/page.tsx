"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import type { JobResponse } from "@/types/api";
import { format } from "date-fns";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await apiClient.listJobs({ limit: 50 });
      setJobs(data);
    } catch (err: any) {
      setError(err.message || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: "bg-gray-100 text-gray-800",
      running: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      cancelled: "bg-yellow-100 text-yellow-800",
    };

    return (
      <span
        className={`px-2 py-1 text-xs font-medium rounded-full ${
          styles[status as keyof typeof styles] || styles.pending
        }`}
      >
        {status.toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Ładowanie zleceń...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <svg
            className="w-12 h-12 text-red-600 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-medium text-red-900 mb-2">Błąd ładowania</h3>
          <p className="text-red-700">{error}</p>
          <button
            onClick={loadJobs}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Spróbuj ponownie
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Zlecenia</h1>
          <p className="text-gray-600">
            Zarządzaj wszystkimi projektami literackimi AI
          </p>
        </div>
        <Link
          href="/jobs/new"
          className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          + Nowe Zlecenie
        </Link>
      </div>

      {jobs.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-12 text-center">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Brak zleceń
          </h3>
          <p className="text-gray-600 mb-6">
            Utwórz nowe zlecenie, aby rozpocząć produkcję treści literackiej
          </p>
          <Link
            href="/jobs/new"
            className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Utwórz Pierwsze Zlecenie
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => (
            <Link
              key={job.job_id}
              href={`/jobs/${job.job_id}`}
              className="block bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {job.job_type.replace("_", " ").toUpperCase()}
                    </h3>
                    {getStatusBadge(job.status)}
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {job.user_inspiration}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <div className="text-sm font-medium text-gray-900">
                    ${job.current_cost.toFixed(3)}
                  </div>
                  <div className="text-xs text-gray-500">
                    z ${job.budget_limit.toFixed(2)}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-500 mb-1">Gatunek</div>
                  <div className="font-medium text-gray-900 capitalize">
                    {job.genre}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Cel Słów</div>
                  <div className="font-medium text-gray-900">
                    {job.target_word_count.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Postęp</div>
                  <div className="font-medium text-gray-900">{job.progress}%</div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Utworzono</div>
                  <div className="font-medium text-gray-900">
                    {format(new Date(job.created_at), "dd MMM yyyy")}
                  </div>
                </div>
              </div>

              {job.progress > 0 && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
