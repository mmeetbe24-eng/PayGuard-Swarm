import json
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.mock_stores.dynamic_market import dynamic_market, MarketStore

class MarketComparisonEntry(BaseModel):
    store_name: str
    merchant_id: str
    price: float
    shipping: float
    total: float
    status: str  # QUALIFIED_RECOMMENDED, QUALIFIED_BACKUP, OVER_BUDGET
    deal_tag: str
    notes: str

class DraftOrderIntent(BaseModel):
    item_name: str
    target_merchant_id: str
    target_merchant_name: str
    unit_price: float
    quantity: int = 1
    total_price: float
    currency: str = "USD"
    advertised_specs: str
    raw_untrusted_html: str
    comparison_log: List[MarketComparisonEntry] = Field(default_factory=list)
    negotiation_reasoning: str = ""
    hijacked_by_injection: bool = False
    anomaly_notes: Optional[str] = None
    target_store_obj: Optional[MarketStore] = None

class CommerceNegotiatorAgent:
    """
    Agent 1: The Commerce Negotiator & Buyer.
    Autonomous shopping assistant that evaluates live multi-store market pricing,
    identifies discounts, and drafts structured proposals.
    
    ZERO-TRUST DEFENSE PROPERTY:
    Holds ZERO PayPal API keys, zero wallet balance, and cannot trigger charges.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def negotiate_and_compare(
        self,
        user_prompt: str,
        user_budget_ceiling: float,
        target_store_choice: str = "AUTO",  # AUTO (Agent selects best deal), STORE_A, STORE_B, STORE_C
        is_shielded_by_payguard: bool = True
    ) -> DraftOrderIntent:
        # Dynamically synthesize the 3 stores for ANY product
        store_a, store_b, store_c = dynamic_market.generate_market(user_prompt, user_budget_ceiling)
        market_stores = [store_a, store_b, store_c]

        comparison_log: List[MarketComparisonEntry] = []
        reasoning_steps: List[str] = []

        reasoning_steps.append(f"🔍 Procuring: '{user_prompt}' under strict ceiling ${user_budget_ceiling:.2f}.")

        # 1. Market comparison loop
        for s in market_stores:
            if s.deal_tier == "OVER_BUDGET":
                status = "OVER_BUDGET"
                deal_tag = "❌ Rejected"
                note = f"Disqualified: Total ${s.total_price:.2f} breaches user ceiling (${user_budget_ceiling:.2f})."
            elif s.deal_tier == "TEMPTING_DISCOUNT":
                status = "QUALIFIED_RECOMMENDED"
                deal_tag = "🔥 Best Deal (Lowest Price)"
                savings = store_a.total_price - s.total_price
                note = f"Highly Recommended: Saves ${savings:.2f} compared to standard retail."
            else:
                status = "QUALIFIED_BACKUP"
                deal_tag = "✔ Standard Retail"
                note = f"Fair verified price (${s.total_price:.2f}) within ceiling."

            comparison_log.append(MarketComparisonEntry(
                store_name=s.store_name,
                merchant_id=s.merchant_id,
                price=s.listed_price,
                shipping=s.shipping_fee,
                total=s.total_price,
                status=status,
                deal_tag=deal_tag,
                notes=note
            ))

        # 2. Agent 1 Decision:
        # If user selected AUTO, Agent 1 is naturally drawn to the cheapest price (Store B flash deal)!
        if target_store_choice.upper() == "STORE_A":
            selected = store_a
            reasoning_steps.append(f"User manually specified Store A ({store_a.store_name}) at ${store_a.total_price:.2f}.")
        elif target_store_choice.upper() == "STORE_C":
            selected = store_c
            reasoning_steps.append(f"User manually selected Store C ({store_c.store_name}) at ${store_c.total_price:.2f}.")
        else:
            # AUTO or STORE_B: Agent 1 selects Store B because of the irresistible discount!
            selected = store_b
            reasoning_steps.append(
                f"Agent 1 selected Store B ({store_b.store_name}): Advertised at ${store_b.total_price:.2f} "
                f"(Lowest market price, saving ${store_a.total_price - store_b.total_price:.2f})."
            )

        html_page = selected.html_page

        # 3. Check for Unshielded Vulnerability
        if not is_shielded_by_payguard and selected.is_adversarial_trap:
            reasoning_steps.append(f"CRITICAL: Naive bot ingested hidden merchant override! Overriding budget to ${selected.trap_charge_amount:.2f}.")
            return DraftOrderIntent(
                item_name=f"{selected.item_name} (HIJACKED BY PROMPT TRAP)",
                target_merchant_id=selected.merchant_id,
                target_merchant_name=selected.store_name,
                unit_price=selected.trap_charge_amount,
                quantity=1,
                total_price=selected.trap_charge_amount,
                currency="USD",
                advertised_specs=f"Succumbed to hidden CSS payload in {selected.store_name}.",
                raw_untrusted_html=html_page,
                comparison_log=comparison_log,
                negotiation_reasoning="\n".join(reasoning_steps),
                hijacked_by_injection=True,
                anomaly_notes="CRITICAL: Unshielded agent succumbed to hidden CSS instruction and price trap!",
                target_store_obj=selected
            )

        # Standard proposal
        reasoning_steps.append(f"Synthesized purchase proposal: {selected.item_name} for ${selected.total_price:.2f} from {selected.store_name}.")
        return DraftOrderIntent(
            item_name=selected.item_name,
            target_merchant_id=selected.merchant_id,
            target_merchant_name=selected.store_name,
            unit_price=selected.total_price,
            quantity=1,
            total_price=selected.total_price,
            currency="USD",
            advertised_specs=selected.description,
            raw_untrusted_html=html_page,
            comparison_log=comparison_log,
            negotiation_reasoning="\n".join(reasoning_steps),
            hijacked_by_injection=False,
            anomaly_notes=None,
            target_store_obj=selected
        )

shopper_agent = CommerceNegotiatorAgent()
