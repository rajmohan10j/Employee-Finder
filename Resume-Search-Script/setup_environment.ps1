# ==============================================================================
# Automated Environment Installer for Resume Tool
# ==============================================================================

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "   Setting Up Dependencies for Resume Auto-Fetcher       " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Check if Python is installed; if not, install via Winget
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "`n[1/3] Python not found. Installing Python 3.12 via Winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements

    # Refresh PATH environment variable for the current PowerShell session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "`n[1/3] Python is already installed." -ForegroundColor Green
}

# Verify Python access
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "      Detected:" (python --version) -ForegroundColor Gray

    # 2. Upgrade pip and install required Python packages
    Write-Host "`n[2/3] Installing Python libraries (playwright, google-genai, python-docx, pypdf)..." -ForegroundColor Yellow
    python -m pip install --upgrade pip --quiet
    python -m pip install playwright google-genai python-docx pypdf --quiet

    # 3. Install Playwright browser dependencies (Chromium)
    Write-Host "`n[3/3] Downloading Playwright browser binaries (Chromium)..." -ForegroundColor Yellow
    python -m playwright install chromium

    Write-Host "`n=========================================================" -ForegroundColor Green
    Write-Host "  ✅ ALL INSTALLATIONS COMPLETE!                          " -ForegroundColor Green
    Write-Host "  You are ready to run: python resume_auto_fetcher.py    " -ForegroundColor Green
    Write-Host "=========================================================" -ForegroundColor Green
} else {
    Write-Host "`n❌ Python was installed, but environment paths require a terminal restart." -ForegroundColor Red
    Write-Host "Please close this PowerShell window, open a new one, and run the script again." -ForegroundColor Red
}