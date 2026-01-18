"use client";

import { useState } from "react";
import Link from "next/link";
import { useJobs } from "@/hooks/useJobs";
import { JobStatus } from "@/types/api";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState<string>("");

  const {
    jobs,
    total,
    currentPage,
    totalPages,
    loading,
    error,
    fetchJobs,
    cancelJob,
  } = useJobs({
    status: statusFilter || undefined,
    pollInterval: 5000, // Poll every 5 seconds for updates
  });

  const handleCancelJob = async (jobId: string) => {
    if (confirm("Are you sure you want to cancel this job?")) {
      try {
        await cancelJob(jobId);
      } catch (err) {
        console.error("Failed to cancel job:", err);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300";
      case "RUNNING":
        return "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300";
      case "QUEUED":
        return "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300";
      case "FAILED":
        return "bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300";
      case "CANCELLED":
        return "bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generation Jobs</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor and manage your narrative generation jobs
          </p>
        </div>
        <Link href="/dashboard/generate">
          <Button>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Job
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="w-48">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Statuses</SelectItem>
              <SelectItem value="QUEUED">Queued</SelectItem>
              <SelectItem value="RUNNING">Running</SelectItem>
              <SelectItem value="COMPLETED">Completed</SelectItem>
              <SelectItem value="FAILED">Failed</SelectItem>
              <SelectItem value="CANCELLED">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Jobs List */}
      {loading && jobs.length === 0 ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <svg className="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No jobs yet</h3>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Start generating narratives to see them here
          </p>
          <Link href="/dashboard/generate">
            <Button className="mt-6">Create Your First Job</Button>
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {jobs.map((job) => (
              <Link
                key={job.id}
                href={`/dashboard/jobs/${job.id}`}
                className="block bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Job #{job.id.slice(0, 8)}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Created {new Date(job.created_at).toLocaleString()}
                    </p>
                  </div>

                  {(job.status === JobStatus.QUEUED || job.status === JobStatus.RUNNING) && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.preventDefault();
                        handleCancelJob(job.id);
                      }}
                      className="text-red-600 hover:text-red-700"
                    >
                      Cancel
                    </Button>
                  )}
                </div>

                {/* Progress Bar */}
                {(job.status === JobStatus.RUNNING || job.status === JobStatus.QUEUED) && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-600 dark:text-gray-400">
                        {job.current_stage || "Initializing..."}
                      </span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {job.progress_percentage?.toFixed(0) || 0}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${job.progress_percentage || 0}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Job Details */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Target Length</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {job.production_brief?.target_length?.toLocaleString() || "N/A"} words
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Genre</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {job.production_brief?.genre || "N/A"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Estimated Cost</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      ${job.estimated_cost_usd?.toFixed(2) || "0.00"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Actual Cost</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      ${job.actual_cost_usd?.toFixed(2) || "0.00"}
                    </p>
                  </div>
                </div>

                {/* Error Message */}
                {job.status === JobStatus.FAILED && job.error_message && (
                  <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-sm text-red-600 dark:text-red-400">{job.error_message}</p>
                  </div>
                )}
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {jobs.length} of {total} jobs
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => fetchJobs(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={() => fetchJobs(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
