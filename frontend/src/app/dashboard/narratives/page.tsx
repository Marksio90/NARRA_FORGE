"use client";

import { useState } from "react";
import Link from "next/link";
import { useNarratives } from "@/hooks/useNarratives";
import { useProjects } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import type { Narrative } from "@/types/api";

export default function NarrativesPage() {
  const [projectFilter, setProjectFilter] = useState<string>("");
  const [genreFilter, setGenreFilter] = useState<string>("");
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedNarrative, setSelectedNarrative] = useState<Narrative | null>(null);

  const { projects } = useProjects({ pageSize: 100 });

  const {
    narratives,
    total,
    currentPage,
    totalPages,
    loading,
    error,
    fetchNarratives,
    deleteNarrative,
  } = useNarratives({
    projectId: projectFilter || undefined,
    genre: genreFilter || undefined,
  });

  const handleDeleteClick = (narrative: Narrative) => {
    setSelectedNarrative(narrative);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedNarrative) return;

    try {
      await deleteNarrative(selectedNarrative.id);
      setIsDeleteDialogOpen(false);
    } catch (err) {
      console.error("Failed to delete narrative:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Narratives</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            View and manage your generated narratives
          </p>
        </div>
        <Link href="/dashboard/generate">
          <Button>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Generate New
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="w-64">
          <Select value={projectFilter} onValueChange={setProjectFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All Projects" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Projects</SelectItem>
              {projects.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
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

      {/* Narratives Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading narratives...</p>
        </div>
      ) : narratives.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <svg className="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No narratives yet</h3>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Generate your first narrative to see it here
          </p>
          <Link href="/dashboard/generate">
            <Button className="mt-6">Generate Narrative</Button>
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {narratives.map((narrative) => (
              <div
                key={narrative.id}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {narrative.title || `Narrative #${narrative.id.slice(0, 8)}`}
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {narrative.genre && (
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                          {narrative.genre}
                        </span>
                      )}
                      {narrative.production_type && (
                        <span className="px-2 py-1 text-xs rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
                          {narrative.production_type}
                        </span>
                      )}
                      <span className="px-2 py-1 text-xs rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300">
                        {narrative.quality_score ? `${(narrative.quality_score * 100).toFixed(0)}% Quality` : "Generated"}
                      </span>
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteClick(narrative)}
                    className="text-red-600 hover:text-red-700 dark:text-red-400"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </Button>
                </div>

                {narrative.summary && (
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                    {narrative.summary}
                  </p>
                )}

                <div className="grid grid-cols-3 gap-4 mb-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Word Count</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {narrative.word_count?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Views</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {narrative.view_count || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Cost</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      ${narrative.generation_cost_usd?.toFixed(2) || "0.00"}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Link href={`/dashboard/narratives/${narrative.id}`} className="flex-1">
                    <Button variant="outline" className="w-full">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      View
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      try {
                        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/narratives/${narrative.id}/text`, {
                          headers: {
                            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                          },
                        });
                        const data = await response.json();
                        const blob = new Blob([data.full_text], { type: "text/plain" });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `${narrative.title || narrative.id}.txt`;
                        a.click();
                      } catch (err) {
                        console.error("Failed to download narrative:", err);
                      }
                    }}
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download
                  </Button>
                </div>

                <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
                  Created {new Date(narrative.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {narratives.length} of {total} narratives
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => fetchNarratives(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={() => fetchNarratives(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Narrative</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this narrative? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm} className="bg-red-600 hover:bg-red-700">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
