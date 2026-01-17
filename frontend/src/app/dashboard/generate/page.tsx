"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useProjects } from "@/hooks/useProjects";
import { useJobs } from "@/hooks/useJobs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Step = 1 | 2 | 3 | 4;

interface ProductionBrief {
  genre?: string;
  production_type?: string;
  target_length?: number;
  target_audience?: string;
  tone?: string;
  themes?: string;
  characters?: string;
  setting?: string;
  plot_outline?: string;
  special_requirements?: string;
}

export default function GeneratePage() {
  const router = useRouter();
  const { projects, loading: projectsLoading } = useProjects({ autoFetch: true });
  const { createJob } = useJobs({ autoFetch: false });

  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [productionBrief, setProductionBrief] = useState<ProductionBrief>({
    genre: "",
    production_type: "",
    target_length: 5000,
    target_audience: "",
    tone: "",
    themes: "",
    characters: "",
    setting: "",
    plot_outline: "",
    special_requirements: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateBrief = (field: keyof ProductionBrief, value: string | number) => {
    setProductionBrief((prev) => ({ ...prev, [field]: value }));
  };

  const canProceedToStep2 = selectedProjectId !== "";
  const canProceedToStep3 =
    productionBrief.genre && productionBrief.production_type && productionBrief.target_length;
  const canProceedToStep4 = productionBrief.plot_outline && productionBrief.plot_outline.length > 50;

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => (prev + 1) as Step);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as Step);
    }
  };

  const handleSubmit = async () => {
    if (!selectedProjectId) {
      setError("Please select a project");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Filter out empty fields
      const cleanedBrief = Object.entries(productionBrief).reduce((acc, [key, value]) => {
        if (value !== "" && value !== undefined) {
          acc[key] = value;
        }
        return acc;
      }, {} as Record<string, any>);

      const job = await createJob({
        project_id: selectedProjectId,
        production_brief: cleanedBrief,
      });

      // Redirect to job progress page
      router.push(`/dashboard/jobs/${job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generate Story</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Create a new narrative using AI-powered generation
        </p>
      </div>

      {/* Progress Steps */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4].map((step, idx) => (
            <div key={step} className="flex items-center flex-1">
              <div className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    currentStep >= step
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                  }`}
                >
                  {step}
                </div>
                <div className="ml-3">
                  <p
                    className={`text-sm font-medium ${
                      currentStep >= step
                        ? "text-gray-900 dark:text-white"
                        : "text-gray-500 dark:text-gray-400"
                    }`}
                  >
                    {step === 1 && "Project"}
                    {step === 2 && "Basic Info"}
                    {step === 3 && "Details"}
                    {step === 4 && "Review"}
                  </p>
                </div>
              </div>
              {idx < 3 && (
                <div
                  className={`flex-1 h-1 mx-4 ${
                    currentStep > step
                      ? "bg-blue-600"
                      : "bg-gray-200 dark:bg-gray-700"
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Step Content */}
      <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700">
        {/* Step 1: Select Project */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Select Project
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Choose which project this narrative belongs to
              </p>
            </div>

            {projectsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Loading projects...</p>
              </div>
            ) : projects.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  You need to create a project first
                </p>
                <Button onClick={() => router.push("/dashboard/projects")}>
                  Go to Projects
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => setSelectedProjectId(project.id)}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${
                      selectedProjectId === project.id
                        ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20"
                        : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                    }`}
                  >
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {project.name}
                    </h3>
                    {project.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {project.description}
                      </p>
                    )}
                    <div className="flex gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                      <span>{project.narrative_count} narratives</span>
                      {project.default_genre && <span>• {project.default_genre}</span>}
                      {project.default_production_type && (
                        <span>• {project.default_production_type}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Basic Info */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Basic Information
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Set the genre, production type, and target length
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="genre">Genre *</Label>
                <Input
                  id="genre"
                  value={productionBrief.genre}
                  onChange={(e) => updateBrief("genre", e.target.value)}
                  placeholder="e.g., Science Fiction, Fantasy, Drama"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="production_type">Production Type *</Label>
                <Select
                  value={productionBrief.production_type}
                  onValueChange={(value) => updateBrief("production_type", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="film">Film</SelectItem>
                    <SelectItem value="series">TV Series</SelectItem>
                    <SelectItem value="novel">Novel</SelectItem>
                    <SelectItem value="short_story">Short Story</SelectItem>
                    <SelectItem value="game">Video Game</SelectItem>
                    <SelectItem value="podcast">Podcast</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="target_length">Target Length (words) *</Label>
                <Input
                  id="target_length"
                  type="number"
                  value={productionBrief.target_length}
                  onChange={(e) => updateBrief("target_length", parseInt(e.target.value))}
                  min={100}
                  max={50000}
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Recommended: 2,000-10,000 words
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="target_audience">Target Audience</Label>
                <Input
                  id="target_audience"
                  value={productionBrief.target_audience}
                  onChange={(e) => updateBrief("target_audience", e.target.value)}
                  placeholder="e.g., Young Adults, General Audience"
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="tone">Tone</Label>
                <Input
                  id="tone"
                  value={productionBrief.tone}
                  onChange={(e) => updateBrief("tone", e.target.value)}
                  placeholder="e.g., Dark, Humorous, Suspenseful"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Production Details */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Production Details
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Provide details about characters, setting, and plot
              </p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="themes">Themes</Label>
                <Input
                  id="themes"
                  value={productionBrief.themes}
                  onChange={(e) => updateBrief("themes", e.target.value)}
                  placeholder="e.g., Love, Betrayal, Redemption"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="setting">Setting</Label>
                <Textarea
                  id="setting"
                  value={productionBrief.setting}
                  onChange={(e) => updateBrief("setting", e.target.value)}
                  placeholder="Describe the time period, location, and world..."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="characters">Main Characters</Label>
                <Textarea
                  id="characters"
                  value={productionBrief.characters}
                  onChange={(e) => updateBrief("characters", e.target.value)}
                  placeholder="Describe the main characters, their traits, and motivations..."
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="plot_outline">Plot Outline *</Label>
                <Textarea
                  id="plot_outline"
                  value={productionBrief.plot_outline}
                  onChange={(e) => updateBrief("plot_outline", e.target.value)}
                  placeholder="Provide a brief outline of the story arc, key events, and resolution... (minimum 50 characters)"
                  rows={6}
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {productionBrief.plot_outline?.length || 0} characters (minimum 50)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="special_requirements">Special Requirements</Label>
                <Textarea
                  id="special_requirements"
                  value={productionBrief.special_requirements}
                  onChange={(e) => updateBrief("special_requirements", e.target.value)}
                  placeholder="Any specific requirements or constraints..."
                  rows={3}
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Review & Submit */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Review & Submit
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Review your settings before submitting
              </p>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Project</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {projects.find((p) => p.id === selectedProjectId)?.name}
                </p>
              </div>

              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Production Brief
                </h3>
                <dl className="grid grid-cols-2 gap-3 text-sm">
                  {Object.entries(productionBrief)
                    .filter(([_, value]) => value)
                    .map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-gray-500 dark:text-gray-400 capitalize">
                          {key.replace(/_/g, " ")}
                        </dt>
                        <dd className="text-gray-900 dark:text-white mt-1">
                          {typeof value === "string" && value.length > 100
                            ? value.substring(0, 100) + "..."
                            : String(value)}
                        </dd>
                      </div>
                    ))}
                </dl>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  <strong>Estimated cost:</strong> $
                  {((productionBrief.target_length || 5000) / 1000 * 0.05).toFixed(2)}
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  Generation may take several minutes depending on complexity
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1 || loading}
        >
          Back
        </Button>

        <div className="flex gap-2">
          {currentStep < 4 ? (
            <Button
              onClick={handleNext}
              disabled={
                (currentStep === 1 && !canProceedToStep2) ||
                (currentStep === 2 && !canProceedToStep3) ||
                (currentStep === 3 && !canProceedToStep4)
              }
            >
              Next
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Creating Job..." : "Submit & Generate"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
