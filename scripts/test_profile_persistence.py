import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

repo_dir = Path("E:/OfficeServerSuite V2.0/NexusGamingArena")
sys.path.insert(0, str(repo_dir))

from app.main import app
from app.database import init_db, ADMIN_CREDENTIALS_BACKUP_PATH

# Initialize DB migrations explicitly
init_db()

client = TestClient(app)

def test_profile_persistence_suite():
    print("\n=======================================================")
    print("NEXUS GAMING ARENA - PROFILE PICTURE & FOLIO TEST SUITE")
    print("=======================================================\n")

    # 1. Login as Admin
    print("1. Authenticating as Master Admin...")
    admin_login = client.post("/api/auth/login", json={
        "username_or_email": "admin",
        "password": "password123"
    })
    if admin_login.status_code != 200:
        # Try alternate default password
        admin_login = client.post("/api/auth/login", json={
            "username_or_email": "admin",
            "password": "admin"
        })
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_data = admin_login.json()
    admin_token = admin_data["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"   [PASS] Admin logged in successfully: {admin_data['user']['username']}")

    # 2. Update Admin Profile Picture & Folio
    print("\n2. Updating Admin Profile Picture & Folio...")
    custom_admin_avatar = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAPadminCustomAvatarHexCodeTest123"
    admin_update = client.post("/api/users/profile/update", json={
        "avatar_url": custom_admin_avatar,
        "bio": "Supreme Arena Commander & Founder #Founder #Wolfy #Champion",
        "primary_game": "Valorant",
        "in_game_name": "AdminBoss",
        "character_uid": "99887766",
        "clan_name": "Nexus Founders",
        "gaming_rig": "Dual RTX 4090 • 360Hz Alienware",
        "gamer_tags": "#Founder #Wolfy #Supreme"
    }, headers=admin_headers)
    assert admin_update.status_code == 200, f"Admin profile update failed: {admin_update.text}"
    updated_user = admin_update.json()["user"]
    assert updated_user["avatar_url"] == custom_admin_avatar, "Admin avatar was not updated in response"
    assert updated_user["clan_name"] == "Nexus Founders", "Admin clan_name was not updated"
    assert updated_user["gaming_rig"] == "Dual RTX 4090 • 360Hz Alienware"
    print("   [PASS] Admin profile updated in DB and returned in response.")

    # Check lockfile persistence
    assert ADMIN_CREDENTIALS_BACKUP_PATH.exists(), "Admin backup lockfile does not exist"
    lockfile_data = json.loads(ADMIN_CREDENTIALS_BACKUP_PATH.read_text(encoding="utf-8"))
    assert lockfile_data.get("avatar_url") == custom_admin_avatar, f"Lockfile did not persist avatar_url! Got: {lockfile_data.get('avatar_url')}"
    print("   [PASS] Admin custom avatar preserved in disk backup lockfile (.admin_credentials).")

    # 3. Simulate Server Restart / Container Reboot (calling init_db)
    print("\n3. Simulating Server Reboot & init_db() cold run...")
    init_db()
    print("   [PASS] init_db() completed without errors.")

    # Verify admin in DB after reboot
    reboot_login = client.post("/api/auth/login", json={
        "username_or_email": "admin",
        "password": "password123"
    })
    if reboot_login.status_code != 200:
        reboot_login = client.post("/api/auth/login", json={
            "username_or_email": "admin",
            "password": "admin"
        })
    assert reboot_login.status_code == 200
    reboot_user = reboot_login.json()["user"]
    assert reboot_user["avatar_url"] == custom_admin_avatar, f"Reboot reverted admin avatar! Expected {custom_admin_avatar}, got {reboot_user['avatar_url']}"
    assert reboot_user["clan_name"] == "Nexus Founders", "Reboot wiped admin clan name"
    print(f"   [PASS] Admin avatar & folio persisted across server reboot! Avatar: {reboot_user['avatar_url'][:40]}...")

    # 4. Register a standard player and verify profile update & /api/auth/me
    print("\n4. Registering standard player and testing profile customization...")
    import uuid
    uname = f"tester_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "username": uname,
        "email": email,
        "password": "Cyber#Nexus99SecurePass!",
        "phone_number": "+91 9876543210"
    })
    assert reg_resp.status_code == 200
    otp = reg_resp.json().get("demo_otp")
    assert otp, "No demo OTP returned in sandbox mode"

    # Verify account
    ver_resp = client.post("/api/auth/verify-account", json={
        "identifier": email,
        "code": otp
    })
    assert ver_resp.status_code == 200
    player_token = ver_resp.json()["token"]
    player_headers = {"Authorization": f"Bearer {player_token}"}

    # Update player profile picture & folio
    player_avatar = "https://api.dicebear.com/7.x/bottts/svg?seed=CustomPlayerAvatar99"
    player_update = client.post("/api/users/profile/update", json={
        "avatar_url": player_avatar,
        "bio": "Apex predator on the climb #Grindset #Radiant",
        "primary_game": "BGMI",
        "in_game_name": "SniperGhost",
        "character_uid": "5544332211",
        "clan_name": "Ghost Squad",
        "gaming_rig": "ROG Phone 8 Pro",
        "gamer_tags": "#Grindset #Radiant #Sniper"
    }, headers=player_headers)
    assert player_update.status_code == 200
    p_data = player_update.json()["user"]
    assert p_data["avatar_url"] == player_avatar
    assert p_data["in_game_name"] == "SniperGhost"
    assert p_data["gaming_rig"] == "ROG Phone 8 Pro"
    print("   [PASS] Standard player avatar & folio updated successfully.")

    # 5. Verify /api/auth/me returns the customized folio & avatar
    print("\n5. Testing /api/auth/me background hydration...")
    me_resp = client.get("/api/auth/me", headers=player_headers)
    assert me_resp.status_code == 200
    me_user = me_resp.json()["user"]
    assert me_user["avatar_url"] == player_avatar
    assert me_user["bio"] == "Apex predator on the climb #Grindset #Radiant"
    assert me_user["primary_game"] == "BGMI"
    assert me_user["character_uid"] == "5544332211"
    assert me_user["clan_name"] == "Ghost Squad"
    assert me_user["gaming_rig"] == "ROG Phone 8 Pro"
    print("   [PASS] /api/auth/me returns exact persisted avatar and full folio metadata.")

    print("\n=======================================================")
    print("ALL PROFILE PERSISTENCE TESTS PASSED PERFECTLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_profile_persistence_suite()
