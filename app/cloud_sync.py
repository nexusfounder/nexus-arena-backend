"""
Nexus Gaming Arena - Cloud Synchronization Engine
Synchronizes users, profiles, avatars, and administrative state to Firebase Realtime Database.
Guarantees persistent state across ephemeral server restarts on Render / container reboots.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("nexus.cloud_sync")

FIREBASE_RTDB_URL = "https://nexus-gaming-arena-28be9-default-rtdb.firebaseio.com/cloud_sync"

def cloud_put(path: str, data: Any) -> bool:
    """Executes an atomic PUT to Firebase Realtime Database cloud sync with retry."""
    url = f"{FIREBASE_RTDB_URL}/{path.strip('/')}.json"
    payload = json.dumps(data).encode("utf-8")
    for attempt in range(2):
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                method="PUT",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                return res.status in (200, 204)
        except Exception as e:
            if attempt == 1:
                logger.warning(f"[CloudSync] PUT error at {path}: {e}")
    return False

def cloud_get(path: str) -> Optional[Any]:
    """Retrieves data from Firebase Realtime Database cloud sync with retry."""
    url = f"{FIREBASE_RTDB_URL}/{path.strip('/')}.json"
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as res:
                raw = res.read()
                if not raw or raw == b"null":
                    return None
                return json.loads(raw)
        except Exception as e:
            if attempt == 1:
                logger.warning(f"[CloudSync] GET error at {path}: {e}")
    return None

def cloud_sync_user(user_dict: Dict[str, Any]) -> bool:
    """Synchronizes a user profile to the cloud database."""
    if not user_dict or not user_dict.get("id"):
        return False
    u = dict(user_dict)
    u_id = str(u["id"])
    payload = {
        "id": u_id,
        "username": u.get("username"),
        "email": u.get("email"),
        "password_hash": u.get("password_hash"),
        "role": u.get("role", "PLAYER"),
        "avatar_url": u.get("avatar_url"),
        "bio": u.get("bio") or "",
        "primary_game": u.get("primary_game") or "Valorant",
        "in_game_name": u.get("in_game_name") or u.get("username"),
        "character_uid": u.get("character_uid") or "",
        "clan_name": u.get("clan_name") or "",
        "gaming_rig": u.get("gaming_rig") or "",
        "gamer_tags": u.get("gamer_tags") or "",
        "phone_number": u.get("phone_number"),
        "phone_verified": int(bool(u.get("phone_verified"))),
        "two_factor_enabled": int(bool(u.get("two_factor_enabled"))),
        "two_factor_method": u.get("two_factor_method", "OTP"),
        "status": u.get("status", "ACTIVE"),
        "elo_rating": u.get("elo_rating", 1200),
        "nexus_coins": u.get("nexus_coins", 100),
        "created_at": u.get("created_at")
    }
    return cloud_put(f"users/{u_id}", payload)

def cloud_sync_admin(admin_dict: Dict[str, Any]) -> bool:
    """Synchronizes admin credentials and custom avatar to the cloud database."""
    if not admin_dict:
        return False
    payload = {
        "username": admin_dict.get("username", "admin"),
        "email": admin_dict.get("email", "admin@nexusgamingarena.online"),
        "password_hash": admin_dict.get("password_hash"),
        "avatar_url": admin_dict.get("avatar_url"),
        "updated_at": admin_dict.get("updated_at")
    }
    return cloud_put("admin", payload)

def cloud_get_admin() -> Optional[Dict[str, Any]]:
    """Retrieves current admin credentials and avatar from cloud."""
    return cloud_get("admin")

def cloud_get_all_users() -> Dict[str, Dict[str, Any]]:
    """Retrieves all registered users from the cloud database."""
    users = cloud_get("users")
    if isinstance(users, dict):
        return users
    return {}

def restore_cloud_state_to_db(conn) -> int:
    """
    Called upon server startup in init_db().
    Synchronizes cloud-persisted users and admin into the local SQLite database.
    """
    restored_count = 0
    try:
        cursor = conn.cursor()
        
        # 1. Restore Admin State
        admin_data = cloud_get_admin()
        if admin_data and admin_data.get("username"):
            adm_uname = admin_data["username"]
            adm_avatar = admin_data.get("avatar_url")
            adm_pw_hash = admin_data.get("password_hash")
            adm_email = admin_data.get("email", "admin@nexusgamingarena.online")
            
            cursor.execute("SELECT id, avatar_url, password_hash, username FROM users WHERE role IN ('ADMIN', 'SUPERADMIN') LIMIT 1")
            existing_adm = cursor.fetchone()
            if existing_adm:
                updates = []
                params = []
                if adm_avatar and adm_avatar != existing_adm["avatar_url"]:
                    updates.append("avatar_url = ?")
                    params.append(adm_avatar)
                if adm_pw_hash and adm_pw_hash != existing_adm["password_hash"]:
                    updates.append("password_hash = ?")
                    params.append(adm_pw_hash)
                if adm_uname and adm_uname != existing_adm["username"]:
                    updates.append("username = ?")
                    params.append(adm_uname)
                if updates:
                    params.append(existing_adm["id"])
                    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
                    conn.commit()
                    logger.info(f"[CloudSync] Synchronized admin state from cloud: {updates}")

        # 2. Restore Registered Users
        cloud_users = cloud_get_all_users()
        for u_id, u in cloud_users.items():
            if not isinstance(u, dict) or not u.get("username"):
                continue
            
            cursor.execute("SELECT id, avatar_url, bio, primary_game, in_game_name, character_uid, clan_name, gaming_rig, gamer_tags FROM users WHERE id = ? OR LOWER(username) = LOWER(?)", (u_id, u["username"]))
            existing = cursor.fetchone()
            
            if not existing:
                # User exists in cloud but not in fresh SQLite container -> Insert!
                cursor.execute("""
                INSERT INTO users (
                    id, username, email, password_hash, role, avatar_url, phone_number,
                    phone_verified, two_factor_enabled, two_factor_method, status, elo_rating, nexus_coins,
                    bio, primary_game, in_game_name, character_uid, clan_name, gaming_rig, gamer_tags, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    u.get("id", u_id),
                    u.get("username"),
                    u.get("email"),
                    u.get("password_hash") or "$argon2id$v=19$m=65536,t=3,p=4$dummyHash",
                    u.get("role", "PLAYER"),
                    u.get("avatar_url") or f"https://api.dicebear.com/7.x/bottts/svg?seed={u.get('username')}",
                    u.get("phone_number"),
                    u.get("phone_verified", 1),
                    u.get("two_factor_enabled", 0),
                    u.get("two_factor_method", "OTP"),
                    u.get("status", "ACTIVE"),
                    u.get("elo_rating", 1200),
                    u.get("nexus_coins", 100),
                    u.get("bio") or "",
                    u.get("primary_game") or "Valorant",
                    u.get("in_game_name") or u.get("username"),
                    u.get("character_uid") or "",
                    u.get("clan_name") or "",
                    u.get("gaming_rig") or "",
                    u.get("gamer_tags") or "",
                    u.get("created_at") or "2026-10-24T00:00:00Z"
                ))
                restored_count += 1
            else:
                # User exists -> Update profile picture and folio if cloud has newer custom avatar
                c_avatar = u.get("avatar_url")
                if c_avatar and c_avatar != existing["avatar_url"]:
                    cursor.execute("""
                    UPDATE users SET avatar_url = ?, bio = ?, primary_game = ?, in_game_name = ?, character_uid = ?, clan_name = ?, gaming_rig = ?, gamer_tags = ?
                    WHERE id = ?
                    """, (
                        c_avatar,
                        u.get("bio") or existing["bio"] or "",
                        u.get("primary_game") or existing["primary_game"] or "Valorant",
                        u.get("in_game_name") or existing["in_game_name"] or u.get("username"),
                        u.get("character_uid") or existing["character_uid"] or "",
                        u.get("clan_name") or existing["clan_name"] or "",
                        u.get("gaming_rig") or existing["gaming_rig"] or "",
                        u.get("gamer_tags") or existing["gamer_tags"] or "",
                        existing["id"]
                    ))
                    restored_count += 1
        
        conn.commit()
        if restored_count > 0:
            logger.info(f"[CloudSync] Successfully restored/updated {restored_count} user profiles from cloud database.")
    except Exception as e:
        logger.warning(f"[CloudSync] Error restoring cloud state: {e}")
    return restored_count
