"""
API Router dla zadań generowania książek - NarraForge.

Endpointy:
- POST /jobs - Tworzenie nowego zadania
- GET /jobs - Lista wszystkich zadań
- GET /jobs/{job_id} - Szczegóły zadania
- GET /jobs/{job_id}/result - Pełny wynik (świat, postacie, fabuła, proza)
- DELETE /jobs/{job_id} - Usunięcie zadania
"""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db import get_async_session
from core.logging import get_logger
from models.schema import Character, Job, Plot, ProseChunk, World
from services.tasks import generate_book_task

logger = get_logger(__name__)
router = APIRouter()


# === Pydantic Models (Request/Response) ===


class CreateJobRequest(BaseModel):
    """Request do tworzenia nowego zadania."""

    gatunek: str = Field(
        ...,
        description="Gatunek literacki (fantasy, sci-fi, thriller, romans, horror, itd.)",
        min_length=2,
        max_length=100,
    )
    inspiracja: str = Field(
        ...,
        description="Inspiracja dla świata i historii",
        min_length=10,
        max_length=2000,
    )
    liczba_glownych_postaci: int = Field(
        default=3,
        description="Liczba głównych postaci (2-5)",
        ge=2,
        le=5,
    )
    docelowa_dlugosc: str = Field(
        default="srednia",
        description="Długość książki: 'krótka' (8-12 scen), 'srednia' (15-20 scen), 'długa' (25+ scen)",
        pattern="^(krótka|srednia|długa)$",
    )
    styl_narracji: str = Field(
        default="literacki",
        description="Styl narracji: 'literacki', 'poetycki', 'dynamiczny', 'noir'",
        pattern="^(literacki|poetycki|dynamiczny|noir)$",
    )
    dodatkowe_wskazowki: Optional[str] = Field(
        default=None,
        description="Opcjonalne dodatkowe wskazówki dla agentów",
        max_length=1000,
    )
    budget_limit: float = Field(
        default=10.0,
        description="Limit budżetu w USD",
        ge=1.0,
        le=100.0,
    )


class JobResponse(BaseModel):
    """Response z podstawowymi informacjami o zadaniu."""

    id: str
    gatunek: str
    inspiracja: str
    status: str  # queued, running, completed, failed
    cost_current: float
    budget_limit: float
    liczba_glownych_postaci: int
    docelowa_dlugosc: str
    styl_narracji: str
    created_at: str
    updated_at: str
    result: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class JobResultResponse(BaseModel):
    """Response z pełnym wynikiem zadania."""

    job: JobResponse
    swiat: Optional[dict[str, Any]] = None
    postacie: list[dict[str, Any]] = []
    fabula: Optional[dict[str, Any]] = None
    proza_chunks: list[dict[str, Any]] = []
    statystyki: dict[str, Any]


# === API Endpoints ===


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_async_session),
) -> JobResponse:
    """
    Tworzy nowe zadanie generowania książki.

    Zadanie jest dodawane do kolejki Celery i przetwarzane asynchronicznie.

    Args:
        request: Parametry zadania
        db: Sesja bazy danych

    Returns:
        JobResponse: Utworzone zadanie

    Raises:
        HTTPException: Gdy tworzenie się nie powiedzie
    """
    logger.info(
        "Tworzenie nowego zadania",
        gatunek=request.gatunek,
        dlugosc=request.docelowa_dlugosc,
    )

    try:
        # Utwórz Job w bazie
        job = Job(
            genre=request.gatunek,
            inspiration=request.inspiracja,
            status="queued",
            budget_limit=request.budget_limit,
            cost_current=0.0,
            metadata={
                "liczba_glownych_postaci": request.liczba_glownych_postaci,
                "docelowa_dlugosc": request.docelowa_dlugosc,
                "styl_narracji": request.styl_narracji,
                "dodatkowe_wskazowki": request.dodatkowe_wskazowki,
            },
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)

        logger.info("Zadanie utworzone w bazie", job_id=str(job.id))

        # Wyślij do Celery
        generate_book_task.apply_async(
            kwargs={
                "job_id": str(job.id),
                "gatunek": request.gatunek,
                "inspiracja": request.inspiracja,
                "liczba_glownych_postaci": request.liczba_glownych_postaci,
                "docelowa_dlugosc": request.docelowa_dlugosc,
                "styl_narracji": request.styl_narracji,
                "dodatkowe_wskazowki": request.dodatkowe_wskazowki,
            },
            task_id=str(job.id),  # Task ID = Job ID dla łatwego śledzenia
        )

        logger.info("Zadanie wysłane do Celery", job_id=str(job.id))

        return JobResponse(
            id=str(job.id),
            gatunek=job.genre,
            inspiracja=job.inspiration,
            status=job.status,
            cost_current=job.cost_current,
            budget_limit=job.budget_limit,
            liczba_glownych_postaci=request.liczba_glownych_postaci,
            docelowa_dlugosc=request.docelowa_dlugosc,
            styl_narracji=request.styl_narracji,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
            result=job.result,
        )

    except Exception as e:
        logger.error("Błąd podczas tworzenia zadania", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się utworzyć zadania: {str(e)}",
        )


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
) -> list[JobResponse]:
    """
    Pobiera listę wszystkich zadań.

    Args:
        limit: Maksymalna liczba wyników (domyślnie 50)
        offset: Offset dla paginacji (domyślnie 0)
        status_filter: Opcjonalny filtr po statusie (queued, running, completed, failed)
        db: Sesja bazy danych

    Returns:
        list[JobResponse]: Lista zadań

    Raises:
        HTTPException: Gdy pobieranie się nie powiedzie
    """
    logger.info("Pobieranie listy zadań", limit=limit, offset=offset)

    try:
        query = select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)

        if status_filter:
            query = query.where(Job.status == status_filter)

        result = await db.execute(query)
        jobs = result.scalars().all()

        return [
            JobResponse(
                id=str(job.id),
                gatunek=job.genre,
                inspiracja=job.inspiration,
                status=job.status,
                cost_current=job.cost_current,
                budget_limit=job.budget_limit,
                liczba_glownych_postaci=job.metadata.get("liczba_glownych_postaci", 3),
                docelowa_dlugosc=job.metadata.get("docelowa_dlugosc", "srednia"),
                styl_narracji=job.metadata.get("styl_narracji", "literacki"),
                created_at=job.created_at.isoformat(),
                updated_at=job.updated_at.isoformat(),
                result=job.result,
            )
            for job in jobs
        ]

    except Exception as e:
        logger.error("Błąd podczas pobierania listy zadań", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się pobrać listy zadań: {str(e)}",
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> JobResponse:
    """
    Pobiera szczegóły zadania.

    Args:
        job_id: UUID zadania
        db: Sesja bazy danych

    Returns:
        JobResponse: Szczegóły zadania

    Raises:
        HTTPException: Gdy zadanie nie istnieje
    """
    logger.info("Pobieranie zadania", job_id=job_id)

    try:
        job = await db.get(Job, uuid.UUID(job_id))

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zadanie {job_id} nie istnieje",
            )

        return JobResponse(
            id=str(job.id),
            gatunek=job.genre,
            inspiracja=job.inspiration,
            status=job.status,
            cost_current=job.cost_current,
            budget_limit=job.budget_limit,
            liczba_glownych_postaci=job.metadata.get("liczba_glownych_postaci", 3),
            docelowa_dlugosc=job.metadata.get("docelowa_dlugosc", "srednia"),
            styl_narracji=job.metadata.get("styl_narracji", "literacki"),
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
            result=job.result,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy format UUID",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Błąd podczas pobierania zadania", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się pobrać zadania: {str(e)}",
        )


@router.get("/jobs/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(
    job_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> JobResultResponse:
    """
    Pobiera pełny wynik zadania ze wszystkimi danymi.

    Zawiera:
    - Świat (geografia, historia, systemy)
    - Postacie (biografia, psychologia, relacje)
    - Fabuła (struktura, sceny)
    - Proza (wszystkie wygenerowane chunki)

    Args:
        job_id: UUID zadania
        db: Sesja bazy danych

    Returns:
        JobResultResponse: Pełny wynik zadania

    Raises:
        HTTPException: Gdy zadanie nie istnieje lub nie jest ukończone
    """
    logger.info("Pobieranie wyniku zadania", job_id=job_id)

    try:
        job = await db.get(Job, uuid.UUID(job_id))

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zadanie {job_id} nie istnieje",
            )

        if job.status not in ["completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Zadanie nie jest ukończone (status: {job.status})",
            )

        # Pobierz świat
        world_result = await db.execute(
            select(World).where(World.job_id == job.id)
        )
        world = world_result.scalar_one_or_none()

        # Pobierz postacie
        characters_result = await db.execute(
            select(Character).where(Character.job_id == job.id).order_by(Character.role)
        )
        characters = characters_result.scalars().all()

        # Pobierz fabułę
        plot_result = await db.execute(
            select(Plot).where(Plot.job_id == job.id)
        )
        plot = plot_result.scalar_one_or_none()

        # Pobierz prozę
        prose_result = await db.execute(
            select(ProseChunk)
            .where(ProseChunk.job_id == job.id)
            .order_by(ProseChunk.scene_number)
        )
        prose_chunks = prose_result.scalars().all()

        # Oblicz statystyki
        total_words = sum(chunk.word_count for chunk in prose_chunks)
        total_scenes = len(prose_chunks)

        return JobResultResponse(
            job=JobResponse(
                id=str(job.id),
                gatunek=job.genre,
                inspiracja=job.inspiration,
                status=job.status,
                cost_current=job.cost_current,
                budget_limit=job.budget_limit,
                liczba_glownych_postaci=job.metadata.get("liczba_glownych_postaci", 3),
                docelowa_dlugosc=job.metadata.get("docelowa_dlugosc", "srednia"),
                styl_narracji=job.metadata.get("styl_narracji", "literacki"),
                created_at=job.created_at.isoformat(),
                updated_at=job.updated_at.isoformat(),
                result=job.result,
            ),
            swiat={
                "id": str(world.id),
                "nazwa": world.world_name,
                "opis": world.world_description,
                "geografia": world.geography,
                "historia": world.history,
                "systemy": world.systems,
                "kultury": world.cultures,
                "tematyka": world.themes,
            }
            if world
            else None,
            postacie=[
                {
                    "id": str(char.id),
                    "imie": char.name,
                    "rola": char.role,
                    "biografia": char.biography,
                    "psychologia": char.psychology,
                    "wyglad": char.appearance,
                    "glos": char.voice,
                    "arc_rozwojowy": char.character_arc,
                    "relacje": char.relationships,
                }
                for char in characters
            ],
            fabula={
                "id": str(plot.id),
                "struktura": plot.structure,
                "akty": plot.acts,
                "sceny": plot.scenes,
                "konflikt": plot.conflict,
                "zwroty_akcji": plot.turning_points,
                "foreshadowing": plot.foreshadowing,
            }
            if plot
            else None,
            proza_chunks=[
                {
                    "id": str(chunk.id),
                    "scena_numer": chunk.scene_number,
                    "rozdzial_numer": chunk.chapter_number,
                    "tresc": chunk.content,
                    "liczba_slow": chunk.word_count,
                    "notatki_stylistyczne": chunk.style_notes,
                }
                for chunk in prose_chunks
            ],
            statystyki={
                "koszt_total_usd": job.cost_current,
                "liczba_scen": total_scenes,
                "liczba_slow_razem": total_words,
                "liczba_postaci": len(characters),
                "status": job.status,
            },
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy format UUID",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Błąd podczas pobierania wyniku zadania", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się pobrać wyniku zadania: {str(e)}",
        )


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Usuwa zadanie i wszystkie powiązane dane.

    UWAGA: Operacja nieodwracalna! Usuwa:
    - Job
    - World
    - Characters
    - Plot
    - ProseChunks
    - CostSnapshots

    Args:
        job_id: UUID zadania
        db: Sesja bazy danych

    Raises:
        HTTPException: Gdy zadanie nie istnieje
    """
    logger.info("Usuwanie zadania", job_id=job_id)

    try:
        job = await db.get(Job, uuid.UUID(job_id))

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zadanie {job_id} nie istnieje",
            )

        # Usuń job (cascade usunie powiązane dane dzięki relationships w schema)
        await db.delete(job)
        await db.commit()

        logger.info("Zadanie usunięte", job_id=job_id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy format UUID",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Błąd podczas usuwania zadania", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nie udało się usunąć zadania: {str(e)}",
        )
