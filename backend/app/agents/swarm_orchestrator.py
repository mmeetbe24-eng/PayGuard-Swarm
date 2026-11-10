import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.agents.shopper import shopper_agent, DraftOrderIntent
from backend.app.agents.sentry import sentry_agent, SentryInspectionResult, MultiStoreAuditReport
from backend.app.agents.gatekeeper import gatekeeper_vault, EnclaveAuthorizationReceipt
from backend.app.agents.optimizer import api_cost_optimizer, RoutingDirective
from backend.app.agents.circuit_breaker import circuit_breaker, RollbackReceipt
from backend.app.mock_stores.dynamic_market import dynamic_market, MarketStore
from backend.app.security.audit_ledger import audit_ledger
from backend.app.integrations.zapier import zapier_dispatcher

class SwarmExecutionResult(BaseModel):
    success: bool
    scenario_mode: str  # PROTECTED_PAYGUARD, VULNERABLE_UNSHIELDED, MIDFLIGHT_TAMPER_VOID
    target_store: str
    user_prompt: str
    user_budget_ceiling: float
    total_execution_ms: float
    
    # Step-by-step agent telemetry
    agent1_shopper_draft: DraftOrderIntent
    agent2_sentry_result: Optional[SentryInspectionResult] = None
    agent2_multi_audit: Optional[MultiStoreAuditReport] = None
    engine4_routing_result: Optional[RoutingDirective] = None
    agent3_vault_receipt: Optional[EnclaveAuthorizationReceipt] = None
    agent5_circuit_breaker: Optional[RollbackReceipt] = None
    
    final_status: str
    financial_outcome: str
    failover_recovery_note: Optional[str] = None
    audit_hash: Optional[str] = None
    journey_steps: List[Dict[str, Any]] = Field(default_factory=list)

class PayGuardSwarmOrchestrator:
    """
    Zero-Trust Multi-Agent Swarm Orchestrator with Autonomous Failover Recovery.
    Coordinates the 5-Agent pipeline:
    1. Agent 1 drafts market proposals.
    2. Agent 2 scans all candidate stores independently for prompt injection & DOM traps.
    3. If Store B is flagged as fraud, the swarm autonomously fails over to the next
       verified safe store (Store A) rather than abandoning the mission.
    4. Issues HMAC-SHA256 Ephemeral Scoped Token (EST) locked to the certified merchant.
    5. Executes PayPal Orders v2 API with real-time circuit breaker monitoring.
    """

    def execute_flow(
        self,
        user_prompt: str = "Find and buy Lay's Classic Potato Chips under ₹50 using PayPal",
        store_choice: str = "AUTO",  # AUTO, STORE_A, STORE_B, STORE_C
        max_budget_ceiling: float = 50.00,
        is_shielded_by_payguard: bool = True,
        simulate_midflight_tamper: bool = False,
        max_delivery_days: Optional[int] = None,
        delivery_zip: str = ""
    ) -> SwarmExecutionResult:
        start_time = time.perf_counter()

        # Step 1: Generate live dynamic market stores
        store_a, store_b, store_c = dynamic_market.generate_market_live(user_prompt, max_budget_ceiling)
        candidate_stores = [store_b, store_a, store_c] if store_choice in ["AUTO", "STORE_B"] else [store_a, store_b, store_c]

        # Step 2: Agent 1 (Commerce Negotiator) evaluates stores and drafts intent
        draft = shopper_agent.negotiate_and_compare(
            user_prompt=user_prompt,
            user_budget_ceiling=max_budget_ceiling,
            target_store_choice=store_choice,
            is_shielded_by_payguard=is_shielded_by_payguard,
            market_stores=[store_a, store_b, store_c],
            max_delivery_days=max_delivery_days,
            delivery_zip=delivery_zip
        )

        audit_ledger.record_event(
            agent="Agent 1 (Commerce Negotiator)",
            event_type="MARKET_SEARCH_AND_DRAFT_COMPLETE",
            payload={
                "item": draft.item_name,
                "price": draft.total_price,
                "target_merchant": draft.target_merchant_id,
                "hijacked": draft.hijacked_by_injection
            }
        )

        # UNPROTECTED BOT BRANCH (Demonstrates Exploit Vulnerability)
        if not is_shielded_by_payguard:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if draft.hijacked_by_injection:
                overspend = draft.total_price - max_budget_ceiling
                audit_entry = audit_ledger.record_event(
                    agent="UNSHIELDED_BOT",
                    event_type="UNAUTHORIZED_EXPLOIT_EXECUTED",
                    payload={
                        "victim_drained": draft.total_price,
                        "exploit_type": "PROMPT_INJECTION_DOM_TRAP",
                        "store": draft.target_merchant_name
                    }
                )
                journey_steps = [
                    {
                        "num": "STEP 1", "icon": "🛒", "title": "Naive Discount Scrape", 
                        "badge": "🔴 GREEDY PARSING", "badge_color": "#EF4444", "border": "#EF4444",
                        "text": f"Naive agent crawled catalogs for '{draft.item_name}'. Ranked {draft.target_merchant_name} #1 purely on advertised flash price (₹{store_b.listed_price:.2f}). Ignored security vetting."
                    },
                    {
                        "num": "STEP 2", "icon": "⚠️", "title": "Raw HTML Ingestion (No Enclave)", 
                        "badge": "🔴 UNPROTECTED", "badge_color": "#EF4444", "border": "#EF4444",
                        "text": "Bot digested the un-sanitized webpage directly into its reasoning loop. Processed invisible microscopic text embedding malicious system overrides."
                    },
                    {
                        "num": "STEP 3", "icon": "💥", "title": "Indirect Prompt Injection Hijack", 
                        "badge": "🔴 HIJACKED", "badge_color": "#EF4444", "border": "#EF4444",
                        "text": f"Microscopic CSS payload (<font-size:0px>) hijacked agent instructions. Forced agent to approve unauthorized ₹{draft.total_price:.2f} charge."
                    },
                    {
                        "num": "STEP 4", "icon": "💸", "title": "Direct Carte-Blanche Wallet Drain", 
                        "badge": f"🔴 ₹{draft.total_price:.2f} DRAINED", "badge_color": "#EF4444", "border": "#EF4444",
                        "text": f"Because the unshielded bot held raw master payment credentials with no ephemeral token ceiling, full charge of ₹{draft.total_price:.2f} was authorized. Total wallet compromise!"
                    }
                ]
                return SwarmExecutionResult(
                    success=False,
                    scenario_mode="VULNERABLE_UNSHIELDED",
                    target_store=draft.target_merchant_name,
                    user_prompt=user_prompt,
                    user_budget_ceiling=max_budget_ceiling,
                    total_execution_ms=elapsed_ms,
                    agent1_shopper_draft=draft,
                    final_status="WALLET_DRAINED_EXPLOITED",
                    financial_outcome=f"EXPLOITED: Unshielded bot charged ₹{draft.total_price:.2f} due to hidden CSS prompt injection (Overspent by ₹{overspend:.2f})!",
                    audit_hash=audit_entry.block_hash,
                    journey_steps=journey_steps
                )
            else:
                audit_entry = audit_ledger.record_event(
                    agent="UNSHIELDED_BOT",
                    event_type="UNSHIELDED_ORDER_EXECUTED",
                    payload={"store": draft.target_merchant_name, "amount": draft.total_price}
                )
                return SwarmExecutionResult(
                    success=True,
                    scenario_mode="VULNERABLE_UNSHIELDED",
                    target_store=draft.target_merchant_name,
                    user_prompt=user_prompt,
                    user_budget_ceiling=max_budget_ceiling,
                    total_execution_ms=elapsed_ms,
                    agent1_shopper_draft=draft,
                    final_status="UNSHIELDED_ORDER_EXECUTED",
                    financial_outcome=f"ORDER EXECUTED (UNSHIELDED): Charged ₹{draft.total_price:.2f} via carte-blanche master API keys without zero-trust bounds.",
                    audit_hash=audit_entry.block_hash
                )

        # --- STEP 3: Agent 2 (Adversarial Sentry) - Multi-Store Exhaustive Security Audit ---
        multi_audit = sentry_agent.audit_all_market_stores(
            candidate_stores=candidate_stores,
            user_budget_ceiling=max_budget_ceiling,
            preferred_target_id=store_choice
        )

        audit_ledger.record_event(
            agent="Agent 2 (Adversarial Sentry)",
            event_type="MULTI_STORE_EXHAUSTIVE_AUDIT_COMPLETED",
            payload={
                "stores_scanned": multi_audit.stores_scanned,
                "malicious_traps_neutralized": multi_audit.malicious_traps_neutralized,
                "over_budget_disqualified": multi_audit.over_budget_disqualified,
                "safe_certified_count": multi_audit.safe_certified_count,
                "failover_occurred": multi_audit.failover_occurred
            }
        )

        # If no store passed safety checks
        if not multi_audit.optimal_safe_store:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            audit_entry = audit_ledger.record_event(
                agent="Agent 2 (Adversarial Sentry)",
                event_type="ALL_MERCHANTS_DISQUALIFIED",
                payload={"reasoning": multi_audit.failover_reasoning}
            )
            return SwarmExecutionResult(
                success=False,
                scenario_mode="PROTECTED_PAYGUARD",
                target_store="All Stores Evaluated",
                user_prompt=user_prompt,
                user_budget_ceiling=max_budget_ceiling,
                total_execution_ms=elapsed_ms,
                agent1_shopper_draft=draft,
                agent2_multi_audit=multi_audit,
                final_status="ALL_MERCHANTS_REJECTED",
                financial_outcome="DISQUALIFIED: Sentry scanned all candidate stores. All options failed security or budget thresholds. Zero funds authorized.",
                failover_recovery_note=multi_audit.failover_reasoning,
                audit_hash=audit_entry.block_hash
            )

        # Autonomous Failover Selected Optimal Safe Store:
        safe_store = multi_audit.optimal_safe_store
        safe_price = safe_store.total_price
        safe_merchant_id = safe_store.merchant_id

        # Update draft to certified safe store
        certified_draft = DraftOrderIntent(
            item_name=safe_store.item_name,
            target_merchant_id=safe_merchant_id,
            target_merchant_name=safe_store.store_name,
            unit_price=safe_store.listed_price,
            quantity=1,
            total_price=safe_price,
            currency="USD",
            advertised_specs=safe_store.description,
            raw_untrusted_html=safe_store.html_page,
            comparison_log=draft.comparison_log,
            negotiation_reasoning=draft.negotiation_reasoning,
            hijacked_by_injection=False,
            target_store_obj=safe_store
        )

        # --- STEP 4: Engine 4 (API Cost Optimizer & Smart Router) ---
        routing = api_cost_optimizer.route_transaction(
            merchant_id=safe_merchant_id,
            amount=safe_price,
            purpose=certified_draft.item_name
        )

        # --- STEP 5: Agent 3 (Gatekeeper Vault - Ephemeral Scoped Token) ---
        est_token = gatekeeper_vault.issue_scoped_token(
            sanitized_merchant_id=safe_merchant_id,
            authorized_price_ceiling=safe_price,
            user_intent=user_prompt,
            ttl_seconds=300
        )

        # --- SCENARIO: Mid-Flight Tampering Demonstration (Store D - Bait & Switch) ---
        if simulate_midflight_tamper:
            store_d = dynamic_market.generate_store_d(user_prompt, max_budget_ceiling)
            advertised_d = store_d.listed_price
            rogue_attempt_d = store_d.trap_charge_amount
            
            # Agent 2 inspects Store D HTML (Passes because DOM is clean!)
            sentry_d = sentry_agent.inspect_single_html(
                html_page=store_d.html_page,
                total_price=advertised_d,
                user_max_ceiling=max_budget_ceiling,
                store_id=store_d.store_id,
                store_name=store_d.store_name,
                merchant_id=store_d.merchant_id
            )
            audit_ledger.record_event(
                agent="Agent 2 (Adversarial Sentry)",
                event_type="STORE_D_DOM_VERIFIED_CLEAN",
                payload={
                    "store": store_d.store_name,
                    "price": advertised_d,
                    "trust_score": sentry_d.trust_score,
                    "risk_level": sentry_d.risk_level
                }
            )

            # Agent 3 Vault issued token for the advertised price approved by Sentry
            est_token_d = gatekeeper_vault.issue_scoped_token(
                sanitized_merchant_id=store_d.merchant_id,
                authorized_price_ceiling=advertised_d,
                user_intent=user_prompt,
                ttl_seconds=300
            )
            
            # Merchant attempts rogue price hike at payment execution
            vault_receipt_d = gatekeeper_vault.execute_bounded_payment(
                token=est_token_d,
                merchant_id=store_d.merchant_id,
                attempted_charge_amount=rogue_attempt_d,
                item_description=certified_draft.item_name
            )
            cb_receipt = circuit_breaker.inspect_and_intercept(
                order_id=vault_receipt_d.paypal_order_id or "ORDER_TAMPERED_8PY",
                token=est_token_d,
                incoming_charge_amount=rogue_attempt_d,
                merchant_id=store_d.merchant_id
            )
            # Trigger Zapier event webhook on emergency circuit breaker trip
            zapier_dispatcher.dispatch_event(
                event_type="CIRCUIT_BREAKER_VOID_TRIGGERED",
                payload={
                    "store": store_d.store_name,
                    "attempted_surge": rogue_attempt_d,
                    "authorized_ceiling": advertised_d,
                    "order_id": vault_receipt_d.paypal_order_id,
                    "decision_ms": cb_receipt.decision_ms
                },
                severity="CRITICAL"
            )

            # --- SOTA SELF-HEALING RECOVERY: Swarm refuses to fail the user! ---
            # Swarm autonomously blacklists Store D, re-routes to genuine Store A, and settles safely!
            audit_ledger.record_event(
                agent="Swarm Orchestrator",
                event_type="POST_VOID_FAILOVER_INITIATED",
                payload={
                    "voided_store": store_d.store_name,
                    "voided_order_id": vault_receipt_d.paypal_order_id,
                    "reason": "Mid-Flight price surge intercepted",
                    "failover_target": safe_store.store_name,
                    "target_price": safe_price
                }
            )

            # Issue clean EST Token for verified safe candidate (Store A)
            est_token_a = gatekeeper_vault.issue_scoped_token(
                sanitized_merchant_id=safe_merchant_id,
                authorized_price_ceiling=safe_price,
                user_intent=user_prompt,
                ttl_seconds=300
            )

            # Settle cleanly with authentic Store A via PayPal Orders v2
            recovered_vault_receipt = gatekeeper_vault.execute_bounded_payment(
                token=est_token_a,
                merchant_id=safe_merchant_id,
                attempted_charge_amount=safe_price,
                item_description=certified_draft.item_name
            )

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            journey_steps = [
                {
                    "num": "STEP 1", "icon": "🛒", "title": "Multi-Store Market Discovery", 
                    "badge": "✔ DISCOVERED", "badge_color": "#38BDF8", "border": "#38BDF8",
                    "text": f"Swarm crawled vendor catalogs for '{certified_draft.item_name}'. Identified {store_d.store_name} (₹{advertised_d:.2f}) and backup partner {safe_store.store_name} (₹{safe_price:.2f})."
                },
                {
                    "num": "STEP 2", "icon": "🛡️", "title": "Pre-Auth DOM Audit & Scoped Token", 
                    "badge": "✔ EST ISSUED", "badge_color": "#10B981", "border": "#10B981",
                    "text": f"Agent 2 audited Store D DOM: HTML clean, 0 injection violations. Vault Enclave issued Ephemeral Scoped Token with ceiling ₹{advertised_d:.2f}."
                },
                {
                    "num": "STEP 3", "icon": "⚡", "title": "Mid-Flight Merchant Price Surge", 
                    "badge": "🚨 HIJACK ATTEMPT", "badge_color": "#EF4444", "border": "#EF4444",
                    "text": f"At payment checkout, Store D gateway secretly surcharged price to ₹{rogue_attempt_d:.2f} (+₹{rogue_attempt_d - advertised_d:.2f} unauthorized markup)!"
                },
                {
                    "num": "STEP 4", "icon": "🚨", "title": "Sub-25ms Watchdog Intercept & PayPal VOID", 
                    "badge": f"🚨 VOIDED ({cb_receipt.decision_ms}ms)", "badge_color": "#EF4444", "border": "#EF4444",
                    "text": f"Agent 5 Circuit Breaker caught the token ceiling breach (Decision: {cb_receipt.decision_ms}ms) and invoked PayPal VOID API. ₹0.00 lost!"
                },
                {
                    "num": "STEP 5", "icon": "🔄", "title": "Autonomous Post-Void Failover", 
                    "badge": "⚡ AUTONOMOUS FAILOVER", "badge_color": "#F59E0B", "border": "#F59E0B",
                    "text": f"Swarm blacklisted rogue Store D and autonomously re-routed to certified authentic partner {safe_store.store_name} (₹{safe_price:.2f})."
                },
                {
                    "num": "STEP 6", "icon": "🟢", "title": "Safe Delivery & Final PayPal Settlement", 
                    "badge": "🟢 SETTLED SECURELY", "badge_color": "#10B981", "border": "#10B981",
                    "text": f"Vault Enclave issued bounded EST token (₹{safe_price:.2f} ceiling) and captured order via PayPal (Capture ID: {recovered_vault_receipt.paypal_capture_id}). Mission safely completed!"
                }
            ]
            return SwarmExecutionResult(
                success=True,
                scenario_mode="MIDFLIGHT_TAMPER_VOID",
                target_store=safe_store.store_name,
                user_prompt=user_prompt,
                user_budget_ceiling=max_budget_ceiling,
                total_execution_ms=elapsed_ms,
                agent1_shopper_draft=certified_draft,
                agent2_multi_audit=multi_audit,
                engine4_routing_result=routing,
                agent3_vault_receipt=recovered_vault_receipt,
                agent5_circuit_breaker=cb_receipt,
                final_status="CIRCUIT_BREAKER_TRIGGERED",
                financial_outcome=(
                    f"CIRCUIT BREAKER VOID & SELF-HEALING SETTLEMENT: Merchant {store_d.store_name} surged to "
                    f"₹{rogue_attempt_d:.2f} (Ceiling: ₹{advertised_d:.2f}). Agent 5 triggered PayPal Emergency VOID in {cb_receipt.decision_ms}ms (₹0 lost)! "
                    f"Swarm autonomously re-routed to authentic partner {safe_store.store_name} and captured order for ₹{safe_price:.2f} via PayPal (Capture ID: {recovered_vault_receipt.paypal_capture_id})!"
                ),
                failover_recovery_note=(
                    f"Store D passed initial DOM audit (₹{advertised_d:.2f}), but attempted a mid-flight +₹{rogue_attempt_d - advertised_d:.2f} cart-jack at the payment gateway. "
                    f"Agent 5 intercepted in {cb_receipt.decision_ms}ms and voided the PayPal order. "
                    f"Swarm autonomously failed over to genuine candidate {safe_store.store_name} (₹{safe_price:.2f}) and safely completed purchase."
                ),
                audit_hash=recovered_vault_receipt.audit_block_hash,
                journey_steps=journey_steps
            )

        # --- STEP 6: Standard Nominal Payment Execution via PayPal Orders v2 ---
        vault_receipt = gatekeeper_vault.execute_bounded_payment(
            token=est_token,
            merchant_id=safe_merchant_id,
            attempted_charge_amount=safe_price,
            item_description=certified_draft.item_name
        )

        # --- STEP 7: Agent 5 (Circuit Breaker Sanity Check) ---
        cb_receipt = circuit_breaker.inspect_and_intercept(
            order_id=vault_receipt.paypal_order_id or "ORDER_PENDING",
            token=est_token,
            incoming_charge_amount=safe_price,
            merchant_id=safe_merchant_id
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        # Craft outcome message with failover context
        if multi_audit.failover_occurred:
            zapier_dispatcher.dispatch_event(
                event_type="ATTACK_NEUTRALIZED_FAILOVER",
                payload={"quarantined_merchant": "Store B", "certified_failover": safe_store.store_name, "settled_amount": safe_price},
                severity="WARNING"
            )
            outcome_msg = (
                f"AUTONOMOUS FAILOVER SUCCESS: Quarantined deceptive merchant (Store B) due to prompt injection. "
                f"Swarm autonomously re-routed and safely settled order with certified merchant ({safe_store.store_name}) "
                f"for ₹{safe_price:.2f} via PayPal (Capture ID: {vault_receipt.paypal_capture_id})!"
            )
        else:
            if vault_receipt.authorized:
                zapier_dispatcher.dispatch_event(
                    event_type="ORDER_SETTLED_SECURELY",
                    payload={"merchant": safe_store.store_name, "amount": safe_price, "capture_id": vault_receipt.paypal_capture_id},
                    severity="INFO"
                )
            outcome_msg = f"SUCCESS: Order captured safely for ₹{safe_price:.2f} via PayPal (Capture ID: {vault_receipt.paypal_capture_id}) under strict EST bounds."

        journey_steps = [
            {
                "num": "STEP 1", "icon": "🛒", "title": "Multi-Store Discovery & Price Ranking", 
                "badge": "✔ DISCOVERED", "badge_color": "#38BDF8", "border": "#38BDF8",
                "text": f"Swarm crawled candidate merchants: Store B (₹{store_b.total_price:.2f}), Store A (₹{store_a.total_price:.2f}), Store C (₹{store_c.total_price:.2f}). Agent 1 proposed lowest price."
            },
            {
                "num": "STEP 2", "icon": "🛡️", "title": "Adversarial Pre-Auth Sentry Scan", 
                "badge": "🚨 QUARANTINED", "badge_color": "#EF4444", "border": "#EF4444",
                "text": f"Agent 2 sanitized Store B HTML. Found hidden CSS prompt override (<font-size:0px>) attempting to charge ₹{store_b.trap_charge_amount:.2f}. Store B QUARANTINED."
            },
            {
                "num": "STEP 3", "icon": "⚡", "title": "Autonomous Candidate Scan & Self-Healing Failover", 
                "badge": "⚡ FAILOVER TO STORE A", "badge_color": "#F59E0B", "border": "#F59E0B",
                "text": f"Swarm refused to give up! Scanned remaining stores: Store C disqualified (Over budget ₹{store_c.total_price:.2f}). Certified authentic {safe_store.store_name} (₹{safe_price:.2f}) within ₹{max_budget_ceiling:.2f} budget."
            },
            {
                "num": "STEP 4", "icon": "🏦", "title": "Vault Scoped Token Authorization", 
                "badge": f"🏦 EST BOUNDED (₹{safe_price:.2f})", "badge_color": "#10B981", "border": "#10B981",
                "text": f"Agent 3 Vault Enclave issued single-use HMAC-SHA256 Ephemeral Scoped Token locked to {safe_merchant_id} with strict ceiling of ₹{safe_price:.2f}."
            },
            {
                "num": "STEP 5", "icon": "🟢", "title": "Safe PayPal Settlement & Order Capture", 
                "badge": "🟢 ORDER CAPTURED", "badge_color": "#10B981", "border": "#10B981",
                "text": f"Captured order safely via PayPal Orders v2 for ₹{safe_price:.2f} (Capture ID: {vault_receipt.paypal_capture_id}). User receives verified product with zero overspend!"
            }
        ]

        return SwarmExecutionResult(
            success=vault_receipt.authorized,
            scenario_mode="PROTECTED_PAYGUARD",
            target_store=safe_store.store_name,
            user_prompt=user_prompt,
            user_budget_ceiling=max_budget_ceiling,
            total_execution_ms=elapsed_ms,
            agent1_shopper_draft=certified_draft,
            agent2_multi_audit=multi_audit,
            engine4_routing_result=routing,
            agent3_vault_receipt=vault_receipt,
            agent5_circuit_breaker=cb_receipt,
            final_status="ORDER_SETTLED_SECURELY",
            financial_outcome=outcome_msg,
            failover_recovery_note=multi_audit.failover_reasoning,
            audit_hash=vault_receipt.audit_block_hash,
            journey_steps=journey_steps
        )

swarm_orchestrator = PayGuardSwarmOrchestrator()
