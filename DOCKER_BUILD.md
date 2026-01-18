# Docker Build Guide - NARRA FORGE V2

## 🚀 Quick Start (Automatic Type Safety)

The platform now has **automatic type safety** built into the Docker build process!

### Simple Build (Recommended)

```bash
# Build with automatic type generation
./scripts/build-with-types.sh

# Or build specific services
./scripts/build-with-types.sh frontend
./scripts/build-with-types.sh backend frontend
```

### What Happens Automatically

1. **OpenAPI spec generation** - Backend schemas → `api-spec.json`
2. **TypeScript type generation** - `api-spec.json` → Frontend types
3. **Type checking** - Both backend (mypy) and frontend (tsc)
4. **Docker build** - Containers with validated types

**No manual steps required!** 🎉

---

## 🛠️ Traditional Build (Also Works)

```bash
# Standard docker-compose build (uses committed types)
docker-compose build

# Build specific service
docker-compose build frontend
```

---

## 📋 Build Process Details

### Backend Build

The backend Dockerfile automatically:
- ✅ Installs Python dependencies
- ✅ Generates OpenAPI spec during build
- ✅ Validates Pydantic schemas
- ✅ Creates optimized production image

### Frontend Build

The frontend Dockerfile automatically:
- ✅ Installs Node dependencies
- ✅ Uses committed `api-spec.json` for type generation
- ✅ Runs TypeScript type checking (via prebuild hook)
- ✅ Builds Next.js application
- ✅ Creates optimized production image

---

## 🔄 Type Synchronization

### How It Works

```
1. Developer changes backend schema (api/schemas/*.py)
   ↓
2. Pre-commit hook runs (if installed)
   ↓
3. Generates api-spec.json automatically
   ↓
4. Generates frontend TypeScript types automatically
   ↓
5. Runs type checking (fails if errors)
   ↓
6. Commit includes updated types
   ↓
7. Docker build uses committed types
   ✅ Always synchronized!
```

### Manual Type Generation (if needed)

```bash
# Generate OpenAPI spec
python scripts/generate_openapi_spec.py

# Generate TypeScript types
cd frontend
npm run generate:types:local

# Or use the all-in-one script
./scripts/regenerate-types.sh --local
```

---

## 🧪 Development Workflow

### Option 1: With Pre-commit Hooks (Recommended)

```bash
# One-time setup
pip install pre-commit
pre-commit install

# Now types auto-update on every commit!
git commit -m "feat: Add new field to ProductionBrief"
# → Pre-commit automatically:
#    - Generates OpenAPI spec
#    - Generates TypeScript types
#    - Runs type checking
#    - Fails if type errors
```

### Option 2: Manual Type Updates

```bash
# 1. Change backend schema
vim api/schemas/production.py

# 2. Regenerate types
./scripts/regenerate-types.sh --local

# 3. Commit everything
git add api/schemas/ api-spec.json frontend/src/types/
git commit -m "feat: Update schemas"
```

### Option 3: Docker Build Only

```bash
# Just build - uses committed types
docker-compose build

# Or with helper script (regenerates types first)
./scripts/build-with-types.sh
```

---

## 🐛 Troubleshooting

### Build fails with "api-spec.json not found"

```bash
# Generate it manually
python scripts/generate_openapi_spec.py --output api-spec.json
cp api-spec.json frontend/

# Then rebuild
docker-compose build
```

### TypeScript errors during build

```bash
# Check type errors locally
cd frontend
npm run type-check

# Regenerate types
npm run generate:types:local

# Check again
npm run type-check
```

### Backend import errors during OpenAPI generation

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Try generating spec directly
python -c "from api.main import app; print(app.openapi())"
```

### Pre-commit hook fails

```bash
# Run hooks manually to see errors
pre-commit run --all-files

# Or skip hooks temporarily (not recommended)
git commit --no-verify -m "..."
```

---

## 📊 Build Optimization

### Multi-stage Builds

Both Dockerfiles use multi-stage builds for:
- ✅ Smaller production images
- ✅ Faster builds (cached layers)
- ✅ Separation of build vs runtime dependencies

### Caching

Docker build cache works best when:
- Dependencies change less frequently than code
- You build regularly (cache stays warm)
- You use `docker-compose build` (not `--no-cache`)

### Parallel Builds

```bash
# Build all services in parallel
docker-compose build --parallel

# Or with our script
./scripts/build-with-types.sh
```

---

## 🎯 CI/CD Integration

### GitHub Actions

The `.github/workflows/test.yml` automatically:
1. Validates Python types (mypy)
2. Generates OpenAPI spec
3. Generates TypeScript types
4. Validates type synchronization
5. Runs TypeScript type checking
6. **Fails PR if types are out of sync**

### Local Pre-push

Add to `.git/hooks/pre-push`:
```bash
#!/bin/bash
./scripts/regenerate-types.sh --local
npm run type-check
```

---

## 💡 Best Practices

### DO ✅

- Use `./scripts/build-with-types.sh` for builds
- Install pre-commit hooks for automatic type updates
- Commit `api-spec.json` to version control
- Run type-check before pushing
- Review generated types after schema changes

### DON'T ❌

- Manually edit `frontend/src/types/api-generated.ts`
- Skip type checking with `--no-verify`
- Build with stale `api-spec.json`
- Ignore type errors during build
- Use `Dict[str, Any]` for structured data in backend

---

## 📚 Additional Resources

- [Type Safety System Documentation](docs/TYPE_SAFETY_SYSTEM.md)
- [Pre-commit Hooks Configuration](.pre-commit-config.yaml)
- [OpenAPI Spec Generator](scripts/generate_openapi_spec.py)
- [Type Regeneration Script](scripts/regenerate-types.sh)

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Read error messages carefully
3. Try regenerating types manually
4. Check pre-commit hook logs
5. Review TypeScript compilation errors
6. Validate backend schemas with mypy

**Common fixes solve 90% of issues:**
```bash
# The magic reset
./scripts/regenerate-types.sh --local
docker-compose build --no-cache
```

---

**Build with confidence!** 🚀
