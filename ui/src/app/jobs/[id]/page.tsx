"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import type {
  JobResponse,
  PipelineExecutionResponse,
  ArtifactSchema,
  CostSnapshot,
} from "@/types/api";
import { format } from "date-fns";

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  const [job, setJob] = useState<JobResponse | null>(null);
  const [pipeline, setPipeline] = useState<PipelineExecutionResponse | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactSchema[]>([]);
  const [costs, setCosts] = useState<CostSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "artifacts" | "costs">("overview");

  useEffect(() => {
    loadJobData();
    const interval = setInterval(loadJobData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [jobId]);

  const loadJobData = async () => {
    try {
      const [jobData, pipelineData, artifactsData, costsData] = await Promise.all([
        apiClient.getJob(jobId),
        apiClient.getPipelineStatus(jobId).catch(() => null),
        apiClient.getArtifacts(jobId).catch(() => []),
        apiClient.getCosts(jobId).catch(() => []),
      ]);

      setJob(jobData);
      setPipeline(pipelineData);
      setArtifacts(artifactsData);
      setCosts(costsData);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load job");
    } finally {
      setLoading(false);
    }
  };

  const handleStartPipeline = async () => {
    try {
      await apiClient.executePipeline(jobId);
      await loadJobData();
    } catch (err: any) {
      alert(`Błąd uruchamiania pipeline: ${err.message}`);
    }
  };

  const handleCancelJob = async () => {
    if (!confirm("Czy na pewno chcesz anulować to zlecenie?")) return;

    try {
      await apiClient.cancelJob(jobId);
      router.push("/jobs");
    } catch (err: any) {
      alert(`Błąd anulowania zlecenia: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Ładowanie szczegółów zlecenia...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">{error || "Job not found"}</p>
          <button
            onClick={() => router.back()}
            className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Wróć
          </button>
        </div>
      </div>
    );
  }

  const pipelineStages = [
    { name: "STRUCTURE", label: "Struktura", color: "bg-blue-500" },
    { name: "PLAN", label: "Plan", color: "bg-green-500" },
    { name: "WORLD", label: "Świat", color: "bg-yellow-500" },
    { name: "CHARACTER_PROFILE", label: "Postacie", color: "bg-purple-500" },
    { name: "PROSE", label: "Proza", color: "bg-pink-500" },
    { name: "STYLE", label: "Styl", color: "bg-indigo-500" },
    { name: "QA", label: "QA", color: "bg-red-500" },
    { name: "DIALOG", label: "Dialog", color: "bg-orange-500" },
    { name: "PACKAGE", label: "Pakiet", color: "bg-teal-500" },
  ];

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: "bg-gray-100 text-gray-800",
      running: "bg-blue-100 text-blue-800 animate-pulse",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      cancelled: "bg-yellow-100 text-yellow-800",
    };

    return (
      <span
        className={`px-3 py-1 text-sm font-medium rounded-full ${
          styles[status as keyof typeof styles] || styles.pending
        }`}
      >
        {status.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
          <a href="/jobs" className="hover:text-primary-600">Zlecenia</a>
          <span>/</span>
          <span className="text-gray-900">{job.job_id.substring(0, 8)}</span>
        </div>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                {job.job_type.replace("_", " ").toUpperCase()}
              </h1>
              {getStatusBadge(job.status)}
            </div>
            <p className="text-gray-600">{job.user_inspiration}</p>
          </div>
          <div className="flex gap-3">
            {job.status === "pending" && (
              <button
                onClick={handleStartPipeline}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
              >
                Uruchom Pipeline
              </button>
            )}
            {job.status !== "completed" && job.status !== "cancelled" && (
              <button
                onClick={handleCancelJob}
                className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
              >
                Anuluj
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Gatunek</div>
          <div className="text-xl font-semibold text-gray-900 capitalize">
            {job.genre}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Cel Słów</div>
          <div className="text-xl font-semibold text-gray-900">
            {job.target_word_count.toLocaleString()}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Postęp</div>
          <div className="text-xl font-semibold text-gray-900">{job.progress}%</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Koszt</div>
          <div className="text-xl font-semibold text-gray-900">
            ${(job.current_cost ?? 0).toFixed(3)} / ${job.budget_limit.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Pipeline Visualization */}
      {pipeline && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pipeline Status</h2>
          <div className="grid grid-cols-9 gap-2 mb-4">
            {pipelineStages.map((stage) => {
              const isCompleted = pipeline.completed_stages.includes(stage.name as any);
              const isCurrent = pipeline.current_stage === stage.name;

              return (
                <div key={stage.name} className="text-center">
                  <div
                    className={`${
                      isCompleted
                        ? stage.color + " text-white"
                        : isCurrent
                        ? stage.color + " text-white animate-pulse"
                        : "bg-gray-200 text-gray-500"
                    } rounded-lg py-3 px-1 mb-2 font-medium text-xs`}
                  >
                    {isCompleted ? "✓" : isCurrent ? "..." : ""}
                  </div>
                  <div className="text-xs text-gray-600 font-medium">
                    {stage.label}
                  </div>
                </div>
              );
            })}
          </div>
          {pipeline.current_stage && (
            <div className="text-sm text-gray-600 text-center">
              Aktualny etap: <span className="font-semibold">{pipeline.current_stage}</span>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {[
            { key: "overview", label: "Przegląd" },
            { key: "artifacts", label: `Artefakty (${artifacts.length})` },
            { key: "costs", label: `Koszty (${costs.length})` },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`pb-3 px-1 font-medium text-sm border-b-2 transition-colors ${
                activeTab === tab.key
                  ? "border-primary-600 text-primary-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Szczegóły Zlecenia</h3>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-gray-600 mb-1">ID Zlecenia</dt>
                <dd className="font-mono text-gray-900">{job.job_id}</dd>
              </div>
              <div>
                <dt className="text-gray-600 mb-1">Utworzono</dt>
                <dd className="text-gray-900">
                  {format(new Date(job.created_at), "dd MMM yyyy HH:mm")}
                </dd>
              </div>
              <div>
                <dt className="text-gray-600 mb-1">Zaktualizowano</dt>
                <dd className="text-gray-900">
                  {format(new Date(job.updated_at), "dd MMM yyyy HH:mm")}
                </dd>
              </div>
              {job.completed_at && (
                <div>
                  <dt className="text-gray-600 mb-1">Zakończono</dt>
                  <dd className="text-gray-900">
                    {format(new Date(job.completed_at), "dd MMM yyyy HH:mm")}
                  </dd>
                </div>
              )}
            </dl>
          </div>

          {job.error_message && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-red-900 mb-2">Błąd</h4>
              <p className="text-sm text-red-700">{job.error_message}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "artifacts" && (
        <div className="space-y-4">
          {artifacts.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <p className="text-gray-600">Brak artefaktów</p>
            </div>
          ) : (
            artifacts.map((artifact) => (
              <div
                key={artifact.artifact_id}
                className="bg-white rounded-lg border border-gray-200 p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-900">{artifact.type}</h4>
                    <p className="text-xs text-gray-500 font-mono">
                      {artifact.artifact_id.substring(0, 12)}...
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">v{artifact.version}</span>
                </div>
                <div className="text-sm text-gray-600">
                  <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-64">
                    {JSON.stringify(artifact.data, null, 2)}
                  </pre>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === "costs" && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {costs.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-600">Brak danych o kosztach</p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Agent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Model
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Tokeny In
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Tokeny Out
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Koszt (USD)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Czas
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {costs.map((cost) => (
                  <tr key={cost.snapshot_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {cost.agent_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {cost.model}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">
                      {cost.tokens_input.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">
                      {cost.tokens_output.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                      ${cost.cost_usd.toFixed(4)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {format(new Date(cost.created_at), "HH:mm:ss")}
                    </td>
                  </tr>
                ))}
                <tr className="bg-gray-50 font-semibold">
                  <td colSpan={4} className="px-6 py-4 text-sm text-gray-900 text-right">
                    RAZEM:
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">
                    ${costs.reduce((sum, c) => sum + c.cost_usd, 0).toFixed(4)}
                  </td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
