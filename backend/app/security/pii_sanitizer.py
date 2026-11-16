import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel, Field

class PIIRedactionResult(BaseModel):
    original_length: int
    sanitized_length: int
    redaction_count: int
    redactions: List[Dict[str, str]] = Field(default_factory=list)
    sanitized_text: str
    has_pii: bool

class PIISanitizer:
    """
    Enterprise Data Privacy & PII Redaction Gate (PCI-DSS & GDPR Compliance).
    Inspects and scrubs sensitive customer financial and personal data
    (Credit Cards, CVVs, Emails, Phone Numbers, Aadhaar/SSN, Physical Addresses)
    before any directive is dispatched to external LLMs (Google Gemini) or written to public logs.
    """

    # 1. Payment Card Patterns (Visa, Mastercard, Amex, Discover, RuPay)
    CARD_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

    # 2. CVV / CVC Security Codes
    CVV_PATTERN = re.compile(r'(?i)\b(?:cvv|cvc|cvv2|security\s*code)[\s:=#]*([0-9]{3,4})\b')

    # 3. Email Addresses
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

    # 4. Phone Numbers (Indian +91, US/Intl 10-12 digits with optional dashes/spaces)
    PHONE_PATTERN = re.compile(r'(?:\+?91[\s-]?)?[6789]\d{9}\b|\b(?:\+?1[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b')

    # 5. Government IDs: Indian Aadhaar (strictly 12 digits) & Indian PAN (ABCDE1234F) & US SSN
    AADHAAR_PATTERN = re.compile(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b(?!\s?\d{1,4})')
    PAN_CARD_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
    SSN_PATTERN = re.compile(r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b')

    # 6. Physical Address keywords
    ADDRESS_PATTERN = re.compile(
        r'(?i)\b(?:deliver\s+to|shipping\s+address|street|apt|flat|building|sector|pincode|zip\s*code|postal\s*code)[\s:=]+([^\n,;]{4,60})',
        re.IGNORECASE
    )

    @classmethod
    def _is_luhn_valid(cls, number_str: str) -> bool:
        """Standard Luhn Algorithm (Mod 10) for payment card checksum verification."""
        digits = [int(c) for c in number_str if c.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        total = 0
        reverse_digits = digits[::-1]
        for idx, digit in enumerate(reverse_digits):
            if idx % 2 == 1:
                doubled = digit * 2
                total += doubled - 9 if doubled > 9 else doubled
            else:
                total += digit
        return total % 10 == 0

    @classmethod
    def sanitize_text(cls, text: str) -> PIIRedactionResult:
        """
        Inspects text and replaces all sensitive PII with cryptographically tagged,
        zero-knowledge tokens.
        """
        if not text:
            return PIIRedactionResult(
                original_length=0,
                sanitized_length=0,
                redaction_count=0,
                sanitized_text="",
                has_pii=False
            )

        sanitized = str(text)
        redactions: List[Dict[str, str]] = []

        # 1. Redact CVV codes first
        def replace_cvv(m):
            redactions.append({"type": "CVV", "masked": "[REDACTED_CVV]"})
            return re.sub(r'[0-9]{3,4}', '[REDACTED_CVV]', m.group(0))
        sanitized = cls.CVV_PATTERN.sub(replace_cvv, sanitized)

        # 2. Redact Payment Cards (with Luhn validation to avoid false positives on budgets/barcodes)
        def replace_card(m):
            raw = m.group(0)
            cleaned_digits = re.sub(r'\D', '', raw)
            if cls._is_luhn_valid(cleaned_digits):
                last4 = cleaned_digits[-4:]
                masked = f"[REDACTED_CARD_••••_{last4}]"
                redactions.append({"type": "CREDIT_CARD", "masked": masked})
                return masked
            return raw
        sanitized = cls.CARD_PATTERN.sub(replace_card, sanitized)

        # 3. Redact Email Addresses
        def replace_email(m):
            raw_email = m.group(0)
            token = hashlib.sha256(raw_email.lower().encode()).hexdigest()[:6]
            masked = f"[USER_EMAIL_{token}]"
            redactions.append({"type": "EMAIL", "masked": masked})
            return masked
        sanitized = cls.EMAIL_PATTERN.sub(replace_email, sanitized)

        # 4. Redact Phone Numbers
        def replace_phone(m):
            raw_phone = m.group(0)
            token = hashlib.sha256(raw_phone.encode()).hexdigest()[:6]
            masked = f"[PHONE_REF_{token}]"
            redactions.append({"type": "PHONE", "masked": masked})
            return masked
        sanitized = cls.PHONE_PATTERN.sub(replace_phone, sanitized)

        # 5. Redact Government IDs
        def replace_aadhaar(m):
            redactions.append({"type": "GOV_ID", "masked": "[REDACTED_AADHAAR]"})
            return "[REDACTED_AADHAAR]"
        sanitized = cls.AADHAAR_PATTERN.sub(replace_aadhaar, sanitized)

        def replace_pan(m):
            redactions.append({"type": "GOV_ID", "masked": "[REDACTED_TAX_PAN]"})
            return "[REDACTED_TAX_PAN]"
        sanitized = cls.PAN_CARD_PATTERN.sub(replace_pan, sanitized)

        def replace_ssn(m):
            redactions.append({"type": "GOV_ID", "masked": "[REDACTED_SSN]"})
            return "[REDACTED_SSN]"
        sanitized = cls.SSN_PATTERN.sub(replace_ssn, sanitized)

        # 6. Redact Physical Addresses
        def replace_address(m):
            raw_addr = m.group(1).strip()
            token = hashlib.sha256(raw_addr.lower().encode()).hexdigest()[:6]
            masked = f"[SHIPPING_ZONE_TOKEN_{token}]"
            redactions.append({"type": "ADDRESS", "masked": masked})
            return m.group(0).replace(raw_addr, masked)
        sanitized = cls.ADDRESS_PATTERN.sub(replace_address, sanitized)

        return PIIRedactionResult(
            original_length=len(text),
            sanitized_length=len(sanitized),
            redaction_count=len(redactions),
            redactions=redactions,
            sanitized_text=sanitized,
            has_pii=len(redactions) > 0
        )

    @classmethod
    def sanitize_payload(cls, data: Any) -> Any:
        """
        Recursively scrubs dictionaries, lists, and strings for safe, compliant
        storage in the audit ledger or logging pipelines.
        """
        if isinstance(data, dict):
            cleaned = {}
            for k, v in data.items():
                # Obfuscate common sensitive keys completely
                lower_k = str(k).lower()
                if any(sec in lower_k for sec in ["secret", "password", "token", "cvv", "card_number", "ssn", "auth"]):
                    cleaned[k] = "[ENCRYPTED_VAULT_REFERENCE]"
                else:
                    cleaned[k] = cls.sanitize_payload(v)
            return cleaned
        elif isinstance(data, list):
            return [cls.sanitize_payload(item) for item in data]
        elif isinstance(data, str):
            res = cls.sanitize_text(data)
            return res.sanitized_text
        return data

pii_sanitizer = PIISanitizer()
