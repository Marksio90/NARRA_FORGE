"""
Publishing Platform Integration API - NarraForge 3.0 Phase 4
Endpoints for multi-platform publishing and distribution management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.publishing_integration import (
    publishing_integration,
    Platform,
    PublishingStatus,
    BookFormat,
    FileFormat,
    PricingModel,
    RoyaltyTier
)

router = APIRouter(prefix="/platforms")


# Request/Response Models
class PlatformCredentialsRequest(BaseModel):
    """Request to set platform credentials"""
    platform: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    additional_settings: Optional[Dict[str, Any]] = None


class CredentialsResponse(BaseModel):
    """Credentials response"""
    success: bool
    platform: str
    connected: bool
    message: str = ""


class BookMetadataRequest(BaseModel):
    """Request with book metadata"""
    title: str
    subtitle: Optional[str] = None
    author: str
    description: str
    genres: List[str]
    keywords: List[str] = []
    language: str = "pl"
    isbn: Optional[str] = None
    series_name: Optional[str] = None
    series_number: Optional[int] = None
    page_count: int = 0
    word_count: int = 0
    publication_date: Optional[str] = None
    age_rating: str = "adult"
    contains_explicit_content: bool = False


class PricingRequest(BaseModel):
    """Request for pricing configuration"""
    base_price: float
    currency: str = "PLN"
    pricing_model: str = "fixed"
    discounts: Optional[Dict[str, float]] = None
    promotion_start: Optional[str] = None
    promotion_end: Optional[str] = None


class SubmissionRequest(BaseModel):
    """Request to submit book to platform"""
    project_id: str
    platform: str
    book_format: str = "ebook"
    file_format: str = "epub"
    metadata: BookMetadataRequest
    pricing: PricingRequest
    schedule_date: Optional[str] = None
    territories: List[str] = ["worldwide"]


class SubmissionResponse(BaseModel):
    """Submission response"""
    success: bool
    submission: Optional[Dict[str, Any]] = None
    message: str = ""


class DistributionRequest(BaseModel):
    """Request for multi-platform distribution"""
    project_id: str
    platforms: List[str]
    metadata: BookMetadataRequest
    pricing: Dict[str, PricingRequest]  # Platform -> pricing
    synchronize_updates: bool = True


# Endpoints

@router.get("/available")
async def get_available_platforms():
    """Get all available publishing platforms"""
    try:
        platforms = publishing_integration.get_available_platforms()

        return {
            "success": True,
            "platforms": platforms,
            "count": len(platforms)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{platform}/requirements")
async def get_platform_requirements(platform: str):
    """Get requirements for a specific platform"""
    try:
        platform_enum = Platform(platform)
        requirements = publishing_integration.get_platform_requirements(platform_enum)

        if not requirements:
            raise HTTPException(
                status_code=404,
                detail=f"Requirements not found for {platform}"
            )

        return {
            "success": True,
            "platform": platform,
            "requirements": requirements.to_dict()
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credentials", response_model=CredentialsResponse)
async def set_platform_credentials(
    user_id: str,
    request: PlatformCredentialsRequest
):
    """
    Set credentials for a publishing platform

    Credentials are encrypted and stored securely.
    """
    try:
        platform = Platform(request.platform)

        connected = publishing_integration.set_credentials(
            user_id=user_id,
            platform=platform,
            api_key=request.api_key,
            api_secret=request.api_secret,
            username=request.username,
            password=request.password,
            additional_settings=request.additional_settings
        )

        return CredentialsResponse(
            success=True,
            platform=request.platform,
            connected=connected,
            message="Credentials saved and verified" if connected else "Credentials saved"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credentials/{platform}/status")
async def check_credentials_status(user_id: str, platform: str):
    """Check if credentials are set and valid for a platform"""
    try:
        platform_enum = Platform(platform)
        status = publishing_integration.check_credentials(user_id, platform_enum)

        return {
            "success": True,
            "platform": platform,
            "has_credentials": status.get("has_credentials", False),
            "is_valid": status.get("is_valid", False),
            "last_verified": status.get("last_verified")
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/credentials/{platform}")
async def remove_credentials(user_id: str, platform: str):
    """Remove credentials for a platform"""
    try:
        platform_enum = Platform(platform)
        publishing_integration.remove_credentials(user_id, platform_enum)

        return {
            "success": True,
            "message": f"Credentials removed for {platform}"
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=SubmissionResponse)
async def submit_to_platform(
    user_id: str,
    request: SubmissionRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a book to a publishing platform

    Handles formatting, metadata preparation, and submission
    according to platform-specific requirements.
    """
    try:
        platform = Platform(request.platform)
        book_format = BookFormat(request.book_format)
        file_format = FileFormat(request.file_format)
        pricing_model = PricingModel(request.pricing.pricing_model)

        submission = publishing_integration.submit_book(
            user_id=user_id,
            project_id=request.project_id,
            platform=platform,
            book_format=book_format,
            file_format=file_format,
            metadata=request.metadata.dict(),
            pricing={
                **request.pricing.dict(),
                "pricing_model": pricing_model
            },
            schedule_date=request.schedule_date,
            territories=request.territories
        )

        return SubmissionResponse(
            success=True,
            submission=submission.to_dict(),
            message=f"Book submitted to {platform.value}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{submission_id}")
async def get_submission_status(submission_id: str):
    """Get status of a submission"""
    try:
        submission = publishing_integration.get_submission(submission_id)

        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        return {
            "success": True,
            "submission": submission.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/submissions")
async def get_project_submissions(user_id: str, project_id: str):
    """Get all submissions for a project"""
    try:
        submissions = publishing_integration.get_project_submissions(
            user_id=user_id,
            project_id=project_id
        )

        return {
            "success": True,
            "submissions": [s.to_dict() for s in submissions],
            "count": len(submissions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/distribute", response_model=SubmissionResponse)
async def distribute_to_multiple_platforms(
    user_id: str,
    request: DistributionRequest,
    background_tasks: BackgroundTasks
):
    """
    Distribute book to multiple platforms simultaneously

    Handles platform-specific formatting and pricing for
    each selected platform.
    """
    try:
        platforms = [Platform(p) for p in request.platforms]

        distribution = publishing_integration.distribute_book(
            user_id=user_id,
            project_id=request.project_id,
            platforms=platforms,
            metadata=request.metadata.dict(),
            pricing={p: pr.dict() for p, pr in request.pricing.items()},
            synchronize_updates=request.synchronize_updates
        )

        return SubmissionResponse(
            success=True,
            submission=distribution,
            message=f"Distribution initiated to {len(platforms)} platforms"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/distribution")
async def get_distribution_status(user_id: str, project_id: str):
    """Get distribution status across all platforms"""
    try:
        status = publishing_integration.get_distribution_status(
            user_id=user_id,
            project_id=project_id
        )

        return {
            "success": True,
            "distribution": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/update")
async def update_submission(
    submission_id: str,
    metadata: Optional[BookMetadataRequest] = None,
    pricing: Optional[PricingRequest] = None
):
    """Update metadata or pricing for an existing submission"""
    try:
        updated = publishing_integration.update_submission(
            submission_id=submission_id,
            metadata=metadata.dict() if metadata else None,
            pricing=pricing.dict() if pricing else None
        )

        return {
            "success": True,
            "submission": updated.to_dict(),
            "message": "Submission updated"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/unpublish")
async def unpublish_book(submission_id: str, reason: str = ""):
    """Unpublish a book from a platform"""
    try:
        result = publishing_integration.unpublish_book(
            submission_id=submission_id,
            reason=reason
        )

        return {
            "success": True,
            "message": "Book unpublished",
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/sales")
async def get_sales_data(
    user_id: str,
    project_id: str,
    platform: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get sales data for a project"""
    try:
        platform_enum = Platform(platform) if platform else None

        sales = publishing_integration.get_sales_data(
            user_id=user_id,
            project_id=project_id,
            platform=platform_enum,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": True,
            "sales": sales.to_dict() if hasattr(sales, 'to_dict') else sales
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sales/summary")
async def get_sales_summary(
    user_id: str,
    period: str = "month"
):
    """Get sales summary across all platforms and projects"""
    try:
        summary = publishing_integration.get_sales_summary(
            user_id=user_id,
            period=period
        )

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/royalties")
async def get_royalty_report(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get royalty report across all platforms"""
    try:
        report = publishing_integration.get_royalty_report(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": True,
            "report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-metadata")
async def validate_metadata(platform: str, metadata: BookMetadataRequest):
    """Validate metadata against platform requirements"""
    try:
        platform_enum = Platform(platform)

        validation = publishing_integration.validate_metadata(
            platform=platform_enum,
            metadata=metadata.dict()
        )

        return {
            "success": True,
            "is_valid": validation.get("is_valid", False),
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", [])
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-file")
async def validate_file(platform: str, file_format: str, file_path: str):
    """Validate book file against platform requirements"""
    try:
        platform_enum = Platform(platform)
        format_enum = FileFormat(file_format)

        validation = publishing_integration.validate_file(
            platform=platform_enum,
            file_format=format_enum,
            file_path=file_path
        )

        return {
            "success": True,
            "is_valid": validation.get("is_valid", False),
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", [])
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{platform}/categories")
async def get_platform_categories(platform: str):
    """Get available categories/genres for a platform"""
    try:
        platform_enum = Platform(platform)
        categories = publishing_integration.get_platform_categories(platform_enum)

        return {
            "success": True,
            "platform": platform,
            "categories": categories
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pricing/calculate")
async def calculate_pricing(
    base_price: float,
    currency: str,
    platforms: List[str]
):
    """Calculate suggested pricing across platforms"""
    try:
        platform_enums = [Platform(p) for p in platforms]

        pricing = publishing_integration.calculate_pricing(
            base_price=base_price,
            currency=currency,
            platforms=platform_enums
        )

        return {
            "success": True,
            "pricing": pricing
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
