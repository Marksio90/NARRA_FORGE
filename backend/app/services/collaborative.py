"""
Collaborative Writing Tools - NarraForge 3.0 Phase 4

System for collaborative writing between human authors and AI,
including version control, commenting, suggestions, and real-time collaboration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from datetime import datetime
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class CollaboratorRole(Enum):
    """Roles in collaborative writing"""
    AUTHOR = "author"              # Primary author
    CO_AUTHOR = "co_author"        # Co-author with full edit rights
    EDITOR = "editor"              # Can suggest and comment
    REVIEWER = "reviewer"          # Can comment only
    AI_ASSISTANT = "ai_assistant"  # AI collaborator


class ChangeType(Enum):
    """Types of changes"""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    FORMAT = "format"
    MOVE = "move"
    MERGE = "merge"


class SuggestionStatus(Enum):
    """Status of a suggestion"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"


class CommentType(Enum):
    """Types of comments"""
    GENERAL = "general"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    ISSUE = "issue"
    PRAISE = "praise"
    AI_INSIGHT = "ai_insight"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    KEEP_MINE = "keep_mine"
    KEEP_THEIRS = "keep_theirs"
    MERGE = "merge"
    MANUAL = "manual"


class SessionStatus(Enum):
    """Collaboration session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Collaborator:
    """A collaborator in a writing project"""
    collaborator_id: str
    user_id: str
    name: str
    role: CollaboratorRole
    joined_at: datetime
    last_active: datetime
    permissions: List[str]
    color: str  # For highlighting contributions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collaborator_id": self.collaborator_id,
            "user_id": self.user_id,
            "name": self.name,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "permissions": self.permissions,
            "color": self.color
        }


@dataclass
class TextChange:
    """A change to the text"""
    change_id: str
    change_type: ChangeType
    chapter: int
    start_position: int
    end_position: int
    old_text: str
    new_text: str
    author_id: str
    timestamp: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "chapter": self.chapter,
            "start_position": self.start_position,
            "end_position": self.end_position,
            "old_text": self.old_text,
            "new_text": self.new_text,
            "author_id": self.author_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class Version:
    """A version of the document"""
    version_id: str
    version_number: int
    chapter: int
    content: str
    changes_from_previous: List[str]  # Change IDs
    author_id: str
    created_at: datetime
    message: str
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "version_number": self.version_number,
            "chapter": self.chapter,
            "word_count": len(self.content.split()),
            "changes_count": len(self.changes_from_previous),
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat(),
            "message": self.message,
            "tags": self.tags
        }


@dataclass
class Suggestion:
    """A suggestion for text change"""
    suggestion_id: str
    chapter: int
    start_position: int
    end_position: int
    original_text: str
    suggested_text: str
    reason: str
    author_id: str
    status: SuggestionStatus
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    response: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggestion_id": self.suggestion_id,
            "chapter": self.chapter,
            "start_position": self.start_position,
            "end_position": self.end_position,
            "original_text": self.original_text,
            "suggested_text": self.suggested_text,
            "reason": self.reason,
            "author_id": self.author_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "response": self.response
        }


@dataclass
class Comment:
    """A comment on the text"""
    comment_id: str
    chapter: int
    position: int
    selection_start: Optional[int]
    selection_end: Optional[int]
    selected_text: Optional[str]
    content: str
    comment_type: CommentType
    author_id: str
    created_at: datetime
    resolved: bool
    replies: List['Comment']
    thread_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "comment_id": self.comment_id,
            "chapter": self.chapter,
            "position": self.position,
            "selection_start": self.selection_start,
            "selection_end": self.selection_end,
            "selected_text": self.selected_text,
            "content": self.content,
            "comment_type": self.comment_type.value,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat(),
            "resolved": self.resolved,
            "replies": [r.to_dict() for r in self.replies],
            "thread_id": self.thread_id
        }


@dataclass
class Conflict:
    """A merge conflict"""
    conflict_id: str
    chapter: int
    position: int
    version_a: str
    version_b: str
    author_a: str
    author_b: str
    detected_at: datetime
    resolved: bool
    resolution: Optional[ConflictResolution]
    resolved_text: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "chapter": self.chapter,
            "position": self.position,
            "version_a": self.version_a,
            "version_b": self.version_b,
            "author_a": self.author_a,
            "author_b": self.author_b,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolution": self.resolution.value if self.resolution else None,
            "resolved_text": self.resolved_text
        }


@dataclass
class CollaborationSession:
    """A collaboration session"""
    session_id: str
    project_id: str
    collaborators: List[Collaborator]
    active_chapter: int
    status: SessionStatus
    changes: List[TextChange]
    suggestions: List[Suggestion]
    comments: List[Comment]
    conflicts: List[Conflict]
    versions: Dict[int, List[Version]]  # chapter -> versions
    current_editors: List[str]  # Currently editing
    started_at: datetime
    last_activity: datetime
    settings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "collaborators": [c.to_dict() for c in self.collaborators],
            "active_chapter": self.active_chapter,
            "status": self.status.value,
            "changes_count": len(self.changes),
            "suggestions_count": len(self.suggestions),
            "comments_count": len(self.comments),
            "conflicts_count": len([c for c in self.conflicts if not c.resolved]),
            "current_editors": self.current_editors,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "settings": self.settings
        }


@dataclass
class AIContribution:
    """An AI contribution to collaborative writing"""
    contribution_id: str
    contribution_type: str  # "suggestion", "draft", "expansion", "revision"
    chapter: int
    content: str
    context: str
    confidence: float
    accepted: Optional[bool]
    human_feedback: Optional[str]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contribution_id": self.contribution_id,
            "contribution_type": self.contribution_type,
            "chapter": self.chapter,
            "content": self.content,
            "context": self.context,
            "confidence": self.confidence,
            "accepted": self.accepted,
            "human_feedback": self.human_feedback,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# COLLABORATION SETTINGS
# =============================================================================

DEFAULT_PERMISSIONS = {
    CollaboratorRole.AUTHOR: ["read", "write", "delete", "manage", "publish"],
    CollaboratorRole.CO_AUTHOR: ["read", "write", "delete", "suggest"],
    CollaboratorRole.EDITOR: ["read", "suggest", "comment"],
    CollaboratorRole.REVIEWER: ["read", "comment"],
    CollaboratorRole.AI_ASSISTANT: ["read", "suggest"]
}

COLLABORATOR_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
]


# =============================================================================
# MAIN CLASS
# =============================================================================

class CollaborativeWritingSystem:
    """
    Collaborative Writing Tools System

    Enables real-time collaboration between human authors and AI,
    with version control, suggestions, and conflict resolution.
    """

    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.ai_contributions: Dict[str, List[AIContribution]] = {}

    async def create_session(
        self,
        project_id: str,
        creator_user_id: str,
        creator_name: str
    ) -> CollaborationSession:
        """
        Create a new collaboration session.
        """
        # Create creator as first collaborator
        creator = Collaborator(
            collaborator_id=str(uuid.uuid4()),
            user_id=creator_user_id,
            name=creator_name,
            role=CollaboratorRole.AUTHOR,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            permissions=DEFAULT_PERMISSIONS[CollaboratorRole.AUTHOR],
            color=COLLABORATOR_COLORS[0]
        )

        # Create AI assistant
        ai_assistant = Collaborator(
            collaborator_id="ai_assistant",
            user_id="ai",
            name="NarraForge AI",
            role=CollaboratorRole.AI_ASSISTANT,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            permissions=DEFAULT_PERMISSIONS[CollaboratorRole.AI_ASSISTANT],
            color="#888888"
        )

        session = CollaborationSession(
            session_id=str(uuid.uuid4()),
            project_id=project_id,
            collaborators=[creator, ai_assistant],
            active_chapter=1,
            status=SessionStatus.ACTIVE,
            changes=[],
            suggestions=[],
            comments=[],
            conflicts=[],
            versions={},
            current_editors=[creator_user_id],
            started_at=datetime.now(),
            last_activity=datetime.now(),
            settings={
                "auto_save": True,
                "track_changes": True,
                "ai_suggestions": True,
                "conflict_notification": True
            }
        )

        self.sessions[session.session_id] = session
        self.ai_contributions[session.session_id] = []

        return session

    async def add_collaborator(
        self,
        session_id: str,
        user_id: str,
        name: str,
        role: CollaboratorRole
    ) -> Collaborator:
        """
        Add a collaborator to a session.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        # Assign color
        used_colors = {c.color for c in session.collaborators}
        available_colors = [c for c in COLLABORATOR_COLORS if c not in used_colors]
        color = available_colors[0] if available_colors else COLLABORATOR_COLORS[0]

        collaborator = Collaborator(
            collaborator_id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            role=role,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            permissions=DEFAULT_PERMISSIONS[role],
            color=color
        )

        session.collaborators.append(collaborator)
        session.last_activity = datetime.now()

        return collaborator

    async def record_change(
        self,
        session_id: str,
        author_id: str,
        chapter: int,
        change_type: ChangeType,
        start_pos: int,
        end_pos: int,
        old_text: str,
        new_text: str
    ) -> TextChange:
        """
        Record a text change.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        change = TextChange(
            change_id=str(uuid.uuid4()),
            change_type=change_type,
            chapter=chapter,
            start_position=start_pos,
            end_position=end_pos,
            old_text=old_text,
            new_text=new_text,
            author_id=author_id,
            timestamp=datetime.now(),
            metadata={}
        )

        session.changes.append(change)
        session.last_activity = datetime.now()

        # Update collaborator activity
        for collab in session.collaborators:
            if collab.user_id == author_id:
                collab.last_active = datetime.now()

        return change

    async def create_version(
        self,
        session_id: str,
        chapter: int,
        content: str,
        author_id: str,
        message: str,
        tags: Optional[List[str]] = None
    ) -> Version:
        """
        Create a new version (snapshot) of a chapter.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        # Get previous version number
        chapter_versions = session.versions.get(chapter, [])
        version_number = len(chapter_versions) + 1

        # Get changes since last version
        recent_changes = [
            c.change_id for c in session.changes
            if c.chapter == chapter and
            (not chapter_versions or c.timestamp > chapter_versions[-1].created_at)
        ]

        version = Version(
            version_id=str(uuid.uuid4()),
            version_number=version_number,
            chapter=chapter,
            content=content,
            changes_from_previous=recent_changes,
            author_id=author_id,
            created_at=datetime.now(),
            message=message,
            tags=tags or []
        )

        if chapter not in session.versions:
            session.versions[chapter] = []
        session.versions[chapter].append(version)

        return version

    async def create_suggestion(
        self,
        session_id: str,
        author_id: str,
        chapter: int,
        start_pos: int,
        end_pos: int,
        original_text: str,
        suggested_text: str,
        reason: str
    ) -> Suggestion:
        """
        Create a suggestion for text change.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        suggestion = Suggestion(
            suggestion_id=str(uuid.uuid4()),
            chapter=chapter,
            start_position=start_pos,
            end_position=end_pos,
            original_text=original_text,
            suggested_text=suggested_text,
            reason=reason,
            author_id=author_id,
            status=SuggestionStatus.PENDING,
            created_at=datetime.now(),
            resolved_at=None,
            resolved_by=None,
            response=None
        )

        session.suggestions.append(suggestion)
        session.last_activity = datetime.now()

        return suggestion

    async def resolve_suggestion(
        self,
        session_id: str,
        suggestion_id: str,
        resolver_id: str,
        accept: bool,
        response: Optional[str] = None
    ) -> Suggestion:
        """
        Resolve a suggestion.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        suggestion = None
        for s in session.suggestions:
            if s.suggestion_id == suggestion_id:
                suggestion = s
                break

        if not suggestion:
            raise ValueError("Suggestion not found")

        suggestion.status = SuggestionStatus.ACCEPTED if accept else SuggestionStatus.REJECTED
        suggestion.resolved_at = datetime.now()
        suggestion.resolved_by = resolver_id
        suggestion.response = response

        return suggestion

    async def add_comment(
        self,
        session_id: str,
        author_id: str,
        chapter: int,
        position: int,
        content: str,
        comment_type: CommentType,
        selection_start: Optional[int] = None,
        selection_end: Optional[int] = None,
        selected_text: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Comment:
        """
        Add a comment.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        comment = Comment(
            comment_id=str(uuid.uuid4()),
            chapter=chapter,
            position=position,
            selection_start=selection_start,
            selection_end=selection_end,
            selected_text=selected_text,
            content=content,
            comment_type=comment_type,
            author_id=author_id,
            created_at=datetime.now(),
            resolved=False,
            replies=[],
            thread_id=thread_id
        )

        # If this is a reply, add to parent
        if thread_id:
            for c in session.comments:
                if c.comment_id == thread_id:
                    c.replies.append(comment)
                    break
        else:
            session.comments.append(comment)

        session.last_activity = datetime.now()

        return comment

    async def detect_conflicts(
        self,
        session_id: str,
        chapter: int,
        text_a: str,
        text_b: str,
        author_a: str,
        author_b: str
    ) -> List[Conflict]:
        """
        Detect merge conflicts between two versions.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        conflicts = []

        # Simple line-by-line conflict detection
        lines_a = text_a.split("\n")
        lines_b = text_b.split("\n")

        for i, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
            if line_a != line_b:
                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    chapter=chapter,
                    position=i,
                    version_a=line_a,
                    version_b=line_b,
                    author_a=author_a,
                    author_b=author_b,
                    detected_at=datetime.now(),
                    resolved=False,
                    resolution=None,
                    resolved_text=None
                )
                conflicts.append(conflict)
                session.conflicts.append(conflict)

        return conflicts

    async def resolve_conflict(
        self,
        session_id: str,
        conflict_id: str,
        resolution: ConflictResolution,
        resolved_text: Optional[str] = None
    ) -> Conflict:
        """
        Resolve a conflict.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        conflict = None
        for c in session.conflicts:
            if c.conflict_id == conflict_id:
                conflict = c
                break

        if not conflict:
            raise ValueError("Conflict not found")

        conflict.resolved = True
        conflict.resolution = resolution

        if resolution == ConflictResolution.KEEP_MINE:
            conflict.resolved_text = conflict.version_a
        elif resolution == ConflictResolution.KEEP_THEIRS:
            conflict.resolved_text = conflict.version_b
        elif resolution == ConflictResolution.MERGE:
            # Simple merge - combine both
            conflict.resolved_text = f"{conflict.version_a}\n{conflict.version_b}"
        else:
            conflict.resolved_text = resolved_text

        return conflict

    async def get_ai_suggestions(
        self,
        session_id: str,
        chapter: int,
        text: str,
        context: str
    ) -> List[AIContribution]:
        """
        Get AI suggestions for the text.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        contributions = []

        # Generate various types of AI suggestions
        suggestion_types = [
            ("improvement", "Poprawa stylistyczna"),
            ("expansion", "Rozwinięcie fragmentu"),
            ("alternative", "Alternatywne ujęcie")
        ]

        for stype, description in suggestion_types:
            contribution = AIContribution(
                contribution_id=str(uuid.uuid4()),
                contribution_type=stype,
                chapter=chapter,
                content=f"[AI {description}]: {text[:100]}...",
                context=context,
                confidence=0.75,
                accepted=None,
                human_feedback=None,
                created_at=datetime.now()
            )
            contributions.append(contribution)
            self.ai_contributions[session_id].append(contribution)

        return contributions

    async def provide_ai_feedback(
        self,
        session_id: str,
        contribution_id: str,
        accepted: bool,
        feedback: Optional[str] = None
    ) -> AIContribution:
        """
        Provide feedback on AI contribution.
        """
        contributions = self.ai_contributions.get(session_id, [])

        contribution = None
        for c in contributions:
            if c.contribution_id == contribution_id:
                contribution = c
                break

        if not contribution:
            raise ValueError("Contribution not found")

        contribution.accepted = accepted
        contribution.human_feedback = feedback

        return contribution

    async def get_change_history(
        self,
        session_id: str,
        chapter: Optional[int] = None,
        author_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get change history.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        changes = session.changes

        if chapter is not None:
            changes = [c for c in changes if c.chapter == chapter]

        if author_id:
            changes = [c for c in changes if c.author_id == author_id]

        return [c.to_dict() for c in sorted(changes, key=lambda x: x.timestamp, reverse=True)]

    async def get_collaboration_stats(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get collaboration statistics.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        # Calculate stats per collaborator
        collab_stats = {}
        for collab in session.collaborators:
            collab_changes = [c for c in session.changes if c.author_id == collab.user_id]
            collab_suggestions = [s for s in session.suggestions if s.author_id == collab.user_id]
            collab_comments = [c for c in session.comments if c.author_id == collab.user_id]

            collab_stats[collab.name] = {
                "role": collab.role.value,
                "changes": len(collab_changes),
                "suggestions": len(collab_suggestions),
                "comments": len(collab_comments),
                "last_active": collab.last_active.isoformat()
            }

        return {
            "session_id": session_id,
            "project_id": session.project_id,
            "duration_hours": (datetime.now() - session.started_at).total_seconds() / 3600,
            "total_changes": len(session.changes),
            "total_suggestions": len(session.suggestions),
            "pending_suggestions": len([s for s in session.suggestions if s.status == SuggestionStatus.PENDING]),
            "total_comments": len(session.comments),
            "unresolved_comments": len([c for c in session.comments if not c.resolved]),
            "conflicts_resolved": len([c for c in session.conflicts if c.resolved]),
            "conflicts_pending": len([c for c in session.conflicts if not c.resolved]),
            "collaborator_stats": collab_stats,
            "versions_created": sum(len(v) for v in session.versions.values()),
            "ai_contributions": len(self.ai_contributions.get(session_id, []))
        }

    async def compare_versions(
        self,
        session_id: str,
        chapter: int,
        version_a: int,
        version_b: int
    ) -> Dict[str, Any]:
        """
        Compare two versions of a chapter.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        versions = session.versions.get(chapter, [])

        ver_a = None
        ver_b = None

        for v in versions:
            if v.version_number == version_a:
                ver_a = v
            if v.version_number == version_b:
                ver_b = v

        if not ver_a or not ver_b:
            raise ValueError("Version not found")

        # Simple diff
        lines_a = ver_a.content.split("\n")
        lines_b = ver_b.content.split("\n")

        additions = []
        deletions = []
        modifications = []

        for i, (la, lb) in enumerate(zip(lines_a, lines_b)):
            if la != lb:
                modifications.append({
                    "line": i + 1,
                    "version_a": la,
                    "version_b": lb
                })

        # Lines only in one version
        if len(lines_a) > len(lines_b):
            deletions = lines_a[len(lines_b):]
        elif len(lines_b) > len(lines_a):
            additions = lines_b[len(lines_a):]

        return {
            "chapter": chapter,
            "version_a": ver_a.to_dict(),
            "version_b": ver_b.to_dict(),
            "modifications": len(modifications),
            "additions": len(additions),
            "deletions": len(deletions),
            "details": {
                "modifications": modifications[:20],
                "additions": additions[:10],
                "deletions": deletions[:10]
            }
        }

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get a collaboration session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List collaboration sessions."""
        sessions = self.sessions.values()

        if project_id:
            sessions = [s for s in sessions if s.project_id == project_id]

        return [s.to_dict() for s in sessions]

    def get_pending_suggestions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get pending suggestions for a session."""
        session = self.sessions.get(session_id)
        if not session:
            return []

        pending = [s for s in session.suggestions if s.status == SuggestionStatus.PENDING]
        return [s.to_dict() for s in pending]

    def get_unresolved_comments(self, session_id: str) -> List[Dict[str, Any]]:
        """Get unresolved comments for a session."""
        session = self.sessions.get(session_id)
        if not session:
            return []

        unresolved = [c for c in session.comments if not c.resolved]
        return [c.to_dict() for c in unresolved]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_collab_system: Optional[CollaborativeWritingSystem] = None


def get_collab_system() -> CollaborativeWritingSystem:
    """Get the singleton collaborative writing system instance."""
    global _collab_system
    if _collab_system is None:
        _collab_system = CollaborativeWritingSystem()
    return _collab_system
