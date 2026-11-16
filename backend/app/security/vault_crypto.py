import os
import base64
import hashlib
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from backend.app.config import settings

class VaultCrypto:
    """
    AES-256-GCM Hardware-Grade Authenticated Encryption for Stored Credentials (PCI-DSS 3.4).
    Ensures that PayPal API secrets, tokens, and merchant signing keys are never stored
    or cached in plaintext at rest.
    """

    PBKDF2_ITERATIONS = 100_000

    def __init__(self, master_key_material: Optional[str] = None):
        self._master = master_key_material or getattr(settings, "EST_HMAC_SECRET_KEY", "payguard_zero_trust_master_secret_2026")

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a 256-bit AES key using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
        )
        return kdf.derive(self._master.encode("utf-8"))

    def encrypt(self, plaintext: str, associated_data: Optional[str] = None) -> str:
        """
        Encrypts plaintext using AES-256-GCM with a random 16-byte salt and 12-byte nonce.
        Returns a portable Base64-encoded payload: salt + nonce + ciphertext_with_tag.
        """
        if not plaintext:
            return ""

        salt = os.urandom(16)
        nonce = os.urandom(12)
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)

        aad_bytes = associated_data.encode("utf-8") if associated_data else None
        ciphertext_and_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad_bytes)

        # Structure: 16 bytes salt | 12 bytes nonce | remainder ciphertext+tag
        payload = salt + nonce + ciphertext_and_tag
        return base64.b64encode(payload).decode("utf-8")

    def decrypt(self, encrypted_b64: str, associated_data: Optional[str] = None) -> str:
        """
        Decrypts an AES-256-GCM Base64 payload, validating cryptographic authenticity.
        Raises ValueError if tampered or corrupt.
        """
        if not encrypted_b64:
            return ""

        raw = base64.b64decode(encrypted_b64.encode("utf-8"))
        if len(raw) < 28:
            raise ValueError("Corrupt encrypted payload: insufficient byte length.")

        salt = raw[:16]
        nonce = raw[16:28]
        ciphertext_and_tag = raw[28:]

        key = self._derive_key(salt)
        aesgcm = AESGCM(key)

        aad_bytes = associated_data.encode("utf-8") if associated_data else None
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_and_tag, aad_bytes)
        return plaintext_bytes.decode("utf-8")

    @classmethod
    def mask_secret(cls, secret: str, show_last: int = 4) -> str:
        """Returns a PCI-compliant masked string (e.g., '••••••••••••1a2b')."""
        if not secret:
            return "••••"
        if len(secret) <= show_last:
            return "•" * len(secret)
        return "•" * (len(secret) - show_last) + secret[-show_last:]

vault_crypto = VaultCrypto()
