$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
# jobspy pins broken numpy on Py3.13 — reassert compatible wheels
.\.venv\Scripts\pip.exe install "python-jobspy==1.1.82" --no-deps
.\.venv\Scripts\pip.exe install "numpy>=2.1,<2.3" "pandas>=2.2,<3" "markdownify>=0.13.1,<0.14" "regex>=2024.4.28,<2025" tls-client requests beautifulsoup4 pydantic
.\.venv\Scripts\python.exe -m playwright install chromium

Write-Host "Done. Activate with: .\.venv\Scripts\Activate.ps1"
Write-Host "Smoke test:   .\.venv\Scripts\python.exe -m scripts.smoke_scrape"
