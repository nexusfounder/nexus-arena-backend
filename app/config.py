import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Server Settings
HOST = os.environ.get("NEXUS_HOST", "0.0.0.0")
PORT = int(os.environ.get("NEXUS_PORT", 8088))
DEBUG = os.environ.get("NEXUS_DEBUG", "false").strip().lower() == "true"

# Security & Cryptography
import secrets
_default_secret = secrets.token_hex(32)
SECRET_KEY = os.environ.get("NEXUS_SECRET_KEY") or _default_secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# AES-256-GCM Envelope Encryption Key (Derived 32 bytes)
import hashlib
MASTER_ENCRYPTION_KEY = hashlib.sha256(SECRET_KEY.encode('utf-8')).digest()

# Database
DB_PATH = BASE_DIR / "data" / "nexus_arena.db"

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
