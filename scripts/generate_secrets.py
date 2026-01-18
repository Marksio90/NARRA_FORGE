#!/usr/bin/env python3
"""
NARRA_FORGE V2 - Secret Generator

Generates cryptographically secure secrets for .env configuration.
Run this script and copy the output to your .env file.

Usage:
    python scripts/generate_secrets.py

Output:
    Generates all required secrets with proper format for .env file
"""

import secrets
import string
from typing import Dict


def generate_hex_token(length: int = 64) -> str:
    """Generate a hex token (for JWT and other secrets)."""
    return secrets.token_hex(length // 2)


def generate_password(length: int = 32, include_special: bool = True) -> str:
    """Generate a strong random password."""
    alphabet = string.ascii_letters + string.digits
    if include_special:
        alphabet += "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Ensure at least one character from each category
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]

    if include_special:
        password.append(secrets.choice("!@#$%^&*()-_=+"))

    # Fill the rest
    password.extend(secrets.choice(alphabet) for _ in range(length - len(password)))

    # Shuffle
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def generate_database_url(user: str, password: str, host: str, port: int, dbname: str) -> str:
    """Generate properly formatted DATABASE_URL."""
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


def generate_redis_url(password: str, host: str, port: int, db: int) -> str:
    """Generate properly formatted REDIS_URL."""
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"


def main():
    """Generate all required secrets and display them."""

    # Generate secrets
    secrets_dict = {
        'jwt_secret': generate_hex_token(64),
        'db_password': generate_password(32),
        'redis_password': generate_password(32),
        'grafana_password': generate_password(16, include_special=False),
    }

    # Database and Redis config
    db_user = 'narra_forge'
    db_host = 'postgres'
    db_port = 5432
    db_name = 'narra_forge'
    redis_host = 'redis'
    redis_port = 6379

    # Generate URLs
    database_url = generate_database_url(
        db_user,
        secrets_dict['db_password'],
        db_host,
        db_port,
        db_name
    )

    redis_url = generate_redis_url(
        secrets_dict['redis_password'],
        redis_host,
        redis_port,
        0
    )

    celery_broker = generate_redis_url(
        secrets_dict['redis_password'],
        redis_host,
        redis_port,
        0
    )

    celery_result = generate_redis_url(
        secrets_dict['redis_password'],
        redis_host,
        redis_port,
        1
    )

    # Display results
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "NARRA_FORGE V2 - Generated Secrets" + " " * 24 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print("📋 Copy these values to your .env file:")
    print("=" * 80)
    print()

    print("# 🔐 Security Secrets")
    print(f"JWT_SECRET_KEY={secrets_dict['jwt_secret']}")
    print(f"DB_PASSWORD={secrets_dict['db_password']}")
    print(f"REDIS_PASSWORD={secrets_dict['redis_password']}")
    print()

    print("# 🗄️  Database Configuration")
    print(f"DATABASE_URL={database_url}")
    print()

    print("# 🔴 Redis & Celery Configuration")
    print(f"REDIS_URL={redis_url}")
    print(f"CELERY_BROKER_URL={celery_broker}")
    print(f"CELERY_RESULT_BACKEND={celery_result}")
    print()

    print("# 📊 Grafana")
    print(f"GRAFANA_ADMIN_PASSWORD={secrets_dict['grafana_password']}")
    print()

    print("=" * 80)
    print()
    print("✅ All secrets generated successfully!")
    print()
    print("⚠️  SECURITY WARNINGS:")
    print("  • Never commit these secrets to git")
    print("  • Store them securely (password manager, vault, etc.)")
    print("  • Use different secrets for dev/staging/production")
    print("  • Rotate secrets regularly (every 90 days)")
    print()
    print("📝 Next steps:")
    print("  1. Copy the values above to your .env file")
    print("  2. Set your OPENAI_API_KEY")
    print("  3. Run: docker-compose build && docker-compose up -d")
    print()


if __name__ == "__main__":
    main()
