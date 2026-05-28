# ============================================================
# PDFjin - Cloud-First DEPLOY (Integrated Frontend & Backend)
# ============================================================

$ErrorActionPreference = "Continue"
$ProjectRoot = $PSScriptRoot

$GCP_PROJECT = "pdgjin"
$GCP_REGION  = "us-central1"
$SERVICE_NAME = "pdfjin-api"

Write-Host "Starting Cloud-First Deployment for PDFjin..." -ForegroundColor Cyan

# ── STEP 0: Sync local Frontend to Backend directory ────
Write-Host "STEP 0: Regenerating sitemap and RSS feed, syncing frontend source to backend/static_frontend..." -ForegroundColor Yellow
python "$ProjectRoot\generate_sitemap.py"
python "$ProjectRoot\generate_rss.py"

if (Test-Path "$ProjectRoot\backend\static_frontend") {
    Remove-Item -Path "$ProjectRoot\backend\static_frontend" -Recurse -Force
}
New-Item -ItemType Directory -Path "$ProjectRoot\backend\static_frontend" -Force
Copy-Item -Path "$ProjectRoot\frontend\*" -Destination "$ProjectRoot\backend\static_frontend\" -Recurse -Force

# ── STEP 1: Skip DB Sync to prevent overwriting production DB ──────────────
Write-Host "STEP 1/2: Skipping DB sync to preserve production data..." -ForegroundColor Yellow

# ── STEP 2: Backend & Frontend - Deploy to Cloud Run ──────
Write-Host "STEP 2/2: Building and deploying Integrated Service to Cloud Run..." -ForegroundColor Yellow
# Using gcloud run deploy directly with source code (it uses Cloud Build internally)
$deployResult = gcloud.cmd run deploy $SERVICE_NAME `
    --source ./backend `
    --region $GCP_REGION `
    --platform managed `
    --allow-unauthenticated `
    --project $GCP_PROJECT `
    --quiet `
    --port 8080 `
    --cpu 2 `
    --memory 2Gi `
    --max-instances 20

if ($LASTEXITCODE -ne 0) {
    Write-Host "Cloud Run deploy failed!" -ForegroundColor Red
    exit 1
}

Write-Host "============================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "  Project: $GCP_PROJECT"
Write-Host "  URL: https://pdfjin-api-97530578628.us-central1.run.app"
Write-Host "============================================" -ForegroundColor Green
