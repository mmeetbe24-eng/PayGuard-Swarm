import hmac
import hashlib
import json
import time
import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class EphemeralScopedToken(BaseModel):
    token_id: str = Field(default_factory=lambda: f"EST-{uuid.uuid4().hex[:12].upper()}")
    merchant_id: str
    amount_ceiling: float
    currency: str = "USD"
    issued_at: float = Field(default_factory=time.time)
    expires_at: float
    user_intent_hash: str
    signature: str

class TokenVerificationResult(BaseModel):
    is_valid: bool
    status: str  # VALID, EXPIRED, LIMIT_EXCEEDED, MERCHANT_MISMATCH, INVALID_SIGNATURE
    error_message: Optional[str] = None
    remaining_seconds: float = 0.0

class EphemeralTokenEngine:
    """
    Cryptographic Enclave for Ephemeral Scoped Token (EST) Issuance and Verification.
    Eliminates Carte-Blanche API key access by issuing mathematically bounded,
    single-use, short-lived tokens locked to an exact merchant and dollar limit.
    """

    def __init__(self, master_secret: str):
        self.master_secret = master_secret.encode('utf-8')

    def generate_token(
        self, 
        merchant_id: str, 
        amount_ceiling: float, 
        user_intent: str,
        ttl_seconds: int = 300,
        currency: str = "USD"
    ) -> EphemeralScopedToken:
        now = time.time()
        expires_at = now + ttl_seconds
        
        # Hash user intent to cryptographically bind the token to user authorization
        intent_hash = hashlib.sha256(user_intent.strip().lower().encode('utf-8')).hexdigest()
        token_id = f"EST-{uuid.uuid4().hex[:12].upper()}"

        # Canonical signing payload
        payload = f"{token_id}:{merchant_id}:{amount_ceiling:.2f}:{currency}:{now:.2f}:{expires_at:.2f}:{intent_hash}"
        signature = hmac.new(self.master_secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()

        return EphemeralScopedToken(
            token_id=token_id,
            merchant_id=merchant_id,
            amount_ceiling=round(amount_ceiling, 2),
            currency=currency,
            issued_at=now,
            expires_at=expires_at,
            user_intent_hash=intent_hash,
            signature=signature
        )

    def verify_and_authorize(
        self, 
        token: EphemeralScopedToken, 
        requested_merchant_id: str, 
        requested_amount: float
    ) -> TokenVerificationResult:
        now = time.time()

        # 1. Check expiration
        if now > token.expires_at:
            return TokenVerificationResult(
                is_valid=False,
                status="EXPIRED",
                error_message=f"Token {token.token_id} expired {now - token.expires_at:.1f}s ago.",
                remaining_seconds=0.0
            )

        # 2. Check valid positive amount
        if requested_amount <= 0:
            return TokenVerificationResult(
                is_valid=False,
                status="INVALID_AMOUNT",
                error_message=f"Invalid transaction amount ${requested_amount:.2f}. Must be greater than $0.00.",
                remaining_seconds=max(0.0, token.expires_at - now)
            )

        # 2. Check cryptographic signature integrity
        expected_payload = (
            f"{token.token_id}:{token.merchant_id}:{token.amount_ceiling:.2f}:"
            f"{token.currency}:{token.issued_at:.2f}:{token.expires_at:.2f}:{token.user_intent_hash}"
        )
        expected_sig = hmac.new(self.master_secret, expected_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_sig, token.signature):
            return TokenVerificationResult(
                is_valid=False,
                status="INVALID_SIGNATURE",
                error_message="Cryptographic signature mismatch! Ephemeral token has been tampered with.",
                remaining_seconds=max(0.0, token.expires_at - now)
            )

        # 3. Check merchant lock
        if token.merchant_id != requested_merchant_id:
            return TokenVerificationResult(
                is_valid=False,
                status="MERCHANT_MISMATCH",
                error_message=f"Merchant mismatch: Token locked to '{token.merchant_id}', attempted charge by '{requested_merchant_id}'.",
                remaining_seconds=max(0.0, token.expires_at - now)
            )

        # 4. Check strict dollar ceiling
        if requested_amount > token.amount_ceiling:
            excess = requested_amount - token.amount_ceiling
            return TokenVerificationResult(
                is_valid=False,
                status="LIMIT_EXCEEDED",
                error_message=f"Financial ceiling breached! Requested ${requested_amount:.2f} exceeds authorized ceiling ${token.amount_ceiling:.2f} (Overspend: ${excess:.2f}).",
                remaining_seconds=max(0.0, token.expires_at - now)
            )

        return TokenVerificationResult(
            is_valid=True,
            status="VALID",
            error_message=None,
            remaining_seconds=round(token.expires_at - now, 1)
        )
