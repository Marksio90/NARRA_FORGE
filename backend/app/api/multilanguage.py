"""
Multi-Language Generation API - NarraForge 3.0 Phase 4
Endpoints for multi-language book generation and translation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.multilanguage import (
    multi_language_generator,
    Language,
    TranslationMode,
    ContentType,
    QualityLevel,
    FileFormat
)

router = APIRouter(prefix="/multilanguage")


# Request/Response Models
class TranslationProjectRequest(BaseModel):
    """Request to create a translation project"""
    project_id: str
    source_language: str = "pl"
    target_languages: List[str]
    translation_mode: str = "hybrid"
    quality_level: str = "professional"
    preserve_style: bool = True
    cultural_adaptation: bool = True


class TranslationProjectResponse(BaseModel):
    """Translation project response"""
    success: bool
    project: Optional[Dict[str, Any]] = None
    message: str = ""


class ChapterTranslationRequest(BaseModel):
    """Request to translate a chapter"""
    chapter_id: str
    chapter_title: str
    content: str
    target_language: str
    character_names: Optional[Dict[str, str]] = None


class ChapterTranslationResponse(BaseModel):
    """Chapter translation response"""
    success: bool
    translation: Optional[Dict[str, Any]] = None
    message: str = ""


class GlossaryRequest(BaseModel):
    """Request to add glossary terms"""
    terms: Dict[str, str]
    domain: str = "literary"


class LanguageSupportResponse(BaseModel):
    """Language support information"""
    languages: List[Dict[str, Any]]
    total_count: int


class TranslationStatsResponse(BaseModel):
    """Translation statistics"""
    success: bool
    stats: Dict[str, Any]


class ExportRequest(BaseModel):
    """Request to export translation"""
    target_language: str
    file_format: str = "docx"
    include_original: bool = False


# Endpoints

@router.post("/projects/create", response_model=TranslationProjectResponse)
async def create_translation_project(request: TranslationProjectRequest):
    """
    Create a new translation project

    Creates a multi-language translation project with specified
    source and target languages, translation settings, and quality level.
    """
    try:
        # Convert string to enums
        source_lang = Language(request.source_language)
        target_langs = [Language(lang) for lang in request.target_languages]
        mode = TranslationMode(request.translation_mode)
        quality = QualityLevel(request.quality_level)

        project = multi_language_generator.create_translation_project(
            project_id=request.project_id,
            source_language=source_lang,
            target_languages=target_langs,
            translation_mode=mode,
            quality_level=quality,
            preserve_style=request.preserve_style,
            cultural_adaptation=request.cultural_adaptation
        )

        return TranslationProjectResponse(
            success=True,
            project=project.to_dict(),
            message=f"Translation project created for {len(target_langs)} languages"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")


@router.get("/projects/{project_id}", response_model=TranslationProjectResponse)
async def get_translation_project(project_id: str):
    """Get translation project details"""
    try:
        project = multi_language_generator.get_project(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return TranslationProjectResponse(
            success=True,
            project=project.to_dict(),
            message="Project retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/translate-chapter", response_model=ChapterTranslationResponse)
async def translate_chapter(
    project_id: str,
    request: ChapterTranslationRequest,
    background_tasks: BackgroundTasks
):
    """
    Translate a chapter to specified target language

    Performs high-quality literary translation with:
    - Style preservation
    - Cultural adaptation
    - Character name mapping
    - Idiom localization
    """
    try:
        target_lang = Language(request.target_language)

        translation = multi_language_generator.translate_chapter(
            project_id=project_id,
            chapter_id=request.chapter_id,
            chapter_title=request.chapter_title,
            content=request.content,
            target_language=target_lang,
            character_name_mapping=request.character_names
        )

        return ChapterTranslationResponse(
            success=True,
            translation=translation.to_dict(),
            message=f"Chapter translated to {target_lang.value}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/projects/{project_id}/glossary")
async def add_glossary_terms(project_id: str, request: GlossaryRequest):
    """Add glossary terms to a translation project"""
    try:
        multi_language_generator.add_glossary_terms(
            project_id=project_id,
            terms=request.terms,
            domain=request.domain
        )

        return {
            "success": True,
            "message": f"Added {len(request.terms)} glossary terms",
            "terms_count": len(request.terms)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/character-names")
async def set_character_name_mappings(
    project_id: str,
    mappings: Dict[str, Dict[str, str]]
):
    """
    Set character name mappings for translation

    Example:
    {
        "Jan Kowalski": {
            "en": "John Smith",
            "de": "Johann Schmidt"
        }
    }
    """
    try:
        multi_language_generator.set_character_mappings(
            project_id=project_id,
            mappings=mappings
        )

        return {
            "success": True,
            "message": f"Set mappings for {len(mappings)} characters"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages", response_model=LanguageSupportResponse)
async def get_supported_languages():
    """Get all supported languages with their profiles"""
    try:
        languages = multi_language_generator.get_supported_languages()

        return LanguageSupportResponse(
            languages=languages,
            total_count=len(languages)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages/{language_code}/profile")
async def get_language_profile(language_code: str):
    """Get detailed profile for a specific language"""
    try:
        language = Language(language_code)
        profile = multi_language_generator.get_language_profile(language)

        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for {language_code}"
            )

        return {
            "success": True,
            "profile": profile.to_dict()
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid language: {language_code}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/stats", response_model=TranslationStatsResponse)
async def get_translation_stats(project_id: str):
    """Get translation statistics for a project"""
    try:
        stats = multi_language_generator.get_translation_stats(project_id)

        return TranslationStatsResponse(
            success=True,
            stats=stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/export")
async def export_translation(project_id: str, request: ExportRequest):
    """Export translation to specified format"""
    try:
        target_lang = Language(request.target_language)
        file_format = FileFormat(request.file_format)

        export_data = multi_language_generator.export_translation(
            project_id=project_id,
            target_language=target_lang,
            file_format=file_format,
            include_original=request.include_original
        )

        return {
            "success": True,
            "export": export_data,
            "message": f"Export prepared in {file_format.value} format"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/validate")
async def validate_translation(project_id: str, target_language: str):
    """Validate translation quality and consistency"""
    try:
        target_lang = Language(target_language)

        validation = multi_language_generator.validate_translation(
            project_id=project_id,
            target_language=target_lang
        )

        return {
            "success": True,
            "validation": validation,
            "is_valid": validation.get("is_valid", False)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/memory")
async def get_translation_memory(project_id: str, target_language: str):
    """Get translation memory for a project and language"""
    try:
        target_lang = Language(target_language)

        memory = multi_language_generator.get_translation_memory(
            project_id=project_id,
            target_language=target_lang
        )

        return {
            "success": True,
            "memory": memory.to_dict() if memory else None,
            "segments_count": len(memory.segments) if memory else 0
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-text")
async def analyze_text_for_translation(
    text: str,
    source_language: str = "pl",
    target_language: str = "en"
):
    """
    Analyze text for translation complexity

    Returns difficulty assessment, potential challenges,
    and recommended translation approach.
    """
    try:
        source_lang = Language(source_language)
        target_lang = Language(target_language)

        analysis = multi_language_generator.analyze_translation_complexity(
            text=text,
            source_language=source_lang,
            target_language=target_lang
        )

        return {
            "success": True,
            "analysis": analysis
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
