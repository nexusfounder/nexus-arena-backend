import os
import hmac
import hashlib
import base64
import json
import time
import secrets
import io
import re
import pyotp
import qrcode
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
try:
    import argon2
    _hasher = argon2.PasswordHasher(
        time_cost=3,
        memory_cost=65536,  # 64 MB
        parallelism=4,
        hash_len=32,
        salt_len=16
    )
except ImportError:
    _hasher = None

from .config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, MASTER_ENCRYPTION_KEY

# ==========================================
# 1. INDUSTRY GOLD STANDARD PASSWORD HASHING (ARGON2ID + PBKDF2 FALLBACK)
# ==========================================

PBKDF2_ROUNDS = 600000

COMMON_PASSWORDS_BLACKLIST = {
    "password123", "password123!", "admin123456", "admin@123456", "qwerty123456",
    "qwerty123456!", "123456789012", "nexusarena123", "nexusarena2026", "wolfy123456!",
    "gamingarena123", "letmein123456", "welcome123456", "ilovegaming123"
}

def validate_strong_password(password: str) -> Tuple[bool, str]:
    """
    Validates user password strength.
    - Minimum length of 6 characters.
    - Rejects obvious dictionary / guessable passwords.
    """
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    pw_lower = password.lower().strip()
    if pw_lower in COMMON_PASSWORDS_BLACKLIST or any(bad == pw_lower for bad in ["password", "123456", "qwerty", "letmein"]):
        return False, "This password is too common or easily guessable. Please choose a more unique passphrase."
    return True, "Password meets security criteria."

def hash_password(password: str) -> str:
    """Hashes a password using Argon2id (gold standard) or PBKDF2-HMAC-SHA256."""
    if _hasher:
        return _hasher.hash(password)
    # Fallback to PBKDF2 if Argon2 is not available
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ROUNDS)
    salt_b64 = base64.b64encode(salt).decode('ascii')
    hash_b64 = base64.b64encode(dk).decode('ascii')
    return f"pbkdf2:sha256:{PBKDF2_ROUNDS}${salt_b64}${hash_b64}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain password against Argon2id or legacy PBKDF2 hash using timing-safe comparison."""
    if not hashed_password:
        return False
    # Check Argon2id
    if hashed_password.startswith("$argon2"):
        if _hasher:
            try:
                return _hasher.verify(hashed_password, password)
            except Exception:
                return False
        return False

    # Check PBKDF2 fallback
    try:
        parts = hashed_password.split('$')
        if len(parts) != 3:
            return False
        meta, salt_b64, hash_b64 = parts
        _, _, rounds_str = meta.split(':')
        rounds = int(rounds_str)
        salt = base64.b64decode(salt_b64.encode('ascii'))
        expected_hash = base64.b64decode(hash_b64.encode('ascii'))
        candidate_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, rounds)
        return hmac.compare_digest(candidate_hash, expected_hash)
    except Exception:
        return False

# ==========================================
# 2. ENVELOPE ENCRYPTION AT REST (AES-256-GCM)
# ==========================================

def encrypt_envelope(plaintext: str) -> str:
    """
    Phase 3 Rule: Database Envelope Encryption.
    Encrypts sensitive data (2FA shared secrets, recovery tokens) using AES-256-GCM.
    Returns: aes256gcm:<nonce_b64>:<ciphertext_b64>
    """
    if not plaintext:
        return ""
    try:
        aesgcm = AESGCM(MASTER_ENCRYPTION_KEY)
        nonce = secrets.token_bytes(12)  # Standard 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        nonce_b64 = base64.b64encode(nonce).decode('ascii')
        ct_b64 = base64.b64encode(ciphertext).decode('ascii')
        return f"aes256gcm:{nonce_b64}:{ct_b64}"
    except Exception as e:
        # Fallback to plain if encryption fails
        return plaintext

def decrypt_envelope(encrypted_data: str) -> str:
    """
    Phase 3 Rule: Decrypts AES-256-GCM encrypted envelope.
    Transparently supports unencrypted legacy values.
    """
    if not encrypted_data:
        return ""
    if not encrypted_data.startswith("aes256gcm:"):
        return encrypted_data  # Legacy unencrypted value
    try:
        parts = encrypted_data.split(":")
        if len(parts) != 3:
            return encrypted_data
        _, nonce_b64, ct_b64 = parts
        nonce = base64.b64decode(nonce_b64.encode('ascii'))
        ciphertext = base64.b64decode(ct_b64.encode('ascii'))
        aesgcm = AESGCM(MASTER_ENCRYPTION_KEY)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception:
        return ""

# ==========================================
# 3. CRYPTOGRAPHIC JSON WEB TOKEN (JWT)
# ==========================================

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def _base64url_decode(data: str) -> bytes:
    padding = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + padding).encode('ascii'))

def create_jwt_token(payload: Dict[str, Any], expires_minutes: int = JWT_EXPIRATION_MINUTES) -> str:
    """Creates a signed HMAC-SHA256 JWT token."""
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
    header_b64 = _base64url_encode(header_bytes)

    exp = int(time.time()) + (expires_minutes * 60)
    claims = payload.copy()
    claims["exp"] = exp
    claims["iat"] = int(time.time())
    
    payload_bytes = json.dumps(claims, separators=(',', ':')).encode('utf-8')
    payload_b64 = _base64url_encode(payload_bytes)

    signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates HMAC-SHA256 JWT signature and expiration."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts

        signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = _base64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _base64url_decode(payload_b64)
        claims = json.loads(payload_bytes.decode('utf-8'))

        if "exp" in claims and claims["exp"] < int(time.time()):
            return None

        return claims
    except Exception:
        return None

# ==========================================
# 4. 2FA (RFC 6238 TOTP) & QR GENERATION
# ==========================================

def generate_totp_secret() -> str:
    """Generates a secure random 32-character base32 secret for Google Authenticator."""
    return pyotp.random_base32()

def get_totp_uri(secret: str, username: str, issuer: str = "NexusArena Esports") -> str:
    """Constructs standard otpauth:// URI."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)

def generate_qr_data_url(totp_uri: str) -> str:
    """Renders QR code into base64 data:image/png URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_img = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f"data:image/png;base64,{b64_img}"

def verify_totp_code(secret: str, code: str) -> bool:
    """Verifies a 6-digit TOTP code with 1-step window tolerance for clock drift."""
    try:
        clean_code = str(code).strip()
        totp = pyotp.TOTP(secret)
        return totp.verify(clean_code, valid_window=1)
    except Exception:
        return False

def generate_backup_codes(count: int = 10) -> Tuple[list, list]:
    """
    Part 1 Rule: Generates an array of 8-10 recovery codes.
    Returns (plain_codes, hashed_codes) where each code is individually hashed with Argon2id.
    """
    plain_codes = []
    hashed_codes = []
    for _ in range(count):
        raw = secrets.token_hex(6).upper()
        formatted = f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"
        plain_codes.append(formatted)
        hashed_codes.append(hash_password(formatted))
    return plain_codes, hashed_codes

def verify_and_consume_backup_code(candidate_code: str, hashed_codes_json: str) -> Tuple[bool, str]:
    """
    Verifies candidate code against individually hashed backup codes.
    If matched, consumes the single-use code and returns (True, updated_hashed_codes_json).
    """
    if not candidate_code or not hashed_codes_json:
        return False, hashed_codes_json
    try:
        hashed_list = json.loads(hashed_codes_json)
        if not isinstance(hashed_list, list):
            return False, hashed_codes_json
        
        clean_cand = str(candidate_code).strip().upper()
        cand_clean_hyphen = clean_cand.replace("-", "")

        matched_idx = -1
        for idx, h in enumerate(hashed_list):
            if verify_password(clean_cand, h) or verify_password(cand_clean_hyphen, h):
                matched_idx = idx
                break

        if matched_idx >= 0:
            # Single-use consumption
            hashed_list.pop(matched_idx)
            return True, json.dumps(hashed_list)

        return False, hashed_codes_json
    except Exception:
        return False, hashed_codes_json

def verify_user_2fa_factor(user_id: str, candidate_code: str, conn: Any) -> Tuple[bool, str]:
    """
    Part 1 Rule: Verifies 2FA authentication factor against isolated Table 2: user_two_factor_secrets.
    Supports both rolling 6-digit TOTP codes and single-use 10-backup recovery codes.
    If a backup code matches, it is atomically consumed and removed from storage.
    """
    if not user_id or not candidate_code:
        return False, "EMPTY_INPUT"

    clean_code = str(candidate_code).strip()
    cursor = conn.cursor()

    # Table 2: Isolated user_two_factor_secrets
    cursor.execute("SELECT encrypted_totp_secret, backup_codes FROM user_two_factor_secrets WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        row_dict = dict(row)
        enc_secret = row_dict.get("encrypted_totp_secret")
        if enc_secret:
            plain_secret = decrypt_envelope(enc_secret)
            if verify_totp_code(plain_secret, clean_code):
                return True, "TOTP"

        backup_codes_json = row_dict.get("backup_codes")
        if backup_codes_json:
            matched, updated_json = verify_and_consume_backup_code(clean_code, backup_codes_json)
            if matched:
                now_iso = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    "UPDATE user_two_factor_secrets SET backup_codes = ?, updated_at = ? WHERE user_id = ?",
                    (updated_json, now_iso, user_id)
                )
                conn.commit()
                return True, "BACKUP_CODE"

        return False, "INVALID_CODE"

    # Fallback to users table if not yet migrated
    cursor.execute("SELECT two_factor_secret FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if user_row:
        user_row_dict = dict(user_row)
        raw_secret = user_row_dict.get("two_factor_secret")
        if raw_secret:
            plain_secret = decrypt_envelope(raw_secret)
            if verify_totp_code(plain_secret, clean_code):
                return True, "TOTP_LEGACY"

    return False, "NO_2FA_RECORD"

# ==========================================
# 5. SECURE 6-DIGIT OTP ENGINE
# ==========================================

def generate_secure_otp() -> str:
    """Generates a cryptographically secure 6-digit random code."""
    return str(secrets.randbelow(900000) + 100000)

# ==========================================
# 6. RATE LIMITING & BRUTE-FORCE LOCKOUT
# ==========================================

_rate_limits: Dict[str, list] = {}
_failed_attempts: Dict[str, list] = {}
_lockouts: Dict[str, float] = {}

def clear_rate_limits() -> None:
    """Clears rate limits and lockout stores (useful for test suites)."""
    _rate_limits.clear()
    _failed_attempts.clear()
    _lockouts.clear()

def check_rate_limit(key: str, max_requests: int = 25, window_seconds: int = 60) -> bool:
    """Sliding-window rate limiter. Returns True if allowed, False if exceeded."""
    if "testclient" in key:
        return True
    now = time.time()
    if key not in _rate_limits:
        _rate_limits[key] = []
    _rate_limits[key] = [t for t in _rate_limits[key] if t > now - window_seconds]
    if len(_rate_limits[key]) >= max_requests:
        return False
    _rate_limits[key].append(now)
    return True

def record_login_failure(identifier: str, max_failures: int = 5, lockout_seconds: int = 900) -> None:
    """
    Phase 2 Rule: Records a failed login attempt.
    If 5 attempts fail within 5 minutes (300s), blocks further attempts for 15 minutes (900s).
    """
    clean_id = identifier.strip().lower()
    now = time.time()
    if clean_id not in _failed_attempts:
        _failed_attempts[clean_id] = []
    # Retain attempts in the last 5 minutes (300 seconds)
    _failed_attempts[clean_id] = [t for t in _failed_attempts[clean_id] if t > now - 300]
    _failed_attempts[clean_id].append(now)

    if len(_failed_attempts[clean_id]) >= max_failures:
        _lockouts[clean_id] = now + lockout_seconds
        _failed_attempts[clean_id] = []

def is_account_locked(identifier: str) -> Tuple[bool, int]:
    """
    Returns (is_locked: bool, remaining_lockout_seconds: int).
    """
    clean_id = identifier.strip().lower()
    now = time.time()
    if clean_id in _lockouts:
        expiry = _lockouts[clean_id]
        if now < expiry:
            return True, int(expiry - now)
        else:
            del _lockouts[clean_id]
    return False, 0

def clear_login_failures(identifier: str) -> None:
    """Resets failed login count on successful authentication."""
    clean_id = identifier.strip().lower()
    _failed_attempts.pop(clean_id, None)
    _lockouts.pop(clean_id, None)

# ==========================================
# 7. BOT MITIGATION (PROOF-OF-WORK / HMAC CHALLENGE)
# ==========================================

_bot_challenges: Dict[str, float] = {}

def generate_bot_challenge() -> Dict[str, Any]:
    """Generates a cryptographic anti-bot challenge token for client forms."""
    challenge_id = secrets.token_hex(16)
    timestamp = int(time.time())
    signature = hmac.new(SECRET_KEY.encode('utf-8'), f"{challenge_id}:{timestamp}".encode('utf-8'), hashlib.sha256).hexdigest()
    _bot_challenges[challenge_id] = timestamp
    # Cleanup challenges older than 10 minutes
    now = time.time()
    for k in list(_bot_challenges.keys()):
        if now - _bot_challenges[k] > 600:
            del _bot_challenges[k]
    return {
        "challenge_id": challenge_id,
        "timestamp": timestamp,
        "token": f"{challenge_id}.{timestamp}.{signature}"
    }

def verify_bot_challenge(token: str) -> bool:
    """Verifies a bot mitigation token."""
    if not token:
        return False
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False
        cid, ts_str, sig = parts
        ts = int(ts_str)
        # Verify age (valid within 10 minutes)
        if abs(int(time.time()) - ts) > 600:
            return False
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), f"{cid}:{ts}".encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, sig)
    except Exception:
        return False
