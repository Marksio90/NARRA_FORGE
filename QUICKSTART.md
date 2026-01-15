# NARRA_FORGE Quick Start Guide

Get up and running with NARRA_FORGE in 5 minutes.

---

## ⚡ Installation

```bash
# 1. Clone repository
git clone https://github.com/your-repo/NARRA_FORGE.git
cd NARRA_FORGE

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

---

## 🔑 Setup API Keys

```bash
# Set Anthropic API key (required)
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

---

## 🚀 Generate Your First Story

### Option 1: Run Example

```bash
python example_usage.py
```

This will:
1. Initialize the system
2. Create a world
3. Design characters
4. Start narrative generation

### Option 2: Python Script

```python
import asyncio
from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator

async def main():
    # Setup
    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    # Your narrative request
    request = """
    Stwórz krótkie opowiadanie fantasy o młodym magiku,
    który musi podjąć decyzję między prawdą a wiernością.

    Forma: opowiadanie (3000-5000 słów)
    Ton: introspektywny, moralnie złożony
    """

    # Generate
    result = await orchestrator.produce_narrative(request)

    # Results
    if result["success"]:
        print("✓ Story generated successfully!")
        print(f"Project ID: {result['project_id']}")
        # Access the generated content
        # print(result["output"])
    else:
        print(f"✗ Error: {result['error']}")

# Run
asyncio.run(main())
```

---

## 📚 Basic Concepts

### 1. World Creation

```python
from narra_forge.world.world_manager import WorldManager

world = world_manager.create_world(
    name="Nexus Prime",
    laws_of_reality={
        "physics": "Advanced post-singularity",
        "technology": "Nano-molecular",
        "social": "Post-scarcity consciousness"
    },
    core_conflict="Individual identity vs collective consciousness",
    existential_theme="What defines humanity after transcendence?"
)
```

### 2. Character Design

```python
# Characters are designed automatically based on world
# But you can specify character requirements:

result = await orchestrator.produce_narrative(
    request="Story with 3 main characters...",
    character_count=3,
    character_roles=["protagonist", "antagonist", "mentor"]
)
```

### 3. Memory System

The system automatically tracks:
- **Structural**: Worlds, characters, rules
- **Semantic**: Events, relationships, motifs
- **Evolutionary**: How things change

Access memory:

```python
# Get world summary
summary = orchestrator.world_manager.get_world_summary(world_id)

# Get character evolution
history = orchestrator.evolutionary_memory.get_character_evolution_history(
    world_id, character_id
)

# Get events
events = orchestrator.semantic_memory.get_world_events(world_id)
```

---

## 🎯 Request Format

### Short Story Request
```
Stwórz opowiadanie science fiction o [premise].

Forma: opowiadanie (5000 słów)
Ton: [dark/light/philosophical/action]
Temat: [themes]
```

### Novel Request
```
Napisz powieść fantasy o [premise].

Forma: powieść (50000-80000 słów)
Struktura: [trzyczęściowa/podróż bohatera/wielowątkowa]
Postacie: [liczba głównych postaci]
Świat: [skala: intimate/regional/global/cosmic]
```

### Epic Saga Request
```
Zaprojektuj sagę składającą się z [X] tomów o [premise].

Każdy tom: 80000-100000 słów
Skala świata: cosmic
Potencjał ekspansji: universe
Główne wątki: [lista]
```

---

## 🔧 Configuration

### Customize Model Usage

```python
from narra_forge.core.config import SystemConfig, ModelConfig

config = SystemConfig()

# Use faster model for some stages
config.models["stage1-4"] = ModelConfig(
    provider="anthropic",
    model_name="claude-3-5-haiku-20241022",
    temperature=0.6,
    cost_per_token=0.000001
)

# Use best model for critical stages
config.models["stage6-9"] = ModelConfig(
    provider="anthropic",
    model_name="claude-opus-4-5-20251101",
    temperature=0.8,
    cost_per_token=0.000015
)
```

### Adjust Quality Settings

```python
config.min_coherence_score = 0.9  # Higher = stricter
config.enable_strict_validation = True
config.max_retries = 5
```

---

## 📊 Monitoring Production

```python
# Get production status
status = orchestrator.get_production_status(project_id)
print(f"Stage: {status['current_stage']}")
print(f"Progress: {status['progress']*100:.1f}%")

# List all active productions
productions = orchestrator.list_productions()
for prod in productions:
    print(f"{prod['project_id']}: {prod['current_stage']}")
```

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Error: "No module named 'anthropic'"
```bash
pip install anthropic
```

### Error: "Database locked"
```bash
# Delete database and restart
rm -rf data/memory.db
```

### Low quality output
```python
# Increase quality threshold
config.min_coherence_score = 0.9

# Use better models
config.default_model = "claude-opus"
```

---

## 📖 Next Steps

1. **Read Full Documentation**: See `README.md`
2. **Explore Architecture**: Check `narra_forge/` directory
3. **Customize Agents**: Extend `narra_forge/agents/`
4. **Add New Models**: Implement in `narra_forge/models/`
5. **Build UI**: Create web interface for the system

---

## 💡 Example Use Cases

### 1. Anthology Series
Generate multiple short stories in the same world:

```python
world_id = create_world(...)

for i in range(10):
    result = await orchestrator.produce_narrative(
        f"Story {i+1} in world X...",
        world_id=world_id
    )
```

### 2. Character-Driven Saga
Create interconnected novels following characters:

```python
# Book 1
book1 = await produce_narrative("Origin story...")

# Book 2 - continue with same characters
book2 = await produce_narrative(
    "Sequel with characters from Book 1...",
    world_id=book1.world_id,
    characters=book1.characters
)
```

### 3. Multi-World Universe
Build connected but distinct worlds:

```python
world_a = create_world("Fantasy Realm")
world_b = create_world("Sci-Fi Future")

# Link worlds
world_manager.link_worlds(world_a.id, world_b.id, "portal")

# Generate cross-world story
result = await produce_narrative(
    "Character travels between worlds...",
    world_ids=[world_a.id, world_b.id]
)
```

---

**Ready to forge narratives? Start generating!** 🚀
