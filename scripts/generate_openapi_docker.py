#!/usr/bin/env python3
"""
Generate OpenAPI spec during Docker build.
This script is called by Dockerfile to generate api-spec.json.
"""
import sys
import json

# Add app to path
sys.path.insert(0, '/app')

try:
    from api.main import app

    # Generate OpenAPI spec
    spec = app.openapi()
    spec['info']['description'] = 'NARRA FORGE V2 - Auto-generated OpenAPI spec for TypeScript type generation'

    # Write to file
    with open('/app/api-spec.json', 'w') as f:
        json.dump(spec, f, indent=2)

    print('OpenAPI spec generated successfully')

except Exception as e:
    print(f'Failed to generate OpenAPI spec: {e}')
    sys.exit(1)
