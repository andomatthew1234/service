# ====================================================================
#               SETUP SCRIPT FOR WINDEPOT/TLA/OTHER APPLICATIONS   
# ====================================================================
$ErrorActionPreference = "Stop"

# Define Target Locations (Explicitly bypassing OneDrive for immediate local boot)
$localDocs = Join-Path $env:USERPROFILE "Documents"
$srvcFolder = Join-Path $localDocs "SRVC"

$batFilePath = Join-Path $srvcFolder "run_agent.bat"
$vbsFilePath = Join-Path $srvcFolder "silent_run.vbs"
$startupFolder = [Environment]::GetFolderPath("Startup")
$startupShortcut = Join-Path $startupFolder "SRVC_Agent.lnk"

Write-Host "=== Starting SRVC Installation Deployment ===" -ForegroundColor Cyan

# --------------------------------------------------------------------
# 1/3 - INSTALLING DEPENDENCIES
# --------------------------------------------------------------------
Write-Host "[1/5] Verifying Python installation status..." -ForegroundColor Yellow

$pythonInstalled = $false
try {
    $null = python --version
    $pythonInstalled = $true
    Write-Host "-> Python is already installed on this machine." -ForegroundColor Green
} catch {
    Write-Host "-> Python not found. Initiating deployment via Winget..." -ForegroundColor Blue
    Start-Process winget -ArgumentList "install --id Python.Python.3.12 --silent --exact" -NoNewWindow -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "-> Python installation sequence completed successfully." -ForegroundColor Green
}

# Install Required Dependencies (Now includes pystray and pillow for the Taskbar Icon)
Write-Host "-> Verifying package prerequisites..." -ForegroundColor Blue
Start-Process python -ArgumentList "-m pip install --user requests urllib3 pystray pillow" -NoNewWindow -Wait
Write-Host "-> Dependencies successfully verified." -ForegroundColor Green

# --------------------------------------------------------------------
# 2/3 - INSTALLING APPLICATION
# --------------------------------------------------------------------
Write-Host "[2/5] Structuring storage volumes..." -ForegroundColor Yellow
if (-not (Test-Path $srvcFolder)) {
    New-Item -ItemType Directory -Path $srvcFolder -Force | Out-Null
    Write-Host "-> Target structure created locally at: $srvcFolder" -ForegroundColor Green
} else {
    Write-Host "-> Target structure already exists at: $srvcFolder" -ForegroundColor Green
}

Write-Host "[3/5] Fetching production asset 'app.py' from repository..." -ForegroundColor Yellow
$sourceUrl = "https://raw.githubusercontent.com/andomatthew1234/service/main/app.py"
$targetScriptPath = Join-Path $srvcFolder "app.py"

$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($sourceUrl, $targetScriptPath)
Write-Host "-> Successfully deployed app.py to local filesystem array." -ForegroundColor Green

# --------------------------------------------------------------------
# 2/3B - PREPARING EXECUTION 
# --------------------------------------------------------------------
Write-Host "[4/5] Constructing execution layer scripts..." -ForegroundColor Yellow

$batContent = "@echo off`ncd /d `"$srvcFolder`"`npython app.py"
Set-Content -Path $batFilePath -Value $batContent

$vbsContent = "Set WshShell = CreateObject(`"WScript.Shell`")`nWshShell.Run `"$batFilePath`", 0, False"
Set-Content -Path $vbsFilePath -Value $vbsContent
Write-Host "-> Automation scripts compiled successfully." -ForegroundColor Green

Write-Host "[5/5] Integrating service with Windows Startup subsystem..." -ForegroundColor Yellow

# Clear any old shortcuts that might be pointing to the wrong drive
if (Test-Path $startupShortcut) {
    Remove-Item $startupShortcut -Force
}

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($startupShortcut)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$vbsFilePath`""
$shortcut.WorkingDirectory = $srvcFolder
$shortcut.WindowStyle = 7 
$shortcut.Save()

Write-Host "-> Active link deployed to global Startup cluster." -ForegroundColor Green

# --------------------------------------------------------------------
# 3/3 - FINALIZAING INSTALLATION
# --------------------------------------------------------------------
Write-Host "`n=== Installation Finalized Successfully ===" -ForegroundColor Green
Write-Host "Spawning background listener process now..." -ForegroundColor Blue

# Triggering the initial launch so the tray icon appears immediately
Start-Process wscript.exe -ArgumentList "`"$vbsFilePath`""

Write-Host "Installation completed - you can now use the application." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Exit