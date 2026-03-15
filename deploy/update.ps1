# ============================================================
#  PDFjin — Deploy Updates Script
#  Run this every time you change HTML/CSS/JS files
#  Usage: .\deploy\update.ps1
# ============================================================

$BUCKET_NAME = "pdfjin.com"
$FRONTEND_DIR = "C:\Users\ADMIN\Desktop\pdfjin\frontend"
$HAS_CDN = $true              # Set to $true after add-custom-domain is run

function Write-Step($msg) { Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "  [INFO] $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "┌─────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│  PDFjin — Deploying Update to GCP   │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────┘" -ForegroundColor Magenta

# ── Sync all files ───────────────────────────────────────────
Write-Step "Uploading changed files..."

# Upload everything first
gcloud storage cp -r "$FRONTEND_DIR/*" "gs://$BUCKET_NAME/"

# Force MIME types and no-cache for ALL HTML files recursively
Write-Info "Setting metadata for HTML files..."
Get-ChildItem -Path "$FRONTEND_DIR" -Filter "*.html" -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Replace("$FRONTEND_DIR\", "").Replace("\", "/")
    gcloud storage objects update "gs://$BUCKET_NAME/$relativePath" --content-type="text/html" --cache-control="no-cache, max-age=0"
}

Write-Success "Files uploaded and metadata updated for gs://$BUCKET_NAME"

# ── Bust CDN cache if applicable ─────────────────────────────
if ($HAS_CDN) {
    Write-Step "Invalidating CDN cache..."
    gcloud compute url-maps invalidate-cdn-cache pdgjin-url-map --path="/*" --async
    Write-Success "CDN cache cleared! Changes will be live in ~30 seconds."
}
else {
    Write-Info "Changes are live immediately (no CDN cache to clear)."
}

Write-Host ""
Write-Host "  🌐  Live at: https://storage.googleapis.com/$BUCKET_NAME/index.html" -ForegroundColor Green
Write-Host ""
