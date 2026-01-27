"""
Publishing API endpoints for commercial book sales
"""

from typing import Optional, List, Literal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.publishing_service import publishing_service
from app.models.user import User
from app.models.project import Project
from app.models.publishing import PublishingMetadata
from app.api.auth import get_current_active_user


router = APIRouter(prefix="/publishing", tags=["Publishing"])


# ============== Schemas ==============

class UpdateMetadataRequest(BaseModel):
    """Request to update publishing metadata"""
    book_description: Optional[str] = Field(None, max_length=4000)
    tagline: Optional[str] = Field(None, max_length=255)
    author_bio: Optional[str] = Field(None, max_length=2000)
    copyright_holder: Optional[str] = Field(None, max_length=255)
    copyright_year: Optional[int] = None
    price_usd: Optional[float] = Field(None, ge=0.99, le=999.99)
    price_eur: Optional[float] = Field(None, ge=0.99, le=999.99)
    price_pln: Optional[float] = Field(None, ge=3.99, le=999.99)
    age_rating: Optional[str] = Field(None, max_length=20)
    is_adult_content: Optional[bool] = None
    series_name: Optional[str] = Field(None, max_length=255)
    series_position: Optional[int] = Field(None, ge=1)
    royalty_type: Optional[Literal["35_percent", "70_percent"]] = None
    kdp_select_enrolled: Optional[bool] = None


class SetPricingRequest(BaseModel):
    """Request to set pricing"""
    price_usd: float = Field(..., ge=0.99, le=999.99)
    price_eur: Optional[float] = Field(None, ge=0.99, le=999.99)
    price_gbp: Optional[float] = Field(None, ge=0.99, le=999.99)
    price_pln: Optional[float] = Field(None, ge=3.99, le=999.99)
    royalty_type: Literal["35_percent", "70_percent"] = "70_percent"


class MarkPublishedRequest(BaseModel):
    """Request to mark book as published"""
    platform: str = Field(..., min_length=1, max_length=50)
    platform_id: str = Field(..., min_length=1, max_length=100)


class RecordSaleRequest(BaseModel):
    """Request to record a sale"""
    platform: str
    units: int = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    royalty: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)


class MetadataResponse(BaseModel):
    """Publishing metadata response"""
    id: int
    project_id: int
    isbn_13: Optional[str]
    primary_category: Optional[str]
    secondary_categories: Optional[List[str]]
    keywords: Optional[List[str]]
    book_description: Optional[str]
    tagline: Optional[str]
    price_usd: Optional[float]
    price_pln: Optional[float]
    is_published: bool
    publication_date: Optional[datetime]
    copyright_holder: Optional[str]
    cover_image_url: Optional[str]
    is_ready: bool

    class Config:
        from_attributes = True


class SalesSummaryResponse(BaseModel):
    """Sales summary response"""
    total_units: int
    total_revenue: float
    total_royalty: float
    platforms: dict
    records_count: int


# ============== Endpoints ==============

@router.get("/{project_id}", response_model=MetadataResponse)
async def get_publishing_metadata(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get publishing metadata for a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    metadata = publishing_service.get_or_create_metadata(db, project_id)

    return MetadataResponse(
        id=metadata.id,
        project_id=metadata.project_id,
        isbn_13=metadata.isbn_13,
        primary_category=metadata.primary_category,
        secondary_categories=metadata.secondary_categories,
        keywords=metadata.keywords,
        book_description=metadata.book_description,
        tagline=metadata.tagline,
        price_usd=metadata.price_usd,
        price_pln=metadata.price_pln,
        is_published=metadata.is_published,
        publication_date=metadata.publication_date,
        copyright_holder=metadata.copyright_holder,
        cover_image_url=metadata.cover_image_url,
        is_ready=metadata.is_ready_for_publishing()
    )


@router.put("/{project_id}", response_model=MetadataResponse)
async def update_publishing_metadata(
    project_id: int,
    request: UpdateMetadataRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update publishing metadata"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update only provided fields
    update_data = request.model_dump(exclude_unset=True, exclude_none=True)
    metadata = publishing_service.update_metadata(db, project_id, **update_data)

    return MetadataResponse(
        id=metadata.id,
        project_id=metadata.project_id,
        isbn_13=metadata.isbn_13,
        primary_category=metadata.primary_category,
        secondary_categories=metadata.secondary_categories,
        keywords=metadata.keywords,
        book_description=metadata.book_description,
        tagline=metadata.tagline,
        price_usd=metadata.price_usd,
        price_pln=metadata.price_pln,
        is_published=metadata.is_published,
        publication_date=metadata.publication_date,
        copyright_holder=metadata.copyright_holder,
        cover_image_url=metadata.cover_image_url,
        is_ready=metadata.is_ready_for_publishing()
    )


@router.post("/{project_id}/generate-isbn")
async def generate_isbn(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate ISBN for the book.
    NOTE: This generates a mock ISBN for development.
    Real ISBNs require Bowker/Nielsen account.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    metadata = publishing_service.get_or_create_metadata(db, project_id)

    # Check if ISBN already exists
    if metadata.isbn_13:
        return {
            "isbn": metadata.isbn_13,
            "message": "ISBN already generated",
            "is_mock": True
        }

    isbn = publishing_service.generate_isbn(
        db=db,
        project_id=project_id,
        title=project.name,
        author=metadata.copyright_holder or current_user.full_name or current_user.username
    )

    return {
        "isbn": isbn,
        "message": "ISBN generated successfully",
        "is_mock": True,
        "note": "This is a mock ISBN for development. Real ISBNs require Bowker/Nielsen registration."
    }


@router.post("/{project_id}/generate-description")
async def generate_description(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate marketing description using AI"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    try:
        description = await publishing_service.generate_book_description(db, project_id)

        return {
            "description": description,
            "length": len(description),
            "message": "Description generated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate description: {str(e)}"
        )


@router.post("/{project_id}/generate-keywords")
async def generate_keywords(
    project_id: int,
    num_keywords: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate SEO keywords using AI"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    try:
        keywords = await publishing_service.generate_keywords(
            db, project_id, num_keywords=min(num_keywords, 7)
        )

        return {
            "keywords": keywords,
            "count": len(keywords),
            "message": "Keywords generated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate keywords: {str(e)}"
        )


@router.post("/{project_id}/set-categories")
async def set_categories(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set BISAC categories based on book genre"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    genre = project.genre.value if project.genre else "drama"
    categories = publishing_service.set_categories_for_genre(db, project_id, genre)

    return {
        "primary_category": categories["primary"],
        "secondary_categories": categories["secondary"],
        "message": f"Categories set for {genre} genre"
    }


@router.put("/{project_id}/pricing")
async def set_pricing(
    project_id: int,
    request: SetPricingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set pricing for the book"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Auto-calculate missing prices if not provided
    price_eur = request.price_eur or round(request.price_usd * 0.92, 2)
    price_gbp = request.price_gbp or round(request.price_usd * 0.79, 2)
    price_pln = request.price_pln or round(request.price_usd * 4.0, 2)

    metadata = publishing_service.update_metadata(
        db, project_id,
        price_usd=request.price_usd,
        price_eur=price_eur,
        price_gbp=price_gbp,
        price_pln=price_pln,
        royalty_type=request.royalty_type
    )

    return {
        "price_usd": metadata.price_usd,
        "price_eur": metadata.price_eur,
        "price_gbp": metadata.price_gbp,
        "price_pln": metadata.price_pln,
        "royalty_type": metadata.royalty_type,
        "message": "Pricing updated successfully"
    }


@router.post("/{project_id}/generate-cover-prompt")
async def generate_cover_prompt(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a prompt for AI cover generation"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    try:
        cover_prompt = await publishing_service.generate_cover_prompt(db, project_id)

        return {
            "cover_prompt": cover_prompt,
            "message": "Cover prompt generated. Use this with DALL-E, Midjourney, or similar AI tools.",
            "recommended_dimensions": "1024x1792 (6:9 ratio for book covers)"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate cover prompt: {str(e)}"
        )


@router.get("/{project_id}/export/kdp")
async def prepare_kdp_export(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Prepare export data for Amazon KDP"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    kdp_data = publishing_service.prepare_kdp_export(db, project_id)

    if not kdp_data.get("ready"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=kdp_data.get("message", "Missing required fields"),
            headers={"X-Missing-Fields": ",".join(kdp_data.get("missing_fields", []))}
        )

    return kdp_data


@router.get("/{project_id}/export/d2d")
async def prepare_draft2digital_export(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Prepare export data for Draft2Digital"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    d2d_data = publishing_service.prepare_draft2digital_export(db, project_id)

    if not d2d_data.get("ready"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=d2d_data.get("message", "Missing required fields")
        )

    return d2d_data


@router.post("/{project_id}/mark-published")
async def mark_as_published(
    project_id: int,
    request: MarkPublishedRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark book as published on a platform"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    metadata = publishing_service.mark_as_published(
        db, project_id, request.platform, request.platform_id
    )

    return {
        "is_published": metadata.is_published,
        "publication_date": metadata.publication_date.isoformat() if metadata.publication_date else None,
        "platform": request.platform,
        "platform_id": request.platform_id,
        "message": f"Book marked as published on {request.platform}"
    }


@router.post("/{project_id}/sales")
async def record_sale(
    project_id: int,
    request: RecordSaleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a sales entry"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    record = publishing_service.record_sale(
        db=db,
        project_id=project_id,
        platform=request.platform,
        units=request.units,
        revenue=request.revenue,
        royalty=request.royalty,
        currency=request.currency
    )

    return {
        "id": record.id,
        "platform": record.platform,
        "units_sold": record.units_sold,
        "revenue": record.gross_revenue,
        "royalty": record.royalty_earned,
        "message": "Sale recorded successfully"
    }


@router.get("/{project_id}/sales", response_model=SalesSummaryResponse)
async def get_sales_summary(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sales summary for the book"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    summary = publishing_service.get_sales_summary(db, project_id)
    return SalesSummaryResponse(**summary)


@router.get("/{project_id}/readiness-check")
async def check_publishing_readiness(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if book is ready for publishing"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    metadata = publishing_service.get_or_create_metadata(db, project_id)

    checklist = {
        "has_description": bool(metadata.book_description),
        "has_category": bool(metadata.primary_category),
        "has_keywords": bool(metadata.keywords and len(metadata.keywords) >= 3),
        "has_pricing": bool(metadata.price_usd or metadata.price_pln),
        "has_copyright": bool(metadata.copyright_holder),
        "has_cover": bool(metadata.cover_image_url or metadata.cover_image_path),
        "has_isbn": bool(metadata.isbn_13),
    }

    missing = [k.replace("has_", "") for k, v in checklist.items() if not v]
    is_ready = all(checklist.values())

    return {
        "is_ready": is_ready,
        "checklist": checklist,
        "missing_items": missing,
        "completion_percentage": round(sum(checklist.values()) / len(checklist) * 100, 1)
    }
