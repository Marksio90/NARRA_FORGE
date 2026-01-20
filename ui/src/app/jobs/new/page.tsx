'use client'

/**
 * Formularz tworzenia nowego zadania - AUTONOMICZNE AI - NarraForge
 *
 * Użytkownik wybiera TYLKO:
 * - Gatunek literacki
 * - Długość książki
 *
 * AI decyduje o wszystkim innym:
 * - Świat i fabuła (całkowicie autonomiczne)
 * - Liczba postaci (2-5, auto-dobrana)
 * - Styl narracji (auto-mapowany z gatunku)
 * - Budżet (auto-obliczony)
 */

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface Estimate {
  gatunek: string
  docelowa_dlugosc: string
  szacowany_koszt_min: number
  szacowany_koszt_max: number
  szacowany_czas_min: number
  szacowany_czas_max: number
  liczba_scen: number
  szacowana_liczba_slow: number
  auto_styl_narracji: string
  auto_liczba_postaci: number
}

const GATUNKI = [
  'Fantasy',
  'Sci-Fi',
  'Thriller',
  'Horror',
  'Romans',
  'Western',
  'Noir',
  'Mystery',
]

export default function NewJobPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [estimating, setEstimating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state - TYLKO 2 POLA!
  const [gatunek, setGatunek] = useState('Fantasy')
  const [dlugosc, setDlugosc] = useState<'krótka' | 'srednia' | 'długa'>('srednia')

  // Estimate state
  const [estimate, setEstimate] = useState<Estimate | null>(null)

  const handleEstimate = async () => {
    setEstimating(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/jobs/estimate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gatunek,
          docelowa_dlugosc: dlugosc,
        }),
      })

      if (!response.ok) {
        throw new Error('Nie udało się oszacować kosztów')
      }

      const data = await response.json()
      setEstimate(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nieznany błąd')
    } finally {
      setEstimating(false)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gatunek,
          docelowa_dlugosc: dlugosc,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Nie udało się utworzyć zadania')
      }

      const job = await response.json()

      // Redirect to job details page
      router.push(`/jobs/${job.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nieznany błąd')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/jobs"
            className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
          >
            ← Powrót do listy
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Generowanie Książki z AI
          </h1>
          <p className="text-gray-600">
            Wybierz gatunek i długość - AI stworzy resztę autonomicznie!
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">Błąd: {error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-8">
          {/* Gatunek */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gatunek literacki
            </label>
            <select
              value={gatunek}
              onChange={(e) => {
                setGatunek(e.target.value)
                setEstimate(null) // Reset estimate
              }}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            >
              {GATUNKI.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          {/* Długość */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Długość książki
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => {
                  setDlugosc('krótka')
                  setEstimate(null)
                }}
                className={`px-4 py-4 rounded-lg border-2 transition-all ${
                  dlugosc === 'krótka'
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-bold text-lg">Krótka</div>
                <div className="text-xs text-gray-600 mt-1">~10 scen</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  setDlugosc('srednia')
                  setEstimate(null)
                }}
                className={`px-4 py-4 rounded-lg border-2 transition-all ${
                  dlugosc === 'srednia'
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-bold text-lg">Średnia</div>
                <div className="text-xs text-gray-600 mt-1">~16 scen</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  setDlugosc('długa')
                  setEstimate(null)
                }}
                className={`px-4 py-4 rounded-lg border-2 transition-all ${
                  dlugosc === 'długa'
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-bold text-lg">Długa</div>
                <div className="text-xs text-gray-600 mt-1">~25 scen</div>
              </button>
            </div>
          </div>

          {/* Estimate Button */}
          <div className="mb-6">
            <button
              type="button"
              onClick={handleEstimate}
              disabled={estimating}
              className="w-full px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium disabled:bg-gray-400"
            >
              {estimating ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Szacowanie...
                </span>
              ) : (
                '💰 Oszacuj koszt i szczegóły'
              )}
            </button>
          </div>

          {/* Estimate Display */}
          {estimate && (
            <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-bold text-lg text-blue-900 mb-4">
                📊 Szacowanie dla: {estimate.gatunek} ({estimate.docelowa_dlugosc})
              </h3>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-white rounded-lg p-3">
                  <div className="text-sm text-gray-600">Szacowany koszt</div>
                  <div className="text-2xl font-bold text-blue-900">
                    ${estimate.szacowany_koszt_min.toFixed(2)} - $
                    {estimate.szacowany_koszt_max.toFixed(2)}
                  </div>
                </div>
                <div className="bg-white rounded-lg p-3">
                  <div className="text-sm text-gray-600">Czas generowania</div>
                  <div className="text-2xl font-bold text-blue-900">
                    {estimate.szacowany_czas_min}-{estimate.szacowany_czas_max} min
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-white rounded-lg p-3">
                  <div className="text-sm text-gray-600">Liczba scen</div>
                  <div className="text-xl font-bold text-gray-900">
                    {estimate.liczba_scen} scen
                  </div>
                </div>
                <div className="bg-white rounded-lg p-3">
                  <div className="text-sm text-gray-600">Liczba słów</div>
                  <div className="text-xl font-bold text-gray-900">
                    ~{estimate.szacowana_liczba_slow.toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-4">
                <div className="font-semibold text-gray-900 mb-2">
                  🤖 Auto-wybory AI:
                </div>
                <div className="space-y-1 text-sm">
                  <div>
                    <span className="text-gray-600">Styl narracji:</span>{' '}
                    <span className="font-medium">{estimate.auto_styl_narracji}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Liczba głównych postaci:</span>{' '}
                    <span className="font-medium">{estimate.auto_liczba_postaci}</span>
                  </div>
                  <div className="text-gray-500 italic mt-2">
                    AI autonomicznie stworzy świat, postacie i fabułę
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Submit */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-bold text-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Tworzenie zadania...
                </span>
              ) : (
                '🚀 Rozpocznij autonomiczne generowanie'
              )}
            </button>

            <Link
              href="/jobs"
              className="px-6 py-4 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium flex items-center"
            >
              Anuluj
            </Link>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-bold text-lg mb-3">✨ Jak to działa?</h3>
          <ol className="space-y-2 text-sm text-gray-700">
            <li>
              <strong>1. Wybierz</strong> gatunek i długość (tylko 2 pola!)
            </li>
            <li>
              <strong>2. Oszacuj</strong> koszt aby zobaczyć szczegóły
            </li>
            <li>
              <strong>3. Rozpocznij</strong> - AI stworzy wszystko autonomicznie
            </li>
            <li>
              <strong>4. Obserwuj</strong> live progress każdego kroku
            </li>
          </ol>
          <div className="mt-4 p-3 bg-white rounded-lg">
            <div className="text-sm font-medium text-gray-900 mb-1">
              AI decyduje o:
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <div>• Unikalnym świecie i jego historii</div>
              <div>• Fascynujących postaciach (2-5 głównych)</div>
              <div>• Wciągającej fabule i zwrotach akcji</div>
              <div>• Stylu narracji dopasowanym do gatunku</div>
              <div>• Każdym szczególe prozy</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
