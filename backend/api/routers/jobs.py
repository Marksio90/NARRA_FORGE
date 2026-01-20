"""
API Router dla zadań generowania książek - NarraForge.

Endpointy:
- POST /jobs/estimate - Szacowanie kosztów generowania
- POST /jobs - Tworzenie nowego zadania (autonomiczne AI)
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


class EstimateRequest(BaseModel):
    """Request do szacowania kosztów generowania."""

    gatunek: str = Field(
        ...,
        description="Gatunek literacki (fantasy, sci-fi, thriller, romans, horror, western, noir)",
        min_length=2,
        max_length=50,
    )
    docelowa_dlugosc: str = Field(
        default="srednia",
        description="Długość książki: 'krótka', 'srednia', 'długa'",
        pattern="^(krótka|srednia|długa)$",
    )


class EstimateResponse(BaseModel):
    """Response ze szacowaniem kosztów."""

    gatunek: str
    docelowa_dlugosc: str
    szacowany_koszt_min: float
    szacowany_koszt_max: float
    szacowany_czas_min: int  # minuty
    szacowany_czas_max: int
    liczba_scen: int
    szacowana_liczba_slow: int
    auto_styl_narracji: str
    auto_liczba_postaci: int


class CreateJobRequest(BaseModel):
    """Request do tworzenia nowego zadania - AUTONOMICZNE AI."""

    gatunek: str = Field(
        ...,
        description="Gatunek literacki (fantasy, sci-fi, thriller, romans, horror, western, noir)",
        min_length=2,
        max_length=50,
    )
    docelowa_dlugosc: str = Field(
        default="srednia",
        description="Długość książki: 'krótka' (8-12 scen), 'srednia' (15-20 scen), 'długa' (25-30 scen)",
        pattern="^(krótka|srednia|długa)$",
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


# === Helper Functions ===


def auto_map_genre_to_style(gatunek: str) -> str:
    """
    Automatycznie mapuje gatunek na optymalny styl narracji.

    Args:
        gatunek: Gatunek literacki

    Returns:
        str: Styl narracji
    """
    gatunek_lower = gatunek.lower()

    style_mapping = {
        "fantasy": "poetycki",
        "sci-fi": "dynamiczny",
        "science fiction": "dynamiczny",
        "thriller": "dynamiczny",
        "horror": "noir",
        "noir": "noir",
        "romans": "literacki",
        "romance": "literacki",
        "western": "dynamiczny",
        "mystery": "noir",
    }

    # Znajdź najlepsze dopasowanie
    for key, value in style_mapping.items():
        if key in gatunek_lower:
            return value

    # Domyślnie literacki
    return "literacki"


def auto_determine_character_count(gatunek: str, dlugosc: str) -> int:
    """
    Automatycznie określa optymalną liczbę głównych postaci.

    Args:
        gatunek: Gatunek literacki
        dlugosc: Długość książki

    Returns:
        int: Liczba głównych postaci (2-5)
    """
    # Bazowa liczba według długości
    base_counts = {
        "krótka": 2,
        "srednia": 3,
        "długa": 4,
    }

    count = base_counts.get(dlugosc, 3)

    # Dostosuj według gatunku
    gatunek_lower = gatunek.lower()
    if "fantasy" in gatunek_lower or "sci-fi" in gatunek_lower:
        count += 1  # Fantasy/Sci-fi często ma więcej postaci
    elif "thriller" in gatunek_lower or "noir" in gatunek_lower:
        count = max(2, count - 1)  # Thriller/Noir skupia się na mniejszej liczbie

    return min(5, max(2, count))


def calculate_estimate(gatunek: str, dlugosc: str) -> EstimateResponse:
    """
    Oblicza szacowane koszty i parametry generowania.

    Args:
        gatunek: Gatunek literacki
        dlugosc: Długość książki

    Returns:
        EstimateResponse: Szacowanie kosztów i parametrów
    """
    # Mapowanie długości → liczba scen
    scene_counts = {
        "krótka": 10,
        "srednia": 16,
        "długa": 25,
    }

    liczba_scen = scene_counts.get(dlugosc, 16)

    # Szacowana liczba słów (średnio 1000-1500 słów/scena)
    szacowana_liczba_slow = liczba_scen * 1200

    # Szacowane koszty (na podstawie empirycznych danych)
    # Założenia: ~$0.30-0.50 per scena (world + characters + plot + prose)
    cost_per_scene_min = 0.30
    cost_per_scene_max = 0.50

    szacowany_koszt_min = liczba_scen * cost_per_scene_min
    szacowany_koszt_max = liczba_scen * cost_per_scene_max

    # Szacowany czas (2-3 minuty per scena)
    szacowany_czas_min = liczba_scen * 2
    szacowany_czas_max = liczba_scen * 3

    return EstimateResponse(
        gatunek=gatunek,
        docelowa_dlugosc=dlugosc,
        szacowany_koszt_min=round(szacowany_koszt_min, 2),
        szacowany_koszt_max=round(szacowany_koszt_max, 2),
        szacowany_czas_min=szacowany_czas_min,
        szacowany_czas_max=szacowany_czas_max,
        liczba_scen=liczba_scen,
        szacowana_liczba_slow=szacowana_liczba_slow,
        auto_styl_narracji=auto_map_genre_to_style(gatunek),
        auto_liczba_postaci=auto_determine_character_count(gatunek, dlugosc),
    )


# === API Endpoints ===


@router.post("/jobs/estimate", response_model=EstimateResponse)
async def estimate_job_cost(request: EstimateRequest) -> EstimateResponse:
    """
    Szacuje koszty i parametry generowania książki.

    Endpoint ten pozwala użytkownikowi zobaczyć przewidywane koszty,
    czas generowania i parametry PRZED rozpoczęciem faktycznego generowania.

    Args:
        request: Parametry do szacowania (gatunek + długość)

    Returns:
        EstimateResponse: Szczegółowe szacowanie

    Example:
        POST /api/jobs/estimate
        {
          "gatunek": "fantasy",
          "docelowa_dlugosc": "srednia"
        }

        Response:
        {
          "szacowany_koszt_min": 4.80,
          "szacowany_koszt_max": 8.00,
          "szacowany_czas_min": 32,
          "szacowany_czas_max": 48,
          "liczba_scen": 16,
          "szacowana_liczba_slow": 19200,
          "auto_styl_narracji": "poetycki",
          "auto_liczba_postaci": 4
        }
    """
    logger.info(
        "Szacowanie kosztów",
        gatunek=request.gatunek,
        dlugosc=request.docelowa_dlugosc,
    )

    return calculate_estimate(request.gatunek, request.docelowa_dlugosc)


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_async_session),
) -> JobResponse:
    """
    Tworzy nowe zadanie generowania książki - AUTONOMICZNE AI.

    System automatycznie:
    - Generuje unikalny świat i fabułę
    - Decyduje o liczbie postaci (2-5)
    - Wybiera optymalny styl narracji dla gatunku
    - Szacuje budżet z 20% marginesem bezpieczeństwa

    Użytkownik podaje TYLKO gatunek i długość - reszta jest autonomiczna!

    Args:
        request: Tylko gatunek + długość
        db: Sesja bazy danych

    Returns:
        JobResponse: Utworzone zadanie

    Raises:
        HTTPException: Gdy tworzenie się nie powiedzie

    Example:
        POST /api/jobs
        {
          "gatunek": "fantasy",
          "docelowa_dlugosc": "srednia"
        }
    """
    logger.info(
        "Tworzenie nowego zadania - AUTONOMICZNE AI",
        gatunek=request.gatunek,
        dlugosc=request.docelowa_dlugosc,
    )

    try:
        # Auto-oblicz parametry
        estimate = calculate_estimate(request.gatunek, request.docelowa_dlugosc)

        # Auto-mapuj styl i liczbę postaci
        auto_styl = auto_map_genre_to_style(request.gatunek)
        auto_liczba_postaci = auto_determine_character_count(request.gatunek, request.docelowa_dlugosc)

        # Budżet = maksymalny szacowany koszt + 20% marginesu
        auto_budget = round(estimate.szacowany_koszt_max * 1.2, 2)

        # AI sam generuje inspirację - użytkownik nie podaje nic!
        auto_inspiracja = f"Autonomicznie wygeneruj unikalną i kreatywną książkę w gatunku {request.gatunek}. Stwórz oryginalny świat, fascynujące postacie i wciągającą fabułę bez bazowania na znanych dziełach."

        # Utwórz Job w bazie
        job = Job(
            genre=request.gatunek,
            inspiration=auto_inspiracja,  # Auto-generowana
            status="queued",
            budget_limit=auto_budget,  # Auto-obliczony
            cost_current=0.0,
            job_metadata={
                "liczba_glownych_postaci": auto_liczba_postaci,  # Auto 2-5
                "docelowa_dlugosc": request.docelowa_dlugosc,
                "styl_narracji": auto_styl,  # Auto-mapowany
                "auto_generated": True,  # Flag: zadanie w pełni autonomiczne
                "estimated_scenes": estimate.liczba_scen,
                "estimated_words": estimate.szacowana_liczba_slow,
            },
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)

        logger.info(
            "Zadanie utworzone w bazie - AUTONOMICZNE AI",
            job_id=str(job.id),
            auto_styl=auto_styl,
            auto_liczba_postaci=auto_liczba_postaci,
            auto_budget=auto_budget,
        )

        # Wyślij do Celery z auto-wygenerowanymi parametrami
        generate_book_task.apply_async(
            kwargs={
                "job_id": str(job.id),
                "gatunek": request.gatunek,
                "inspiracja": auto_inspiracja,  # Auto-generowana
                "liczba_glownych_postaci": auto_liczba_postaci,  # Auto 2-5
                "docelowa_dlugosc": request.docelowa_dlugosc,
                "styl_narracji": auto_styl,  # Auto-mapowany
                "dodatkowe_wskazowki": None,  # Brak - AI sam decyduje
            },
            task_id=str(job.id),  # Task ID = Job ID dla łatwego śledzenia
        )

        logger.info("Zadanie wysłane do Celery", job_id=str(job.id))

        return JobResponse(
            id=str(job.id),
            gatunek=job.genre,
            inspiracja=auto_inspiracja,  # Zwracamy auto-generowaną
            status=job.status,
            cost_current=job.cost_current,
            budget_limit=auto_budget,  # Auto-obliczony
            liczba_glownych_postaci=auto_liczba_postaci,
            docelowa_dlugosc=request.docelowa_dlugosc,
            styl_narracji=auto_styl,
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
                liczba_glownych_postaci=job.job_metadata.get("liczba_glownych_postaci", 3),
                docelowa_dlugosc=job.job_metadata.get("docelowa_dlugosc", "srednia"),
                styl_narracji=job.job_metadata.get("styl_narracji", "literacki"),
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
            liczba_glownych_postaci=job.job_metadata.get("liczba_glownych_postaci", 3),
            docelowa_dlugosc=job.job_metadata.get("docelowa_dlugosc", "srednia"),
            styl_narracji=job.job_metadata.get("styl_narracji", "literacki"),
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
                liczba_glownych_postaci=job.job_metadata.get("liczba_glownych_postaci", 3),
                docelowa_dlugosc=job.job_metadata.get("docelowa_dlugosc", "srednia"),
                styl_narracji=job.job_metadata.get("styl_narracji", "literacki"),
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
