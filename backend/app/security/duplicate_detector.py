import time
import re
import hashlib
import sqlite3
import threading
from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field
from backend.app.config import settings

class DuplicateCheckResult(BaseModel):
    is_duplicate: bool
    time_ago_seconds: Optional[float] = None
    previous_order_id: Optional[str] = None
    fingerprint: str
    normalized_product: str
    warning_message: Optional[str] = None
    idempotency_key: str

class DuplicateOrderDetector:
    """
    Real-Time Sliding-Window Duplicate Order Interceptor & Idempotency Engine.
    Prevents accidental double-clicks, fat-finger double orders, and automated replay charges
    on PayPal by enforcing a configurable sliding time window (default 10 minutes).
    """

    DEFAULT_WINDOW_SECONDS: int = 600  # 10 Minutes sliding window

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._lock = threading.Lock()
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS order_idempotency_log (
                        fingerprint TEXT PRIMARY KEY,
                        order_id TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        normalized_product TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        status TEXT NOT NULL
                    )
                """)
                conn.commit()
        except Exception:
            pass

    @classmethod
    def normalize_product_intent(cls, prompt: str) -> str:
        """
        Extracts and normalizes core product tokens from autonomous directives.
        Filters out generic filler words (find, buy, under, using, paypal, please).
        """
        cleaned = prompt.lower()
        # Remove currency symbols and price patterns
        cleaned = re.sub(r'[₹\$€£][\d,.]+', ' ', cleaned)
        cleaned = re.sub(r'\bunder\s+[\d,.]+', ' ', cleaned)
        cleaned = re.sub(r'\bfor\s+[\d,.]+', ' ', cleaned)
        
        # Stop words
        stop_words = {"find", "and", "buy", "purchase", "order", "get", "using", "via", "paypal", "with", "under", "deliver", "to", "please", "item", "product"}
        tokens = [w for w in re.findall(r'[a-z0-9]+', cleaned) if w not in stop_words and len(w) > 1]
        return " ".join(tokens)

    def generate_fingerprint(self, prompt: str, amount: Optional[float] = None, currency: str = "INR") -> str:
        """Generates deterministic semantic fingerprint based on normalized product and currency."""
        norm_item = self.normalize_product_intent(prompt)
        base = f"{norm_item}|{currency.upper()}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()[:24]

    def generate_idempotency_key(self, prompt: str, amount: Optional[float] = None, currency: str = "INR") -> str:
        """
        Generates a standard PayPal-Request-Id idempotency key tied to a 10-minute time bucket.
        """
        norm_item = self.normalize_product_intent(prompt)
        time_bucket = int(time.time() // self.DEFAULT_WINDOW_SECONDS)
        base = f"IDEM_{norm_item}_{currency}_{time_bucket}"
        return f"PG-{hashlib.sha256(base.encode()).hexdigest()[:18].upper()}"

    def check_duplicate(
        self,
        prompt: str,
        amount: float,
        currency: str = "INR",
        window_seconds: Optional[int] = None
    ) -> DuplicateCheckResult:
        """
        Checks whether an identical or semantically equivalent order was placed
        within the sliding time window.
        """
        window = window_seconds or self.DEFAULT_WINDOW_SECONDS
        now = time.time()
        norm_product = self.normalize_product_intent(prompt)
        fingerprint = self.generate_fingerprint(prompt, amount, currency)
        idempotency_key = self.generate_idempotency_key(prompt, amount, currency)

        # 1. Fast in-memory check
        with self._lock:
            cached = self._memory_cache.get(fingerprint)
            if cached:
                elapsed = now - cached["created_at"]
                if elapsed < window and cached["status"] != "CANCELLED":
                    mins = int(elapsed // 60)
                    secs = int(elapsed % 60)
                    time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                    return DuplicateCheckResult(
                        is_duplicate=True,
                        time_ago_seconds=round(elapsed, 1),
                        previous_order_id=cached["order_id"],
                        fingerprint=fingerprint,
                        normalized_product=norm_product,
                        warning_message=(
                            f"Identical order for '{norm_product}' (₹{amount:.0f}) was placed {time_str} ago "
                            f"(Order ID: {cached['order_id']}). Halted to prevent accidental duplicate charge."
                        ),
                        idempotency_key=idempotency_key
                    )

        # 2. SQLite persistent check (survives app reboots)
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT order_id, created_at, status FROM order_idempotency_log WHERE fingerprint = ? ORDER BY created_at DESC LIMIT 1",
                    (fingerprint,)
                )
                row = cursor.fetchone()
                if row:
                    elapsed = now - row["created_at"]
                    if elapsed < window and row["status"] != "CANCELLED":
                        # Populate back into memory cache
                        with self._lock:
                            self._memory_cache[fingerprint] = {
                                "order_id": row["order_id"],
                                "created_at": row["created_at"],
                                "status": row["status"]
                            }
                        mins = int(elapsed // 60)
                        secs = int(elapsed % 60)
                        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                        return DuplicateCheckResult(
                            is_duplicate=True,
                            time_ago_seconds=round(elapsed, 1),
                            previous_order_id=row["order_id"],
                            fingerprint=fingerprint,
                            normalized_product=norm_product,
                            warning_message=(
                                f"Identical order for '{norm_product}' (₹{amount:.0f}) was placed {time_str} ago "
                                f"(Order ID: {row['order_id']}). Halted to prevent accidental duplicate charge."
                            ),
                            idempotency_key=idempotency_key
                        )
        except Exception:
            pass

        return DuplicateCheckResult(
            is_duplicate=False,
            time_ago_seconds=None,
            previous_order_id=None,
            fingerprint=fingerprint,
            normalized_product=norm_product,
            warning_message=None,
            idempotency_key=idempotency_key
        )

    def record_order(
        self,
        order_id: str,
        prompt: str,
        amount: float,
        currency: str = "INR",
        status: str = "COMPLETED"
    ):
        """Records an authorized or completed order into the idempotency registry."""
        now = time.time()
        norm_product = self.normalize_product_intent(prompt)
        fingerprint = self.generate_fingerprint(prompt, amount, currency)

        with self._lock:
            self._memory_cache[fingerprint] = {
                "order_id": order_id,
                "created_at": now,
                "status": status
            }

        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO order_idempotency_log 
                    (fingerprint, order_id, created_at, normalized_product, amount, currency, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (fingerprint, order_id, now, norm_product, amount, currency, status))
                conn.commit()
        except Exception:
            pass

    def clear_history(self):
        """Clears memory and database history (primarily for test isolation)."""
        with self._lock:
            self._memory_cache.clear()
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM order_idempotency_log")
                conn.commit()
        except Exception:
            pass

duplicate_detector = DuplicateOrderDetector()
