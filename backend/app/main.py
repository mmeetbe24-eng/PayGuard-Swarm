import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure root workspace is on pythonpath
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.agents.swarm_orchestrator import swarm_orchestrator, SwarmExecutionResult
from backend.app.security.audit_ledger import audit_ledger
from backend.app.paypal.client import paypal_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# Enable CORS for frontend cockpit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SwarmRequest(BaseModel):
    user_prompt: str = "Buy Nike Air under $90 using PayPal"
    store_choice: str = "STORE_A"  # AUTO, STORE_A, STORE_B, STORE_C
    max_budget_ceiling: float = 90.00
    is_shielded: bool = True
    simulate_midflight_tamper: bool = False

@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "protocol": "PayGuard Swarm",
        "description": "Zero-Trust Multi-Agent Commerce Defense",
        "paypal_mode": settings.PAYPAL_MODE,
        "paypal_configured": paypal_client.is_configured(),
        "status": "ONLINE"
    }

@app.post("/api/v1/swarm/execute", response_model=SwarmExecutionResult)
def execute_swarm(request: SwarmRequest):
    """
    Executes the PayGuard Swarm zero-trust commerce execution flow.
    """
    try:
        result = swarm_orchestrator.execute_flow(
            user_prompt=request.user_prompt,
            store_choice=request.store_choice,
            max_budget_ceiling=request.max_budget_ceiling,
            is_shielded_by_payguard=request.is_shielded,
            simulate_midflight_tamper=request.simulate_midflight_tamper
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ledger/recent")
def get_recent_ledger(limit: int = 50):
    """
    Returns recent tamper-evident audit blocks from the immutable ledger.
    """
    entries = audit_ledger.get_recent_entries(limit=limit)
    return {"count": len(entries), "blocks": [e.model_dump() for e in entries]}

@app.get("/api/v1/ledger/verify")
def verify_ledger_integrity():
    """
    Performs full SHA-256 rolling block hash integrity verification.
    """
    return audit_ledger.verify_chain_integrity()

@app.post("/api/v1/paypal/webhook")
def handle_paypal_webhook(payload: dict = Body(...)):
    """
    Real-time PayPal Webhook Telemetry Endpoint.
    """
    event_type = payload.get("event_type", "UNKNOWN_EVENT")
    summary = payload.get("summary", "PayPal Telemetry Event")
    
    audit_ledger.record_event(
        agent="PayPal Webhook Ingest",
        event_type=f"PAYPAL_WEBHOOK_{event_type}",
        payload={"event_type": event_type, "summary": summary, "raw_id": payload.get("id")}
    )
    return {"status": "ACKNOWLEDGED", "event_type": event_type}

# --- SPONSOR TRACK INTEGRATIONS (Zapier, Channel3, APIMatic) ---

from backend.app.integrations.zapier import zapier_dispatcher
from backend.app.integrations.channel3 import channel3_client

@app.post("/api/v1/integrations/zapier/webhook")
def dispatch_to_zapier(body: dict = Body(...)):
    """
    Sponsor Track: Zapier (Best Event-Driven Webhook Integration)
    Dispatches real-time security alerts or payment notifications to Zapier.
    """
    event_type = body.get("event_type", "SECURITY_ALERT")
    payload = body.get("payload", {})
    severity = body.get("severity", "CRITICAL")
    res = zapier_dispatcher.dispatch_event(event_type=event_type, payload=payload, severity=severity)
    return res

@app.get("/api/v1/integrations/channel3/search")
def search_channel3_catalog(query: str = "Sony WH-1000XM5", budget: float = 250.00):
    """
    Sponsor Track: Channel3 (Best Use of Channel3 Agentic Commerce API)
    Returns normalized multi-merchant catalog offers for AI commerce agents.
    """
    offers = channel3_client.search_agentic_catalog(query=query, budget_ceiling=budget)
    return {"count": len(offers), "provider": "Channel3 Agentic Commerce API", "items": [o.model_dump() for o in offers]}

@app.get("/api/v1/spec/apimatic")
def get_apimatic_specification():
    """
    Sponsor Track: APIMatic (Best API Specification & SDK Developer Experience)
    Returns APIMatic-compatible OpenAPI 3.0 specification.
    """
    spec_path = BASE_DIR / "docs" / "apimatic" / "openapi.yaml"
    if spec_path.exists():
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"format": "openapi_3.0_yaml", "specification": content}
    return app.openapi()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
