import sqlite3
import hashlib
import json
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.config import settings

class AuditEntry(BaseModel):
    id: Optional[int] = None
    timestamp: float
    iso_time: str
    agent: str
    event_type: str
    payload: Dict[str, Any]
    prev_hash: str
    block_hash: str

class ImmutableAuditLedger:
    """
    Cryptographically chained SQLite audit ledger.
    Every agent action and payment state transition creates a tamper-evident,
    SHA-256 chained receipt.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._write_lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    iso_time TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    block_hash TEXT NOT NULL UNIQUE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS used_tokens (
                    token_id TEXT PRIMARY KEY,
                    consumed_at REAL NOT NULL,
                    merchant_id TEXT NOT NULL,
                    amount REAL NOT NULL
                )
            """)
            # Immutability triggers to prevent tampering, updating, or deleting existing ledger rows
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS abort_update_audit_blocks
                BEFORE UPDATE ON audit_blocks
                BEGIN
                    SELECT RAISE(ABORT, 'Audit ledger is immutable: UPDATE not permitted');
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS abort_delete_audit_blocks
                BEFORE DELETE ON audit_blocks
                BEGIN
                    SELECT RAISE(ABORT, 'Audit ledger is immutable: DELETE not permitted');
                END;
            """)
            conn.commit()

    def consume_token(self, token_id: str, merchant_id: str, amount: float) -> bool:
        """
        Atomically records token consumption to prevent replay attacks.
        Returns False if token was already used.
        """
        with self._write_lock:
            try:
                with self._get_connection() as conn:
                    conn.execute(
                        "INSERT INTO used_tokens (token_id, consumed_at, merchant_id, amount) VALUES (?, ?, ?, ?)",
                        (token_id, time.time(), merchant_id, amount)
                    )
                    conn.commit()
                    return True
            except sqlite3.IntegrityError:
                return False

    def is_token_consumed(self, token_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token_id FROM used_tokens WHERE token_id = ?", (token_id,))
            return cursor.fetchone() is not None

    def _get_latest_hash(self, conn: sqlite3.Connection) -> str:
        cursor = conn.cursor()
        cursor.execute("SELECT block_hash FROM audit_blocks ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row["block_hash"]
        # Genesis block anchor hash
        return "0000000000000000000000000000000000000000000000000000000000000000"

    def record_event(self, agent: str, event_type: str, payload: Dict[str, Any]) -> AuditEntry:
        now = time.time()
        iso_str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))
        payload_json = json.dumps(payload, sort_keys=True)

        with self._write_lock:
            with self._get_connection() as conn:
                prev_hash = self._get_latest_hash(conn)
                
                # Compute block hash
                block_data = f"{now:.4f}|{agent}|{event_type}|{payload_json}|{prev_hash}"
                block_hash = hashlib.sha256(block_data.encode('utf-8')).hexdigest()

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_blocks (timestamp, iso_time, agent, event_type, payload, prev_hash, block_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (now, iso_str, agent, event_type, payload_json, prev_hash, block_hash))
                conn.commit()
                entry_id = cursor.lastrowid

            return AuditEntry(
                id=entry_id,
                timestamp=now,
                iso_time=iso_str,
                agent=agent,
                event_type=event_type,
                payload=payload,
                prev_hash=prev_hash,
                block_hash=block_hash
            )

    def get_recent_entries(self, limit: int = 50) -> List[AuditEntry]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_blocks ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            entries = []
            for r in rows:
                entries.append(AuditEntry(
                    id=r["id"],
                    timestamp=r["timestamp"],
                    iso_time=r["iso_time"],
                    agent=r["agent"],
                    event_type=r["event_type"],
                    payload=json.loads(r["payload"]),
                    prev_hash=r["prev_hash"],
                    block_hash=r["block_hash"]
                ))
            return entries

    def verify_chain_integrity(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_blocks ORDER BY id ASC")
            rows = cursor.fetchall()

            if not rows:
                return {"valid": True, "count": 0, "message": "Ledger is empty (Genesis state)"}

            prev_expected_hash = "0000000000000000000000000000000000000000000000000000000000000000"
            for r in rows:
                if r["prev_hash"] != prev_expected_hash:
                    return {
                        "valid": False,
                        "tampered_block_id": r["id"],
                        "message": f"Hash link broken at block {r['id']}. Expected {prev_expected_hash}, found {r['prev_hash']}"
                    }
                
                # Recompute hash
                payload_json = r["payload"]
                block_data = f"{r['timestamp']:.4f}|{r['agent']}|{r['event_type']}|{payload_json}|{r['prev_hash']}"
                recomputed_hash = hashlib.sha256(block_data.encode('utf-8')).hexdigest()

                if recomputed_hash != r["block_hash"]:
                    return {
                        "valid": False,
                        "tampered_block_id": r["id"],
                        "message": f"Block data altered at block {r['id']}. Hash mismatch."
                    }

                prev_expected_hash = r["block_hash"]

            return {
                "valid": True, 
                "count": len(rows), 
                "message": f"All {len(rows)} cryptographically chained blocks are intact and untampered."
            }

    def count_events(self, pattern: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_blocks WHERE event_type LIKE ?", (f"%{pattern}%",))
            return cursor.fetchone()[0]

    def reset_ledger(self):
        """
        Resets the audit ledger to Genesis state.
        Useful for recording clean demonstrations.
        """
        with self._get_connection() as conn:
            conn.execute("DROP TRIGGER IF EXISTS abort_update_audit_blocks")
            conn.execute("DROP TRIGGER IF EXISTS abort_delete_audit_blocks")
            conn.execute("DELETE FROM audit_blocks")
            conn.execute("DELETE FROM used_tokens")
            conn.execute("DELETE FROM sqlite_sequence WHERE name='audit_blocks'")
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS abort_update_audit_blocks
                BEFORE UPDATE ON audit_blocks
                BEGIN
                    SELECT RAISE(ABORT, 'Audit ledger is immutable: UPDATE not permitted');
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS abort_delete_audit_blocks
                BEFORE DELETE ON audit_blocks
                BEGIN
                    SELECT RAISE(ABORT, 'Audit ledger is immutable: DELETE not permitted');
                END;
            """)
            conn.commit()

audit_ledger = ImmutableAuditLedger()
