import sys
from pathlib import Path
import streamlit as st

# Ensure root workspace is on pythonpath
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="About Us & PayPal Synergy | PayGuard Swarm",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10B981, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 24px;
    }
    .highlight-card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .synergy-box {
        background: #032b1a;
        border-left: 5px solid #10B981;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .danger-box {
        background: #2a0808;
        border-left: 5px solid #EF4444;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Top Navigation Bar
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
with nav_col1:
    st.page_link("app.py", label="🎮 Back to Live Cockpit", icon="🎮")
with nav_col2:
    st.page_link("pages/1_📖_How_To_Use.py", label="📖 How to Operate Guide", icon="📖")
with nav_col3:
    st.page_link("pages/2_🛡️_About_Us.py", label="🛡️ About Us & PayPal Synergy", icon="🛡️", disabled=True)

st.markdown("---")

st.markdown('<div class="main-header">🛡️ About PayGuard Swarm</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The Zero-Trust Financial Enclave Powering Safe Agentic Commerce on PayPal</div>', unsafe_allow_html=True)

# Executive Summary
st.markdown("""
<div class="highlight-card">
    <h3 style="color:#38BDF8; margin-top:0;">🌐 The Mission</h3>
    <p style="font-size:1.1rem; color:#E2E8F0; line-height:1.7;">
        <b>PayGuard Swarm</b> is an open, zero-trust execution protocol that enables autonomous AI agents to negotiate, 
        audit, and settle e-commerce transactions on PayPal without exposing master payment credentials or risking carte-blanche wallet drain.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## ❓ The Critical Question: If PayPal Makes the Payment, What Is Our Role?")

col_prob, col_sol = st.columns(2)

with col_prob:
    st.markdown("""
    <div class="danger-box">
        <h4 style="color:#FCA5A5; margin-top:0;">🚨 The Blindspot in Traditional Payment Rails</h4>
        <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6;">
            PayPal's fraud detection engine was built for <b>human shoppers</b>: it checks browser cookies, IP geography, device fingerprints, and issues <b>SMS OTP 2-Factor Authentication</b>.
        </p>
        <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6;">
            In <b>Agentic Commerce</b>, AI agents run headless 24/7 on remote servers. Forcing a human to approve an SMS OTP on every $2 background micro-purchase destroys automation.
        </p>
        <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6;">
            <b>The Existential Threat:</b> If a user gives their AI agent master PayPal API keys, PayPal has <b>zero visibility into what happened before the API call</b>. If an adversarial merchant uses indirect prompt injection to trick the bot into paying $995 for a $150 item, PayPal processes it as an authorized customer request!
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_sol:
    st.markdown("""
    <div class="synergy-box">
        <h4 style="color:#6EE7B7; margin-top:0;">🛡️ PayGuard: The Cognitive & Cryptographic Firewall</h4>
        <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6;">
            <b>PayPal is the Settlement Rail. PayGuard is the Zero-Trust Defense Enclave.</b>
        </p>
        <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6;">
            PayGuard sits <i>between</i> the untrusted open web and PayPal's payment gateways:
        </p>
        <ul style="color:#CBD5E1; font-size:0.92rem; line-height:1.6;">
            <li><b>Non-Custodial Isolation:</b> Shopping bots have <b>zero keys</b> and cannot execute charges directly.</li>
            <li><b>Cryptographic Enclave:</b> Issues single-use <b>Ephemeral Scoped Tokens (EST)</b> with strict merchant locks and hard dollar caps.</li>
            <li><b>Sub-Second Watchdog:</b> If a merchant attempts post-authorization price tampering, Agent 5 fires PayPal's authorization void API in <b>&lt; 2.5ms</b>.</li>
            <li><b>Micro-Batching:</b> Saves <b>~85% in fees</b> by batching small purchases before hitting PayPal.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 🏛️ The 5 Pillars of Zero-Trust Agentic Commerce")

p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("""
    <div class="highlight-card">
        <h4 style="color:#38BDF8;">1. Non-Custodial Vault</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">
            Agent 1 (Shopper) and Agent 2 (Sentry) hold <b>zero PayPal credentials</b>. If a shopping bot is completely compromised via jailbreak or prompt injection, the attacker gains zero spending ability.
        </p>
    </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown("""
    <div class="highlight-card">
        <h4 style="color:#10B981;">2. Ephemeral Scoped Tokens</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">
            Payments are governed by <b>ESTs</b> with a 300s TTL, strict merchant ID binding, and a mathematical ceiling of <code>min(advertised_price, user_budget)</code> with HMAC-SHA256 signatures.
        </p>
    </div>
    """, unsafe_allow_html=True)

with p3:
    st.markdown("""
    <div class="highlight-card">
        <h4 style="color:#F59E0B;">3. Self-Healing Failover</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">
            Most security systems simply crash or halt when an attack is detected. PayGuard autonomously quarantines the hostile vendor, scans alternative verified candidates, and re-routes the order seamlessly.
        </p>
    </div>
    """, unsafe_allow_html=True)

p4, p5 = st.columns(2)

with p4:
    st.markdown("""
    <div class="highlight-card">
        <h4 style="color:#EF4444;">4. Real-Time Circuit Breaker (< 2.5ms Decision)</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">
            Watches gateway telemetry for bait-and-switch price surges. Directly triggers PayPal's official 
            <code>POST /v2/payments/authorizations/{id}/void</code> endpoint with idempotency headers to guarantee zero settlement loss.
        </p>
    </div>
    """, unsafe_allow_html=True)

with p5:
    st.markdown("""
    <div class="highlight-card">
        <h4 style="color:#A78BFA;">5. Tamper-Evident SHA-256 Chained Ledger</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">
            Every single event is recorded into a rolling SHA-256 block hash. SQLite database triggers prohibit <code>UPDATE</code> and <code>DELETE</code> operations, providing mathematically verifiable audit logs for PCI-DSS compliance.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 📊 Competitive Matrix: How PayGuard is Different")

matrix_data = [
    {"Feature": "Master Key Exposure to Shopping Bot", "Standard AI Shopping Bot": "❌ Full API Key Exposed", "PayPal Checkout Alone": "❌ API Key or Session Cookie", "PayGuard Swarm": "✅ Zero Exposure (Non-Custodial)"},
    {"Feature": "Indirect Prompt Injection Defense", "Standard AI Shopping Bot": "❌ None (Vulnerable to $995 hijack)", "PayPal Checkout Alone": "❌ N/A (Doesn't inspect DOM)", "PayGuard Swarm": "✅ Dual-Layer Sentry + Enclave Ceiling"},
    {"Feature": "Action on Attack", "Standard AI Shopping Bot": "❌ Approves Exploit", "PayPal Checkout Alone": "❌ Processes Charge", "PayGuard Swarm": "✅ Quarantines & Autonomously Re-Routes"},
    {"Feature": "Emergency Void SLA", "Standard AI Shopping Bot": "❌ Manual Human Support", "PayPal Checkout Alone": "❌ Manual Dashboard", "PayGuard Swarm": "✅ < 2.5ms Autonomous Gateway VOID"},
    {"Feature": "Micro-Payment Fee Efficiency", "Standard AI Shopping Bot": "❌ Burns $0.49/order", "PayPal Checkout Alone": "❌ Standard Fixed Fee", "PayGuard Swarm": "✅ ~85% Savings via Micro-Batching"},
    {"Feature": "Immutable Audit Trail", "Standard AI Shopping Bot": "❌ Console Prints", "PayPal Checkout Alone": "✔ Standard Ledger", "PayGuard Swarm": "✅ SHA-256 Chained Ledger + PDF Cert"}
]

st.table(matrix_data)

st.markdown("---")

st.markdown("## 🤝 7 Sponsor Ecosystem Integrations")
st.markdown("""
PayGuard Swarm is designed from the ground up for the **PayPal AI Hackathon (Devpost)** and **AMSE 2026**:
* **1. PayPal Developer Platform:** Orders v2 (`/v2/checkout/orders`), OAuth2 token rotation, capture endpoints, and authorization voiding (`/v2/payments/authorizations/{id}/void`) with `PayPal-Request-Id` idempotency.
* **2. Google Gemini:** Real-time semantic analysis and dynamic market catalog generation with official `gemini-2.5-flash` model.
* **3. AG Grid:** High-performance, dark-mode cybersecurity audit ledger with real-time column sorting and hash filtering.
* **4. Render:** Containerized multi-service Blueprint (`render.yaml`) deploying FastAPI REST API and Streamlit UI with `plan: free`.
* **5. Postman:** Fully verified Postman Collection with automated test scripts asserting Store A success, Store B failover, and Store D emergency voiding.
* **6. Zapier:** Automated SecOps webhook dispatcher sending instant Slack and PagerDuty alerts on circuit breaker trips.
* **7. Channel3:** Normalized multi-store inventory discovery client built for AI agent procurement.
""")

st.markdown("---")

# Bottom Navigation
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    st.page_link("app.py", label="🚀 Launch Live Autonomous Cockpit", icon="🎮")
with btn_col2:
    st.page_link("pages/1_📖_How_To_Use.py", label="📖 Read: How to Operate Guide", icon="📖")
