"""
Base agent class - foundation for all specialized agents
"""

from typing import Dict, Any
import logging
from abc import ABC, abstractmethod

from app.agents.model_tier_manager import model_tier_manager
from app.prompts.agent_prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all NarraForge agents
    
    All agents inherit from this and implement their specific logic
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.model_manager = model_tier_manager
        logger.info(f"Initialized agent: {agent_name}")
    
    def get_system_prompt(self, genre: str = "", language: str = "polski") -> str:
        """Get the system prompt for this agent"""
        return get_agent_prompt(self.agent_name, genre=genre, language=language)
    
    async def execute(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute agent task
        
        Args:
            task: Task specification with prompt and parameters
            context: Additional context (project data, previous outputs, etc.)
        
        Returns:
            Result dictionary with generated content and metadata
        """
        logger.info(f"{self.agent_name} executing task: {task.get('type', 'unknown')}")
        
        # Get system prompt
        genre = context.get("genre", "") if context else ""
        system_prompt = self.get_system_prompt(genre=genre)
        
        # Build user prompt
        user_prompt = self._build_prompt(task, context)
        
        # Determine task type for tier selection
        task_type = task.get("task_type", "simple_outline")
        
        # Generate content
        result = await self.model_manager.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            task_type=task_type,
            temperature=task.get("temperature", 0.7),
            max_tokens=task.get("max_tokens", 4000),
        )
        
        if not result["success"]:
            logger.error(f"{self.agent_name} generation failed: {result.get('error')}")
            return result
        
        # Check if escalation needed
        if result["tier"] < 3:  # Only escalate if not already at highest tier
            should_escalate = await self.model_manager.should_escalate(result["content"])
            if should_escalate:
                logger.info(f"{self.agent_name} escalating to higher tier")
                result = await self.model_manager.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    task_type=task_type,
                    temperature=task.get("temperature", 0.7),
                    max_tokens=task.get("max_tokens", 4000),
                    force_tier=result["tier"] + 1,
                )
        
        # Post-process result
        processed_result = self._post_process(result, task, context)
        
        logger.info(f"{self.agent_name} completed task successfully")
        return processed_result
    
    @abstractmethod
    def _build_prompt(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Build the user prompt for this specific agent
        Must be implemented by each agent
        """
        pass
    
    def _post_process(
        self,
        result: Dict[str, Any],
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Post-process the generated result
        Can be overridden by specific agents
        """
        return result
