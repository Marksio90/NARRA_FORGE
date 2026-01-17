"""
Checkpointing system for NARRA_FORGE pipeline.

Allows:
- Saving pipeline state after each stage
- Resuming from last successful checkpoint
- Cost rollback on failure
- Progress tracking for long-running jobs
"""

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from narra_forge.core.types import ProductionBrief, ProductionType


class CheckpointManager:
    """
    Manages checkpoints for pipeline execution.

    Features:
    - Save/load checkpoint state
    - Resume from last successful stage
    - Track costs and progress
    - Clean up old checkpoints
    """

    def __init__(self, checkpoint_dir: Path = Path("checkpoints")):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def get_job_checkpoint_dir(self, job_id: str) -> Path:
        """Get checkpoint directory for specific job."""
        job_dir = self.checkpoint_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def save_checkpoint(
        self,
        job_id: str,
        stage_name: str,
        stage_output: Any,
        metadata: Optional[Dict] = None,
    ) -> Path:
        """
        Save checkpoint for a stage.

        Args:
            job_id: Job identifier
            stage_name: Name of the stage (e.g., "02_world_architect")
            stage_output: Output from the stage
            metadata: Additional metadata (cost, tokens, duration, etc.)

        Returns:
            Path to checkpoint file
        """
        job_dir = self.get_job_checkpoint_dir(job_id)

        # Create checkpoint data
        checkpoint = {
            "job_id": job_id,
            "stage_name": stage_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage_output": stage_output,
            "metadata": metadata or {},
        }

        # Save checkpoint
        checkpoint_file = job_dir / f"{stage_name}.checkpoint"

        with open(checkpoint_file, "wb") as f:
            pickle.dump(checkpoint, f)

        # Also save JSON version for inspection
        json_file = job_dir / f"{stage_name}.json"
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "job_id": job_id,
                        "stage_name": stage_name,
                        "timestamp": checkpoint["timestamp"],
                        "metadata": metadata or {},
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except (TypeError, ValueError):
            # Skip JSON if data not serializable
            pass

        return checkpoint_file

    def load_checkpoint(self, job_id: str, stage_name: str) -> Optional[Dict]:
        """
        Load checkpoint for a stage.

        Args:
            job_id: Job identifier
            stage_name: Name of the stage

        Returns:
            Checkpoint data or None if not found
        """
        job_dir = self.get_job_checkpoint_dir(job_id)
        checkpoint_file = job_dir / f"{stage_name}.checkpoint"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, "rb") as f:
            return pickle.load(f)

    def get_latest_checkpoint(self, job_id: str) -> Optional[tuple[str, Dict]]:
        """
        Get the latest checkpoint for a job.

        Returns:
            Tuple of (stage_name, checkpoint_data) or None
        """
        job_dir = self.get_job_checkpoint_dir(job_id)

        if not job_dir.exists():
            return None

        # Find all checkpoint files
        checkpoints = list(job_dir.glob("*.checkpoint"))

        if not checkpoints:
            return None

        # Sort by modification time (newest first)
        checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Load latest
        latest_file = checkpoints[0]
        stage_name = latest_file.stem  # Remove .checkpoint extension

        with open(latest_file, "rb") as f:
            checkpoint_data = pickle.load(f)

        return stage_name, checkpoint_data

    def list_checkpoints(self, job_id: str) -> list[str]:
        """
        List all checkpoints for a job.

        Returns:
            List of stage names with checkpoints
        """
        job_dir = self.get_job_checkpoint_dir(job_id)

        if not job_dir.exists():
            return []

        checkpoints = job_dir.glob("*.checkpoint")
        return [cp.stem for cp in sorted(checkpoints, key=lambda p: p.stat().st_mtime)]

    def delete_checkpoints(self, job_id: str) -> None:
        """Delete all checkpoints for a job."""
        job_dir = self.get_job_checkpoint_dir(job_id)

        if job_dir.exists():
            import shutil
            shutil.rmtree(job_dir)

    def get_progress(self, job_id: str, total_stages: int = 10) -> Dict:
        """
        Get progress information for a job.

        Args:
            job_id: Job identifier
            total_stages: Total number of stages in pipeline

        Returns:
            Progress information
        """
        checkpoints = self.list_checkpoints(job_id)
        completed = len(checkpoints)
        percentage = (completed / total_stages * 100) if total_stages > 0 else 0

        # Get latest checkpoint for cost info
        latest = self.get_latest_checkpoint(job_id)
        total_cost = 0.0
        total_tokens = 0

        if latest:
            _, checkpoint_data = latest
            metadata = checkpoint_data.get("metadata", {})
            total_cost = metadata.get("cumulative_cost_usd", 0.0)
            total_tokens = metadata.get("cumulative_tokens", 0)

        return {
            "job_id": job_id,
            "completed_stages": completed,
            "total_stages": total_stages,
            "percentage": percentage,
            "latest_stage": checkpoints[-1] if checkpoints else None,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
        }

    def can_resume(self, job_id: str) -> bool:
        """Check if job can be resumed from checkpoint."""
        return len(self.list_checkpoints(job_id)) > 0

    def save_brief(self, job_id: str, brief: ProductionBrief) -> None:
        """Save production brief for a job."""
        job_dir = self.get_job_checkpoint_dir(job_id)
        brief_file = job_dir / "brief.json"

        with open(brief_file, "w", encoding="utf-8") as f:
            json.dump(brief.model_dump(), f, indent=2, ensure_ascii=False)

    def load_brief(self, job_id: str) -> Optional[ProductionBrief]:
        """Load production brief for a job."""
        job_dir = self.get_job_checkpoint_dir(job_id)
        brief_file = job_dir / "brief.json"

        if not brief_file.exists():
            return None

        with open(brief_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ProductionBrief(**data)

    def save_metadata(self, job_id: str, metadata: Dict) -> None:
        """Save job metadata."""
        job_dir = self.get_job_checkpoint_dir(job_id)
        metadata_file = job_dir / "metadata.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def load_metadata(self, job_id: str) -> Optional[Dict]:
        """Load job metadata."""
        job_dir = self.get_job_checkpoint_dir(job_id)
        metadata_file = job_dir / "metadata.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def cleanup_old_checkpoints(self, max_age_days: int = 30) -> int:
        """
        Clean up checkpoints older than max_age_days.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of jobs cleaned up
        """
        import time
        from datetime import timedelta

        now = time.time()
        max_age_seconds = timedelta(days=max_age_days).total_seconds()

        cleaned = 0

        for job_dir in self.checkpoint_dir.iterdir():
            if not job_dir.is_dir():
                continue

            # Check last modification time
            mtime = job_dir.stat().st_mtime
            age = now - mtime

            if age > max_age_seconds:
                import shutil
                shutil.rmtree(job_dir)
                cleaned += 1

        return cleaned


class PipelineStateManager:
    """
    High-level manager for pipeline state and resumption.

    Integrates with CheckpointManager to provide:
    - State accumulation across stages
    - Resume logic
    - Error recovery
    """

    def __init__(self, checkpoint_manager: CheckpointManager):
        """
        Initialize state manager.

        Args:
            checkpoint_manager: Checkpoint manager instance
        """
        self.checkpoint_manager = checkpoint_manager

    def initialize_job(
        self,
        job_id: str,
        brief: ProductionBrief,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Initialize a new job or load existing state.

        Args:
            job_id: Job identifier
            brief: Production brief
            metadata: Optional job metadata

        Returns:
            Initial state dictionary
        """
        # Check if we can resume
        if self.checkpoint_manager.can_resume(job_id):
            return self.resume_job(job_id)

        # Start fresh
        self.checkpoint_manager.save_brief(job_id, brief)

        if metadata:
            self.checkpoint_manager.save_metadata(job_id, metadata)

        return {
            "job_id": job_id,
            "brief": brief,
            "completed_stages": [],
            "stage_outputs": {},
            "cumulative_cost_usd": 0.0,
            "cumulative_tokens": 0,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    def resume_job(self, job_id: str) -> Dict:
        """
        Resume job from last checkpoint.

        Args:
            job_id: Job identifier

        Returns:
            Resumed state dictionary
        """
        # Load brief
        brief = self.checkpoint_manager.load_brief(job_id)
        metadata = self.checkpoint_manager.load_metadata(job_id)

        # Load all checkpoints
        checkpoints = self.checkpoint_manager.list_checkpoints(job_id)
        stage_outputs = {}
        cumulative_cost = 0.0
        cumulative_tokens = 0

        for stage_name in checkpoints:
            checkpoint = self.checkpoint_manager.load_checkpoint(job_id, stage_name)
            if checkpoint:
                stage_outputs[stage_name] = checkpoint["stage_output"]

                # Accumulate costs
                stage_metadata = checkpoint.get("metadata", {})
                cumulative_cost += stage_metadata.get("cost_usd", 0.0)
                cumulative_tokens += stage_metadata.get("tokens_used", 0)

        return {
            "job_id": job_id,
            "brief": brief,
            "completed_stages": checkpoints,
            "stage_outputs": stage_outputs,
            "cumulative_cost_usd": cumulative_cost,
            "cumulative_tokens": cumulative_tokens,
            "resumed_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_stage_result(
        self,
        state: Dict,
        stage_name: str,
        stage_output: Any,
        cost_usd: float = 0.0,
        tokens_used: int = 0,
    ) -> Dict:
        """
        Save stage result and update state.

        Args:
            state: Current state dictionary
            stage_name: Name of the stage
            stage_output: Output from the stage
            cost_usd: Cost for this stage
            tokens_used: Tokens used in this stage

        Returns:
            Updated state dictionary
        """
        job_id = state["job_id"]

        # Update cumulative tracking
        state["cumulative_cost_usd"] += cost_usd
        state["cumulative_tokens"] += tokens_used
        state["stage_outputs"][stage_name] = stage_output
        state["completed_stages"].append(stage_name)

        # Save checkpoint
        self.checkpoint_manager.save_checkpoint(
            job_id=job_id,
            stage_name=stage_name,
            stage_output=stage_output,
            metadata={
                "cost_usd": cost_usd,
                "tokens_used": tokens_used,
                "cumulative_cost_usd": state["cumulative_cost_usd"],
                "cumulative_tokens": state["cumulative_tokens"],
            },
        )

        return state

    def get_next_stage(
        self,
        state: Dict,
        all_stages: list[str],
    ) -> Optional[str]:
        """
        Get next stage to execute.

        Args:
            state: Current state dictionary
            all_stages: List of all pipeline stages in order

        Returns:
            Next stage name or None if complete
        """
        completed = set(state["completed_stages"])

        for stage in all_stages:
            if stage not in completed:
                return stage

        return None  # All stages complete

    def cleanup_on_success(self, job_id: str) -> None:
        """
        Clean up checkpoints after successful completion.

        Args:
            job_id: Job identifier
        """
        # Optionally keep checkpoints for audit
        # or delete them to save space
        # self.checkpoint_manager.delete_checkpoints(job_id)
        pass

    def rollback_on_failure(self, job_id: str, failed_stage: str) -> None:
        """
        Rollback on failure (mark for retry).

        Args:
            job_id: Job identifier
            failed_stage: Stage that failed
        """
        # Keep checkpoints for retry
        # Could add failure metadata
        metadata = self.checkpoint_manager.load_metadata(job_id) or {}
        metadata["last_failure"] = {
            "stage": failed_stage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.checkpoint_manager.save_metadata(job_id, metadata)


__all__ = [
    "CheckpointManager",
    "PipelineStateManager",
]
