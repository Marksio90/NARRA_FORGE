#!/usr/bin/env python3
"""
Verification script for NARRA_FORGE monitoring setup.
Checks that all configurations are valid and complete.
"""

import json
import sys
from pathlib import Path

import yaml


def check_file_exists(path: Path, description: str) -> bool:
    """Check if file exists."""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} - NOT FOUND")
        return False


def validate_yaml(path: Path, description: str) -> bool:
    """Validate YAML file."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        print(f"✓ {description}: Valid YAML")
        return True
    except Exception as e:
        print(f"✗ {description}: Invalid YAML - {e}")
        return False


def validate_json(path: Path, description: str) -> bool:
    """Validate JSON file."""
    try:
        with open(path) as f:
            data = json.load(f)
        print(f"✓ {description}: Valid JSON")
        return True
    except Exception as e:
        print(f"✗ {description}: Invalid JSON - {e}")
        return False


def check_grafana_dashboard(path: Path) -> bool:
    """Validate Grafana dashboard structure."""
    try:
        with open(path) as f:
            data = json.load(f)

        required_fields = ['panels', 'title', 'uid']
        missing = [f for f in required_fields if f not in data]

        if missing:
            print(f"✗ Dashboard missing fields: {missing}")
            return False

        panel_count = len(data.get('panels', []))
        print(f"✓ Dashboard has {panel_count} panels")

        # Check panel types
        panel_types = {}
        for panel in data['panels']:
            ptype = panel.get('type', 'unknown')
            panel_types[ptype] = panel_types.get(ptype, 0) + 1

        print(f"  Panel types: {dict(panel_types)}")
        return True

    except Exception as e:
        print(f"✗ Dashboard validation failed: {e}")
        return False


def check_prometheus_config(path: Path) -> bool:
    """Validate Prometheus configuration."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)

        # Check scrape configs
        scrape_configs = data.get('scrape_configs', [])
        if not scrape_configs:
            print("✗ No scrape_configs defined")
            return False

        print(f"✓ Prometheus has {len(scrape_configs)} scrape configs:")
        for config in scrape_configs:
            job_name = config.get('job_name', 'unknown')
            targets = config.get('static_configs', [{}])[0].get('targets', [])
            print(f"  - {job_name}: {targets}")

        return True

    except Exception as e:
        print(f"✗ Prometheus config validation failed: {e}")
        return False


def check_docker_compose(path: Path) -> bool:
    """Validate docker-compose configuration."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)

        services = data.get('services', {})
        if not services:
            print("✗ No services defined")
            return False

        print(f"✓ Docker Compose has {len(services)} services:")
        for service_name, config in services.items():
            image = config.get('image', 'N/A')
            ports = config.get('ports', [])
            print(f"  - {service_name}: {image} (ports: {ports})")

        # Check volumes
        volumes = data.get('volumes', {})
        print(f"✓ Docker Compose has {len(volumes)} volumes: {list(volumes.keys())}")

        return True

    except Exception as e:
        print(f"✗ Docker Compose validation failed: {e}")
        return False


def check_metrics_implementation() -> bool:
    """Check if metrics are implemented in code."""
    metrics_file = Path('narra_forge/monitoring/metrics.py')

    if not metrics_file.exists():
        print(f"✗ Metrics implementation not found: {metrics_file}")
        return False

    with open(metrics_file) as f:
        content = f.read()

    # Check for key metrics
    required_metrics = [
        'pipeline_duration_seconds',
        'pipeline_total',
        'agent_duration_seconds',
        'cost_usd_total',
        'quality_score',
        'tokens_used_total',
    ]

    missing = []
    for metric in required_metrics:
        if metric not in content:
            missing.append(metric)

    if missing:
        print(f"✗ Missing metrics in implementation: {missing}")
        return False

    print(f"✓ All {len(required_metrics)} required metrics implemented")
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🔍 NARRA_FORGE Monitoring Setup Verification")
    print("=" * 60)
    print()

    base_path = Path('.')
    monitoring_path = base_path / 'monitoring'

    checks = []

    # File existence checks
    print("📁 Checking file existence...")
    checks.append(check_file_exists(
        monitoring_path / 'prometheus.yml',
        'Prometheus config'
    ))
    checks.append(check_file_exists(
        monitoring_path / 'grafana/datasources/prometheus.yml',
        'Grafana datasource config'
    ))
    checks.append(check_file_exists(
        monitoring_path / 'grafana/dashboards/dashboard.yml',
        'Grafana dashboard provisioning'
    ))
    checks.append(check_file_exists(
        monitoring_path / 'grafana/dashboards/narra_forge_dashboard.json',
        'Grafana dashboard JSON'
    ))
    checks.append(check_file_exists(
        base_path / 'docker-compose.monitoring.yml',
        'Docker Compose config'
    ))
    checks.append(check_file_exists(
        monitoring_path / 'metrics_server.py',
        'Metrics test server'
    ))
    checks.append(check_file_exists(
        monitoring_path / 'MONITORING_GUIDE.md',
        'Monitoring guide'
    ))
    checks.append(check_file_exists(
        monitoring_path / 'README.md',
        'Monitoring README'
    ))
    print()

    # Configuration validation
    print("🔧 Validating configurations...")
    checks.append(validate_yaml(
        monitoring_path / 'prometheus.yml',
        'Prometheus YAML'
    ))
    checks.append(validate_yaml(
        monitoring_path / 'grafana/datasources/prometheus.yml',
        'Grafana datasource YAML'
    ))
    checks.append(validate_yaml(
        monitoring_path / 'grafana/dashboards/dashboard.yml',
        'Grafana provisioning YAML'
    ))
    checks.append(validate_json(
        monitoring_path / 'grafana/dashboards/narra_forge_dashboard.json',
        'Grafana dashboard JSON'
    ))
    checks.append(validate_yaml(
        base_path / 'docker-compose.monitoring.yml',
        'Docker Compose YAML'
    ))
    print()

    # Detailed checks
    print("📊 Checking dashboard structure...")
    checks.append(check_grafana_dashboard(
        monitoring_path / 'grafana/dashboards/narra_forge_dashboard.json'
    ))
    print()

    print("🔍 Checking Prometheus configuration...")
    checks.append(check_prometheus_config(
        monitoring_path / 'prometheus.yml'
    ))
    print()

    print("🐳 Checking Docker Compose setup...")
    checks.append(check_docker_compose(
        base_path / 'docker-compose.monitoring.yml'
    ))
    print()

    print("📈 Checking metrics implementation...")
    checks.append(check_metrics_implementation())
    print()

    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total}) - {percentage:.0f}%")
        print()
        print("🎉 Monitoring setup is complete and valid!")
        print()
        print("📝 Next steps:")
        print("   1. Start monitoring stack: docker-compose -f docker-compose.monitoring.yml up -d")
        print("   2. Start metrics server: python monitoring/metrics_server.py")
        print("   3. Open Grafana: http://localhost:3000 (admin/admin)")
        print("   4. View dashboard: 'NARRA_FORGE Production Dashboard'")
        return 0
    else:
        failed = total - passed
        print(f"❌ {failed} CHECK(S) FAILED ({passed}/{total}) - {percentage:.0f}%")
        print()
        print("⚠️  Please fix the issues above before proceeding.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
