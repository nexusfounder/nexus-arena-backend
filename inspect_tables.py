from app.database import get_db_connection

def main():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r['name'] for r in c.fetchall()]
    print("Tables:", tables)
    for t in tables:
        c.execute(f"SELECT count(*) as cnt FROM {t}")
        print(f"  {t}: {c.fetchone()['cnt']} rows")
    conn.close()

if __name__ == "__main__":
    main()
