# VidyaMitra Windows Quick Start
# Run with: powershell -ExecutionPolicy Bypass -File .\start.ps1

Write-Host "VidyaMitra -- The Renaissance Edition" -ForegroundColor Cyan
Write-Host "-----------------------------------------"

$py = ""
foreach ($cmd in @("python", "py", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $py = $cmd
        break
    }
}

if ($py -eq "") {
    Write-Host "Error: Python not found." -ForegroundColor Red
    exit
}

Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location backend

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $py -m venv venv
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install -r requirements.txt --quiet

Write-Host "Backend ready" -ForegroundColor Green

# Use the virtual environment's python to run uvicorn
$venvPy = ".\venv\Scripts\python.exe"
Write-Host "Starting Backend on http://localhost:8000" -ForegroundColor Green
$backendProcess = Start-Process $venvPy -ArgumentList "-m uvicorn app.main:app --reload --port 8000" -PassThru -NoNewWindow

Set-Location ../frontend
Write-Host "Starting Frontend on http://localhost:3000" -ForegroundColor Green
$frontendProcess = Start-Process $py -ArgumentList "-m http.server 3000" -PassThru -NoNewWindow

Write-Host "VidyaMitra is running!" -ForegroundColor Green
Write-Host "Press any key to stop..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "Stopping servers..." -ForegroundColor Yellow
Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
Write-Host "Stopped."
