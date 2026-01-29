"""
Live Preview Service for NarraForge 2.0

WebSocket-based real-time preview of book generation.
User sees every word as it's being generated.
"""

from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of live preview events"""
    # Analysis phase
    TITAN_ANALYSIS_START = "TITAN_ANALYSIS_START"
    TITAN_DIMENSION = "TITAN_DIMENSION"
    TITAN_COMPLETE = "TITAN_COMPLETE"

    # Parameters phase
    PARAMETERS_GENERATED = "PARAMETERS_GENERATED"

    # World building phase
    WORLD_BUILDING_START = "WORLD_BUILDING_START"
    WORLD_CHUNK = "WORLD_CHUNK"
    WORLD_COMPLETE = "WORLD_COMPLETE"

    # Character creation phase
    CHARACTER_CREATION_START = "CHARACTER_CREATION_START"
    CHARACTER_BORN = "CHARACTER_BORN"
    CHARACTERS_COMPLETE = "CHARACTERS_COMPLETE"

    # Plot phase
    PLOT_START = "PLOT_START"
    PLOT_COMPLETE = "PLOT_COMPLETE"

    # Writing phase
    CHAPTER_START = "CHAPTER_START"
    SCENE_START = "SCENE_START"
    PROSE_STREAM = "PROSE_STREAM"
    SCENE_COMPLETE = "SCENE_COMPLETE"
    CHAPTER_COMPLETE = "CHAPTER_COMPLETE"

    # Completion
    BOOK_COMPLETE = "BOOK_COMPLETE"

    # Errors
    ERROR = "ERROR"
    WARNING = "WARNING"

    # Progress
    PROGRESS_UPDATE = "PROGRESS_UPDATE"


@dataclass
class LiveEvent:
    """A single live preview event"""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        })


class WebSocketManager:
    """Manages WebSocket connections for live preview"""

    def __init__(self):
        # project_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, project_id: str):
        """Connect a new WebSocket for a project."""
        await websocket.accept()

        async with self._lock:
            if project_id not in self.active_connections:
                self.active_connections[project_id] = []
            self.active_connections[project_id].append(websocket)

        logger.info(f"WebSocket connected for project {project_id}. Total: {len(self.active_connections[project_id])}")

    async def disconnect(self, websocket: WebSocket, project_id: str):
        """Disconnect a WebSocket."""
        async with self._lock:
            if project_id in self.active_connections:
                if websocket in self.active_connections[project_id]:
                    self.active_connections[project_id].remove(websocket)

                if not self.active_connections[project_id]:
                    del self.active_connections[project_id]

        logger.info(f"WebSocket disconnected for project {project_id}")

    async def broadcast(self, project_id: str, event: LiveEvent):
        """Broadcast event to all connected clients for a project."""
        if project_id not in self.active_connections:
            return

        message = event.to_json()
        disconnected = []

        for websocket in self.active_connections[project_id]:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                disconnected.append(websocket)

        # Clean up disconnected
        for ws in disconnected:
            await self.disconnect(ws, project_id)

    def get_connection_count(self, project_id: str) -> int:
        """Get number of active connections for a project."""
        return len(self.active_connections.get(project_id, []))


class LivePreviewService:
    """
    Service for live preview of book generation.
    Streams events to connected WebSocket clients.
    """

    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.active_streams: Dict[str, bool] = {}  # project_id -> is_active

    async def handle_websocket(self, websocket: WebSocket, project_id: str):
        """Handle a WebSocket connection for live preview."""
        await self.websocket_manager.connect(websocket, project_id)

        try:
            # Keep connection alive and handle incoming messages
            while True:
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=30.0  # Ping/pong interval
                    )

                    # Handle client messages (e.g., pause/resume)
                    message = json.loads(data)
                    await self._handle_client_message(project_id, message)

                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    try:
                        await websocket.send_text(json.dumps({"type": "PING"}))
                    except:
                        break

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket error for project {project_id}: {e}")
        finally:
            await self.websocket_manager.disconnect(websocket, project_id)

    async def _handle_client_message(self, project_id: str, message: Dict):
        """Handle messages from client."""
        msg_type = message.get("type", "")

        if msg_type == "PONG":
            pass  # Client responding to ping
        elif msg_type == "PAUSE":
            # Could implement pause functionality
            pass
        elif msg_type == "RESUME":
            pass

    # Event emission methods

    async def emit_titan_start(self, project_id: str, title: str):
        """Emit TITAN analysis start event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.TITAN_ANALYSIS_START,
                data={"title": title, "message": "Analizuję głębię tytułu..."}
            )
        )

    async def emit_titan_dimension(
        self,
        project_id: str,
        dimension_name: str,
        result: Dict,
        impact_preview: Dict
    ):
        """Emit TITAN dimension analysis event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.TITAN_DIMENSION,
                data={
                    "dimension": dimension_name,
                    "result": result,
                    "impact": impact_preview
                }
            )
        )

    async def emit_parameters_generated(
        self,
        project_id: str,
        parameters: Dict
    ):
        """Emit parameters generated event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.PARAMETERS_GENERATED,
                data={
                    "word_count": parameters.get("target_word_count"),
                    "chapters": parameters.get("chapter_count"),
                    "characters": parameters.get("character_count", {}).get("main"),
                    "locations": parameters.get("locations_count"),
                    "message": f"Ta książka będzie miała {parameters.get('target_word_count', 0):,} słów!"
                }
            )
        )

    async def emit_world_building_start(self, project_id: str):
        """Emit world building start event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.WORLD_BUILDING_START,
                data={"message": "Tworzę świat..."}
            )
        )

    async def emit_character_born(
        self,
        project_id: str,
        character: Dict
    ):
        """Emit character creation event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.CHARACTER_BORN,
                data={
                    "name": character.get("name"),
                    "role": character.get("role"),
                    "portrait_prompt": character.get("physical_description", "")[:100],
                    "psychology_preview": {
                        "wound": character.get("psychology", {}).get("wound", "")[:100],
                        "want": character.get("psychology", {}).get("want", ""),
                        "fear": character.get("psychology", {}).get("fear", "")
                    }
                }
            )
        )

    async def emit_chapter_start(
        self,
        project_id: str,
        chapter_num: int,
        chapter_title: str,
        hook: str = ""
    ):
        """Emit chapter start event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.CHAPTER_START,
                data={
                    "chapter": chapter_num,
                    "title": chapter_title,
                    "preview": hook
                }
            )
        )

    async def emit_scene_start(
        self,
        project_id: str,
        chapter_num: int,
        scene_num: int
    ):
        """Emit scene start event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.SCENE_START,
                data={"chapter": chapter_num, "scene": scene_num}
            )
        )

    async def emit_prose_stream(
        self,
        project_id: str,
        chapter_num: int,
        scene_num: int,
        text_chunk: str,
        word_count_so_far: int
    ):
        """Emit prose streaming event (word by word / chunk by chunk)."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.PROSE_STREAM,
                data={
                    "chapter": chapter_num,
                    "scene": scene_num,
                    "text": text_chunk,
                    "word_count_so_far": word_count_so_far
                }
            )
        )

    async def emit_scene_complete(
        self,
        project_id: str,
        chapter_num: int,
        scene_num: int,
        word_count: int,
        quality_score: float
    ):
        """Emit scene complete event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.SCENE_COMPLETE,
                data={
                    "chapter": chapter_num,
                    "scene": scene_num,
                    "word_count": word_count,
                    "quality_score": quality_score
                }
            )
        )

    async def emit_chapter_complete(
        self,
        project_id: str,
        chapter_num: int,
        word_count: int,
        cliffhanger_rating: int = 0
    ):
        """Emit chapter complete event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.CHAPTER_COMPLETE,
                data={
                    "chapter": chapter_num,
                    "word_count": word_count,
                    "cliffhanger_rating": cliffhanger_rating
                }
            )
        )

    async def emit_book_complete(
        self,
        project_id: str,
        total_words: int,
        total_chapters: int,
        generation_time_seconds: int,
        quality_score: float,
        continuation_suggestions: List[Dict] = None
    ):
        """Emit book complete event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.BOOK_COMPLETE,
                data={
                    "total_words": total_words,
                    "total_chapters": total_chapters,
                    "generation_time": generation_time_seconds,
                    "quality_score": quality_score,
                    "continuation_suggestions": continuation_suggestions or []
                }
            )
        )

    async def emit_progress_update(
        self,
        project_id: str,
        step: int,
        total_steps: int,
        percentage: float,
        activity: str
    ):
        """Emit progress update event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.PROGRESS_UPDATE,
                data={
                    "step": step,
                    "total_steps": total_steps,
                    "percentage": percentage,
                    "activity": activity
                }
            )
        )

    async def emit_error(
        self,
        project_id: str,
        error_message: str,
        recoverable: bool = True
    ):
        """Emit error event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.ERROR,
                data={
                    "message": error_message,
                    "recoverable": recoverable
                }
            )
        )

    async def emit_warning(
        self,
        project_id: str,
        warning_message: str
    ):
        """Emit warning event."""
        await self.websocket_manager.broadcast(
            project_id,
            LiveEvent(
                type=EventType.WARNING,
                data={"message": warning_message}
            )
        )


# Singleton instance
_live_preview_service: Optional[LivePreviewService] = None


def get_live_preview_service() -> LivePreviewService:
    """Get or create live preview service instance."""
    global _live_preview_service
    if _live_preview_service is None:
        _live_preview_service = LivePreviewService()
    return _live_preview_service
