#!/usr/bin/env bash
# ==============================================================================
# NEXUS GAMING ARENA - OS-LEVEL ACCESS ISOLATION & UFW FIREWALL HARDENING
# Mandated by RBI Cyber Security Framework for Payment Systems
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo "Initializing RBI & CERT-In Compliant UFW Perimeter Defense"
echo "=========================================================="

# Check root privileges
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (sudo ./setup_ufw_firewall.sh)"
  exit 1
fi

# Ensure UFW is installed
if ! command -v ufw >/dev/null 2>&1; then
    echo "[+] Installing ufw package..."
    apt-get update && apt-get install -y ufw
fi

# 1. Reset rules to clean baseline
echo "[+] Resetting UFW to pristine baseline..."
ufw --force reset

# 2. Default Policies: Drop all incoming, permit outgoing
echo "[+] Setting default policies: DENY INCOMING, ALLOW OUTGOING..."
ufw default deny incoming
ufw default allow outgoing

# 3. Secure SSH with Brute-Force Rate Limiting (Protects port 22)
echo "[+] Enabling rate-limited SSH (Mitigates brute-force credential stuffing)..."
ufw limit 22/tcp comment 'SSH Rate Limited'

# 4. Allow Standard Web Traffic (HTTP 80 -> 443 Redirect, HTTPS 443 TLS 1.3)
echo "[+] Permitting inbound HTTP (80) and HTTPS (443)..."
ufw allow 80/tcp comment 'HTTP (Redirects to TLS 1.3)'
ufw allow 443/tcp comment 'HTTPS (Strict TLS 1.3 Only)'

# 5. Strictly Isolate Internal Services (Block outside access to DB and Redis)
echo "[+] Enforcing internal access isolation for backend application & databases..."
# Block any external connections to port 8088 (accessible only via localhost / reverse proxy)
ufw deny 8088/tcp comment 'Nexus Backend Direct Port (Localhost Only)'

# 6. Enable High-Audit Logging for CERT-In / RBI Incident Monitoring
echo "[+] Enabling UFW Medium Audit Logging for SIEM & CERT-In Compliance..."
ufw logging medium

# 7. Enable Firewall
echo "[+] Activating UFW firewall..."
ufw --force enable

echo "=========================================================="
echo "UFW Firewall Successfully Hardened for RBI PA Compliance!"
echo "Status Summary:"
ufw status verbose
echo "=========================================================="
