"""
Nexus Gaming Arena - Production Clean Start & Demo Data Purge Script
Safely deletes all mock/demo users, tournaments, fake matches, and mock transactions.
Preserves:
- The Master Admin account (username: admin)
- System Escrow and Revenue ledger accounts
- Base games catalog (BGMI, Valorant, Free Fire, etc.)
"""

from app.database import get_db_connection

def purge_all_demo_data():
    conn = get_db_connection()
    c = conn.cursor()

    print("[*] Initiating comprehensive demo data purge...")

    # 1. Clear transactional and gameplay data
    c.execute("DELETE FROM matches")
    c.execute("DELETE FROM tournament_participants")
    c.execute("DELETE FROM tournaments")
    c.execute("DELETE FROM tournament_interests")
    c.execute("DELETE FROM ledger_entries")
    c.execute("DELETE FROM support_tickets")
    c.execute("DELETE FROM video_likes")
    c.execute("DELETE FROM videos")
    c.execute("DELETE FROM otp_codes")
    c.execute("DELETE FROM moogold_orders")
    c.execute("DELETE FROM user_feedback")
    c.execute("DELETE FROM user_quest_progress")

    # 2. Delete non-admin accounts
    c.execute("""
        DELETE FROM accounts 
        WHERE account_type = 'USER_WALLET' 
        AND user_id NOT IN (SELECT id FROM users WHERE username = 'admin')
    """)

    # 3. Delete non-admin financial profiles
    c.execute("""
        DELETE FROM financial_profiles 
        WHERE user_id NOT IN (SELECT id FROM users WHERE username = 'admin')
    """)

    # 4. Delete non-admin 2FA secrets
    c.execute("""
        DELETE FROM user_two_factor_secrets 
        WHERE user_id NOT IN (SELECT id FROM users WHERE username = 'admin')
    """)

    # 5. Delete non-admin users
    c.execute("DELETE FROM users WHERE username != 'admin'")

    # 6. Reset admin statistics to clean starting state
    c.execute("""
        UPDATE users 
        SET tournaments_won = 0,
            matches_played = 0,
            matches_won = 0,
            elo_rating = 1500
        WHERE username = 'admin'
    """)

    conn.commit()

    # Verify counts
    print("\n--- POST-PURGE DATABASE AUDIT ---")
    c.execute("SELECT COUNT(*) as cnt FROM users")
    print(f"Users remaining: {c.fetchone()['cnt']} (Master Admin)")

    c.execute("SELECT COUNT(*) as cnt FROM accounts")
    print(f"Accounts remaining: {c.fetchone()['cnt']} (Escrow, Revenue, Admin)")

    c.execute("SELECT COUNT(*) as cnt FROM ledger_entries")
    print(f"Ledger entries remaining: {c.fetchone()['cnt']} (Pristine zero ledger)")

    c.execute("SELECT COUNT(*) as cnt FROM tournaments")
    print(f"Tournaments remaining: {c.fetchone()['cnt']}")

    c.execute("SELECT COUNT(*) as cnt FROM matches")
    print(f"Matches remaining: {c.fetchone()['cnt']}")

    c.execute("SELECT COUNT(*) as cnt FROM games")
    print(f"Games catalog preserved: {c.fetchone()['cnt']} official titles")
    print("---------------------------------\n")

    conn.close()
    print("[OK] Demo data successfully purged. Clean production testing state ready!")

if __name__ == "__main__":
    purge_all_demo_data()
