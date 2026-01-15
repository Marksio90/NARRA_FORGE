# NARRA_FORGE V2 - Quick Start

**Version:** 2.0.0-foundation
**Date:** 2026-01-15
**Status:** Foundation (Agents are placeholders)

---

## 🎯 What Is This?

**NARRA_FORGE V2** is a **batch production engine** for publishing-grade narratives.

This is **NOT**:
- A chatbot
- A streaming system
- An interactive tool

This **IS**:
- A closed-cycle batch processor
- OpenAI-only (no Anthropic, no Claude)
- Docker-first (all tests in Docker)
- Production-grade architecture

---

## 🏗️ Current Status

**FOUNDATION VERSION**

✅ **Implemented:**
- Complete project structure
- Docker configuration
- OpenAI client with rate limiting
- Model router (mini vs gpt-4o)
- Triple memory system (structural, semantic, evolutionary)
- Batch orchestrator (10-stage pipeline)
- Configuration system
- Cost tracking

⏳ **In Progress:**
- Real agents (currently placeholders)
- Full prompts for each agent
- Quality validation
- UI

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repo
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE

# Copy .env
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-...
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
pip install -e .
```

### 3. Run Example

```bash
python example_basic.py
```

**Expected output:**
```
═══════════════════════════════════════════
  NARRA_FORGE V2 - Basic Example
═══════════════════════════════════════════

⚙ Loading configuration...
✓ Config loaded (model: gpt-4o-mini)

⚙ Initializing orchestrator...
✓ Orchestrator ready

📝 Production Brief:
   Type: short_story
   Genre: fantasy
   Inspiration: A young alchemist discovers...

🚀 Starting batch production...

═══════════════════════════════════════════
    NARRA_FORGE - Batch Production
═══════════════════════════════════════════

Job ID: job_abc123def456
Type: short_story
Genre: fantasy

⚙ Stage 1/10: Brief Interpretation
  ✓ Completed in 0.1s (cost: $0.05)

⚙ Stage 2/10: World Architecture
  ✓ Completed in 0.1s (cost: $0.10)

... [stages 3-10] ...

✓ Production complete!

═══════════════════════════════════════════
           Production Summary
═══════════════════════════════════════════

Job ID: job_abc123def456
Type: short_story
Genre: fantasy
Word Count: 123

Quality:
  Coherence: 0.90/1.0
  Logical: ✓
  Psychological: ✓
  Temporal: ✓

Cost: $2.50 USD
Tokens: 15,000
Time: 7.3s

Output:
  narrative: output/job_abc123def456/narrative.txt
  metadata: output/job_abc123def456/metadata.json

═══════════════════════════════════════════
```

---

## 🐳 Docker Testing

### Build and Run

```bash
# Build image
docker-compose build

# Run example
docker-compose run --rm narra_forge python example_basic.py
```

### Run Tests (when implemented)

```bash
# Run test suite
./docker-test.sh
```

---

## 📐 Architecture Overview

```
narra_forge/
├── core/                    # Core engine
│   ├── config.py           # Configuration (OpenAI keys, models)
│   ├── orchestrator.py     # Batch orchestrator (10-stage pipeline)
│   └── types.py            # Data types
│
├── models/                  # AI models (OpenAI ONLY)
│   ├── openai_client.py    # OpenAI API client
│   └── model_router.py     # Route mini vs gpt-4o
│
├── memory/                  # Triple memory system
│   ├── structural.py       # Worlds, characters (SKELETON)
│   ├── semantic.py         # Events, motifs (CONTENT)
│   ├── evolutionary.py     # Changes over time (TEMPORAL)
│   └── storage.py          # SQLite backend
│
├── agents/                  # 10 specialized agents (TODO)
│   ├── a01_brief_interpreter.py
│   ├── a02_world_architect.py
│   ├── ... [8 more agents]
│   └── a10_output_processor.py
│
└── ui/                      # User interface (TODO)
    └── batch_ui.py
```

---

## 🔧 Configuration

Edit `.env`:

```bash
# OpenAI API (REQUIRED)
OPENAI_API_KEY=sk-proj-...

# Models
DEFAULT_MINI_MODEL=gpt-4o-mini  # Analysis, planning
DEFAULT_GPT4_MODEL=gpt-4o       # Narrative generation

# Cost limits
MAX_COST_PER_JOB=10.0
WARN_COST_THRESHOLD=5.0

# Quality
MIN_COHERENCE_SCORE=0.85
MIN_LANGUAGE_QUALITY=0.80
MIN_NARRATIVE_WEIGHT=0.75

# Paths
DB_PATH=data/narra_forge.db
OUTPUT_DIR=output
```

---

## 💡 Usage Patterns

### Basic Production

```python
import asyncio
from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core import ProductionBrief, ProductionType, Genre

async def produce():
    config = NarraForgeConfig()
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()

    brief = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="Your story idea here..."
    )

    output = await orchestrator.produce_narrative(brief)
    print(f"Done! Output: {output.output_dir}")

asyncio.run(produce())
```

### With Custom Config

```python
from narra_forge.core.config import create_default_config

config = create_default_config(
    openai_api_key="sk-...",
    max_cost_per_job=20.0,  # Higher limit
    min_coherence_score=0.90  # Stricter quality
)

orchestrator = BatchOrchestrator(config)
```

---

## 🎨 Production Types

| Type | Word Count | Estimated Cost |
|------|-----------|---------------|
| `SHORT_STORY` | 5k-10k | $2-5 |
| `NOVELLA` | 10k-40k | $5-20 |
| `NOVEL` | 40k-120k | $20-100 |
| `EPIC_SAGA` | 120k+ | $100+ |

**Note:** Costs are estimates. Actual costs depend on:
- Complexity of brief
- Quality requirements
- Number of characters/locations
- Retry needs

---

## 🧪 Testing Strategy

### Unit Tests (TODO)
```bash
pytest tests/
```

### Integration Tests (TODO)
```bash
pytest tests/integration/
```

### Quality Tests (TODO)
```bash
python tests/quality/test_narrative_quality.py
```

### Cost Tests (TODO)
```bash
python tests/cost/test_token_usage.py
```

---

## 📊 Cost Optimization

**MINI EVERYWHERE, GPT-4 ONLY WHERE NECESSARY**

| Stage | Model | Why |
|-------|-------|-----|
| Brief Interpretation | mini | Analysis |
| World Architecture | mini | Structure |
| Character Architecture | mini | Structure |
| Structure Design | mini | Planning |
| Segment Planning | mini | Planning |
| **Sequential Generation** | **gpt-4o** | **Quality critical** |
| Coherence Validation | mini | Can judge quality |
| **Language Stylization** | **gpt-4o** | **Quality critical** |
| Editorial Review | mini | Can review |
| Output Processing | mini | Formatting |

**Result:** ~60-70% of tokens use mini (cheap), ~30-40% use gpt-4o (expensive but necessary)

---

## 🚧 Roadmap

### Phase 1: Foundation ✅ (DONE)
- [x] Project structure
- [x] Docker setup
- [x] OpenAI client
- [x] Memory system
- [x] Orchestrator skeleton

### Phase 2: Agents (CURRENT)
- [ ] Implement all 10 agents with full prompts
- [ ] Real narrative generation
- [ ] Quality validation
- [ ] Error handling & retries

### Phase 3: Polish
- [ ] Simple UI (CLI/Web)
- [ ] Comprehensive tests
- [ ] Documentation
- [ ] Performance optimization

### Phase 4: Production
- [ ] Multi-world support fully tested
- [ ] Long-form narrative support (novels, sagas)
- [ ] Cost optimization
- [ ] Production deployment

---

## ⚠️ Important Notes

1. **This is a foundation version.** Agents are placeholders that simulate work.

2. **No actual narrative is generated yet.** The system runs through all stages but produces placeholder text.

3. **Real implementation coming next.** Phase 2 will add:
   - Full agent prompts (Polish language)
   - Real OpenAI generation
   - Quality validation
   - Retry logic

4. **OpenAI API key required.** Get one at: https://platform.openai.com/api-keys

5. **Cost tracking is real.** Even though agents are placeholders, the cost tracking system is functional and will track real costs when agents are implemented.

---

## 📚 Documentation

- **[ARCHITECTURE_V2.md](ARCHITECTURE_V2.md)** - Complete architecture specification
- **[README.md](README.md)** - Project overview
- This file - Quick start guide

---

## 🆘 Troubleshooting

### "OPENAI_API_KEY not set"
```bash
cp .env.example .env
# Edit .env and add your key
```

### "Module not found"
```bash
pip install -e .
```

### Docker issues
```bash
# Rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs
```

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/Marksio90/NARRA_FORGE/issues)
- **Docs:** See ARCHITECTURE_V2.md

---

**Status:** Foundation established. Ready for agent implementation.

**Next:** Phase 2 - Implement real agents with full prompts.
