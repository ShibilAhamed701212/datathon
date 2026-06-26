param(
    [switch]$Local,
    [string]$Port = "8000"
)

$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON = "C:\Users\sclip\AppData\Local\Programs\Python\Python312\python.exe"

if ($Local) {
    Write-Host "Starting locally on port $Port..." -ForegroundColor Green
    & $PYTHON "$PROJECT_DIR\server.py"
    return
}

Write-Host "=== KSP Crime Copilot - Catalyst Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check if logged in
$whoami = & catalyst whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Step 1: Login to Catalyst" -ForegroundColor Yellow
    Write-Host "A browser will open for authentication." -ForegroundColor Yellow
    catalyst login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Login failed. Aborting."
        exit 1
    }
}

Write-Host "Step 2: Build Docker image for AppSail..." -ForegroundColor Yellow
docker build -t ksp-crime-copilot "$PROJECT_DIR"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed."
    exit 1
}

Write-Host "Step 3: Deploy to Catalyst..." -ForegroundColor Yellow
Write-Host "Option A: Deploy as AdvancedIO Function" -ForegroundColor Green
Write-Host "  catalyst deploy --only functions" -ForegroundColor White
Write-Host ""
Write-Host "Option B: Deploy as AppSail (recommended for full app)" -ForegroundColor Green
Write-Host "  Push Docker image to Catalyst Container Registry, then:" -ForegroundColor White
Write-Host "  catalyst appsail:add" -ForegroundColor White
Write-Host ""
Write-Host "Option C: Deploy everything with one command" -ForegroundColor Green
Write-Host "  catalyst deploy" -ForegroundColor White
Write-Host ""
Write-Host "For quick deploy, run: catalyst deploy" -ForegroundColor Cyan
