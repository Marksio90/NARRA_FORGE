"""
Publishing Platform Integration - NarraForge 3.0 Phase 4

Integration with major publishing platforms including Amazon KDP,
Apple Books, Google Play Books, Kobo, and more.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class Platform(Enum):
    """Supported publishing platforms"""
    AMAZON_KDP = "amazon_kdp"
    APPLE_BOOKS = "apple_books"
    GOOGLE_PLAY = "google_play"
    KOBO = "kobo"
    BARNES_NOBLE = "barnes_noble"
    SMASHWORDS = "smashwords"
    DRAFT2DIGITAL = "draft2digital"
    LULU = "lulu"
    INGRAMSPARK = "ingramspark"
    BOOKBABY = "bookbaby"
    # Polish platforms
    EMPIK = "empik"
    PUBLIO = "publio"
    LEGIMI = "legimi"
    WOBLINK = "woblink"


class PublishingStatus(Enum):
    """Publishing status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    UNPUBLISHED = "unpublished"


class BookFormat(Enum):
    """Book formats"""
    EBOOK = "ebook"
    PAPERBACK = "paperback"
    HARDCOVER = "hardcover"
    AUDIOBOOK = "audiobook"


class FileFormat(Enum):
    """File formats for publishing"""
    EPUB = "epub"
    MOBI = "mobi"
    PDF = "pdf"
    DOCX = "docx"
    KPF = "kpf"  # Kindle Package Format
    MP3 = "mp3"  # For audiobooks
    M4B = "m4b"  # For audiobooks


class PricingModel(Enum):
    """Pricing models"""
    FIXED = "fixed"
    FREE = "free"
    KINDLE_UNLIMITED = "kindle_unlimited"
    SUBSCRIPTION = "subscription"


class RoyaltyTier(Enum):
    """Royalty tiers"""
    STANDARD = "standard"      # Usually 35%
    PREMIUM = "premium"        # Usually 70%
    EXCLUSIVE = "exclusive"    # Platform exclusive deals


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PlatformCredentials:
    """Credentials for a publishing platform"""
    credential_id: str
    platform: Platform
    user_id: str
    api_key: Optional[str]
    api_secret: Optional[str]
    account_id: str
    verified: bool
    connected_at: datetime
    last_sync: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "credential_id": self.credential_id,
            "platform": self.platform.value,
            "account_id": self.account_id[:4] + "***",  # Masked
            "verified": self.verified,
            "connected_at": self.connected_at.isoformat(),
            "last_sync": self.last_sync.isoformat() if self.last_sync else None
        }


@dataclass
class PlatformRequirements:
    """Requirements for a publishing platform"""
    platform: Platform
    supported_formats: List[FileFormat]
    supported_book_formats: List[BookFormat]
    max_file_size_mb: int
    min_price: float
    max_price: float
    currency: str
    royalty_options: Dict[str, float]
    required_metadata: List[str]
    cover_requirements: Dict[str, Any]
    content_guidelines: List[str]
    review_time_days: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "supported_formats": [f.value for f in self.supported_formats],
            "supported_book_formats": [f.value for f in self.supported_book_formats],
            "max_file_size_mb": self.max_file_size_mb,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "currency": self.currency,
            "royalty_options": self.royalty_options,
            "required_metadata": self.required_metadata,
            "cover_requirements": self.cover_requirements,
            "content_guidelines": self.content_guidelines,
            "review_time_days": self.review_time_days
        }


@dataclass
class BookMetadata:
    """Metadata for book publishing"""
    title: str
    subtitle: Optional[str]
    author_name: str
    description: str
    short_description: Optional[str]
    keywords: List[str]
    categories: List[str]
    bisac_codes: List[str]
    language: str
    isbn: Optional[str]
    asin: Optional[str]
    page_count: Optional[int]
    word_count: int
    publication_date: Optional[datetime]
    series_name: Optional[str]
    series_position: Optional[int]
    edition: str
    publisher: str
    copyright_holder: str
    age_rating: Optional[str]
    content_warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "author_name": self.author_name,
            "description": self.description,
            "short_description": self.short_description,
            "keywords": self.keywords,
            "categories": self.categories,
            "bisac_codes": self.bisac_codes,
            "language": self.language,
            "isbn": self.isbn,
            "asin": self.asin,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "series_name": self.series_name,
            "series_position": self.series_position,
            "edition": self.edition,
            "publisher": self.publisher,
            "copyright_holder": self.copyright_holder,
            "age_rating": self.age_rating,
            "content_warnings": self.content_warnings
        }


@dataclass
class PricingConfig:
    """Pricing configuration"""
    base_price: float
    currency: str
    pricing_model: PricingModel
    platform_prices: Dict[str, float]  # platform -> price
    promotional_price: Optional[float]
    promotion_start: Optional[datetime]
    promotion_end: Optional[datetime]
    royalty_tier: RoyaltyTier

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_price": self.base_price,
            "currency": self.currency,
            "pricing_model": self.pricing_model.value,
            "platform_prices": self.platform_prices,
            "promotional_price": self.promotional_price,
            "promotion_start": self.promotion_start.isoformat() if self.promotion_start else None,
            "promotion_end": self.promotion_end.isoformat() if self.promotion_end else None,
            "royalty_tier": self.royalty_tier.value
        }


@dataclass
class PublishingSubmission:
    """A submission to a publishing platform"""
    submission_id: str
    book_id: str
    platform: Platform
    format: BookFormat
    file_format: FileFormat
    metadata: BookMetadata
    pricing: PricingConfig
    status: PublishingStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    published_at: Optional[datetime]
    platform_book_id: Optional[str]
    platform_url: Optional[str]
    rejection_reason: Optional[str]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "submission_id": self.submission_id,
            "book_id": self.book_id,
            "platform": self.platform.value,
            "format": self.format.value,
            "file_format": self.file_format.value,
            "metadata": self.metadata.to_dict(),
            "pricing": self.pricing.to_dict(),
            "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "platform_book_id": self.platform_book_id,
            "platform_url": self.platform_url,
            "rejection_reason": self.rejection_reason,
            "notes": self.notes
        }


@dataclass
class SalesData:
    """Sales data from a platform"""
    platform: Platform
    book_id: str
    period_start: datetime
    period_end: datetime
    units_sold: int
    units_returned: int
    units_borrowed: int  # For subscription services
    revenue_gross: float
    royalties_earned: float
    currency: str
    by_country: Dict[str, int]
    by_format: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "book_id": self.book_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "units_sold": self.units_sold,
            "units_returned": self.units_returned,
            "units_borrowed": self.units_borrowed,
            "net_units": self.units_sold - self.units_returned,
            "revenue_gross": self.revenue_gross,
            "royalties_earned": self.royalties_earned,
            "currency": self.currency,
            "by_country": self.by_country,
            "by_format": self.by_format
        }


@dataclass
class DistributionStatus:
    """Distribution status across platforms"""
    book_id: str
    platforms: Dict[str, PublishingSubmission]
    total_platforms: int
    published_count: int
    pending_count: int
    rejected_count: int
    total_sales: int
    total_revenue: float
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_id": self.book_id,
            "platforms": {k: v.to_dict() for k, v in self.platforms.items()},
            "total_platforms": self.total_platforms,
            "published_count": self.published_count,
            "pending_count": self.pending_count,
            "rejected_count": self.rejected_count,
            "total_sales": self.total_sales,
            "total_revenue": self.total_revenue,
            "last_updated": self.last_updated.isoformat()
        }


# =============================================================================
# PLATFORM REQUIREMENTS DATABASE
# =============================================================================

PLATFORM_REQUIREMENTS = {
    Platform.AMAZON_KDP: PlatformRequirements(
        platform=Platform.AMAZON_KDP,
        supported_formats=[FileFormat.EPUB, FileFormat.MOBI, FileFormat.KPF, FileFormat.DOCX, FileFormat.PDF],
        supported_book_formats=[BookFormat.EBOOK, BookFormat.PAPERBACK, BookFormat.HARDCOVER],
        max_file_size_mb=650,
        min_price=0.99,
        max_price=9999.99,
        currency="USD",
        royalty_options={"35%": 0.35, "70%": 0.70},
        required_metadata=["title", "author", "description", "categories", "keywords"],
        cover_requirements={
            "min_width": 1000,
            "min_height": 1600,
            "max_width": 10000,
            "max_height": 10000,
            "format": ["jpg", "tiff"],
            "dpi": 300,
            "ratio": "1:1.6"
        },
        content_guidelines=["No public domain without added value", "No AI-generated without disclosure"],
        review_time_days=3
    ),
    Platform.APPLE_BOOKS: PlatformRequirements(
        platform=Platform.APPLE_BOOKS,
        supported_formats=[FileFormat.EPUB],
        supported_book_formats=[BookFormat.EBOOK, BookFormat.AUDIOBOOK],
        max_file_size_mb=2000,
        min_price=0.99,
        max_price=999.99,
        currency="USD",
        royalty_options={"70%": 0.70},
        required_metadata=["title", "author", "description", "categories"],
        cover_requirements={
            "min_short_side": 1400,
            "format": ["jpg", "png"],
            "rgb_only": True
        },
        content_guidelines=["Must be original content", "No hate speech"],
        review_time_days=5
    ),
    Platform.EMPIK: PlatformRequirements(
        platform=Platform.EMPIK,
        supported_formats=[FileFormat.EPUB, FileFormat.MOBI, FileFormat.PDF],
        supported_book_formats=[BookFormat.EBOOK, BookFormat.AUDIOBOOK],
        max_file_size_mb=500,
        min_price=4.99,
        max_price=999.99,
        currency="PLN",
        royalty_options={"35%": 0.35, "50%": 0.50},
        required_metadata=["title", "author", "description", "isbn"],
        cover_requirements={
            "min_width": 800,
            "min_height": 1200,
            "format": ["jpg"]
        },
        content_guidelines=["Polish language or translations", "No illegal content"],
        review_time_days=7
    ),
    Platform.LEGIMI: PlatformRequirements(
        platform=Platform.LEGIMI,
        supported_formats=[FileFormat.EPUB, FileFormat.MOBI],
        supported_book_formats=[BookFormat.EBOOK, BookFormat.AUDIOBOOK],
        max_file_size_mb=300,
        min_price=0.0,
        max_price=999.99,
        currency="PLN",
        royalty_options={"subscription": 0.50},
        required_metadata=["title", "author", "description"],
        cover_requirements={
            "min_width": 600,
            "format": ["jpg", "png"]
        },
        content_guidelines=["Subscription model available"],
        review_time_days=5
    )
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class PublishingIntegration:
    """
    Publishing Platform Integration

    Manages publishing to multiple platforms with automated
    formatting, metadata handling, and distribution tracking.
    """

    def __init__(self):
        self.credentials: Dict[str, PlatformCredentials] = {}
        self.submissions: Dict[str, PublishingSubmission] = {}
        self.sales_data: Dict[str, List[SalesData]] = {}
        self.platform_requirements = PLATFORM_REQUIREMENTS.copy()

    async def connect_platform(
        self,
        user_id: str,
        platform: Platform,
        api_key: str,
        api_secret: Optional[str] = None,
        account_id: str = ""
    ) -> PlatformCredentials:
        """
        Connect a publishing platform account.
        """
        # In production, this would verify credentials with the platform API
        credential = PlatformCredentials(
            credential_id=str(uuid.uuid4()),
            platform=platform,
            user_id=user_id,
            api_key=api_key,
            api_secret=api_secret,
            account_id=account_id,
            verified=True,  # Would be verified via API
            connected_at=datetime.now(),
            last_sync=None
        )

        key = f"{user_id}_{platform.value}"
        self.credentials[key] = credential

        return credential

    async def validate_metadata(
        self,
        platform: Platform,
        metadata: BookMetadata
    ) -> Dict[str, Any]:
        """
        Validate metadata against platform requirements.
        """
        requirements = self.platform_requirements.get(platform)
        if not requirements:
            return {"valid": False, "errors": ["Platform not supported"]}

        errors = []
        warnings = []

        # Check required fields
        metadata_dict = metadata.to_dict()
        for field in requirements.required_metadata:
            if field not in metadata_dict or not metadata_dict[field]:
                errors.append(f"Brakujące pole: {field}")

        # Check description length
        if len(metadata.description) < 100:
            warnings.append("Opis jest bardzo krótki - zalecane minimum 100 znaków")
        if len(metadata.description) > 4000:
            errors.append("Opis przekracza 4000 znaków")

        # Check keywords
        if len(metadata.keywords) < 3:
            warnings.append("Zalecane minimum 3 słowa kluczowe")
        if len(metadata.keywords) > 7:
            warnings.append("Więcej niż 7 słów kluczowych może być ignorowanych")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "platform": platform.value
        }

    async def prepare_submission(
        self,
        book_id: str,
        platform: Platform,
        metadata: BookMetadata,
        pricing: PricingConfig,
        format: BookFormat = BookFormat.EBOOK
    ) -> PublishingSubmission:
        """
        Prepare a book submission for a platform.
        """
        requirements = self.platform_requirements.get(platform)
        if not requirements:
            raise ValueError("Platform not supported")

        # Determine file format
        file_format = requirements.supported_formats[0]

        submission = PublishingSubmission(
            submission_id=str(uuid.uuid4()),
            book_id=book_id,
            platform=platform,
            format=format,
            file_format=file_format,
            metadata=metadata,
            pricing=pricing,
            status=PublishingStatus.DRAFT,
            submitted_at=datetime.now(),
            reviewed_at=None,
            published_at=None,
            platform_book_id=None,
            platform_url=None,
            rejection_reason=None,
            notes=[]
        )

        self.submissions[submission.submission_id] = submission

        return submission

    async def submit_to_platform(
        self,
        submission_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Submit a book to a publishing platform.
        """
        submission = self.submissions.get(submission_id)
        if not submission:
            raise ValueError("Submission not found")

        # Check credentials
        key = f"{user_id}_{submission.platform.value}"
        credential = self.credentials.get(key)
        if not credential:
            return {
                "success": False,
                "error": f"Brak połączenia z platformą {submission.platform.value}"
            }

        # Validate metadata
        validation = await self.validate_metadata(submission.platform, submission.metadata)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Nieprawidłowe metadane",
                "details": validation["errors"]
            }

        # In production, this would call the platform API
        # For now, simulate submission
        submission.status = PublishingStatus.PENDING_REVIEW
        submission.notes.append(f"Wysłano do {submission.platform.value}")

        return {
            "success": True,
            "submission_id": submission_id,
            "platform": submission.platform.value,
            "status": submission.status.value,
            "estimated_review_days": self.platform_requirements[submission.platform].review_time_days
        }

    async def check_submission_status(
        self,
        submission_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a submission.
        """
        submission = self.submissions.get(submission_id)
        if not submission:
            raise ValueError("Submission not found")

        # In production, this would query the platform API
        return {
            "submission_id": submission_id,
            "platform": submission.platform.value,
            "status": submission.status.value,
            "submitted_at": submission.submitted_at.isoformat(),
            "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
            "published_at": submission.published_at.isoformat() if submission.published_at else None,
            "platform_url": submission.platform_url,
            "notes": submission.notes
        }

    async def get_distribution_status(
        self,
        book_id: str
    ) -> DistributionStatus:
        """
        Get distribution status across all platforms.
        """
        book_submissions = {
            s.platform.value: s
            for s in self.submissions.values()
            if s.book_id == book_id
        }

        published = sum(1 for s in book_submissions.values() if s.status == PublishingStatus.PUBLISHED)
        pending = sum(1 for s in book_submissions.values() if s.status in [PublishingStatus.PENDING_REVIEW, PublishingStatus.IN_REVIEW])
        rejected = sum(1 for s in book_submissions.values() if s.status == PublishingStatus.REJECTED)

        # Get sales data
        total_sales = 0
        total_revenue = 0.0
        for sales_list in self.sales_data.get(book_id, []):
            total_sales += sales_list.units_sold - sales_list.units_returned
            total_revenue += sales_list.royalties_earned

        return DistributionStatus(
            book_id=book_id,
            platforms=book_submissions,
            total_platforms=len(book_submissions),
            published_count=published,
            pending_count=pending,
            rejected_count=rejected,
            total_sales=total_sales,
            total_revenue=total_revenue,
            last_updated=datetime.now()
        )

    async def get_sales_report(
        self,
        book_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get sales report for a book.
        """
        all_sales = self.sales_data.get(book_id, [])

        if start_date:
            all_sales = [s for s in all_sales if s.period_start >= start_date]
        if end_date:
            all_sales = [s for s in all_sales if s.period_end <= end_date]

        # Aggregate by platform
        by_platform = {}
        for sales in all_sales:
            platform = sales.platform.value
            if platform not in by_platform:
                by_platform[platform] = {
                    "units_sold": 0,
                    "units_returned": 0,
                    "revenue": 0.0,
                    "royalties": 0.0
                }
            by_platform[platform]["units_sold"] += sales.units_sold
            by_platform[platform]["units_returned"] += sales.units_returned
            by_platform[platform]["revenue"] += sales.revenue_gross
            by_platform[platform]["royalties"] += sales.royalties_earned

        # Totals
        total_units = sum(p["units_sold"] - p["units_returned"] for p in by_platform.values())
        total_revenue = sum(p["revenue"] for p in by_platform.values())
        total_royalties = sum(p["royalties"] for p in by_platform.values())

        return {
            "book_id": book_id,
            "period": {
                "start": start_date.isoformat() if start_date else "all_time",
                "end": end_date.isoformat() if end_date else "now"
            },
            "by_platform": by_platform,
            "totals": {
                "units_sold": total_units,
                "revenue_gross": total_revenue,
                "royalties_earned": total_royalties
            }
        }

    async def update_pricing(
        self,
        submission_id: str,
        new_pricing: PricingConfig
    ) -> Dict[str, Any]:
        """
        Update pricing for a published book.
        """
        submission = self.submissions.get(submission_id)
        if not submission:
            raise ValueError("Submission not found")

        old_price = submission.pricing.base_price
        submission.pricing = new_pricing
        submission.notes.append(f"Cena zmieniona z {old_price} na {new_pricing.base_price}")

        return {
            "success": True,
            "submission_id": submission_id,
            "old_price": old_price,
            "new_price": new_pricing.base_price,
            "platform": submission.platform.value
        }

    async def schedule_promotion(
        self,
        submission_id: str,
        promotional_price: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Schedule a price promotion.
        """
        submission = self.submissions.get(submission_id)
        if not submission:
            raise ValueError("Submission not found")

        submission.pricing.promotional_price = promotional_price
        submission.pricing.promotion_start = start_date
        submission.pricing.promotion_end = end_date

        submission.notes.append(
            f"Promocja zaplanowana: {promotional_price} od {start_date.date()} do {end_date.date()}"
        )

        return {
            "success": True,
            "submission_id": submission_id,
            "promotional_price": promotional_price,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

    def get_platform_requirements(self, platform: Platform) -> Optional[PlatformRequirements]:
        """Get requirements for a platform."""
        return self.platform_requirements.get(platform)

    def list_supported_platforms(self) -> List[Dict[str, Any]]:
        """List all supported platforms."""
        return [
            {
                "platform": p.value,
                "name": p.value.replace("_", " ").title(),
                "formats": [f.value for f in req.supported_formats],
                "book_formats": [f.value for f in req.supported_book_formats],
                "currency": req.currency,
                "review_days": req.review_time_days
            }
            for p, req in self.platform_requirements.items()
        ]

    def list_connected_platforms(self, user_id: str) -> List[Dict[str, Any]]:
        """List connected platforms for a user."""
        connected = [
            cred for key, cred in self.credentials.items()
            if cred.user_id == user_id
        ]
        return [c.to_dict() for c in connected]

    def get_submission(self, submission_id: str) -> Optional[PublishingSubmission]:
        """Get a submission by ID."""
        return self.submissions.get(submission_id)

    def list_submissions(self, book_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List submissions."""
        submissions = self.submissions.values()

        if book_id:
            submissions = [s for s in submissions if s.book_id == book_id]

        return [s.to_dict() for s in submissions]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_publishing_integration: Optional[PublishingIntegration] = None


def get_publishing_integration() -> PublishingIntegration:
    """Get the singleton publishing integration instance."""
    global _publishing_integration
    if _publishing_integration is None:
        _publishing_integration = PublishingIntegration()
    return _publishing_integration
