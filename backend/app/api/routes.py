"""
API routes for NarraForge.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Request/Response Models
# ============================================

class GenerateBookRequest(BaseModel):
    genre: str


class BookResponse(BaseModel):
    id: str
    genre: str
    status: str
    title: str | None = None
    word_count: int = 0
    chapter_count: int = 0
    cost_total: float = 0.0
    created_at: str
    completed_at: str | None = None


class GenreInfo(BaseModel):
    id: str
    name: str
    description: str
    typical_length: str
    complexity: int


class ExportRequest(BaseModel):
    format: str = "docx"


# ============================================
# Genre Endpoints
# ============================================

@router.get("/genres", response_model=List[GenreInfo])
async def list_genres():
    """Lista dostępnych gatunków z opisami."""
    return [
        {
            "id": "scifi",
            "name": "Science Fiction",
            "description": "Wizjonerskie opowieści o przyszłości, technologii i ludzkości",
            "typical_length": "80-120k słów",
            "complexity": 5,
        },
        {
            "id": "fantasy",
            "name": "Fantasy",
            "description": "Epickie podróże w światach magii i legend",
            "typical_length": "100-150k słów",
            "complexity": 5,
        },
        {
            "id": "thriller",
            "name": "Thriller",
            "description": "Trzymające w napięciu historie pełne zwrotów akcji",
            "typical_length": "70-90k słów",
            "complexity": 4,
        },
        {
            "id": "horror",
            "name": "Horror",
            "description": "Mroczne opowieści, które nie dają spać po nocach",
            "typical_length": "60-80k słów",
            "complexity": 4,
        },
        {
            "id": "romance",
            "name": "Romans",
            "description": "Poruszające historie o miłości i relacjach",
            "typical_length": "70-100k słów",
            "complexity": 3,
        },
        {
            "id": "mystery",
            "name": "Kryminał",
            "description": "Zagadki, śledztwa i niespodziewane rozwiązania",
            "typical_length": "70-90k słów",
            "complexity": 4,
        },
        {
            "id": "drama",
            "name": "Dramat",
            "description": "Głębokie historie o ludzkich doświadczeniach",
            "typical_length": "60-90k słów",
            "complexity": 4,
        },
        {
            "id": "comedy",
            "name": "Komedia",
            "description": "Lekkie, zabawne historie z humorem i satyrą",
            "typical_length": "50-70k słów",
            "complexity": 3,
        },
        {
            "id": "dystopia",
            "name": "Dystopia",
            "description": "Mroczne wizje społeczeństwa przyszłości",
            "typical_length": "80-110k słów",
            "complexity": 5,
        },
        {
            "id": "historical",
            "name": "Powieść Historyczna",
            "description": "Podróże w czasie do fascynujących epok",
            "typical_length": "90-130k słów",
            "complexity": 5,
        },
    ]


# ============================================
# Book Endpoints
# ============================================

@router.post("/books/generate", response_model=BookResponse)
async def generate_book(
    request: GenerateBookRequest,
    background_tasks: BackgroundTasks,
):
    """
    Rozpoczyna generowanie nowej książki.

    Użytkownik wybiera TYLKO gatunek - reszta jest autonomiczna.
    """
    # Walidacja gatunku
    valid_genres = [
        'scifi', 'fantasy', 'thriller', 'horror',
        'romance', 'mystery', 'drama', 'comedy',
        'dystopia', 'historical'
    ]

    if request.genre.lower() not in valid_genres:
        raise HTTPException(
            status_code=400,
            detail=f"Nieznany gatunek. Dostępne: {valid_genres}"
        )

    # TODO: Implement book generation
    # For now, return a mock response
    import uuid
    from datetime import datetime

    book_id = str(uuid.uuid4())

    logger.info(f"Starting book generation: {book_id} - genre: {request.genre}")

    # Background task would be added here
    # background_tasks.add_task(generate_book_async, book_id)

    return BookResponse(
        id=book_id,
        genre=request.genre,
        status="generating",
        title=None,
        word_count=0,
        chapter_count=0,
        cost_total=0.0,
        created_at=datetime.utcnow().isoformat(),
        completed_at=None
    )


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    """Pobiera szczegóły książki."""
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Książka nie znaleziona")


@router.get("/books", response_model=List[BookResponse])
async def list_books(limit: int = 20, offset: int = 0):
    """Lista wszystkich książek."""
    # TODO: Implement
    return []


@router.get("/books/{book_id}/progress")
async def get_progress(book_id: str):
    """Pobiera aktualny postęp generowania."""
    # TODO: Implement
    return {
        "phase": "writing",
        "message": "Pisanie rozdziału 5...",
        "progress": 35.0
    }


@router.get("/books/{book_id}/cost")
async def get_cost(book_id: str):
    """Pobiera szczegóły kosztów generowania."""
    # TODO: Implement
    return {
        "total": 0.0,
        "breakdown": {}
    }


@router.post("/books/{book_id}/export")
async def export_book(book_id: str, request: ExportRequest):
    """
    Eksportuje książkę do wybranego formatu.

    Formaty: docx, pdf, epub, txt, md
    """
    valid_formats = ['docx', 'pdf', 'epub', 'txt', 'md']
    if request.format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Nieznany format. Dostępne: {valid_formats}"
        )

    # TODO: Implement export
    raise HTTPException(status_code=404, detail="Książka nie znaleziona")


@router.post("/books/{book_id}/continue", response_model=BookResponse)
async def continue_series(book_id: str, background_tasks: BackgroundTasks):
    """
    Kontynuuje serię - tworzy następny tom.

    Importuje świat, postacie i otwarte wątki z poprzedniego tomu.
    """
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Książka nie znaleziona")
