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

from ..core.orchestrator import NarrativeOrchestrator
from ..core.config import get_default_config
from ..core.types import ProductionStage
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
