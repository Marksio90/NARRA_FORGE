"""
Narrative Routes.

Handles generated narrative retrieval, export, and management.
"""

from typing import Annotated, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.models.base import get_db
from api.models.user import User
from api.models.narrative import Narrative
from api.schemas.narrative import (
    NarrativeResponse,
    NarrativeDetailResponse,
    NarrativeListResponse
)
from api.schemas.auth import MessageResponse
from api.auth import get_current_active_user


router = APIRouter(prefix="/narratives", tags=["Narratives"])


@router.get("/", response_model=NarrativeListResponse)
async def list_narratives(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    production_type: Optional[str] = Query(None, description="Filter by production type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all narratives for current user with pagination and filtering.

    Filters:
    - project_id: Show narratives for specific project
    - genre: Filter by genre
    - production_type: Filter by production type
    """
    # Build query
    offset = (page - 1) * page_size

    filters = [Narrative.user_id == current_user.id]

    if project_id:
        filters.append(Narrative.project_id == project_id)
    if genre:
        filters.append(Narrative.genre == genre)
    if production_type:
        filters.append(Narrative.production_type == production_type)

    # Get total count
    count_stmt = select(func.count(Narrative.id)).where(*filters)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get narratives (without full text for performance)
    stmt = (
        select(Narrative)
        .where(*filters)
        .order_by(Narrative.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    narratives = result.scalars().all()

    total_pages = ceil(total / page_size) if total > 0 else 0

    return NarrativeListResponse(
        narratives=[NarrativeResponse.model_validate(n) for n in narratives],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{narrative_id}", response_model=NarrativeDetailResponse)
async def get_narrative(
    narrative_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get full narrative by ID (including text and metadata).

    Increments view count.
    """
    stmt = select(Narrative).where(
        Narrative.id == narrative_id,
        Narrative.user_id == current_user.id
    )
    result = await db.execute(stmt)
    narrative = result.scalar_one_or_none()

    if not narrative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narrative not found"
        )

    # Increment view count
    narrative.increment_view_count()
    await db.commit()
    await db.refresh(narrative)

    return NarrativeDetailResponse.model_validate(narrative)


@router.get("/{narrative_id}/text", response_class=PlainTextResponse)
async def get_narrative_text(
    narrative_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get narrative text only (plain text response).

    Useful for downloads or raw text viewing.
    """
    stmt = select(Narrative).where(
        Narrative.id == narrative_id,
        Narrative.user_id == current_user.id
    )
    result = await db.execute(stmt)
    narrative = result.scalar_one_or_none()

    if not narrative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narrative not found"
        )

    return narrative.narrative_text


@router.delete("/{narrative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_narrative(
    narrative_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete narrative.

    User must own the narrative.
    """
    stmt = select(Narrative).where(
        Narrative.id == narrative_id,
        Narrative.user_id == current_user.id
    )
    result = await db.execute(stmt)
    narrative = result.scalar_one_or_none()

    if not narrative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narrative not found"
        )

    await db.delete(narrative)
    await db.commit()

    return None


# Advanced features (Phase 4) - kept as placeholders

@router.get("/{narrative_id}/export/{format}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def export_narrative(narrative_id: str, format: str):
    """
    Export narrative in specified format.

    Supported formats: txt, pdf, epub, docx

    TODO: Implement in Phase 4 (Advanced Features)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Narrative export will be implemented in Phase 4"
    )


@router.get("/{narrative_id}/versions", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_narrative_versions(narrative_id: str):
    """
    Get all versions of a narrative.

    TODO: Implement in Phase 4 (Iterative refinement)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Version history will be implemented in Phase 4"
    )


@router.post("/{narrative_id}/regenerate", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def regenerate_narrative(narrative_id: str):
    """
    Create new version by regenerating narrative.

    TODO: Implement in Phase 4 (Iterative refinement)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Narrative regeneration will be implemented in Phase 4"
    )
