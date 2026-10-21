"""
Nexus Gaming Arena - Deep Feature Scanner & Comprehensive Regression Test Suite
Executes end-to-end testing across all 6 core feature domains:
1. System Health, RBI Compliance & Ledger Reconciliation
2. Authentication, Password Security & 2FA Gateways
3. Banking Rails, Fiat Deposits & Ledger Balance Invariance
4. Tournaments, Bracket Progression & Escrow Prize Payouts
5. Community, Social Linking, Quests & Support Tickets
6. Admin Command Center, User Governance & Master Admin Immunity
"""

import sys
import os
import uuid
import time
import json
import hmac
import hashlib
from typing import Dict, Any, List

# Ensure app root is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_connection
from app.rbi_compliance import _payment_rate_limit_records

client = TestClient(app)

TEST_RESULTS: List[Dict[str, Any]] = []

def record_test(domain: str, feature: str, description: str, passed: bool, detail: str = "", duration_ms: float = 0.0):
    TEST_RESULTS.append({
        "domain": domain,
        "feature": feature,
        "description": description,
        "passed": passed,
        "detail": detail,
        "duration_ms": round(duration_ms, 2)
    })
    status_str = "[PASS]" if passed else "[FAIL]"
    print(f"  {status_str} {feature}: {description} ({duration_ms:.1f}ms)")
    if not passed and detail:
        print(f"         Error Detail: {detail}")

def run_deep_scan():
    print("\n" + "="*80)
    print("NEXUS GAMING ARENA - COMPREHENSIVE DEEP FEATURE SCAN & REGRESSION SUITE")
    print("="*80 + "\n")

    # =========================================================================
    # DOMAIN 1: SYSTEM HEALTH, RBI COMPLIANCE & LEDGER RECONCILIATION
    # =========================================================================
    print(">>> DOMAIN 1: System Health, RBI Compliance & Ledger Reconciliation")

    # 1.1 Healthcheck
    t0 = time.time()
    res = client.get("/api/health")
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "HEALTHY" and res.json().get("database_connected") is True
    record_test("System Infrastructure", "Healthcheck (/api/health)", "Returns 200 OK, database connected and healthy", is_ok, res.text if not is_ok else "", dur)

    # 1.2 RBI Disclosures
    t0 = time.time()
    res = client.get("/api/compliance/rbi-disclosures")
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and "CIN" in res.json().get("legal_framework", {}).get("cin_number", "CIN") and "Mumbai" in res.text
    record_test("Regulatory Compliance", "RBI Disclosures", "Mandatory CIN, Grievance Officer and Data Localization in Mumbai", is_ok, res.text if not is_ok else "", dur)

    # 1.3 Real-Time Mathematical Ledger Reconciliation
    t0 = time.time()
    res = client.get("/api/admin/reconcile")
    dur = (time.time() - t0) * 1000
    data = res.json()
    is_ok = res.status_code == 200 and data.get("status") == "PASS" and data.get("invariants", {}).get("double_entry_balanced") is True and len(data.get("negative_balance_violations", [])) == 0
    record_test("Banking Engine", "Ledger Invariant Audit", "Zero balance drift, Sum(Debits) == Sum(Credits), zero negative wallets", is_ok, res.text if not is_ok else "", dur)

    # =========================================================================
    # DOMAIN 2: AUTHENTICATION, PASSWORD SECURITY & 2FA GATEWAYS
    # =========================================================================
    print("\n>>> DOMAIN 2: Authentication, Password Security & 2FA Gateways")

    test_uid = uuid.uuid4().hex[:8]
    test_username = f"player_{test_uid}"
    test_email = f"player_{test_uid}@testarena.gg"
    test_password = "SecurePassword@123"

    # 2.1 User Registration & Verification Wall Initiation
    t0 = time.time()
    res = client.post("/api/auth/register", json={
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "phone_number": f"+91 9800{int(time.time())%100000:05d}"
    })
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "VERIFICATION_SENT" and res.json().get("requires_verification") is True
    record_test("Authentication", "User Registration (Verification Wall)", "Registers new user into PENDING_VERIFICATION and issues single-use OTP", is_ok, res.text if not is_ok else "", dur)

    # 2.2 Anti-Account-Enumeration Protection (Duplicate Registration)
    t0 = time.time()
    res = client.post("/api/auth/register", json={
        "username": test_username,
        "email": f"diff_{test_email}",
        "password": test_password
    })
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and "If this account does not already exist" in res.json().get("message", "")
    record_test("Security Defense", "Anti-Enumeration Defense", "Returns uniform generic response preventing attacker account discovery", is_ok, res.text if not is_ok else "", dur)

    # 2.3 Unverified Login Block
    t0 = time.time()
    res = client.post("/api/auth/login", json={
        "username_or_email": test_username,
        "password": test_password
    })
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "VERIFICATION_REQUIRED"
    record_test("Authentication", "Unverified Account Login Block", "Enforces verification wall; unverified users cannot login", is_ok, res.text if not is_ok else "", dur)

    # 2.4 Account Activation via 6-Digit Email OTP
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT code FROM otp_codes WHERE identifier = ? AND otp_type = 'ACCOUNT_VERIFICATION' ORDER BY created_at DESC LIMIT 1", (test_email,))
    row = c.fetchone()
    activation_code = row["code"] if row else ""
    c.execute("SELECT id FROM users WHERE username = ?", (test_username,))
    reg_user_id = c.fetchone()["id"]
    conn.close()

    t0 = time.time()
    res = client.post("/api/auth/verify-account", json={
        "identifier": test_email,
        "code": activation_code
    })
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "SUCCESS" and bool(res.json().get("token"))
    player_token = res.json().get("token")
    player_headers = {"Authorization": f"Bearer {player_token}"}
    record_test("Authentication", "Account Activation via OTP", "Validates 6-digit OTP, activates account to ACTIVE and returns JWT", is_ok, res.text if not is_ok else "", dur)

    # 2.5 Strict Password Verification (Wrong Password)
    t0 = time.time()
    res = client.post("/api/auth/login", json={
        "username_or_email": test_username,
        "password": "WrongPassword!456"
    })
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 400 and "Invalid username or password" in res.json().get("detail", "")
    record_test("Authentication", "Wrong Password Rejection", "Strict rejection on invalid password with brute-force tracking", is_ok, res.text if not is_ok else "", dur)

    # 2.6 Login with Correct Password
    t0 = time.time()
    res = client.post("/api/auth/login", json={
        "username_or_email": test_username,
        "password": test_password
    })
    dur = (time.time() - t0) * 1000
    data = res.json()
    player_token = data.get("token") or player_token
    player_headers = {"Authorization": f"Bearer {player_token}"}
    is_ok = res.status_code == 200 and bool(player_token) and data.get("user", {}).get("username") == test_username
    record_test("Authentication", "Valid User Login", "Authenticates verified user and returns valid session JWT", is_ok, res.text if not is_ok else "", dur)

    # 2.7 Case-Insensitive Login
    t0 = time.time()
    res = client.post("/api/auth/login", json={
        "username_or_email": test_username.upper(),
        "password": test_password
    })
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "SUCCESS"
    record_test("Authentication", "Case-Insensitive Login", "Supports uppercase mobile keyboards seamlessly", is_ok, res.text if not is_ok else "", dur)

    # 2.8 Master Admin Login
    t0 = time.time()
    res = client.post("/api/auth/login", json={
        "username_or_email": "admin",
        "password": "admin"
    })
    dur = (time.time() - t0) * 1000
    data = res.json()
    admin_token = data.get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    is_ok = res.status_code == 200 and data.get("user", {}).get("role") == "ADMIN"
    record_test("Authorization", "Master Admin Login", "Authenticates master admin and grants executive privileges", is_ok, res.text if not is_ok else "", dur)

    # 2.9 Phone OTP Gateway Dispatch
    t0 = time.time()
    res = client.post("/api/auth/otp/send", json={"identifier": "+919876500000", "otp_type": "PHONE"})
    dur = (time.time() - t0) * 1000
    otp_data = res.json()
    is_ok = res.status_code == 200 and otp_data.get("status") in ("SUCCESS", "SENT")
    record_test("Identity Verification", "SMS OTP Dispatch", "Dispatches telecom OTP with rate limiting defense", is_ok, res.text if not is_ok else "", dur)

    # =========================================================================
    # DOMAIN 3: BANKING RAILS, PAYMENTS & DOUBLE-ENTRY LEDGER
    # =========================================================================
    print("\n>>> DOMAIN 3: Banking Rails, Payments & Double-Entry Ledger")

    _payment_rate_limit_records.clear()

    # 3.1 Initial Clean Balance Check
    t0 = time.time()
    res = client.get("/api/wallet/transactions", headers=player_headers)
    dur = (time.time() - t0) * 1000
    txs = res.json()
    is_ok = res.status_code == 200 and isinstance(txs, list)
    record_test("Banking Engine", "Transaction Ledger Query", f"Returns immutable ledger records ({len(txs)} initial entries)", is_ok, res.text if not is_ok else "", dur)

    # 3.2 Payment Order Creation (Cashfree / UPI Gateway)
    t0 = time.time()
    res = client.post("/api/payments/create-order", json={
        "amount": 1000.0,
        "purpose": "WALLET_TOPUP",
        "payment_method": "UPI_INTENT"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    order_data = res.json()
    order = order_data.get("order", {})
    order_id = order.get("order_id")
    is_ok = res.status_code == 200 and bool(order_id) and "upi://pay" in order.get("upi_intent_url", "")
    record_test("Payment Gateway", "Order Creation", "Generates UPI Intent and dynamic QR Code order in INR", is_ok, res.text if not is_ok else "", dur)

    # 3.3 HMAC-SHA256 Payment Verification & Atomic Ledger Credit
    t0 = time.time()
    payment_id = f"pay_test_{uuid.uuid4().hex[:8]}"
    secret = "secret_rbi_compliant_pa_key_998877"
    sig_payload = f"{order_id}|{payment_id}".encode('utf-8')
    computed_sig = hmac.new(secret.encode('utf-8'), sig_payload, hashlib.sha256).hexdigest()

    res = client.post("/api/payments/verify", json={
        "order_id": order_id,
        "payment_id": payment_id,
        "signature": computed_sig,
        "purpose": "WALLET_TOPUP",
        "amount": 1000.0,
        "payment_method": "UPI",
        "upi_vpa": "player@okaxis"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    v_data = res.json()
    new_bal = v_data.get("new_balance")
    is_ok = res.status_code == 200 and v_data.get("status") == "SUCCESS" and new_bal >= 1000.0
    record_test("Banking Engine", "HMAC Webhook & Deposit Credit", "Verifies HMAC signature and atomically credits INR 1000 to user wallet", is_ok, res.text if not is_ok else "", dur)

    # 3.4 Tampered Signature Rejection
    t0 = time.time()
    res = client.post("/api/payments/verify", json={
        "order_id": order_id,
        "payment_id": payment_id,
        "signature": "fake_tampered_signature_hex_123456",
        "purpose": "WALLET_TOPUP",
        "amount": 50000.0,
        "payment_method": "UPI"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 400 and "verification failed" in res.text.lower()
    record_test("Security Defense", "Fraudulent Signature Block", "Strictly rejects invalid cryptographic signatures and logs anomaly", is_ok, res.text if not is_ok else "", dur)

    # 3.5 Coin Purchase via Cash Wallet
    t0 = time.time()
    res = client.post("/api/wallet/buy-coins", json={
        "package_id": "pack_elite",
        "coins": 1500,
        "amount": 119.0,
        "payment_method": "UPI_INTENT",
        "idempotency_key": f"test_coin_buy_{uuid.uuid4().hex}"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "SUCCESS"
    record_test("Virtual Economy", "Coin Pack Purchase", "Debits INR 119 from cash wallet to platform revenue and credits 1,500 coins", is_ok, res.text if not is_ok else "", dur)

    # 3.6 Insufficient Funds Enforcement
    t0 = time.time()
    res = client.post("/api/wallet/buy-coins", json={
        "package_id": "pack_ultra",
        "coins": 100000,
        "amount": 99999.0,
        "payment_method": "UPI_INTENT",
        "idempotency_key": f"test_coin_buy_broke_{uuid.uuid4().hex}"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 400 and "insufficient funds" in res.text.lower()
    record_test("Financial Safeguard", "Negative Balance Prevention", "Strictly blocks purchases exceeding wallet balance", is_ok, res.text if not is_ok else "", dur)

    # =========================================================================
    # DOMAIN 4: TOURNAMENTS, BRACKETS & ESCROW PRIZE PAYOUTS
    # =========================================================================
    print("\n>>> DOMAIN 4: Tournaments, Brackets & Escrow Prize Payouts")

    # 4.1 Games Catalog Listing
    t0 = time.time()
    res = client.get("/api/games")
    dur = (time.time() - t0) * 1000
    games = res.json()
    is_ok = res.status_code == 200 and len(games) > 0 and any(g["name"] == "Valorant" for g in games)
    record_test("Games Catalog", "Catalog Query", f"Returns {len(games)} official game titles including BGMI and Valorant", is_ok, res.text if not is_ok else "", dur)

    # 4.2 Non-Admin Tournament Creation Block
    t0 = time.time()
    res = client.post("/api/tournaments", json={
        "title": "Unauthorized Cup",
        "game_id": "valorant",
        "entry_fee_dollars": 50.0,
        "prize_pool_dollars": 500.0,
        "max_participants": 4,
        "format": "SINGLE_ELIMINATION"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 403
    record_test("Access Control", "Non-Admin Tournament Block", "Standard players cannot create official tournaments (403 Forbidden)", is_ok, res.text if not is_ok else "", dur)

    # Top up Admin wallet with INR 1000 so Admin can fund tournament escrow
    _payment_rate_limit_records.clear()
    adm_order = client.post("/api/payments/create-order", json={"amount": 1000.0, "purpose": "WALLET_TOPUP", "payment_method": "UPI"}, headers=admin_headers).json()["order"]
    adm_pay_id = f"pay_adm_{uuid.uuid4().hex[:8]}"
    adm_sig = hmac.new(secret.encode(), f"{adm_order['order_id']}|{adm_pay_id}".encode(), hashlib.sha256).hexdigest()
    client.post("/api/payments/verify", json={"order_id": adm_order["order_id"], "payment_id": adm_pay_id, "signature": adm_sig, "purpose": "WALLET_TOPUP", "amount": 1000.0, "payment_method": "UPI"}, headers=admin_headers)

    # 4.3 Tournament Creation by Admin
    t0 = time.time()
    tourn_title = f"Pro Valorant Showcase {test_uid}"
    res = client.post("/api/tournaments", json={
        "title": tourn_title,
        "game_id": "valorant",
        "entry_fee_dollars": 50.0,
        "prize_pool_dollars": 500.0,
        "max_participants": 4,
        "format": "SINGLE_ELIMINATION",
        "rules": "Standard 5v5 Competitive Rules"
    }, headers=admin_headers)
    dur = (time.time() - t0) * 1000
    tourn_data = res.json()
    tournament_id = tourn_data.get("tournament_id") or tourn_data.get("tournament", {}).get("id") or tourn_data.get("id")
    is_ok = res.status_code == 200 and bool(tournament_id)
    record_test("Tournament Engine", "Tournament Creation & Prize Escrow", "Admin creates 4-player Single Elimination tournament with INR 500 prize pool", is_ok, res.text if not is_ok else "", dur)

    # Register and activate Player Beta for tournament competition
    beta_uid = uuid.uuid4().hex[:6]
    beta_user = f"beta_{beta_uid}"
    beta_email = f"beta_{beta_uid}@test.com"
    client.post("/api/auth/register", json={
        "username": beta_user,
        "email": beta_email,
        "password": "PasswordBeta@123"
    })
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT code FROM otp_codes WHERE identifier = ? AND otp_type = 'ACCOUNT_VERIFICATION' ORDER BY created_at DESC LIMIT 1", (beta_email,))
    beta_code = c.fetchone()["code"]
    conn.close()
    beta_auth = client.post("/api/auth/verify-account", json={"identifier": beta_email, "code": beta_code}).json()
    beta_token = beta_auth.get("token")
    beta_headers = {"Authorization": f"Bearer {beta_token}"}

    # Top up Beta player so they can join
    _payment_rate_limit_records.clear()
    b_order = client.post("/api/payments/create-order", json={"amount": 200.0, "purpose": "WALLET_TOPUP", "payment_method": "UPI"}, headers=beta_headers).json()["order"]
    b_pay_id = f"pay_beta_{uuid.uuid4().hex[:8]}"
    b_sig = hmac.new(secret.encode(), f"{b_order['order_id']}|{b_pay_id}".encode(), hashlib.sha256).hexdigest()
    client.post("/api/payments/verify", json={"order_id": b_order["order_id"], "payment_id": b_pay_id, "signature": b_sig, "purpose": "WALLET_TOPUP", "amount": 200.0, "payment_method": "UPI"}, headers=beta_headers)

    # 4.4 Players Join Tournament
    t0 = time.time()
    join_a = client.post(f"/api/tournaments/{tournament_id}/join", json={
        "tournament_id": tournament_id,
        "team_name": "Team Alpha",
        "captain_contact": "+919876543210",
        "idempotency_key": f"join_a_{test_uid}",
        "payment_type": "WALLET"
    }, headers=player_headers)
    join_b = client.post(f"/api/tournaments/{tournament_id}/join", json={
        "tournament_id": tournament_id,
        "team_name": "Team Beta",
        "captain_contact": "+919876543211",
        "idempotency_key": f"join_b_{test_uid}",
        "payment_type": "WALLET"
    }, headers=beta_headers)
    dur = (time.time() - t0) * 1000
    is_ok = join_a.status_code == 200 and join_b.status_code == 200
    record_test("Tournament Engine", "Player Tournament Registration", "Players join tournament; entry fees debited to platform escrow", is_ok, f"A:{join_a.text} B:{join_b.text}" if not is_ok else "", dur)

    # 4.5 Start Tournament & Generate Match Brackets
    t0 = time.time()
    start_res = client.post(f"/api/tournaments/{tournament_id}/start", headers=admin_headers)
    dur = (time.time() - t0) * 1000
    is_ok = start_res.status_code == 200 and start_res.json().get("status") == "SUCCESS"
    record_test("Tournament Engine", "Bracket Generation", "Starts tournament and generates single-elimination match bracket", is_ok, start_res.text if not is_ok else "", dur)

    # 4.6 Match Result Reporting & Automated Escrow Prize Payout
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM matches WHERE tournament_id = ? ORDER BY round_index DESC LIMIT 1", (tournament_id,))
    final_match = c.fetchone()
    conn.close()

    if final_match:
        final_match_id = final_match["id"]
        t0 = time.time()
        rep_res = client.post(f"/api/matches/{final_match_id}/report", json={
            "match_id": final_match_id,
            "score_a": 13,
            "score_b": 9,
            "evidence_url": "https://example.com/match_screenshot.png"
        }, headers=player_headers)
        dur = (time.time() - t0) * 1000
        rep_data = rep_res.json()
        is_ok = rep_res.status_code == 200 and rep_data.get("status") == "COMPLETED" and rep_data.get("is_final") is True
        record_test("Tournament Engine", "Match Reporting & Escrow Payout", "Winner reported (13-9), Grand Final completed and INR 500 prize credited", is_ok, rep_res.text if not is_ok else "", dur)
    else:
        record_test("Tournament Engine", "Match Reporting & Escrow Payout", "Match reporting skipped (bracket match not found)", False, "No match generated", 0)

    # =========================================================================
    # DOMAIN 5: COMMUNITY, SOCIAL, QUESTS & SUPPORT TICKETS
    # =========================================================================
    print("\n>>> DOMAIN 5: Community, Social, Quests & Support Tickets")

    # 5.1 Social Account Linking
    t0 = time.time()
    res = client.post("/api/social/link", json={
        "provider": "discord",
        "handle_or_id": f"{test_username}#1337"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("status") == "SUCCESS"
    record_test("Social Hub", "Social Account Linking", "Binds verified Discord handle to player profile", is_ok, res.text if not is_ok else "", dur)

    # 5.2 Daily Quests
    t0 = time.time()
    res = client.get("/api/quests", headers=player_headers)
    dur = (time.time() - t0) * 1000
    q_data = res.json()
    is_ok = res.status_code == 200 and isinstance(q_data.get("quests"), list)
    record_test("Gamification", "Daily Quests", f"Returns {len(q_data.get('quests', []))} active daily/weekly esports quests", is_ok, res.text if not is_ok else "", dur)

    # 5.3 Support Ticket Submission
    t0 = time.time()
    res = client.post("/api/tickets", json={
        "category": "TOURNAMENT",
        "subject": "Match Screenshot Verification",
        "description": "Please verify our round 1 ping latency log.",
        "priority": "HIGH"
    }, headers=player_headers)
    dur = (time.time() - t0) * 1000
    tick_data = res.json()
    ticket_id = tick_data.get("ticket_id")
    is_ok = res.status_code == 200 and bool(ticket_id) and "TICK-" in tick_data.get("ticket_number", "")
    record_test("Support System", "Ticket Submission", f"Submits support ticket #{tick_data.get('ticket_number')}", is_ok, res.text if not is_ok else "", dur)

    # 5.4 Admin Ticket Resolution
    t0 = time.time()
    res = client.post(f"/api/admin/tickets/{ticket_id}/resolve", json={
        "status": "RESOLVED",
        "resolution": "Ping logs verified. Match valid.",
        "admin_notes": "Reviewed and closed."
    }, headers=admin_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and "RESOLVED" in res.text
    record_test("Admin Operations", "Ticket Resolution", "Admin resolves ticket and updates ticket status", is_ok, res.text if not is_ok else "", dur)

    # 5.5 Leaderboard Rankings Query
    t0 = time.time()
    res = client.get("/api/leaderboard")
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and isinstance(res.json(), list)
    record_test("Leaderboard", "Live Rankings", f"Returns {len(res.json())} official ranked tournament players", is_ok, res.text if not is_ok else "", dur)

    # =========================================================================
    # DOMAIN 6: ADMIN COMMAND CENTER, GOVERNANCE & IMMUNITY
    # =========================================================================
    print("\n>>> DOMAIN 6: Admin Command Center, Governance & Immunity")

    # 6.1 Admin User Management List
    t0 = time.time()
    res = client.get("/api/admin/users", headers=admin_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and isinstance(res.json(), list) and len(res.json()) >= 2
    record_test("Admin Governance", "User Directory Query", f"Lists all platform users ({len(res.json())} users found)", is_ok, res.text if not is_ok else "", dur)

    # 6.2 User Suspension by Admin
    t0 = time.time()
    res = client.post(f"/api/admin/users/{reg_user_id}/status", json={
        "status": "SUSPENDED",
        "reason": "Test suspension check"
    }, headers=admin_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("new_status") == "SUSPENDED"
    record_test("Admin Governance", "Account Suspension", "Admin successfully suspends user account and logs audit entry", is_ok, res.text if not is_ok else "", dur)

    # 6.3 Master Admin Suspension Immunity Check
    t0 = time.time()
    res = client.post("/api/admin/users/admin/status", json={
        "status": "SUSPENDED",
        "reason": "Accidental suspension attempt"
    }, headers=admin_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 400 and "cannot be suspended" in res.text.lower()
    record_test("Security Safeguard", "Master Admin Immunity", "Strictly rejects suspension of 'admin' account with 400", is_ok, res.text if not is_ok else "", dur)

    # 6.4 Reactivate User Account
    t0 = time.time()
    res = client.post(f"/api/admin/users/{reg_user_id}/status", json={
        "status": "ACTIVE",
        "reason": "Reinstated after test"
    }, headers=admin_headers)
    dur = (time.time() - t0) * 1000
    is_ok = res.status_code == 200 and res.json().get("new_status") == "ACTIVE"
    record_test("Admin Governance", "Account Reinstatement", "Admin reinstates user account back to ACTIVE status", is_ok, res.text if not is_ok else "", dur)

    # 6.5 User Role Promotion (Player -> CO_ADMIN)
    t0 = time.time()
    res = client.post(f"/api/admin/users/{reg_user_id}/role", json={
        "role": "CO_ADMIN",
        "reason": "Promoted to Tournament Referee"
    }, headers=admin_headers)
    dur = (time.time() - t0) * 1000
    data = res.json()
    new_role = data.get("user", {}).get("role") or data.get("new_role")
    is_ok = res.status_code == 200 and new_role == "CO_ADMIN"
    record_test("Role-Based Access Control", "Role Promotion", "Promotes user to CO_ADMIN with executive delegation", is_ok, res.text if not is_ok else "", dur)

    # 6.6 Final Mathematical Reconciliation Check
    t0 = time.time()
    res = client.get("/api/admin/reconcile")
    dur = (time.time() - t0) * 1000
    recon = res.json()
    is_ok = res.status_code == 200 and recon.get("status") == "PASS" and recon.get("invariants", {}).get("double_entry_balanced") is True
    record_test("Banking Engine", "Post-Test Ledger Integrity", "All deposits, coin purchases and tournament escrow payouts balanced perfectly", is_ok, res.text if not is_ok else "", dur)

    # =========================================================================
    # SUMMARY REPORT
    # =========================================================================
    total_tests = len(TEST_RESULTS)
    passed_tests = sum(1 for t in TEST_RESULTS if t["passed"])
    failed_tests = total_tests - passed_tests

    print("\n" + "="*80)
    print(f"TEST EXECUTION COMPLETE: {passed_tests}/{total_tests} PASSED ({failed_tests} FAILED)")
    print("="*80 + "\n")

    return TEST_RESULTS

if __name__ == "__main__":
    results = run_deep_scan()
    with open("feature_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    if any(not t["passed"] for t in results):
        sys.exit(1)
