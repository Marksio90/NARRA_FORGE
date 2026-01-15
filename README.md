# NARRA_FORGE

**Autonomous Multi-World Narrative Generation System of Absolute Publishing Class**

> Not a chatbot. Not a creative tool. Not a single model.
>
> A **SYNTHESIS** of advanced generative models, long-term memory systems, multi-agent orchestration, quality control mechanisms, publishing logic, and narrative architecture at universe scale.

---

## 🎯 Mission

**NARRA_FORGE** produces **READY-TO-SELL** narrative content:
- Short stories
- Long novels
- Multi-volume epic sagas
- Audiobook-ready content

Every form—SHORT or LONG—must meet THE SAME standard of quality, coherence, and depth.

---

## 🏗️ Core Principles

### 1. **ABSOLUTE PRINCIPLE**
Scale of text (short story vs novel) **NEVER** reduces:
- Narrative quality
- World depth
- Character coherence
- Plot logic
- Language level

**Short form ≠ Simplified form**
**Long form ≠ Bloated form**

Every text is a fragment of a **POTENTIAL UNIVERSE**.

---

### 2. **TECHNOLOGICAL PRINCIPLE (ULTIMATE)**

The system **MUST**:
- Leverage the latest available technologies
- Be **model-agnostic**
- Support integration with:
  - New LLM architectures
  - Long context (persistent memory)
  - Reflective agents
  - Narrative simulations
  - Algorithms beyond current paradigm (emergent models, symbolic hybrids, narrative prediction systems)

If available technology is:
- More accurate
- Cheaper
- More consistent
- Better scalable

→ **The system MUST prefer it.**

This is an **engine of the future**, not a temporary implementation.

---

### 3. **MULTI-WORLD / MULTI-IP**

The system handles:
- Multiple worlds
- Multiple universes
- Multiple timelines
- Multiple series
- Multiple independent stories

Each world:
- Has its own **World Bible**
- Own laws of reality
- Own archetypes
- Own constraints

Worlds can be:
- Isolated
- Interconnected
- Evolving over time

The system treats worlds as **IP**, and stories as **IP INSTANCES**.

---

## 🧠 Architecture

### Triple Memory System

1. **Structural Memory**
   - Worlds, characters, rules, archetypes
   - The SKELETON of narrative universes

2. **Semantic Memory**
   - Events, motifs, relationships
   - The LIVING CONTENT of stories

3. **Evolutionary Memory**
   - How worlds and characters change over time
   - Tracks TRANSFORMATION and GROWTH

### Multi-Agent Orchestration

Specialized agents for each responsibility:
- **Brief Interpreter** - Understands requirements
- **World Architect** - Designs complete worlds as systems
- **Character Architect** - Creates characters as PROCESSES, not static entities
- **Structure Designer** - Architects narrative structure
- **Segment Planner** - Plans chapters/scenes/sequences
- **Sequential Generator** - Generates content segment by segment
- **Coherence Validator** - Ensures logical/psychological/temporal consistency
- **Language Stylizer** - Highest level of Polish language
- **Editorial Reviewer** - Publishing-quality editing
- **Output Processor** - Final formatting (text, audiobook)

---

## 🚀 10-Stage Production Pipeline

```
1. BRIEF INTERPRETATION
   ↓ Determine form, genre, scale, potential

2. WORLD ARCHITECTURE
   ↓ Design world as complete system

3. CHARACTER ARCHITECTURE
   ↓ Design characters as dynamic processes

4. NARRATIVE STRUCTURE
   ↓ Choose structure appropriate for scale

5. SEGMENT PLANNING
   ↓ Plan chapters/scenes with narrative function

6. SEQUENTIAL GENERATION
   ↓ Generate segment by segment with memory

7. COHERENCE CONTROL
   ↓ Validate logical, psychological, temporal consistency

8. LANGUAGE STYLIZATION
   ↓ Highest level Polish, style matched to form

9. EDITORIAL REVIEW
   ↓ Publishing-quality editing

10. FINAL OUTPUT
    ↓ Ready-to-publish text + audiobook structure
```

---

## 📦 Installation

### Requirements
- Python 3.11+
- Anthropic API key (or OpenAI, or local models)

### Setup

```bash
# Clone repository
git clone https://github.com/your-repo/NARRA_FORGE.git
cd NARRA_FORGE

# Install dependencies
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"  # optional

# Run example
python example_usage.py
```

---

## 🎮 Usage

### Basic Usage

```python
import asyncio
from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator

async def generate_story():
    # Initialize
    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    # Define request
    request = """
    Stwórz opowiadanie fantasy o młodym alchemiku,
    który odkrywa, że jego mistrz jest odpowiedzialny
    za plagi niszczące królestwo.

    Forma: opowiadanie (~5000 słów)
    Ton: mroczny, moralnie złożony
    """

    # Generate
    result = await orchestrator.produce_narrative(request)

    if result["success"]:
        print(f"Story generated: {result['project_id']}")
        print(result["output"])
    else:
        print(f"Error: {result['error']}")

# Run
asyncio.run(generate_story())
```

### Advanced: Multi-World Management

```python
from narra_forge.world.world_manager import WorldManager

# Create world
world = world_manager.create_world(
    name="Umbral Expanse",
    laws_of_reality={
        "physics": "Newtonian with minor anomalies",
        "magic": "Elemental, requires sacrifice",
        "technology": "Medieval + alchemical"
    },
    core_conflict="Balance between order and chaos",
    existential_theme="The cost of power and knowledge"
)

# Generate story in this world
result = await orchestrator.produce_narrative(
    request="Create a story in Umbral Expanse...",
    world_id=world.world_id
)
```

---

## 🧬 System Components

### Core (`narra_forge/core/`)
- `orchestrator.py` - Main production engine
- `types.py` - Core type definitions
- `config.py` - Configuration management

### Memory (`narra_forge/memory/`)
- `base.py` - Memory system base
- `structural.py` - Structural memory (worlds, characters, rules)
- `semantic.py` - Semantic memory (events, motifs, relationships)
- `evolutionary.py` - Evolutionary memory (change tracking)

### Agents (`narra_forge/agents/`)
- `base_agent.py` - Agent base class
- `brief_interpreter.py` - Stage 1: Brief interpretation
- `world_architect.py` - Stage 2: World design
- `character_architect.py` - Stage 3: Character design
- *(Stages 4-10 agents to be completed)*

### Models (`narra_forge/models/`)
- `backend.py` - Model abstraction layer
- `anthropic_backend.py` - Anthropic (Claude) implementation
- `openai_backend.py` - OpenAI (GPT) implementation *(TODO)*
- `local_backend.py` - Local model support *(TODO)*

### World (`narra_forge/world/`)
- `world_manager.py` - Multi-IP world management

---

## 🎨 Design Philosophy

### Characters as Processes
Characters are **NOT** static descriptions. They are **dynamic processes** with:
- Internal trajectories (where they're going psychologically)
- Contradictions (internal conflicts)
- Cognitive limits (what they can't perceive)
- Evolution capacity (resistance to change)

### Worlds as Systems
Worlds are **complete systems** with:
- Laws of reality (rules that create constraints)
- Boundaries (spatial, temporal, dimensional)
- Anomalies (intentional exceptions)
- Core conflicts (fundamental tensions)
- Existential themes (narrative purpose)

### Quality Over Speed
- Every segment is validated for coherence
- Psychological consistency is mandatory
- World rules cannot be violated
- Language must be publication-quality

---

## 🔬 Technology Stack

- **Python 3.11+** - Core language
- **Anthropic Claude** - Primary LLM (Opus 4.5 for critical stages, Sonnet 4.5 for general)
- **OpenAI GPT-4** - Alternative/fallback
- **SQLite** - Persistent memory storage
- **Async/Await** - Concurrent agent execution
- **Model-agnostic architecture** - Ready for future models

---

## 📊 Quality Metrics

The system tracks:
- **Coherence Score** (0.0-1.0) - Logical consistency
- **Psychological Validity** - Character behavior consistency
- **World Consistency** - No rule violations
- **Narrative Weight** - Importance of each segment
- **Evolution Tracking** - Character and world changes

Minimum quality threshold: **0.85/1.0**

---

## 🚧 Roadmap

### Phase 1: Core Pipeline ✅
- [x] Memory systems
- [x] Agent framework
- [x] World management
- [x] Stages 1-3 agents

### Phase 2: Complete Pipeline
- [ ] Stages 4-10 agents
- [ ] Structure designer
- [ ] Segment planner
- [ ] Sequential generator
- [ ] Coherence validator
- [ ] Language stylizer
- [ ] Editorial reviewer
- [ ] Output processor

### Phase 3: Advanced Features
- [ ] Vector embeddings for semantic search
- [ ] Long-context caching
- [ ] Parallel agent execution
- [ ] Real-time coherence monitoring
- [ ] Multi-language support

### Phase 4: Production Ready
- [ ] Web interface
- [ ] API endpoints
- [ ] Batch processing
- [ ] Cost optimization
- [ ] Performance profiling

---

## 🤝 Contributing

This is a **professional narrative production system**.

Contributions must maintain:
- Architectural consistency
- Code quality standards
- Documentation completeness
- Test coverage

---

## 📄 License

*To be determined*

---

## 🎭 Philosophy

> "We don't create 'text'. We don't create 'stories'. We don't create 'books'.
>
> We create **WORLDS**, **HISTORIES**, **UNIVERSES**, **PUBLISHING PRODUCTS**.
>
> We operate as a narrative studio, a publisher of the future, an engine of timeless stories."

**NARRA_FORGE** is the synthesis of art and engineering at the highest level.

---

**Built with precision. Designed for infinity.**
