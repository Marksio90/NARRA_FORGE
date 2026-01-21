# AI Multi-Agent System Setup

NarraForge now uses a **professional multi-agent AI system** for world-class book generation!

## 🤖 What We Use

### AI Models
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4, o1
- **Anthropic Claude**: Opus 4.5, Sonnet 4.5

### Agents
1. **World Builder Agent** - Creates rich, consistent fictional worlds
2. **Character Creator Agent** - Generates psychologically deep characters
3. **Plot Architect Agent** - Designs compelling story structures
4. **Prose Writer Agent** - Writes publication-quality prose
5. **Quality Control Agent** - Professional editorial validation

## 📋 Requirements

### API Keys Needed

You need at least ONE of these:
- **OpenAI API Key** (required for most features)
- **Anthropic API Key** (optional but recommended for best quality)

Get them here:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

### Cost Estimates

For a ~90,000 word novel (25 chapters):

**Using GPT-4o (Tier 2) + GPT-4o-mini (Tier 1)**:
- Estimated cost: **$15-30 per book**
- Generation time: 2-4 hours

**Using Claude Sonnet 4.5 (Tier 2) + GPT-4o-mini (Tier 1)**:
- Estimated cost: **$20-40 per book**
- Generation time: 2-4 hours
- Higher quality prose

**Using Claude Opus 4.5 (Tier 3) for climax**:
- Add **$5-10** for critical chapters
- Best quality for turning points

### Breakdown:
- World Building: $0.50-1.00
- Character Creation (5 chars): $1.00-2.00
- Plot Structure: $1.00-2.00
- Prose Generation (25 chapters): $10-25
- Quality Control: $2.00-5.00

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `openai==1.54.0` - Latest OpenAI SDK
- `anthropic==0.39.0` - Latest Anthropic SDK
- `tiktoken==0.8.0` - Token counting

### 2. Configure API Keys

#### Option A: Environment Variables (Recommended)

Create or update `.env` file:

```bash
# OpenAI (Required)
OPENAI_API_KEY=sk-proj-...your-key-here

# Anthropic (Optional but recommended)
ANTHROPIC_API_KEY=sk-ant-...your-key-here

# Other settings
DEFAULT_MODEL_TIER=2  # 1=cheap, 2=balanced, 3=premium
MAX_COST_PER_PROJECT=100.0
COST_ALERT_THRESHOLD=0.8
```

#### Option B: Docker Environment

Update `docker-compose.yml`:

```yaml
services:
  narraforge-backend:
    environment:
      - OPENAI_API_KEY=sk-proj-...your-key-here
      - ANTHROPIC_API_KEY=sk-ant-...your-key-here
```

### 3. Verify Setup

Test AI service:

```python
from app.services.ai_service import get_ai_service

ai = get_ai_service()
print("✅ AI Service initialized successfully!")
print(f"OpenAI: {'✅ Connected' if ai.openai_client else '❌ Not configured'}")
print(f"Anthropic: {'✅ Connected' if ai.anthropic_client else '❌ Not configured'}")
```

### 4. Test Generation

```python
from app.agents import WorldBuilderAgent

agent = WorldBuilderAgent()
result = await agent.create_world_bible(
    genre="sci-fi",
    project_name="Test Project",
    title_analysis={},
    target_word_count=90000,
    style_complexity="medium"
)

print("✅ World Bible generated!")
print(f"World type: {result['geography']['world_type']}")
```

## ⚙️ Configuration

### Model Tier System

The system automatically selects models based on task importance:

**Tier 1** (Fast & Cheap - GPT-4o-mini):
- Simple tasks (initialization, formatting, summaries)
- Cost: ~$0.15 per 1M input tokens
- Best for: Supporting character creation, simple validation

**Tier 2** (Balanced - GPT-4o, Claude Sonnet):
- Main generation (world, characters, plot, most chapters)
- Cost: ~$2.50 per 1M input tokens
- Best for: Primary content creation

**Tier 3** (Premium - GPT-4, Claude Opus, o1):
- Critical scenes (climax, major turning points)
- Cost: ~$30 per 1M input tokens
- Best for: Pivotal chapters requiring highest quality

### Customize Tier Selection

Edit `backend/app/config.py`:

```python
class ModelTierConfig:
    TIER_1_TASKS = [
        "initialization",
        "validation",
        "formatting",
        # Add more...
    ]

    TIER_2_TASKS = [
        "world_building",
        "character_creation",
        "plot_structure",
        "prose_writing",
        # Add more...
    ]

    TIER_3_TASKS = [
        "climax_scene",
        "complex_resolution",
        # Add more...
    ]
```

### Provider Preference

By default:
- **Creative tasks** → Claude (world building, characters, prose)
- **Structured tasks** → GPT (validation, formatting, analysis)

Override in agent calls:

```python
# Prefer Claude
response = await ai_service.generate(
    prompt=prompt,
    prefer_anthropic=True  # Force Claude if available
)

# Force GPT
response = await ai_service.generate(
    prompt=prompt,
    prefer_anthropic=False  # Force OpenAI
)
```

## 💰 Cost Management

### Real-Time Tracking

Every generation tracks:
- Tokens used (input + output)
- Cost per API call
- Total project cost
- API call count

View in logs:
```
📊 Progress: Step 3/15 (20.0%) - Generowanie World Bible (AI) [Cost: $1.25]
```

### Cost Limits

Set limits in `.env`:

```bash
MAX_COST_PER_PROJECT=100.0  # Stop if project exceeds $100
COST_ALERT_THRESHOLD=0.8    # Warn at 80% of max
```

### Cost Optimization Tips

1. **Use Tier 1 for simple tasks**: Summaries, formatting
2. **Reserve Tier 3 for critical moments**: Climax, major reveals
3. **Batch operations**: Generate multiple chapters in one session
4. **Monitor prompts**: Shorter prompts = lower cost
5. **Use caching**: Repeated context can be cached

## 🐛 Troubleshooting

### "OpenAI API Key not found"

```bash
# Check environment
echo $OPENAI_API_KEY

# Set temporarily
export OPENAI_API_KEY=sk-proj-...

# Or add to .env
echo "OPENAI_API_KEY=sk-proj-..." >> backend/.env
```

### "Rate limit exceeded"

OpenAI/Anthropic have rate limits:
- **Tier 1** (free): Very limited
- **Tier 2** ($5 spent): Higher limits
- **Tier 3** ($50 spent): Production limits

Solutions:
- Add payment method
- Increase tier
- Add retry logic (already implemented!)

### "Model not found"

Update model names in `config.py`:

```python
GPT_4O_MINI = "gpt-4o-mini"  # Check OpenAI docs for current names
GPT_4O = "gpt-4o"
GPT_4 = "gpt-4"
```

### High costs?

1. Check `ai_service` metrics:
   ```python
   metrics = ai_service.get_metrics()
   print(f"Total cost: ${metrics.total_cost:.2f}")
   print(f"API calls: {metrics.calls_made}")
   ```

2. Review tier assignments in agents
3. Reduce chapter count for testing
4. Use GPT-4o-mini for development

## 📊 Monitoring

### View Generation Stats

After generation completes:

```json
{
  "ai_metrics": {
    "total_cost": 25.50,
    "total_tokens": 500000,
    "api_calls": 45,
    "errors": 0
  },
  "statistics": {
    "chapters": 25,
    "characters": 5,
    "total_words": 92000
  },
  "quality_scores": {
    "average_chapter_quality": 87.5
  }
}
```

### Logs

Check logs for detailed AI activity:

```bash
# Docker
docker-compose logs -f narraforge-backend

# Look for:
# 🌍 World Builder Agent: Creating world...
# ✅ World created (cost: $1.25, tokens: 8500)
# 👥 Character Creator Agent: Creating 5 characters...
```

## 🚀 Production Deployment

### Best Practices

1. **Always use environment variables** for API keys
2. **Set cost limits** per project
3. **Monitor usage** via OpenAI/Anthropic dashboards
4. **Cache where possible** (world bible, characters)
5. **Use Tier 2 as default** (best balance)
6. **Reserve Tier 3 for premium features** (user pays more)
7. **Implement user quotas** (X books per month)

### Security

```bash
# Never commit API keys!
echo ".env" >> .gitignore

# Use secrets management in production
# AWS Secrets Manager, Azure Key Vault, etc.
```

### Scaling

For high volume:
1. Use **OpenAI Batch API** (50% discount, 24h turnaround)
2. Implement **request queuing**
3. Add **caching layer** (Redis)
4. Use **multiple API keys** (load balancing)
5. Consider **fine-tuned models** (lower cost)

## 📚 Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic API Docs](https://docs.anthropic.com)
- [OpenAI Pricing](https://openai.com/pricing)
- [Anthropic Pricing](https://anthropic.com/pricing)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)

## 🎯 Quick Start Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Get OpenAI API key
- [ ] (Optional) Get Anthropic API key
- [ ] Set `OPENAI_API_KEY` in `.env`
- [ ] (Optional) Set `ANTHROPIC_API_KEY` in `.env`
- [ ] Test with: `python -c "from app.services.ai_service import get_ai_service; get_ai_service()"`
- [ ] Create a test project
- [ ] Run simulation
- [ ] Start generation
- [ ] Monitor costs in logs
- [ ] Enjoy your AI-generated book! 🎉

---

**Questions?** Check the agent source code in `backend/app/agents/` for detailed prompts and techniques!
