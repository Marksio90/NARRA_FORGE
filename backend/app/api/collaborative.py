"""
Collaborative Writing API - NarraForge 3.0 Phase 4
Endpoints for collaborative writing tools with version control
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.collaborative import (
    collaborative_writing_system,
    CollaboratorRole,
    ChangeType,
    SuggestionStatus,
    CommentType,
    ConflictResolution
)

router = APIRouter(prefix="/collaborative")


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Request to create collaboration session"""
    project_id: str
    document_id: str
    title: str
    initial_content: str = ""


class SessionResponse(BaseModel):
    """Collaboration session response"""
    success: bool
    session: Optional[Dict[str, Any]] = None
    message: str = ""


class JoinSessionRequest(BaseModel):
    """Request to join a session"""
    user_id: str
    username: str
    role: str = "editor"


class CollaboratorResponse(BaseModel):
    """Collaborator response"""
    success: bool
    collaborator: Optional[Dict[str, Any]] = None
    message: str = ""


class TextChangeRequest(BaseModel):
    """Request to make a text change"""
    user_id: str
    change_type: str
    position: int
    content: str = ""
    old_content: str = ""
    length: int = 0


class ChangeResponse(BaseModel):
    """Change response"""
    success: bool
    change: Optional[Dict[str, Any]] = None
    version: Optional[Dict[str, Any]] = None
    message: str = ""


class SuggestionRequest(BaseModel):
    """Request to create a suggestion"""
    user_id: str
    start_position: int
    end_position: int
    original_text: str
    suggested_text: str
    reason: str = ""


class SuggestionResponse(BaseModel):
    """Suggestion response"""
    success: bool
    suggestion: Optional[Dict[str, Any]] = None
    message: str = ""


class CommentRequest(BaseModel):
    """Request to add a comment"""
    user_id: str
    content: str
    comment_type: str = "general"
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    parent_id: Optional[str] = None


class CommentResponse(BaseModel):
    """Comment response"""
    success: bool
    comment: Optional[Dict[str, Any]] = None
    message: str = ""


class AIContributionRequest(BaseModel):
    """Request for AI contribution"""
    contribution_type: str
    context: str
    parameters: Optional[Dict[str, Any]] = None


# Endpoints

@router.post("/sessions/create", response_model=SessionResponse)
async def create_collaboration_session(request: CreateSessionRequest):
    """
    Create a new collaboration session

    Initializes a real-time collaborative editing session
    with version control and conflict resolution.
    """
    try:
        session = collaborative_writing_system.create_session(
            project_id=request.project_id,
            document_id=request.document_id,
            title=request.title,
            initial_content=request.initial_content
        )

        return SessionResponse(
            success=True,
            session=session.to_dict(),
            message="Collaboration session created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get collaboration session details"""
    try:
        session = collaborative_writing_system.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            success=True,
            session=session.to_dict(),
            message="Session retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/join", response_model=CollaboratorResponse)
async def join_session(session_id: str, request: JoinSessionRequest):
    """Join an existing collaboration session"""
    try:
        role = CollaboratorRole(request.role)

        collaborator = collaborative_writing_system.join_session(
            session_id=session_id,
            user_id=request.user_id,
            username=request.username,
            role=role
        )

        return CollaboratorResponse(
            success=True,
            collaborator=collaborator.to_dict(),
            message=f"Joined session as {role.value}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/leave")
async def leave_session(session_id: str, user_id: str):
    """Leave a collaboration session"""
    try:
        collaborative_writing_system.leave_session(
            session_id=session_id,
            user_id=user_id
        )

        return {
            "success": True,
            "message": "Left session successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/collaborators")
async def get_collaborators(session_id: str):
    """Get all collaborators in a session"""
    try:
        collaborators = collaborative_writing_system.get_collaborators(session_id)

        return {
            "success": True,
            "collaborators": [c.to_dict() for c in collaborators],
            "count": len(collaborators)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/changes", response_model=ChangeResponse)
async def make_change(session_id: str, request: TextChangeRequest):
    """
    Make a text change in the document

    Supports insert, delete, and replace operations
    with automatic version control.
    """
    try:
        change_type = ChangeType(request.change_type)

        change, version = collaborative_writing_system.make_change(
            session_id=session_id,
            user_id=request.user_id,
            change_type=change_type,
            position=request.position,
            content=request.content,
            old_content=request.old_content,
            length=request.length
        )

        return ChangeResponse(
            success=True,
            change=change.to_dict(),
            version=version.to_dict() if version else None,
            message="Change applied"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/content")
async def get_current_content(session_id: str):
    """Get the current document content"""
    try:
        content = collaborative_writing_system.get_current_content(session_id)

        return {
            "success": True,
            "content": content,
            "length": len(content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/versions")
async def get_version_history(session_id: str, limit: int = 50):
    """Get version history for a session"""
    try:
        versions = collaborative_writing_system.get_version_history(
            session_id=session_id,
            limit=limit
        )

        return {
            "success": True,
            "versions": [v.to_dict() for v in versions],
            "count": len(versions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/versions/{version_id}")
async def get_version(session_id: str, version_id: str):
    """Get a specific version"""
    try:
        version = collaborative_writing_system.get_version(
            session_id=session_id,
            version_id=version_id
        )

        if not version:
            raise HTTPException(status_code=404, detail="Version not found")

        return {
            "success": True,
            "version": version.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/versions/{version_id}/restore")
async def restore_version(session_id: str, version_id: str, user_id: str):
    """Restore document to a previous version"""
    try:
        version = collaborative_writing_system.restore_version(
            session_id=session_id,
            version_id=version_id,
            user_id=user_id
        )

        return {
            "success": True,
            "version": version.to_dict(),
            "message": f"Restored to version {version_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/suggestions", response_model=SuggestionResponse)
async def create_suggestion(session_id: str, request: SuggestionRequest):
    """Create a text suggestion for review"""
    try:
        suggestion = collaborative_writing_system.create_suggestion(
            session_id=session_id,
            user_id=request.user_id,
            start_position=request.start_position,
            end_position=request.end_position,
            original_text=request.original_text,
            suggested_text=request.suggested_text,
            reason=request.reason
        )

        return SuggestionResponse(
            success=True,
            suggestion=suggestion.to_dict(),
            message="Suggestion created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/suggestions")
async def get_suggestions(
    session_id: str,
    status: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Get all suggestions for a session"""
    try:
        suggestion_status = SuggestionStatus(status) if status else None

        suggestions = collaborative_writing_system.get_suggestions(
            session_id=session_id,
            status=suggestion_status,
            user_id=user_id
        )

        return {
            "success": True,
            "suggestions": [s.to_dict() for s in suggestions],
            "count": len(suggestions)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/suggestions/{suggestion_id}/accept")
async def accept_suggestion(session_id: str, suggestion_id: str, user_id: str):
    """Accept a suggestion and apply it"""
    try:
        suggestion = collaborative_writing_system.accept_suggestion(
            session_id=session_id,
            suggestion_id=suggestion_id,
            reviewer_id=user_id
        )

        return {
            "success": True,
            "suggestion": suggestion.to_dict(),
            "message": "Suggestion accepted and applied"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    session_id: str,
    suggestion_id: str,
    user_id: str,
    reason: str = ""
):
    """Reject a suggestion"""
    try:
        suggestion = collaborative_writing_system.reject_suggestion(
            session_id=session_id,
            suggestion_id=suggestion_id,
            reviewer_id=user_id,
            reason=reason
        )

        return {
            "success": True,
            "suggestion": suggestion.to_dict(),
            "message": "Suggestion rejected"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/comments", response_model=CommentResponse)
async def add_comment(session_id: str, request: CommentRequest):
    """Add a comment to the document"""
    try:
        comment_type = CommentType(request.comment_type)

        comment = collaborative_writing_system.add_comment(
            session_id=session_id,
            user_id=request.user_id,
            content=request.content,
            comment_type=comment_type,
            start_position=request.start_position,
            end_position=request.end_position,
            parent_id=request.parent_id
        )

        return CommentResponse(
            success=True,
            comment=comment.to_dict(),
            message="Comment added"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/comments")
async def get_comments(
    session_id: str,
    resolved: Optional[bool] = None,
    comment_type: Optional[str] = None
):
    """Get all comments for a session"""
    try:
        ctype = CommentType(comment_type) if comment_type else None

        comments = collaborative_writing_system.get_comments(
            session_id=session_id,
            resolved=resolved,
            comment_type=ctype
        )

        return {
            "success": True,
            "comments": [c.to_dict() for c in comments],
            "count": len(comments)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/comments/{comment_id}/resolve")
async def resolve_comment(session_id: str, comment_id: str, user_id: str):
    """Mark a comment as resolved"""
    try:
        comment = collaborative_writing_system.resolve_comment(
            session_id=session_id,
            comment_id=comment_id,
            resolver_id=user_id
        )

        return {
            "success": True,
            "comment": comment.to_dict(),
            "message": "Comment resolved"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/conflicts")
async def get_conflicts(session_id: str):
    """Get all unresolved conflicts"""
    try:
        conflicts = collaborative_writing_system.get_conflicts(session_id)

        return {
            "success": True,
            "conflicts": [c.to_dict() for c in conflicts],
            "count": len(conflicts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    session_id: str,
    conflict_id: str,
    resolution: str,
    merged_content: Optional[str] = None
):
    """Resolve a conflict"""
    try:
        resolution_type = ConflictResolution(resolution)

        conflict = collaborative_writing_system.resolve_conflict(
            session_id=session_id,
            conflict_id=conflict_id,
            resolution=resolution_type,
            merged_content=merged_content
        )

        return {
            "success": True,
            "conflict": conflict.to_dict(),
            "message": f"Conflict resolved using {resolution}"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/ai-assist")
async def request_ai_assistance(session_id: str, request: AIContributionRequest):
    """
    Request AI assistance for collaborative writing

    Types: continuation, rewrite, expansion, summary, dialogue, description
    """
    try:
        contribution = collaborative_writing_system.get_ai_contribution(
            session_id=session_id,
            contribution_type=request.contribution_type,
            context=request.context,
            parameters=request.parameters or {}
        )

        return {
            "success": True,
            "contribution": contribution.to_dict(),
            "message": f"AI {request.contribution_type} generated"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get collaboration statistics for a session"""
    try:
        stats = collaborative_writing_system.get_session_stats(session_id)

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/lock")
async def lock_section(
    session_id: str,
    user_id: str,
    start_position: int,
    end_position: int
):
    """Lock a section for exclusive editing"""
    try:
        lock = collaborative_writing_system.lock_section(
            session_id=session_id,
            user_id=user_id,
            start_position=start_position,
            end_position=end_position
        )

        return {
            "success": True,
            "lock": lock,
            "message": "Section locked"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/unlock")
async def unlock_section(session_id: str, user_id: str, lock_id: str):
    """Unlock a previously locked section"""
    try:
        collaborative_writing_system.unlock_section(
            session_id=session_id,
            user_id=user_id,
            lock_id=lock_id
        )

        return {
            "success": True,
            "message": "Section unlocked"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
