"""
Tracker kosztów dla NarraForge.

Moduł zapisuje snapshoty kosztów do bazy danych
dla każdego wywołania OpenAI API.
"""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from models.schema import CostSnapshot, Job

logger = get_logger(__name__)


class CostTracker:
    """
    Tracker kosztów wywołań OpenAI API.

    Zapisuje szczegółowe informacje o kosztach do bazy danych,
    umożliwiając analizę wydatków per projekt i etap.

    Przykład użycia:
        >>> tracker = CostTracker(db_session)
        >>> await tracker.zapisz_koszt(
        ...     job_id=uuid.uuid4(),
        ...     etap="budowanie_swiata",
        ...     model="gpt-4o",
        ...     tokeny_input=1000,
        ...     tokeny_output=1500,
        ...     koszt_usd=0.025
        ... )
    """

    def __init__(self, db: AsyncSession):
        """
        Inicjalizacja trackera kosztów.

        Args:
            db: Sesja bazy danych SQLAlchemy
        """
        self.db = db
        logger.debug("Zainicjalizowano tracker kosztów")

    async def zapisz_koszt(
        self,
        job_id: uuid.UUID,
        etap: str,
        model: str,
        tokeny_input: int,
        tokeny_output: int,
        koszt_usd: float,
    ) -> CostSnapshot:
        """
        Zapisuje snapshot kosztu do bazy danych.

        Args:
            job_id: ID zadania
            etap: Nazwa etapu (np. "budowanie_swiata")
            model: Nazwa modelu OpenAI
            tokeny_input: Liczba tokenów wejściowych
            tokeny_output: Liczba tokenów wyjściowych
            koszt_usd: Koszt w USD

        Returns:
            CostSnapshot: Zapisany snapshot

        Raises:
            DatabaseError: Gdy zapis się nie powiedzie
        """
        snapshot = CostSnapshot(
            job_id=job_id,
            stage=etap,
            model_used=model,
            tokens_input=tokeny_input,
            tokens_output=tokeny_output,
            tokens_total=tokeny_input + tokeny_output,
            cost_usd=koszt_usd,
        )

        self.db.add(snapshot)
        await self.db.flush()  # Flush ale jeszcze nie commit

        logger.info(
            "Zapisano snapshot kosztu",
            job_id=str(job_id),
            etap=etap,
            model=model,
            tokeny_razem=snapshot.tokens_total,
            koszt_usd=koszt_usd,
        )

        return snapshot

    async def aktualizuj_koszt_joba(
        self,
        job_id: uuid.UUID,
        dodatkowy_koszt: float,
        dodatkowe_tokeny: int,
    ) -> None:
        """
        Aktualizuje łączny koszt i tokeny w rekordzie joba.

        Args:
            job_id: ID zadania
            dodatkowy_koszt: Koszt do dodania (USD)
            dodatkowe_tokeny: Tokeny do dodania
        """
        # Pobierz job
        job = await self.db.get(Job, job_id)
        if not job:
            logger.error("Nie znaleziono joba", job_id=str(job_id))
            return

        # Aktualizuj koszty
        job.cost_current += dodatkowy_koszt
        job.tokens_used += dodatkowe_tokeny

        await self.db.flush()

        logger.info(
            "Zaktualizowano koszt joba",
            job_id=str(job_id),
            koszt_aktualny=job.cost_current,
            tokeny_uzyte=job.tokens_used,
        )

    async def pobierz_koszty_joba(
        self,
        job_id: uuid.UUID,
    ) -> dict[str, any]:
        """
        Pobiera podsumowanie kosztów dla joba.

        Args:
            job_id: ID zadania

        Returns:
            dict: Podsumowanie kosztów
        """
        from sqlalchemy import func, select

        # Pobierz job
        job = await self.db.get(Job, job_id)
        if not job:
            return {"blad": "Job nie znaleziony"}

        # Pobierz snapshoty
        stmt = (
            select(
                CostSnapshot.stage,
                func.sum(CostSnapshot.tokens_input).label("tokeny_input"),
                func.sum(CostSnapshot.tokens_output).label("tokeny_output"),
                func.sum(CostSnapshot.cost_usd).label("koszt_usd"),
                func.count().label("liczba_wywolan"),
            )
            .where(CostSnapshot.job_id == job_id)
            .group_by(CostSnapshot.stage)
        )

        result = await self.db.execute(stmt)
        koszty_per_etap = []

        for row in result:
            koszty_per_etap.append(
                {
                    "etap": row.stage,
                    "tokeny_input": row.tokeny_input,
                    "tokeny_output": row.tokeny_output,
                    "tokeny_razem": row.tokeny_input + row.tokeny_output,
                    "koszt_usd": float(row.koszt_usd),
                    "liczba_wywolan": row.liczba_wywolan,
                }
            )

        logger.debug("Pobrano koszty joba", job_id=str(job_id), liczba_etapow=len(koszty_per_etap))

        return {
            "job_id": str(job_id),
            "koszt_razem_usd": float(job.cost_current),
            "tokeny_razem": job.tokens_used,
            "budzet_limit_usd": float(job.budget_limit),
            "pozostaly_budzet_usd": float(job.budget_limit - job.cost_current),
            "procent_budzetu_uzyty": round((job.cost_current / job.budget_limit) * 100, 2),
            "koszty_per_etap": koszty_per_etap,
        }

    async def sprawdz_budzet(
        self,
        job_id: uuid.UUID,
    ) -> dict[str, any]:
        """
        Sprawdza czy job nie przekroczył budżetu.

        Args:
            job_id: ID zadania

        Returns:
            dict: Status budżetu
        """
        job = await self.db.get(Job, job_id)
        if not job:
            return {"blad": "Job nie znaleziony"}

        przekroczony = job.cost_current >= job.budget_limit
        pozostaly = job.budget_limit - job.cost_current

        if przekroczony:
            logger.warning(
                "Przekroczono budżet!",
                job_id=str(job_id),
                koszt_aktualny=job.cost_current,
                limit=job.budget_limit,
            )
        else:
            logger.debug(
                "Budżet OK",
                job_id=str(job_id),
                pozostaly_budzet=pozostaly,
            )

        return {
            "przekroczony": przekroczony,
            "koszt_aktualny_usd": float(job.cost_current),
            "limit_usd": float(job.budget_limit),
            "pozostaly_usd": float(max(0, pozostaly)),
            "procent_uzyty": round((job.cost_current / job.budget_limit) * 100, 2),
        }


def utworz_tracker(db: AsyncSession) -> CostTracker:
    """
    Tworzy instancję trackera kosztów.

    Args:
        db: Sesja bazy danych

    Returns:
        CostTracker: Instancja trackera
    """
    return CostTracker(db)
