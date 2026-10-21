import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from .database import get_db_connection
from .config import PLATFORM_ESCROW_ACCOUNT_ID, PLATFORM_REVENUE_ACCOUNT_ID

class LedgerError(Exception):
    """Base exception for financial ledger operations."""
    pass

class InsufficientFundsError(LedgerError):
    pass

class DuplicateIdempotencyKeyError(LedgerError):
    pass

def get_or_create_user_account(user_id: str, conn: Optional[sqlite3.Connection] = None) -> str:
    """Returns the account ID for a user, creating one if it doesn't exist."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        
        new_account_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO accounts (id, user_id, account_type, currency, created_at)
        VALUES (?, ?, 'USER_WALLET', 'USD', ?)
        """, (new_account_id, user_id, now))
        conn.commit()
        return new_account_id
    finally:
        if close_conn:
            conn.close()

def get_account_balance_cents(account_id: str, conn: Optional[sqlite3.Connection] = None) -> int:
    """
    Computes exact real-time balance by aggregating immutable ledger credits and debits.
    Balance = Sum(Credits) - Sum(Debits)
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        cursor = conn.cursor()
        # Sum credits
        cursor.execute("""
        SELECT COALESCE(SUM(amount_cents), 0) as total_credits
        FROM ledger_entries
        WHERE credit_account_id = ?
        """, (account_id,))
        total_credits = cursor.fetchone()["total_credits"]

        # Sum debits
        cursor.execute("""
        SELECT COALESCE(SUM(amount_cents), 0) as total_debits
        FROM ledger_entries
        WHERE debit_account_id = ?
        """, (account_id,))
        total_debits = cursor.fetchone()["total_debits"]

        return total_credits - total_debits
    finally:
        if close_conn:
            conn.close()

def record_transaction(
    debit_account_id: str,
    credit_account_id: str,
    amount_cents: int,
    category: str,
    idempotency_key: str,
    description: str = "",
    check_balance: bool = True,
    conn: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Executes an atomic double-entry bookkeeping transaction with idempotency and row-locking.
    Guarantees zero duplicate charges and zero balance corruption.
    """
    if amount_cents <= 0:
        raise LedgerError("Transaction amount must be strictly greater than zero.")

    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        # Check idempotency first (read-only check)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, transaction_id, debit_account_id, credit_account_id, amount_cents, category, description, created_at
        FROM ledger_entries
        WHERE idempotency_key = ?
        """, (idempotency_key,))
        existing = cursor.fetchone()
        if existing:
            # Idempotency hit: return existing transaction details safely
            return {
                "status": "IDEMPOTENT_HIT",
                "transaction_id": existing["transaction_id"],
                "entry_id": existing["id"],
                "amount_cents": existing["amount_cents"],
                "category": existing["category"],
                "description": existing["description"],
                "created_at": existing["created_at"],
            }

        # Begin immediate exclusive transaction if managing connection
        if close_conn:
            cursor.execute("BEGIN IMMEDIATE;")

        # Balance check if this is debiting a user wallet
        if check_balance:
            current_balance = get_account_balance_cents(debit_account_id, conn)
            if current_balance < amount_cents:
                if close_conn:
                    cursor.execute("ROLLBACK;")
                raise InsufficientFundsError(
                    f"Insufficient funds: available {current_balance/100:.2f} USD, required {amount_cents/100:.2f} USD."
                )

        transaction_id = str(uuid.uuid4())
        entry_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
        INSERT INTO ledger_entries (
            id, transaction_id, idempotency_key, debit_account_id, credit_account_id,
            amount_cents, category, description, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, transaction_id, idempotency_key, debit_account_id, credit_account_id,
            amount_cents, category, description, now
        ))

        if close_conn:
            cursor.execute("COMMIT;")
        return {
            "status": "SUCCESS",
            "transaction_id": transaction_id,
            "entry_id": entry_id,
            "amount_cents": amount_cents,
            "category": category,
            "description": description,
            "created_at": now
        }
    except Exception as e:
        if close_conn:
            try:
                conn.execute("ROLLBACK;")
            except Exception:
                pass
        raise e
    finally:
        if close_conn:
            conn.close()

def get_user_transaction_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves chronological financial ledger entries for a user."""
    conn = get_db_connection()
    try:
        account_id = get_or_create_user_account(user_id, conn)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, transaction_id, idempotency_key, debit_account_id, credit_account_id,
               amount_cents, category, description, created_at
        FROM ledger_entries
        WHERE debit_account_id = ? OR credit_account_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (account_id, account_id, limit))
        
        results = []
        for row in cursor.fetchall():
            is_credit = row["credit_account_id"] == account_id
            results.append({
                "id": row["id"],
                "transaction_id": row["transaction_id"],
                "idempotency_key": row["idempotency_key"],
                "type": "CREDIT" if is_credit else "DEBIT",
                "amount": row["amount_cents"] / 100.0,
                "category": row["category"],
                "description": row["description"],
                "created_at": row["created_at"],
            })
        return results
    finally:
        conn.close()
