@echo off
title NexusArena Esports Platform - Wolfy's Ultimate Gaming Arena
cd /d "%~dp0"

echo ======================================================================
echo         NEXUS ARENA - WOLFY'S ULTIMATE GAMING PLATFORM V2.0
echo ======================================================================
echo.
echo  [*] High-Performance Asynchronous Python FastAPI Backend
echo  [*] Double-Entry Bookkeeping Ledger with UUID Idempotency Keys
echo  [*] RFC 6238 TOTP 2FA (Google Authenticator / Authy) QR Generator
echo  [*] Real-time WebSockets Live Bracket, Matches and Dispute Freeze
echo  [*] Responsive Cyberpunk Esports UI with Orbitron & Inter Typography
echo.
echo  Starting server at http://127.0.0.1:8088 ...
echo.
echo  [+] Admin Account:   Username: Wolfy            Password: password123 (₹50,000 Balance - Admin Ops)
echo  [+] Player Account:  Username: PlayerPro        Password: password123 (₹5,000 Balance)
echo ======================================================================
echo.

start "" "http://127.0.0.1:8088"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8088

pause
