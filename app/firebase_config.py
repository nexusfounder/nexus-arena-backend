"""
NEXUS GAMING ARENA - FIREBASE INTEGRATION MODULE
Provides Firebase Storage and Realtime Database interfaces for:
- Live Tournament synchronization
- Match Room ID & Password live broadcasts
- Realtime player presence tracking
- Game artwork & receipt storage
"""

import os
import json
import logging
from typing import Optional, Dict, Any
import urllib.request
import urllib.error

logger = logging.getLogger("nexus.firebase")

# Firebase Project Credentials
FIREBASE_PROJECT_ID: str = os.environ.get("FIREBASE_PROJECT_ID", "nexus-gaming-arena-28be9")
FIREBASE_DATABASE_URL: str = os.environ.get(
    "FIREBASE_DATABASE_URL", 
    "https://nexus-gaming-arena-28be9-default-rtdb.firebaseio.com"
)
FIREBASE_STORAGE_BUCKET: str = os.environ.get(
    "FIREBASE_STORAGE_BUCKET", 
    "nexus-gaming-arena-28be9.firebasestorage.app"
)
FIREBASE_WEB_APP_ID: str = os.environ.get(
    "FIREBASE_WEB_APP_ID", 
    "1:200763746255:web:0bec6f19476e5cccb214ba"
)

def get_firebase_client_config() -> Dict[str, str]:
    """Returns the client-side configuration for Firebase SDK v10."""
    return {
        "apiKey": os.environ.get("FIREBASE_API_KEY", "AIzaSyD6UpsXLrSprM3yznvM5h8ws7-6pjhDM5k"),
        "authDomain": f"{FIREBASE_PROJECT_ID}.firebaseapp.com",
        "databaseURL": FIREBASE_DATABASE_URL,
        "projectId": FIREBASE_PROJECT_ID,
        "storageBucket": FIREBASE_STORAGE_BUCKET,
        "messagingSenderId": "200763746255",
        "appId": FIREBASE_WEB_APP_ID,
        "measurementId": "G-DP38Q4MBK0"
    }

def sync_tournament_to_realtime(tournament_id: str, data: Dict[str, Any]) -> bool:
    """
    Synchronizes a tournament object to Firebase Realtime Database at /live_tournaments/{tournament_id}.json.
    Allows all connected players to see instant real-time lobby updates.
    """
    if not FIREBASE_DATABASE_URL:
        return False

    url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/live_tournaments/{tournament_id}.json"
    try:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={"Content-Type": "application/json"}, 
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in (200, 204)
    except Exception as e:
        logger.warning(f"[Firebase RTDB] Failed to sync tournament {tournament_id}: {e}")
        return False

def broadcast_live_announcement(title: str, message: str, level: str = "INFO") -> Optional[str]:
    """
    Pushes a live esports broadcast announcement to /live_announcements.json.
    """
    if not FIREBASE_DATABASE_URL:
        return None

    import time
    url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/live_announcements.json"
    announcement = {
        "title": title,
        "message": message,
        "level": level,
        "timestamp": int(time.time() * 1000)
    }
    try:
        payload = json.dumps(announcement).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("name")
    except Exception as e:
        logger.warning(f"[Firebase RTDB] Failed to broadcast announcement: {e}")
        return None

def check_firebase_health() -> Dict[str, Any]:
    """
    Checks the connectivity and status of Firebase Realtime Database and Storage.
    """
    status = {
        "project_id": FIREBASE_PROJECT_ID,
        "database_url": FIREBASE_DATABASE_URL,
        "storage_bucket": FIREBASE_STORAGE_BUCKET,
        "rtdb_connected": False,
        "storage_configured": bool(FIREBASE_STORAGE_BUCKET)
    }
    
    # Ping RTDB via shallow read
    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/.json?shallow=true"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                status["rtdb_connected"] = True
    except Exception as e:
        status["rtdb_error"] = str(e)

    return status
