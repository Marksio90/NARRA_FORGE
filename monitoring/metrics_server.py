#!/usr/bin/env python3
"""
Standalone metrics server for testing Prometheus + Grafana integration.
Exposes /metrics endpoint that Prometheus can scrape.

Usage:
    python monitoring/metrics_server.py
"""

import asyncio
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


# Define all NARRA_FORGE metrics
# Pipeline Metrics
pipeline_duration = Histogram(
    'narra_forge_pipeline_duration_seconds',
    'Time taken for full pipeline execution',
    ['production_type', 'genre'],
    buckets=[10, 30, 60, 120, 300, 600, 1200, 1800]
)

pipeline_total = Counter(
    'narra_forge_pipeline_total',
    'Total number of pipelines executed',
    ['production_type', 'genre', 'status']
)

jobs_active = Gauge(
    'narra_forge_jobs_active',
    'Number of currently active jobs'
)

# Agent Metrics
agent_duration = Histogram(
    'narra_forge_agent_duration_seconds',
    'Time taken for agent execution',
    ['agent_id', 'model'],
    buckets=[0.5, 1, 2, 5, 10, 30, 60, 120]
)

agent_errors = Counter(
    'narra_forge_agent_errors_total',
    'Total number of agent errors',
    ['agent_id', 'error_type']
)

# API Metrics
api_calls = Counter(
    'narra_forge_api_calls_total',
    'Total number of OpenAI API calls',
    ['model', 'agent_id']
)

api_call_duration = Histogram(
    'narra_forge_api_call_duration_seconds',
    'OpenAI API call duration',
    ['model'],
    buckets=[0.5, 1, 2, 5, 10, 20, 30]
)

api_errors = Counter(
    'narra_forge_api_errors_total',
    'Total number of API errors',
    ['model', 'error_type']
)

# Token & Cost Metrics
tokens_used = Counter(
    'narra_forge_tokens_used_total',
    'Total tokens used',
    ['model', 'token_type']
)

cost_usd = Counter(
    'narra_forge_cost_usd_total',
    'Total cost in USD',
    ['model', 'agent_id']
)

# Quality Metrics
quality_score = Histogram(
    'narra_forge_quality_score',
    'Narrative quality score (0.0-1.0)',
    ['production_type', 'metric_type'],
    buckets=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
)

# Retry Metrics
retry_attempts = Counter(
    'narra_forge_retry_attempts_total',
    'Total number of retry attempts',
    ['agent_id', 'reason']
)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for /metrics endpoint."""

    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = b"""
            <html>
            <head><title>NARRA_FORGE Metrics</title></head>
            <body>
            <h1>NARRA_FORGE Metrics Server</h1>
            <p>Prometheus metrics available at <a href="/metrics">/metrics</a></p>
            <p>Status: Running</p>
            </body>
            </html>
            """
            self.wfile.write(html)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress request logging."""
        pass


def simulate_metrics():
    """Simulate realistic metric data for testing."""
    production_types = ['short_story', 'novella', 'novel']
    genres = ['fantasy', 'scifi', 'mystery', 'romance']
    agents = [
        'a01_brief_interpreter',
        'a02_world_architect',
        'a03_character_architect',
        'a04_structure_designer',
        'a05_segment_planner',
        'a06_sequential_generator',
        'a07_coherence_validator',
        'a08_language_stylizer',
        'a09_editorial_reviewer',
        'a10_output_processor'
    ]
    models = ['gpt-4o-mini', 'gpt-4o']
    metric_types = ['coherence', 'logic', 'psychology', 'temporal']

    print("🔄 Starting metric simulation...")
    print("   Generating realistic NARRA_FORGE metrics...")

    while True:
        # Simulate pipeline execution
        prod_type = random.choice(production_types)
        genre = random.choice(genres)

        # Pipeline duration (short_story: 300-600s, novella: 600-1200s, novel: 1200-1800s)
        if prod_type == 'short_story':
            duration = random.uniform(300, 600)
        elif prod_type == 'novella':
            duration = random.uniform(600, 1200)
        else:
            duration = random.uniform(1200, 1800)

        pipeline_duration.labels(production_type=prod_type, genre=genre).observe(duration)

        # Pipeline success (95% success rate)
        status = 'success' if random.random() < 0.95 else 'failed'
        pipeline_total.labels(production_type=prod_type, genre=genre, status=status).inc()

        # Active jobs
        jobs_active.set(random.randint(0, 5))

        # Simulate agent executions
        for agent in agents:
            model = 'gpt-4o' if agent in ['a06_sequential_generator', 'a08_language_stylizer'] else 'gpt-4o-mini'

            # Agent duration
            agent_time = random.uniform(5, 120)
            agent_duration.labels(agent_id=agent, model=model).observe(agent_time)

            # Agent errors (2% error rate)
            if random.random() < 0.02:
                error_type = random.choice(['rate_limit', 'timeout', 'validation'])
                agent_errors.labels(agent_id=agent, error_type=error_type).inc()

            # API calls
            api_calls.labels(model=model, agent_id=agent).inc()
            api_call_duration.labels(model=model).observe(random.uniform(0.5, 10))

            # API errors (1% error rate)
            if random.random() < 0.01:
                error_type = random.choice(['rate_limit', 'timeout', 'server_error'])
                api_errors.labels(model=model, error_type=error_type).inc()

            # Tokens
            if model == 'gpt-4o-mini':
                tokens = random.randint(500, 2000)
            else:
                tokens = random.randint(2000, 8000)

            tokens_used.labels(model=model, token_type='prompt').inc(tokens // 2)
            tokens_used.labels(model=model, token_type='completion').inc(tokens // 2)

            # Cost (gpt-4o-mini: $0.15/1M, gpt-4o: $2.50/1M prompt)
            if model == 'gpt-4o-mini':
                cost = tokens * 0.00000015
            else:
                cost = tokens * 0.0000025

            cost_usd.labels(model=model, agent_id=agent).inc(cost)

            # Retry attempts (5% retry rate)
            if random.random() < 0.05:
                reason = random.choice(['rate_limit', 'timeout', 'validation'])
                retry_attempts.labels(agent_id=agent, reason=reason).inc()

        # Quality scores (high quality: 0.85-0.95)
        for metric_type in metric_types:
            score = random.uniform(0.85, 0.95)
            quality_score.labels(production_type=prod_type, metric_type=metric_type).observe(score)

        # Sleep between simulations (simulate 1 pipeline every 30-60 seconds)
        sleep_time = random.uniform(30, 60)
        print(f"✓ Simulated {prod_type} ({genre}) - duration: {duration:.0f}s, status: {status}")
        time.sleep(sleep_time)


def main():
    """Start metrics server and simulation."""
    print("=" * 60)
    print("🚀 NARRA_FORGE Metrics Server")
    print("=" * 60)
    print()
    print("📊 Metrics endpoint: http://localhost:8000/metrics")
    print("🌐 Web interface:    http://localhost:8000/")
    print()
    print("ℹ️  This server simulates NARRA_FORGE metrics for testing")
    print("   Prometheus + Grafana monitoring stack.")
    print()
    print("📈 Grafana dashboard: http://localhost:3000")
    print("   (username: admin, password: admin)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Start HTTP server in background thread
    server = HTTPServer(('0.0.0.0', 8000), MetricsHandler)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print("✓ Metrics server started on http://0.0.0.0:8000")
    print()

    # Start metric simulation
    try:
        simulate_metrics()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down metrics server...")
        server.shutdown()
        print("✓ Server stopped")


if __name__ == '__main__':
    main()
