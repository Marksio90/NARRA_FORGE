# NARRA_FORGE - Docker Guide

Quick guide for running NARRA_FORGE in Docker.

---

## 🚀 Quick Start

```bash
# 1. Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Build image
docker-compose build

# 3. Run example
docker-compose run --rm narra_forge python example_basic.py

# Or run a specific example
docker-compose run --rm narra_forge python examples/example_short_story.py
```

---

## 📦 Available Commands

### Run Examples

```bash
# Basic example
docker-compose run --rm narra_forge python example_basic.py

# Short story
docker-compose run --rm narra_forge python examples/example_short_story.py

# Novella (sci-fi)
docker-compose run --rm narra_forge python examples/example_novella_scifi.py

# Programmatic API
docker-compose run --rm narra_forge python examples/example_programmatic_api.py
```

### Run CLI

```bash
# Interactive mode
docker-compose run --rm narra_forge narra-forge

# Direct mode
docker-compose run --rm narra_forge narra-forge \
  --type short_story \
  --genre fantasy \
  --inspiration "Your inspiration here"

# List jobs
docker-compose run --rm narra_forge narra-forge --list-jobs
```

### Run Tests

```bash
# Run all tests
docker-compose --profile test run --rm narra_forge_test

# Or use the test script
./docker-test.sh
```

### Python REPL

```bash
# Interactive Python shell
docker-compose run --rm narra_forge python
```

---

## 📁 Volumes

Docker compose automatically mounts:

- `./data` → `/app/data` - Database (persistent)
- `./output` → `/app/output` - Generated narratives
- `./logs` → `/app/logs` - Log files

Generated files will appear in your local directories.

---

## 🔧 Configuration

Edit `.env` to configure:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional
ENVIRONMENT=production
DEFAULT_MINI_MODEL=gpt-4o-mini
DEFAULT_GPT4_MODEL=gpt-4o
MAX_COST_PER_JOB=10.0
MIN_COHERENCE_SCORE=0.85
LOG_LEVEL=INFO
```

---

## 🐳 Docker Compose Services

### narra_forge (main)

Production service for running narratives.

```bash
docker-compose up narra_forge
docker-compose run --rm narra_forge <command>
```

### narra_forge_test

Testing service (uses `--profile test`).

```bash
docker-compose --profile test run --rm narra_forge_test
```

---

## 💡 Tips

### Custom Configuration

Create a custom `.env` file:

```bash
cp .env.example .env.custom
# Edit .env.custom
docker-compose --env-file .env.custom run --rm narra_forge python example_basic.py
```

### Check Container Health

```bash
docker-compose ps
docker-compose exec narra_forge python -c "import narra_forge; print('OK')"
```

### View Logs

```bash
# Container logs
docker-compose logs narra_forge

# Follow logs
docker-compose logs -f narra_forge
```

### Clean Up

```bash
# Remove containers
docker-compose down

# Remove containers + volumes
docker-compose down -v

# Remove image
docker rmi narra_forge:2.0.0
```

---

## 🔍 Troubleshooting

### "No such file or directory"

**Problem:** Can't find example files

**Solution:** Rebuild image to include new files

```bash
docker-compose build --no-cache
```

### "OPENAI_API_KEY not set"

**Problem:** Missing API key

**Solution:** Check `.env` file

```bash
cat .env | grep OPENAI_API_KEY
# Should show: OPENAI_API_KEY=sk-...
```

### "Permission denied"

**Problem:** Can't write to mounted volumes

**Solution:** Fix permissions

```bash
sudo chown -R $USER:$USER data/ output/ logs/
```

### "Out of memory"

**Problem:** Container runs out of memory

**Solution:** Increase Docker memory limit in `docker-compose.yml`

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
```

---

## 📊 Resource Usage

Typical resource usage:

| Task | Memory | Time | Cost |
|------|--------|------|------|
| Short story | ~1GB | 2-5 min | $0.50-$2.00 |
| Novella | ~1-2GB | 5-15 min | $2.00-$8.00 |
| Novel | ~2-3GB | 20-60 min | $8.00-$30.00 |

Adjust `docker-compose.yml` limits based on your needs.

---

## 🚢 Production Deployment

For production deployment (cloud):

```bash
# Build for production
docker build -t narra_forge:2.0.0 .

# Tag for registry
docker tag narra_forge:2.0.0 your-registry.com/narra_forge:2.0.0

# Push to registry
docker push your-registry.com/narra_forge:2.0.0

# Deploy
docker run -d \
  --name narra_forge_prod \
  -e OPENAI_API_KEY=sk-... \
  -v /data:/app/data \
  -v /output:/app/output \
  your-registry.com/narra_forge:2.0.0
```

---

**For more information, see [USER_GUIDE.md](USER_GUIDE.md)**
