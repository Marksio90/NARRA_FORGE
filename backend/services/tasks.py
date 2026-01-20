"""
Celery tasks dla przetwarzania zadań w tle - NarraForge.

Definiuje asynchroniczne taski dla pipeline'u generowania książek.
"""

import asyncio
import uuid
from typing import Any, Optional

from celery import Celery, Task
from redis import Redis

from agents.orchestrator import Orchestrator
from core.config import get_settings
from core.db import get_async_session
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery(
    "narraforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.health_check", bind=True)
def health_check(self) -> dict:
    """
    Health check task dla Celery workera.

    Returns:
        dict: Status zdrowia workera
    """
    logger.info("Celery worker health check", task_id=self.request.id)
    return {"status": "healthy", "worker": "running"}


class GenerateBookTask(Task):
    """
    Custom Task class dla generowania książki.

    Zapewnia progress tracking przez Redis.
    """

    def __init__(self):
        super().__init__()
        self._redis: Optional[Redis] = None

    @property
    def redis(self) -> Redis:
        """Lazy initialization Redis connection."""
        if self._redis is None:
            self._redis = Redis.from_url(
                settings.CELERY_BROKER_URL,
                decode_responses=True,
            )
        return self._redis

    def _progress_callback(self, job_id: str, etap: str, procent: float) -> None:
        """
        Callback dla śledzenia postępu.

        Publikuje postęp do Redis dla WebSocket subscribers.

        Args:
            job_id: ID zadania
            etap: Nazwa aktualnego etapu
            procent: Procent ukończenia (0-100)
        """
        try:
            progress_data = {
                "job_id": job_id,
                "etap": etap,
                "procent": procent,
                "task_id": self.request.id,
            }

            # Publish do Redis channel dla WebSocket
            self.redis.publish(
                f"job_progress:{job_id}",
                str(progress_data),
            )

            # Zapisz ostatni stan do Redis (dla klientów łączących się później)
            self.redis.setex(
                f"job_progress_latest:{job_id}",
                3600,  # TTL 1 godzina
                str(progress_data),
            )

            logger.debug(
                "Progress update",
                job_id=job_id,
                etap=etap,
                procent=procent,
            )

        except Exception as e:
            logger.warning("Błąd podczas publikacji postępu", error=str(e))


@celery_app.task(
    name="tasks.generate_book",
    bind=True,
    base=GenerateBookTask,
    max_retries=0,  # Nie retry - zadanie długotrwałe
)
def generate_book_task(
    self,
    job_id: str,
    gatunek: str,
    inspiracja: str,
    liczba_glownych_postaci: int = 3,
    docelowa_dlugosc: str = "srednia",
    styl_narracji: str = "literacki",
    dodatkowe_wskazowki: Optional[str] = None,
) -> dict[str, Any]:
    """
    Asynchroniczny task generowania książki.

    Uruchamia Orchestrator który koordynuje wszystkie agenty AI:
    - World_Architect: budowanie świata
    - Character_Smith: tworzenie postaci
    - Plot_Master: projektowanie fabuły
    - Prose_Weaver: generowanie scen (w pętli)

    Args:
        job_id: UUID zadania (string)
        gatunek: Gatunek literacki (fantasy, sci-fi, thriller, etc.)
        inspiracja: Inspiracja dla świata
        liczba_glownych_postaci: Liczba głównych postaci (2-5)
        docelowa_dlugosc: Długość ("krótka"|"srednia"|"długa")
        styl_narracji: Styl ("literacki"|"poetycki"|"dynamiczny"|"noir")
        dodatkowe_wskazowki: Opcjonalne dodatkowe wskazówki

    Returns:
        dict: Wynik generowania z ID-ami utworzonych zasobów

    Raises:
        Exception: Gdy generowanie się nie powiedzie
    """
    logger.info(
        "Rozpoczynam generowanie książki",
        job_id=job_id,
        gatunek=gatunek,
        task_id=self.request.id,
    )

    async def _run_pipeline():
        """Inner async function dla uruchomienia pipeline."""
        async for db in get_async_session():
            try:
                # Utwórz progress callback z zamknięciem na job_id
                def progress_callback(etap: str, procent: float):
                    self._progress_callback(job_id, etap, procent)

                # Utwórz orchestrator
                orchestrator = Orchestrator(
                    db=db,
                    progress_callback=progress_callback,
                )

                # Uruchom pipeline
                wynik = await orchestrator.uruchom_pipeline(
                    job_id=uuid.UUID(job_id),
                    gatunek=gatunek,
                    inspiracja=inspiracja,
                    liczba_glownych_postaci=liczba_glownych_postaci,
                    docelowa_dlugosc=docelowa_dlugosc,
                    styl_narracji=styl_narracji,
                    dodatkowe_wskazowki=dodatkowe_wskazowki,
                )

                logger.info(
                    "Zakończono generowanie książki",
                    job_id=job_id,
                    sukces=wynik["sukces"],
                    liczba_slow=wynik.get("liczba_slow_razem"),
                )

                return wynik

            except Exception as e:
                logger.error(
                    "Błąd podczas generowania książki",
                    job_id=job_id,
                    error=str(e),
                )
                raise
            finally:
                await db.close()

    # Uruchom async pipeline w sync context (Celery)
    try:
        wynik = asyncio.run(_run_pipeline())
        return wynik

    except Exception as e:
        komunikat = f"Task generowania książki failed: {str(e)}"
        logger.error(komunikat, job_id=job_id, task_id=self.request.id)

        # Opublikuj błąd do progress channel
        self._progress_callback(
            job_id,
            f"BŁĄD: {str(e)[:100]}",
            0.0,
        )

        raise
