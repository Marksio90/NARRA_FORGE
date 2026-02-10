"""
Service Orchestrator - NarraForge 3.0 Phase 5
Coordinates multi-service workflows and manages complex book generation pipelines
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from datetime import datetime, timedelta
import uuid
import asyncio
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Distributed lock via Redis (for horizontal scaling)
# ---------------------------------------------------------------------------

class RedisDistributedLock:
    """Redis-based distributed lock for multi-instance safety.

    Uses SET NX EX pattern (atomic set-if-not-exists with TTL).
    This ensures that only one backend instance can execute a given
    workflow step at a time, even when scaled to N replicas.
    """

    def __init__(self, lock_timeout: int = 300):
        self._redis = None
        self._lock_timeout = lock_timeout  # seconds

    def _get_redis(self):
        if self._redis is None:
            try:
                import redis as redis_lib
                from app.config import settings
                self._redis = redis_lib.Redis.from_url(
                    settings.REDIS_URL, decode_responses=True
                )
                self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis distributed lock unavailable: {e}")
                self._redis = None
        return self._redis

    def acquire(self, lock_name: str, holder_id: str) -> bool:
        """Try to acquire a named lock. Returns True if acquired."""
        r = self._get_redis()
        if r is None:
            return True  # Fallback: no lock when Redis unavailable

        key = f"narraforge:lock:{lock_name}"
        acquired = r.set(key, holder_id, nx=True, ex=self._lock_timeout)
        if acquired:
            logger.debug(f"Acquired distributed lock '{lock_name}' (holder={holder_id})")
        return bool(acquired)

    def release(self, lock_name: str, holder_id: str) -> bool:
        """Release a lock, but only if we still own it."""
        r = self._get_redis()
        if r is None:
            return True

        key = f"narraforge:lock:{lock_name}"
        # Lua script ensures atomic check-and-delete
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = r.eval(lua, 1, key, holder_id)
        if result:
            logger.debug(f"Released distributed lock '{lock_name}'")
        return bool(result)

    def is_locked(self, lock_name: str) -> bool:
        """Check if a lock is currently held."""
        r = self._get_redis()
        if r is None:
            return False
        return r.exists(f"narraforge:lock:{lock_name}") > 0


# Module-level distributed lock instance
_distributed_lock = RedisDistributedLock(lock_timeout=600)  # 10 min TTL


# ---------------------------------------------------------------------------
# DB persistence helpers (store workflow state in PostgreSQL JSONB)
# ---------------------------------------------------------------------------

def _persist_execution_to_db(execution: "WorkflowExecution") -> bool:
    """Persist workflow execution state to the database (generation_logs).

    Uses the existing GenerationLog model to store workflow snapshots so that
    active workflows survive process restarts.  Runs synchronously because
    Celery workers don't have an async DB driver – we open a short-lived
    session, upsert, and close.
    """
    try:
        from app.database import SessionLocal
        from app.models.generation_log import GenerationLog

        db = SessionLocal()
        try:
            # Look for existing log entry for this execution
            log_entry = (
                db.query(GenerationLog)
                .filter(GenerationLog.step_name == f"workflow_{execution.execution_id}")
                .first()
            )

            snapshot = {
                "execution_id": execution.execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "current_step_id": execution.current_step_id,
                "context": _safe_json(execution.context),
                "step_executions": {
                    k: v.to_dict() for k, v in execution.step_executions.items()
                },
                "checkpoints": execution.checkpoints,
                "input_data": _safe_json(execution.input_data),
                "output_data": _safe_json(execution.output_data),
                "error_message": execution.error_message,
                "user_id": execution.user_id,
                "project_id": execution.project_id,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            }

            if log_entry is None:
                # Use generation_log's ModelTier (str enum "tier1"/"tier2"/"tier3")
                # NOT ai_service.ModelTier (int enum 1/2/3) - DB column expects string enum
                from app.models.generation_log import ModelTier as DBModelTier
                log_entry = GenerationLog(
                    project_id=int(execution.project_id) if execution.project_id and str(execution.project_id).isdigit() else None,
                    step=0,
                    step_name=f"workflow_{execution.execution_id}",
                    agent_name="ServiceOrchestrator",
                    model_tier=DBModelTier.TIER1,
                    model_name="orchestrator",
                    tokens_in=0,
                    tokens_out=0,
                    cost=0.0,
                    success=1 if execution.status != WorkflowStatus.FAILED else 0,
                    error_message=json.dumps(snapshot, default=str),
                )
                db.add(log_entry)
            else:
                log_entry.error_message = json.dumps(snapshot, default=str)
                log_entry.success = 1 if execution.status != WorkflowStatus.FAILED else 0

            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Failed to persist workflow execution to DB: {e}")
        return False


def _safe_json(obj: Any) -> Any:
    """Make an object JSON-safe by converting non-serializable types."""
    if isinstance(obj, dict):
        return {k: _safe_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe_json(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    return obj


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"


class StepStatus(Enum):
    """Individual step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class StepType(Enum):
    """Step execution types"""
    SERVICE_CALL = "service_call"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    WAIT = "wait"
    HUMAN_APPROVAL = "human_approval"
    CHECKPOINT = "checkpoint"


class ServiceType(Enum):
    """NarraForge service types"""
    # Phase 1 - Foundation
    MIRIX = "mirix"
    EMOTIONAL = "emotional"
    DIALOGUE = "dialogue"
    CONSCIOUSNESS = "consciousness"
    STYLE = "style"
    PACING = "pacing"
    # Phase 2 - Multimodal
    ILLUSTRATIONS = "illustrations"
    AUDIOBOOK = "audiobook"
    COVERS = "covers"
    TRAILER = "trailer"
    INTERACTIVE = "interactive"
    SOUNDTRACK = "soundtrack"
    # Phase 3 - Intelligence
    COHERENCE = "coherence"
    PSYCHOLOGY = "psychology"
    CULTURAL = "cultural"
    COMPLEXITY = "complexity"
    TRENDS = "trends"
    # Phase 4 - Expansion
    MULTILANGUAGE = "multilanguage"
    COLLABORATIVE = "collaborative"
    COACH = "coach"
    PLATFORMS = "platforms"
    ANALYTICS = "analytics"


class RetryPolicy(Enum):
    """Retry policies"""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class RetryConfig:
    """Retry configuration"""
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    max_retries: int = 3
    initial_delay_seconds: int = 1
    max_delay_seconds: int = 60
    retry_on_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy": self.policy.value,
            "max_retries": self.max_retries,
            "initial_delay_seconds": self.initial_delay_seconds,
            "max_delay_seconds": self.max_delay_seconds
        }


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step_id: str
    name: str
    step_type: StepType
    service: Optional[ServiceType] = None
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # Expression for conditional execution
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    timeout_seconds: int = 300
    on_failure: str = "fail"  # fail, skip, continue
    on_success: Optional[str] = None  # Next step override
    parallel_steps: List["WorkflowStep"] = field(default_factory=list)
    loop_items: Optional[str] = None  # Expression for loop items
    checkpoint_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "step_type": self.step_type.value,
            "service": self.service.value if self.service else None,
            "action": self.action,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "condition": self.condition,
            "retry_config": self.retry_config.to_dict(),
            "timeout_seconds": self.timeout_seconds,
            "on_failure": self.on_failure,
            "metadata": self.metadata
        }


@dataclass
class StepExecution:
    """Step execution record"""
    execution_id: str
    step_id: str
    status: StepStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "step_id": self.step_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms
        }


@dataclass
class Workflow:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": [s.to_dict() for s in self.steps],
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "timeout_seconds": self.timeout_seconds,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "tags": self.tags
        }


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)  # Shared data between steps
    step_executions: Dict[str, StepExecution] = field(default_factory=dict)
    current_step_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    error_message: Optional[str] = None
    checkpoints: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "step_executions": {
                k: v.to_dict() for k, v in self.step_executions.items()
            },
            "current_step_id": self.current_step_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "project_id": self.project_id
        }


@dataclass
class WorkflowTemplate:
    """Pre-built workflow template"""
    template_id: str
    name: str
    description: str
    category: str
    workflow: Workflow
    parameters: Dict[str, Any] = field(default_factory=dict)
    example_input: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "workflow": self.workflow.to_dict(),
            "parameters": self.parameters,
            "example_input": self.example_input
        }


# Pre-built workflow templates
WORKFLOW_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "full_book_generation": {
        "name": "Full Book Generation",
        "description": "Complete book generation with all phases",
        "category": "book_creation",
        "steps": [
            {"name": "Initialize Project", "service": "mirix", "action": "initialize"},
            {"name": "Analyze Trends", "service": "trends", "action": "analyze"},
            {"name": "Create Outline", "service": "pacing", "action": "create_outline"},
            {"name": "Develop Characters", "service": "consciousness", "action": "create_characters"},
            {"name": "Generate Chapters", "service": "dialogue", "action": "generate", "type": "loop"},
            {"name": "Apply Style", "service": "style", "action": "apply"},
            {"name": "Add Emotional Resonance", "service": "emotional", "action": "enhance"},
            {"name": "Check Coherence", "service": "coherence", "action": "analyze"},
            {"name": "Cultural Adaptation", "service": "cultural", "action": "adapt"},
            {"name": "Generate Cover", "service": "covers", "action": "generate"},
            {"name": "Create Illustrations", "service": "illustrations", "action": "generate"},
            {"name": "Generate Audiobook", "service": "audiobook", "action": "generate"},
            {"name": "Prepare Publishing", "service": "platforms", "action": "prepare"},
        ]
    },
    "translation_workflow": {
        "name": "Book Translation",
        "description": "Translate book to multiple languages",
        "category": "translation",
        "steps": [
            {"name": "Analyze Source", "service": "multilanguage", "action": "analyze"},
            {"name": "Create Glossary", "service": "multilanguage", "action": "create_glossary"},
            {"name": "Translate Chapters", "service": "multilanguage", "action": "translate", "type": "loop"},
            {"name": "Cultural Adaptation", "service": "cultural", "action": "adapt"},
            {"name": "Quality Check", "service": "coherence", "action": "validate"},
            {"name": "Generate Localized Cover", "service": "covers", "action": "localize"},
        ]
    },
    "audiobook_production": {
        "name": "Audiobook Production",
        "description": "Full audiobook production pipeline",
        "category": "multimodal",
        "steps": [
            {"name": "Text Preparation", "service": "audiobook", "action": "prepare_text"},
            {"name": "Voice Selection", "service": "audiobook", "action": "select_voices"},
            {"name": "Chapter Narration", "service": "audiobook", "action": "narrate", "type": "loop"},
            {"name": "Add Soundtrack", "service": "soundtrack", "action": "generate"},
            {"name": "Master Audio", "service": "audiobook", "action": "master"},
            {"name": "Quality Check", "service": "audiobook", "action": "validate"},
        ]
    },
    "marketing_package": {
        "name": "Marketing Package",
        "description": "Generate complete marketing materials",
        "category": "marketing",
        "steps": [
            {"name": "Analyze Book", "service": "psychology", "action": "analyze_appeal"},
            {"name": "Generate Cover Variants", "service": "covers", "action": "generate_variants"},
            {"name": "Create Trailer", "service": "trailer", "action": "generate"},
            {"name": "Generate Promo Text", "service": "style", "action": "generate_promo"},
            {"name": "Social Media Assets", "service": "illustrations", "action": "social_assets"},
        ]
    }
}


class ServiceOrchestrator:
    """
    Service Orchestrator for NarraForge

    Features:
    - Multi-step workflow execution
    - Parallel and sequential step execution
    - Conditional branching
    - Loop execution for batch processing
    - Checkpoint and resume capability
    - Rollback support
    - Retry with exponential backoff
    - Workflow templates
    """

    _instance = None
    _init_lock = asyncio.Lock() if False else None  # Placeholder; real lock below

    def __new__(cls):
        # Thread-safe singleton via module-level lock
        import threading
        if not hasattr(cls, '_singleton_lock'):
            cls._singleton_lock = threading.Lock()
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Workflow registry
        self.workflows: Dict[str, Workflow] = {}

        # Execution history (bounded LRU-style: max 1000 entries)
        self.executions: Dict[str, WorkflowExecution] = {}
        self._max_executions = 1000

        # Templates
        self.templates: Dict[str, WorkflowTemplate] = {}

        # Real service instances (lazy-loaded)
        self._service_instances: Dict[str, Any] = {}

        # Service action whitelist - only these methods can be called per service
        self._allowed_actions: Dict[str, List[str]] = {
            "mirix": ["initialize", "query_all_layers", "store_core_fact", "store_episode",
                       "get_context_for_scene", "check_consistency", "get_memory_statistics"],
            "emotional": ["analyze_emotional_resonance", "predict_reader_state",
                          "optimize_emotional_impact"],
            "coherence": ["analyze_full_story", "analyze_chapter", "check_proposed_change"],
            "style": ["apply", "analyze"],
            "pacing": ["create_outline", "analyze"],
            "consciousness": ["create_characters"],
            "dialogue": ["generate"],
            "covers": ["generate", "generate_variants", "localize"],
            "illustrations": ["generate", "social_assets"],
            "audiobook": ["prepare_text", "select_voices", "narrate", "master", "validate"],
            "trailer": ["generate"],
            "soundtrack": ["generate"],
            "interactive": ["generate"],
            "multilanguage": ["analyze", "create_glossary", "translate"],
            "cultural": ["adapt"],
            "psychology": ["analyze_appeal"],
            "complexity": ["analyze"],
            "trends": ["analyze"],
            "collaborative": ["sync"],
            "coach": ["advise"],
            "platforms": ["prepare"],
            "analytics": ["report"],
        }

        # Concurrency lock – prevents race conditions on shared state
        self._lock = asyncio.Lock()

        # Execution hooks
        self.pre_step_hooks: List[Callable] = []
        self.post_step_hooks: List[Callable] = []

        # Metrics
        self.metrics: Dict[str, Any] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_steps_executed": 0
        }

        self._register_default_templates()
        self._initialized = True

    def _get_service_instance(self, service_name: str) -> Any:
        """Lazy-load and return a real service instance."""
        if service_name in self._service_instances:
            return self._service_instances[service_name]

        instance = None
        try:
            if service_name == "mirix":
                from app.services.mirix_memory_system import get_mirix_system
                instance = get_mirix_system()
            elif service_name == "emotional":
                from app.services.emotional_resonance_engine import get_emotional_resonance_engine
                instance = get_emotional_resonance_engine()
            elif service_name == "coherence":
                from app.services.quantum_coherence import get_coherence_analyzer
                instance = get_coherence_analyzer()
            elif service_name == "style":
                from app.agents.prose_writer_agent import ProseWriterAgent
                instance = ProseWriterAgent()
            elif service_name == "consciousness":
                from app.agents.character_creator_agent import CharacterCreatorAgent
                instance = CharacterCreatorAgent()
            elif service_name == "pacing":
                from app.agents.plot_architect_agent import PlotArchitectAgent
                instance = PlotArchitectAgent()
            elif service_name == "dialogue":
                from app.agents.prose_writer_agent import ProseWriterAgent
                instance = ProseWriterAgent()
            else:
                logger.warning(
                    f"Service '{service_name}' has no registered implementation yet. "
                    f"Using stub fallback."
                )
                return None
        except ImportError as e:
            logger.warning(f"Could not import service '{service_name}': {e}")
            return None

        if instance:
            self._service_instances[service_name] = instance
            logger.info(f"Loaded service instance: {service_name} ({type(instance).__name__})")

        return instance

    def _register_default_templates(self):
        """Register default workflow templates"""
        for template_id, template_data in WORKFLOW_TEMPLATES.items():
            steps = []
            for i, step_data in enumerate(template_data["steps"]):
                step = WorkflowStep(
                    step_id=f"step_{i}",
                    name=step_data["name"],
                    step_type=StepType.LOOP if step_data.get("type") == "loop" else StepType.SERVICE_CALL,
                    service=ServiceType(step_data["service"]),
                    action=step_data["action"],
                    dependencies=[f"step_{i-1}"] if i > 0 else []
                )
                steps.append(step)

            workflow = Workflow(
                workflow_id=template_id,
                name=template_data["name"],
                description=template_data["description"],
                steps=steps,
                tags=[template_data["category"]]
            )

            self.templates[template_id] = WorkflowTemplate(
                template_id=template_id,
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                workflow=workflow
            )

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        timeout_seconds: int = 3600,
        tags: Optional[List[str]] = None
    ) -> Workflow:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())

        workflow_steps = []
        for i, step_data in enumerate(steps):
            step = WorkflowStep(
                step_id=step_data.get("step_id", f"step_{i}"),
                name=step_data["name"],
                step_type=StepType(step_data.get("step_type", "service_call")),
                service=ServiceType(step_data["service"]) if step_data.get("service") else None,
                action=step_data.get("action", ""),
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", []),
                condition=step_data.get("condition"),
                timeout_seconds=step_data.get("timeout_seconds", 300),
                on_failure=step_data.get("on_failure", "fail")
            )
            workflow_steps.append(step)

        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            timeout_seconds=timeout_seconds,
            tags=tags or []
        )

        self.workflows[workflow_id] = workflow
        return workflow

    def create_from_template(
        self,
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Create workflow from template"""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")

        template = self.templates[template_id]
        workflow = Workflow(
            workflow_id=str(uuid.uuid4()),
            name=template.workflow.name,
            description=template.workflow.description,
            steps=template.workflow.steps.copy(),
            tags=template.workflow.tags.copy()
        )

        # Apply customizations
        if customizations:
            if "name" in customizations:
                workflow.name = customizations["name"]
            if "timeout_seconds" in customizations:
                workflow.timeout_seconds = customizations["timeout_seconds"]

        self.workflows[workflow.workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)

    def start_execution(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> WorkflowExecution:
        """Start workflow execution (thread-safe with DB persistence)"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        execution_id = str(uuid.uuid4())

        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            input_data=input_data,
            context=input_data.copy(),
            user_id=user_id,
            project_id=project_id
        )

        # Evict oldest executions if at capacity (prevents memory leak)
        if len(self.executions) >= self._max_executions:
            oldest_key = next(iter(self.executions))
            del self.executions[oldest_key]

        self.executions[execution_id] = execution
        self.metrics["total_executions"] += 1

        # Start execution
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now()

        # Persist initial state to DB
        _persist_execution_to_db(execution)

        return execution

    async def execute_workflow(
        self,
        execution_id: str
    ) -> WorkflowExecution:
        """Execute workflow steps (with local lock, distributed lock, and DB persistence)"""
        async with self._lock:
            execution = self.executions.get(execution_id)
            if not execution:
                raise ValueError(f"Execution not found: {execution_id}")

            workflow = self.workflows.get(execution.workflow_id)
            if not workflow:
                raise ValueError(f"Workflow not found: {execution.workflow_id}")

        # Distributed lock: prevent two backend instances from running
        # the same workflow execution simultaneously
        lock_name = f"workflow:{execution_id}"
        holder_id = str(uuid.uuid4())
        if not _distributed_lock.acquire(lock_name, holder_id):
            logger.warning(
                f"Distributed lock already held for execution {execution_id}. "
                f"Another instance is processing this workflow."
            )
            return execution

        try:
            # Execute steps in order
            for step in workflow.steps:
                # Check dependencies
                if not self._check_dependencies(execution, step):
                    continue

                # Check condition
                if step.condition and not self._evaluate_condition(step.condition, execution.context):
                    execution.step_executions[step.step_id] = StepExecution(
                        execution_id=str(uuid.uuid4()),
                        step_id=step.step_id,
                        status=StepStatus.SKIPPED
                    )
                    continue

                # Execute step
                async with self._lock:
                    execution.current_step_id = step.step_id
                step_execution = await self._execute_step(step, execution)

                async with self._lock:
                    execution.step_executions[step.step_id] = step_execution

                # Persist progress after each step
                _persist_execution_to_db(execution)

                if step_execution.status == StepStatus.FAILED:
                    if step.on_failure == "fail":
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = step_execution.error_message
                        break
                    elif step.on_failure == "skip":
                        continue

            # Complete execution
            async with self._lock:
                if execution.status == WorkflowStatus.RUNNING:
                    execution.status = WorkflowStatus.COMPLETED
                    execution.output_data = execution.context.get("output", {})
                    self.metrics["successful_executions"] += 1

                execution.completed_at = datetime.now()

        except Exception as e:
            async with self._lock:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.now()
                self.metrics["failed_executions"] += 1
        finally:
            # Always release distributed lock
            _distributed_lock.release(lock_name, holder_id)

        # Persist final state
        _persist_execution_to_db(execution)

        return execution

    async def _execute_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution
    ) -> StepExecution:
        """Execute a single step with iterative (non-recursive) retry logic"""
        step_execution = StepExecution(
            execution_id=str(uuid.uuid4()),
            step_id=step.step_id,
            status=StepStatus.RUNNING,
            started_at=datetime.now(),
            input_data=self._prepare_step_input(step, execution.context)
        )

        execution.current_step_id = step.step_id

        async with self._lock:
            self.metrics["total_steps_executed"] += 1

        # Run pre-step hooks
        for hook in self.pre_step_hooks:
            await hook(step, execution, step_execution)

        # Iterative retry loop (fixes infinite recursion bug)
        max_attempts = step.retry_config.max_retries + 1
        for attempt in range(max_attempts):
            try:
                if step.step_type == StepType.PARALLEL:
                    result = await self._execute_parallel_steps(step, execution)
                elif step.step_type == StepType.LOOP:
                    result = await self._execute_loop(step, execution)
                elif step.step_type == StepType.CHECKPOINT:
                    result = self._create_checkpoint(step, execution)
                else:
                    result = await self._call_service(step, execution.context)

                step_execution.status = StepStatus.COMPLETED
                step_execution.output_data = result
                execution.context.update(result)
                break  # Success - exit retry loop

            except Exception as e:
                step_execution.retry_count = attempt + 1
                if attempt < max_attempts - 1:
                    step_execution.status = StepStatus.RETRYING
                    delay = self._calculate_retry_delay(step.retry_config, attempt + 1)
                    logger.warning(
                        f"Step '{step.name}' failed (attempt {attempt + 1}/{max_attempts}), "
                        f"retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    step_execution.status = StepStatus.FAILED
                    step_execution.error_message = str(e)

        step_execution.completed_at = datetime.now()
        step_execution.duration_ms = (
            step_execution.completed_at - step_execution.started_at
        ).total_seconds() * 1000

        # Run post-step hooks
        for hook in self.post_step_hooks:
            await hook(step, execution, step_execution)

        return step_execution

    async def _execute_parallel_steps(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute steps in parallel"""
        tasks = []
        for parallel_step in step.parallel_steps:
            task = self._execute_step(parallel_step, execution)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_result = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise result
            combined_result[step.parallel_steps[i].step_id] = result.output_data

        return combined_result

    async def _execute_loop(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute step in a loop"""
        items = self._get_loop_items(step, execution.context)
        results = []

        for i, item in enumerate(items):
            loop_context = {**execution.context, "loop_item": item, "loop_index": i}
            result = await self._call_service(step, loop_context)
            results.append(result)

        return {"loop_results": results}

    async def _call_service(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a real NarraForge service.

        Dispatches to actual service instances with action whitelisting.
        Falls back to stub response for unimplemented services.
        """
        if step.service is None:
            return {}

        service_name = step.service.value
        action = step.action
        parameters = self._prepare_step_input(step, context)

        # Validate action against whitelist
        allowed = self._allowed_actions.get(service_name, [])
        if action and action not in allowed:
            raise ValueError(
                f"Action '{action}' is not allowed for service '{service_name}'. "
                f"Allowed actions: {allowed}"
            )

        # Get real service instance
        service_instance = self._get_service_instance(service_name)

        if service_instance is None:
            # Stub fallback for unimplemented services
            logger.warning(
                f"Service '{service_name}' not implemented, returning stub response "
                f"for action '{action}'"
            )
            return {
                "service": service_name,
                "action": action,
                "success": True,
                "stub": True,
                "result": f"Stub: {service_name}.{action} (not yet implemented)",
                "timestamp": datetime.now().isoformat()
            }

        # Resolve and call the method
        if not action:
            logger.warning(f"No action specified for service '{service_name}'")
            return {"service": service_name, "success": True, "result": "No action specified"}

        method = getattr(service_instance, action, None)
        if method is None:
            raise ValueError(
                f"Service '{service_name}' ({type(service_instance).__name__}) "
                f"has no method '{action}'"
            )

        if not callable(method):
            raise ValueError(
                f"'{action}' on service '{service_name}' is not callable"
            )

        logger.info(f"Calling {service_name}.{action}({list(parameters.keys())})")

        # Call the real method.
        # Synchronous (CPU-bound) service calls are offloaded to a thread
        # via asyncio.to_thread so they don't block the FastAPI event loop.
        try:
            if asyncio.iscoroutinefunction(method):
                result = await method(**parameters)
            else:
                result = await asyncio.to_thread(method, **parameters)
        except TypeError as e:
            # Parameter mismatch - try calling without params
            logger.warning(
                f"Parameter mismatch for {service_name}.{action}: {e}. "
                f"Retrying with context-only call."
            )
            try:
                if asyncio.iscoroutinefunction(method):
                    result = await method()
                else:
                    result = await asyncio.to_thread(method)
            except Exception:
                raise

        # Normalize result to dict
        if not isinstance(result, dict):
            result = {"result": result}

        result.update({
            "service": service_name,
            "action": action,
            "success": True,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Service {service_name}.{action} completed successfully")
        return result

    def _check_dependencies(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep
    ) -> bool:
        """Check if step dependencies are satisfied"""
        for dep_id in step.dependencies:
            dep_execution = execution.step_executions.get(dep_id)
            if not dep_execution or dep_execution.status != StepStatus.COMPLETED:
                return False
        return True

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate step condition safely without eval().

        Supports simple expressions:
        - "key" → truthy check on context[key]
        - "key == value" → equality check
        - "key != value" → inequality check
        - "key > value" / "key < value" → numeric comparison
        - "key in list_key" → membership check
        - "not key" → negation
        """
        try:
            condition = condition.strip()

            # Negation: "not key"
            if condition.startswith("not "):
                inner = condition[4:].strip()
                return not self._evaluate_condition(inner, context)

            # Comparison operators
            for op, func in [
                ("!=", lambda a, b: a != b),
                ("==", lambda a, b: a == b),
                (">=", lambda a, b: float(a) >= float(b)),
                ("<=", lambda a, b: float(a) <= float(b)),
                (">", lambda a, b: float(a) > float(b)),
                ("<", lambda a, b: float(a) < float(b)),
            ]:
                if op in condition:
                    left, right = condition.split(op, 1)
                    left_val = context.get(left.strip(), left.strip())
                    right_val = context.get(right.strip(), right.strip())
                    return func(left_val, right_val)

            # Membership: "key in list_key"
            if " in " in condition:
                item_key, list_key = condition.split(" in ", 1)
                item_val = context.get(item_key.strip(), item_key.strip())
                list_val = context.get(list_key.strip(), [])
                return item_val in list_val

            # Simple truthy check
            return bool(context.get(condition, False))
        except Exception:
            return False

    def _prepare_step_input(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input data for step"""
        input_data = {}
        for key, value in step.parameters.items():
            if isinstance(value, str) and value.startswith("$"):
                # Variable reference
                var_name = value[1:]
                input_data[key] = context.get(var_name)
            else:
                input_data[key] = value
        return input_data

    def _get_loop_items(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Get items for loop execution"""
        if step.loop_items:
            if step.loop_items.startswith("$"):
                var_name = step.loop_items[1:]
                items = context.get(var_name, [])
                return items if isinstance(items, list) else [items]
        return context.get("items", [])

    def _calculate_retry_delay(
        self,
        config: RetryConfig,
        retry_count: int
    ) -> float:
        """Calculate delay for retry"""
        if config.policy == RetryPolicy.FIXED:
            return config.initial_delay_seconds
        elif config.policy == RetryPolicy.LINEAR:
            return min(
                config.initial_delay_seconds * retry_count,
                config.max_delay_seconds
            )
        elif config.policy == RetryPolicy.EXPONENTIAL:
            return min(
                config.initial_delay_seconds * (2 ** (retry_count - 1)),
                config.max_delay_seconds
            )
        return 0

    def _create_checkpoint(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Create execution checkpoint"""
        checkpoint_name = step.checkpoint_name or f"checkpoint_{step.step_id}"
        execution.checkpoints[checkpoint_name] = {
            "context": execution.context.copy(),
            "step_executions": {
                k: v.to_dict() for k, v in execution.step_executions.items()
            },
            "created_at": datetime.now().isoformat()
        }
        return {"checkpoint": checkpoint_name}

    def pause_execution(self, execution_id: str) -> WorkflowExecution:
        """Pause workflow execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.PAUSED
            execution.paused_at = datetime.now()

        return execution

    def resume_execution(self, execution_id: str) -> WorkflowExecution:
        """Resume paused execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        if execution.status == WorkflowStatus.PAUSED:
            execution.status = WorkflowStatus.RUNNING

        return execution

    def cancel_execution(self, execution_id: str) -> WorkflowExecution:
        """Cancel workflow execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now()

        return execution

    def restore_from_checkpoint(
        self,
        execution_id: str,
        checkpoint_name: str
    ) -> WorkflowExecution:
        """Restore execution from checkpoint"""
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        checkpoint = execution.checkpoints.get(checkpoint_name)
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_name}")

        execution.context = checkpoint["context"]
        execution.status = WorkflowStatus.RUNNING

        return execution

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution by ID"""
        return self.executions.get(execution_id)

    def get_executions(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[WorkflowStatus] = None,
        limit: int = 100
    ) -> List[WorkflowExecution]:
        """Get executions with filters"""
        executions = list(self.executions.values())

        if user_id:
            executions = [e for e in executions if e.user_id == user_id]

        if project_id:
            executions = [e for e in executions if e.project_id == project_id]

        if status:
            executions = [e for e in executions if e.status == status]

        return sorted(
            executions,
            key=lambda e: e.started_at or datetime.min,
            reverse=True
        )[:limit]

    def get_templates(
        self,
        category: Optional[str] = None
    ) -> List[WorkflowTemplate]:
        """Get workflow templates"""
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return templates

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        running_count = len([
            e for e in self.executions.values()
            if e.status == WorkflowStatus.RUNNING
        ])

        return {
            **self.metrics,
            "workflows_count": len(self.workflows),
            "templates_count": len(self.templates),
            "running_executions": running_count,
            "total_executions_stored": len(self.executions)
        }

    def add_pre_step_hook(self, hook: Callable):
        """Add hook to run before each step"""
        self.pre_step_hooks.append(hook)

    def add_post_step_hook(self, hook: Callable):
        """Add hook to run after each step"""
        self.post_step_hooks.append(hook)


# Singleton instance
service_orchestrator = ServiceOrchestrator()
