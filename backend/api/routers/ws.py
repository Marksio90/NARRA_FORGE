"""
WebSocket router dla real-time progress tracking - NarraForge.

Umożliwia klientom subskrypcję do postępu generowania książki w czasie rzeczywistym.
"""

import asyncio
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter()


class ProgressManager:
    """
    Zarządza połączeniami WebSocket dla śledzenia postępu.

    Używa Redis pub/sub do odbierania progress updates z Celery tasków.
    """

    def __init__(self):
        """Inicjalizacja managera."""
        self._redis: Optional[Redis] = None

    async def get_redis(self) -> Redis:
        """
        Pobiera połączenie Redis (lazy initialization).

        Returns:
            Redis: Połączenie Redis
        """
        if self._redis is None:
            self._redis = await Redis.from_url(
                settings.CELERY_BROKER_URL,
                decode_responses=True,
            )
        return self._redis

    async def close_redis(self) -> None:
        """Zamyka połączenie Redis."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    async def subscribe_to_progress(
        self,
        job_id: str,
        websocket: WebSocket,
    ) -> None:
        """
        Subskrybuje do progress updates dla zadania i wysyła do WebSocket.

        Args:
            job_id: UUID zadania
            websocket: Połączenie WebSocket z klientem

        Raises:
            WebSocketDisconnect: Gdy klient rozłączy się
        """
        redis = await self.get_redis()
        pubsub = redis.pubsub()

        try:
            # Subskrybuj do kanału postępu dla tego joba
            channel = f"job_progress:{job_id}"
            await pubsub.subscribe(channel)

            logger.info(
                "WebSocket subskrybowany",
                job_id=job_id,
                channel=channel,
            )

            # Wyślij ostatni znany stan (jeśli istnieje)
            latest_key = f"job_progress_latest:{job_id}"
            latest_progress = await redis.get(latest_key)

            if latest_progress:
                try:
                    # Parse string representation of dict
                    progress_dict = eval(latest_progress)  # Bezpieczne tu, bo z Redis
                    await websocket.send_json({
                        "typ": "progress",
                        "data": progress_dict,
                    })
                except Exception as e:
                    logger.warning(
                        "Nie można sparsować ostatniego postępu",
                        error=str(e),
                    )

            # Słuchaj nowych wiadomości
            while True:
                # Timeout co 1s żeby móc sprawdzić czy połączenie jeszcze żyje
                try:
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0,
                    )

                    if message and message["type"] == "message":
                        # Parse progress data
                        try:
                            progress_str = message["data"]
                            progress_dict = eval(progress_str)  # Z Redis - bezpieczne

                            await websocket.send_json({
                                "typ": "progress",
                                "data": progress_dict,
                            })

                            logger.debug(
                                "Progress update wysłany",
                                job_id=job_id,
                                etap=progress_dict.get("etap"),
                                procent=progress_dict.get("procent"),
                            )

                            # Jeśli ukończono (100%), zakończ subskrypcję
                            if progress_dict.get("procent", 0) >= 100:
                                await websocket.send_json({
                                    "typ": "zakonczono",
                                    "data": {"job_id": job_id},
                                })
                                logger.info("Job ukończony, zamykam WebSocket", job_id=job_id)
                                break

                        except Exception as e:
                            logger.error(
                                "Błąd parsowania progress message",
                                error=str(e),
                                message=message,
                            )

                except asyncio.TimeoutError:
                    # Timeout - sprawdź czy połączenie żyje pingiem
                    try:
                        await websocket.send_json({"typ": "ping"})
                    except Exception:
                        # Połączenie martwe
                        logger.warning("WebSocket connection died", job_id=job_id)
                        break

        except WebSocketDisconnect:
            logger.info("WebSocket rozłączony przez klienta", job_id=job_id)
            raise

        except Exception as e:
            logger.error("Błąd w WebSocket subscription", job_id=job_id, error=str(e))
            try:
                await websocket.send_json({
                    "typ": "blad",
                    "data": {"komunikat": str(e)},
                })
            except Exception:
                pass  # Nie można wysłać - połączenie przerwane

        finally:
            # Unsubscribe i zamknij pubsub
            await pubsub.unsubscribe(channel)
            await pubsub.close()

            logger.info("WebSocket subscription zakończona", job_id=job_id)


# Global instance
progress_manager = ProgressManager()


@router.websocket("/ws/jobs/{job_id}/progress")
async def websocket_job_progress(
    websocket: WebSocket,
    job_id: str,
):
    """
    WebSocket endpoint dla śledzenia postępu zadania w czasie rzeczywistym.

    Klient otrzymuje:
    - Aktualny stan (jeśli dostępny)
    - Real-time updates o postępie
    - Powiadomienie o ukończeniu

    Format wiadomości:
    ```json
    {
      "typ": "progress",
      "data": {
        "job_id": "uuid",
        "etap": "Budowanie świata",
        "procent": 25.5,
        "task_id": "uuid"
      }
    }
    ```

    Args:
        websocket: Połączenie WebSocket
        job_id: UUID zadania do śledzenia

    Example (JS client):
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/ws/jobs/123/progress')
        ws.onmessage = (event) => {
          const msg = JSON.parse(event.data)
          if (msg.typ === 'progress') {
            console.log(`${msg.data.etap}: ${msg.data.procent}%`)
          }
        }
        ```
    """
    await websocket.accept()

    logger.info(
        "Nowe połączenie WebSocket",
        job_id=job_id,
        client=websocket.client,
    )

    try:
        # Wyślij powitanie
        await websocket.send_json({
            "typ": "polaczono",
            "data": {
                "job_id": job_id,
                "komunikat": "Połączono z serwerem postępu",
            },
        })

        # Subskrybuj do progress updates
        await progress_manager.subscribe_to_progress(job_id, websocket)

    except WebSocketDisconnect:
        logger.info("Klient rozłączony", job_id=job_id)

    except Exception as e:
        logger.error("Błąd WebSocket", job_id=job_id, error=str(e))

    finally:
        # Zamknij połączenie
        try:
            await websocket.close()
        except Exception:
            pass


@router.on_event("shutdown")
async def shutdown_event():
    """Zamyka Redis connection przy shutdown."""
    await progress_manager.close_redis()
    logger.info("Progress manager shutdown complete")
