import time
import threading
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """
    Sliding-Window Token-Bucket Rate Limiter.
    Prevents Denial-of-Wallet (DoW) attacks, automated bot spam, and API quota exhaustion
    against PayPal Sandbox and Gemini Multimodal APIs.
    """

    def __init__(self, capacity: int = 15, refill_rate_per_sec: float = 0.5):
        """
        capacity: Maximum burst capacity of tokens.
        refill_rate_per_sec: Tokens added back per second (default: 1 token every 2 seconds).
        """
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self._lock = threading.Lock()
        self._buckets: Dict[str, Dict[str, float]] = {}

    def is_allowed(self, client_id: str = "default_user", cost: int = 1) -> Tuple[bool, int, float]:
        """
        Checks if the request is permitted.
        Returns: (is_allowed: bool, remaining_tokens: int, retry_after_seconds: float)
        """
        now = time.time()
        with self._lock:
            if client_id not in self._buckets:
                self._buckets[client_id] = {
                    "tokens": float(self.capacity),
                    "last_updated": now
                }
            
            bucket = self._buckets[client_id]
            elapsed = now - bucket["last_updated"]
            bucket["tokens"] = min(float(self.capacity), bucket["tokens"] + elapsed * self.refill_rate)
            bucket["last_updated"] = now

            if bucket["tokens"] >= cost:
                bucket["tokens"] -= cost
                return True, int(bucket["tokens"]), 0.0
            else:
                needed = cost - bucket["tokens"]
                retry_after = round(needed / self.refill_rate, 1)
                return False, int(bucket["tokens"]), retry_after

    def reset(self, client_id: str = "default_user"):
        with self._lock:
            if client_id in self._buckets:
                del self._buckets[client_id]

rate_limiter = TokenBucketRateLimiter(capacity=20, refill_rate_per_sec=1.0)
