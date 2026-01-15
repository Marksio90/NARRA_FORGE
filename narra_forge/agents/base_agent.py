"""
Base agent class for NARRA_FORGE.
All specialized agents inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..models.backend import ModelOrchestrator
from ..memory.base import MemorySystem
from ..memory.structural import StructuralMemory
from ..memory.semantic import SemanticMemory
from ..memory.evolutionary import EvolutionaryMemory


@dataclass
class AgentResponse:
    """Standardized agent response."""
    success: bool
    output: Any
    metadata: Dict[str, Any]
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base agent.
    Every agent has:
    - Single responsibility
    - Access to memory
    - Access to models
    - Cognitive scope
    """

    def __init__(
        self,
        name: str,
        model_orchestrator: ModelOrchestrator,
        memory_system: MemorySystem,
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.model = model_orchestrator
        self.config = config or {}

        # Memory interfaces
        self.structural_memory = StructuralMemory(memory_system)
        self.semantic_memory = SemanticMemory(memory_system)
        self.evolutionary_memory = EvolutionaryMemory(memory_system)

        # Agent state
        self.execution_count = 0
        self.last_execution_time = None

    @abstractmethod
    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Execute agent's task.

        Args:
            context: Current production context
            **kwargs: Additional parameters

        Returns:
            AgentResponse with results
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt."""
        pass

    @abstractmethod
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate that agent has necessary inputs."""
        pass

    def get_preferred_model(self) -> str:
        """Get preferred model for this agent."""
        return self.config.get("preferred_model", "claude-sonnet")

    def get_temperature(self) -> float:
        """Get sampling temperature for this agent."""
        return self.config.get("temperature", 0.7)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Helper method for text generation.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt (uses agent default if not provided)
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        response = await self.model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            preferred_model=self.get_preferred_model(),
            temperature=self.get_temperature(),
            **kwargs
        )

        self.execution_count += 1

        return response.content

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Helper method for structured generation.

        Args:
            prompt: User prompt
            schema: Expected output schema
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Parsed structured data
        """
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        result = await self.model.generate_structured(
            prompt=prompt,
            schema=schema,
            system_prompt=system_prompt,
            preferred_model=self.get_preferred_model(),
            **kwargs
        )

        self.execution_count += 1

        return result

    def log(self, message: str, level: str = "INFO"):
        """Log agent activity."""
        print(f"[{self.name}] {level}: {message}")


class CompositionalAgent(BaseAgent):
    """
    Agent that can invoke other agents.
    Used for complex multi-step tasks.
    """

    def __init__(
        self,
        name: str,
        model_orchestrator: ModelOrchestrator,
        memory_system: MemorySystem,
        sub_agents: Optional[Dict[str, BaseAgent]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, model_orchestrator, memory_system, config)
        self.sub_agents = sub_agents or {}

    def add_sub_agent(self, agent: BaseAgent):
        """Add a sub-agent to this compositional agent."""
        self.sub_agents[agent.name] = agent

    async def delegate_to(
        self,
        agent_name: str,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Delegate task to a sub-agent.

        Args:
            agent_name: Name of sub-agent
            context: Context to pass
            **kwargs: Additional parameters

        Returns:
            Sub-agent's response
        """
        if agent_name not in self.sub_agents:
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=f"Sub-agent '{agent_name}' not found"
            )

        agent = self.sub_agents[agent_name]
        self.log(f"Delegating to {agent_name}")

        return await agent.execute(context, **kwargs)
