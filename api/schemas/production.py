"""
Strongly-typed Pydantic schemas for production briefs.

This replaces Dict[str, Any] with type-safe schemas that:
1. Validate input at runtime
2. Generate accurate OpenAPI documentation
3. Auto-generate TypeScript types (SINGLE SOURCE OF TRUTH)
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from api.schemas.enums import ProductionType, Genre


class ProductionBriefSchema(BaseModel):
    """
    Production brief for narrative generation.

    This is the SINGLE SOURCE OF TRUTH for production brief structure.
    Frontend TypeScript types are auto-generated from this schema.

    Example:
        {
            "production_type": "short_story",
            "genre": "fantasy",
            "subject": "A wizard's apprentice discovers forbidden magic",
            "target_length": 5000,
            "style_instructions": "Dark and mysterious tone with vivid imagery",
            "character_count": 3
        }
    """

    production_type: ProductionType = Field(
        ...,
        description="Type of production to generate"
    )

    genre: Genre = Field(
        ...,
        description="Genre/category of the narrative"
    )

    subject: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Main subject/premise of the narrative",
        examples=["A detective investigates a series of mysterious disappearances in a small coastal town"]
    )

    target_length: int = Field(
        default=5000,
        ge=100,
        le=200000,
        description="Target word count for the narrative"
    )

    style_instructions: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Style, tone, or special instructions for the narrative",
        examples=["Write in first person with a noir detective tone"]
    )

    character_count: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Approximate number of main characters"
    )

    setting_period: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Time period or setting (e.g., '1920s Chicago', 'Future Mars Colony')",
        examples=["Victorian England", "Post-apocalyptic 2150"]
    )

    pov: Optional[str] = Field(
        default="third_person",
        description="Point of view (first_person, third_person_limited, third_person_omniscient)",
        examples=["first_person", "third_person_limited"]
    )

    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Validate subject is not just whitespace."""
        if not v.strip():
            raise ValueError("Subject cannot be empty or just whitespace")
        return v.strip()

    @field_validator('style_instructions')
    @classmethod
    def validate_style_instructions(cls, v: Optional[str]) -> Optional[str]:
        """Clean up style instructions."""
        if v is None:
            return None
        v = v.strip()
        return v if v else None

    @field_validator('target_length')
    @classmethod
    def validate_target_length(cls, v: int, info) -> int:
        """Validate target length is reasonable for production type."""
        production_type = info.data.get('production_type')

        if production_type == ProductionType.SHORT_STORY and v > 15000:
            raise ValueError("Short stories should be under 15,000 words")
        elif production_type == ProductionType.NOVELLA and v < 15000:
            raise ValueError("Novellas should be at least 15,000 words")
        elif production_type == ProductionType.NOVEL and v < 40000:
            raise ValueError("Novels should be at least 40,000 words")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "production_type": "short_story",
                    "genre": "fantasy",
                    "subject": "A young mage discovers an ancient artifact that threatens to unravel reality",
                    "target_length": 5000,
                    "style_instructions": "Dark fantasy with rich world-building and moral ambiguity",
                    "character_count": 3,
                    "setting_period": "Medieval-inspired fantasy world",
                    "pov": "third_person_limited"
                },
                {
                    "production_type": "screenplay",
                    "genre": "thriller",
                    "subject": "A journalist uncovers a conspiracy at the highest levels of government",
                    "target_length": 25000,
                    "style_instructions": "Fast-paced, tense dialogue with plot twists",
                    "character_count": 5,
                    "setting_period": "Present day Washington DC",
                    "pov": "third_person"
                }
            ]
        }
    }


class NarrativeOutputSchema(BaseModel):
    """
    Strongly-typed schema for narrative generation output.

    Replaces Dict[str, Any] in job.output field.
    """

    narrative_text: str = Field(
        ...,
        description="The complete generated narrative text"
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Generated title for the narrative"
    )

    word_count: int = Field(
        ...,
        ge=0,
        description="Total word count of the narrative"
    )

    metadata: NarrativeMetadataSchema = Field(
        default_factory=NarrativeMetadataSchema,
        description="Narrative metadata (characters, structure, etc.)"
    )

    quality_metrics: Optional[QualityMetricsSchema] = Field(
        default=None,
        description="Quality assessment metrics"
    )

    generation_metadata: dict = Field(
        default_factory=dict,
        description="Metadata about generation process (model, tokens, etc.)"
    )

    model_config = {"from_attributes": True}


class CharacterSchema(BaseModel):
    """Character metadata schema."""
    name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., description="Character role (protagonist, antagonist, supporting)")
    description: str = Field(..., description="Character description")
    traits: Optional[List[str]] = None
    backstory: Optional[str] = None


class NarrativeMetadataSchema(BaseModel):
    """Strongly-typed metadata for narratives."""
    characters: List[CharacterSchema] = Field(default_factory=list)
    structure: dict = Field(
        default_factory=dict,
        description="Narrative structure (acts, chapters, scenes)"
    )
    segments: List[dict] = Field(
        default_factory=list,
        description="Individual narrative segments"
    )
    themes: Optional[List[str]] = None
    setting_details: Optional[dict] = None


class QualityMetricsSchema(BaseModel):
    """Quality metrics for narrative assessment."""
    coherence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    logic_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    character_consistency_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    pacing_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    dialogue_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    overall_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: Optional[List[str]] = None
