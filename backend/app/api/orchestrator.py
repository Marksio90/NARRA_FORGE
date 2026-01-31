"""
Service Orchestrator API - NarraForge 3.0 Phase 5
Endpoints for workflow orchestration and management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.orchestrator import (
    service_orchestrator,
    WorkflowStatus,
    StepType,
    ServiceType
)

router = APIRouter(prefix="/orchestrator")


# Request/Response Models
class WorkflowCreateRequest(BaseModel):
    """Request to create workflow"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    timeout_seconds: int = 3600
    tags: Optional[List[str]] = None


class WorkflowResponse(BaseModel):
    """Workflow response"""
    success: bool
    workflow: Optional[Dict[str, Any]] = None
    message: str = ""


class ExecutionStartRequest(BaseModel):
    """Request to start execution"""
    input_data: Dict[str, Any]
    user_id: Optional[str] = None
    project_id: Optional[str] = None


class ExecutionResponse(BaseModel):
    """Execution response"""
    success: bool
    execution: Optional[Dict[str, Any]] = None
    message: str = ""


class TemplateCustomizationRequest(BaseModel):
    """Request to customize template"""
    name: Optional[str] = None
    timeout_seconds: Optional[int] = None
    additional_steps: Optional[List[Dict[str, Any]]] = None


# Endpoints

@router.get("/health")
async def orchestrator_health():
    """Get orchestrator health status"""
    metrics = service_orchestrator.get_metrics()
    return {
        "success": True,
        "status": "healthy",
        "metrics": metrics
    }


@router.post("/workflows/create", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreateRequest):
    """
    Create a new workflow

    Define multi-step workflows with service calls,
    parallel execution, conditions, and loops.
    """
    try:
        workflow = service_orchestrator.create_workflow(
            name=request.name,
            description=request.description,
            steps=request.steps,
            timeout_seconds=request.timeout_seconds,
            tags=request.tags
        )

        return WorkflowResponse(
            success=True,
            workflow=workflow.to_dict(),
            message="Workflow created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    try:
        workflow = service_orchestrator.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return WorkflowResponse(
            success=True,
            workflow=workflow.to_dict(),
            message="Workflow retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_workflow_templates(category: Optional[str] = None):
    """Get available workflow templates"""
    try:
        templates = service_orchestrator.get_templates(category)
        return {
            "success": True,
            "templates": [t.to_dict() for t in templates],
            "count": len(templates)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get specific template details"""
    try:
        templates = service_orchestrator.get_templates()
        template = next((t for t in templates if t.template_id == template_id), None)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        return {
            "success": True,
            "template": template.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/create", response_model=WorkflowResponse)
async def create_from_template(
    template_id: str,
    request: Optional[TemplateCustomizationRequest] = None
):
    """Create workflow from template"""
    try:
        customizations = request.dict() if request else None

        workflow = service_orchestrator.create_from_template(
            template_id=template_id,
            customizations=customizations
        )

        return WorkflowResponse(
            success=True,
            workflow=workflow.to_dict(),
            message=f"Workflow created from template {template_id}"
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/start", response_model=ExecutionResponse)
async def start_execution(
    workflow_id: str,
    request: ExecutionStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start workflow execution

    Executes workflow steps in order, handling parallel steps,
    conditions, loops, and retries.
    """
    try:
        execution = service_orchestrator.start_execution(
            workflow_id=workflow_id,
            input_data=request.input_data,
            user_id=request.user_id,
            project_id=request.project_id
        )

        # Execute in background
        background_tasks.add_task(
            service_orchestrator.execute_workflow,
            execution.execution_id
        )

        return ExecutionResponse(
            success=True,
            execution=execution.to_dict(),
            message="Execution started"
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str):
    """Get execution status and details"""
    try:
        execution = service_orchestrator.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        return ExecutionResponse(
            success=True,
            execution=execution.to_dict(),
            message="Execution retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions")
async def get_executions(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """Get executions with filters"""
    try:
        workflow_status = WorkflowStatus(status) if status else None

        executions = service_orchestrator.get_executions(
            user_id=user_id,
            project_id=project_id,
            status=workflow_status,
            limit=limit
        )

        return {
            "success": True,
            "executions": [e.to_dict() for e in executions],
            "count": len(executions)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/pause")
async def pause_execution(execution_id: str):
    """Pause a running execution"""
    try:
        execution = service_orchestrator.pause_execution(execution_id)
        return {
            "success": True,
            "execution": execution.to_dict(),
            "message": "Execution paused"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/resume")
async def resume_execution(
    execution_id: str,
    background_tasks: BackgroundTasks
):
    """Resume a paused execution"""
    try:
        execution = service_orchestrator.resume_execution(execution_id)

        # Continue execution in background
        background_tasks.add_task(
            service_orchestrator.execute_workflow,
            execution_id
        )

        return {
            "success": True,
            "execution": execution.to_dict(),
            "message": "Execution resumed"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel a running execution"""
    try:
        execution = service_orchestrator.cancel_execution(execution_id)
        return {
            "success": True,
            "execution": execution.to_dict(),
            "message": "Execution cancelled"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}/checkpoints")
async def get_checkpoints(execution_id: str):
    """Get execution checkpoints"""
    try:
        execution = service_orchestrator.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        return {
            "success": True,
            "checkpoints": execution.checkpoints,
            "count": len(execution.checkpoints)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/restore/{checkpoint_name}")
async def restore_checkpoint(
    execution_id: str,
    checkpoint_name: str,
    background_tasks: BackgroundTasks
):
    """Restore execution from checkpoint"""
    try:
        execution = service_orchestrator.restore_from_checkpoint(
            execution_id=execution_id,
            checkpoint_name=checkpoint_name
        )

        # Continue execution
        background_tasks.add_task(
            service_orchestrator.execute_workflow,
            execution_id
        )

        return {
            "success": True,
            "execution": execution.to_dict(),
            "message": f"Restored from checkpoint: {checkpoint_name}"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services")
async def get_available_services():
    """Get available NarraForge services"""
    return {
        "success": True,
        "services": [s.value for s in ServiceType],
        "count": len(ServiceType)
    }


@router.get("/step-types")
async def get_step_types():
    """Get available step types"""
    return {
        "success": True,
        "step_types": [
            {
                "type": st.value,
                "description": {
                    "service_call": "Call a NarraForge service",
                    "parallel": "Execute steps in parallel",
                    "conditional": "Execute based on condition",
                    "loop": "Execute step for each item",
                    "wait": "Wait for duration or event",
                    "human_approval": "Wait for human approval",
                    "checkpoint": "Create execution checkpoint"
                }.get(st.value, "")
            }
            for st in StepType
        ]
    }


@router.get("/metrics")
async def get_orchestrator_metrics():
    """Get orchestrator metrics"""
    try:
        metrics = service_orchestrator.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
