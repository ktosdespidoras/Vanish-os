# Vanish-OS — Windows One-Click Builder via WSL2
# No VirtualBox or VMware required.
$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "     VANISH-OS BUILD AUTOMATION (WSL2)      " -ForegroundColor Magenta
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Check WSL Status
Write-Host "`n[1/3] Checking WSL2 Environment..." -ForegroundColor Yellow
$wslCheck = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] WSL is not active. Installing WSL Ubuntu now (one-time setup)..." -ForegroundColor Yellow
    wsl --install -d Ubuntu --no-launch
    Write-Host "[+] WSL installed. Please reboot your PC if prompted, then re-run this script." -ForegroundColor Green
    Exit
} else {
    Write-Host "[✓] WSL2 is ready." -ForegroundColor Green
}

# 2. Translate Windows path to WSL path
$projectDir = (Get-Item -Path "..\").FullName
$wslProjectDir = "/mnt/" + $projectDir.Substring(0,1).ToLower() + $projectDir.Substring(2).Replace("\", "/")
Write-Host "[2/3] Project path mapped: $wslProjectDir" -ForegroundColor Cyan

# 3. Execution Options
Write-Host "`n[3/3] Ready to build Vanish-OS ISO!" -ForegroundColor Green
Write-Host "Option A (Recommended): Launch WSL bash to run the build" -ForegroundColor White
Write-Host "Option B: Run GUI installer locally on Windows to test UI before build" -ForegroundColor White

Write-Host "`nCommands:" -ForegroundColor Yellow
Write-Host "  To test installer GUI on Windows:" -ForegroundColor Gray
Write-Host "    python ..\installer\main.py" -ForegroundColor White
Write-Host "`n  To build ISO in WSL:" -ForegroundColor Gray
Write-Host "    wsl -u root bash -c `"cd '$wslProjectDir/build' && chmod +x build_iso.sh && ./build_iso.sh`"" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor Cyan
