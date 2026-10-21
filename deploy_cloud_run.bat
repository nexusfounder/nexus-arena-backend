@echo off
title Nexus Gaming Arena - Google Cloud Run 1-Click Deployer
cd /d "%~dp0"

echo ======================================================================
echo       🎮 NEXUS GAMING ARENA - GOOGLE CLOUD RUN BACKEND DEPLOYER
echo ======================================================================
echo.
echo  Deploys the Python FastAPI Backend & Double-Entry Ledger Server
echo  to Google Cloud Run (Mumbai Region: asia-south1).
echo.
echo  Project ID: nexus-gaming-arena-28be9
echo ======================================================================
echo.

:: Check gcloud CLI
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Google Cloud SDK (gcloud) is not detected in your PATH.
    echo.
    echo To deploy automatically from this machine, please install the Google Cloud CLI from:
    echo https://cloud.google.com/sdk/docs/install
    echo.
    echo Alternatively, you can deploy via Google Cloud Console:
    echo 1. Open https://console.cloud.google.com/run?project=nexus-gaming-arena-28be9
    echo 2. Click "Create Service" -> "Deploy from source repository"
    echo.
    pause
    exit /b 1
)

echo [*] Setting active project to nexus-gaming-arena-28be9...
call gcloud config set project nexus-gaming-arena-28be9

echo.
echo [*] Submitting build to Google Cloud Build and deploying to Cloud Run...
call gcloud builds submit --config=cloudbuild.yaml .

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo   🎉 SUCCESS! BACKEND SERVER IS LIVE ON GOOGLE CLOUD RUN!
    echo ======================================================================
    echo.
    call gcloud run services describe nexus-arena-backend --region=asia-south1 --format="value(status.url)"
) else (
    echo.
    echo [!] Cloud Run deployment encountered an issue. See log details above.
)

pause
