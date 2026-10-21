import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .config import DB_PATH, PLATFORM_ESCROW_ACCOUNT_ID, PLATFORM_REVENUE_ACCOUNT_ID

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Returns a SQLite connection configured with WAL mode and row factory."""
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency & foreign keys
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    """Initializes database schema and populates starter seed data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table (Table 1: General Account Info)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'PLAYER',
        avatar_url TEXT,
        phone_number TEXT,
        phone_verified INTEGER DEFAULT 0,
        two_factor_secret TEXT,
        two_factor_enabled INTEGER DEFAULT 0,
        discord_tag TEXT,
        steam_id TEXT,
        twitch_channel TEXT,
        twitter_handle TEXT,
        elo_rating INTEGER DEFAULT 1200,
        tournaments_won INTEGER DEFAULT 0,
        matches_played INTEGER DEFAULT 0,
        matches_won INTEGER DEFAULT 0,
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );
    """)

    # 1B. Highly Sensitive 2FA Authentication Data (Table 2: Isolated Security Secrets)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_two_factor_secrets (
        id TEXT PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        encrypted_totp_secret TEXT NOT NULL,
        backup_codes TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_2fa_user_id ON user_two_factor_secrets(user_id);")

    # 1C. Financial Profiles (Table 3: Payment Tracking & Gateway References Only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_profiles (
        id TEXT PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        payment_gateway_customer_id TEXT,
        account_status TEXT DEFAULT 'active',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fin_user_id ON financial_profiles(user_id);")

    # 2. OTP Codes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_codes (
        id TEXT PRIMARY KEY,
        identifier TEXT NOT NULL,
        code TEXT NOT NULL,
        otp_type TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        attempts INTEGER DEFAULT 0,
        verified INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_identifier ON otp_codes(identifier);")

    # 3. Financial Accounts Table (Wallets & Escrow)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        user_id TEXT UNIQUE,
        account_type TEXT NOT NULL,
        currency TEXT DEFAULT 'USD',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 4. Double-Entry Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ledger_entries (
        id TEXT PRIMARY KEY,
        transaction_id TEXT NOT NULL,
        idempotency_key TEXT UNIQUE NOT NULL,
        debit_account_id TEXT NOT NULL,
        credit_account_id TEXT NOT NULL,
        amount_cents INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (debit_account_id) REFERENCES accounts(id),
        FOREIGN KEY (credit_account_id) REFERENCES accounts(id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_trans ON ledger_entries(transaction_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_debit ON ledger_entries(debit_account_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_credit ON ledger_entries(credit_account_id);")

    # 5. Tournaments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournaments (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        game_id TEXT NOT NULL,
        game_title TEXT NOT NULL,
        organizer_id TEXT NOT NULL,
        entry_fee_cents INTEGER DEFAULT 0,
        prize_pool_cents INTEGER NOT NULL,
        max_participants INTEGER DEFAULT 8,
        status TEXT DEFAULT 'REGISTRATION',
        format TEXT DEFAULT 'SINGLE_ELIMINATION',
        rules TEXT,
        start_time TEXT NOT NULL,
        banner_url TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (organizer_id) REFERENCES users(id)
    );
    """)

    # 6. Tournament Participants Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournament_participants (
        id TEXT PRIMARY KEY,
        tournament_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        checked_in INTEGER DEFAULT 0,
        seed INTEGER DEFAULT 1,
        status TEXT DEFAULT 'ACTIVE',
        registered_at TEXT NOT NULL,
        UNIQUE(tournament_id, user_id),
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 7. Matches Table (Bracket Nodes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        tournament_id TEXT NOT NULL,
        round_index INTEGER NOT NULL,
        match_order INTEGER NOT NULL,
        round_name TEXT NOT NULL,
        player_a_id TEXT,
        player_b_id TEXT,
        score_a INTEGER DEFAULT 0,
        score_b INTEGER DEFAULT 0,
        winner_id TEXT,
        status TEXT DEFAULT 'PENDING',
        next_match_id TEXT,
        next_match_slot TEXT,
        evidence_url TEXT,
        dispute_reason TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
        FOREIGN KEY (player_a_id) REFERENCES users(id),
        FOREIGN KEY (player_b_id) REFERENCES users(id),
        FOREIGN KEY (winner_id) REFERENCES users(id)
    );
    """)

    # 8. Gameplay Videos and Shorts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        game_id TEXT NOT NULL,
        video_url TEXT NOT NULL,
        thumbnail_url TEXT,
        likes_count INTEGER DEFAULT 0,
        views_count INTEGER DEFAULT 0,
        duration_seconds INTEGER DEFAULT 30,
        is_short INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 9. Video Likes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_likes (
        id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(video_id, user_id),
        FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 10. Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        action TEXT NOT NULL,
        ip_address TEXT,
        details TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 11. Quests Table (GamerFlick Daily Coin Rewards & Quests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        coin_reward INTEGER NOT NULL,
        target_count INTEGER DEFAULT 1,
        icon TEXT DEFAULT 'fa-trophy',
        category TEXT DEFAULT 'DAILY'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_quest_progress (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        quest_id TEXT NOT NULL,
        current_count INTEGER DEFAULT 0,
        is_claimed INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL,
        UNIQUE(user_id, quest_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
    );
    """)

    # 12. Dynamic Games Table (Admin/Co-Admin Game Management)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        icon TEXT DEFAULT '🎯',
        category TEXT DEFAULT 'FPS',
        banner_url TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # 13. Tournament Interest Analyzer Table (Pre-Tournament Teaser Polls)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournament_interests (
        id TEXT PRIMARY KEY,
        tournament_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(tournament_id, user_id),
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 14. Support & Grievance Tickets Table (Admin / Co-Admin Helpdesk)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id TEXT PRIMARY KEY,
        ticket_number TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        category TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        priority TEXT DEFAULT 'MEDIUM',
        assigned_to TEXT,
        admin_notes TEXT,
        resolution TEXT,
        related_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 15. Homepage Section Delegation & Co-Admin Responsibility Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_section_delegations (
        section_key TEXT PRIMARY KEY,
        section_number INTEGER NOT NULL,
        section_name TEXT NOT NULL,
        description TEXT NOT NULL,
        assigned_manager_title TEXT NOT NULL,
        assigned_user_id TEXT,
        assigned_username TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        responsibilities TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        updated_by TEXT DEFAULT 'admin'
    );
    """)

    # 16. Custom Role Levels Table (Main Admin Role Hierarchy & Governance)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_roles (
        role_key TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        badge_color TEXT NOT NULL DEFAULT 'cyan',
        description TEXT,
        can_access_admin INTEGER DEFAULT 0,
        can_arbitrate INTEGER DEFAULT 0,
        can_organize INTEGER DEFAULT 1,
        can_manage_users INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        created_by TEXT DEFAULT 'Wolfy'
    );
    """)

    # Safe Schema Migrations for GamerFlick, Dynamic Games, and Tournament Lifecycle
    migrations = [
        "ALTER TABLE users ADD COLUMN nexus_coins INTEGER DEFAULT 2450;",
        "ALTER TABLE users ADD COLUMN referral_code TEXT DEFAULT 'WOLFY_PRO';",
        "ALTER TABLE users ADD COLUMN daily_streak INTEGER DEFAULT 4;",
        "ALTER TABLE users ADD COLUMN last_claim_date TEXT;",
        "ALTER TABLE users ADD COLUMN custom_title TEXT;",
        "ALTER TABLE users ADD COLUMN recovery_codes TEXT;",
        "ALTER TABLE users ADD COLUMN bound_phone TEXT DEFAULT '+91 9876543210';",
        "ALTER TABLE users ADD COLUMN bound_email TEXT DEFAULT 'wolfy@nexusarena.gg';",
        "ALTER TABLE users ADD COLUMN authenticator_app_bound INTEGER DEFAULT 1;",
        "ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'ACTIVE';",
        "ALTER TABLE users ADD COLUMN has_claimed_referral INTEGER DEFAULT 0;",
        "ALTER TABLE tournaments ADD COLUMN game_mode TEXT DEFAULT 'Squad (TPP)';",
        "ALTER TABLE tournaments ADD COLUMN map_name TEXT DEFAULT 'Erangel';",
        "ALTER TABLE tournaments ADD COLUMN server_region TEXT DEFAULT 'Mumbai AWS';",
        "ALTER TABLE tournaments ADD COLUMN coin_entry_fee INTEGER DEFAULT 500;",
        "ALTER TABLE tournaments ADD COLUMN urgency_tag TEXT DEFAULT 'FILLING FAST';",
        "ALTER TABLE tournaments ADD COLUMN lifecycle_state TEXT DEFAULT 'REGISTRATION';",
        "ALTER TABLE tournaments ADD COLUMN views_count INTEGER DEFAULT 0;",
        "ALTER TABLE tournaments ADD COLUMN interests_count INTEGER DEFAULT 0;",
        "ALTER TABLE tournaments ADD COLUMN registration_opens_at TEXT;",
        "ALTER TABLE tournaments ADD COLUMN registration_deadline TEXT;",
        "ALTER TABLE tournaments ADD COLUMN seeding_type TEXT DEFAULT 'AUTO_MMR';",
        "ALTER TABLE tournaments ADD COLUMN cancellation_reason TEXT;",
        "ALTER TABLE tournaments ADD COLUMN is_teaser INTEGER DEFAULT 0;",
        "ALTER TABLE tournaments ADD COLUMN room_id TEXT;",
        "ALTER TABLE tournaments ADD COLUMN room_password TEXT;",
        "ALTER TABLE tournaments ADD COLUMN credentials_published_at TEXT;"
    ]
    for mig in migrations:
        try:
            cursor.execute(mig)
        except sqlite3.OperationalError:
            pass

    # 17. MooGold Diamond & Game Credits Order History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS moogold_orders (
        id TEXT PRIMARY KEY,
        order_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        game_id TEXT NOT NULL,
        package_id TEXT NOT NULL,
        diamonds INTEGER NOT NULL,
        amount_paid INTEGER NOT NULL,
        player_uid TEXT NOT NULL,
        zone_id TEXT,
        status TEXT DEFAULT 'COMPLETED',
        moogold_ref TEXT,
        payment_method TEXT DEFAULT 'VAULT_CASH',
        created_at TEXT NOT NULL
    );
    """)

    # 18. Commercial User Feedback & Suggestion Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        username TEXT,
        rating INTEGER DEFAULT 5,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        admin_response TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Part 1 Migration: Ensure isolated Table 2 (2FA secrets) and Table 3 (financial profiles) exist
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("SELECT id, username, two_factor_secret, two_factor_enabled, recovery_codes FROM users")
    existing_users = cursor.fetchall()
    for u in existing_users:
        u_dict = dict(u)
        uid = u_dict["id"]

        # Ensure Table 3: financial_profiles exists for user
        cursor.execute("SELECT id FROM financial_profiles WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            clean_token_id = f"cus_{uid.replace('-', '')[:14]}"
            cursor.execute("""
            INSERT INTO financial_profiles (id, user_id, payment_gateway_customer_id, account_status, created_at, updated_at)
            VALUES (?, ?, ?, 'active', ?, ?)
            """, (str(uuid.uuid4()), uid, clean_token_id, now_iso, now_iso))

        # If user has 2FA secret or 2FA enabled, ensure Table 2: user_two_factor_secrets exists
        raw_secret = u_dict.get("two_factor_secret")
        if raw_secret:
            cursor.execute("SELECT id FROM user_two_factor_secrets WHERE user_id = ?", (uid,))
            if not cursor.fetchone():
                from .security import encrypt_envelope, generate_backup_codes
                enc_secret = encrypt_envelope(raw_secret)
                _, hashed_codes = generate_backup_codes(10)
                cursor.execute("""
                INSERT INTO user_two_factor_secrets (id, user_id, encrypted_totp_secret, backup_codes, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), uid, enc_secret, json.dumps(hashed_codes), now_iso))
    conn.commit()

    # Seed Default Games if Empty
    cursor.execute("SELECT COUNT(*) as count FROM games")
    if cursor.fetchone()["count"] == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        default_games = [
            ("g_val", "Valorant", "valorant", "🎯", "FPS", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_cs2", "Counter-Strike 2", "cs2", "💣", "FPS", "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_bgmi", "Battlegrounds Mobile India (BGMI)", "bgmi", "🪂", "Battle Royale", "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_apex", "Apex Legends", "apex", "⚡", "Battle Royale", "https://images.unsplash.com/photo-1612287233202-b51a3ed61f5c?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_ff", "Free Fire", "freefire", "🔥", "Battle Royale", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_codm", "Call of Duty Mobile", "codm", "🎖️", "FPS", "https://images.unsplash.com/photo-1560253023-3ec5d502959f?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_dota2", "Dota 2", "dota2", "⚔️", "MOBA", "https://images.unsplash.com/photo-1542751110-97427bbecf20?w=800&auto=format&fit=crop&q=80", 1, now_iso),
            ("g_rl", "Rocket League", "rl", "🏎️", "Sports/Action", "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800&auto=format&fit=crop&q=80", 1, now_iso)
        ]
        cursor.executemany("""
        INSERT INTO games (id, name, slug, icon, category, banner_url, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, default_games)

    # Seed Default Daily Quests
    cursor.execute("SELECT COUNT(*) as count FROM quests")
    if cursor.fetchone()["count"] == 0:
        default_quests = [
            ("q_daily_checkin", "Daily Login Check-In", "Sign into Nexus Arena daily to build your streak", 50, 1, "fa-calendar-check", "DAILY"),
            ("q_join_tournament", "Enter Esports Tournament", "Compete in any cash or coin battleground bracket", 100, 1, "fa-trophy", "DAILY"),
            ("q_watch_shorts", "Watch Frag Highlights", "Watch 2 community clutch shorts in the Clips Vault", 50, 2, "fa-circle-play", "DAILY"),
            ("q_refer_squad", "Invite Squad Teammate", "Share your squad referral code with a teammate", 150, 1, "fa-user-group", "COMMUNITY"),
            ("q_clutch_ace", "Clutch Match Victory", "Win an official competitive tournament match", 200, 1, "fa-crosshairs", "ELITE")
        ]
        cursor.executemany("""
        INSERT INTO quests (id, title, description, coin_reward, target_count, icon, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_quests)

    # Seed Default Homepage Section Delegations (4 Key Enterprise Sections)
    cursor.execute("SELECT COUNT(*) as count FROM admin_section_delegations")
    if cursor.fetchone()["count"] == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        default_delegations = [
            (
                "tournaments_ops",
                1,
                "ESPORTS TOURNAMENTS & PLAYER ARENA",
                "Live esports tournaments, elimination brackets, joined player rosters, Elo seeding, and prize escrow operations.",
                "Tournament/Event Organizer & Players Management Manager",
                None,
                "NexusCoAdmin",
                "ACTIVE",
                "Verify player check-ins, manage live brackets, assign Elo MMR seeds, resolve disputes, approve delayed starts or cancellations.",
                now_iso,
                "admin"
            ),
            (
                "community_growth",
                2,
                "GAMERFLICK SHOWCASE & COMMUNITY HUB",
                "Esports showcase metrics, regional rankings, XP progression, daily quests, coin store, and squad referral boosts.",
                "GAMERFLICK ESPORTS SHOWCASE / GAMERCONNECT Manager",
                None,
                "NexusCoAdmin",
                "ACTIVE",
                "Monitor regional clan rankings, configure squad referral bonus multipliers, oversee daily quests and coin vouchers inventory.",
                now_iso,
                "admin"
            ),
            (
                "media_promotion",
                3,
                "NEWSDESK, MEDIA LOUNGE & RESOURCES",
                "Official breaking news, press releases, media partnerships, and platform orbital resources hub.",
                "Resources / News and Social Media / Promotion Manager",
                None,
                "NexusCoAdmin",
                "ACTIVE",
                "Draft and publish official tournament statements, manage media sponsorships, coordinate press releases & community newsletters.",
                now_iso,
                "admin"
            ),
            (
                "gallery_video",
                4,
                "FRAG CLIPS, SHORTS & EVENT GALLERY",
                "High-octane frag highlights, community short clips, and official 4K LAN tournament photo archives.",
                "Gallery and Clips / Shorts / Video Editor Manager",
                None,
                "NexusCoAdmin",
                "ACTIVE",
                "Curate community frag video submissions, moderate clips feed, upload and publish high-res LAN championship event photos.",
                now_iso,
                "admin"
            )
        ]
        cursor.executemany("""
        INSERT INTO admin_section_delegations (
            section_key, section_number, section_name, description, assigned_manager_title,
            assigned_user_id, assigned_username, status, responsibilities, updated_at, updated_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_delegations)

    # Seed Default Custom Roles if Empty
    cursor.execute("SELECT COUNT(*) as count FROM custom_roles")
    if cursor.fetchone()["count"] == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        default_roles = [
            ("TOURNAMENT_ORGANIZER", "Tournament Organizer", "cyan", "Authorized to create and oversee competitive esports brackets & event seeding.", 1, 1, 1, 0, now_iso, "Wolfy"),
            ("CHIEF_REFEREE", "Chief Match Referee", "rose", "Adjudicates match disputes, checks player screenshots, and settles bracket scores.", 1, 1, 0, 0, now_iso, "Wolfy"),
            ("CONTENT_CREATOR", "Verified Content Partner", "purple", "Official streamer with showcase highlight publishing & verified broadcast badge.", 0, 0, 0, 0, now_iso, "Wolfy"),
            ("VIP_AMBASSADOR", "VIP Ambassador", "amber", "Top-tier platform patron with community ambassador status and coin rewards.", 0, 0, 0, 0, now_iso, "Wolfy")
        ]
        cursor.executemany("""
        INSERT INTO custom_roles (
            role_key, title, badge_color, description, can_access_admin,
            can_arbitrate, can_organize, can_manage_users, created_at, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_roles)

    conn.commit()

    # Create System Escrow & Revenue accounts if missing
    cursor.execute("SELECT id FROM accounts WHERE id = ?", (PLATFORM_ESCROW_ACCOUNT_ID,))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO accounts (id, user_id, account_type, currency, created_at)
        VALUES (?, NULL, 'PLATFORM_ESCROW', 'USD', ?)
        """, (PLATFORM_ESCROW_ACCOUNT_ID, datetime.now(timezone.utc).isoformat()))

    cursor.execute("SELECT id FROM accounts WHERE id = ?", (PLATFORM_REVENUE_ACCOUNT_ID,))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO accounts (id, user_id, account_type, currency, created_at)
        VALUES (?, NULL, 'PLATFORM_REVENUE', 'USD', ?)
        """, (PLATFORM_REVENUE_ACCOUNT_ID, datetime.now(timezone.utc).isoformat()))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("NexusArena Database Initialized Successfully!")
