'use client'

/**
 * Strona listy zadań generowania książek - NarraForge
 *
 * Wyświetla:
 * - Wszystkie zadania z ich statusami
 * - Filtry po statusie
 * - Linki do szczegółów i tworzenia nowego
 */

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Job {
  id: string
  gatunek: string
  inspiracja: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  cost_current: number
  budget_limit: number
  liczba_glownych_postaci: number
  docelowa_dlugosc: string
  styl_narracji: string
  created_at: string
  updated_at: string
  result?: any
}

export default function JobsListPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    fetchJobs()
  }, [statusFilter])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter) {
        params.append('status_filter', statusFilter)
      }

      const response = await fetch(
        `http://localhost:8000/api/jobs?${params.toString()}`
      )

      if (!response.ok) {
        throw new Error('Nie udało się pobrać listy zadań')
      }

      const data = await response.json()
      setJobs(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nieznany błąd')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      queued: 'bg-gray-100 text-gray-800',
      running: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    }

    const labels: Record<string, string> = {
      queued: 'W kolejce',
      running: 'W trakcie',
      completed: 'Ukończone',
      failed: 'Błąd',
    }

    return (
      <span
        className={`px-2 py-1 text-xs font-semibold rounded-full ${
          styles[status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {labels[status] || status}
      </span>
    )
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('pl-PL')
  }

  const truncate = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Lista Zadań
            </h1>
            <p className="text-gray-600">
              Wszystkie zadania generowania książek
            </p>
          </div>

          <Link
            href="/jobs/new"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + Nowe Zadanie
          </Link>
        </div>

        {/* Filters */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              statusFilter === ''
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Wszystkie
          </button>
          <button
            onClick={() => setStatusFilter('queued')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              statusFilter === 'queued'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            W kolejce
          </button>
          <button
            onClick={() => setStatusFilter('running')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              statusFilter === 'running'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            W trakcie
          </button>
          <button
            onClick={() => setStatusFilter('completed')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              statusFilter === 'completed'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Ukończone
          </button>
          <button
            onClick={() => setStatusFilter('failed')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              statusFilter === 'failed'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Błędy
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Ładowanie zadań...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">Błąd: {error}</p>
            <button
              onClick={fetchJobs}
              className="mt-2 text-red-600 hover:text-red-800 underline"
            >
              Spróbuj ponownie
            </button>
          </div>
        )}

        {/* Jobs List */}
        {!loading && !error && (
          <div className="space-y-4">
            {jobs.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-600 mb-4">
                  Brak zadań do wyświetlenia
                </p>
                <Link
                  href="/jobs/new"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  Utwórz pierwsze zadanie
                </Link>
              </div>
            ) : (
              jobs.map((job) => (
                <Link
                  key={job.id}
                  href={`/jobs/${job.id}`}
                  className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900">
                          {job.gatunek}
                        </h3>
                        {getStatusBadge(job.status)}
                      </div>
                      <p className="text-gray-600 mb-2">
                        {truncate(job.inspiracja, 150)}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Długość</p>
                      <p className="font-medium text-gray-900">
                        {job.docelowa_dlugosc}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Styl</p>
                      <p className="font-medium text-gray-900">
                        {job.styl_narracji}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Koszt</p>
                      <p className="font-medium text-gray-900">
                        ${job.cost_current.toFixed(2)} / ${job.budget_limit.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Utworzono</p>
                      <p className="font-medium text-gray-900">
                        {formatDate(job.created_at)}
                      </p>
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
