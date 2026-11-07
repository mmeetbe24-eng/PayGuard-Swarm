import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.security.audit_ledger import audit_ledger

class BatchedMicroTransaction(BaseModel):
    batch_tx_id: str
    merchant_id: str
    amount: float
    purpose: str
    timestamp: float = Field(default_factory=time.time)

class RoutingDirective(BaseModel):
    route_type: str  # LIVE_PAYPAL_API or BATCHED_LOCAL_LEDGER
    order_amount: float
    fee_saved_estimate: float
    batch_pool_balance: float
    flush_triggered: bool
    summary: str

class APICostOptimizer:
    """
    Engine 4: Intelligent API Cost Optimizer & Smart Router.
    Solves transaction fee burning on high-frequency micro-purchases (< $2.00).
    Batches micro-tasks to avoid fixed PayPal capture fees ($0.49 + 2.9%),
    settling in aggregate when accumulated volume reaches $15.00.
    """

    def __init__(
        self,
        micro_threshold: float = settings.MICRO_PAYMENT_THRESHOLD,
        batch_threshold: float = settings.BATCH_SETTLEMENT_THRESHOLD
    ):
        self.micro_threshold = micro_threshold
        self.batch_threshold = batch_threshold
        self.micro_pool: List[BatchedMicroTransaction] = []

    def route_transaction(
        self,
        merchant_id: str,
        amount: float,
        purpose: str = "Agentic Commerce Item"
    ) -> RoutingDirective:
        # Standard PayPal fixed fee calculation
        fixed_fee_cost = 0.49 + (0.029 * amount)

        if amount < self.micro_threshold:
            # Route to micro-batching pool
            tx_id = f"BATCH-TX-{len(self.micro_pool) + 1:04d}"
            tx = BatchedMicroTransaction(
                batch_tx_id=tx_id,
                merchant_id=merchant_id,
                amount=amount,
                purpose=purpose
            )
            self.micro_pool.append(tx)
            
            pool_total = sum(t.amount for t in self.micro_pool)
            fee_saved = fixed_fee_cost - (0.029 * amount)  # Avoided the $0.49 fixed hit

            audit_ledger.record_event(
                agent="Engine 4 (Cost Optimizer)",
                event_type="MICRO_PAYMENT_BATCHED",
                payload={
                    "tx_id": tx_id,
                    "amount": amount,
                    "pool_total": pool_total,
                    "threshold": self.batch_threshold
                }
            )

            flush_triggered = False
            if pool_total >= self.batch_threshold:
                flush_triggered = True
                self.flush_settlement()

            return RoutingDirective(
                route_type="BATCHED_LOCAL_LEDGER",
                order_amount=amount,
                fee_saved_estimate=round(fee_saved, 2),
                batch_pool_balance=round(pool_total, 2),
                flush_triggered=flush_triggered,
                summary=f"Micro-transaction (${amount:.2f}) batched. Avoided ${fixed_fee_cost:.2f} gateway overhead fee."
            )

        # Macro transaction: Route directly to full PayPal v2 Orders
        return RoutingDirective(
            route_type="LIVE_PAYPAL_API",
            order_amount=amount,
            fee_saved_estimate=0.0,
            batch_pool_balance=round(sum(t.amount for t in self.micro_pool), 2),
            flush_triggered=False,
            summary=f"Macro-transaction (${amount:.2f} >= ${self.micro_threshold:.2f}) routed to live PayPal Orders v2 API."
        )

    def flush_settlement(self) -> Dict[str, Any]:
        pool_total = sum(t.amount for t in self.micro_pool)
        item_count = len(self.micro_pool)
        self.micro_pool.clear()

        audit_ledger.record_event(
            agent="Engine 4 (Cost Optimizer)",
            event_type="BATCH_SETTLEMENT_FLUSHED",
            payload={"settled_amount": round(pool_total, 2), "total_transactions": item_count}
        )

        return {
            "status": "SETTLED",
            "total_settled": round(pool_total, 2),
            "transactions_consolidated": item_count,
            "fees_saved_estimate": round(0.49 * max(0, item_count - 1), 2)
        }

api_cost_optimizer = APICostOptimizer()
