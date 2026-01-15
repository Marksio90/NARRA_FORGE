"""
Base Agent for NARRA_FORGE V2

All agents inherit from this base class.
Provides access to:
- Memory system (structural, semantic, evolutionary)
- Model router (for OpenAI API calls)
- Configuration

Each agent has ONE responsibility and communicates via structured data.
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from narra_forge.core.config import NarraForgeConfig
from narra_forge.core.types import AgentResult, ModelCall, PipelineStage
from narra_forge.memory import MemorySystem
from narra_forge.models import ModelRouter


class BaseAgent(ABC):
    """
    Base class for all agents.

    Each agent:
    - Has ONE responsibility
    - Works deterministically
    - Communicates via structured data
    - Has access to memory and models
    """

    def __init__(
        self,
        config: NarraForgeConfig,
        memory: MemorySystem,
        router: ModelRouter,
        stage: PipelineStage,
    ):
        """
        Initialize base agent.

        Args:
            config: System configuration
            memory: Memory system (structural, semantic, evolutionary)
            router: Model router for AI calls
            stage: Pipeline stage this agent handles
        """
        self.config = config
        self.memory = memory
        self.router = router
        self.stage = stage

        # Track execution
        self.model_calls: List[ModelCall] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute agent logic.

        This is the main entry point for each agent.
        Must be implemented by each agent subclass.

        Args:
            context: Execution context (job data, previous results, etc.)

        Returns:
            AgentResult with structured output
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get system prompt for this agent.

        Each agent has its own prompt that defines:
        - Its identity and role
        - Its capabilities
        - Output format
        - Quality standards

        Returns:
            System prompt in Polish
        """
        pass

    async def call_model(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> tuple[str, ModelCall]:
        """
        Call AI model with appropriate routing.

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Max completion tokens
            json_mode: Use JSON mode

        Returns:
            (response_text, model_call_record)
        """
        system_prompt = self.get_system_prompt()

        if json_mode:
            response, call = await self.router.generate_json(
                prompt=prompt,
                stage=self.stage,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # Convert dict to string for consistent return type
            import json
            text = json.dumps(response, ensure_ascii=False, indent=2)
            self.model_calls.append(call)
            return text, call
        else:
            text, call = await self.router.generate(
                prompt=prompt,
                stage=self.stage,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            self.model_calls.append(call)
            return text, call

    async def call_model_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> tuple[Dict[str, Any], ModelCall]:
        """
        Call AI model and return parsed JSON.

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Max completion tokens

        Returns:
            (parsed_dict, model_call_record)
        """
        system_prompt = self.get_system_prompt()

        data, call = await self.router.generate_json(
            prompt=prompt,
            stage=self.stage,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self.model_calls.append(call)
        return data, call

    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        """Add an error message"""
        self.errors.append(message)

    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Run agent with timing and error handling.

        This wraps execute() with standard timing and result packaging.

        Args:
            context: Execution context

        Returns:
            AgentResult
        """
        start_time = time.time()

        try:
            result = await self.execute(context)
            result.execution_time_seconds = time.time() - start_time
            return result

        except Exception as e:
            # Handle execution failure
            self.add_error(f"Agent execution failed: {str(e)}")

            return AgentResult(
                agent_name=self.__class__.__name__,
                stage=self.stage,
                success=False,
                data={},
                model_calls=self.model_calls,
                warnings=self.warnings,
                errors=self.errors,
                execution_time_seconds=time.time() - start_time,
            )

    def _create_result(
        self,
        success: bool,
        data: Dict[str, Any],
    ) -> AgentResult:
        """
        Helper to create AgentResult.

        Args:
            success: Whether execution succeeded
            data: Result data

        Returns:
            AgentResult
        """
        return AgentResult(
            agent_name=self.__class__.__name__,
            stage=self.stage,
            success=success,
            data=data,
            model_calls=self.model_calls,
            warnings=self.warnings,
            errors=self.errors,
        )


class AnalysisAgent(BaseAgent):
    """
    Base class for analysis agents (using gpt-4o-mini).

    These agents analyze, plan, validate, structure.
    They don't generate narrative prose.
    """

    pass


class GenerationAgent(BaseAgent):
    """
    Base class for generation agents (using gpt-4o).

    These agents generate narrative prose or perform
    high-quality language work.
    """

    pass
