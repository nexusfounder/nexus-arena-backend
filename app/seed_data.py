import uuid
from datetime import datetime, timezone
from .database import get_db_connection, init_db
from .security import hash_password, generate_totp_secret
from .ledger import get_or_create_user_account, record_transaction
from .config import PLATFORM_ESCROW_ACCOUNT_ID
from .tournament_engine import generate_single_elimination_bracket, report_match_result

def seed_database(force: bool = False):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if not force:
        # Check if Wolfy exists
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'Wolfy'")
        if cursor.fetchone()["count"] > 0:
            print("[*] Database already populated with Wolfy's Arena seed data.")
            conn.close()
            return
    else:
        # Clear tables for clean reseed
        cursor.execute("DELETE FROM support_tickets")
        cursor.execute("DELETE FROM tournament_interests")
        cursor.execute("DELETE FROM ledger_entries")
        cursor.execute("DELETE FROM tournament_participants")
        cursor.execute("DELETE FROM matches")
        cursor.execute("DELETE FROM tournaments")
        cursor.execute("DELETE FROM video_likes")
        cursor.execute("DELETE FROM videos")
        cursor.execute("DELETE FROM accounts WHERE account_type = 'USER_WALLET'")
        cursor.execute("DELETE FROM users")
        conn.commit()

    print("[*] Seeding NexusArena with Wolfy's Ultimate Gaming Platform data...")
    now = datetime.now(timezone.utc).isoformat()

    # 1. Seed Core Users
    users_data = [
        {
            "username": "Wolfy",
            "email": "wolfy@gaming.com",
            "password": "password123",
            "role": "ADMIN",
            "avatar_url": "https://images.unsplash.com/photo-1566492031773-4f4e44671857?w=100&auto=format&fit=crop&q=80",
            "phone_number": "+91 9876543210",
            "phone_verified": 1,
            "two_factor_enabled": 1,
            "elo_rating": 2850,
            "tournaments_won": 15,
            "matches_played": 130,
            "matches_won": 118,
            "discord_tag": "Wolfy#0001",
            "steam_id": "76561198012345678",
            "twitch_channel": "wolfy_pro_live"
        },
        {
            "username": "admin",
            "email": "admin@nexusarena.gg",
            "password": "admin",
            "role": "ADMIN",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=admin",
            "phone_number": "+91 9800011122",
            "phone_verified": 1,
            "two_factor_enabled": 0,
            "elo_rating": 2600,
            "tournaments_won": 12,
            "matches_played": 120,
            "matches_won": 108,
            "discord_tag": "NexusAdmin#0001",
            "twitch_channel": "nexus_admin"
        },
        {
            "username": "NexusCoAdmin",
            "email": "coadmin@nexusarena.gg",
            "password": "coadmin123",
            "role": "CO_ADMIN",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=coadmin",
            "phone_number": "+91 9800011133",
            "phone_verified": 1,
            "two_factor_enabled": 0,
            "elo_rating": 2300,
            "tournaments_won": 6,
            "matches_played": 80,
            "matches_won": 65,
            "discord_tag": "NexusCoAdmin#0002",
            "twitch_channel": "nexus_coadmin"
        },
        {
            "username": "CyberPhoenix",
            "email": "cyberphoenix@gaming.com",
            "password": "password123",
            "role": "PLAYER",
            "avatar_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80",
            "phone_number": "+91 9876543211",
            "phone_verified": 1,
            "two_factor_enabled": 1,
            "elo_rating": 2150,
            "tournaments_won": 5,
            "matches_played": 62,
            "matches_won": 49,
            "discord_tag": "Phoenix#7777",
            "twitch_channel": "cyberphoenix"
        },
        {
            "username": "ShadowStriker",
            "email": "shadowstriker@gaming.com",
            "password": "password123",
            "role": "PLAYER",
            "avatar_url": "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&auto=format&fit=crop&q=80",
            "phone_number": "+91 9876543212",
            "phone_verified": 1,
            "two_factor_enabled": 0,
            "elo_rating": 1980,
            "tournaments_won": 4,
            "matches_played": 50,
            "matches_won": 38,
            "discord_tag": "Shadow#1337",
            "steam_id": "76561198099887766"
        },
        {
            "username": "ViperQueen",
            "email": "viperqueen@gaming.com",
            "password": "password123",
            "role": "PLAYER",
            "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80",
            "phone_number": "+91 9876543213",
            "phone_verified": 1,
            "two_factor_enabled": 0,
            "elo_rating": 1850,
            "tournaments_won": 3,
            "matches_played": 42,
            "matches_won": 30,
            "discord_tag": "Viper#9999"
        },
        {
            "username": "NexusTitan",
            "email": "nexustitan@gaming.com",
            "password": "password123",
            "role": "PLAYER",
            "avatar_url": "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=100&auto=format&fit=crop&q=80",
            "phone_number": "+91 9876543214",
            "phone_verified": 0,
            "two_factor_enabled": 0,
            "elo_rating": 1740,
            "tournaments_won": 2,
            "matches_played": 36,
            "matches_won": 25,
            "discord_tag": "Titan#4444"
        },
        {
            "username": "PixelSniper",
            "email": "pixelsniper@gaming.com",
            "password": "password123",
            "role": "PLAYER",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=PixelSniper",
            "phone_number": "+91 9876543215",
            "phone_verified": 1,
            "two_factor_enabled": 0,
            "elo_rating": 1650,
            "tournaments_won": 1,
            "matches_played": 28,
            "matches_won": 19
        },
        {
            "username": "ApexPredator",
            "email": "apexpredator@gaming.com",
            "password": "password123",
            "role": "PLAYER",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=ApexPredator",
            "phone_number": "+91 9876543216",
            "phone_verified": 1,
            "two_factor_enabled": 0,
            "elo_rating": 1580,
            "tournaments_won": 1,
            "matches_played": 24,
            "matches_won": 16
        }
    ]

    user_ids = {}
    for u in users_data:
        uid = str(uuid.uuid4())
        user_ids[u["username"]] = uid
        totp_sec = generate_totp_secret() if u["two_factor_enabled"] else None
        cursor.execute("""
        INSERT INTO users (
            id, username, email, password_hash, role, avatar_url,
            phone_number, phone_verified, two_factor_secret, two_factor_enabled,
            elo_rating, tournaments_won, matches_played, matches_won,
            discord_tag, steam_id, twitch_channel, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uid, u["username"], u["email"], hash_password(u["password"]), u["role"], u["avatar_url"],
            u.get("phone_number"), u.get("phone_verified", 0), totp_sec, u.get("two_factor_enabled", 0),
            u["elo_rating"], u["tournaments_won"], u["matches_played"], u["matches_won"],
            u.get("discord_tag"), u.get("steam_id"), u.get("twitch_channel"), now
        ))

    conn.commit()

    # 2. Setup Wallets & Seed Real Double-Entry Ledger Transactions
    # Wolfy gets exact ₹50,000 balance!
    wolfy_id = user_ids["Wolfy"]
    r_acc = get_or_create_user_account(wolfy_id, conn)

    # Initial deposit ₹10,000
    record_transaction(
        debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
        credit_account_id=r_acc,
        amount_cents=1000000, # ₹10,000.00
        category="DEPOSIT",
        idempotency_key="TXN-97211",
        description="Wallet Top-up (UPI / GPay)",
        check_balance=False
    )

    # Entry fee -₹500
    record_transaction(
        debit_account_id=r_acc,
        credit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
        amount_cents=50000, # ₹500.00
        category="ENTRY_FEE",
        idempotency_key="TXN-98102",
        description="Entry Fee: Valorant Cup",
        check_balance=False
    )

    # Tournament Prize +₹25,500 (yielding exact ₹35,000)
    record_transaction(
        debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
        credit_account_id=r_acc,
        amount_cents=2550000, # ₹25,500.00
        category="PRIZE_PAYOUT",
        idempotency_key="TXN-98421",
        description="Tournament Prizepool Credit",
        check_balance=False
    )

    # Admin wallet
    admin_acc = get_or_create_user_account(user_ids["admin"], conn)
    record_transaction(
        debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
        credit_account_id=admin_acc,
        amount_cents=100000000, # ₹10,00,000
        category="DEPOSIT",
        idempotency_key="admin_seed_wallet",
        description="Platform Admin Escrow Reserve",
        check_balance=False
    )

    # Other players
    for uname, uid in user_ids.items():
        if uname not in ("Wolfy", "admin"):
            acc = get_or_create_user_account(uid, conn)
            record_transaction(
                debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
                credit_account_id=acc,
                amount_cents=500000, # ₹5,000
                category="DEPOSIT",
                idempotency_key=f"seed_dep_{uid}",
                description="Esports Starter Wallet",
                check_balance=False
            )

    # 3. Create the 6 Tournaments from User's UI
    tournaments = [
        {
            "id": str(uuid.uuid4()),
            "title": "Valorant Pro Champions Cup",
            "game_id": "valorant",
            "game_title": "Valorant",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 50000,    # ₹500
            "prize_pool_cents": 15000000, # ₹1,50,000
            "max_participants": 8,
            "status": "IN_PROGRESS",
            "format": "SINGLE_ELIMINATION",
            "rules": "5v5 Competitive ruleset. Standard active map pool. Anti-cheat required.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "BGMI National Championship Masters",
            "game_id": "bgmi",
            "game_title": "BGMI",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 0,        # Free
            "prize_pool_cents": 25000000, # ₹2,50,000
            "max_participants": 16,
            "status": "REGISTRATION",
            "format": "SINGLE_ELIMINATION",
            "rules": "Erangel & Miramar. Mobile devices only. Emulators strictly banned.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "CS2 Elite Showdown Arena",
            "game_id": "cs2",
            "game_title": "CS2",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 30000,    # ₹300
            "prize_pool_cents": 7500000,  # ₹75,000
            "max_participants": 8,
            "status": "REGISTRATION",
            "format": "SINGLE_ELIMINATION",
            "rules": "MR12 format, active duty map pool. Captains veto in lobby.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Free Fire Apex Rumble",
            "game_id": "freefire",
            "game_title": "Free Fire",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 0,        # Free
            "prize_pool_cents": 5000000,  # ₹50,000
            "max_participants": 8,
            "status": "REGISTRATION",
            "format": "SINGLE_ELIMINATION",
            "rules": "Bermuda clash squad tournament. Mobile only.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Apex Legends Nexus Clash",
            "game_id": "apex",
            "game_title": "Apex Legends",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 40000,    # ₹400
            "prize_pool_cents": 8000000,  # ₹80,000
            "max_participants": 8,
            "status": "REGISTRATION",
            "format": "SINGLE_ELIMINATION",
            "rules": "Trio squad battle royale scoring.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1612287233202-b51a3ed61f5c?w=800&auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Call of Duty Mobile Blitz",
            "game_id": "codm",
            "game_title": "COD Mobile",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 25000,    # ₹250
            "prize_pool_cents": 6000000,  # ₹60,000
            "max_participants": 8,
            "status": "REGISTRATION",
            "format": "SINGLE_ELIMINATION",
            "rules": "Search and Destroy 5v5 competitive.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1560253023-3ec5d502959f?w=800&auto=format&fit=crop&q=80",
            "views_count": 84,
            "interests_count": 9,
            "lifecycle_state": "REGISTRATION",
            "is_teaser": 0
        },
        {
            "id": "t_freefire_teaser",
            "title": "Free Fire Mega League 2026 (Teaser)",
            "game_id": "freefire",
            "game_title": "Free Fire",
            "organizer_id": user_ids["admin"],
            "entry_fee_cents": 10000,    # ₹100
            "prize_pool_cents": 2500000,  # ₹25,000
            "max_participants": 16,
            "status": "REGISTRATION",
            "lifecycle_state": "TEASER",
            "format": "SINGLE_ELIMINATION",
            "rules": "Community voting teaser poll to evaluate squad demand before official announcement.",
            "start_time": now,
            "banner_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",
            "views_count": 210,
            "interests_count": 18,
            "is_teaser": 1
        }
    ]

    for t in tournaments:
        cursor.execute("""
        INSERT INTO tournaments (
            id, title, game_id, game_title, organizer_id, entry_fee_cents,
            prize_pool_cents, max_participants, status, format, rules,
            start_time, banner_url, created_at, lifecycle_state,
            views_count, interests_count, is_teaser, seeding_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["id"], t["title"], t["game_id"], t["game_title"], t["organizer_id"],
            t["entry_fee_cents"], t["prize_pool_cents"], t["max_participants"],
            t["status"], t["format"], t["rules"], t["start_time"], t["banner_url"], now,
            t.get("lifecycle_state", "REGISTRATION"),
            t.get("views_count", 45),
            t.get("interests_count", 6),
            t.get("is_teaser", 0),
            t.get("seeding_type", "AUTO_MMR")
        ))

    conn.commit()

    # 4. Generate Live Bracket for Valorant Pro Champions Cup
    active_t_id = tournaments[0]["id"]
    bracket_participants = [
        user_ids["Wolfy"],
        user_ids["CyberPhoenix"],
        user_ids["ShadowStriker"],
        user_ids["ViperQueen"],
        user_ids["NexusTitan"],
        user_ids["PixelSniper"],
        user_ids["ApexPredator"],
        user_ids["admin"]
    ]

    for p_id in bracket_participants:
        cursor.execute("""
        INSERT INTO tournament_participants (id, tournament_id, user_id, checked_in, registered_at)
        VALUES (?, ?, ?, 1, ?)
        """, (str(uuid.uuid4()), active_t_id, p_id, now))
    conn.commit()

    generate_single_elimination_bracket(active_t_id, bracket_participants)

    # Simulate Round 1 completed matches with live progression
    cursor.execute("""
    SELECT id FROM matches 
    WHERE tournament_id = ? AND round_index = 1 AND status = 'READY'
    ORDER BY match_order ASC
    """, (active_t_id,))
    r1_matches = cursor.fetchall()
    
    if len(r1_matches) >= 4:
        report_match_result(r1_matches[0]["id"], score_a=13, score_b=8, reported_by_user_id=user_ids["admin"])
        report_match_result(r1_matches[1]["id"], score_a=13, score_b=11, reported_by_user_id=user_ids["admin"])
        report_match_result(r1_matches[2]["id"], score_a=13, score_b=9, reported_by_user_id=user_ids["admin"])
        report_match_result(r1_matches[3]["id"], score_a=13, score_b=6, reported_by_user_id=user_ids["admin"])

    # 5. Populate Gameplay Videos & Clips
    videos = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_ids["Wolfy"],
            "title": "Insane 1v5 Vandal Ace in Grand Finals!",
            "game_id": "valorant",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "thumbnail_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&auto=format&fit=crop&q=80",
            "likes_count": 1420,
            "views_count": 8920,
            "duration_seconds": 15,
            "is_short": 1
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_ids["CyberPhoenix"],
            "title": "1000m Headshot Sniper Clutch on Miramar",
            "game_id": "bgmi",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "thumbnail_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=80",
            "likes_count": 980,
            "views_count": 5400,
            "duration_seconds": 22,
            "is_short": 1
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_ids["ShadowStriker"],
            "title": "CS2 Mirage A-Site Smoke & Exec Breakdown",
            "game_id": "cs2",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "thumbnail_url": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&auto=format&fit=crop&q=80",
            "likes_count": 1150,
            "views_count": 6200,
            "duration_seconds": 28,
            "is_short": 1
        }
    ]

    for v in videos:
        cursor.execute("""
        INSERT INTO videos (
            id, user_id, title, game_id, video_url, thumbnail_url,
            likes_count, views_count, duration_seconds, is_short, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            v["id"], v["user_id"], v["title"], v["game_id"], v["video_url"],
            v["thumbnail_url"], v["likes_count"], v["views_count"],
            v["duration_seconds"], v["is_short"], now
        ))

    # 6. Seed Teaser Pre-Registration Interest Votes
    sample_interests = [
        (str(uuid.uuid4()), "t_freefire_teaser", user_ids["Wolfy"], now),
        (str(uuid.uuid4()), "t_freefire_teaser", user_ids["CyberPhoenix"], now),
        (str(uuid.uuid4()), "t_freefire_teaser", user_ids["ShadowStriker"], now)
    ]
    cursor.executemany("""
    INSERT INTO tournament_interests (id, tournament_id, user_id, created_at)
    VALUES (?, ?, ?, ?)
    """, sample_interests)

    # 7. Seed Admin / Co-Admin Support Tickets (Help & Grievance Desk)
    sample_tickets = [
        (
            str(uuid.uuid4()),
            "TICK-8001",
            user_ids["CyberPhoenix"],
            "FINANCIAL",
            "Payment Gateway Escrow Verification Delay",
            "Razorpay UPI transaction of ₹1,000 for tournament entry pass is taking longer than 60 seconds to reflect in wallet balance.",
            "OPEN",
            "HIGH",
            None,
            "Awaiting automated webhook reconciliation.",
            None,
            "TXN-97211",
            now,
            now
        ),
        (
            str(uuid.uuid4()),
            "TICK-8002",
            user_ids["ShadowStriker"],
            "MATCH_DISPUTE",
            "Score Discrepancy in Quarterfinals Match",
            "Opposing team reported 13-9 but official match screenshots verify final score was 13-11. Requesting referee review.",
            "IN_PROGRESS",
            "MEDIUM",
            user_ids["NexusCoAdmin"],
            "Referee assigned. Screenshot evidence under review.",
            None,
            "m_val_qf1",
            now,
            now
        ),
        (
            str(uuid.uuid4()),
            "TICK-8003",
            user_ids["PixelSniper"],
            "ACCOUNT_2FA",
            "Google Authenticator Recovery Request",
            "Replaced mobile device and need backup verification code to re-link TOTP 2-Factor Authentication.",
            "RESOLVED",
            "LOW",
            user_ids["admin"],
            "Identity verified via registered SMS OTP.",
            "Backup 2FA seed regenerated and sent to verified email.",
            None,
            now,
            now
        )
    ]
    cursor.executemany("""
    INSERT INTO support_tickets (
        id, ticket_number, user_id, category, subject, description,
        status, priority, assigned_to, admin_notes, resolution, related_id,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_tickets)

    conn.commit()
    conn.close()
    print("[+] NexusArena successfully seeded with Wolfy's Arena tournaments and records!")

if __name__ == "__main__":
    seed_database(force=True)

