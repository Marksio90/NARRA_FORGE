
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useProjects } from "@/hooks/useProjects";
import { useJobs } from "@/hooks/useJobs";
import { ProductionBrief, ProductionType, Genre } from "@/types/api";
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

export default function GeneratePage() {
  const router = useRouter();
  const { projects, loading: projectsLoading } = useProjects({ autoFetch: true });
  const { createJob } = useJobs({ autoFetch: false });

  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [productionBrief, setProductionBrief] = useState<Partial<ProductionBrief>>({
    genre: undefined,
    production_type: undefined,
    subject: "",
    target_length: 5000,
    style_instructions: "",
    character_count: 3,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateBrief = <K extends keyof ProductionBrief>(field: K, value: ProductionBrief[K]) => {
    setProductionBrief((prev) => ({ ...prev, [field]: value }));
  };

  const canProceedToStep2 = selectedProjectId !== "";
  const canProceedToStep3 =
    productionBrief.genre && productionBrief.production_type && productionBrief.target_length;
  const canProceedToStep4 = productionBrief.subject && productionBrief.subject.length > 20;

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

    if (!productionBrief.production_type || !productionBrief.genre || !productionBrief.subject || !productionBrief.target_length) {
      setError("Please fill in all required fields");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const finalBrief: ProductionBrief = {
        production_type: productionBrief.production_type as ProductionType,
        genre: productionBrief.genre as Genre,
        subject: productionBrief.subject,
        target_length: productionBrief.target_length,
        style_instructions: productionBrief.style_instructions,
        character_count: productionBrief.character_count,
      };

      const job = await createJob({
        project_id: selectedProjectId,
        production_brief: finalBrief,
      });

      router.push("/dashboard/jobs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generate Narrative</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Create a new narrative using AI-powered generation
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-6">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  currentStep >= step
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                }`}
              >
                {step}
              </div>
              {step < 4 && (
                <div
                  className={`w-16 h-1 mx-2 ${
                    currentStep > step ? "bg-blue-600" : "bg-gray-200 dark:bg-gray-700"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

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
              <p className="text-gray-600 dark:text-gray-400">Loading projects...</p>
            ) : (
              <div className="grid gap-4">
                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => setSelectedProjectId(project.id)}
                    className={`text-left p-4 rounded-lg border-2 transition-colors ${
                      selectedProjectId === project.id
                        ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20"
                        : "border-gray-200 dark:border-gray-700 hover:border-blue-400"
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
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

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
                <Select
                  value={productionBrief.genre}
                  onValueChange={(value) => updateBrief("genre", value as Genre)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select genre" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={Genre.FANTASY}>Fantasy</SelectItem>
                    <SelectItem value={Genre.SCI_FI}>Science Fiction</SelectItem>
                    <SelectItem value={Genre.HORROR}>Horror</SelectItem>
                    <SelectItem value={Genre.THRILLER}>Thriller</SelectItem>
                    <SelectItem value={Genre.MYSTERY}>Mystery</SelectItem>
                    <SelectItem value={Genre.DRAMA}>Drama</SelectItem>
                    <SelectItem value={Genre.ROMANCE}>Romance</SelectItem>
                    <SelectItem value={Genre.HYBRID}>Hybrid</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="production_type">Production Type *</Label>
                <Select
                  value={productionBrief.production_type}
                  onValueChange={(value) => updateBrief("production_type", value as ProductionType)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ProductionType.SHORT_STORY}>Short Story (5k-10k)</SelectItem>
                    <SelectItem value={ProductionType.NOVELLA}>Novella (10k-40k)</SelectItem>
                    <SelectItem value={ProductionType.NOVEL}>Novel (40k-120k)</SelectItem>
                    <SelectItem value={ProductionType.EPIC_SAGA}>Epic Saga (120k+)</SelectItem>
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
                  max={150000}
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Recommended: 5,000-50,000 words
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="character_count">Number of Main Characters</Label>
                <Input
                  id="character_count"
                  type="number"
                  value={productionBrief.character_count || 3}
                  onChange={(e) => updateBrief("character_count", parseInt(e.target.value))}
                  min={1}
                  max={10}
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Optional: 1-10 characters
                </p>
              </div>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Story Details
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Describe what you want your narrative to be about
              </p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="subject">Story Subject / Plot *</Label>
                <Textarea
                  id="subject"
                  value={productionBrief.subject}
                  onChange={(e) => updateBrief("subject", e.target.value)}
                  placeholder="Describe the main story, plot points, characters, setting, and what you want to happen... (minimum 20 characters)"
                  rows={8}
                  className="resize-none"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {productionBrief.subject?.length || 0} characters (minimum 20)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="style_instructions">Style Instructions (Optional)</Label>
                <Textarea
                  id="style_instructions"
                  value={productionBrief.style_instructions}
                  onChange={(e) => updateBrief("style_instructions", e.target.value)}
                  placeholder="Specify writing style, tone, perspective, or any special instructions..."
                  rows={4}
                  className="resize-none"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Example: "Write in first person, dark tone, literary style"
                </p>
              </div>
            </div>
          </div>
        )}

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
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-gray-500 dark:text-gray-400">Genre</dt>
                    <dd className="text-gray-900 dark:text-white mt-1">{productionBrief.genre}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500 dark:text-gray-400">Production Type</dt>
                    <dd className="text-gray-900 dark:text-white mt-1">{productionBrief.production_type}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500 dark:text-gray-400">Target Length</dt>
                    <dd className="text-gray-900 dark:text-white mt-1">{productionBrief.target_length} words</dd>
                  </div>
                  {productionBrief.character_count && (
                    <div>
                      <dt className="text-gray-500 dark:text-gray-400">Main Characters</dt>
                      <dd className="text-gray-900 dark:text-white mt-1">{productionBrief.character_count}</dd>
                    </div>
                  )}
                  <div>
                    <dt className="text-gray-500 dark:text-gray-400">Subject</dt>
                    <dd className="text-gray-900 dark:text-white mt-1">
                      {productionBrief.subject && productionBrief.subject.length > 200
                        ? productionBrief.subject.substring(0, 200) + "..."
                        : productionBrief.subject}
                    </dd>
                  </div>
                  {productionBrief.style_instructions && (
                    <div>
                      <dt className="text-gray-500 dark:text-gray-400">Style Instructions</dt>
                      <dd className="text-gray-900 dark:text-white mt-1">{productionBrief.style_instructions}</dd>
                    </div>
                  )}
                </dl>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  ⚡ Your narrative will be generated asynchronously. You can track progress in the Jobs page.
                </p>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
              </div>
            )}
          </div>
        )}

        <div className="flex justify-between mt-8">
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
              <Button
                onClick={handleSubmit}
                disabled={loading || !canProceedToStep4}
              >
                {loading ? "Submitting..." : "Submit"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
