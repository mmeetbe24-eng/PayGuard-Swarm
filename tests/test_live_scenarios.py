import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.agents.swarm_orchestrator import swarm_orchestrator
from backend.app.security.audit_ledger import audit_ledger

def test_legitimate_store_a():
    print("\n" + "="*70)
    print("SCENARIO 1: Legitimate Store A (Nike Air under $90)")
    print("="*70)
    
    result = swarm_orchestrator.execute_flow(
        user_prompt="Buy Nike Air under $90 using PayPal",
        store_choice="STORE_A",
        max_budget_ceiling=90.00,
        is_shielded_by_payguard=True
    )
    
    print(f"Status: {result.final_status}")
    print(f"Outcome: {result.financial_outcome}")
    print(f"Execution Latency: {result.total_execution_ms} ms")
    if result.agent3_vault_receipt:
        print(f"PayPal Order ID: {result.agent3_vault_receipt.paypal_order_id}")
        print(f"PayPal Capture ID: {result.agent3_vault_receipt.paypal_capture_id}")
        print(f"EST Token ID: {result.agent3_vault_receipt.token.token_id}")
    print(f"Audit Block Hash: {result.audit_hash}")
    assert result.success is True
    print("[TEST 1 PASSED]: Clean purchase settled securely within EST ceiling!")

def test_unshielded_bot_exploit_store_b():
    print("\n" + "="*70)
    print("SCENARIO 2: UNSHIELDED Standard Bot on Store B (Adversarial Prompt Trap)")
    print("="*70)
    
    result = swarm_orchestrator.execute_flow(
        user_prompt="Buy Nike Air under $90 using PayPal",
        store_choice="STORE_B",
        max_budget_ceiling=90.00,
        is_shielded_by_payguard=False  # Simulates standard bot without PayGuard
    )
    
    print(f"Status: {result.final_status}")
    print(f"Outcome: {result.financial_outcome}")
    print(f"Drain Amount: ${result.agent1_shopper_draft.total_price:.2f}")
    assert result.final_status == "WALLET_DRAINED_EXPLOITED"
    print("[TEST 2 PASSED]: Correctly demonstrated how an unshielded bot is exploited!")

def test_payguard_autonomous_failover():
    print("\n" + "="*70)
    print("SCENARIO 3: PAYGUARD SHIELDED Swarm - Autonomous Multi-Store Failover Recovery")
    print("="*70)
    
    result = swarm_orchestrator.execute_flow(
        user_prompt="Buy Nike Air under $90 using PayPal",
        store_choice="STORE_B",
        max_budget_ceiling=90.00,
        is_shielded_by_payguard=True  # PayGuard Zero-Trust Active
    )
    
    print(f"Status: {result.final_status}")
    print(f"Outcome: {result.financial_outcome}")
    assert result.agent2_multi_audit is not None
    print(f"Stores Scanned: {result.agent2_multi_audit.stores_scanned}")
    print(f"Malicious Quarantined: {result.agent2_multi_audit.malicious_traps_neutralized}")
    print(f"Autonomous Failover Occurred: {result.agent2_multi_audit.failover_occurred}")
    assert result.agent2_multi_audit.failover_occurred is True
    assert result.success is True
    print("[TEST 3 PASSED]: PayGuard quarantined hostile Store B and autonomously failed over to certified Store A!")

def test_midflight_tamper_void():
    print("\n" + "="*70)
    print("SCENARIO 4: Mid-Flight Price Tampering & PayPal Emergency VOID")
    print("="*70)
    
    result = swarm_orchestrator.execute_flow(
        user_prompt="Buy Nike Air under $90 using PayPal",
        store_choice="STORE_A",
        max_budget_ceiling=90.00,
        is_shielded_by_payguard=True,
        simulate_midflight_tamper=True
    )
    
    print(f"Status: {result.final_status}")
    print(f"Outcome: {result.financial_outcome}")
    assert result.final_status == "CIRCUIT_BREAKER_TRIGGERED"
    assert result.agent5_circuit_breaker.circuit_breaker_tripped is True
    print("[TEST 4 PASSED]: Circuit Breaker intercepted post-auth hike and triggered PayPal emergency VOID!")

def test_audit_ledger_integrity():
    print("\n" + "="*70)
    print("SCENARIO 5: Cryptographic Audit Ledger Integrity Verification")
    print("="*70)
    
    verification = audit_ledger.verify_chain_integrity()
    print(f"Integrity Valid: {verification['valid']}")
    print(f"Total Chained Blocks: {verification['count']}")
    print(f"Verification Message: {verification['message']}")
    assert verification["valid"] is True
    print("[TEST 5 PASSED]: Tamper-evident hash-chained audit ledger is 100% untampered!")

if __name__ == "__main__":
    test_legitimate_store_a()
    test_unshielded_bot_exploit_store_b()
    test_payguard_autonomous_failover()
    test_midflight_tamper_void()
    test_audit_ledger_integrity()
    print("\n" + "#"*70)
    print("ALL 5 CRITICAL ADVANCED SECURITY & FAILOVER TESTS PASSED FLAWLESSLY!")
    print("#"*70)
