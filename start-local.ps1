# ============================================================
# PDFjin - One-Click LOCAL Development Starter
# Run this to start the backend + open the frontend locally.
# ============================================================

$ErrorActionPreference = "Stop"
$BackendDir = "$PSScriptRoot\backend"
$FrontendIndex = "$PSScriptRoot\frontend\index.html"
$Port = 8080

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PDFjin Local Dev Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Install requirements if needed
Write-Host ""
Write-Host "[SETUP] Installing/checking backend requirements..." -ForegroundColor Yellow
Push-Location $BackendDir
pip install -r requirements.txt -q
Pop-Location

# Kill any process already using port 8080
$existing = netstat -aon | Select-String ":$Port " | Select-String "LISTENING"
if ($existing) {
    $pid = ($existing -split '\s+')[-1]
    Write-Host "[CLEANUP] Killing existing process on port $Port (PID: $pid)..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Start backend server in a new PowerShell window
Write-Host ""
Write-Host "[START] Launching backend on http://localhost:$Port ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; python -m uvicorn app:app --host 0.0.0.0 --port $Port --reload"

# Wait for backend to be ready
Write-Host "[WAIT] Waiting for backend to come online..." -ForegroundColor Yellow
$maxWait = 20
$waited = 0
do {
    Start-Sleep -Seconds 1
    $waited++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Backend is online!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "   ... still starting ($waited/$maxWait)" -ForegroundColor DarkGray
    }
} while ($waited -lt $maxWait)

# Open frontend in browser
Write-Host ""
Write-Host "[OPEN] Opening frontend in browser..." -ForegroundColor Green
Start-Process $FrontendIndex

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PDFjin is running!" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:$Port" -ForegroundColor White
Write-Host "  Frontend: $FrontendIndex" -ForegroundColor White
Write-Host ""
Write-Host "  Close the backend PowerShell window to stop." -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor Cyan
