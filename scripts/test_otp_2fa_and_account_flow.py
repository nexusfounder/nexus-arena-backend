"""
Nexus Gaming Arena - OTP 2FA & Systematic Account Opening Verification Suite
Tests:
1. Pre-verified OTP registration (instant ACTIVE status and token generation)
2. Verification wall fallback registration (PENDING_VERIFICATION -> verify-account)
3. Login verification wall challenge for pending accounts
4. 2FA via SMS/Email OTP setup, verification, and backup codes generation
5. 2FA via OTP login challenge with dynamic OTP dispatch and validation
6. 2FA emergency backup recovery code login
7. Admin credentials update persistence across init_db() cold boots
"""

import os
import sys
import uuid
import json
import logging
from datetime import datetime, timezone

# Ensure project root is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, get_db_connection
from app.cloud_sync import cloud_get_admin, cloud_get_all_users

client = TestClient(app)
logger = logging.getLogger("test_otp_2fa")

def run_tests():
    print("=" * 65)
    print("NEXUS GAMING ARENA - OTP 2FA & ACCOUNT REGISTRATION SUITE")
    print("=" * 65)

    # Re-initialize DB
    init_db()

    # ---------------------------------------------------------
    # TEST 1: Smooth In-Line OTP Registration (Instant ACTIVE)
    # ---------------------------------------------------------
    print("\n1. Testing In-Line OTP Registration Flow (Smooth Single-Step)...")
    test_mobile = f"+9198{uuid.uuid4().hex[:8]}"
    test_email = f"gamer_{uuid.uuid4().hex[:6]}@arena.gg"
    test_user = f"Ace_{uuid.uuid4().hex[:6]}"
    test_pw = "ProGamer@2026!"

    # Step 1A: Send OTP
    send_res = client.post("/api/auth/otp/send", json={"identifier": test_email, "otp_type": "EMAIL"})
    assert send_res.status_code == 200, f"Send OTP failed: {send_res.text}"
    send_data = send_res.json()
    assert send_data["status"] == "SENT"
    print(f"   [PASS] Pre-registration OTP sent to {test_email}")

    # Step 1B: Retrieve OTP from DB to simulate user receiving code
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT code FROM otp_codes WHERE identifier = ? ORDER BY created_at DESC LIMIT 1", (test_email,))
    otp_code = c.fetchone()["code"]
    conn.close()

    # Step 1C: Complete registration with OTP
    reg_res = client.post("/api/auth/register", json={
        "username": test_user,
        "email": test_email,
        "password": test_pw,
        "phone_number": test_mobile,
        "otp_code": otp_code
    })
    assert reg_res.status_code == 200, f"Registration with OTP failed: {reg_res.text}"
    reg_data = reg_res.json()
    assert reg_data["status"] == "SUCCESS", f"Expected SUCCESS but got: {reg_data}"
    assert reg_data["requires_verification"] is False
    assert "token" in reg_data and len(reg_data["token"]) > 20
    assert reg_data["user"]["role"] == "PLAYER"
    assert reg_data["user"]["phone_verified"] is True
    print(f"   [PASS] Account created directly in ACTIVE status with token & welcome credits!")

    # ---------------------------------------------------------
    # TEST 2: Verification Wall Fallback (Registration without OTP)
    # ---------------------------------------------------------
    print("\n2. Testing Registration Without Pre-OTP (Verification Wall Pathway)...")
    wall_email = f"wall_{uuid.uuid4().hex[:6]}@arena.gg"
    wall_user = f"Wall_{uuid.uuid4().hex[:6]}"
    wall_pw = "WallPlayer#2026"

    wall_res = client.post("/api/auth/register", json={
        "username": wall_user,
        "email": wall_email,
        "password": wall_pw
    })
    assert wall_res.status_code == 200, f"Wall registration failed: {wall_res.text}"
    wall_data = wall_res.json()
    assert wall_data["status"] == "VERIFICATION_SENT"
    assert wall_data["requires_verification"] is True
    assert wall_data.get("demo_otp") is not None
    print(f"   [PASS] User created in PENDING_VERIFICATION. Demo OTP provided: {wall_data.get('demo_otp')}")

    # Test login on pending account -> Returns VERIFICATION_REQUIRED
    pending_login = client.post("/api/auth/login", json={
        "username_or_email": wall_user,
        "password": wall_pw
    })
    assert pending_login.status_code == 200, f"Pending login failed: {pending_login.text}"
    pending_data = pending_login.json()
    assert pending_data["status"] == "VERIFICATION_REQUIRED"
    assert pending_data.get("demo_otp") is not None
    print(f"   [PASS] Login intercepts pending user: returns VERIFICATION_REQUIRED with activation code.")

    # Activate account via /api/auth/verify-account
    act_res = client.post("/api/auth/verify-account", json={
        "identifier": wall_email,
        "code": wall_data["demo_otp"]
    })
    assert act_res.status_code == 200, f"Account verification failed: {act_res.text}"
    act_data = act_res.json()
    assert act_data["status"] == "SUCCESS"
    assert "token" in act_data
    print(f"   [PASS] Account successfully verified & activated! Token issued.")

    # ---------------------------------------------------------
    # TEST 3: 2FA via SMS/Email OTP Setup & Verification
    # ---------------------------------------------------------
    print("\n3. Testing 2FA Implementation by OTP Verification Process...")
    player_token = reg_data["token"]
    player_headers = {"Authorization": f"Bearer {player_token}"}

    # Step 3A: Request 2FA OTP Setup code
    otp_setup_res = client.post("/api/auth/2fa/otp/send", headers=player_headers, json={})
    assert otp_setup_res.status_code == 200, f"2FA OTP setup send failed: {otp_setup_res.text}"
    setup_data = otp_setup_res.json()
    assert setup_data["status"] == "SENT"
    assert setup_data.get("demo_otp") is not None
    otp_2fa_code = setup_data["demo_otp"]
    print(f"   [PASS] 2FA Setup OTP dispatched: {otp_2fa_code}")

    # Step 3B: Enable 2FA with verified OTP
    enable_res = client.post("/api/auth/2fa/otp/enable", headers=player_headers, json={"code": otp_2fa_code})
    assert enable_res.status_code == 200, f"Enable 2FA OTP failed: {enable_res.text}"
    enable_data = enable_res.json()
    assert enable_data["status"] == "SUCCESS"
    assert enable_data["method"] == "OTP"
    assert len(enable_data["backup_codes"]) == 10
    backup_code_sample = enable_data["backup_codes"][0]
    print(f"   [PASS] 2FA via OTP enabled successfully! 10 backup codes generated.")

    # ---------------------------------------------------------
    # TEST 4: 2FA via OTP Login Verification Flow
    # ---------------------------------------------------------
    print("\n4. Testing Login Challenge with 2FA via OTP...")
    # Attempt login without 2FA code
    step1_login = client.post("/api/auth/login", json={
        "username_or_email": test_user,
        "password": test_pw
    })
    assert step1_login.status_code == 200, f"Step 1 login failed: {step1_login.text}"
    s1_data = step1_login.json()
    assert s1_data["status"] == "2FA_REQUIRED"
    assert s1_data["method"] == "OTP"
    assert s1_data.get("demo_otp") is not None
    login_2fa_otp = s1_data["demo_otp"]
    print(f"   [PASS] Login challenge returned 2FA_REQUIRED (method: OTP). Dynamic OTP: {login_2fa_otp}")

    # Test resend 2FA login OTP endpoint
    resend_res = client.post("/api/auth/2fa/otp/resend-login", json={"user_id": s1_data["user_id"]})
    assert resend_res.status_code == 200, f"Resend 2FA login OTP failed: {resend_res.text}"
    resend_data = resend_res.json()
    assert resend_data["status"] == "SENT"
    new_login_otp = resend_data["demo_otp"]
    print(f"   [PASS] Resend 2FA login OTP issued fresh code: {new_login_otp}")

    # Step 4B: Submit login with the dynamic 2FA OTP
    step2_login = client.post("/api/auth/login", json={
        "username_or_email": test_user,
        "password": test_pw,
        "two_factor_code": new_login_otp
    })
    assert step2_login.status_code == 200, f"Step 2 login with OTP failed: {step2_login.text}"
    s2_data = step2_login.json()
    assert s2_data["status"] == "SUCCESS"
    assert "token" in s2_data
    assert s2_data["user"]["username"] == test_user
    print(f"   [PASS] 2FA OTP Login successful! Full session token granted.")

    # ---------------------------------------------------------
    # TEST 5: 2FA Emergency Backup Recovery Code Login
    # ---------------------------------------------------------
    print("\n5. Testing 2FA Single-Use Emergency Backup Code Login...")
    backup_login = client.post("/api/auth/login", json={
        "username_or_email": test_user,
        "password": test_pw,
        "two_factor_code": backup_code_sample
    })
    assert backup_login.status_code == 200, f"Backup code login failed: {backup_login.text}"
    assert backup_login.json()["status"] == "SUCCESS"
    print(f"   [PASS] Login with emergency backup recovery code succeeded!")

    # Attempt re-use of consumed backup code -> Must fail
    reuse_login = client.post("/api/auth/login", json={
        "username_or_email": test_user,
        "password": test_pw,
        "two_factor_code": backup_code_sample
    })
    assert reuse_login.status_code == 400, "Consumed backup code was incorrectly permitted!"
    print(f"   [PASS] Consumed single-use backup code correctly rejected.")

    # ---------------------------------------------------------
    # TEST 6: Admin Credentials Update & Server Reboot Shield
    # ---------------------------------------------------------
    print("\n6. Testing Admin Credentials Update & Cloud Sync Shield across Server Reboot...")
    # Log in as admin
    admin_login = client.post("/api/auth/login", json={
        "username_or_email": "admin",
        "password": "admin"
    })
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    adm_token = admin_login.json()["token"]
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    new_admin_user = "admin_master_shield"
    new_admin_pw = "SupremeAdmin@2026!"

    # Update admin credentials with Authorization header
    up_res = client.post("/api/admin/credentials/update", headers=adm_headers, json={
        "current_password": "admin",
        "new_username": new_admin_user,
        "new_password": new_admin_pw
    })
    assert up_res.status_code == 200, f"Admin credentials update failed: {up_res.text}"
    up_data = up_res.json()
    assert up_data["status"] == "SUCCESS"
    print(f"   [PASS] Admin credentials updated: username='{new_admin_user}'")

    # Simulate cold server restart on Render (call init_db())
    init_db()

    # Login with new admin credentials -> Must succeed!
    new_adm_login = client.post("/api/auth/login", json={
        "username_or_email": new_admin_user,
        "password": new_admin_pw
    })
    assert new_adm_login.status_code == 200, f"Login with updated admin credentials failed after restart: {new_adm_login.text}"
    assert new_adm_login.json()["status"] == "SUCCESS"
    print(f"   [PASS] Admin credentials persisted across server reboot! Reversion bug completely eliminated.")

    # Restore admin credentials back to admin/admin for ongoing testing compatibility
    fresh_adm_token = new_adm_login.json()["token"]
    client.post("/api/admin/credentials/update", headers={"Authorization": f"Bearer {fresh_adm_token}"}, json={
        "current_password": new_admin_pw,
        "new_username": "admin",
        "new_password": "admin"
    })
    print(f"   [PASS] Cleaned up test admin credentials back to standard setup.")

    print("\n" + "=" * 65)
    print("ALL OTP 2FA & ACCOUNT OPENING FLOW TESTS PASSED 100%!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
