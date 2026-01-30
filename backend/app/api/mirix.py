"""
MIRIX Memory System API - NarraForge 3.0

Endpoints for managing and querying the MIRIX memory system.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.mirix_memory_system import get_mirix_system, MemoryType
from app.services.mirix_procedural_seeds import seed_mirix_procedural_memory

router = APIRouter(prefix="/mirix", tags=["MIRIX Memory"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class MemoryQueryRequest(BaseModel):
    """Request model for querying memory"""
    query: str
    limit_per_layer: int = 5


class CoreFactRequest(BaseModel):
    """Request model for storing a core fact"""
    fact: str
    category: str
    entities: List[str]
    source: str = ""
    is_absolute: bool = True


class ConceptRequest(BaseModel):
    """Request model for storing a semantic concept"""
    concept: str
    concept_type: str
    definition: str
    symbolic_meaning: str = ""
    related: List[Dict] = []


class ConsistencyCheckRequest(BaseModel):
    """Request model for consistency check"""
    new_fact: str
    entities: List[str]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status")
async def get_mirix_status() -> Dict[str, Any]:
    """
    Get MIRIX memory system status and global statistics.
    """
    mirix = get_mirix_system()

    return {
        "status": "active",
        "version": "3.0",
        "global_memory": {
            "procedural_techniques": len(mirix.global_procedural.items),
            "resources": len(mirix.global_resources.items)
        },
        "active_projects": list(mirix.project_memories.keys()),
        "memory_layers": [
            "core", "episodic", "semantic",
            "procedural", "resource", "knowledge_vault"
        ]
    }


@router.post("/seed")
async def seed_procedural_memory() -> Dict[str, Any]:
    """
    Seed the global MIRIX procedural memory with writing techniques.

    This should be called once during system initialization or
    when you want to refresh the procedural knowledge base.
    """
    mirix = get_mirix_system()
    counts = await seed_mirix_procedural_memory(mirix)

    return {
        "success": True,
        "message": "MIRIX procedural memory seeded successfully",
        "items_seeded": counts,
        "total": sum(counts.values())
    }


@router.get("/project/{project_id}/statistics")
async def get_project_memory_statistics(project_id: str) -> Dict[str, Any]:
    """
    Get memory statistics for a specific project.
    """
    mirix = get_mirix_system()
    stats = mirix.get_memory_statistics(project_id)

    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])

    return stats


@router.post("/project/{project_id}/query")
async def query_project_memory(
    project_id: str,
    request: MemoryQueryRequest
) -> Dict[str, Any]:
    """
    Query all memory layers for relevant information.
    """
    mirix = get_mirix_system()

    if project_id not in mirix.project_memories:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not initialized in MIRIX"
        )

    results = await mirix.query_all_layers(
        project_id,
        request.query,
        request.limit_per_layer
    )

    return {
        "project_id": project_id,
        "query": request.query,
        "results": results,
        "total_items": sum(len(items) for items in results.values())
    }


@router.post("/project/{project_id}/core-fact")
async def store_core_fact(
    project_id: str,
    request: CoreFactRequest
) -> Dict[str, Any]:
    """
    Store a new core (immutable) fact for a project.
    """
    mirix = get_mirix_system()

    item_id = await mirix.store_core_fact(
        project_id=project_id,
        fact=request.fact,
        category=request.category,
        entities=request.entities,
        source=request.source,
        is_absolute=request.is_absolute
    )

    return {
        "success": True,
        "item_id": item_id,
        "message": f"Core fact stored: {request.fact[:50]}..."
    }


@router.post("/project/{project_id}/concept")
async def store_concept(
    project_id: str,
    request: ConceptRequest
) -> Dict[str, Any]:
    """
    Store a semantic concept (theme, motif, symbol).
    """
    mirix = get_mirix_system()

    # Convert related list to tuples
    related_tuples = [
        (r.get("concept", ""), r.get("relation", ""), r.get("strength", 0.5))
        for r in request.related
    ]

    item_id = await mirix.store_concept(
        project_id=project_id,
        concept=request.concept,
        concept_type=request.concept_type,
        definition=request.definition,
        related=related_tuples,
        symbolic_meaning=request.symbolic_meaning
    )

    return {
        "success": True,
        "item_id": item_id,
        "message": f"Concept stored: {request.concept}"
    }


@router.post("/project/{project_id}/check-consistency")
async def check_consistency(
    project_id: str,
    request: ConsistencyCheckRequest
) -> Dict[str, Any]:
    """
    Check if a new fact contradicts existing core memory.
    """
    mirix = get_mirix_system()

    result = await mirix.check_consistency(
        project_id=project_id,
        new_fact=request.new_fact,
        entities=request.entities
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not initialized in MIRIX"
        )

    return result


@router.get("/project/{project_id}/export")
async def export_project_memory(project_id: str) -> Dict[str, Any]:
    """
    Export all project memory as JSON.
    """
    mirix = get_mirix_system()
    export = mirix.export_project_memory(project_id)

    if "error" in export:
        raise HTTPException(status_code=404, detail=export["error"])

    return export


@router.get("/techniques")
async def get_available_techniques(
    genre: Optional[str] = None,
    technique_type: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get available writing techniques from global procedural memory.
    """
    mirix = get_mirix_system()

    techniques = []
    for item in mirix.global_procedural.items.values():
        # Filter by genre if specified
        if genre and genre.lower() not in item.genre_affinity:
            continue

        # Filter by type if specified
        if technique_type and item.technique_type != technique_type:
            continue

        techniques.append(item.to_dict())

        if len(techniques) >= limit:
            break

    # Sort by effectiveness
    techniques.sort(key=lambda x: x.get("effectiveness_score", 0), reverse=True)

    return {
        "techniques": techniques,
        "count": len(techniques),
        "filters": {
            "genre": genre,
            "technique_type": technique_type
        }
    }


@router.get("/resources")
async def get_available_resources(
    resource_type: Optional[str] = None,
    emotion: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get available creative resources (metaphors, descriptions).
    """
    mirix = get_mirix_system()

    resources = []
    for item in mirix.global_resources.items.values():
        # Filter by resource type
        if resource_type and item.resource_type != resource_type:
            continue

        # Filter by emotion
        if emotion and emotion.lower() not in [e.lower() for e in item.emotional_context]:
            continue

        # Filter by genre
        if genre and genre.lower() not in [g.lower() for g in item.genre_context]:
            continue

        resources.append(item.to_dict())

        if len(resources) >= limit:
            break

    # Sort by impact
    resources.sort(key=lambda x: x.get("impact_score", 0), reverse=True)

    return {
        "resources": resources,
        "count": len(resources),
        "filters": {
            "resource_type": resource_type,
            "emotion": emotion,
            "genre": genre
        }
    }


@router.get("/project/{project_id}/emotional-trajectory")
async def get_emotional_trajectory(project_id: str) -> Dict[str, Any]:
    """
    Get the emotional trajectory across all stored episodes.
    """
    mirix = get_mirix_system()

    if project_id not in mirix.project_memories:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not initialized in MIRIX"
        )

    episodic_layer = mirix.project_memories[project_id][MemoryType.EPISODIC]
    trajectory = await episodic_layer.get_emotional_trajectory()

    return {
        "project_id": project_id,
        "trajectory": trajectory,
        "episode_count": len(trajectory)
    }


@router.get("/project/{project_id}/theme-network")
async def get_theme_network(project_id: str) -> Dict[str, Any]:
    """
    Get the semantic network of themes and motifs.
    """
    mirix = get_mirix_system()

    if project_id not in mirix.project_memories:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id} not initialized in MIRIX"
        )

    semantic_layer = mirix.project_memories[project_id][MemoryType.SEMANTIC]
    network = await semantic_layer.get_theme_network()

    return {
        "project_id": project_id,
        "network": network
    }
