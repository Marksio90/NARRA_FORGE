# Scripts Directory

Utility scripts for NARRA_FORGE V2 platform management.

## Available Scripts

### `generate_secrets.py`

Generates cryptographically secure secrets for your `.env` configuration.

**Usage:**
```bash
python scripts/generate_secrets.py
```

**Output:**
- JWT secret key (64 characters hex)
- Database password (32 characters)
- Redis password (32 characters)
- Grafana admin password (16 characters)
- Pre-formatted DATABASE_URL
- Pre-formatted REDIS_URL
- Pre-formatted Celery URLs

**Example:**
```bash
$ python scripts/generate_secrets.py

╔══════════════════════════════════════════════════════════════════════════════╗
║                    NARRA_FORGE V2 - Generated Secrets                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 Copy these values to your .env file:
================================================================================

# 🔐 Security Secrets
JWT_SECRET_KEY=a1b2c3d4...
DB_PASSWORD=Xy9#mK...
REDIS_PASSWORD=Pq8@nT...

# 🗄️  Database Configuration
DATABASE_URL=postgresql+asyncpg://narra_forge:Xy9#mK...@postgres:5432/narra_forge

# 🔴 Redis & Celery Configuration
REDIS_URL=redis://:Pq8@nT...@redis:6379/0
CELERY_BROKER_URL=redis://:Pq8@nT...@redis:6379/0
CELERY_RESULT_BACKEND=redis://:Pq8@nT...@redis:6379/1

# 📊 Grafana
GRAFANA_ADMIN_PASSWORD=Ab3XyZ...

✅ All secrets generated successfully!
```

## Adding New Scripts

When adding new scripts:
1. Add Python shebang: `#!/usr/bin/env python3`
2. Include docstring with usage
3. Make executable: `chmod +x scripts/your_script.py`
4. Document here in README.md
