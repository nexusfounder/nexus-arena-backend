import json
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, get_db_connection

def test_api():
    init_db()
    client = TestClient(app)

    # 1. Login as Wolfy (get JWT cookie)
    login_res = client.post("/api/auth/login", json={
        "username_or_email": "Wolfy",
        "password": "password123"
    })
    print("Initial login response:", login_res.status_code, login_res.json().get("status"))

    # 2. Setup 2FA
    setup_res = client.post("/api/auth/2fa/setup")
    print("2FA setup status:", setup_res.status_code)
    assert setup_res.status_code == 200
    setup_data = setup_res.json()
    assert "backup_codes" in setup_data
    assert len(setup_data["backup_codes"]) == 10
    assert "secret" in setup_data
    backup_codes = setup_data["backup_codes"]
    first_backup_code = backup_codes[0]
    print(f"Generated 10 backup codes. Sample: {first_backup_code}")

    # 3. Verify & Enable 2FA using first backup code
    enable_res = client.post("/api/auth/2fa/verify-and-enable", json={"code": first_backup_code})
    print("2FA enable response:", enable_res.status_code, enable_res.json())
    assert enable_res.status_code == 200

    # 4. Login with 2FA required and provide second backup code
    login_with_backup = client.post("/api/auth/login", json={
        "username_or_email": "Wolfy",
        "password": "password123",
        "two_factor_code": backup_codes[1]
    })
    print("Login with backup code status:", login_with_backup.status_code)
    assert login_with_backup.status_code == 200

    # 5. Try to re-use the same second backup code (should fail!)
    login_reuse_backup = client.post("/api/auth/login", json={
        "username_or_email": "Wolfy",
        "password": "password123",
        "two_factor_code": backup_codes[1]
    })
    print("Re-used backup code status (expected 400):", login_reuse_backup.status_code)
    assert login_reuse_backup.status_code == 400

    # 6. Stripe Profile Endpoint (Table 3)
    stripe_prof_res = client.get("/api/wallet/stripe/profile")
    print("Stripe profile status:", stripe_prof_res.status_code, stripe_prof_res.json())
    assert stripe_prof_res.status_code == 200
    stripe_prof = stripe_prof_res.json()
    assert stripe_prof["customer_id"].startswith("cus_")

    # 7. Stripe Charge with Raw Card Number (Strict PCI-DSS Rejection)
    raw_card_res = client.post("/api/wallet/stripe/charge-token", json={
        "amount": 25.0,
        "payment_token": "4111222233334444",
        "idempotency_key": f"test_raw_{uuid.uuid4().hex}"
    })
    print("Raw card submission status (expected 400):", raw_card_res.status_code, raw_card_res.json()["detail"])
    assert raw_card_res.status_code == 400
    assert "PCI-DSS" in raw_card_res.json()["detail"]

    # 8. Stripe Charge with Safe Token (tok_...)
    safe_token = f"tok_1N4k92Abcde_{uuid.uuid4().hex[:8]}"
    idem_key = f"idem_{uuid.uuid4().hex}"
    charge_res = client.post("/api/wallet/stripe/charge-token", json={
        "amount": 25.0,
        "payment_token": safe_token,
        "idempotency_key": idem_key
    })
    print("Safe token charge status:", charge_res.status_code, charge_res.json())
    assert charge_res.status_code == 200
    charge_data = charge_res.json()
    assert charge_data["status"] == "SUCCESS"
    assert charge_data["customer_id"].startswith("cus_")

    # 9. Test Idempotency on Stripe Charge Replay
    replay_res = client.post("/api/wallet/stripe/charge-token", json={
        "amount": 25.0,
        "payment_token": safe_token,
        "idempotency_key": idem_key
    })
    print("Idempotent replay status:", replay_res.status_code)
    assert replay_res.status_code == 200

    print("ALL API TESTS FOR PART 1 & PART 2 PASSED!")

if __name__ == "__main__":
    test_api()
