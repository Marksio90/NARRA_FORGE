"""
WebSocket connection manager for live updates.
"""
from fastapi import WebSocket
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for live updates.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        """Close WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_progress(self, session_id: str, progress: dict):
        """Send progress update."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "progress",
                    "data": progress
                })
            except Exception as e:
                logger.error(f"Error sending progress to {session_id}: {e}")
                self.disconnect(session_id)

    async def send_cost_update(self, session_id: str, cost: dict):
        """Send cost update."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "cost",
                    "data": cost
                })
            except Exception as e:
                logger.error(f"Error sending cost update to {session_id}: {e}")
                self.disconnect(session_id)

    async def send_agent_status(self, session_id: str, agent: str, status: str, details: dict = None):
        """Send agent status update."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "agent_status",
                    "data": {
                        "agent": agent,
                        "status": status,
                        "details": details or {}
                    }
                })
            except Exception as e:
                logger.error(f"Error sending agent status to {session_id}: {e}")
                self.disconnect(session_id)

    async def send_chapter_preview(self, session_id: str, chapter_num: int, preview: str):
        """Send chapter preview."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "chapter_preview",
                    "data": {
                        "chapter": chapter_num,
                        "preview": preview[:500] + "..." if len(preview) > 500 else preview
                    }
                })
            except Exception as e:
                logger.error(f"Error sending chapter preview to {session_id}: {e}")
                self.disconnect(session_id)

    async def send_completion(self, session_id: str, book_id: str):
        """Send completion notification."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "completed",
                    "data": {"book_id": book_id}
                })
            except Exception as e:
                logger.error(f"Error sending completion to {session_id}: {e}")
                self.disconnect(session_id)


# Global instance
ws_manager = ConnectionManager()
