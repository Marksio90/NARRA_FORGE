"""
AI Writing Coach API - NarraForge 3.0 Phase 4
Endpoints for personalized AI writing coaching and skill development
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.writing_coach import (
    ai_writing_coach,
    WritingSkill,
    FeedbackType,
    ExerciseType,
    SkillLevel,
    CoachingMode
)

router = APIRouter(prefix="/coach")


# Request/Response Models
class WriterProfileRequest(BaseModel):
    """Request to create or update writer profile"""
    user_id: str
    name: str
    experience_level: str = "intermediate"
    genres: List[str] = []
    goals: List[str] = []
    weaknesses: List[str] = []
    preferred_coaching_style: str = "balanced"


class ProfileResponse(BaseModel):
    """Writer profile response"""
    success: bool
    profile: Optional[Dict[str, Any]] = None
    message: str = ""


class FeedbackRequest(BaseModel):
    """Request for writing feedback"""
    text: str
    context: str = ""
    focus_areas: Optional[List[str]] = None
    feedback_depth: str = "detailed"


class FeedbackResponse(BaseModel):
    """Writing feedback response"""
    success: bool
    feedback: List[Dict[str, Any]] = []
    overall_score: float = 0.0
    summary: str = ""


class ExerciseRequest(BaseModel):
    """Request for a writing exercise"""
    skill: str
    difficulty: str = "intermediate"
    topic: Optional[str] = None
    genre: Optional[str] = None
    time_limit_minutes: Optional[int] = None


class ExerciseResponse(BaseModel):
    """Exercise response"""
    success: bool
    exercise: Optional[Dict[str, Any]] = None
    message: str = ""


class SubmissionRequest(BaseModel):
    """Request to submit an exercise"""
    exercise_id: str
    submission_text: str
    time_spent_minutes: int


class SubmissionResponse(BaseModel):
    """Submission evaluation response"""
    success: bool
    evaluation: Optional[Dict[str, Any]] = None
    feedback: List[Dict[str, Any]] = []
    score: float = 0.0


class CoachingSessionRequest(BaseModel):
    """Request to start a coaching session"""
    mode: str = "practice"
    focus_skill: Optional[str] = None
    duration_minutes: int = 30
    intensity: str = "moderate"


class SessionResponse(BaseModel):
    """Coaching session response"""
    success: bool
    session: Optional[Dict[str, Any]] = None
    message: str = ""


class PromptRequest(BaseModel):
    """Request for a writing prompt"""
    genre: Optional[str] = None
    theme: Optional[str] = None
    difficulty: str = "intermediate"
    word_count_target: int = 500


# Endpoints

@router.post("/profiles/create", response_model=ProfileResponse)
async def create_writer_profile(request: WriterProfileRequest):
    """
    Create a new writer profile

    Sets up personalized coaching based on experience level,
    goals, and identified areas for improvement.
    """
    try:
        profile = ai_writing_coach.create_writer_profile(
            user_id=request.user_id,
            name=request.name,
            experience_level=request.experience_level,
            genres=request.genres,
            goals=request.goals,
            weaknesses=request.weaknesses,
            preferred_coaching_style=request.preferred_coaching_style
        )

        return ProfileResponse(
            success=True,
            profile=profile.to_dict(),
            message="Writer profile created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_writer_profile(user_id: str):
    """Get a writer's profile and progress"""
    try:
        profile = ai_writing_coach.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return ProfileResponse(
            success=True,
            profile=profile.to_dict(),
            message="Profile retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profiles/{user_id}", response_model=ProfileResponse)
async def update_writer_profile(user_id: str, request: WriterProfileRequest):
    """Update a writer's profile"""
    try:
        profile = ai_writing_coach.update_profile(
            user_id=user_id,
            name=request.name,
            experience_level=request.experience_level,
            genres=request.genres,
            goals=request.goals,
            weaknesses=request.weaknesses,
            preferred_coaching_style=request.preferred_coaching_style
        )

        return ProfileResponse(
            success=True,
            profile=profile.to_dict(),
            message="Profile updated"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/analyze", response_model=FeedbackResponse)
async def analyze_writing(user_id: str, request: FeedbackRequest):
    """
    Analyze writing and provide detailed feedback

    Evaluates:
    - Grammar and style
    - Dialogue quality
    - Description effectiveness
    - Pacing and structure
    - Character voice consistency
    - Show vs. tell balance
    """
    try:
        focus_skills = None
        if request.focus_areas:
            focus_skills = [WritingSkill(area) for area in request.focus_areas]

        feedback_list, score, summary = ai_writing_coach.analyze_writing(
            user_id=user_id,
            text=request.text,
            context=request.context,
            focus_skills=focus_skills,
            feedback_depth=request.feedback_depth
        )

        return FeedbackResponse(
            success=True,
            feedback=[f.to_dict() for f in feedback_list],
            overall_score=score,
            summary=summary
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/quick")
async def quick_feedback(text: str, aspect: str = "general"):
    """Get quick feedback on a specific aspect"""
    try:
        feedback = ai_writing_coach.quick_feedback(
            text=text,
            aspect=aspect
        )

        return {
            "success": True,
            "feedback": feedback,
            "aspect": aspect
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills")
async def get_available_skills():
    """Get all available writing skills for training"""
    try:
        skills = ai_writing_coach.get_available_skills()

        return {
            "success": True,
            "skills": skills
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/skills")
async def get_skill_progress(user_id: str):
    """Get skill progress for a writer"""
    try:
        progress = ai_writing_coach.get_skill_progress(user_id)

        return {
            "success": True,
            "skills": {skill: p.to_dict() for skill, p in progress.items()},
            "overall_level": ai_writing_coach.calculate_overall_level(user_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/skills/{skill}")
async def get_specific_skill_progress(user_id: str, skill: str):
    """Get progress for a specific skill"""
    try:
        writing_skill = WritingSkill(skill)
        progress = ai_writing_coach.get_specific_skill(user_id, writing_skill)

        if not progress:
            raise HTTPException(status_code=404, detail="Skill progress not found")

        return {
            "success": True,
            "skill": skill,
            "progress": progress.to_dict()
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid skill: {skill}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/generate", response_model=ExerciseResponse)
async def generate_exercise(user_id: str, request: ExerciseRequest):
    """
    Generate a personalized writing exercise

    Creates exercises targeting specific skills at
    appropriate difficulty levels.
    """
    try:
        skill = WritingSkill(request.skill)
        difficulty = SkillLevel(request.difficulty)

        exercise = ai_writing_coach.generate_exercise(
            user_id=user_id,
            skill=skill,
            difficulty=difficulty,
            topic=request.topic,
            genre=request.genre,
            time_limit_minutes=request.time_limit_minutes
        )

        return ExerciseResponse(
            success=True,
            exercise=exercise.to_dict(),
            message=f"Exercise generated for {skill.value}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises/{exercise_id}")
async def get_exercise(exercise_id: str):
    """Get an exercise by ID"""
    try:
        exercise = ai_writing_coach.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        return {
            "success": True,
            "exercise": exercise.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/submit", response_model=SubmissionResponse)
async def submit_exercise(
    exercise_id: str,
    user_id: str,
    request: SubmissionRequest
):
    """
    Submit an exercise for evaluation

    Evaluates the submission and updates skill progress.
    """
    try:
        submission = ai_writing_coach.submit_exercise(
            user_id=user_id,
            exercise_id=exercise_id,
            submission_text=request.submission_text,
            time_spent_minutes=request.time_spent_minutes
        )

        return SubmissionResponse(
            success=True,
            evaluation=submission.to_dict(),
            feedback=[f.to_dict() for f in submission.feedback],
            score=submission.score
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/exercises")
async def get_exercise_history(
    user_id: str,
    skill: Optional[str] = None,
    limit: int = 20
):
    """Get exercise history for a writer"""
    try:
        writing_skill = WritingSkill(skill) if skill else None

        history = ai_writing_coach.get_exercise_history(
            user_id=user_id,
            skill=writing_skill,
            limit=limit
        )

        return {
            "success": True,
            "exercises": [e.to_dict() for e in history],
            "count": len(history)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/start", response_model=SessionResponse)
async def start_coaching_session(user_id: str, request: CoachingSessionRequest):
    """
    Start a coaching session

    Modes:
    - practice: Focused skill practice with exercises
    - feedback: In-depth feedback on submitted writing
    - freewrite: Guided freewriting with prompts
    - review: Review and improve existing work
    """
    try:
        mode = CoachingMode(request.mode)
        focus_skill = WritingSkill(request.focus_skill) if request.focus_skill else None

        session = ai_writing_coach.start_session(
            user_id=user_id,
            mode=mode,
            focus_skill=focus_skill,
            duration_minutes=request.duration_minutes,
            intensity=request.intensity
        )

        return SessionResponse(
            success=True,
            session=session.to_dict(),
            message=f"Coaching session started in {mode.value} mode"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_coaching_session(session_id: str):
    """Get coaching session details"""
    try:
        session = ai_writing_coach.get_session(session_id)

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


@router.post("/sessions/{session_id}/complete")
async def complete_coaching_session(session_id: str):
    """Complete a coaching session and get summary"""
    try:
        summary = ai_writing_coach.complete_session(session_id)

        return {
            "success": True,
            "summary": summary,
            "message": "Session completed"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/generate")
async def generate_writing_prompt(user_id: str, request: PromptRequest):
    """Generate a personalized writing prompt"""
    try:
        difficulty = SkillLevel(request.difficulty)

        prompt = ai_writing_coach.generate_prompt(
            user_id=user_id,
            genre=request.genre,
            theme=request.theme,
            difficulty=difficulty,
            word_count_target=request.word_count_target
        )

        return {
            "success": True,
            "prompt": prompt.to_dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/recommendations")
async def get_recommendations(user_id: str):
    """
    Get personalized recommendations for improvement

    Based on:
    - Current skill levels
    - Recent exercise performance
    - Identified weaknesses
    - Learning goals
    """
    try:
        recommendations = ai_writing_coach.get_recommendations(user_id)

        return {
            "success": True,
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/stats")
async def get_writer_stats(user_id: str):
    """Get comprehensive statistics for a writer"""
    try:
        stats = ai_writing_coach.get_writer_stats(user_id)

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/achievements")
async def get_achievements(user_id: str):
    """Get writer's achievements and badges"""
    try:
        achievements = ai_writing_coach.get_achievements(user_id)

        return {
            "success": True,
            "achievements": achievements
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/{user_id}/goals")
async def set_writing_goals(user_id: str, goals: List[Dict[str, Any]]):
    """Set writing goals for tracking"""
    try:
        updated_goals = ai_writing_coach.set_goals(user_id, goals)

        return {
            "success": True,
            "goals": updated_goals,
            "message": f"Set {len(goals)} goals"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{user_id}/goals")
async def get_writing_goals(user_id: str):
    """Get writing goals and progress"""
    try:
        goals = ai_writing_coach.get_goals(user_id)

        return {
            "success": True,
            "goals": goals
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_texts(
    original_text: str,
    revised_text: str,
    aspects: Optional[List[str]] = None
):
    """Compare two versions of text and highlight improvements"""
    try:
        comparison = ai_writing_coach.compare_texts(
            original_text=original_text,
            revised_text=revised_text,
            aspects=aspects
        )

        return {
            "success": True,
            "comparison": comparison
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite-suggestions")
async def get_rewrite_suggestions(
    text: str,
    focus: str = "clarity",
    style: Optional[str] = None
):
    """Get AI suggestions for rewriting text"""
    try:
        suggestions = ai_writing_coach.get_rewrite_suggestions(
            text=text,
            focus=focus,
            target_style=style
        )

        return {
            "success": True,
            "suggestions": suggestions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
