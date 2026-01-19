"""Pydantic v2 schemas for data validation and contracts."""

from models.schemas.agent import (
    CharacterRequest,
    CharacterResponse,
    InterpretRequest,
    InterpretResponse,
    PlotRequest,
    PlotResponse,
    ProseRequest,
    ProseResponse,
    QARequest,
    QAResponse,
    StyleRequest,
    StyleResponse,
    WorldRequest,
    WorldResponse,
)
from models.schemas.base import BaseRequest, BaseResponse, ErrorResponse, PaginationParams
from models.schemas.domain import (
    ArtifactSchema,
    CharacterSchema,
    CostSnapshotSchema,
    PlotSchema,
    SegmentSchema,
    WorldSchema,
)
from models.schemas.job import (
    CreateJobRequest,
    JobResponse,
    JobStatusUpdate,
    PipelineExecutionResponse,
)

__all__ = [
    # Base
    "BaseRequest",
    "BaseResponse",
    "ErrorResponse",
    "PaginationParams",
    # Agent
    "InterpretRequest",
    "InterpretResponse",
    "WorldRequest",
    "WorldResponse",
    "CharacterRequest",
    "CharacterResponse",
    "PlotRequest",
    "PlotResponse",
    "ProseRequest",
    "ProseResponse",
    "QARequest",
    "QAResponse",
    "StyleRequest",
    "StyleResponse",
    # Domain
    "WorldSchema",
    "CharacterSchema",
    "PlotSchema",
    "SegmentSchema",
    "ArtifactSchema",
    "CostSnapshotSchema",
    # Job
    "CreateJobRequest",
    "JobResponse",
    "JobStatusUpdate",
    "PipelineExecutionResponse",
]
