from fastapi.testclient import TestClient
from app.main import app
from app.rbi_compliance import create_rbi_payment_order, MANDATORY_DISCLOSURES

client = TestClient(app)

def test_rbi_disclosures():
    res = client.get("/api/compliance/rbi-disclosures")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "ap-south-1" in data["data_localization"]["region"]
    assert "Mr. Rajesh Sharma" in data["disclosures"]["nodal_grievance_officer"]["name"]
    assert "48 Hours" in data["disclosures"]["nodal_grievance_officer"]["mandated_sla"]
    assert "grievance@nexusgamingarena.in" in data["disclosures"]["nodal_grievance_officer"]["email"]
    assert "Level 5" in data["disclosures"]["registered_office"]["address_line1"]
    # Check headers
    assert res.headers["x-data-localization"] == "ap-south-1-mumbai"
    assert "RBI" in res.headers["x-rbi-pa-compliance"]
    print("\n[+] test_rbi_disclosures PASSED!")

def test_payment_order_creation_and_verification():
    # Login as admin to get token
    login_res = client.post("/api/auth/login", json={"username_or_email": "admin", "password": "admin"})
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 1. Create RBI Payment Order for Wallet Top-up
    create_res = client.post("/api/payments/create-order", json={
        "amount": 500.0,
        "purpose": "WALLET_TOPUP",
        "payment_method": "UPI"
    }, headers=headers)
    assert create_res.status_code == 200
    order_data = create_res.json()
    assert order_data["status"] == "SUCCESS"
    order = order_data["order"]
    assert order["amount"] == 500.0
    assert order["vpa"] == "nexusarena@icici"
    assert "upi://pay?" in order["upi_intent_url"]
    assert "qrserver.com" in order["qr_code_url"]

    # 2. Verify Payment Order with Cryptographic HMAC-SHA256 Signature
    import hmac, hashlib
    payment_id = f"pay_test_{order['order_id'][-8:]}"
    secret = "secret_rbi_compliant_pa_key_998877"
    sig_payload = f"{order['order_id']}|{payment_id}".encode('utf-8')
    computed_signature = hmac.new(secret.encode('utf-8'), sig_payload, hashlib.sha256).hexdigest()

    verify_res = client.post("/api/payments/verify", json={
        "order_id": order["order_id"],
        "payment_id": payment_id,
        "signature": computed_signature,
        "purpose": "WALLET_TOPUP",
        "amount": 500.0,
        "payment_method": "UPI",
        "upi_vpa": "gamer@okaxis"
    }, headers=headers)
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["status"] == "SUCCESS"
    assert "Successfully credited ₹500.00" in verify_data["message"]
    print("[+] test_payment_order_creation_and_verification PASSED!")

def test_coin_purchase_via_gateway():
    login_res = client.post("/api/auth/login", json={"username_or_email": "admin", "password": "admin"})
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 1. Top up ₹500 first so wallet has funds
    order_res = client.post("/api/payments/create-order", json={
        "amount": 500.0,
        "purpose": "WALLET_TOPUP",
        "payment_method": "UPI_INTENT"
    }, headers=headers)
    order = order_res.json()["order"]
    import hmac, hashlib
    payment_id = f"pay_test_{order['order_id'][-8:]}"
    secret = "secret_rbi_compliant_pa_key_998877"
    sig_payload = f"{order['order_id']}|{payment_id}".encode('utf-8')
    computed_sig = hmac.new(secret.encode('utf-8'), sig_payload, hashlib.sha256).hexdigest()
    client.post("/api/payments/verify", json={
        "order_id": order["order_id"],
        "payment_id": payment_id,
        "signature": computed_sig,
        "purpose": "WALLET_TOPUP",
        "amount": 500.0,
        "payment_method": "UPI",
        "upi_vpa": "admin@okaxis"
    }, headers=headers)

    import uuid
    # 2. Buy Elite pack (1,500 coins for ₹119)
    res = client.post("/api/wallet/buy-coins", json={
        "package_id": "pack_elite",
        "coins": 1500,
        "amount": 119.0,
        "payment_method": "UPI_INTENT",
        "idempotency_key": f"test_coin_buy_{uuid.uuid4().hex}"
    }, headers=headers)
    print("BUY COINS RESULT:", res.status_code, res.json())
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "1,500 Nexus Coins" in data["message"]
    print("[+] test_coin_purchase_via_gateway PASSED!")

if __name__ == "__main__":
    test_rbi_disclosures()
    test_payment_order_creation_and_verification()
    test_coin_purchase_via_gateway()
    print("\nALL RBI COMPLIANCE & GATEWAY TESTS PASSED SUCCESSFULLY!")
