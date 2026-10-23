import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Server Settings
HOST = os.environ.get("NEXUS_HOST", "0.0.0.0")
PORT = int(os.environ.get("NEXUS_PORT", 8088))
DEBUG = os.environ.get("NEXUS_DEBUG", "false").strip().lower() == "true"

# Security & Cryptography
import hashlib
import secrets
import logging

_logger = logging.getLogger("nexus.config")

_env_secret = os.environ.get("NEXUS_SECRET_KEY")
if _env_secret:
    SECRET_KEY = _env_secret
elif DEBUG:
    SECRET_KEY = "nexus_arena_dev_debug_secret_key_for_local_testing_only_2026"
    _logger.warning("⚠️ Running with developer debug SECRET_KEY in local DEBUG mode. Set NEXUS_SECRET_KEY in production.")
else:
    # High-entropy production fallback: persist unique server instance secret
    _secret_file = BASE_DIR / "data" / ".nexus_secret"
    try:
        if _secret_file.exists():
            SECRET_KEY = _secret_file.read_text(encoding="utf-8").strip()
        else:
            SECRET_KEY = secrets.token_urlsafe(64)
            _secret_file.parent.mkdir(parents=True, exist_ok=True)
            _secret_file.write_text(SECRET_KEY, encoding="utf-8")
    except Exception:
        SECRET_KEY = secrets.token_urlsafe(64)

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# AES-256-GCM Envelope Encryption Key (Derived 32 bytes)
MASTER_ENCRYPTION_KEY = hashlib.sha256(SECRET_KEY.encode('utf-8')).digest()

# Database
DB_PATH = BASE_DIR / "data" / "nexus_arena.db"

# Master Administrator Credential Locks (Configurable via Environment Variables)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin").strip()
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@nexusgamingarena.online").strip()
ADMIN_CREDENTIALS_BACKUP_PATH = BASE_DIR / "data" / ".admin_credentials"

# Platform Financial Escrow Account ID
PLATFORM_ESCROW_ACCOUNT_ID = "00000000-0000-0000-0000-000000000001"
PLATFORM_REVENUE_ACCOUNT_ID = "00000000-0000-0000-0000-000000000002"

# Supported Esports Titles
SUPPORTED_GAMES = [
    {"id": "valorant", "name": "Valorant", "icon": "🎯", "category": "FPS"},
    {"id": "cs2", "name": "Counter-Strike 2", "icon": "💣", "category": "FPS"},
    {"id": "bgmi", "name": "Battlegrounds Mobile India (BGMI)", "icon": "🪂", "category": "Battle Royale"},
    {"id": "apex", "name": "Apex Legends", "icon": "⚡", "category": "Battle Royale"},
    {"id": "rl", "name": "Rocket League", "icon": "🏎️", "category": "Sports/Action"},
    {"id": "dota2", "name": "Dota 2", "icon": "⚔️", "category": "MOBA"},
]
