"""
Progress tracker - tracks generation progress.
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Tracks progress during book generation.
    """

    def __init__(self):
        self.current_phase = ""
        self.current_message = ""
        self.progress_percentage = 0.0
        self.chapter_progress = {
            'current': 0,
            'total': 0,
        }

    def update(
        self,
        phase: Optional[str] = None,
        message: Optional[str] = None,
        progress: Optional[float] = None
    ):
        """
        Update progress.

        Args:
            phase: Current phase (e.g., 'concept', 'writing', 'polishing')
            message: Progress message
            progress: Progress percentage (0-100)
        """
        if phase:
            self.current_phase = phase
        if message:
            self.current_message = message
        if progress is not None:
            self.progress_percentage = progress

        logger.info(
            f"Progress: {self.progress_percentage:.1f}% - "
            f"{self.current_phase}: {self.current_message}"
        )

    def update_chapter_progress(self, current: int, total: int):
        """Update chapter progress."""
        self.chapter_progress = {
            'current': current,
            'total': total,
        }

    def get_status(self) -> Dict:
        """Get current status."""
        return {
            'phase': self.current_phase,
            'message': self.current_message,
            'progress': self.progress_percentage,
            'chapter_progress': self.chapter_progress,
        }

    def reset(self):
        """Reset tracker."""
        self.current_phase = ""
        self.current_message = ""
        self.progress_percentage = 0.0
        self.chapter_progress = {'current': 0, 'total': 0}
