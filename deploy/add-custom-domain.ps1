# ============================================================
#  PDFjin - Add Custom Domain + HTTPS + CDN
#  Updated for pdfjin.com
# ============================================================

$DOMAIN = "www.pdfjin.com"
$ROOT_DOMAIN = "pdfjin.com"
$BUCKET_NAME = "pdfjin.com"

function Write-Step($msg) { Write-Host "`n-- $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "  [INFO] $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "Setting up Custom Domain for: $DOMAIN and $ROOT_DOMAIN" -ForegroundColor Cyan

# 1. Backend Bucket
Write-Step "1. Creating CDN-enabled backend bucket..."
gcloud compute backend-buckets create pdgjin-backend `
    --gcs-bucket-name=$BUCKET_NAME `
    --enable-cdn `
    --compression-mode=AUTOMATIC --quiet
Write-Success "CDN backend created!"

# 2. URL Map
Write-Step "2. Creating URL map..."
gcloud compute url-maps create pdgjin-url-map `
    --default-backend-bucket=pdgjin-backend --quiet
Write-Success "URL map created!"

# 3. SSL Certificate
Write-Step "3. Creating managed SSL certificate..."
gcloud compute ssl-certificates create pdgjin-ssl-cert `
    --domains="$DOMAIN,$ROOT_DOMAIN" `
    --global --quiet
Write-Success "SSL certificate created!"

# 4. HTTPS Proxy
Write-Step "4. Creating HTTPS target proxy..."
gcloud compute target-https-proxies create pdgjin-https-proxy `
    --url-map=pdgjin-url-map `
    --ssl-certificates=pdgjin-ssl-cert `
    --global --quiet
Write-Success "HTTPS proxy created!"

# 5. HTTP Redirect
Write-Step "5. Setting up HTTP redirect..."
gcloud compute url-maps create pdgjin-http-redirect `
    --default-redirect-response-code=301 `
    --redirect-response-code=MOVED_PERMANENTLY_DEFAULT --quiet

gcloud compute target-http-proxies create pdgjin-http-proxy `
    --url-map=pdgjin-http-redirect --quiet
Write-Success "HTTP redirect configured!"

# 6. Forwarding Rules
Write-Step "6. Creating global forwarding rules..."
gcloud compute forwarding-rules create pdgjin-https-fwd `
    --global `
    --target-https-proxy=pdgjin-https-proxy `
    --ports=443 --quiet

gcloud compute forwarding-rules create pdgjin-http-fwd `
    --global `
    --target-http-proxy=pdgjin-http-proxy `
    --ports=80 --quiet
Write-Success "Forwarding rules created!"

# 7. Get IP
Write-Step "7. Getting your public IP address..."
$IP = gcloud compute forwarding-rules describe pdgjin-https-fwd `
    --global `
    --format="value(IPAddress)"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "         LB + CDN IS READY" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  IP Address: $IP" -ForegroundColor White
Write-Host ""
Write-Host "  Add these A Records to your DNS:" -ForegroundColor Yellow
Write-Host "  1. Type: A | Name: @   | Value: $IP" -ForegroundColor Cyan
Write-Host "  2. Type: A | Name: www | Value: $IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "  SSL certificate will activate within 60 minutes."
Write-Host ""
