-- ========================================================================
-- NEXUS GAMING ARENA - SUPABASE POSTGRESQL PRODUCTION SCHEMA & SEED DATA
-- Designed for Supabase SQL Editor (Turnkey One-Click Execution)
-- ========================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
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
    nexus_coins INTEGER DEFAULT 2450,
    referral_code TEXT DEFAULT 'RAJENDRAN_PRO',
    daily_streak INTEGER DEFAULT 4,
    last_claim_date TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. OTP CODES TABLE
CREATE TABLE IF NOT EXISTS otp_codes (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    code TEXT NOT NULL,
    otp_type TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    attempts INTEGER DEFAULT 0,
    verified INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_otp_identifier ON otp_codes(identifier);

-- 3. FINANCIAL ACCOUNTS (WALLETS & ESCROW)
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE,
    account_type TEXT NOT NULL, -- 'USER_WALLET', 'PLATFORM_ESCROW', 'PLATFORM_REVENUE'
    currency TEXT DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. DOUBLE-ENTRY FINANCIAL LEDGER ENTRIES
CREATE TABLE IF NOT EXISTS ledger_entries (
    id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    idempotency_key TEXT UNIQUE NOT NULL,
    debit_account_id TEXT NOT NULL,
    credit_account_id TEXT NOT NULL,
    amount_cents BIGINT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (debit_account_id) REFERENCES accounts(id),
    FOREIGN KEY (credit_account_id) REFERENCES accounts(id)
);
CREATE INDEX IF NOT EXISTS idx_ledger_trans ON ledger_entries(transaction_id);
CREATE INDEX IF NOT EXISTS idx_ledger_debit ON ledger_entries(debit_account_id);
CREATE INDEX IF NOT EXISTS idx_ledger_credit ON ledger_entries(credit_account_id);

-- 5. TOURNAMENTS TABLE
CREATE TABLE IF NOT EXISTS tournaments (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    game_id TEXT NOT NULL,
    game_title TEXT NOT NULL,
    organizer_id TEXT NOT NULL,
    entry_fee_cents BIGINT DEFAULT 0,
    prize_pool_cents BIGINT NOT NULL,
    max_participants INTEGER DEFAULT 16,
    status TEXT DEFAULT 'REGISTRATION', -- 'REGISTRATION', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'POSTPONED'
    format TEXT DEFAULT 'SINGLE_ELIMINATION',
    rules TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    banner_url TEXT,
    game_mode TEXT DEFAULT 'Squad (TPP)',
    map_name TEXT DEFAULT 'Erangel',
    server_region TEXT DEFAULT 'Mumbai AWS',
    coin_entry_fee INTEGER DEFAULT 500,
    urgency_tag TEXT DEFAULT 'FILLING FAST',
    lifecycle_state TEXT DEFAULT 'REGISTRATION',
    views_count INTEGER DEFAULT 0,
    interests_count INTEGER DEFAULT 0,
    registration_opens_at TIMESTAMPTZ,
    registration_deadline TIMESTAMPTZ,
    seeding_type TEXT DEFAULT 'AUTO_MMR',
    cancellation_reason TEXT,
    is_teaser INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (organizer_id) REFERENCES users(id)
);

-- 6. TOURNAMENT PARTICIPANTS
CREATE TABLE IF NOT EXISTS tournament_participants (
    id TEXT PRIMARY KEY,
    tournament_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    checked_in INTEGER DEFAULT 0,
    seed INTEGER DEFAULT 1,
    status TEXT DEFAULT 'ACTIVE',
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tournament_id, user_id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. MATCHES TABLE (BRACKET NODES)
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
    FOREIGN KEY (player_a_id) REFERENCES users(id),
    FOREIGN KEY (player_b_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id)
);

-- 8. GAMEPLAY CLIPS & SHORTS
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 9. VIDEO LIKES
CREATE TABLE IF NOT EXISTS video_likes (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(video_id, user_id),
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. AUDIT LOGS (IMMUTABLE SECURITY LEDGER)
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    ip_address TEXT,
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. GAMERFLICK QUESTS & REWARDS
CREATE TABLE IF NOT EXISTS quests (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    coin_reward INTEGER NOT NULL,
    target_count INTEGER DEFAULT 1,
    icon TEXT DEFAULT 'fa-trophy',
    category TEXT DEFAULT 'DAILY'
);

CREATE TABLE IF NOT EXISTS user_quest_progress (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    quest_id TEXT NOT NULL,
    current_count INTEGER DEFAULT 0,
    is_claimed INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, quest_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
);

-- 12. DYNAMIC GAMES MANAGEMENT
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '🎯',
    category TEXT DEFAULT 'FPS',
    banner_url TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. PRE-TOURNAMENT TEASER INTEREST ANALYZER
CREATE TABLE IF NOT EXISTS tournament_interests (
    id TEXT PRIMARY KEY,
    tournament_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tournament_id, user_id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 14. 24/7 SUPPORT & GRIEVANCE TICKETS
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 15. ENTERPRISE SECTION DELEGATION & CO-ADMIN DIVISION MANAGEMENT
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT 'admin'
);

-- ========================================================================
-- ENABLE ROW LEVEL SECURITY (RLS) WITH TRIAL ACCESS POLICIES
-- ========================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournaments ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournament_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_quest_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournament_interests ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_section_delegations ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Permissive Policies for Testing / Public Trials
DO $$
BEGIN
    EXECUTE 'CREATE POLICY "Public Read Users" ON users FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Tournaments" ON tournaments FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Participants" ON tournament_participants FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Matches" ON matches FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Videos" ON videos FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Quests" ON quests FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Games" ON games FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Delegations" ON admin_section_delegations FOR SELECT USING (true)';
    EXECUTE 'CREATE POLICY "Public Read Interests" ON tournament_interests FOR SELECT USING (true)';
EXCEPTION WHEN duplicate_object THEN
    NULL;
END $$;

-- ========================================================================
-- STARTER SEED DATA (NEXUS GAMING ARENA - FOUNDED BY RAJENDRAN)
-- ========================================================================

-- Insert Platform System Financial Accounts
INSERT INTO accounts (id, user_id, account_type, currency)
VALUES 
    ('00000000-0000-0000-0000-000000000001', NULL, 'PLATFORM_ESCROW', 'USD'),
    ('00000000-0000-0000-0000-000000000002', NULL, 'PLATFORM_REVENUE', 'USD')
ON CONFLICT (id) DO NOTHING;

-- Insert Games
INSERT INTO games (id, name, slug, icon, category, banner_url, is_active)
VALUES
    ('g_val', 'Valorant', 'valorant', '🎯', 'FPS', 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&auto=format&fit=crop&q=80', 1),
    ('g_cs2', 'Counter-Strike 2', 'cs2', '💣', 'FPS', 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&auto=format&fit=crop&q=80', 1),
    ('g_bgmi', 'Battlegrounds Mobile India (BGMI)', 'bgmi', '🪂', 'Battle Royale', 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=80', 1),
    ('g_apex', 'Apex Legends', 'apex', '⚡', 'Battle Royale', 'https://images.unsplash.com/photo-1612287233202-b51a3ed61f5c?w=800&auto=format&fit=crop&q=80', 1),
    ('g_ff', 'Free Fire', 'freefire', '🔥', 'Battle Royale', 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80', 1),
    ('g_codm', 'Call of Duty Mobile', 'codm', '🎖️', 'FPS', 'https://images.unsplash.com/photo-1560253023-3ec5d502959f?w=800&auto=format&fit=crop&q=80', 1),
    ('g_dota2', 'Dota 2', 'dota2', '⚔️', 'MOBA', 'https://images.unsplash.com/photo-1542751110-97427bbecf20?w=800&auto=format&fit=crop&q=80', 1),
    ('g_rl', 'Rocket League', 'rl', '🏎️', 'Sports/Action', 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800&auto=format&fit=crop&q=80', 1)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, icon = EXCLUDED.icon;

-- Insert Daily GamerFlick Quests
INSERT INTO quests (id, title, description, coin_reward, target_count, icon, category)
VALUES
    ('q_first_blood', 'First Blood Daily Scrim', 'Win at least 1 competitive match in Valorant or BGMI.', 150, 1, 'fa-bolt', 'DAILY'),
    ('q_squad_wipe', 'Clutch Vault Uploader', 'Publish a verified gameplay clip or short highlight.', 200, 1, 'fa-video', 'DAILY'),
    ('q_top_fragger', 'Weekend Master Tournament', 'Register and check-in to any open tournament cup.', 500, 1, 'fa-trophy', 'WEEKLY'),
    ('q_invite_squad', 'Squad Recruiter', 'Share your referral code and recruit 1 teammate.', 300, 1, 'fa-users', 'SPECIAL')
ON CONFLICT (id) DO NOTHING;

-- Insert 4 Enterprise Section Delegations
INSERT INTO admin_section_delegations (
    section_key, section_number, section_name, description, assigned_manager_title,
    assigned_username, status, responsibilities, updated_at, updated_by
) VALUES
(
    'tournaments_ops', 1, 'ESPORTS TOURNAMENTS & PLAYER ARENA',
    'Live esports tournaments, elimination brackets, joined player rosters, Elo seeding, and prize escrow operations.',
    'Tournament/Event Organizer & Players Management Manager',
    'NexusCoAdmin', 'ACTIVE',
    'Verify player check-ins, manage live brackets, assign Elo MMR seeds, resolve disputes, approve delayed starts or cancellations.',
    NOW(), 'admin'
),
(
    'community_growth', 2, 'GAMERFLICK SHOWCASE & COMMUNITY HUB',
    'Esports showcase metrics, regional rankings, XP progression, daily quests, coin store, and squad referral boosts.',
    'GAMERFLICK ESPORTS SHOWCASE / GAMERCONNECT Manager',
    'NexusCoAdmin', 'ACTIVE',
    'Monitor regional clan rankings, configure squad referral bonus multipliers, oversee daily quests and coin vouchers inventory.',
    NOW(), 'admin'
),
(
    'media_promotion', 3, 'NEWSDESK, MEDIA LOUNGE & RESOURCES',
    'Official breaking news, press releases, media partnerships, and platform orbital resources hub.',
    'Resources / News and Social Media / Promotion Manager',
    'NexusCoAdmin', 'ACTIVE',
    'Draft and publish official tournament statements, manage media sponsorships, coordinate press releases & community newsletters.',
    NOW(), 'admin'
),
(
    'gallery_video', 4, 'FRAG CLIPS, SHORTS & EVENT GALLERY',
    'High-octane frag highlights, community short clips, and official 4K LAN tournament photo archives.',
    'Gallery and Clips / Shorts / Video Editor Manager',
    'Rajendran_God', 'ACTIVE',
    'Curate community frag video submissions, moderate clips feed, upload and publish high-res LAN championship event photos.',
    NOW(), 'admin'
)
ON CONFLICT (section_key) DO UPDATE SET
    assigned_manager_title = EXCLUDED.assigned_manager_title,
    assigned_username = EXCLUDED.assigned_username,
    status = EXCLUDED.status,
    responsibilities = EXCLUDED.responsibilities;

-- ========================================================================
-- STORAGE BUCKET FOR WEBSITE DEPLOYMENT & TESTING
-- ========================================================================
INSERT INTO storage.buckets (id, name, public, file_size_limit)
VALUES ('nexus-arena', 'nexus-arena', true, 52428800)
ON CONFLICT (id) DO UPDATE SET public = true;

DO $$
BEGIN
    DROP POLICY IF EXISTS "Public Upload nexus-arena" ON storage.objects;
    DROP POLICY IF EXISTS "Public Select nexus-arena" ON storage.objects;
    DROP POLICY IF EXISTS "Public Update nexus-arena" ON storage.objects;

    CREATE POLICY "Public Upload nexus-arena" ON storage.objects 
    FOR INSERT WITH CHECK (bucket_id = 'nexus-arena');

    CREATE POLICY "Public Select nexus-arena" ON storage.objects 
    FOR SELECT USING (bucket_id = 'nexus-arena');

    CREATE POLICY "Public Update nexus-arena" ON storage.objects 
    FOR UPDATE USING (bucket_id = 'nexus-arena');
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

