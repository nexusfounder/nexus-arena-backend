import uuid
import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .database import get_db_connection
from .ledger import record_transaction, get_or_create_user_account
from .config import PLATFORM_ESCROW_ACCOUNT_ID, PLATFORM_REVENUE_ACCOUNT_ID

# K-factor for Elo rating updates
ELO_K_FACTOR = 32

def calculate_elo(winner_rating: int, loser_rating: int) -> tuple[int, int]:
    """Calculates updated Elo ratings using standard chess/esports formula."""
    expected_winner = 1.0 / (1.0 + 10.0 ** ((loser_rating - winner_rating) / 400.0))
    expected_loser = 1.0 / (1.0 + 10.0 ** ((winner_rating - loser_rating) / 400.0))

    new_winner_rating = round(winner_rating + ELO_K_FACTOR * (1.0 - expected_winner))
    new_loser_rating = round(loser_rating + ELO_K_FACTOR * (0.0 - expected_loser))
    return max(100, new_winner_rating), max(100, new_loser_rating)

def generate_esports_seed_order(n: int) -> List[int]:
    """
    Generates standard professional esports seed pairings (e.g. 1 vs 8, 4 vs 5, 2 vs 7, 3 vs 6).
    Ensures top seeds (Seed 1 & Seed 2) can only meet in the Grand Final.
    """
    if n <= 1:
        return [1]
    rounds = int(math.log2(n))
    seed_list = [1, 2]
    for _ in range(rounds - 1):
        next_seeds = []
        target_sum = len(seed_list) * 2 + 1
        for s in seed_list:
            next_seeds.append(s)
            next_seeds.append(target_sum - s)
        seed_list = next_seeds
    return seed_list

def generate_single_elimination_bracket(tournament_id: str, participant_ids: List[str], seeding_type: str = "AUTO_MMR") -> List[str]:
    """
    Generates a full binary tree elimination bracket for N participants.
    Supports esports AUTO_MMR seeding (based on Elo) and MANUAL seeding.
    Returns list of generated match IDs.
    """
    num_participants = len(participant_ids)
    if num_participants < 2:
        raise ValueError("At least 2 participants required to generate a bracket.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Find next power of 2
        bracket_size = 1 << (num_participants - 1).bit_length()
        total_rounds = int(math.log2(bracket_size))

        # Seeding logic:
        # Fetch players with their Elo ratings and manual seed numbers
        cursor.execute("""
        SELECT u.id, u.elo_rating, tp.seed
        FROM users u
        LEFT JOIN tournament_participants tp ON u.id = tp.user_id AND tp.tournament_id = ?
        WHERE u.id IN ({})
        """.format(','.join(['?'] * num_participants)), (tournament_id, *participant_ids))
        player_rows = cursor.fetchall()
        player_map = {row["id"]: dict(row) for row in player_rows}

        if seeding_type == "AUTO_MMR":
            # Sort descending by Elo (Rank 1 = highest Elo MMR)
            ranked_players = sorted(participant_ids, key=lambda pid: player_map.get(pid, {}).get("elo_rating", 1000), reverse=True)
        elif seeding_type == "MANUAL":
            # Sort ascending by manual seed number (Seed 1, 2, 3...)
            ranked_players = sorted(participant_ids, key=lambda pid: player_map.get(pid, {}).get("seed", 999))
        else:
            ranked_players = list(participant_ids)

        # Update seeds in tournament_participants table
        for idx, pid in enumerate(ranked_players, start=1):
            cursor.execute("UPDATE tournament_participants SET seed = ? WHERE tournament_id = ? AND user_id = ?", (idx, tournament_id, pid))

        # Generate esports seed pairings
        seed_orders = generate_esports_seed_order(bracket_size)
        seeded_players: List[Optional[str]] = [None] * bracket_size

        for bracket_slot, seed_num in enumerate(seed_orders):
            if seed_num <= num_participants:
                seeded_players[bracket_slot] = ranked_players[seed_num - 1]
            else:
                seeded_players[bracket_slot] = None  # Bye

        match_ids = []

        # Round names mapping
        def get_round_name(round_num: int, total: int) -> str:
            distance_from_final = total - round_num
            if distance_from_final == 1:
                return "Grand Final"
            elif distance_from_final == 2:
                return "Semifinals"
            elif distance_from_final == 3:
                return "Quarterfinals"
            elif distance_from_final == 4:
                return "Round of 16"
            return f"Round {round_num}"

        # Build from Final backwards to link next_match_id correctly
        rounds_matches: Dict[int, List[Dict[str, Any]]] = {}

        for r in range(1, total_rounds + 1):
            matches_in_round = bracket_size // (2 ** r)
            rounds_matches[r] = []
            round_title = get_round_name(r, total_rounds)
            for m in range(matches_in_round):
                match_id = str(uuid.uuid4())
                rounds_matches[r].append({
                    "id": match_id,
                    "round_index": r,
                    "match_order": m,
                    "round_name": round_title,
                    "player_a_id": None,
                    "player_b_id": None,
                    "next_match_id": None,
                    "next_match_slot": None,
                    "status": "PENDING"
                })

        # Link parent matches
        for r in range(1, total_rounds):
            next_round = r + 1
            for m_idx, match in enumerate(rounds_matches[r]):
                parent_idx = m_idx // 2
                slot = "A" if m_idx % 2 == 0 else "B"
                parent_match = rounds_matches[next_round][parent_idx]
                match["next_match_id"] = parent_match["id"]
                match["next_match_slot"] = slot

        # Seed Round 1 participants
        for i in range(0, bracket_size, 2):
            match_idx = i // 2
            p_a = seeded_players[i]
            p_b = seeded_players[i + 1] if (i + 1) < len(seeded_players) else None
            rounds_matches[1][match_idx]["player_a_id"] = p_a
            rounds_matches[1][match_idx]["player_b_id"] = p_b

            # If both players present, status is READY
            if p_a and p_b:
                rounds_matches[1][match_idx]["status"] = "READY"
            elif p_a and not p_b:
                # Bye for player A: auto advance
                rounds_matches[1][match_idx]["winner_id"] = p_a
                rounds_matches[1][match_idx]["status"] = "COMPLETED"
            elif not p_a and p_b:
                # Bye for player B: auto advance
                rounds_matches[1][match_idx]["winner_id"] = p_b
                rounds_matches[1][match_idx]["status"] = "COMPLETED"

        # Save all matches to DB
        now = datetime.now(timezone.utc).isoformat()
        for r in range(1, total_rounds + 1):
            for m in rounds_matches[r]:
                cursor.execute("""
                INSERT INTO matches (
                    id, tournament_id, round_index, match_order, round_name,
                    player_a_id, player_b_id, winner_id, status,
                    next_match_id, next_match_slot, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    m["id"], tournament_id, m["round_index"], m["match_order"], m["round_name"],
                    m["player_a_id"], m["player_b_id"], m.get("winner_id"), m["status"],
                    m["next_match_id"], m["next_match_slot"], now
                ))
                match_ids.append(m["id"])

                # If Round 1 match had a bye, advance player to next match
                if m.get("winner_id") and m.get("next_match_id"):
                    slot = m["next_match_slot"]
                    col = "player_a_id" if slot == "A" else "player_b_id"
                    cursor.execute(f"UPDATE matches SET {col} = ? WHERE id = ?", (m["winner_id"], m["next_match_id"]))

        conn.commit()
        return match_ids
    finally:
        conn.close()

def report_match_result(
    match_id: str,
    score_a: int,
    score_b: int,
    reported_by_user_id: str,
    evidence_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submits match scores, determines winner, advances winner in bracket,
    updates player Elo ratings, and distributes prize pool if this is the Grand Final.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
        match = cursor.fetchone()
        if not match:
            raise ValueError("Match not found.")

        if match["status"] == "COMPLETED":
            return {"status": "ALREADY_COMPLETED", "winner_id": match["winner_id"]}

        # Determine winner
        if score_a == score_b:
            raise ValueError("Ties are not allowed in elimination matches. Play overtime!")

        winner_id = match["player_a_id"] if score_a > score_b else match["player_b_id"]
        loser_id = match["player_b_id"] if score_a > score_b else match["player_a_id"]

        now = datetime.now(timezone.utc).isoformat()

        # Update Match
        cursor.execute("""
        UPDATE matches
        SET score_a = ?, score_b = ?, winner_id = ?, status = 'COMPLETED',
            evidence_url = ?
        WHERE id = ?
        """, (score_a, score_b, winner_id, evidence_url, match_id))

        # Update Player Stats & Elo
        if winner_id and loser_id:
            cursor.execute("SELECT elo_rating, matches_won, matches_played FROM users WHERE id = ?", (winner_id,))
            winner_data = cursor.fetchone()
            cursor.execute("SELECT elo_rating, matches_played FROM users WHERE id = ?", (loser_id,))
            loser_data = cursor.fetchone()

            if winner_data and loser_data:
                new_w_elo, new_l_elo = calculate_elo(winner_data["elo_rating"], loser_data["elo_rating"])
                cursor.execute("""
                UPDATE users
                SET elo_rating = ?, matches_won = matches_won + 1, matches_played = matches_played + 1
                WHERE id = ?
                """, (new_w_elo, winner_id))

                cursor.execute("""
                UPDATE users
                SET elo_rating = ?, matches_played = matches_played + 1
                WHERE id = ?
                """, (new_l_elo, loser_id))

        # Advance to next match if there is a parent match
        if match["next_match_id"] and match["next_match_slot"]:
            next_col = "player_a_id" if match["next_match_slot"] == "A" else "player_b_id"
            cursor.execute(f"UPDATE matches SET {next_col} = ? WHERE id = ?", (winner_id, match["next_match_id"]))
            
            # Check if both players are now populated in next match
            cursor.execute("SELECT player_a_id, player_b_id FROM matches WHERE id = ?", (match["next_match_id"],))
            next_m = cursor.fetchone()
            if next_m and next_m["player_a_id"] and next_m["player_b_id"]:
                cursor.execute("UPDATE matches SET status = 'READY' WHERE id = ?", (match["next_match_id"],))
        else:
            # THIS WAS THE GRAND FINAL!
            tournament_id = match["tournament_id"]
            cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
            tournament = cursor.fetchone()

            cursor.execute("UPDATE tournaments SET status = 'COMPLETED' WHERE id = ?", (tournament_id,))
            cursor.execute("UPDATE users SET tournaments_won = tournaments_won + 1 WHERE id = ?", (winner_id,))

            # Automatic Escrow Prize Payout
            prize_pool_cents = tournament["prize_pool_cents"]
            if prize_pool_cents > 0:
                winner_account_id = get_or_create_user_account(winner_id, conn)
                idempotency_key = f"prize_payout_{tournament_id}_{winner_id}"
                record_transaction(
                    debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
                    credit_account_id=winner_account_id,
                    amount_cents=prize_pool_cents,
                    category="PRIZE_PAYOUT",
                    idempotency_key=idempotency_key,
                    description=f"1st Place Prize for {tournament['title']}",
                    check_balance=False,
                    conn=conn
                )

        conn.commit()
        return {
            "status": "COMPLETED",
            "winner_id": winner_id,
            "score_a": score_a,
            "score_b": score_b,
            "is_final": match["next_match_id"] is None
        }
    finally:
        conn.close()

def raise_match_dispute(match_id: str, user_id: str, reason: str, evidence_url: Optional[str] = None) -> Dict[str, Any]:
    """Freezes the match and notifies referees of a disputed result."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE matches
        SET status = 'DISPUTED', dispute_reason = ?, evidence_url = COALESCE(?, evidence_url)
        WHERE id = ?
        """, (reason, evidence_url, match_id))
        conn.commit()
        return {"status": "DISPUTED", "match_id": match_id, "reason": reason}
    finally:
        conn.close()

def cancel_tournament_with_refunds(tournament_id: str, cancelled_by_user_id: str, reason: str = "Lack of participants") -> Dict[str, Any]:
    """
    Cancels a tournament and executes guaranteed 100% automated refunds:
    1. Refunds cash entry fees from PLATFORM_ESCROW to all registered participants via double-entry ledger.
    2. Refunds Nexus Coins to all participants who entered using coins.
    3. Releases and refunds organizer's prize pool escrow hold back to organizer's wallet.
    4. Marks tournament status = 'CANCELLED' and records audit log.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
        tournament = cursor.fetchone()
        if not tournament:
            raise ValueError("Tournament not found.")

        if tournament["status"] in ("CANCELLED", "COMPLETED"):
            raise ValueError(f"Tournament is already {tournament['status']}.")

        now_iso = datetime.now(timezone.utc).isoformat()
        entry_fee_cents = tournament["entry_fee_cents"] or 0
        coin_entry_fee = tournament["coin_entry_fee"] or 0
        prize_pool_cents = tournament["prize_pool_cents"] or 0
        organizer_id = tournament["organizer_id"]

        # Fetch participants
        cursor.execute("SELECT user_id, status FROM tournament_participants WHERE tournament_id = ?", (tournament_id,))
        participants = cursor.fetchall()

        refunded_participants = 0
        total_cash_refunded_cents = 0
        total_coins_refunded = 0

        for p in participants:
            user_id = p["user_id"]
            # Cash refund if fee was > 0
            if entry_fee_cents > 0:
                user_account_id = get_or_create_user_account(user_id, conn)
                idempotency_key = f"tournament_cancel_refund_{tournament_id}_{user_id}"
                record_transaction(
                    debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
                    credit_account_id=user_account_id,
                    amount_cents=entry_fee_cents,
                    category="TOURNAMENT_REFUND",
                    idempotency_key=idempotency_key,
                    description=f"100% Refund: Tournament '{tournament['title']}' cancelled ({reason})",
                    check_balance=False,
                    conn=conn
                )
                total_cash_refunded_cents += entry_fee_cents

            # Coin refund if coins entry fee
            if coin_entry_fee > 0:
                cursor.execute("UPDATE users SET nexus_coins = nexus_coins + ? WHERE id = ?", (coin_entry_fee, user_id))
                total_coins_refunded += coin_entry_fee

            cursor.execute("UPDATE tournament_participants SET status = 'REFUNDED' WHERE tournament_id = ? AND user_id = ?", (tournament_id, user_id))
            refunded_participants += 1

        # Organizer prize pool escrow refund
        if prize_pool_cents > 0 and organizer_id:
            org_account_id = get_or_create_user_account(organizer_id, conn)
            idempotency_key = f"organizer_prize_refund_{tournament_id}"
            record_transaction(
                debit_account_id=PLATFORM_ESCROW_ACCOUNT_ID,
                credit_account_id=org_account_id,
                amount_cents=prize_pool_cents,
                category="ESCROW_RELEASE",
                idempotency_key=idempotency_key,
                description=f"Prize pool escrow returned for cancelled tournament '{tournament['title']}'",
                check_balance=False,
                conn=conn
            )

        # Update tournament record
        cursor.execute("""
        UPDATE tournaments
        SET status = 'CANCELLED', lifecycle_state = 'CANCELLED', cancellation_reason = ?
        WHERE id = ?
        """, (reason, tournament_id))

        # Audit log
        cursor.execute("""
        INSERT INTO audit_logs (id, user_id, action, details, created_at)
        VALUES (?, ?, 'TOURNAMENT_CANCELLED', ?, ?)
        """, (
            str(uuid.uuid4()),
            cancelled_by_user_id,
            f"Tournament {tournament_id} cancelled. Reason: {reason}. Refunded {refunded_participants} players (${total_cash_refunded_cents/100:.2f}, {total_coins_refunded} coins).",
            now_iso
        ))

        conn.commit()
        return {
            "status": "CANCELLED",
            "tournament_id": tournament_id,
            "refunded_players_count": refunded_participants,
            "total_cash_refunded": total_cash_refunded_cents / 100.0,
            "total_coins_refunded": total_coins_refunded,
            "cancellation_reason": reason
        }
    finally:
        conn.close()

def postpone_tournament(
    tournament_id: str,
    postponed_by_user_id: str,
    new_start_time: str,
    new_registration_deadline: Optional[str] = None,
    reason: str = "Registration window extended"
) -> Dict[str, Any]:
    """
    Extends/postpones tournament schedule and deadline.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
        tournament = cursor.fetchone()
        if not tournament:
            raise ValueError("Tournament not found.")

        now_iso = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        UPDATE tournaments
        SET start_time = ?,
            registration_deadline = COALESCE(?, registration_deadline),
            lifecycle_state = 'POSTPONED'
        WHERE id = ?
        """, (new_start_time, new_registration_deadline, tournament_id))

        cursor.execute("""
        INSERT INTO audit_logs (id, user_id, action, details, created_at)
        VALUES (?, ?, 'TOURNAMENT_POSTPONED', ?, ?)
        """, (
            str(uuid.uuid4()),
            postponed_by_user_id,
            f"Tournament {tournament_id} postponed to {new_start_time}. Reason: {reason}",
            now_iso
        ))

        conn.commit()
        return {
            "status": "POSTPONED",
            "tournament_id": tournament_id,
            "new_start_time": new_start_time,
            "new_registration_deadline": new_registration_deadline,
            "reason": reason
        }
    finally:
        conn.close()

def update_tournament_seeding(
    tournament_id: str,
    seeding_type: str,
    seed_assignments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Updates seeding configuration for a tournament (AUTO_MMR or MANUAL).
    If MANUAL, sets seeds according to seed_assignments.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
        tournament = cursor.fetchone()
        if not tournament:
            raise ValueError("Tournament not found.")

        cursor.execute("UPDATE tournaments SET seeding_type = ? WHERE id = ?", (seeding_type, tournament_id))

        if seeding_type == "MANUAL" and seed_assignments:
            for item in seed_assignments:
                cursor.execute("""
                UPDATE tournament_participants
                SET seed = ?
                WHERE tournament_id = ? AND user_id = ?
                """, (item["seed"], tournament_id, item["user_id"]))

        conn.commit()
        return {
            "status": "SUCCESS",
            "tournament_id": tournament_id,
            "seeding_type": seeding_type
        }
    finally:
        conn.close()
