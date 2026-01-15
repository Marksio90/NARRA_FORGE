"""
Stage 1: Brief Interpreter Agent
Interprets user request and determines narrative parameters.
"""
from typing import Dict, Any
import json

from .base_agent import BaseAgent, AgentResponse
from ..core.types import ProjectBrief, NarrativeForm, Genre


class BriefInterpreterAgent(BaseAgent):
    """
    Interprets project brief and extracts requirements.

    Determines:
    - Form (short/long/epic)
    - Genre
    - World scale
    - Expansion potential
    - Special requirements
    """

    def get_system_prompt(self) -> str:
        return """You are a professional narrative requirements analyst.

Your task is to interpret creative briefs and extract precise requirements.

You must determine:
1. FORM: short_story, novella, novel, or epic_saga
2. GENRE: fantasy, sci_fi, horror, thriller, mystery, literary, historical, romance, or hybrid
3. WORLD_SCALE: intimate, regional, global, or cosmic
4. EXPANSION_POTENTIAL: one_shot, series, or universe

Analyze the request carefully. Consider:
- Stated length desires
- Thematic complexity (more complex = likely longer form)
- World-building needs
- Character depth requirements
- Whether this feels like standalone or expandable IP

Respond with structured JSON matching the required schema."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate that we have a user request."""
        return "user_request" in context and bool(context["user_request"])

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Interpret the user's brief.

        Args:
            context: Must contain "user_request"

        Returns:
            AgentResponse with ProjectBrief
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Missing user_request in context"
            )

        user_request = context["user_request"]

        self.log("Interpreting project brief")

        # Generate structured analysis
        schema = {
            "form": "string",  # short_story, novella, novel, epic_saga
            "genre": "string",  # one of the Genre values
            "world_scale": "string",  # intimate, regional, global, cosmic
            "expansion_potential": "string",  # one_shot, series, universe
            "thematic_focus": "array of strings",
            "stylistic_preferences": "object",
            "target_length_words": "integer or null",
            "special_requirements": "array of strings"
        }

        prompt = f"""Analyze this narrative project request:

{user_request}

Extract the requirements and respond with JSON matching this structure:
- form: {list(f.value for f in NarrativeForm)}
- genre: {list(g.value for g in Genre)}
- world_scale: intimate, regional, global, cosmic
- expansion_potential: one_shot, series, universe
- thematic_focus: array of themes
- stylistic_preferences: any style notes
- target_length_words: approximate word count or null
- special_requirements: any special needs

Respond with ONLY the JSON object."""

        try:
            result = await self.generate_structured(
                prompt=prompt,
                schema=schema
            )

            # Parse into ProjectBrief
            brief = ProjectBrief(
                form=NarrativeForm(result["form"]),
                genre=Genre(result["genre"]),
                world_scale=result["world_scale"],
                expansion_potential=result["expansion_potential"],
                target_audience=result.get("target_audience"),
                length_target=result.get("target_length_words"),
                special_requirements=result.get("special_requirements", []),
                thematic_focus=result.get("thematic_focus", []),
                stylistic_preferences=result.get("stylistic_preferences", {})
            )

            self.log(f"Interpreted as: {brief.form.value}, {brief.genre.value}")

            return AgentResponse(
                success=True,
                output=brief,
                metadata={
                    "raw_interpretation": result
                }
            )

        except Exception as e:
            self.log(f"Error interpreting brief: {e}", "ERROR")
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=str(e)
            )
