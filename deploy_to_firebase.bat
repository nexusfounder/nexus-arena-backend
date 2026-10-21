@echo off
title Nexus Gaming Arena - Google Firebase 1-Click Uploader
cd /d "%~dp0"

echo ======================================================================
echo       🎮 NEXUS GAMING ARENA - GOOGLE FIREBASE HOSTING DEPLOYER
echo ======================================================================
echo.
echo  Host your website on Google Cloud's Global Content Delivery Network.
echo  100%% Free Spark Plan - Trusted by Google - Instant Worldwide Access.
echo.
echo ======================================================================
echo.

:: Refresh PATH from Registry to detect Node & Firebase
set "PATH=%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SystemRoot%\System32\WindowsPowerShell\v1.0\;C:\Program Files\nodejs\;%APPDATA%\npm;%PATH%"

:: Always synchronize and prepare latest dist folder
python -c "import shutil, pathlib; d=pathlib.Path('dist'); d.mkdir(exist_ok=True); (d/'static'/'css').mkdir(parents=True, exist_ok=True); (d/'static'/'js').mkdir(parents=True, exist_ok=True); shutil.copy('nexus_gaming_arena.html', d/'index.html'); [shutil.copy(f, d/'static'/'css'/f.name) for f in pathlib.Path('static/css').glob('*.*')]; [shutil.copy(f, d/'static'/'js'/f.name) for f in pathlib.Path('static/js').glob('*.*')]; shutil.copy('static/manifest.json', d/'static/manifest.json')"
echo [✓] Production dist folder synchronized and ready!

:: Step 1: Firebase Login Check
echo [*] Checking Google Firebase Authentication...
call firebase.cmd login --interactive
if %errorlevel% neq 0 (
    echo.
    echo [!] Login failed or cancelled. Please re-run to log in with your Google Account.
    pause
    exit /b %errorlevel%
)

:: Step 2: Ensure Firebase Project
if not exist ".firebaserc" (
    echo.
    echo ----------------------------------------------------------------------
    echo  Please enter your Google Firebase Project ID:
    echo  (You can find or create this at https://console.firebase.google.com)
    echo ----------------------------------------------------------------------
    set /p FIREBASE_PID="Project ID (e.g. nexus-gaming-arena-12345): "
    if not "%FIREBASE_PID%"=="" (
        echo {"projects": {"default": "%FIREBASE_PID%"}} > .firebaserc
    )
)

:: Step 3: Deploy to Google Firebase Hosting
echo.
echo [*] Uploading website assets to Google Firebase CDN...
call firebase.cmd deploy --only hosting

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo   🎉 SUCCESS! YOUR WEBSITE IS LIVE ON GOOGLE FIREBASE!
    echo ======================================================================
    echo.
    echo Opening your live website in browser...
    call firebase.cmd open hosting:site
) else (
    echo.
    echo [!] Deployment encountered an issue. Check the message above.
)

pause
