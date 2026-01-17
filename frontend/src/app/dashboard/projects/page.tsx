"use client";

import { useState } from "react";
import { useProjects } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
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
import type { Project } from "@/types/api";

export default function ProjectsPage() {
  const {
    projects,
    total,
    currentPage,
    totalPages,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
  } = useProjects();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    default_genre: "",
    default_production_type: "",
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const handleCreateClick = () => {
    setFormData({ name: "", description: "", default_genre: "", default_production_type: "" });
    setFormError(null);
    setIsCreateDialogOpen(true);
  };

  const handleEditClick = (project: Project) => {
    setSelectedProject(project);
    setFormData({
      name: project.name,
      description: project.description || "",
      default_genre: project.default_genre || "",
      default_production_type: project.default_production_type || "",
    });
    setFormError(null);
    setIsEditDialogOpen(true);
  };

  const handleDeleteClick = (project: Project) => {
    setSelectedProject(project);
    setIsDeleteDialogOpen(true);
  };

  const handleCreateSubmit = async () => {
    if (!formData.name.trim()) {
      setFormError("Project name is required");
      return;
    }

    setFormLoading(true);
    setFormError(null);

    try {
      await createProject({
        name: formData.name,
        description: formData.description || undefined,
        default_genre: formData.default_genre || undefined,
        default_production_type: formData.default_production_type || undefined,
      });
      setIsCreateDialogOpen(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditSubmit = async () => {
    if (!selectedProject || !formData.name.trim()) {
      setFormError("Project name is required");
      return;
    }

    setFormLoading(true);
    setFormError(null);

    try {
      await updateProject(selectedProject.id, {
        name: formData.name,
        description: formData.description || undefined,
        default_genre: formData.default_genre || undefined,
        default_production_type: formData.default_production_type || undefined,
      });
      setIsEditDialogOpen(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to update project");
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedProject) return;

    try {
      await deleteProject(selectedProject.id);
      setIsDeleteDialogOpen(false);
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your narrative projects and workspaces
          </p>
        </div>
        <Button onClick={handleCreateClick}>
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Project
        </Button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Projects Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading projects...</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <svg className="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No projects yet</h3>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Get started by creating your first project
          </p>
          <Button onClick={handleCreateClick} className="mt-6">
            Create Project
          </Button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {project.name}
                  </h3>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEditClick(project)}
                      className="h-8 w-8"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteClick(project)}
                      className="h-8 w-8 text-red-600 hover:text-red-700 dark:text-red-400"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
                  </div>
                </div>

                {project.description && (
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                    {project.description}
                  </p>
                )}

                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Narratives</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {project.narrative_count}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Words</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {project.total_word_count.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Cost</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      ${project.total_cost_usd.toFixed(2)}
                    </p>
                  </div>
                </div>

                {(project.default_genre || project.default_production_type) && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    {project.default_genre && (
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                        {project.default_genre}
                      </span>
                    )}
                    {project.default_production_type && (
                      <span className="px-2 py-1 text-xs rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
                        {project.default_production_type}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {projects.length} of {total} projects
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => fetchProjects(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={() => fetchProjects(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create Project Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
            <DialogDescription>
              Create a workspace to organize your narratives
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Project Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="My Awesome Project"
                disabled={formLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of your project..."
                disabled={formLoading}
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="genre">Default Genre</Label>
              <Input
                id="genre"
                value={formData.default_genre}
                onChange={(e) => setFormData({ ...formData, default_genre: e.target.value })}
                placeholder="e.g., Science Fiction, Fantasy"
                disabled={formLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="production_type">Default Production Type</Label>
              <Input
                id="production_type"
                value={formData.default_production_type}
                onChange={(e) => setFormData({ ...formData, default_production_type: e.target.value })}
                placeholder="e.g., Film, Novel, Series"
                disabled={formLoading}
              />
            </div>
            {formError && (
              <div className="text-sm text-red-600 dark:text-red-400">{formError}</div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)} disabled={formLoading}>
              Cancel
            </Button>
            <Button onClick={handleCreateSubmit} disabled={formLoading}>
              {formLoading ? "Creating..." : "Create Project"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Project Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
            <DialogDescription>
              Update your project details
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Project Name *</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="My Awesome Project"
                disabled={formLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of your project..."
                disabled={formLoading}
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-genre">Default Genre</Label>
              <Input
                id="edit-genre"
                value={formData.default_genre}
                onChange={(e) => setFormData({ ...formData, default_genre: e.target.value })}
                placeholder="e.g., Science Fiction, Fantasy"
                disabled={formLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-production_type">Default Production Type</Label>
              <Input
                id="edit-production_type"
                value={formData.default_production_type}
                onChange={(e) => setFormData({ ...formData, default_production_type: e.target.value })}
                placeholder="e.g., Film, Novel, Series"
                disabled={formLoading}
              />
            </div>
            {formError && (
              <div className="text-sm text-red-600 dark:text-red-400">{formError}</div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)} disabled={formLoading}>
              Cancel
            </Button>
            <Button onClick={handleEditSubmit} disabled={formLoading}>
              {formLoading ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{selectedProject?.name}"? This will permanently
              delete all narratives and jobs associated with this project. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm} className="bg-red-600 hover:bg-red-700">
              Delete Project
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
