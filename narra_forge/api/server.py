"""
FastAPI Server dla NARRA_FORGE
Zapewnia REST API do generacji narracji.
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from ..core.orchestrator import NarrativeOrchestrator
from ..core.config import get_default_config
from ..core.types import ProductionStage, PipelineStage
from ..core.revision import RevisionRequest as CoreRevisionRequest
from ..models.backend import ModelOrchestrator
from ..models.openai_backend import OpenAIBackend
from ..models.anthropic_backend import AnthropicBackend
from ..memory.base import SQLiteMemorySystem

# ============================================================================
# MODELS
# ============================================================================

class GenerationRequest(BaseModel):
    """Żądanie generacji narracji."""
    brief: str
    form: str = "short_story"  # short_story, novella, novel, epic
    genre: str = "sci_fi"
    world_scale: str = "intimate"
    thematic_focus: List[str] = ["survival", "morality"]
    expansion_potential: str = "standalone"

    # Opcjonalne parametry
    preferred_model: Optional[str] = None
    temperature: Optional[float] = None


class GenerationResponse(BaseModel):
    """Odpowiedź na żądanie generacji."""
    project_id: str
    status: str  # "queued", "processing", "completed", "failed"
    message: str
    status_url: str
    websocket_url: str


class ProjectStatus(BaseModel):
    """Status projektu generacji."""
    project_id: str
    status: str
    current_stage: Optional[str] = None
    progress: float  # 0.0-1.0
    stages_completed: List[str]
    stages_failed: List[str]
    estimated_time_remaining: Optional[int] = None  # seconds
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_files: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None


class RevisionRequest(BaseModel):
    """Żądanie rewizji narracji."""
    project_id: str
    from_stage: str  # Nazwa etapu: "SEQUENTIAL_GENERATION", "COHERENCE_CONTROL", etc.
    instructions: Optional[str] = None
    context_modifications: Optional[Dict[str, Any]] = None
    create_new_version: bool = True


class RevisionResponse(BaseModel):
    """Odpowiedź na żądanie rewizji."""
    project_id: str
    version: int
    status: str
    message: str
    status_url: str


class VersionInfo(BaseModel):
    """Informacje o wersji projektu."""
    version: int
    stages: List[Dict[str, Any]]
    created_at: str


class ExportRequest(BaseModel):
    """Żądanie exportu narracji."""
    project_id: str
    format: str  # "epub" or "pdf"
    version: Optional[int] = None  # Która wersja (domyślnie: najnowsza)
    metadata: Optional[Dict[str, str]] = None  # Dodatkowe metadane (title, author, etc.)
    include_toc: bool = False  # Tylko dla PDF: czy dodać spis treści


class ExportResponse(BaseModel):
    """Odpowiedź na żądanie exportu."""
    success: bool
    message: str
    file_id: Optional[str] = None
    download_url: Optional[str] = None
    format: str
    file_size: Optional[int] = None


# ============================================================================
# APPLICATION
# ============================================================================

app = FastAPI(
    title="NARRA_FORGE API",
    description="Autonomiczny Wieloświatowy System Generowania Narracji",
    version="1.0.0"
)

# CORS dla frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL STATE
# ============================================================================

# Przechowywanie aktywnych projektów
active_projects: Dict[str, Dict[str, Any]] = {}

# WebSocket connections per project
websocket_connections: Dict[str, List[WebSocket]] = {}

# Orchestrator (inicjalizowany przy starcie)
orchestrator: Optional[NarrativeOrchestrator] = None


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicjalizacja przy starcie serwera."""
    global orchestrator

    print("🚀 Inicjalizacja NARRA_FORGE API...")

    # Załaduj konfigurację
    config = get_default_config()

    # Inicjalizuj backendy
    backends = {}

    for model_name, model_config in config.models.items():
        if model_config.provider == "openai":
            backends[model_name] = OpenAIBackend(model_config.__dict__)
        elif model_config.provider == "anthropic":
            backends[model_name] = AnthropicBackend(model_config.__dict__)

    model_orchestrator = ModelOrchestrator(
        backends=backends,
        default=config.default_model
    )

    # Inicjalizuj system pamięci
    memory_system = SQLiteMemorySystem("data/narra_forge.db")

    # Stwórz orchestrator
    orchestrator = NarrativeOrchestrator(
        config=config,
        model_orchestrator=model_orchestrator,
        memory_system=memory_system
    )

    print("✅ NARRA_FORGE API gotowe!")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "NARRA_FORGE API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "generate": "/api/generate",
            "status": "/api/status/{project_id}",
            "projects": "/api/projects",
            "ws": "/ws/{project_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_projects": len(active_projects)
    }


@app.post("/api/generate", response_model=GenerationResponse)
async def generate_narrative(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Rozpocznij generację narracji.

    Proces działa w tle, użyj /api/status/{project_id} lub WebSocket
    do śledzenia postępu.
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="System nie jest gotowy. Spróbuj ponownie za chwilę."
        )

    # Wygeneruj ID projektu
    project_id = str(uuid.uuid4())

    # Zapisz projekt w stanie
    active_projects[project_id] = {
        "id": project_id,
        "status": "queued",
        "request": request.dict(),
        "progress": 0.0,
        "stages_completed": [],
        "stages_failed": [],
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "current_stage": None,
        "output_files": None,
        "metadata": {},
        "error": None
    }

    # Uruchom generację w tle
    background_tasks.add_task(
        run_generation,
        project_id=project_id,
        request=request
    )

    return GenerationResponse(
        project_id=project_id,
        status="queued",
        message="Projekt dodany do kolejki. Generacja rozpocznie się wkrótce.",
        status_url=f"/api/status/{project_id}",
        websocket_url=f"/ws/{project_id}"
    )


@app.get("/api/status/{project_id}", response_model=ProjectStatus)
async def get_project_status(project_id: str):
    """Pobierz status projektu generacji."""
    if project_id not in active_projects:
        raise HTTPException(
            status_code=404,
            detail=f"Projekt {project_id} nie istnieje"
        )

    project = active_projects[project_id]

    # Oblicz postęp
    total_stages = 10
    completed = len(project["stages_completed"])
    progress = completed / total_stages if total_stages > 0 else 0.0

    return ProjectStatus(
        project_id=project_id,
        status=project["status"],
        current_stage=project.get("current_stage"),
        progress=progress,
        stages_completed=project["stages_completed"],
        stages_failed=project["stages_failed"],
        estimated_time_remaining=None,  # TODO: implement
        created_at=project["created_at"],
        started_at=project.get("started_at"),
        completed_at=project.get("completed_at"),
        output_files=project.get("output_files"),
        metadata=project.get("metadata", {}),
        error=project.get("error")
    )


@app.get("/api/projects")
async def list_projects(
    status: Optional[str] = None,
    limit: int = 50
):
    """Lista wszystkich projektów."""
    projects = list(active_projects.values())

    # Filtruj po statusie jeśli podano
    if status:
        projects = [p for p in projects if p["status"] == status]

    # Sortuj po dacie utworzenia (najnowsze pierwsze)
    projects.sort(key=lambda p: p["created_at"], reverse=True)

    # Limituj
    projects = projects[:limit]

    return {
        "total": len(projects),
        "projects": projects
    }


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Usuń projekt."""
    if project_id not in active_projects:
        raise HTTPException(
            status_code=404,
            detail=f"Projekt {project_id} nie istnieje"
        )

    # Nie można usunąć projektów w trakcie przetwarzania
    if active_projects[project_id]["status"] == "processing":
        raise HTTPException(
            status_code=400,
            detail="Nie można usunąć projektu w trakcie przetwarzania"
        )

    del active_projects[project_id]

    return {"message": f"Projekt {project_id} usunięty"}


@app.post("/api/revise", response_model=RevisionResponse)
async def revise_narrative(
    request: RevisionRequest,
    background_tasks: BackgroundTasks
):
    """
    Rewizja i regeneracja narracji od wybranego etapu.

    Umożliwia poprawienie wygenerowanej narracji poprzez:
    - Regenerację od wybranego etapu
    - Dodanie instrukcji rewizji
    - Modyfikację kontekstu
    - Utworzenie nowej wersji lub nadpisanie istniejącej
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="System nie jest gotowy"
        )

    # Sprawdź czy projekt istnieje
    if request.project_id not in active_projects:
        raise HTTPException(
            status_code=404,
            detail=f"Projekt {request.project_id} nie istnieje"
        )

    # Nie można rewizować projektu w trakcie przetwarzania
    if active_projects[request.project_id]["status"] == "processing":
        raise HTTPException(
            status_code=400,
            detail="Nie można rewizować projektu w trakcie przetwarzania"
        )

    # Konwertuj nazwę etapu na PipelineStage
    try:
        from_stage = PipelineStage[request.from_stage]
    except KeyError:
        valid_stages = [stage.name for stage in PipelineStage]
        raise HTTPException(
            status_code=400,
            detail=f"Nieprawidłowy etap: {request.from_stage}. Dozwolone: {valid_stages}"
        )

    # Utwórz core RevisionRequest
    core_request = CoreRevisionRequest(
        project_id=request.project_id,
        from_stage=from_stage,
        instructions=request.instructions,
        context_modifications=request.context_modifications,
        create_new_version=request.create_new_version
    )

    # Określ numer wersji
    version = orchestrator.revision_system.get_latest_version(request.project_id)
    if request.create_new_version:
        version += 1

    # Zaktualizuj status projektu
    active_projects[request.project_id]["status"] = "queued"
    active_projects[request.project_id]["revision_version"] = version

    # Uruchom rewizję w tle
    background_tasks.add_task(
        run_revision,
        core_request=core_request
    )

    return RevisionResponse(
        project_id=request.project_id,
        version=version,
        status="queued",
        message=f"Rewizja dodana do kolejki. Regeneracja od etapu {request.from_stage}.",
        status_url=f"/api/status/{request.project_id}"
    )


@app.get("/api/versions/{project_id}")
async def list_versions(project_id: str):
    """
    Lista wszystkich wersji projektu.

    Pokazuje historię rewizji i wersji projektu.
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="System nie jest gotowy"
        )

    versions = orchestrator.revision_system.list_versions(project_id)

    if not versions:
        raise HTTPException(
            status_code=404,
            detail=f"Nie znaleziono wersji dla projektu {project_id}"
        )

    return {
        "project_id": project_id,
        "total_versions": len(versions),
        "versions": versions
    }


@app.get("/api/compare/{project_id}")
async def compare_versions(
    project_id: str,
    version1: int,
    version2: int,
    stage: str = "FINAL_OUTPUT"
):
    """
    Porównaj dwie wersje projektu na danym etapie.

    Pokazuje różnice między wersjami.
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="System nie jest gotowy"
        )

    # Konwertuj nazwę etapu
    try:
        pipeline_stage = PipelineStage[stage]
    except KeyError:
        valid_stages = [s.name for s in PipelineStage]
        raise HTTPException(
            status_code=400,
            detail=f"Nieprawidłowy etap: {stage}. Dozwolone: {valid_stages}"
        )

    comparison = orchestrator.revision_system.compare_versions(
        project_id,
        version1,
        version2,
        pipeline_stage
    )

    if "error" in comparison:
        raise HTTPException(
            status_code=404,
            detail=comparison["error"]
        )

    return comparison


@app.post("/api/export", response_model=ExportResponse)
async def export_narrative(request: ExportRequest):
    """
    Exportuj narrację do formatu ePub lub PDF.

    Generuje plik ePub lub PDF z narracji i zwraca URL do pobrania.
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="System nie jest gotowy"
        )

    # Validate format
    if request.format not in ["epub", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Nieprawidłowy format. Dozwolone: epub, pdf"
        )

    # Get version to export (default: latest)
    if request.version is None:
        request.version = orchestrator.revision_system.get_latest_version(request.project_id)

    # Load project context
    context = orchestrator.revision_system.load_context_snapshot(
        request.project_id,
        PipelineStage.FINAL_OUTPUT,
        request.version
    )

    if not context:
        raise HTTPException(
            status_code=404,
            detail=f"Nie znaleziono projektu {request.project_id} wersji {request.version}"
        )

    # Prepare narrative data for export
    narrative_data = {
        "output": context.get("output"),
        "metadata": {
            "brief": context.get("brief"),
            "world": context.get("world"),
            "characters": context.get("characters"),
            "edited_segments": context.get("edited_segments"),
            "stylized_segments": context.get("stylized_segments"),
            "segments": context.get("segments")
        }
    }

    # Generate export file
    try:
        import os
        from ..export import EpubExporter, PdfExporter

        # Create exports directory
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)

        # Generate file ID
        file_id = f"{request.project_id}_v{request.version}_{request.format}_{uuid.uuid4().hex[:8]}"
        output_path = exports_dir / f"{file_id}.{request.format}"

        if request.format == "epub":
            exporter = EpubExporter()
            file_path = exporter.export(
                narrative_data=narrative_data,
                output_path=str(output_path),
                metadata=request.metadata
            )
        else:  # pdf
            exporter = PdfExporter()
            file_path = exporter.export(
                narrative_data=narrative_data,
                output_path=str(output_path),
                metadata=request.metadata,
                include_toc=request.include_toc
            )

        # Get file size
        file_size = os.path.getsize(file_path)

        return ExportResponse(
            success=True,
            message="Export zakończony pomyślnie",
            file_id=file_id,
            download_url=f"/api/download/{file_id}",
            format=request.format,
            file_size=file_size
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Błąd podczas exportu: {str(e)}"
        )


@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    """
    Pobierz wyexportowany plik.

    Zwraca plik ePub lub PDF do pobrania.
    """
    from fastapi.responses import FileResponse
    import os

    # Determine format from file_id
    if "_epub_" in file_id:
        format_ext = "epub"
        media_type = "application/epub+zip"
    elif "_pdf_" in file_id:
        format_ext = "pdf"
        media_type = "application/pdf"
    else:
        raise HTTPException(
            status_code=400,
            detail="Nieprawidłowy ID pliku"
        )

    file_path = Path(f"data/exports/{file_id}.{format_ext}")

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Plik nie został znaleziony"
        )

    # Extract project_id for filename
    project_id = file_id.split("_")[0]
    filename = f"narracja_{project_id}.{format_ext}"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename
    )


@app.get("/api/exports/{project_id}")
async def list_exports(project_id: str):
    """
    Lista wszystkich exportów dla projektu.

    Zwraca listę dostępnych plików do pobrania.
    """
    import os
    exports_dir = Path("data/exports")

    if not exports_dir.exists():
        return {"project_id": project_id, "exports": []}

    # Find all export files for this project
    exports = []
    for file in exports_dir.glob(f"{project_id}_*"):
        stat = file.stat()
        file_id = file.stem  # bez rozszerzenia

        # Determine format
        if file.suffix == ".epub":
            format_type = "epub"
        elif file.suffix == ".pdf":
            format_type = "pdf"
        else:
            continue

        # Extract version
        parts = file_id.split("_")
        version = parts[1] if len(parts) > 1 and parts[1].startswith("v") else "unknown"

        exports.append({
            "file_id": file_id,
            "format": format_type,
            "version": version,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "download_url": f"/api/download/{file_id}"
        })

    # Sort by creation time (newest first)
    exports.sort(key=lambda x: x['created_at'], reverse=True)

    return {
        "project_id": project_id,
        "total_exports": len(exports),
        "exports": exports
    }


# ============================================================================
# WEBSOCKET
# ============================================================================

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket dla real-time updates projektu.
    """
    await websocket.accept()

    # Dodaj do listy połączeń
    if project_id not in websocket_connections:
        websocket_connections[project_id] = []
    websocket_connections[project_id].append(websocket)

    try:
        # Wyślij aktualny status
        if project_id in active_projects:
            await websocket.send_json({
                "type": "status",
                "data": active_projects[project_id]
            })

        # Czekaj na wiadomości (keep alive)
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        # Usuń z listy połączeń
        websocket_connections[project_id].remove(websocket)
        if not websocket_connections[project_id]:
            del websocket_connections[project_id]


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def run_generation(project_id: str, request: GenerationRequest):
    """
    Uruchom generację narracji w tle.
    """
    try:
        # Zaktualizuj status
        active_projects[project_id]["status"] = "processing"
        active_projects[project_id]["started_at"] = datetime.now()
        await broadcast_update(project_id)

        # Przygotuj brief
        brief_text = f"""
{request.brief}

FORMA: {request.form}
GATUNEK: {request.genre}
SKALA ŚWIATA: {request.world_scale}
FOKUS TEMATYCZNY: {', '.join(request.thematic_focus)}
POTENCJAŁ EKSPANSJI: {request.expansion_potential}
"""

        # Callback dla aktualizacji postępu
        async def progress_callback(stage: str, data: Dict[str, Any]):
            active_projects[project_id]["current_stage"] = stage

            if data.get("completed"):
                active_projects[project_id]["stages_completed"].append(stage)

            if data.get("failed"):
                active_projects[project_id]["stages_failed"].append(stage)

            await broadcast_update(project_id)

        # Uruchom produkcję
        result = await orchestrator.produce_narrative(
            brief=brief_text,
            progress_callback=progress_callback
        )

        # Zaktualizuj status - sukces
        active_projects[project_id]["status"] = "completed"
        active_projects[project_id]["completed_at"] = datetime.now()
        active_projects[project_id]["output_files"] = result.metadata.get("output_files", {})
        active_projects[project_id]["metadata"] = result.metadata

        await broadcast_update(project_id)

    except Exception as e:
        # Zaktualizuj status - błąd
        active_projects[project_id]["status"] = "failed"
        active_projects[project_id]["completed_at"] = datetime.now()
        active_projects[project_id]["error"] = str(e)

        await broadcast_update(project_id)


async def run_revision(core_request: CoreRevisionRequest):
    """
    Uruchom rewizję narracji w tle.
    """
    project_id = core_request.project_id

    try:
        # Zaktualizuj status
        active_projects[project_id]["status"] = "processing"
        active_projects[project_id]["started_at"] = datetime.now()
        await broadcast_update(project_id)

        # Callback dla aktualizacji postępu
        async def progress_callback(stage: str, data: Dict[str, Any]):
            active_projects[project_id]["current_stage"] = stage

            if data.get("completed"):
                if stage not in active_projects[project_id]["stages_completed"]:
                    active_projects[project_id]["stages_completed"].append(stage)

            if data.get("failed"):
                if stage not in active_projects[project_id]["stages_failed"]:
                    active_projects[project_id]["stages_failed"].append(stage)

            await broadcast_update(project_id)

        # Uruchom rewizję
        result = await orchestrator.revise_narrative(
            revision_request=core_request,
            progress_callback=progress_callback
        )

        # Zaktualizuj status
        if result["success"]:
            active_projects[project_id]["status"] = "completed"
            active_projects[project_id]["completed_at"] = datetime.now()
            active_projects[project_id]["version"] = result["version"]
            active_projects[project_id]["output_files"] = result.get("output", {})
            active_projects[project_id]["metadata"] = result.get("metadata", {})
        else:
            active_projects[project_id]["status"] = "failed"
            active_projects[project_id]["completed_at"] = datetime.now()
            active_projects[project_id]["error"] = result.get("error", "Unknown error")

        await broadcast_update(project_id)

    except Exception as e:
        # Zaktualizuj status - błąd
        active_projects[project_id]["status"] = "failed"
        active_projects[project_id]["completed_at"] = datetime.now()
        active_projects[project_id]["error"] = str(e)

        await broadcast_update(project_id)


async def broadcast_update(project_id: str):
    """Wyślij aktualizację do wszystkich połączonych WebSocket."""
    if project_id not in websocket_connections:
        return

    message = {
        "type": "update",
        "data": active_projects.get(project_id, {})
    }

    # Usuń połączenia które się rozłączyły
    disconnected = []

    for ws in websocket_connections[project_id]:
        try:
            await ws.send_json(message)
        except:
            disconnected.append(ws)

    # Usuń rozłączone
    for ws in disconnected:
        websocket_connections[project_id].remove(ws)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "narra_forge.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
