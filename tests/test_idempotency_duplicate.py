import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest
import time
from backend.app.security.duplicate_detector import duplicate_detector, DuplicateOrderDetector
from backend.app.agents.swarm_orchestrator import swarm_orchestrator
from backend.app.paypal.client import paypal_client

@pytest.fixture(autouse=True)
def clean_idempotency():
    duplicate_detector.clear_history()
    yield
    duplicate_detector.clear_history()

def test_normalize_product_intent():
    p1 = "Find and buy Orient Electric Spectra Ceiling Fan under ₹3800 using PayPal"
    norm = DuplicateOrderDetector.normalize_product_intent(p1)
    assert "orient" in norm
    assert "electric" in norm
    assert "spectra" in norm
    assert "ceiling" in norm
    assert "fan" in norm
    assert "find" not in norm
    assert "paypal" not in norm
    assert "3800" not in norm

def test_duplicate_order_interception_flow():
    prompt = "Find and buy Lay's Classic Potato Chips under ₹50 using PayPal"
    budget = 50.0

    # 1. First execution should succeed normally
    res1 = swarm_orchestrator.execute_flow(
        user_prompt=prompt,
        max_budget_ceiling=budget,
        is_shielded_by_payguard=True
    )
    assert res1.success is True
    assert res1.is_duplicate_intercepted is False

    # 2. Immediate second identical execution should be INTERCEPTED
    res2 = swarm_orchestrator.execute_flow(
        user_prompt=prompt,
        max_budget_ceiling=budget,
        is_shielded_by_payguard=True
    )
    assert res2.is_duplicate_intercepted is True
    assert res2.success is False
    assert "INTERCEPTED_DUPLICATE" in res2.final_status
    assert "Zero Funds Charged" in res2.financial_outcome
    assert res2.idempotency_key is not None
    assert "Identical order" in res2.duplicate_warning

def test_duplicate_order_intentional_override():
    prompt = "Find and buy Orient Electric Spectra Ceiling Fan under ₹3800 using PayPal"
    budget = 3800.0

    # First purchase
    res1 = swarm_orchestrator.execute_flow(
        user_prompt=prompt,
        max_budget_ceiling=budget,
        is_shielded_by_payguard=True
    )
    assert res1.success is True

    # User explicitly overrides duplicate block
    res_override = swarm_orchestrator.execute_flow(
        user_prompt=prompt,
        max_budget_ceiling=budget,
        is_shielded_by_payguard=True,
        override_duplicate_confirmation=True
    )
    assert res_override.is_duplicate_intercepted is False
    assert res_override.success is True

def test_sliding_window_expiration():
    prompt = "Find and buy Test Headphone under ₹2000 using PayPal"
    amount = 2000.0

    duplicate_detector.record_order("ORD_123", prompt, amount)

    # Within 1-second window test
    dup_instant = duplicate_detector.check_duplicate(prompt, amount, window_seconds=1)
    assert dup_instant.is_duplicate is True

    time.sleep(1.2)
    # Outside 1-second window test
    dup_expired = duplicate_detector.check_duplicate(prompt, amount, window_seconds=1)
    assert dup_expired.is_duplicate is False

def test_paypal_request_id_in_order_creation():
    order = paypal_client.create_order(
        amount=50.0,
        currency="INR",
        merchant_name="Store Partner",
        idempotency_key="PG-IDEM-TEST-12345"
    )
    assert order["id"] is not None
    assert order.get("idempotency_key") == "PG-IDEM-TEST-12345"

def test_multimodal_photo_duplicate_matching():
    # User types a concise order first
    p_typed = "Find and buy Lay's Classic Potato Chips under ₹50 using PayPal"
    # User uploads a photo 2 minutes later, which AI vision expands with flavor specs
    p_photo = "Find and buy Lay's Hot Chips Style Asian Fiery Chilli Potato Chips under ₹50 using PayPal"

    # 1. First typed order executes
    res1 = swarm_orchestrator.execute_flow(
        user_prompt=p_typed,
        max_budget_ceiling=50.0,
        is_shielded_by_payguard=True
    )
    assert res1.success is True
    assert res1.is_duplicate_intercepted is False

    # 2. Second execution from photo should be caught by semantic similarity
    res2 = swarm_orchestrator.execute_flow(
        user_prompt=p_photo,
        max_budget_ceiling=50.0,
        is_shielded_by_payguard=True
    )
    assert res2.is_duplicate_intercepted is True
    assert res2.success is False
    assert "Zero Funds Charged" in res2.financial_outcome
    assert "Identical or similar product" in res2.duplicate_warning
