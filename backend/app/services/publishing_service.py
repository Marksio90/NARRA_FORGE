"""
Publishing service for commercial book sales

Handles:
- Publishing metadata management
- ISBN generation (mock for development)
- AI cover generation
- KDP/platform export preparation
- Marketing copy generation
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import os
from io import BytesIO

from app.models.project import Project
from app.models.publishing import PublishingMetadata, SalesTracking, get_bisac_for_genre
from app.agents.model_tier_manager import model_tier_manager
from app.config import settings

logger = logging.getLogger(__name__)


class PublishingService:
    """Service for managing book publishing and sales"""

    def __init__(self):
        self.model_manager = model_tier_manager

    def get_or_create_metadata(
        self,
        db: Session,
        project_id: int
    ) -> PublishingMetadata:
        """Get existing or create new publishing metadata for a project"""
        metadata = db.query(PublishingMetadata).filter(
            PublishingMetadata.project_id == project_id
        ).first()

        if not metadata:
            metadata = PublishingMetadata(project_id=project_id)
            db.add(metadata)
            db.commit()
            db.refresh(metadata)

        return metadata

    def update_metadata(
        self,
        db: Session,
        project_id: int,
        **kwargs
    ) -> PublishingMetadata:
        """Update publishing metadata fields"""
        metadata = self.get_or_create_metadata(db, project_id)

        for key, value in kwargs.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        db.commit()
        db.refresh(metadata)
        return metadata

    def generate_isbn(
        self,
        db: Session,
        project_id: int,
        title: str,
        author: str
    ) -> str:
        """
        Generate ISBN-13 for a book.

        NOTE: Real implementation requires Bowker/Nielsen account.
        This generates a mock ISBN for development purposes.
        """
        import random

        # ISBN-13 format: 978-X-XXXX-XXXX-X
        # 978 = Book prefix
        # X = Registration group (83 for Poland)
        # XXXX = Registrant element (publisher)
        # XXXX = Publication element (title)
        # X = Check digit

        # Generate random mock ISBN
        prefix = "978"
        group = "83"  # Poland
        registrant = str(random.randint(1000, 9999))
        publication = str(random.randint(1000, 9999))

        # Calculate check digit
        isbn_12 = f"{prefix}{group}{registrant}{publication}"
        check_digit = self._calculate_isbn_check_digit(isbn_12)

        isbn = f"{prefix}-{group}-{registrant}-{publication}-{check_digit}"

        # Update metadata
        metadata = self.get_or_create_metadata(db, project_id)
        metadata.isbn_13 = isbn
        db.commit()

        logger.info(f"Generated ISBN {isbn} for project {project_id}")
        return isbn

    def _calculate_isbn_check_digit(self, isbn_12: str) -> str:
        """Calculate ISBN-13 check digit"""
        if len(isbn_12) != 12:
            raise ValueError("ISBN-12 must be 12 digits")

        total = 0
        for i, digit in enumerate(isbn_12):
            multiplier = 1 if i % 2 == 0 else 3
            total += int(digit) * multiplier

        check_digit = (10 - (total % 10)) % 10
        return str(check_digit)

    def validate_isbn(self, isbn: str) -> bool:
        """Validate ISBN-13 checksum"""
        isbn_clean = isbn.replace('-', '').replace(' ', '')

        if len(isbn_clean) != 13:
            return False

        if not isbn_clean.isdigit():
            return False

        calculated_check = self._calculate_isbn_check_digit(isbn_clean[:12])
        return calculated_check == isbn_clean[-1]

    async def generate_book_description(
        self,
        db: Session,
        project_id: int,
        max_length: int = 4000
    ) -> str:
        """
        Generate marketing description (back cover blurb) using AI.
        Optimized for Amazon's 4000 character limit.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")

        # Gather context
        context_parts = [f"Title: {project.name}", f"Genre: {project.genre.value if project.genre else 'Unknown'}"]

        if project.plot_structure:
            if hasattr(project.plot_structure, 'main_conflict'):
                context_parts.append(f"Main Conflict: {project.plot_structure.main_conflict}")

        if project.characters:
            main_chars = [c for c in project.characters[:3]]  # Get first 3 characters
            char_names = [c.name for c in main_chars]
            context_parts.append(f"Main Characters: {', '.join(char_names)}")

        context = "\n".join(context_parts)

        prompt = f"""Napisz chwytliwy opis książki (back cover blurb) w stylu bestsellerów.

KONTEKST:
{context}

WYMAGANIA:
1. Maksymalnie 300 słów
2. Zacznij od HOOK - zdanie przyciągające uwagę
3. Przedstaw główny konflikt bez spoilerów
4. Zaakcentuj emocjonalną stawkę
5. Zakończ pytaniem lub intrygującym niedopowiedzeniem
6. Użyj aktywnego głosu i mocnych czasowników
7. NIE zdradzaj zakończenia!

FORMAT:
- 2-3 akapity
- Krótkie, dynamiczne zdania
- Bezpośredni zwrot do czytelnika

Napisz opis:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert book marketing copywriter specializing in bestseller descriptions.",
            task_type="metadata",
            temperature=0.8,
            max_tokens=600
        )

        description = result.get("content", "")[:max_length] if result.get("success") else ""

        # Save to metadata
        if description:
            metadata = self.get_or_create_metadata(db, project_id)
            metadata.book_description = description
            db.commit()

        return description

    async def generate_keywords(
        self,
        db: Session,
        project_id: int,
        num_keywords: int = 7
    ) -> List[str]:
        """
        Generate keywords for discoverability.
        Amazon allows max 7 keywords.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")

        prompt = f"""Wygeneruj {num_keywords} słów kluczowych dla książki do wyszukiwania na Amazon/platformach sprzedażowych.

Tytuł: {project.name}
Gatunek: {project.genre.value if project.genre else 'Fiction'}

WYMAGANIA:
1. Słowa kluczowe powinny być tym, czego szukają czytelnicy
2. Mieszaj ogólne ("fantasy novel") ze specyficznymi ("dark lord redemption")
3. Uwzględnij tropes i motywy
4. Uwzględnij porównania ("fans of Brandon Sanderson")
5. NIE powtarzaj tytułu ani gatunku dosłownie

Odpowiedz TYLKO listą słów kluczowych, po jednym na linię:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert in book marketing and Amazon SEO.",
            task_type="metadata",
            temperature=0.7,
            max_tokens=300
        )

        if result.get("success"):
            content = result["content"]
            keywords = [kw.strip().strip('-').strip('•').strip() for kw in content.split('\n') if kw.strip()]
            keywords = keywords[:num_keywords]
        else:
            keywords = []

        # Save to metadata
        if keywords:
            metadata = self.get_or_create_metadata(db, project_id)
            metadata.keywords = keywords
            db.commit()

        return keywords

    def set_categories_for_genre(
        self,
        db: Session,
        project_id: int,
        genre: str
    ) -> Dict[str, Any]:
        """Set BISAC categories based on genre"""
        bisac = get_bisac_for_genre(genre)

        metadata = self.get_or_create_metadata(db, project_id)
        metadata.primary_category = bisac["primary"]
        metadata.secondary_categories = bisac["secondary"]
        db.commit()

        return {
            "primary": bisac["primary"],
            "secondary": bisac["secondary"]
        }

    async def generate_cover_prompt(
        self,
        db: Session,
        project_id: int
    ) -> str:
        """
        Generate a detailed prompt for AI cover generation.
        Can be used with DALL-E, Midjourney, or similar.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")

        metadata = self.get_or_create_metadata(db, project_id)

        # Build context
        genre = project.genre.value if project.genre else "fiction"
        title = project.name
        description = metadata.book_description or ""

        prompt = f"""Stwórz szczegółowy prompt do wygenerowania okładki książki przez AI (DALL-E/Midjourney).

Tytuł: {title}
Gatunek: {genre}
Opis: {description[:500]}

Stwórz prompt który:
1. Opisuje główny element wizualny (postać, obiekt, scena)
2. Określa styl artystyczny (realistyczny, painted, minimalistyczny)
3. Określa paletę kolorów
4. Sugeruje nastrój/atmosferę
5. NIE zawiera tekstu (tekst będzie dodany osobno)
6. Jest zoptymalizowany dla formatu okładki (portrait 6:9)

WAŻNE: Prompt w języku angielskim dla lepszej kompatybilności z AI.

Prompt:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert in book cover design and AI image generation prompts.",
            task_type="metadata",
            temperature=0.8,
            max_tokens=500
        )

        return result.get("content", "") if result.get("success") else ""

    def prepare_kdp_export(
        self,
        db: Session,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Prepare all data needed for KDP (Amazon) publishing.
        Returns a dict with all required fields.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")

        metadata = self.get_or_create_metadata(db, project_id)

        # Check if ready for publishing
        missing_fields = []
        if not metadata.book_description:
            missing_fields.append("book_description")
        if not metadata.primary_category:
            missing_fields.append("primary_category")
        if not (metadata.price_usd or metadata.price_pln):
            missing_fields.append("price")
        if not metadata.copyright_holder:
            missing_fields.append("copyright_holder")

        if missing_fields:
            return {
                "ready": False,
                "missing_fields": missing_fields,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }

        # Prepare KDP data
        kdp_data = {
            "ready": True,
            "book_details": {
                "title": project.name,
                "subtitle": metadata.tagline or "",
                "series_name": metadata.series_name,
                "series_number": metadata.series_position,
                "language": metadata.language or "pl",
                "description": metadata.get_amazon_description(),
            },
            "author": {
                "name": metadata.copyright_holder,
                "bio": metadata.author_bio or "",
            },
            "categories": {
                "primary": metadata.primary_category,
                "secondary": metadata.secondary_categories or [],
            },
            "keywords": metadata.get_keywords_for_amazon(),
            "pricing": {
                "list_price_usd": metadata.price_usd or 2.99,
                "list_price_eur": metadata.price_eur or 2.99,
                "list_price_gbp": metadata.price_gbp or 2.49,
                "royalty_plan": metadata.royalty_type or "70_percent",
            },
            "content": {
                "adult_content": metadata.is_adult_content,
                "age_rating": metadata.age_rating or "General",
            },
            "rights": {
                "copyright_holder": metadata.copyright_holder,
                "copyright_year": metadata.copyright_year or datetime.now().year,
                "territories": metadata.rights_territory or "Worldwide",
            },
            "isbn": metadata.isbn_13,
            "cover": {
                "url": metadata.cover_image_url,
                "path": metadata.cover_image_path,
            }
        }

        return kdp_data

    def prepare_draft2digital_export(
        self,
        db: Session,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Prepare data for Draft2Digital distribution.
        D2D distributes to Apple, Kobo, B&N, and 30+ retailers.
        """
        # Similar to KDP but with D2D-specific fields
        kdp_data = self.prepare_kdp_export(db, project_id)

        if not kdp_data.get("ready"):
            return kdp_data

        # D2D uses different category system
        d2d_data = kdp_data.copy()
        d2d_data["distribution"] = {
            "apple_books": True,
            "kobo": True,
            "barnes_noble": True,
            "overdrive": True,
            "scribd": True,
            "tolino": True,
        }

        return d2d_data

    def record_sale(
        self,
        db: Session,
        project_id: int,
        platform: str,
        units: int,
        revenue: float,
        royalty: float,
        currency: str = "USD",
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> SalesTracking:
        """Record a sales entry for tracking"""
        metadata = self.get_or_create_metadata(db, project_id)

        now = datetime.utcnow()
        record = SalesTracking(
            publishing_metadata_id=metadata.id,
            platform=platform,
            period_start=period_start or now,
            period_end=period_end or now,
            units_sold=units,
            gross_revenue=revenue,
            royalty_earned=royalty,
            currency=currency
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    def get_sales_summary(
        self,
        db: Session,
        project_id: int
    ) -> Dict[str, Any]:
        """Get sales summary for a book"""
        metadata = db.query(PublishingMetadata).filter(
            PublishingMetadata.project_id == project_id
        ).first()

        if not metadata:
            return {"total_units": 0, "total_revenue": 0, "platforms": {}}

        records = db.query(SalesTracking).filter(
            SalesTracking.publishing_metadata_id == metadata.id
        ).all()

        total_units = sum(r.units_sold for r in records)
        total_revenue = sum(r.gross_revenue for r in records)
        total_royalty = sum(r.royalty_earned for r in records)

        platforms = {}
        for record in records:
            if record.platform not in platforms:
                platforms[record.platform] = {"units": 0, "revenue": 0, "royalty": 0}
            platforms[record.platform]["units"] += record.units_sold
            platforms[record.platform]["revenue"] += record.gross_revenue
            platforms[record.platform]["royalty"] += record.royalty_earned

        return {
            "total_units": total_units,
            "total_revenue": round(total_revenue, 2),
            "total_royalty": round(total_royalty, 2),
            "platforms": platforms,
            "records_count": len(records)
        }

    def mark_as_published(
        self,
        db: Session,
        project_id: int,
        platform: str,
        platform_id: str
    ) -> PublishingMetadata:
        """Mark book as published on a platform"""
        metadata = self.get_or_create_metadata(db, project_id)

        # Set publication date if first publish
        if not metadata.is_published:
            metadata.is_published = True
            metadata.publication_date = datetime.utcnow()
            metadata.first_publication_date = datetime.utcnow()

        # Set platform-specific ID
        platform_field_map = {
            "kdp": "kdp_book_id",
            "amazon": "kdp_book_id",
            "draft2digital": "draft2digital_id",
            "d2d": "draft2digital_id",
            "smashwords": "smashwords_id",
            "apple": "apple_books_id",
            "kobo": "kobo_id",
            "google": "google_play_id",
            "empik": "empik_id",
            "legimi": "legimi_id",
        }

        field = platform_field_map.get(platform.lower())
        if field:
            setattr(metadata, field, platform_id)

        db.commit()
        db.refresh(metadata)

        logger.info(f"Marked project {project_id} as published on {platform}")
        return metadata


# Singleton instance
publishing_service = PublishingService()
