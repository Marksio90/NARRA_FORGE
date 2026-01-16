# NARRA_FORGE V2 - KOMPLEKSOWY PLAN ROZWOJU PLATFORMY

**Data:** 2026-01-16
**Status:** Obecny system działa jako batch engine (CLI). Plan zakłada evolucję do pełnej platformy produkcyjnej.

---

## 📊 STAN OBECNY - PODSUMOWANIE

### ✅ Co działa:
- 10-stopniowy pipeline generacji narracji
- Triple Memory System (Structural + Semantic + Evolutionary)
- Walidacja jakości (0.88/1.0 coherence score)
- Batch processing (CLI)
- Docker containerization
- Cost tracking & token counting

### ⚠️ Co wymaga rozwoju:
- Brak interfejsu webowego
- Limited test coverage
- Brak API dla zewnętrznych integracji
- Brak monitoringu i observability
- Brak systemu użytkowników i projektów
- Brak long-form testing (powieści 120k+ słów)

---

## 🎯 WIZJA DOCELOWA

### Platform NARRA_FORGE jako:

**1. SaaS Platform** (Software as a Service)
- Web UI dla twórców treści
- REST/GraphQL API
- Multi-tenant architecture
- Subscription model (Free/Pro/Enterprise)

**2. Production Studio**
- Multi-project workspace
- Version control dla narracji
- Collaborative editing
- Export do popularnych formatów (ePub, PDF, Docx)

**3. AI Content Factory**
- Batch generation at scale
- Queue management
- Priority scheduling
- Cost optimization dashboard

---

## 🗺️ ROADMAP - 6 FAZ ROZWOJU

---

## FAZA 1: STABILIZACJA I FUNDAMENT (4-6 tygodni)

**Priorytet:** KRYTYCZNY
**Cel:** Stabilny foundation gotowy do skalowania

### 1.1 Testing & Quality Assurance

**Comprehensive Test Suite:**
```
tests/
├── unit/
│   ├── test_agents/           # Test każdego agenta osobno
│   ├── test_memory/           # Test systemów pamięci
│   ├── test_models/           # Test OpenAI wrapper
│   └── test_utils/            # Test utilities
├── integration/
│   ├── test_pipeline/         # Test całego pipeline'u
│   ├── test_memory_sync/      # Test persistence
│   └── test_error_recovery/   # Test error handling
├── e2e/
│   ├── test_short_story/      # Short story (5k-10k)
│   ├── test_novella/          # Novella (10k-40k)
│   ├── test_novel/            # Novel (40k-120k)
│   └── test_saga/             # Epic saga (120k+)
└── performance/
    ├── test_cost_tracking/    # Verify cost accuracy
    ├── test_token_limits/     # Test max_tokens handling
    └── test_memory_leaks/     # Memory profiling
```

**Coverage Target:** >80% dla core modules

**Test Automation:**
- GitHub Actions CI/CD pipeline
- Automated testing on PR
- Nightly long-form generation tests
- Performance regression tests

### 1.2 Monitoring & Observability

**Stack:**
- **Logging:** structlog (structured logging)
- **Metrics:** Prometheus + Grafana
- **Tracing:** OpenTelemetry (trace pipeline execution)
- **Error Tracking:** Sentry

**Key Metrics:**
```python
# Performance
- pipeline_duration_seconds (by production_type)
- agent_duration_seconds (by stage)
- tokens_per_second (throughput)

# Quality
- coherence_score (by genre, production_type)
- cliche_count (trend over time)
- validation_failures (by reason)

# Cost
- cost_per_narrative_usd (by production_type)
- cost_per_1k_tokens (by model)
- daily_spend_usd (budget tracking)

# Reliability
- api_errors_total (by provider, error_type)
- retry_count (by stage)
- success_rate_percent
```

### 1.3 Error Recovery & Resilience

**Retry Logic Enhancement:**
```python
# Current: Basic tenacity retries
# New: Intelligent retry with fallback

class PipelineRecovery:
    async def execute_stage(self, stage, input_data):
        try:
            return await self._execute_with_primary_model(stage, input_data)
        except ModelOverloadError:
            # Fallback to alternative model or queue
            return await self._queue_for_retry(stage, input_data)
        except ValidationError as e:
            # Retry with corrected input
            corrected = await self._auto_correct(input_data, e)
            return await self._execute_with_primary_model(stage, corrected)
        except CostLimitExceeded:
            # Prompt user or downgrade model
            return await self._handle_budget_exceeded(stage, input_data)
```

**Checkpoint System:**
- Save after each stage (allow resume from failure)
- Persistent queue for long-running jobs
- Cost rollback on failure

### 1.4 Configuration Management

**Environment Profiles:**
```yaml
# config/environments/
development.yaml:
  models:
    default: "gpt-4o-mini"  # Cheaper for dev
  rate_limits:
    rpm: 100
  features:
    enable_caching: true
    enable_metrics: false

staging.yaml:
  models:
    default: "gpt-4o"  # Production-like
  rate_limits:
    rpm: 500
  features:
    enable_caching: true
    enable_metrics: true

production.yaml:
  models:
    default: "gpt-4o"
  rate_limits:
    rpm: 3000
  features:
    enable_caching: true
    enable_metrics: true
    enable_alerting: true
```

**Feature Flags:**
```python
# Allow A/B testing of prompts, models, temperatures
class FeatureFlags:
    USE_NEW_GENERATOR_PROMPT: bool = False
    ENABLE_GPT4_TURBO: bool = False
    ENABLE_COST_OPTIMIZATION: bool = True
```

---

## FAZA 2: API & BACKEND (6-8 tygodni)

**Priorytet:** WYSOKI
**Cel:** RESTful API + Database + Authentication

### 2.1 Database Architecture

**Stack:** PostgreSQL + SQLAlchemy ORM

**Schema:**
```sql
-- Users & Authentication
users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    subscription_tier ENUM('free', 'pro', 'enterprise'),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Projects (workspace dla użytkownika)
projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR,
    description TEXT,
    world_id UUID,  -- Link to memory.worlds
    created_at TIMESTAMP
)

-- Generation Jobs (async task tracking)
generation_jobs (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    status ENUM('queued', 'running', 'completed', 'failed'),
    production_brief JSONB,  -- Store ProductionBrief
    output JSONB,            -- Store NarrativeOutput
    cost_usd DECIMAL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
)

-- Narratives (versioned output)
narratives (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES generation_jobs(id),
    project_id UUID REFERENCES projects(id),
    version INT,
    narrative_text TEXT,     -- Full generated text
    metadata JSONB,          -- Characters, structure, segments
    quality_metrics JSONB,   -- Coherence, logic, etc.
    created_at TIMESTAMP
)

-- Usage & Billing
usage_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES generation_jobs(id),
    tokens_used INT,
    cost_usd DECIMAL,
    created_at TIMESTAMP
)
```

### 2.2 REST API Design

**Framework:** FastAPI (async, auto-docs, type hints)

**Endpoints:**

```python
# Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

# Projects
GET    /api/v1/projects                    # List user projects
POST   /api/v1/projects                    # Create new project
GET    /api/v1/projects/{id}               # Get project details
PUT    /api/v1/projects/{id}               # Update project
DELETE /api/v1/projects/{id}               # Delete project

# Generation
POST   /api/v1/projects/{id}/generate      # Start generation job
GET    /api/v1/jobs/{job_id}               # Get job status
GET    /api/v1/jobs/{job_id}/output        # Get generated narrative
POST   /api/v1/jobs/{job_id}/cancel        # Cancel running job

# Narratives
GET    /api/v1/narratives                  # List narratives (filter by project)
GET    /api/v1/narratives/{id}             # Get specific narrative
GET    /api/v1/narratives/{id}/versions    # List all versions
POST   /api/v1/narratives/{id}/export      # Export to ePub/PDF/Docx

# Memory (World/Character Management)
GET    /api/v1/worlds                      # List worlds
POST   /api/v1/worlds                      # Create world
GET    /api/v1/worlds/{id}/characters      # List characters in world
POST   /api/v1/worlds/{id}/characters      # Create character

# Usage & Billing
GET    /api/v1/usage                       # Get usage stats
GET    /api/v1/usage/current-month         # Current month cost
GET    /api/v1/billing/invoices            # Invoice history
```

**Authentication:**
- JWT tokens (access + refresh)
- OAuth2 (Google, GitHub)
- API keys for programmatic access

### 2.3 Async Task Queue

**Stack:** Celery + Redis/RabbitMQ

**Why?**
- Generation takes 8-10 minutes (too long for HTTP request)
- Need job prioritization (Pro users first)
- Want horizontal scaling (multiple workers)

**Architecture:**
```
User → FastAPI → Celery Queue → Worker Pool → PostgreSQL
                                      ↓
                                 Orchestrator
                                 (generate narrative)
```

**Task Types:**
```python
@celery_app.task(bind=True)
async def generate_narrative_task(self, job_id: str, brief: dict):
    """
    Main generation task.
    - Updates job status in DB
    - Sends progress webhooks
    - Handles errors gracefully
    """
    job = await db.get_job(job_id)
    await db.update_job(job_id, status='running')

    try:
        output = await orchestrator.produce_narrative(brief)
        await db.update_job(job_id, status='completed', output=output)
        await send_webhook(job.user_id, 'job_completed', job_id)
    except Exception as e:
        await db.update_job(job_id, status='failed', error=str(e))
        await send_webhook(job.user_id, 'job_failed', job_id)
```

### 2.4 WebSockets for Real-time Progress

**Use Case:** Show live progress to user

```python
# FastAPI WebSocket endpoint
@app.websocket("/ws/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()

    async for progress in orchestrator.stream_progress(job_id):
        await websocket.send_json({
            "stage": progress.stage.value,
            "percent": progress.percent,
            "message": progress.message,
            "cost_so_far": progress.cost_usd
        })
```

---

## FAZA 3: FRONTEND & UI/UX (8-10 tygodni)

**Priorytet:** WYSOKI
**Cel:** Modern web application dla twórców

### 3.1 Technology Stack

**Framework:** Next.js 14 (App Router)

**Why Next.js?**
- Server-Side Rendering (SSR) for SEO
- API routes (можemy połączyć z FastAPI backend)
- Great developer experience
- Built-in optimizations

**UI Library:** shadcn/ui + TailwindCSS

**Why shadcn?**
- Accessible components (Radix UI)
- Beautiful defaults
- Fully customizable
- No runtime overhead

**Additional Libraries:**
```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-query": "^5.0",        // Server state management
    "zustand": "^4.0",            // Client state management
    "zod": "^3.0",                // Form validation
    "react-hook-form": "^7.0",    // Forms
    "recharts": "^2.0",           // Charts (usage dashboard)
    "framer-motion": "^11.0",     // Animations
    "socket.io-client": "^4.0"    // WebSocket (real-time progress)
  }
}
```

### 3.2 Core Pages & Features

**1. Landing Page** (`/`)
- Hero section with demo video
- Key features showcase
- Pricing tiers
- Testimonials
- CTA buttons (Sign Up / Try Demo)

**2. Dashboard** (`/dashboard`)
```
┌─────────────────────────────────────────────────────┐
│  Recent Projects                   Usage This Month  │
│  ┌─────────────┐ ┌─────────────┐   ┌──────────────┐│
│  │ Fantasy     │ │ Sci-Fi      │   │ $12.50 / $50 ││
│  │ World       │ │ Adventure   │   │              ││
│  │ 3 stories   │ │ 1 novel     │   │ ████░░░░░░   ││
│  └─────────────┘ └─────────────┘   └──────────────┘│
│                                                       │
│  Quick Actions                                        │
│  [+ New Story]  [+ New Project]  [View All]          │
└─────────────────────────────────────────────────────┘
```

**3. Project View** (`/projects/{id}`)
```
┌─────────────────────────────────────────────────────┐
│  ← Back to Dashboard          Fantasy World Project  │
├─────────────────────────────────────────────────────┤
│  World: Eldoria    |    6 Characters    |    3 Stories│
├─────────────────────────────────────────────────────┤
│                                                       │
│  📚 Stories                                           │
│  ┌─────────────────────────────────────────────────┐│
│  │ The Last Alchemist          [View] [Edit] [...]  ││
│  │ Short Story • 7,245 words • Jan 15, 2026         ││
│  │ Quality: ████████░░ 0.88                          ││
│  └─────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────┐│
│  │ Shadow of the Past          [View] [Edit] [...]  ││
│  │ Novella • 23,891 words • Jan 10, 2026            ││
│  │ Quality: █████████░ 0.92                          ││
│  └─────────────────────────────────────────────────┘│
│                                                       │
│  [+ Generate New Story]                               │
└─────────────────────────────────────────────────────┘
```

**4. Story Generator** (`/projects/{id}/generate`)

**Step 1: Basic Info**
```
┌─────────────────────────────────────────────────────┐
│  Generate New Story                          Step 1/4│
├─────────────────────────────────────────────────────┤
│                                                       │
│  Story Type                                           │
│  ○ Short Story (5k-10k words)                         │
│  ● Novella (10k-40k words)                            │
│  ○ Novel (40k-120k words)                             │
│  ○ Epic Saga (120k+ words, multi-volume)              │
│                                                       │
│  Genre                                                │
│  [Fantasy ▼]                                          │
│                                                       │
│  Inspiration / Brief                                  │
│  ┌─────────────────────────────────────────────────┐│
│  │ Young alchemist discovers her master's dark      ││
│  │ secret about the price of immortality...         ││
│  │                                                   ││
│  └─────────────────────────────────────────────────┘│
│                                                       │
│                              [Cancel]  [Next Step →] │
└─────────────────────────────────────────────────────┘
```

**Step 2: World & Characters**
```
┌─────────────────────────────────────────────────────┐
│  Generate New Story                          Step 2/4│
├─────────────────────────────────────────────────────┤
│                                                       │
│  Use Existing World?                                  │
│  ● Create New World                                   │
│  ○ Use Existing: [Eldoria ▼]                          │
│                                                       │
│  Protagonist                                          │
│  ○ Create New Character                               │
│  ● Use Existing: [Lyra (Alchemist) ▼]                │
│                                                       │
│  Supporting Characters (optional)                     │
│  [+ Add Character]                                    │
│                                                       │
│                         [← Back]  [Cancel]  [Next →] │
└─────────────────────────────────────────────────────┘
```

**Step 3: Advanced Settings**
```
┌─────────────────────────────────────────────────────┐
│  Generate New Story                          Step 3/4│
├─────────────────────────────────────────────────────┤
│                                                       │
│  Narrative Structure                                  │
│  [Three-Act Structure ▼]                              │
│                                                       │
│  Tone & Style                                         │
│  Dark ◄═════●═════► Light                             │
│  Serious ◄══●══════► Humorous                         │
│  Slow ◄═══════●════► Fast-paced                       │
│                                                       │
│  Advanced Options                                     │
│  ☑ Enable bestseller-quality prompts                 │
│  ☑ Ultra-strict cliché detection                     │
│  ☐ Allow experimental features                       │
│                                                       │
│  Estimated Cost: ~$0.36 USD (Novella)                 │
│                                                       │
│                         [← Back]  [Cancel]  [Next →] │
└─────────────────────────────────────────────────────┘
```

**Step 4: Review & Generate**
```
┌─────────────────────────────────────────────────────┐
│  Generate New Story                          Step 4/4│
├─────────────────────────────────────────────────────┤
│                                                       │
│  Review Your Choices                                  │
│  ┌─────────────────────────────────────────────────┐│
│  │ Type: Novella (10k-40k words)                    ││
│  │ Genre: Fantasy                                   ││
│  │ World: Eldoria (existing)                        ││
│  │ Protagonist: Lyra (Alchemist)                    ││
│  │ Brief: "Young alchemist discovers..."           ││
│  │                                                   ││
│  │ Estimated Duration: ~20-30 minutes               ││
│  │ Estimated Cost: ~$0.36 USD                       ││
│  └─────────────────────────────────────────────────┘│
│                                                       │
│  ⚠️  This will consume tokens from your monthly quota │
│     (42,000 / 100,000 tokens used this month)        │
│                                                       │
│           [← Back]  [Cancel]  [🚀 Generate Story]    │
└─────────────────────────────────────────────────────┘
```

**5. Generation Progress** (`/jobs/{job_id}`)
```
┌─────────────────────────────────────────────────────┐
│  Generating: The Last Alchemist                       │
├─────────────────────────────────────────────────────┤
│                                                       │
│  Overall Progress                                     │
│  ████████████░░░░░░░░░░░░░░░░░░░  40% (Stage 4/10)   │
│                                                       │
│  Current Stage: Structure Designer                    │
│  Designing narrative structure and act breakdown...   │
│                                                       │
│  Pipeline Status                                      │
│  ✅ Brief Interpreter (completed in 12s)              │
│  ✅ World Architect (completed in 18s)                │
│  ✅ Character Architect (completed in 24s)            │
│  ⏳ Structure Designer (in progress, 8s elapsed)      │
│  ⏸️  Segment Planner                                  │
│  ⏸️  Sequential Generator (quality-critical, GPT-4o)  │
│  ⏸️  Coherence Validator                              │
│  ⏸️  Language Stylizer                                │
│  ⏸️  Editorial Reviewer                               │
│  ⏸️  Output Processor                                 │
│                                                       │
│  Cost So Far: $0.08 USD                               │
│  Estimated Time Remaining: ~18 minutes                │
│                                                       │
│                                     [Cancel Job]      │
└─────────────────────────────────────────────────────┘
```

**6. Narrative Viewer** (`/narratives/{id}`)
```
┌─────────────────────────────────────────────────────┐
│  The Last Alchemist                 [Export ▼] [...]│
├─────────────────────────────────────────────────────┤
│  ┌──────────┬──────────────────────────────────────┐│
│  │ Metadata │  Narrative Text                       ││
│  │          │                                       ││
│  │ 📊 Stats │  Chapter 1: The Discovery            ││
│  │ 7,245    │                                       ││
│  │ words    │  Lyra's fingers trembled as she      ││
│  │          │  opened the ancient grimoire. The    ││
│  │ 🎭 World │  leather binding felt warm against   ││
│  │ Eldoria  │  her skin, as if it contained a      ││
│  │          │  living heart...                     ││
│  │ 👤 Chars │                                       ││
│  │ • Lyra   │  [Full narrative text continues...]  ││
│  │ • Master │                                       ││
│  │   Theron │                                       ││
│  │          │                                       ││
│  │ 📈 Score │                                       ││
│  │ 0.88/1.0 │                                       ││
│  │          │                                       ││
│  │ 💰 Cost  │                                       ││
│  │ $0.36    │                                       ││
│  └──────────┴──────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**7. World Builder** (`/worlds/{id}`)
```
┌─────────────────────────────────────────────────────┐
│  Eldoria - Fantasy World                  [Edit] [...] │
├─────────────────────────────────────────────────────┤
│  ┌───────────────┬───────────────────────────────────┐│
│  │ Characters    │  Map & Locations                  ││
│  │               │                                   ││
│  │ 🧙 Lyra       │  ┌─────────────────────────────┐ ││
│  │ Alchemist     │  │                             │ ││
│  │ Age: 24       │  │   [Interactive World Map]   │ ││
│  │               │  │                             │ ││
│  │ 👴 Theron     │  │   📍 Alchemist's Tower      │ ││
│  │ Master        │  │   📍 Royal Library          │ ││
│  │ Age: ???      │  │   📍 Dark Forest            │ ││
│  │               │  │                             │ ││
│  │ [+ Add]       │  └─────────────────────────────┘ ││
│  │               │                                   ││
│  ├───────────────┤  Rules & Magic System            ││
│  │ Timeline      │  • Alchemy requires life essence  ││
│  │               │  • Immortality = forbidden art    ││
│  │ Year 1: The   │  • Every spell has a price        ││
│  │ Discovery     │                                   ││
│  │               │  [+ Add Rule]                     ││
│  └───────────────┴───────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**8. Usage Dashboard** (`/usage`)
```
┌─────────────────────────────────────────────────────┐
│  Usage & Billing                                      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  Current Month (January 2026)                         │
│  $12.50 / $50.00 (Pro Plan)                           │
│  ████████████░░░░░░░░░░░░░░░░░░░ 25%                  │
│                                                       │
│  ┌──────────────────────────────────────────────────┐│
│  │              Cost Over Time                       ││
│  │  $15 ┤                                            ││
│  │  $10 ┤     ╭─╮                                    ││
│  │   $5 ┤  ╭──╯ ╰─╮                                  ││
│  │   $0 ┴──┴───────┴───────────────                  ││
│  │       Jan  Feb  Mar  Apr  May  Jun               ││
│  └──────────────────────────────────────────────────┘│
│                                                       │
│  Recent Jobs                                          │
│  ┌─────────────────────────────────────────────────┐│
│  │ Jan 15 • Short Story • $0.36 • completed         ││
│  │ Jan 14 • Novella • $1.42 • completed             ││
│  │ Jan 12 • Short Story • $0.38 • completed         ││
│  └─────────────────────────────────────────────────┘│
│                                                       │
│  [Upgrade Plan]  [View Invoices]                      │
└─────────────────────────────────────────────────────┘
```

### 3.3 Design System

**Colors (Dark Mode Primary):**
```css
:root {
  --background: 222.2 84% 4.9%;      /* Deep dark */
  --foreground: 210 40% 98%;         /* Near white */
  --primary: 217.2 91.2% 59.8%;      /* Electric blue */
  --secondary: 217.2 32.6% 17.5%;    /* Dark blue-gray */
  --accent: 280 100% 70%;            /* Purple accent */
  --destructive: 0 84.2% 60.2%;      /* Red */
  --success: 142.1 76.2% 36.3%;      /* Green */
}
```

**Typography:**
```css
font-family: 'Inter', system-ui, sans-serif;

/* Headings */
h1: 32px / 600 / -0.02em
h2: 24px / 600 / -0.01em
h3: 20px / 600 / -0.01em

/* Body */
body: 16px / 400 / 0
small: 14px / 400 / 0
```

**Animations:**
- Smooth page transitions (Framer Motion)
- Skeleton loaders during data fetch
- Progress bars with spring physics
- Micro-interactions on buttons (hover, active states)

### 3.4 Mobile Responsiveness

**Breakpoints:**
```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

**Mobile-First Approach:**
- Responsive grid layouts
- Touch-optimized buttons (min 44px)
- Collapsible sidebars
- Bottom navigation for mobile

---

## FAZA 4: ULEPSZENIA FUNKCJONALNE (6-8 tygodni)

**Priorytet:** ŚREDNI
**Cel:** Advanced features dla power users

### 4.1 Advanced Generation Features

**1. Iterative Refinement**
```python
# User can regenerate specific segments
POST /api/v1/narratives/{id}/regenerate
{
  "segment_index": 3,           # Chapter 3
  "feedback": "Make it darker",
  "preserve_continuity": true
}
```

**2. Style Transfer**
```python
# Generate in style of specific author
POST /api/v1/projects/{id}/generate
{
  "style_reference": "haruki_murakami",
  "style_strength": 0.7  # 0.0-1.0
}
```

**3. Multi-POV (Point of View)**
```python
# Generate same scene from different character perspectives
{
  "scene": "The confrontation",
  "povs": ["lyra", "theron", "narrator_omniscient"]
}
```

**4. Plot Branching**
```
                    ┌─ Branch A: Hero wins
Chapter 5 Decision ├─ Branch B: Hero loses
                    └─ Branch C: Stalemate
```

### 4.2 Collaborative Features

**1. Team Workspaces**
- Multi-user projects
- Role-based access (Owner, Editor, Viewer)
- Comment threads on narratives
- Version history with diffs

**2. Shared Worlds**
- Multiple authors in same universe
- Consistent lore enforcement
- Cross-narrative character tracking

**3. Editorial Workflow**
```
Draft → Review → Revise → Approve → Publish
```

### 4.3 Export & Integration

**Export Formats:**
- ✅ Plain Text (.txt)
- 📄 Microsoft Word (.docx) - with formatting
- 📕 ePub - for e-readers
- 📘 PDF - publication-ready
- 🌐 HTML - for web publishing

**Integration APIs:**
- Wattpad auto-publish
- Medium auto-post
- WordPress plugin
- Notion import

### 4.4 AI-Assisted Editing

**Tools:**

**1. Suggestion Engine**
```python
# Analyze narrative and suggest improvements
POST /api/v1/narratives/{id}/analyze
Response:
{
  "suggestions": [
    {
      "type": "pacing",
      "location": "chapter_2",
      "message": "Chapter 2 feels rushed. Consider expanding the emotional aftermath."
    },
    {
      "type": "character",
      "location": "chapter_5",
      "message": "Lyra's motivation shift seems abrupt. Add foreshadowing in Chapter 3."
    }
  ]
}
```

**2. Cliché Detector (Enhanced)**
- Real-time highlighting in editor
- Suggest alternatives
- Learn from user preferences

**3. Consistency Checker**
- Character name spelling
- Timeline conflicts
- Physical impossibilities
- Continuity errors

---

## FAZA 5: SKALOWANIE & OPTYMALIZACJA (4-6 tygodni)

**Priorytet:** ŚREDNI
**Cel:** Handle 1000+ concurrent users

### 5.1 Infrastructure

**Cloud Provider:** AWS / GCP / Azure

**Architecture:**
```
                    ┌─────────────┐
Users ───────────► │   Cloudflare │
                    │   CDN + WAF  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Load Balancer│
                    │  (ALB/Nginx)  │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  FastAPI  │   │  FastAPI  │   │  FastAPI  │
    │  Instance │   │  Instance │   │  Instance │
    │     #1    │   │     #2    │   │     #3    │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼───────┐
                    │   PostgreSQL │
                    │  (RDS/Cloud  │
                    │     SQL)     │
                    └──────────────┘

                    ┌──────────────┐
                    │  Redis Cache │
                    │ (ElastiCache)│
                    └──────────────┘

                    ┌──────────────┐
                    │Celery Workers│
                    │  (ECS/K8s)   │
                    └──────────────┘
```

**Containerization:**
```yaml
# docker-compose.production.yml
services:
  api:
    image: narra-forge-api:latest
    replicas: 3
    resources:
      limits:
        cpus: '2.0'
        memory: 4G

  worker:
    image: narra-forge-worker:latest
    replicas: 10  # Scale for generation workload
    resources:
      limits:
        cpus: '4.0'
        memory: 8G

  postgres:
    image: postgres:16
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
```

### 5.2 Caching Strategy

**Multi-Level Caching:**

**1. Application-Level Cache (Redis)**
```python
@cache(ttl=3600)  # 1 hour
async def get_user_projects(user_id: str):
    return await db.query(projects).where(user_id=user_id)

@cache(ttl=86400)  # 24 hours
async def get_world(world_id: str):
    return await db.query(worlds).where(id=world_id)
```

**2. CDN Caching (Cloudflare)**
- Static assets (JS, CSS, images)
- Generated narratives (immutable once completed)
- Cache-Control headers

**3. Database Query Caching**
- PostgreSQL query result cache
- Materialized views for analytics

### 5.3 Cost Optimization

**Current Challenge:** GPT-4o is expensive (~$15/1M input tokens)

**Strategies:**

**1. Prompt Caching (OpenAI Feature)**
```python
# Cache system prompts (50% discount on cached tokens)
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": LONG_SYSTEM_PROMPT,  # Will be cached
            "cache_control": {"type": "ephemeral"}
        },
        {"role": "user", "content": user_input}
    ]
)
```

**2. Smart Model Routing**
```python
# Use gpt-4o-mini where quality difference is negligible
MINI_STAGES = {
    "brief_interpretation",    # Analysis task
    "world_architecture",      # Creative but structured
    "character_architecture",  # Creative but structured
    "structure_design",        # Template-based
    "segment_planning",        # Organizational
    "output_processing"        # Formatting only
}

GPT4_STAGES = {
    "sequential_generation",   # QUALITY-CRITICAL
    "coherence_validation",    # Complex analysis
}
```

**3. Batch Processing**
```python
# Generate multiple segments in parallel
async def generate_chapters_parallel(chapters: list[Chapter]):
    tasks = [generate_chapter(ch) for ch in chapters]
    return await asyncio.gather(*tasks)
```

**4. Usage-Based Pricing**
```
Free Tier:     5 short stories/month  ($0.36 × 5 = $1.80)
Pro Tier:      50 stories/month       ($0.36 × 50 = $18)
Enterprise:    Unlimited              (Volume pricing)
```

### 5.4 Performance Benchmarks

**Target SLAs:**

| Metric | Target | Critical Threshold |
|--------|--------|--------------------|
| API Response Time (p95) | <200ms | <500ms |
| Job Queue Latency | <30s | <2min |
| Short Story Generation | <10min | <15min |
| Novella Generation | <30min | <45min |
| Database Query Time (p95) | <50ms | <100ms |
| Page Load Time (FCP) | <1.5s | <3s |
| Uptime | 99.9% | 99.5% |

---

## FAZA 6: MONETYZACJA & GROWTH (Ciągły proces)

**Priorytet:** ŚREDNI
**Cel:** Sustainable business model

### 6.1 Pricing Tiers

**Free Tier** ($0/month)
- 5 short stories/month
- 1 project
- Basic world builder
- Export to .txt only
- Community support

**Pro Tier** ($29/month)
- 50 stories/month OR 10 novellas OR 2 novels
- Unlimited projects
- Advanced world builder
- All export formats
- Priority generation queue
- Email support
- API access (100 requests/day)

**Enterprise Tier** (Custom pricing)
- Unlimited generation
- Dedicated infrastructure
- Custom model fine-tuning
- White-label option
- SLA guarantee (99.9%)
- Dedicated support
- Unlimited API access

### 6.2 Additional Revenue Streams

**1. Marketplace**
- Premium prompts ($5-20)
- Pre-built worlds ($10-50)
- Character archetypes ($5-15)
- Story templates ($15-40)

**2. Publishing Services**
- Professional editing ($0.02/word)
- Cover design ($200-500)
- ISBN registration ($50)
- Distribution (Amazon KDP, IngramSpark) - commission

**3. API Usage Pricing**
```
- $0.50 per short story via API
- $2.00 per novella via API
- $8.00 per novel via API
- Bulk discounts available
```

### 6.3 Growth Strategies

**1. Content Marketing**
- Blog: "How to write compelling narratives"
- YouTube: Platform tutorials + writing tips
- Podcast: Interviews with successful users
- Case studies: "How Author X generated their bestseller"

**2. Community Building**
- Discord server for users
- Monthly writing challenges
- User showcase (best narratives)
- Beta tester program

**3. Partnerships**
- Writing courses (integrate NARRA_FORGE as tool)
- Publishing houses (white-label for in-house use)
- Writing software (Scrivener, Notion) integrations

**4. Referral Program**
```
Refer a friend:
- They get 2 free story credits
- You get 2 free story credits
- If they upgrade to Pro: you get 1 month free
```

### 6.4 Analytics & Metrics

**Key Metrics to Track:**

**Acquisition:**
- Signups per day/week/month
- Conversion rate (visitor → signup)
- Traffic sources (organic, paid, referral)

**Activation:**
- % of users who generate first story
- Time to first story (TTV - Time To Value)
- Onboarding completion rate

**Retention:**
- DAU/MAU ratio (Daily/Monthly Active Users)
- Churn rate (monthly)
- Cohort retention curves

**Revenue:**
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- LTV/CAC ratio (Lifetime Value / Customer Acquisition Cost)

**Product:**
- Stories generated per user
- Average quality score
- Feature adoption rates
- API usage growth

---

## 📋 PRIORYTYZACJA - CO NAJPIERW?

### ⚡ CRITICAL PATH (0-3 miesiące)

**Mileston 1: Stable Foundation** (Miesiąc 1)
- ✅ Comprehensive test suite (>80% coverage)
- ✅ Error recovery & checkpointing
- ✅ Monitoring & observability (Prometheus + Grafana)
- ✅ Long-form testing (novels, sagas)

**Milestone 2: API & Database** (Miesiąc 2)
- ✅ PostgreSQL schema & migrations
- ✅ FastAPI REST endpoints
- ✅ JWT authentication
- ✅ Celery task queue
- ✅ Basic usage tracking

**Milestone 3: MVP Frontend** (Miesiąc 3)
- ✅ Next.js project setup
- ✅ Dashboard + Project list
- ✅ Story generator wizard (4-step)
- ✅ Job progress viewer (WebSocket)
- ✅ Narrative viewer
- ✅ Basic world builder

**MVP Launch Criteria:**
- Users can sign up, create projects, generate stories
- Real-time progress tracking
- Quality score >0.85 consistently
- Uptime >99%
- Cost tracking functional

---

### 🚀 NEXT STEPS (3-6 miesięcy)

**Milestone 4: Advanced Features**
- Iterative refinement
- Export to ePub/PDF/Docx
- Collaborative features (comments, sharing)
- Usage dashboard

**Milestone 5: Optimization**
- Prompt caching
- CDN setup
- Database query optimization
- Cost per narrative <$0.30

**Milestone 6: Scale Testing**
- Load testing (1000 concurrent users)
- Kubernetes deployment
- Auto-scaling configuration

---

### 🌟 FUTURE (6+ miesięcy)

- Style transfer
- Multi-POV generation
- Marketplace launch
- Mobile apps (iOS, Android)
- Enterprise features (SSO, audit logs)
- Custom model fine-tuning

---

## 🛠️ STACK TECHNOLOGICZNY - PODSUMOWANIE

### Backend
```
Language:      Python 3.11+
Framework:     FastAPI
Database:      PostgreSQL 16 + SQLAlchemy ORM
Cache:         Redis 7
Queue:         Celery + RabbitMQ
AI Provider:   OpenAI API (GPT-4o, gpt-4o-mini)
Testing:       pytest + pytest-asyncio
Monitoring:    Prometheus + Grafana + Sentry
```

### Frontend
```
Framework:     Next.js 14 (App Router)
Language:      TypeScript
UI Library:    shadcn/ui + TailwindCSS
State:         React Query + Zustand
Forms:         React Hook Form + Zod
Charts:        Recharts
Animations:    Framer Motion
Real-time:     Socket.IO
```

### Infrastructure
```
Hosting:       AWS / GCP / Vercel (frontend)
Containers:    Docker + Docker Compose
Orchestration: Kubernetes (production)
CDN:           Cloudflare
CI/CD:         GitHub Actions
```

### DevOps
```
IaC:           Terraform
Logging:       structlog + CloudWatch
Tracing:       OpenTelemetry
Secrets:       AWS Secrets Manager / Vault
```

---

## 📊 SZACOWANE KOSZTY ROZWOJU

### Zespół (opcjonalnie - można solo, ale wolniej)
```
Backend Developer:      $60-80/hour × 320h = $19,200-25,600
Frontend Developer:     $60-80/hour × 320h = $19,200-25,600
DevOps Engineer:        $80-100/hour × 160h = $12,800-16,000
UI/UX Designer:         $50-70/hour × 80h = $4,000-5,600

Total Team Cost (6 miesięcy): ~$55,000-$73,000
```

### Infrastruktura (miesięcznie)
```
Development Environment:
- AWS EC2 (t3.medium × 2):     $60
- PostgreSQL RDS (db.t3.small): $35
- Redis ElastiCache:            $15
- S3 Storage:                   $5
Total Dev: ~$115/month

Production (MVP - 100 users):
- AWS EC2 (t3.large × 3):      $300
- PostgreSQL RDS (db.t3.medium): $90
- Redis ElastiCache:            $30
- Load Balancer:                $20
- Cloudflare Pro:               $20
- OpenAI API (~500 stories/mo): $180
- Monitoring (Grafana Cloud):   $50
Total Prod: ~$690/month

Production (Growth - 1000 users):
- AWS ECS/EKS cluster:          $800
- PostgreSQL RDS (db.r5.large): $400
- Redis (cache.r5.large):       $150
- CDN + bandwidth:              $200
- OpenAI API (~5000 stories/mo): $1,800
- Monitoring & logging:         $150
Total Growth: ~$3,500/month
```

### Software Licenses
```
- OpenAI API credits:           $100-500/month (varies)
- Sentry (error tracking):      $0-26/month
- Grafana Cloud:                $0-50/month
- GitHub Team:                  $4/user/month
Total: ~$100-600/month
```

---

## 🎯 KLUCZOWE WSKAŹNIKI SUKCESU (KPIs)

### Technical KPIs
- ✅ Test coverage >80%
- ✅ API response time <200ms (p95)
- ✅ Generation quality score >0.85
- ✅ Uptime >99.9%
- ✅ Cost per story <$0.40

### Product KPIs
- 🎯 1,000 registered users (Month 6)
- 🎯 100 paying customers (Month 6)
- 🎯 10,000 stories generated (Month 6)
- 🎯 50% user retention (30-day)

### Business KPIs
- 🎯 $3,000 MRR (Month 6)
- 🎯 LTV/CAC ratio >3:1
- 🎯 Net Promoter Score (NPS) >50
- 🎯 Break-even by Month 12

---

## ⚠️ RYZYKA & MITYGACJA

### Ryzyko #1: Koszty OpenAI API
**Problem:** GPT-4o może stać się droższy lub hit rate limit
**Mitygacja:**
- Implement prompt caching (50% savings)
- Explore alternative models (Claude, Gemini)
- Negotiate enterprise pricing with OpenAI
- Build cost prediction + alerts

### Ryzyko #2: Jakość generacji
**Problem:** Quality might degrade over time (model updates)
**Mitygacja:**
- Pin specific model versions in production
- Continuous quality monitoring
- A/B test prompt changes
- Maintain validation test suite

### Ryzyko #3: Konkurencja
**Problem:** Large players (Sudowrite, NovelAI) już istnieją
**Mitygacja:**
- Focus on Polish language (niche)
- Superior quality (bestseller-grade)
- Better UX (simpler workflow)
- Unique features (triple memory system)

### Ryzyko #4: Skalowanie
**Problem:** Infrastructure costs scale faster than revenue
**Mitygacja:**
- Usage-based pricing covers API costs
- Aggressive caching strategy
- Efficient batch processing
- Gradual scaling (don't over-provision)

### Ryzyko #5: Prawne (Copyright)
**Problem:** Generated text might infringe copyright
**Mitygacja:**
- Clear ToS: users own generated content
- Plagiarism detection integration
- OpenAI's usage policies compliance
- Legal review before launch

---

## 📚 WYMAGANA DOKUMENTACJA

### Dla Developerów
- ✅ ARCHITECTURE_V2.md (już istnieje)
- ⏳ API_REFERENCE.md (Swagger/OpenAPI)
- ⏳ DEPLOYMENT_GUIDE.md
- ⏳ CONTRIBUTING.md
- ⏳ TESTING_GUIDE.md

### Dla Użytkowników
- ⏳ USER_GUIDE.md (jak używać platformy)
- ⏳ FAQ.md
- ⏳ VIDEO_TUTORIALS (screencasty)
- ⏳ CHANGELOG.md (release notes)

### Business
- ⏳ PRIVACY_POLICY.md
- ⏳ TERMS_OF_SERVICE.md
- ⏳ PRICING_EXPLAINED.md

---

## 🚀 QUICK START - NASTĘPNE KROKI

### Krok 1: Faza Stabilizacji (start teraz)
```bash
# 1. Setup test environment
pytest --cov=narra_forge tests/

# 2. Write missing tests
# Target: >80% coverage

# 3. Setup monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# 4. Long-form testing
python examples/test_long_form.py
```

### Krok 2: Database Setup (tydzień 2)
```bash
# 1. Install PostgreSQL
docker run -d -p 5432:5432 postgres:16

# 2. Create schema
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head

# 3. Test CRUD operations
pytest tests/integration/test_database.py
```

### Krok 3: API Development (tydzień 3-6)
```bash
# 1. FastAPI project structure
mkdir -p api/{routes,models,services}

# 2. Implement endpoints
# Start with /auth and /projects

# 3. Test with Postman/Insomnia
curl -X POST http://localhost:8000/api/v1/auth/register
```

### Krok 4: Frontend Setup (tydzień 7-12)
```bash
# 1. Create Next.js project
npx create-next-app@latest narra-forge-web --typescript --tailwind --app

# 2. Install shadcn/ui
npx shadcn-ui@latest init

# 3. Build Dashboard page
npm run dev
```

---

## 💡 KOŃCOWE PRZEMYŚLENIA

NARRA_FORGE V2 ma solidny fundament. Obecny generator działa i generuje jakościowe treści. Plan rozwoju zakłada ewolucję od CLI tool do pełnej platformy SaaS.

**Kluczowe czynniki sukcesu:**
1. ✅ **Jakość przede wszystkim** - utrzymać 0.85+ coherence score
2. 🎯 **Szybki MVP** - launch za 3 miesiące z podstawowymi features
3. 💰 **Cost management** - aggressive caching + smart model routing
4. 👥 **User feedback** - iterować na podstawie prawdziwych user stories
5. 📈 **Gradual scaling** - nie over-engineer, scale when needed

**Największe wyzwanie:** Balance między quality (GPT-4o) a cost (cena API).

**Największa szansa:** Polski rynek jest niedosytuowany. Zagraniczni gracze (Sudowrite, NovelAI) słabo działają w języku polskim.

Powodzenia! 🚀
