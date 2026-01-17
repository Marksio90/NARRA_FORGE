"""
Project Routes.

Handles project CRUD operations and management.
"""

import uuid
from typing import Annotated
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from api.models.base import get_db
from api.models.user import User
from api.models.project import Project
from api.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse
)
from api.auth import get_current_active_user


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all projects for current user with pagination.

    Returns:
    - List of projects
    - Total count
    - Pagination info
    """
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    count_stmt = select(func.count(Project.id)).where(Project.user_id == current_user.id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get projects
    stmt = (
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    projects = result.scalars().all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new project for the current user.

    Projects are workspaces that organize narratives.
    """
    # Create new project
    new_project = Project(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        world_id=request.world_id,
        default_genre=request.default_genre,
        default_production_type=request.default_production_type,
        narrative_count=0,
        total_word_count=0,
        total_cost_usd=0.0
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return ProjectResponse.model_validate(new_project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get project by ID.

    User must own the project.
    """
    # Get project
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update project details.

    User must own the project. Only provided fields will be updated.
    """
    # Get project
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete project.

    User must own the project. This will cascade delete all narratives and jobs.
    """
    # Check if project exists and user owns it
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Delete project (cascade will handle related records)
    await db.delete(project)
    await db.commit()

    return None
