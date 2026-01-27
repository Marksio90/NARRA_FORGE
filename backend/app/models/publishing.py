"""
Publishing metadata model for commercial book sales

Supports:
- ISBN management
- Category/keyword metadata
- Pricing in multiple currencies
- Cover information
- Platform-specific IDs (Amazon, etc.)
- Sales tracking
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class PublishingMetadata(Base):
    """
    Publishing metadata for book sales on various platforms.
    One-to-one relationship with Project.
    """
    __tablename__ = "publishing_metadata"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)

    # ISBN numbers
    isbn_13 = Column(String(17), unique=True, nullable=True)  # With hyphens: 978-X-XXXX-XXXX-X
    isbn_10 = Column(String(13), unique=True, nullable=True)  # Legacy format
    asin = Column(String(20), nullable=True)  # Amazon Standard Identification Number

    # Categories (BISAC codes for US, THEMA for international)
    primary_category = Column(String(100), nullable=True)
    secondary_categories = Column(JSONB, nullable=True, default=list)  # [category_code1, category_code2]
    thema_codes = Column(JSONB, nullable=True, default=list)  # International classification

    # Keywords for discoverability (max 7 for Amazon)
    keywords = Column(JSONB, nullable=True, default=list)  # [keyword1, keyword2, ...]

    # Pricing in multiple currencies
    price_usd = Column(Float, nullable=True)
    price_eur = Column(Float, nullable=True)
    price_gbp = Column(Float, nullable=True)
    price_pln = Column(Float, nullable=True)

    # Royalty settings
    royalty_type = Column(String(20), default="70_percent")  # 35_percent or 70_percent
    kdp_select_enrolled = Column(Boolean, default=False)  # Kindle Unlimited enrollment

    # Cover
    cover_image_url = Column(String(500), nullable=True)
    cover_image_path = Column(String(500), nullable=True)  # Local path
    cover_designer = Column(String(255), nullable=True)
    cover_generated_by_ai = Column(Boolean, default=False)

    # Marketing copy
    book_description = Column(Text, nullable=True)  # Back cover blurb (max 4000 chars for Amazon)
    editorial_review = Column(Text, nullable=True)  # Professional review quote
    author_bio = Column(Text, nullable=True)
    tagline = Column(String(255), nullable=True)  # One-liner hook

    # Series info (for marketing)
    series_name = Column(String(255), nullable=True)
    series_position = Column(Integer, nullable=True)

    # Content ratings
    age_rating = Column(String(20), nullable=True)  # e.g., "General", "13+", "18+"
    content_warnings = Column(JSONB, nullable=True, default=list)  # [warning1, warning2]
    is_adult_content = Column(Boolean, default=False)

    # Publishing status
    is_published = Column(Boolean, default=False)
    publication_date = Column(DateTime, nullable=True)
    first_publication_date = Column(DateTime, nullable=True)

    # Copyright
    copyright_holder = Column(String(255), nullable=True)
    copyright_year = Column(Integer, nullable=True)
    rights_territory = Column(String(100), default="Worldwide")
    language = Column(String(10), default="pl")  # ISO 639-1

    # Physical book specs (for print-on-demand)
    page_count = Column(Integer, nullable=True)
    trim_size = Column(String(20), nullable=True)  # e.g., "6x9", "5.5x8.5"
    paper_type = Column(String(20), nullable=True)  # cream, white

    # Platform-specific IDs
    kdp_book_id = Column(String(100), nullable=True)  # Amazon KDP
    draft2digital_id = Column(String(100), nullable=True)
    smashwords_id = Column(String(100), nullable=True)
    apple_books_id = Column(String(100), nullable=True)
    kobo_id = Column(String(100), nullable=True)
    google_play_id = Column(String(100), nullable=True)
    empik_id = Column(String(100), nullable=True)
    legimi_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="publishing_metadata")
    sales_records = relationship("SalesTracking", back_populates="publishing_metadata", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_publishing_isbn', 'isbn_13'),
        Index('idx_publishing_project', 'project_id'),
    )

    def get_amazon_description(self) -> str:
        """Get description formatted for Amazon (max 4000 chars)"""
        if not self.book_description:
            return ""
        return self.book_description[:4000]

    def get_keywords_for_amazon(self) -> list:
        """Get keywords formatted for Amazon (max 7)"""
        if not self.keywords:
            return []
        return self.keywords[:7]

    def is_ready_for_publishing(self) -> bool:
        """Check if metadata is complete for publishing"""
        required_fields = [
            self.book_description,
            self.primary_category,
            self.price_usd or self.price_pln,
            self.copyright_holder,
            self.cover_image_url or self.cover_image_path,
        ]
        return all(required_fields)

    def __repr__(self):
        return f"<PublishingMetadata(project_id={self.project_id}, isbn={self.isbn_13})>"


class SalesTracking(Base):
    """
    Track sales across platforms over time.
    Allows for analytics and royalty tracking.
    """
    __tablename__ = "sales_tracking"

    id = Column(Integer, primary_key=True, index=True)
    publishing_metadata_id = Column(Integer, ForeignKey("publishing_metadata.id", ondelete="CASCADE"), nullable=False)

    # Platform
    platform = Column(String(50), nullable=False)  # kdp, apple, kobo, empik, etc.

    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Sales data
    units_sold = Column(Integer, default=0, nullable=False)
    units_returned = Column(Integer, default=0, nullable=False)
    pages_read = Column(Integer, default=0, nullable=False)  # For Kindle Unlimited

    # Revenue
    gross_revenue = Column(Float, default=0.0, nullable=False)
    royalty_earned = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Rankings
    best_rank = Column(Integer, nullable=True)
    average_rank = Column(Integer, nullable=True)
    category_rank = Column(Integer, nullable=True)

    # Reviews
    new_reviews = Column(Integer, default=0, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, nullable=True)

    # Synced timestamp
    synced_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    publishing_metadata = relationship("PublishingMetadata", back_populates="sales_records")

    # Indexes
    __table_args__ = (
        Index('idx_sales_platform', 'platform'),
        Index('idx_sales_period', 'period_start', 'period_end'),
    )

    def __repr__(self):
        return f"<SalesTracking(platform={self.platform}, units={self.units_sold}, revenue=${self.gross_revenue})>"


# BISAC Category codes for common fiction genres
BISAC_CATEGORIES = {
    "fantasy": {
        "primary": "FIC009020",  # FICTION / Fantasy / Epic
        "secondary": [
            "FIC009000",  # FICTION / Fantasy / General
            "FIC009030",  # FICTION / Fantasy / Historical
        ]
    },
    "sci-fi": {
        "primary": "FIC028000",  # FICTION / Science Fiction / General
        "secondary": [
            "FIC028010",  # FICTION / Science Fiction / Action & Adventure
            "FIC028020",  # FICTION / Science Fiction / Hard Science Fiction
        ]
    },
    "thriller": {
        "primary": "FIC031000",  # FICTION / Thrillers / General
        "secondary": [
            "FIC031010",  # FICTION / Thrillers / Crime
            "FIC031080",  # FICTION / Thrillers / Psychological
        ]
    },
    "horror": {
        "primary": "FIC015000",  # FICTION / Horror
        "secondary": [
            "FIC015010",  # FICTION / Horror / Supernatural
            "FIC015020",  # FICTION / Horror / Occult
        ]
    },
    "romance": {
        "primary": "FIC027000",  # FICTION / Romance / General
        "secondary": [
            "FIC027020",  # FICTION / Romance / Contemporary
            "FIC027250",  # FICTION / Romance / Paranormal / General
        ]
    },
    "mystery": {
        "primary": "FIC022000",  # FICTION / Mystery & Detective / General
        "secondary": [
            "FIC022020",  # FICTION / Mystery & Detective / Amateur Sleuth
            "FIC022040",  # FICTION / Mystery & Detective / Police Procedural
        ]
    },
    "drama": {
        "primary": "FIC019000",  # FICTION / Literary
        "secondary": [
            "FIC045000",  # FICTION / Family Life / General
            "FIC066000",  # FICTION / Small Town & Rural
        ]
    },
    "comedy": {
        "primary": "FIC016000",  # FICTION / Humorous / General
        "secondary": [
            "FIC016010",  # FICTION / Humorous / Black Humor
            "FIC016020",  # FICTION / Satire
        ]
    },
}


def get_bisac_for_genre(genre: str) -> dict:
    """Get BISAC category codes for a genre"""
    return BISAC_CATEGORIES.get(genre.lower(), BISAC_CATEGORIES["drama"])
