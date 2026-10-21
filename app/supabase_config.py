import os
from typing import Optional
from pathlib import Path

# Load from environment variables (set in .env or cloud provider)
SUPABASE_URL: Optional[str] = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY: Optional[str] = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_DB_URL: Optional[str] = os.environ.get("SUPABASE_DB_URL")  # Direct Postgres URI

def is_supabase_configured() -> bool:
    """Checks whether valid Supabase configuration is present."""
    return bool(SUPABASE_URL and (SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY))

def get_supabase_client():
    """
    Returns an initialized Supabase client if available.
    Falls back gracefully if credentials are not yet set.
    """
    if not is_supabase_configured():
        return None
    try:
        from supabase import create_client, Client
        key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
        return create_client(SUPABASE_URL, key)
    except ImportError:
        # supabase python library can be installed via 'pip install supabase'
        return None
