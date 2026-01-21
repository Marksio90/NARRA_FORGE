# Health Endpoint Test Script for NarraForge (PowerShell)
# Tests all three health check endpoints

$BackendUrl = if ($env:BACKEND_URL) { $env:BACKEND_URL } else { "http://localhost:8000" }

Write-Host "🏥 Testing NarraForge Health Endpoints" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Test-Endpoint {
    param(
        [string]$Endpoint,
        [string]$Description
    )

    Write-Host "Testing: $Description" -ForegroundColor Yellow
    Write-Host "Endpoint: $BackendUrl$Endpoint"
    Write-Host "---"

    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl$Endpoint" -Method Get -UseBasicParsing
        $statusCode = $response.StatusCode
        $body = $response.Content

        if ($statusCode -eq 200) {
            Write-Host "✓ Status: $statusCode OK" -ForegroundColor Green
            Write-Host "Response:"
            $body | ConvertFrom-Json | ConvertTo-Json -Depth 10
        } else {
            Write-Host "✗ Status: $statusCode FAILED" -ForegroundColor Red
            Write-Host "Response:"
            Write-Host $body
        }
    } catch {
        Write-Host "✗ Request failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host ""
}

# Check if backend is reachable
Write-Host "Checking if backend is reachable..."
try {
    $null = Invoke-WebRequest -Uri "$BackendUrl/health/live" -Method Get -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Backend is reachable" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "✗ Backend is not reachable at $BackendUrl" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure Docker services are running:"
    Write-Host "  docker compose up -d"
    Write-Host ""
    exit 1
}

# Test all health endpoints
Test-Endpoint -Endpoint "/health/live" -Description "Liveness Check (Is app running?)"
Test-Endpoint -Endpoint "/health/ready" -Description "Readiness Check (Is app ready for requests?)"
Test-Endpoint -Endpoint "/health" -Description "Full Health Check (All services status)"

Write-Host ""
Write-Host "📊 Health Check Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Endpoints tested:"
Write-Host "  1. /health/live  - Basic liveness (should always return 200 if app is running)"
Write-Host "  2. /health/ready - Readiness check (returns 200 if ready to process requests)"
Write-Host "  3. /health       - Full health check (shows status of all services)"
Write-Host ""
Write-Host "Expected behavior:"
Write-Host "  - /health/live should always return: {`"alive`": true, `"message`": `"Application is running`"}"
Write-Host "  - /health/ready returns ready:true only if:"
Write-Host "      • PostgreSQL is connected"
Write-Host "      • Redis is connected"
Write-Host "      • OpenAI API key is configured"
Write-Host "  - /health shows status of:"
Write-Host "      • PostgreSQL database"
Write-Host "      • Redis cache/broker"
Write-Host "      • OpenAI API configuration"
Write-Host "      • Anthropic API configuration (optional)"
Write-Host ""
Write-Host "💡 If /health/ready shows ready:false due to missing OpenAI API key:" -ForegroundColor Yellow
Write-Host "   1. Create/edit .env file in project root"
Write-Host "   2. Add: OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE"
Write-Host "   3. Restart services: docker compose restart narraforge-backend"
Write-Host ""
