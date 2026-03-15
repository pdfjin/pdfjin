# ============================================================
#  PDFjin — Google Cloud Setup Script (Windows PowerShell)
#  Run this ONCE to create everything on GCP
#  Usage: .\deploy\setup-gcp.ps1
# ============================================================

# ── Configuration — EDIT THESE ──────────────────────────────
$PROJECT_ID = "pdgjin"                 # ← Your actual GCP Project ID
$BUCKET_NAME = "pdfjin.com"            # ← Your bucket name (matches domain)
$REGION = "asia-southeast1"            # Singapore (closest to Vietnam)
$FRONTEND_DIR = "$PSScriptRoot\..\frontend"
# ─────────────────────────────────────────────────────────────

function Write-Step($msg) {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Write-Success($msg) { Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "  ℹ️  $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  ❌ $msg" -ForegroundColor Red }

# ── Check gcloud is installed ────────────────────────────────
Write-Step "Checking gcloud CLI installation"
try {
    $gcloudVersion = gcloud version --format="value(Google Cloud SDK)" 2>$null
    Write-Success "gcloud CLI found: $gcloudVersion"
}
catch {
    Write-Fail "gcloud CLI not found!"
    Write-Info "Download from: https://cloud.google.com/sdk/docs/install"
    Write-Info "After installing, run: gcloud init"
    exit 1
}

# ── Authenticate ─────────────────────────────────────────────
Write-Step "Step 1 of 7 — Authenticate with Google Cloud"
Write-Info "A browser window will open for Google login..."
gcloud auth login
if ($LASTEXITCODE -ne 0) { Write-Fail "Authentication failed"; exit 1 }
Write-Success "Authenticated!"

# ── Create / Select Project ──────────────────────────────────
Write-Step "Step 2 of 7 — Select GCP Project: $PROJECT_ID"

# Project already exists — just activate it
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Could not select project '$PROJECT_ID'. Make sure you are logged in as the owner."
    exit 1
}
Write-Success "Active project set to: $PROJECT_ID"

# ── Enable APIs ───────────────────────────────────────────────
Write-Step "Step 3 of 7 — Enable Required Google Cloud APIs"
Write-Info "Enabling Storage API..."
gcloud services enable storage.googleapis.com
Write-Info "Enabling Compute API (for Load Balancer / CDN)..."
gcloud services enable compute.googleapis.com
Write-Success "APIs enabled!"

# ── Create Storage Bucket ─────────────────────────────────────
Write-Step "Step 4 of 7 — Create Cloud Storage Bucket: gs://$BUCKET_NAME"

$existingBucket = gcloud storage buckets list --filter="name=$BUCKET_NAME" --format="value(name)" 2>$null
if ($existingBucket -eq $BUCKET_NAME) {
    Write-Info "Bucket 'gs://$BUCKET_NAME' already exists — skipping creation."
}
else {
    gcloud storage buckets create "gs://$BUCKET_NAME" `
        --location=$REGION `
        --uniform-bucket-level-access
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Bucket creation failed. Try a different bucket name."
        exit 1
    }
    Write-Success "Bucket created: gs://$BUCKET_NAME"
}

# ── Make Bucket Public ────────────────────────────────────────
Write-Step "Step 5 of 7 — Make Bucket Publicly Accessible"
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET_NAME" `
    --member=allUsers `
    --role=roles/storage.objectViewer
Write-Success "Bucket is now public!"

# ── Configure Static Website Serving ─────────────────────────
Write-Step "Step 6 of 7 — Configure Static Website Settings"
gcloud storage buckets update "gs://$BUCKET_NAME" `
    --web-main-page-suffix=index.html `
    --web-error-page=index.html
Write-Success "Static website configured! (index.html as default page)"

# ── Upload Frontend Files ─────────────────────────────────────
Write-Step "Step 7 of 7 — Upload Frontend Files to Cloud Storage"
Write-Info "Uploading from: $FRONTEND_DIR"

if (-not (Test-Path $FRONTEND_DIR)) {
    Write-Fail "Frontend directory not found: $FRONTEND_DIR"
    exit 1
}

# Upload with correct MIME types
gcloud storage cp "$FRONTEND_DIR\index.html" "gs://$BUCKET_NAME/" --content-type="text/html"
gcloud storage cp -r "$FRONTEND_DIR\css" "gs://$BUCKET_NAME/"
gcloud storage cp -r "$FRONTEND_DIR\js"  "gs://$BUCKET_NAME/"

# Upload pages folder if it exists
if (Test-Path "$FRONTEND_DIR\pages") {
    gcloud storage cp -r "$FRONTEND_DIR\pages" "gs://$BUCKET_NAME/"
    Write-Success "Pages folder uploaded!"
}

# Upload assets folder if it exists
if (Test-Path "$FRONTEND_DIR\assets") {
    gcloud storage cp -r "$FRONTEND_DIR\assets" "gs://$BUCKET_NAME/"
    Write-Success "Assets folder uploaded!"
}

Write-Success "All files uploaded!"

# ── Print Results ─────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           🎉  PDFjin is LIVE on GCP!  🎉         ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  🌐  Your website URL:" -ForegroundColor White
Write-Host "  https://storage.googleapis.com/$BUCKET_NAME/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📦  GCP Console (Project: pdgjin):" -ForegroundColor White
Write-Host "  https://console.cloud.google.com/storage/browser/$BUCKET_NAME?project=pdgjin" -ForegroundColor Cyan
Write-Host ""
Write-Host "  👉  Next step: Run .\deploy\add-custom-domain.ps1" -ForegroundColor Yellow
Write-Host "      to set up your custom domain + HTTPS + CDN" -ForegroundColor Yellow
Write-Host ""
