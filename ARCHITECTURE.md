# NARRA_FORGE Architecture Documentation

Deep technical documentation of system architecture.

---

## 🏛️ System Overview

NARRA_FORGE is a **multi-agent narrative production system** built on:
- **Model-agnostic LLM orchestration**
- **Triple memory architecture** (structural/semantic/evolutionary)
- **10-stage production pipeline**
- **World management system** for multi-IP operations

---

## 🧬 Core Components

### 1. Memory System (`narra_forge/memory/`)

#### Triple Memory Architecture

**Structural Memory** (`structural.py`)
- **Purpose**: Store static structure of narrative universes
- **Contains**: Worlds, characters, rules, archetypes
- **Operations**:
  - `store_world(world: WorldBible)` → Store world definition
  - `retrieve_world(world_id: str)` → Load world
  - `store_character(character: Character)` → Store character
  - `get_world_characters(world_id: str)` → Get all characters
  - `store_rule_system()`, `store_archetype()` → Store world rules/archetypes

**Semantic Memory** (`semantic.py`)
- **Purpose**: Store dynamic narrative content
- **Contains**: Events, motifs, relationships, consequences
- **Operations**:
  - `store_event(world_id, event_data)` → Record narrative event
  - `get_world_events(world_id)` → Get chronological event list
  - `store_motif()` → Track recurring themes
  - `store_relationship()` → Store entity relationships
  - `update_relationship()` → Track relationship evolution

**Evolutionary Memory** (`evolutionary.py`)
- **Purpose**: Track transformation over time
- **Contains**: Character evolution, world state changes, learning
- **Operations**:
  - `track_character_evolution()` → Record character change
  - `track_world_state_change()` → Record world evolution
  - `track_relationship_evolution()` → Track relationship changes
  - `track_learning()` → Character knowledge acquisition
  - `analyze_evolution_patterns()` → Statistical analysis

#### Storage Backend

**SQLite Implementation** (`base.py`)
- Persistent storage with ACID guarantees
- Indexed queries for performance
- JSON encoding for complex structures
- Schema:
  ```sql
  memory_entries (
    entry_id TEXT PRIMARY KEY,
    memory_type TEXT,
    world_id TEXT,
    content TEXT,  -- JSON
    created_at TEXT,
    updated_at TEXT,
    metadata TEXT  -- JSON
  )
  ```

---

### 2. Model Orchestration (`narra_forge/models/`)

#### Abstraction Layer

**ModelBackend** (`backend.py`)
- Abstract base class for all LLM backends
- Interface:
  ```python
  async def generate(prompt, system_prompt, temperature, max_tokens)
  async def generate_structured(prompt, schema, system_prompt)
  ```
- Tracks usage metrics (tokens, cost)

**ModelOrchestrator** (`backend.py`)
- Manages multiple backends
- Handles:
  - Model selection (by task complexity)
  - Automatic fallback on failure
  - Retry logic with exponential backoff
  - Cost optimization
- Methods:
  ```python
  async def generate()  # With automatic fallback
  def select_optimal_model(task_complexity, cost_priority)
  def get_all_metrics()
  ```

#### Implementations

**AnthropicBackend** (`anthropic_backend.py`)
- Claude integration (Opus 4.5, Sonnet 4.5, Haiku)
- Features:
  - Structured output via prompt engineering
  - Long-form generation support
  - Extended context (planned: prompt caching)

**OpenAI Backend** (TODO)
**Local Model Backend** (TODO)

---

### 3. Agent System (`narra_forge/agents/`)

#### Base Agent (`base_agent.py`)

**BaseAgent** - Abstract base class
- Properties:
  - `name: str` - Agent identifier
  - `model: ModelOrchestrator` - Access to LLMs
  - `structural_memory`, `semantic_memory`, `evolutionary_memory` - Memory access
- Abstract methods:
  - `async execute(context) → AgentResponse` - Main execution
  - `get_system_prompt() → str` - Agent-specific prompt
  - `validate_input(context) → bool` - Input validation
- Helper methods:
  - `async generate_text()` - Simplified text generation
  - `async generate_structured()` - Simplified structured generation

**CompositionalAgent** - Multi-agent composition
- Can delegate to sub-agents
- Used for complex multi-step tasks

#### Specialized Agents

**Stage 1: BriefInterpreterAgent** (`brief_interpreter.py`)
- **Input**: User narrative request
- **Output**: `ProjectBrief` (form, genre, scale, requirements)
- **Model**: Claude Sonnet (cost-effective for analysis)
- **Strategy**: Structured JSON extraction from natural language

**Stage 2: WorldArchitectAgent** (`world_architect.py`)
- **Input**: `ProjectBrief`
- **Output**: `WorldBible` (complete world definition)
- **Model**: Claude Opus (high creativity needed)
- **Strategy**:
  - Design laws of reality FIRST
  - Create constraints that enable drama
  - Define core conflict and existential theme
  - Ensure internal consistency

**Stage 3: CharacterArchitectAgent** (`character_architect.py`)
- **Input**: `WorldBible`, `ProjectBrief`
- **Output**: List of `Character` objects
- **Model**: Claude Opus (psychological complexity)
- **Strategy**:
  - Characters as PROCESSES, not static entities
  - Define internal trajectories
  - Create contradictions and cognitive limits
  - Establish initial relationships

**Stages 4-10**: (Implementation pending)
- Stage 4: Structure Designer
- Stage 5: Segment Planner
- Stage 6: Sequential Generator
- Stage 7: Coherence Validator
- Stage 8: Language Stylizer
- Stage 9: Editorial Reviewer
- Stage 10: Output Processor

---

### 4. World Management (`narra_forge/world/`)

**WorldManager** (`world_manager.py`)
- **Purpose**: Multi-IP world management
- **Features**:
  - Create and store worlds
  - Update world state with tracking
  - Validate world consistency
  - Link worlds (cross-world relationships)
  - World summarization
- **Caching**: Active worlds cached in memory
- **Evolution**: All state changes tracked in evolutionary memory

---

### 5. Orchestration (`narra_forge/core/`)

#### Main Orchestrator

**NarrativeOrchestrator** (`orchestrator.py`)
- **Purpose**: Manage complete production pipeline
- **Architecture**:
  ```
  User Request
       ↓
  Pipeline Stages (1-10)
       ↓
  Agents → Models → Memory
       ↓
  Final Output
  ```
- **Key Methods**:
  ```python
  async produce_narrative(user_request) → Result
  register_agent(stage, agent)
  get_production_status(project_id)
  ```

#### Pipeline Execution

**Flow**:
1. **Stage Execution**: `_execute_stage(stage, context)`
2. **Retry Logic**: Up to N attempts with exponential backoff
3. **Context Propagation**: Each stage adds to shared context
4. **Validation**: Each stage validates inputs before execution
5. **Error Handling**: Graceful degradation or failure reporting

**Context Structure**:
```python
{
    "project_id": str,
    "user_request": str,
    "brief": ProjectBrief,
    "world": WorldBible,
    "characters": List[Character],
    "structure": Dict,
    "segment_plan": List[Dict],
    "segments": List[NarrativeSegment],
    "coherence_report": Dict,
    ...
}
```

---

## 🔄 Data Flow

### Memory Flow

```
Agent Execution
    ↓
Generate Content
    ↓
Store in Memory (structural/semantic/evolutionary)
    ↓
Next Agent Retrieves from Memory
    ↓
Context-Aware Generation
```

### Production Flow

```
User Request
    ↓
[Stage 1] Brief Interpretation
    ↓ ProjectBrief
[Stage 2] World Architecture
    ↓ WorldBible → Structural Memory
[Stage 3] Character Architecture
    ↓ Characters → Structural Memory
[Stage 4] Narrative Structure
    ↓ Structure Plan
[Stage 5] Segment Planning
    ↓ Segment List
[Stage 6] Sequential Generation
    ↓ Generated Segments → Semantic Memory
[Stage 7] Coherence Validation
    ↓ Validation Report
[Stage 8] Language Stylization
    ↓ Stylized Text
[Stage 9] Editorial Review
    ↓ Edited Text
[Stage 10] Final Output
    ↓ Publication-Ready Text
```

---

## 🎯 Design Patterns

### 1. Strategy Pattern
- **Where**: Model selection
- **Why**: Different models for different complexity levels
- **Implementation**: `ModelOrchestrator.select_optimal_model()`

### 2. Template Method
- **Where**: Agent execution
- **Why**: Common execution flow, specialized steps
- **Implementation**: `BaseAgent` with abstract `execute()`

### 3. Repository Pattern
- **Where**: Memory system
- **Why**: Abstraction over storage mechanism
- **Implementation**: `MemorySystem` interface

### 4. Observer Pattern (Planned)
- **Where**: Production monitoring
- **Why**: Track pipeline progress
- **Implementation**: Event emission on stage completion

### 5. Chain of Responsibility
- **Where**: Model fallback
- **Why**: Graceful degradation
- **Implementation**: Fallback chain in `ModelOrchestrator`

---

## 🔐 Quality Control

### Validation Layers

1. **Input Validation**
   - Each agent validates its inputs
   - Early failure if requirements not met

2. **Coherence Validation** (Stage 7)
   - Logical consistency
   - Psychological validity
   - Temporal coherence
   - World rule compliance

3. **Quality Metrics**
   - Coherence score (0.0-1.0)
   - Minimum threshold: 0.85
   - Automatic retry if below threshold

### Error Handling

**Retry Strategy**:
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        result = await agent.execute(context)
        if result.success:
            return result
    except Exception as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

**Fallback Strategy**:
- Primary model fails → Use fallback model
- Fallback defined in `ModelConfig.fallback_to`
- Chain: Opus → Sonnet → Haiku → Error

---

## 🚀 Performance Optimization

### Current Optimizations

1. **Memory Caching**
   - Active worlds cached in `WorldManager._world_cache`
   - Reduces database reads

2. **Async Execution**
   - All I/O operations async
   - Enables parallel agent execution (planned)

3. **Model Selection**
   - Cheap models for simple tasks (Haiku)
   - Expensive models for critical tasks (Opus)

### Planned Optimizations

1. **Parallel Agent Execution**
   - Run independent stages in parallel
   - Example: Multiple segment generation

2. **Prompt Caching**
   - Cache world bibles in prompts
   - Reduce token costs

3. **Vector Embeddings**
   - Semantic search in memory
   - Fast similarity queries

4. **Batch Processing**
   - Generate multiple narratives in batch
   - Shared world initialization

---

## 📊 Extensibility

### Adding New Agents

```python
from narra_forge.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Your specialized prompt"

    def validate_input(self, context) -> bool:
        return "required_key" in context

    async def execute(self, context, **kwargs):
        # Your logic
        result = await self.generate_text(prompt="...")
        return AgentResponse(success=True, output=result)

# Register
orchestrator.register_agent(PipelineStage.CUSTOM, MyCustomAgent(...))
```

### Adding New Model Backends

```python
from narra_forge.models.backend import ModelBackend

class MyModelBackend(ModelBackend):
    async def generate(self, prompt, system_prompt, ...):
        # Call your model
        response = await your_api.generate(...)
        return ModelResponse(...)

    async def generate_structured(self, prompt, schema, ...):
        # Structured generation
        return parsed_json

# Register
backends["my-model"] = MyModelBackend(config)
```

### Adding Memory Storage Backends

```python
from narra_forge.memory.base import MemorySystem

class MyMemoryBackend(MemorySystem):
    def store(self, entry): ...
    def retrieve(self, entry_id): ...
    def query(self, filters): ...
    # ... implement interface

# Use
memory = MyMemoryBackend(config)
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test individual agents
- Mock model responses
- Validate memory operations

### Integration Tests
- Test agent interactions
- Test memory persistence
- Test error handling

### End-to-End Tests
- Complete pipeline execution
- Quality validation
- Performance benchmarks

---

## 📈 Monitoring & Metrics

### Track These Metrics:
- **Tokens Used**: Per stage, per project
- **Cost**: Total and per-stage breakdown
- **Duration**: Pipeline execution time
- **Quality Scores**: Coherence, consistency
- **Error Rates**: By stage, by model
- **Memory Growth**: Database size over time

### Logging:
- Stage completion
- Agent execution
- Model calls
- Memory operations
- Errors and warnings

---

**Architecture evolves with technology. Stay agnostic. Stay flexible.**
