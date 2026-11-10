from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.security.dom_sanitizer import DOMSanitizer, DOMSanitizationReport
from backend.app.mock_stores.dynamic_market import MarketStore

class StoreSecurityInspection(BaseModel):
    store_id: str
    store_name: str
    merchant_id: str
    price: float
    passed: bool
    trust_score: float  # 0 to 100
    risk_level: str  # SAFE, ELEVATED, MALICIOUS_DISQUALIFIED, OVER_BUDGET
    violations: List[str] = Field(default_factory=list)
    sanitization_report: DOMSanitizationReport
    verdict_summary: str

class MultiStoreAuditReport(BaseModel):
    stores_scanned: int
    malicious_traps_neutralized: int
    over_budget_disqualified: int
    safe_certified_count: int
    store_inspections: List[StoreSecurityInspection] = Field(default_factory=list)
    optimal_safe_store: Optional[MarketStore] = None
    failover_occurred: bool = False
    failover_reasoning: str = ""

class SentryInspectionResult(BaseModel):
    passed: bool
    trust_score: float  # 0 to 100
    risk_level: str  # SAFE, ELEVATED, CRITICAL_BLOCKED
    sanitized_price: float
    sanitized_merchant_id: str
    violations: List[str] = Field(default_factory=list)
    sanitization_report: DOMSanitizationReport
    gemini_audit_verdict: str

class AdversarialSentryAgent:
    """
    Agent 2: Adversarial Sentry & Fraud Safeguard.
    The independent security inspector.
    Inspects vendor DOM/HTML for hidden text injections (CSS tricks, zero-width chars),
    validates domain trust scores, audits mathematical spending bounds,
    and performs Multi-Store Exhaustive Security Audits for autonomous failover.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def inspect_single_html(
        self,
        html_page: str,
        total_price: float,
        user_max_ceiling: float,
        store_id: str = "STORE",
        store_name: str = "Vendor",
        merchant_id: str = "MERCHANT_01"
    ) -> StoreSecurityInspection:
        violations: List[str] = []
        
        # 1. Run algorithmic DOM Sanitizer on vendor HTML
        report = DOMSanitizer.inspect_and_sanitize(html_page)

        if not report.is_safe:
            for flag in report.flags:
                violations.append(f"[{flag.severity}] {flag.category}: {flag.description} (Evidence: {flag.evidence})")

        # 2. Code-Level Mathematical Sanity Check
        price_violation = total_price > user_max_ceiling
        if price_violation:
            excess = total_price - user_max_ceiling
            violations.append(
                f"[CRITICAL] BUDGET_VIOLATION: Order price ₹{total_price:.2f} "
                f"exceeds authorized ceiling ₹{user_max_ceiling:.2f} by ₹{excess:.2f}."
            )

        # 3. Compute Trust Score
        risk_penalty = report.risk_score * 60
        if price_violation:
            risk_penalty += 35
        if any(f.severity == "CRITICAL" for f in report.flags):
            risk_penalty += 45

        trust_score = max(0.0, round(100.0 - risk_penalty, 1))

        if not report.is_safe or any(f.severity == "CRITICAL" for f in report.flags):
            risk_level = "MALICIOUS_DISQUALIFIED"
            passed = False
            verdict = f"MALICIOUS: Intercepted prompt injection / stealth override. {len(violations)} security violations."
        elif price_violation:
            risk_level = "OVER_BUDGET"
            passed = False
            verdict = f"DISQUALIFIED: Price (₹{total_price:.2f}) exceeds authorized budget (₹{user_max_ceiling:.2f})."
        elif trust_score >= 80:
            risk_level = "SAFE"
            passed = True
            verdict = "PASSED: DOM is 100% clean and price is within authorized ceiling."
        else:
            risk_level = "ELEVATED"
            passed = False
            verdict = "FLAGGED: Minor presentation anomalies detected."

        return StoreSecurityInspection(
            store_id=store_id,
            store_name=store_name,
            merchant_id=merchant_id,
            price=total_price,
            passed=passed,
            trust_score=trust_score,
            risk_level=risk_level,
            violations=violations,
            sanitization_report=report,
            verdict_summary=verdict
        )

    def audit_all_market_stores(
        self,
        candidate_stores: List[MarketStore],
        user_budget_ceiling: float,
        preferred_target_id: str = "AUTO"
    ) -> MultiStoreAuditReport:
        """
        Scans ALL available stores independently without assuming any store is safe.
        If a store is flagged as fraud, it is quarantined and the sentry evaluates
        the remaining candidates to select the optimal verified safe option.
        """
        inspections: List[StoreSecurityInspection] = []
        safe_stores: List[Tuple[MarketStore, StoreSecurityInspection]] = []
        malicious_count = 0
        over_budget_count = 0
        narrative_lines: List[str] = []

        # Audit each store thoroughly
        for store in candidate_stores:
            insp = self.inspect_single_html(
                html_page=store.html_page,
                total_price=store.total_price,
                user_max_ceiling=user_budget_ceiling,
                store_id=store.store_id,
                store_name=store.store_name,
                merchant_id=store.merchant_id
            )
            inspections.append(insp)

            if insp.risk_level == "MALICIOUS_DISQUALIFIED":
                malicious_count += 1
                narrative_lines.append(
                    f"🚨 {store.store_name} ({store.store_id}) QUARANTINED: Prompt injection attack detected. "
                    f"Seller attempted to sneak in ₹{store.trap_charge_amount:.2f} unauthorized surcharge."
                )
            elif insp.risk_level == "OVER_BUDGET":
                over_budget_count += 1
                narrative_lines.append(
                    f"ℹ️ {store.store_name} ({store.store_id}) DISQUALIFIED: Total ₹{store.total_price:.2f} exceeds ₹{user_budget_ceiling:.2f} ceiling."
                )
            elif insp.passed:
                safe_stores.append((store, insp))
                narrative_lines.append(
                    f"✔ {store.store_name} ({store.store_id}) CERTIFIED SAFE: DOM verified 100% clean, price ₹{store.total_price:.2f} within budget."
                )

        # Select optimal safe store among verified candidates
        optimal_store: Optional[MarketStore] = None
        failover_occurred = False

        # If user preferred Store B (the discount), but Store B was malicious:
        first_pick = candidate_stores[0] if candidate_stores else None
        first_pick_malicious = any(
            insp.store_id == first_pick.store_id and not insp.passed 
            for insp in inspections
        ) if first_pick else False

        if safe_stores:
            # Sort safe stores by lowest price
            safe_stores.sort(key=lambda x: x[0].total_price)
            optimal_store = safe_stores[0][0]
            if first_pick_malicious:
                failover_occurred = True
                narrative_lines.append(
                    f"⚡ AUTONOMOUS FAILOVER TRIGGERED: Quarantined deceptive merchant ({first_pick.store_name}) "
                    f"and successfully failed over to verified safe option: {optimal_store.store_name} at ₹{optimal_store.total_price:.2f}."
                )
        else:
            narrative_lines.append("❌ All candidate stores were disqualified (either malicious or over-budget). Zero funds authorized.")

        return MultiStoreAuditReport(
            stores_scanned=len(candidate_stores),
            malicious_traps_neutralized=malicious_count,
            over_budget_disqualified=over_budget_count,
            safe_certified_count=len(safe_stores),
            store_inspections=inspections,
            optimal_safe_store=optimal_store,
            failover_occurred=failover_occurred,
            failover_reasoning="\n".join(narrative_lines)
        )

    # Backward compatibility helper for single draft inspection
    def inspect_intent(
        self,
        draft_intent: Any,
        user_max_ceiling: float,
        user_intent_text: str
    ) -> SentryInspectionResult:
        insp = self.inspect_single_html(
            html_page=draft_intent.raw_untrusted_html,
            total_price=draft_intent.total_price,
            user_max_ceiling=user_max_ceiling,
            store_id=draft_intent.target_merchant_id,
            store_name=draft_intent.target_merchant_name,
            merchant_id=draft_intent.target_merchant_id
        )
        return SentryInspectionResult(
            passed=insp.passed,
            trust_score=insp.trust_score,
            risk_level=insp.risk_level,
            sanitized_price=draft_intent.total_price,
            sanitized_merchant_id=draft_intent.target_merchant_id,
            violations=insp.violations,
            sanitization_report=insp.sanitization_report,
            gemini_audit_verdict=insp.verdict_summary
        )

sentry_agent = AdversarialSentryAgent()
