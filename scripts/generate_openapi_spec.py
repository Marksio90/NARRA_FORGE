#!/usr/bin/env python3
"""
Generate OpenAPI specification from FastAPI application.

This script extracts the OpenAPI schema from the FastAPI app and saves it to a JSON file.
This allows frontend TypeScript generation without running the API server.

Usage:
    python scripts/generate_openapi_spec.py [--output api-spec.json]
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def generate_openapi_spec(output_file: str = "api-spec.json") -> None:
    """Generate OpenAPI spec from FastAPI app."""
    print(f"🔄 Generating OpenAPI specification...")

    try:
        from api.main import app
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)

    try:
        # Get OpenAPI schema
        openapi_schema = app.openapi()

        # Enhance schema with better descriptions
        openapi_schema["info"]["description"] = """
NARRA FORGE V2 - AI Narrative Generation Platform

This API provides endpoints for:
- User authentication and management
- Project and narrative organization
- AI-powered narrative generation
- Real-time job progress tracking
- Export and version control

All types are strongly-typed using Pydantic schemas.
TypeScript types are auto-generated from this OpenAPI specification.
"""

        # Save to file
        output_path = project_root / output_file
        with open(output_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)

        print(f"✅ OpenAPI spec saved to: {output_path}")
        print(f"📊 Total endpoints: {len(openapi_schema.get('paths', {}))}")
        print(f"📦 Total schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")

        # List all available tags (API categories)
        tags = openapi_schema.get("tags", [])
        if tags:
            print(f"\n📂 API Categories:")
            for tag in tags:
                print(f"   - {tag['name']}: {tag.get('description', 'No description')}")

    except Exception as e:
        print(f"❌ Failed to generate OpenAPI spec: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI specification from FastAPI app"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="api-spec.json",
        help="Output file path (default: api-spec.json)"
    )
    args = parser.parse_args()

    generate_openapi_spec(args.output)


if __name__ == "__main__":
    main()
