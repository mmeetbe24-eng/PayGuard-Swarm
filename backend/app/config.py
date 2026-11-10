import os
from pathlib import Path

# Load .env with optional python-dotenv or native fallback
BASE_DIR = Path(__file__).resolve().parent.parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

# Support Streamlit Cloud st.secrets
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, (str, int, float)):
                os.environ.setdefault(str(k), str(v))
except Exception:
    pass

class Settings:
    PROJECT_NAME: str = "PayGuard Swarm"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Zero-Trust Multi-Agent Protocol for Safe Autonomous Payments on PayPal"
    
    # Gemini Configuration
    DEFAULT_GEMINI_MODEL: str = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash")

    @property
    def GEMINI_API_KEY(self) -> str:
        key = os.getenv("GEMINI_API_KEY", "")
        if key:
            return key
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                return str(st.secrets["GEMINI_API_KEY"])
            if hasattr(st, "session_state") and "runtime_gemini_key" in st.session_state:
                return str(st.session_state["runtime_gemini_key"])
        except Exception:
            pass
        return ""
    
    # PayPal Sandbox Configuration
    PAYPAL_MODE: str = os.getenv("PAYPAL_MODE", "sandbox")
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_BASE_URL: str = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")
    
    # Zero-Trust Protocol Settings
    EST_HMAC_SECRET_KEY: str = os.getenv("EST_HMAC_SECRET_KEY", "payguard_zero_trust_master_secret_2026")
    MICRO_PAYMENT_THRESHOLD: float = float(os.getenv("MICRO_PAYMENT_THRESHOLD", "2.00"))
    BATCH_SETTLEMENT_THRESHOLD: float = float(os.getenv("BATCH_SETTLEMENT_THRESHOLD", "15.00"))
    TOKEN_DEFAULT_TTL_SECONDS: int = int(os.getenv("TOKEN_DEFAULT_TTL_SECONDS", "300"))
    
    # Database
    DATABASE_PATH: Path = BASE_DIR / "audit_ledger.db"

    # Sponsor Integrations: Zapier & Channel3
    ZAPIER_WEBHOOK_URL: str = os.getenv("ZAPIER_WEBHOOK_URL", "")
    CHANNEL3_API_KEY: str = os.getenv("CHANNEL3_API_KEY", "")

settings = Settings()
