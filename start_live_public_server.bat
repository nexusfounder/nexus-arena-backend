@echo off
title Nexus Gaming Arena - 100%% Free Public Cloud Server (No Credit Card)
cd /d "%~dp0"

echo ======================================================================
echo       🎮 NEXUS GAMING ARENA - 100%% FREE PUBLIC SERVER LAUNCHER
echo ======================================================================
echo.
echo  [*] NO CREDIT CARD NEEDED
echo  [*] 100%% Free Cloudflare HTTPS Public Tunnel
echo  [*] Live FastAPI Backend + Double-Entry Ledger + Supabase Cloud DB
echo.
echo ======================================================================
echo.

:: 1. Download cloudflared if not present (Free lightweight single executable)
if not exist "cloudflared.exe" (
    echo [*] Downloading free Cloudflare Tunnel executable (one-time setup)...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe', 'cloudflared.exe')"
    if exist "cloudflared.exe" (
        echo [✓] Cloudflare Tunnel downloaded successfully!
    ) else (
        echo [!] Could not download cloudflared. Running local server only.
    )
)

:: 2. Start Python FastAPI Server in background
echo [*] Starting Python FastAPI Backend on port 8088...
start "Nexus FastAPI Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8088"

:: Wait 3 seconds for server to boot
timeout /t 3 /nobreak >nul

:: 3. Launch Cloudflare Tunnel
if exist "cloudflared.exe" (
    echo.
    echo ======================================================================
    echo  🚀 GENERATING YOUR LIVE WORLDWIDE HTTPS URL...
    echo  Look for the link below ending in ".trycloudflare.com":
    echo ======================================================================
    echo.
    cloudflared.exe tunnel --url http://127.0.0.1:8088
) else (
    echo [*] Server is live locally at http://127.0.0.1:8088
    pause
)
