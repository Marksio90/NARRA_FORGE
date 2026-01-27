"""
Series API endpoints for multi-book saga management
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.series_service import series_service
from app.models.user import User, SubscriptionTier
from app.models.series import Series, SeriesCharacterArc, SeriesPlotThread
from app.api.auth import get_current_active_user


router = APIRouter(prefix="/series", tags=["Series"])


# ============== Schemas ==============

class CreateSeriesRequest(BaseModel):
    """Request to create a new series"""
    name: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=50)
    planned_books: int = Field(default=3, ge=2, le=12)
    description: Optional[str] = Field(None, max_length=2000)
    language: str = Field(default="polski", max_length=20)


class SeriesResponse(BaseModel):
    """Series response schema"""
    id: int
    name: str
    genre: str
    planned_books: int
    completed_books: int
    series_arc: Optional[str]
    is_active: bool
    is_complete: bool
    language: str

    class Config:
        from_attributes = True


class SeriesListResponse(BaseModel):
    """List of series response"""
    series: List[SeriesResponse]
    total: int


class AddCharacterRequest(BaseModel):
    """Request to add a character to series tracking"""
    character_name: str = Field(..., min_length=1, max_length=255)
    first_book: int = Field(..., ge=1)
    starting_state: str = Field(default="", max_length=1000)
    target_end_state: str = Field(default="", max_length=1000)


class UpdateCharacterRequest(BaseModel):
    """Request to update character state"""
    new_state: str = Field(..., max_length=1000)
    book_number: int = Field(..., ge=1)
    key_moment: Optional[str] = Field(None, max_length=500)
    chapter: Optional[int] = Field(None, ge=1)


class AddPlotThreadRequest(BaseModel):
    """Request to add a plot thread"""
    name: str = Field(..., min_length=1, max_length=255)
    introduced_book: int = Field(..., ge=1)
    description: str = Field(default="", max_length=1000)
    is_main_plot: bool = Field(default=False)
    introduced_chapter: Optional[int] = Field(None, ge=1)


class ResolvePlotThreadRequest(BaseModel):
    """Request to resolve a plot thread"""
    resolved_book: int = Field(..., ge=1)
    resolved_chapter: Optional[int] = Field(None, ge=1)


class CharacterArcResponse(BaseModel):
    """Character arc response"""
    id: int
    character_name: str
    starting_state: Optional[str]
    current_state: Optional[str]
    target_end_state: Optional[str]
    first_appearance_book: int
    last_appearance_book: Optional[int]
    is_alive: bool

    class Config:
        from_attributes = True


class PlotThreadResponse(BaseModel):
    """Plot thread response"""
    id: int
    name: str
    description: Optional[str]
    introduced_in_book: int
    resolved_in_book: Optional[int]
    is_resolved: bool
    is_main_plot: bool

    class Config:
        from_attributes = True


class SeriesSummaryResponse(BaseModel):
    """Comprehensive series summary"""
    series: dict
    books: List[dict]
    characters: List[dict]
    plot_threads: dict


class ConsistencyIssue(BaseModel):
    """Consistency issue found in series"""
    type: str
    severity: str
    message: str


# ============== Endpoints ==============

@router.post("", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED)
async def create_series(
    request: CreateSeriesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new book series.
    Requires PRO or PREMIUM subscription.
    """
    # Check subscription
    if not current_user.can_create_series:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Series creation requires PRO or PREMIUM subscription"
        )

    try:
        series = await series_service.create_series(
            db=db,
            user_id=current_user.id,
            name=request.name,
            genre=request.genre,
            planned_books=request.planned_books,
            description=request.description,
            language=request.language
        )

        return SeriesResponse.model_validate(series)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create series: {str(e)}"
        )


@router.get("", response_model=SeriesListResponse)
async def list_series(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all series belonging to the current user"""
    series_list = db.query(Series).filter(
        Series.user_id == current_user.id
    ).order_by(Series.created_at.desc()).all()

    return SeriesListResponse(
        series=[SeriesResponse.model_validate(s) for s in series_list],
        total=len(series_list)
    )


@router.get("/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get series details"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    return SeriesResponse.model_validate(series)


@router.get("/{series_id}/summary", response_model=SeriesSummaryResponse)
async def get_series_summary(
    series_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive series summary including all books, characters, and plot threads"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    try:
        summary = series_service.get_series_summary(db, series_id)
        return SeriesSummaryResponse(**summary)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{series_id}/prepare-next-book")
async def prepare_next_book(
    series_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Prepare the next book in the series with full continuity context.
    Creates a new project linked to the series.
    """
    # Check credits
    if not current_user.has_credits():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient credits to generate a new book"
        )

    try:
        project = await series_service.prepare_next_book(
            db=db,
            series_id=series_id,
            user_id=current_user.id
        )

        # Deduct credit
        current_user.deduct_credit()
        db.commit()

        return {
            "message": "Next book prepared successfully",
            "project_id": project.id,
            "book_number": project.book_number_in_series,
            "title": project.name,
            "credits_remaining": current_user.credits_remaining
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{series_id}/characters", response_model=CharacterArcResponse)
async def add_character_to_series(
    series_id: int,
    request: AddCharacterRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a recurring character to track across the series"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    arc = series_service.add_character_to_series(
        db=db,
        series_id=series_id,
        character_name=request.character_name,
        first_book=request.first_book,
        starting_state=request.starting_state,
        target_end_state=request.target_end_state
    )

    return CharacterArcResponse.model_validate(arc)


@router.get("/{series_id}/characters", response_model=List[CharacterArcResponse])
async def get_series_characters(
    series_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tracked characters in the series"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    arcs = db.query(SeriesCharacterArc).filter(
        SeriesCharacterArc.series_id == series_id
    ).all()

    return [CharacterArcResponse.model_validate(a) for a in arcs]


@router.put("/{series_id}/characters/{arc_id}", response_model=CharacterArcResponse)
async def update_character_state(
    series_id: int,
    arc_id: int,
    request: UpdateCharacterRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a character's state after events in a book"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    try:
        arc = series_service.update_character_state(
            db=db,
            arc_id=arc_id,
            new_state=request.new_state,
            book_number=request.book_number,
            key_moment=request.key_moment,
            chapter=request.chapter
        )

        return CharacterArcResponse.model_validate(arc)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{series_id}/plot-threads", response_model=PlotThreadResponse)
async def add_plot_thread(
    series_id: int,
    request: AddPlotThreadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a plot thread to track across the series"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    thread = series_service.add_plot_thread(
        db=db,
        series_id=series_id,
        name=request.name,
        introduced_book=request.introduced_book,
        description=request.description,
        is_main_plot=request.is_main_plot,
        introduced_chapter=request.introduced_chapter
    )

    return PlotThreadResponse.model_validate(thread)


@router.get("/{series_id}/plot-threads", response_model=List[PlotThreadResponse])
async def get_plot_threads(
    series_id: int,
    unresolved_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all plot threads in the series"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    query = db.query(SeriesPlotThread).filter(
        SeriesPlotThread.series_id == series_id
    )

    if unresolved_only:
        query = query.filter(SeriesPlotThread.is_resolved == False)

    threads = query.all()
    return [PlotThreadResponse.model_validate(t) for t in threads]


@router.put("/{series_id}/plot-threads/{thread_id}/resolve", response_model=PlotThreadResponse)
async def resolve_plot_thread(
    series_id: int,
    thread_id: int,
    request: ResolvePlotThreadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a plot thread as resolved"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    try:
        thread = series_service.resolve_plot_thread(
            db=db,
            thread_id=thread_id,
            resolved_book=request.resolved_book,
            resolved_chapter=request.resolved_chapter
        )

        return PlotThreadResponse.model_validate(thread)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{series_id}/consistency-check", response_model=List[ConsistencyIssue])
async def check_consistency(
    series_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check series for consistency issues.
    Returns list of potential problems found.
    """
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    try:
        issues = await series_service.validate_series_consistency(db, series_id)
        return [ConsistencyIssue(**issue) for issue in issues]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{series_id}/mark-book-completed/{project_id}")
async def mark_book_completed(
    series_id: int,
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a book as completed in the series"""
    # Verify ownership
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    try:
        updated_series = series_service.mark_book_completed(
            db=db,
            series_id=series_id,
            project_id=project_id
        )

        return {
            "message": "Book marked as completed",
            "completed_books": updated_series.completed_books,
            "planned_books": updated_series.planned_books,
            "is_complete": updated_series.is_complete
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{series_id}")
async def delete_series(
    series_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a series and optionally its books"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    db.delete(series)
    db.commit()

    return {"message": "Series deleted successfully"}
