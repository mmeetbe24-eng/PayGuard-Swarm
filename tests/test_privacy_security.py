import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from backend.app.security.pii_sanitizer import pii_sanitizer, PIISanitizer
from backend.app.security.vault_crypto import vault_crypto, VaultCrypto
from backend.app.security.audit_ledger import audit_ledger

def test_pii_sanitizer_credit_card_and_cvv():
    # Test valid Visa card (4111...) with CVV
    prompt = "Buy laptop using card 4111 1111 1111 1111 and CVV 482 under ₹50000"
    report = pii_sanitizer.sanitize_text(prompt)
    assert report.has_pii is True
    assert "4111" not in report.sanitized_text
    assert "482" not in report.sanitized_text
    assert "[REDACTED_CARD_" in report.sanitized_text
    assert "[REDACTED_CVV]" in report.sanitized_text

def test_pii_sanitizer_email_and_phone():
    prompt = "Send receipt to meet.test@gmail.com or call +919876543210"
    report = pii_sanitizer.sanitize_text(prompt)
    assert report.has_pii is True
    assert "meet.test@gmail.com" not in report.sanitized_text
    assert "+919876543210" not in report.sanitized_text
    assert "[USER_EMAIL_" in report.sanitized_text
    assert "[PHONE_REF_" in report.sanitized_text

def test_pii_sanitizer_government_ids():
    prompt = "User KYC verified with PAN ABCDE1234F and Aadhaar 5482 1234 5678"
    report = pii_sanitizer.sanitize_text(prompt)
    assert report.has_pii is True
    assert "ABCDE1234F" not in report.sanitized_text
    assert "[REDACTED_TAX_PAN]" in report.sanitized_text
    assert "[REDACTED_AADHAAR]" in report.sanitized_text

def test_pii_sanitizer_recursive_payload():
    raw_payload = {
        "customer": "meet.sharma@example.com",
        "secret_key": "raw_paypal_client_secret_xyz",
        "order": {
            "cvv": "999",
            "contact": "9876543210",
            "amount": 499.0
        }
    }
    cleaned = pii_sanitizer.sanitize_payload(raw_payload)
    assert "[USER_EMAIL_" in cleaned["customer"]
    assert cleaned["secret_key"] == "[ENCRYPTED_VAULT_REFERENCE]"
    assert cleaned["order"]["cvv"] == "[ENCRYPTED_VAULT_REFERENCE]"
    assert "[PHONE_REF_" in cleaned["order"]["contact"]
    assert cleaned["order"]["amount"] == 499.0

def test_vault_crypto_aes_256_gcm_roundtrip():
    secret = "EAK_TEST_PAYPAL_CLIENT_SECRET_987654321_ALPHA"
    encrypted = vault_crypto.encrypt(secret, associated_data="enclave_v1")
    assert encrypted != secret
    assert len(encrypted) > len(secret)
    
    decrypted = vault_crypto.decrypt(encrypted, associated_data="enclave_v1")
    assert decrypted == secret

def test_vault_crypto_tamper_detection():
    import base64
    secret = "master_super_sensitive_key"
    encrypted_b64 = vault_crypto.encrypt(secret)
    
    # Tamper with the binary ciphertext
    raw_bytes = bytearray(base64.b64decode(encrypted_b64.encode()))
    raw_bytes[-1] ^= 0xFF  # Flip bit in GCM auth tag
    tampered_b64 = base64.b64encode(raw_bytes).decode()

    with pytest.raises(Exception):
        vault_crypto.decrypt(tampered_b64)

def test_vault_crypto_masking():
    masked = VaultCrypto.mask_secret("PAYPAL_SECRET_12345", show_last=4)
    assert masked.endswith("2345")
    assert "PAYPAL" not in masked
    assert "•" in masked

def test_audit_ledger_auto_sanitizes_pii():
    entry = audit_ledger.record_event(
        agent="Security Test",
        event_type="TEST_PII_LOGGING",
        payload={
            "customer_email": "john.doe@test.com",
            "user_card": "4111 1111 1111 1111",
            "safe_metric": 42
        }
    )
    assert "john.doe@test.com" not in str(entry.payload)
    assert "[USER_EMAIL_" in str(entry.payload)
    assert entry.payload["safe_metric"] == 42
    assert entry.block_hash is not None

def test_ssrf_guard_blocks_private_networks_and_loopback():
    from backend.app.security.ssrf_guard import ssrf_guard
    
    # 1. Localhost & Loopbacks
    safe, reason = ssrf_guard.validate_target_url("http://localhost:8501")
    assert safe is False
    assert "SSRF Attack Blocked" in reason

    safe_ip, reason_ip = ssrf_guard.validate_target_url("http://127.0.0.1:8000/api")
    assert safe_ip is False
    assert "private network" in reason_ip

    # 2. Cloud metadata endpoint
    safe_meta, reason_meta = ssrf_guard.validate_target_url("http://169.254.169.254/latest/meta-data/")
    assert safe_meta is False

    # 3. Private RFC 1918 subnets
    safe_priv, _ = ssrf_guard.validate_target_url("http://192.168.1.1/admin")
    assert safe_priv is False

    # 4. Safe public merchant domain
    safe_pub, _ = ssrf_guard.validate_target_url("https://reliancesmart.in/products/lays")
    assert safe_pub is True

def test_token_bucket_rate_limiter():
    from backend.app.security.rate_limiter import TokenBucketRateLimiter
    
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate_per_sec=0.1)
    
    # First 3 tokens allowed
    assert limiter.is_allowed("test_client")[0] is True
    assert limiter.is_allowed("test_client")[0] is True
    assert limiter.is_allowed("test_client")[0] is True
    
    # 4th burst request rejected
    allowed, tokens, retry_after = limiter.is_allowed("test_client")
    assert allowed is False
    assert retry_after > 0
