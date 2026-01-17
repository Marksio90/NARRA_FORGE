#!/usr/bin/env python3
"""
NARRA_FORGE API Server Runner.

Simple script to start the FastAPI development server.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run the API server."""
    import uvicorn
    from api.config import settings

    print("=" * 60)
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print("=" * 60)
    print(f"Environment: {settings.sentry_environment}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"Debug: {settings.debug}")
    print(f"Docs: http://{settings.host}:{settings.port}{settings.docs_url}")
    print(f"Health: http://{settings.host}:{settings.port}/health")
    print("=" * 60)

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="debug" if settings.debug else "info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
