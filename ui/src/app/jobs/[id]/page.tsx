'use client'

/**
 * Strona szczegółów zadania - NarraForge
 *
 * Wyświetla:
 * - Status i szczegóły zadania
 * - Real-time progress (WebSocket)
 * - Wyniki gdy ukończone (świat, postacie, fabuła, proza)
 * - Koszty i statystyki
 */

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
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

interface ProgressUpdate {
  job_id: string
  etap: string
  procent: number
  task_id: string
  szczegoly?: string
}

interface JobResult {
  job: Job
  swiat?: any
  postacie: any[]
  fabula?: any
  proza_chunks: any[]
  statystyki: {
    koszt_total_usd: number
    liczba_scen: number
    liczba_slow_razem: number
    liczba_postaci: number
    status: string
  }
}

export default function JobDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.id as string

  const [job, setJob] = useState<Job | null>(null)
  const [result, setResult] = useState<JobResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Progress state
  const [progress, setProgress] = useState<ProgressUpdate | null>(null)
  const [wsConnected, setWsConnected] = useState(false)

  // Fetch job details
  useEffect(() => {
    fetchJob()
  }, [jobId])

  // WebSocket connection for real-time progress
  useEffect(() => {
    if (!job) return
    if (job.status !== 'running' && job.status !== 'queued') return

    const ws = new WebSocket(`ws://localhost:8000/api/ws/jobs/${jobId}/progress`)

    ws.onopen = () => {
      console.log('WebSocket połączony')
      setWsConnected(true)
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.typ === 'progress') {
        setProgress(message.data)
      } else if (message.typ === 'zakonczono') {
        // Job ukończony - reload details
        fetchJob()
        ws.close()
      } else if (message.typ === 'polaczono') {
        console.log('Połączono z serwerem:', message.data.komunikat)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setWsConnected(false)
    }

    ws.onclose = () => {
      console.log('WebSocket rozłączony')
      setWsConnected(false)
    }

    return () => {
      ws.close()
    }
  }, [job, jobId])

  const fetchJob = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`)

      if (!response.ok) {
        throw new Error('Nie udało się pobrać szczegółów zadania')
      }

      const data = await response.json()
      setJob(data)

      // Jeśli ukończone, pobierz pełny wynik
      if (data.status === 'completed') {
        await fetchResult()
      }

      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nieznany błąd')
    } finally {
      setLoading(false)
    }
  }

  const fetchResult = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${jobId}/result`)

      if (!response.ok) {
        throw new Error('Nie udało się pobrać wyniku')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error('Błąd pobierania wyniku:', err)
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
        className={`px-3 py-1 text-sm font-semibold rounded-full ${
          styles[status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {labels[status] || status}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Ładowanie szczegółów zadania...</p>
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-800">Błąd: {error || 'Zadanie nie znalezione'}</p>
            <Link href="/jobs" className="mt-4 inline-block text-red-600 hover:text-red-800 underline">
              Powrót do listy
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/jobs"
            className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
          >
            ← Powrót do listy
          </Link>

          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-4xl font-bold text-gray-900">
                  {job.gatunek}
                </h1>
                {getStatusBadge(job.status)}
                {wsConnected && job.status === 'running' && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                    ● Live
                  </span>
                )}
              </div>
              <p className="text-gray-600">{job.inspiracja}</p>
            </div>
          </div>
        </div>

        {/* Progress Bar (for running jobs) */}
        {(job.status === 'running' || job.status === 'queued') && (
          <div className="mb-8 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Postęp generowania</h2>

            {progress ? (
              <>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="text-gray-600 font-medium">{progress.etap}</span>
                  <span className="font-semibold text-blue-600">
                    {progress.procent.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                  <div
                    className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${progress.procent}%` }}
                  ></div>
                </div>

                {/* Szczegółowe informacje o tym co AI tworzy */}
                {progress.szczegoly && (
                  <div className="mt-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
                    <div className="text-sm text-gray-800 whitespace-pre-line font-mono">
                      {progress.szczegoly}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-4 text-gray-600">
                {job.status === 'queued' ? 'Oczekiwanie w kolejce...' : 'Łączenie z serwerem...'}
              </div>
            )}
          </div>
        )}

        {/* Job Details */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Szczegóły zadania</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-500">Długość</p>
              <p className="font-medium text-gray-900">{job.docelowa_dlugosc}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Styl</p>
              <p className="font-medium text-gray-900">{job.styl_narracji}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Postacie główne</p>
              <p className="font-medium text-gray-900">{job.liczba_glownych_postaci}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Koszt</p>
              <p className="font-medium text-gray-900">
                ${job.cost_current.toFixed(2)} / ${job.budget_limit.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {/* Results (if completed) */}
        {job.status === 'completed' && result && (
          <div className="space-y-6">
            {/* Statistics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Statystyki</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                  <p className="text-sm text-gray-500">Liczba scen</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {result.statystyki.liczba_scen}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Liczba słów</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {result.statystyki.liczba_slow_razem.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Postaci</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {result.statystyki.liczba_postaci}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Koszt końcowy</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${result.statystyki.koszt_total_usd.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            {/* World */}
            {result.swiat && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Świat</h2>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {result.swiat.nazwa}
                </h3>
                <p className="text-gray-700 mb-4">{result.swiat.opis}</p>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-900 mb-1">Tematyka</p>
                    <p className="text-gray-600">
                      {result.swiat.tematyka?.join(', ') || 'Brak'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Characters */}
            {result.postacie.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">
                  Postacie ({result.postacie.length})
                </h2>
                <div className="space-y-4">
                  {result.postacie.slice(0, 5).map((postac: any) => (
                    <div key={postac.id} className="border-l-4 border-blue-600 pl-4">
                      <h3 className="font-semibold text-gray-900">
                        {postac.imie}
                        <span className="ml-2 text-sm text-gray-500">
                          ({postac.rola})
                        </span>
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {postac.biografia?.skrot || 'Brak biografii'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Prose Preview */}
            {result.proza_chunks.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">
                  Podgląd prozy (pierwsza scena)
                </h2>
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">
                    {result.proza_chunks[0].tresc.substring(0, 1000)}
                    {result.proza_chunks[0].tresc.length > 1000 && '...'}
                  </p>
                </div>
                <p className="mt-4 text-sm text-gray-500">
                  Scena {result.proza_chunks[0].scena_numer} •{' '}
                  {result.proza_chunks[0].liczba_slow} słów
                </p>
              </div>
            )}
          </div>
        )}

        {/* Failed State */}
        {job.status === 'failed' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-900 mb-2">
              Zadanie nie powiodło się
            </h2>
            <p className="text-red-700">
              {job.result?.blad || 'Wystąpił nieoczekiwany błąd podczas generowania'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
