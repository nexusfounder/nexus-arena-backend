import json
import uuid
import re
from app.database import init_db, get_db_connection
from app.security import (
    encrypt_envelope, decrypt_envelope,
    generate_backup_codes, verify_and_consume_backup_code,
    verify_user_2fa_factor, generate_totp_secret
)
import pyotp

def run_tests():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Verify 3 tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'user_two_factor_secrets', 'financial_profiles')")
    tables = [row['name'] for row in cursor.fetchall()]
    print("Isolated tables found:", tables)
    assert 'users' in tables and 'user_two_factor_secrets' in tables and 'financial_profiles' in tables

    # 2. Test 2FA backup codes generation and consumption
    plain, hashed = generate_backup_codes(10)
    assert len(plain) == 10 and len(hashed) == 10
    test_code = plain[0]
    hashed_json = json.dumps(hashed)

    # Consume test_code
    matched, updated_json = verify_and_consume_backup_code(test_code, hashed_json)
    assert matched is True
    remaining = json.loads(updated_json)
    assert len(remaining) == 9

    # Re-consume same code (should fail - single use)
    matched_again, _ = verify_and_consume_backup_code(test_code, updated_json)
    assert matched_again is False

    print("Backup code generation & single-use consumption: PASSED")

    # 3. Test verify_user_2fa_factor on test user
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    u = cursor.fetchone()
    admin_id = u['id']

    secret = generate_totp_secret()
    totp = pyotp.TOTP(secret)
    rolling_code = totp.now()

    enc_sec = encrypt_envelope(secret)
    cursor.execute("SELECT id FROM user_two_factor_secrets WHERE user_id = ?", (admin_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE user_two_factor_secrets SET encrypted_totp_secret = ?, backup_codes = ? WHERE user_id = ?", (enc_sec, hashed_json, admin_id))
    else:
        cursor.execute("INSERT INTO user_two_factor_secrets (id, user_id, encrypted_totp_secret, backup_codes, updated_at) VALUES (?, ?, ?, ?, '2026-10-16T12:00:00Z')", (str(uuid.uuid4()), admin_id, enc_sec, hashed_json))
    conn.commit()

    # Verify with rolling TOTP code
    v1, f1 = verify_user_2fa_factor(admin_id, rolling_code, conn)
    print("TOTP verification:", v1, f1)
    assert v1 is True and f1 == 'TOTP'

    # Verify with backup code
    backup_test = plain[1]
    v2, f2 = verify_user_2fa_factor(admin_id, backup_test, conn)
    print("Backup code verification:", v2, f2)
    assert v2 is True and f2 == 'BACKUP_CODE'

    # Re-verify same backup code (should fail!)
    v3, f3 = verify_user_2fa_factor(admin_id, backup_test, conn)
    print("Re-used backup code verification:", v3, f3)
    assert v3 is False

    # 4. Verify Financial Profile Isolation
    cursor.execute("SELECT * FROM financial_profiles WHERE user_id = ?", (admin_id,))
    fin_row = cursor.fetchone()
    if not fin_row:
        cursor.execute("INSERT INTO financial_profiles (id, user_id, payment_gateway_customer_id, kyc_status, updated_at) VALUES (?, ?, 'cus_admin_001', 'VERIFIED', '2026-10-19T12:00:00Z')", (str(uuid.uuid4()), admin_id))
        conn.commit()
        cursor.execute("SELECT * FROM financial_profiles WHERE user_id = ?", (admin_id,))
        fin_row = cursor.fetchone()
    assert fin_row is not None
    fin_dict = dict(fin_row)
    print("Financial profile found (Customer ID):", fin_dict['payment_gateway_customer_id'])
    assert fin_dict['payment_gateway_customer_id'].startswith("cus_")

    conn.close()
    print("ALL PART 1 & 2 DATABASE AND SECURITY TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
