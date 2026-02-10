"""
Intelligent Model Tier Manager
Automatically selects appropriate OpenAI model based on task complexity
"""

from typing import Literal, Dict, Any, Optional
import logging
from openai import AsyncOpenAI

from app.config import settings, model_tier_config

logger = logging.getLogger(__name__)

ModelTier = Literal[1, 2, 3]


class ModelTierManager:
    """
    Manages intelligent model selection and escalation
    
    TIER 1 (GPT-4o-mini): Simple tasks, validation, formatting
    TIER 2 (GPT-4o): Creative writing, character development, prose
    TIER 3 (GPT-4/o1): Critical scenes, complex resolution, final polish
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=300.0)
        self.tier_models = {
            1: settings.GPT_4O_MINI,
            2: settings.GPT_4O,
            3: settings.GPT_4,
        }
        self.tier_costs = {
            1: (settings.TIER1_INPUT_COST, settings.TIER1_OUTPUT_COST),
            2: (settings.TIER2_INPUT_COST, settings.TIER2_OUTPUT_COST),
            3: (settings.TIER3_INPUT_COST, settings.TIER3_OUTPUT_COST),
        }
    
    def get_tier_for_task(self, task_type: str) -> ModelTier:
        """
        Determine appropriate model tier for task type
        
        Args:
            task_type: Type of task (world_building, prose_writing, etc.)
        
        Returns:
            Model tier (1, 2, or 3)
        """
        tier = model_tier_config.get_tier_for_task(task_type)
        logger.debug(f"Selected tier {tier} for task type: {task_type}")
        return tier
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str,
        task_type: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        force_tier: Optional[ModelTier] = None,
    ) -> Dict[str, Any]:
        """
        Generate content using appropriate model tier
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for agent
            task_type: Type of task (determines tier if not forced)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            force_tier: Force specific tier (for escalation/de-escalation)
        
        Returns:
            Dict with content, usage, cost, and model info
        """
        # Determine tier
        tier = force_tier if force_tier else self.get_tier_for_task(task_type)

        # Type safety: coerce string tiers to int (handles legacy "TIER_1" values)
        if isinstance(tier, str):
            tier_map = {"TIER_1": 1, "TIER_2": 2, "TIER_3": 3}
            tier = tier_map.get(tier, int(tier) if tier.isdigit() else 1)

        model = self.tier_models.get(tier, settings.GPT_4O_MINI)
        
        logger.info(f"Generating with {model} (tier {tier}) for task: {task_type}")
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract content and usage
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost
            input_cost, output_cost = self.tier_costs[tier]
            cost = (
                (usage.prompt_tokens / 1_000_000) * input_cost +
                (usage.completion_tokens / 1_000_000) * output_cost
            )
            
            logger.info(
                f"Generated {usage.completion_tokens} tokens "
                f"(cost: ${cost:.4f}, model: {model})"
            )
            
            return {
                "content": content,
                "model": model,
                "tier": tier,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "cost": cost,
                "success": True,
            }
        
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return {
                "content": None,
                "error": str(e),
                "success": False,
            }
    
    async def should_escalate(
        self,
        content: str,
        quality_threshold: float = 0.7,
    ) -> bool:
        """
        Determine if content quality warrants tier escalation
        
        Args:
            content: Generated content
            quality_threshold: Minimum quality score (0-1)
        
        Returns:
            True if should escalate to higher tier
        """
        # In production, this would use a quality evaluation model
        # For now, simple heuristics
        
        # Check for warning signs of low quality
        # Includes both English and Polish phrases (platform generates in Polish)
        warning_signs = [
            len(content) < 100,  # Too short
            content.count("...") > 5,  # Too many ellipses
            "I cannot" in content,  # Refusal (English)
            "As an AI" in content,  # Breaking character (English)
            "Nie mogę" in content,  # Refusal (Polish)
            "Jako AI" in content,  # Breaking character (Polish)
            "Jako sztuczna inteligencja" in content,  # Breaking character (Polish)
            "nie jestem w stanie" in content,  # "I am unable to" (Polish)
            "Przepraszam, ale" in content,  # "I'm sorry, but" (Polish)
            "Nie jestem w stanie" in content,  # "I am not able to" (Polish)
        ]
        
        if any(warning_signs):
            logger.warning("Quality check failed - recommending escalation")
            return True
        
        return False


# Global instance
model_tier_manager = ModelTierManager()
