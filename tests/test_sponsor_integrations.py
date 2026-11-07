import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.integrations.zapier import zapier_dispatcher
from backend.app.integrations.channel3 import channel3_client
from backend.app.security.audit_ledger import audit_ledger

def test_zapier_webhook_dispatch():
    """Verify that Zapier webhook dispatcher formats and logs events correctly."""
    res = zapier_dispatcher.dispatch_event(
        event_type="TEST_SECURTY_ALERT",
        payload={"alert": "Unauthorized price surge simulated", "amount": 274.99},
        severity="CRITICAL"
    )
    assert res["delivered"] is True
    assert res["event_type"] == "TEST_SECURTY_ALERT"
    assert res["payload"]["severity"] == "CRITICAL"
    assert "data" in res["payload"]

def test_channel3_agentic_catalog_search():
    """Verify that Channel3 client returns normalized multi-store product offers."""
    offers = channel3_client.search_agentic_catalog(
        query="Sony WH-1000XM5 headphones",
        budget_ceiling=250.00
    )
    assert len(offers) >= 3
    # Verify Store A
    store_a = next(o for o in offers if o.merchant_id == "MERCHANT_STORE_A")
    assert store_a.price == 224.99
    assert store_a.channel3_verified is True
    assert store_a.availability == "IN_STOCK"

    # Verify Store B
    store_b = next(o for o in offers if o.merchant_id == "MERCHANT_STORE_B")
    assert store_b.price == 154.98
    assert store_b.channel3_verified is False

def test_apimatic_spec_and_meta_exist():
    """Verify that APIMatic OpenAPI specification and configuration files exist."""
    spec_file = BASE_DIR / "docs" / "apimatic" / "openapi.yaml"
    meta_file = BASE_DIR / "docs" / "apimatic" / "APIMatic-meta.json"
    assert spec_file.exists()
    assert meta_file.exists()
    assert spec_file.stat().st_size > 500
    assert meta_file.stat().st_size > 100
