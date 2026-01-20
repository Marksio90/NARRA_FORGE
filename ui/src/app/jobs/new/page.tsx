'use client'

/**
 * Formularz tworzenia nowego zadania - NarraForge
 *
 * Pozwala użytkownikowi stworzyć nowe zadanie generowania książki z parametrami:
 * - Gatunek literacki
 * - Inspiracja dla świata
 * - Liczba głównych postaci
 * - Długość (krótka/średnia/długa)
 * - Styl narracji
 * - Budżet
 */

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function NewJobPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [gatunek, setGatunek] = useState('')
  const [inspiracja, setInspiracja] = useState('')
  const [liczbaPostaci, setLiczbaPostaci] = useState(3)
  const [dlugosc, setDlugosc] = useState<'krótka' | 'srednia' | 'długa'>('srednia')
  const [styl, setStyl] = useState<'literacki' | 'poetycki' | 'dynamiczny' | 'noir'>('literacki')
  const [wskazowki, setWskazowki] = useState('')
  const [budzet, setBudzet] = useState(10.0)

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
          inspiracja,
          liczba_glownych_postaci: liczbaPostaci,
          docelowa_dlugosc: dlugosc,
          styl_narracji: styl,
          dodatkowe_wskazowki: wskazowki || null,
          budget_limit: budzet,
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
            Nowe Zadanie
          </h1>
          <p className="text-gray-600">
            Utwórz nowe zadanie generowania książki z pomocą AI
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
              Gatunek literacki *
            </label>
            <input
              type="text"
              required
              value={gatunek}
              onChange={(e) => setGatunek(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="np. fantasy, sci-fi, thriller, romans, horror"
              minLength={2}
              maxLength={100}
            />
            <p className="mt-1 text-sm text-gray-500">
              Wybierz gatunek dla swojej książki
            </p>
          </div>

          {/* Inspiracja */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Inspiracja dla świata i historii *
            </label>
            <textarea
              required
              value={inspiracja}
              onChange={(e) => setInspiracja(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Opisz swój pomysł na świat, główne motywy, atmosferę..."
              rows={5}
              minLength={10}
              maxLength={2000}
            />
            <p className="mt-1 text-sm text-gray-500">
              {inspiracja.length} / 2000 znaków
            </p>
          </div>

          {/* Liczba postaci */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Liczba głównych postaci: {liczbaPostaci}
            </label>
            <input
              type="range"
              min="2"
              max="5"
              value={liczbaPostaci}
              onChange={(e) => setLiczbaPostaci(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>2 (minimalna)</span>
              <span>5 (maksymalna)</span>
            </div>
          </div>

          {/* Długość */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Długość książki
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setDlugosc('krótka')}
                className={`px-4 py-3 rounded-lg border-2 transition-all ${
                  dlugosc === 'krótka'
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-semibold">Krótka</div>
                <div className="text-xs text-gray-600">8-12 scen</div>
              </button>
              <button
                type="button"
                onClick={() => setDlugosc('srednia')}
                className={`px-4 py-3 rounded-lg border-2 transition-all ${
                  dlugosc === 'srednia'
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-semibold">Średnia</div>
                <div className="text-xs text-gray-600">15-20 scen</div>
              </button>
              <button
                type="button"
                onClick={() => setDlugosc('długa')}
                className={`px-4 py-3 rounded-lg border-2 transition-all ${
                  dlugosc === 'długa'
                    ? 'border-blue-600 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="font-semibold">Długa</div>
                <div className="text-xs text-gray-600">25+ scen</div>
              </button>
            </div>
          </div>

          {/* Styl narracji */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Styl narracji
            </label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { value: 'literacki', label: 'Literacki', desc: 'Klasyczny, zbalansowany' },
                { value: 'poetycki', label: 'Poetycki', desc: 'Metaforyczny, liryczny' },
                { value: 'dynamiczny', label: 'Dynamiczny', desc: 'Szybki, akcja' },
                { value: 'noir', label: 'Noir', desc: 'Mroczny, atmosferyczny' },
              ].map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setStyl(option.value as any)}
                  className={`px-4 py-3 rounded-lg border-2 text-left transition-all ${
                    styl === option.value
                      ? 'border-blue-600 bg-blue-50 text-blue-900'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="font-semibold">{option.label}</div>
                  <div className="text-xs text-gray-600">{option.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Dodatkowe wskazówki */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dodatkowe wskazówki (opcjonalne)
            </label>
            <textarea
              value={wskazowki}
              onChange={(e) => setWskazowki(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Dodatkowe wytyczne dla AI dotyczące stylu, tematów, postaci..."
              rows={3}
              maxLength={1000}
            />
          </div>

          {/* Budżet */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Limit budżetu: ${budzet.toFixed(2)} USD
            </label>
            <input
              type="range"
              min="1"
              max="100"
              step="0.5"
              value={budzet}
              onChange={(e) => setBudzet(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>$1 (minimum)</span>
              <span>$100 (maksimum)</span>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Szacowany koszt dla średniej książki: $5-15 USD
            </p>
          </div>

          {/* Submit */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
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
                'Utwórz zadanie i rozpocznij generowanie'
              )}
            </button>

            <Link
              href="/jobs"
              className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Anuluj
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
