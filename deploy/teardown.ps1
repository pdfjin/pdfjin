# ============================================================
#  PDFjin — Tear Down / Delete All GCP Resources
#  Use this to clean up if you want to start fresh
#  Usage: .\deploy\teardown.ps1
# ============================================================

$BUCKET_NAME = "pdfjin.com"
gcloud config set project pdgjin --quiet   # Ensure correct project is active

Write-Host ""
Write-Host "⚠️  WARNING: This will delete ALL GCP resources for PDFjin!" -ForegroundColor Red
$confirm = Read-Host "Type 'DELETE' to confirm"
if ($confirm -ne "DELETE") { Write-Host "Cancelled." -ForegroundColor Yellow; exit 0 }

Write-Host ""
Write-Host "🗑️  Deleting resources..." -ForegroundColor Cyan

# Delete Load Balancer components (if created)
gcloud compute forwarding-rules delete pdgjin-https-fwd --global --quiet 2>$null
gcloud compute forwarding-rules delete pdgjin-http-fwd  --global --quiet 2>$null
gcloud compute target-https-proxies delete pdgjin-https-proxy --global --quiet 2>$null
gcloud compute target-http-proxies  delete pdgjin-http-proxy  --global --quiet 2>$null
gcloud compute ssl-certificates delete pdgjin-ssl-cert --global --quiet 2>$null
gcloud compute url-maps delete pdgjin-url-map      --global --quiet 2>$null
gcloud compute url-maps delete pdgjin-http-redirect --global --quiet 2>$null
gcloud compute backend-buckets delete pdgjin-backend --quiet 2>$null

# Delete bucket and all files
gcloud storage rm -r "gs://$BUCKET_NAME" --quiet 2>$null

Write-Host "✅ All GCP resources deleted." -ForegroundColor Green
