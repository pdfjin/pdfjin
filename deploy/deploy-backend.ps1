# PDFjin Backend Deploy
$PROJECT_ID = "pdgjin"
$SERVICE_NAME = "pdfjin-api"
$REGION = "us-central1"

Write-Host "--- Step 1: Initialize Environment ---" -ForegroundColor Cyan
# Skipping config set as we pass --project explicitly below

Write-Host "--- Step 2: Enable APIs ---" -ForegroundColor Cyan
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com --project "pdgjin"


Write-Host "--- Step 3: Deploying (3-5 mins) ---" -ForegroundColor Cyan
$backendPath = "c:\Users\ADMIN\Desktop\pdfjin\backend"
Push-Location $backendPath

# Note: Hardcoded strings to avoid shell variable interpolation errors
# Note: Hardcoded strings to avoid shell variable interpolation errors
gcloud run deploy "pdfjin-api" --source . --region "us-central1" --allow-unauthenticated --memory 2Gi --cpu 2 --timeout 300 --set-env-vars "GEMINI_API_KEY=AIzaSyAN270KrgKkQTtllZGpN-cj1fwFx70Lkv8,DEEPSEEK_API_KEY=sk-8626db807cec4371886ad8aca2c23bd6,STRIPE_SECRET_KEY=sk_test_51T3LvbP066RC8oslMUv3KUzyeWXQYLx3I9DgDv1gJ569vudaYX8Fcz0wWu8nvrwRh24Z2HNheIlksg7qxHSBsKqz00U5Mbuz10,STRIPE_WEBHOOK_SECRET=whsec_yVXQECtHlDXf1oCvlTRkk3POfuRA3Usk,STRIPE_PRICE_PRO_MONTHLY=price_1T6yYrP066RC8osljQNlxCcV,STRIPE_PRICE_PRO_YEARLY=price_1T6yYrP066RC8osljQNlxCcV" --project "pdgjin" --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Backend is live!" -ForegroundColor Green
    gcloud run services describe "pdfjin-api" --region "us-central1" --format "value(status.url)"
}
else {
    Write-Host "FAILED: Check errors above." -ForegroundColor Red
}

Pop-Location

