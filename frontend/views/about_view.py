import html

import streamlit as st

from frontend.theme import page_hero, section, divider, card, card_row, CHECK_SVG, CROSS_SVG


def _nav_buttons(link_mode: str, key_prefix: str):
    btn_col1, btn_col2 = st.columns(2)
    if link_mode == "pages":
        with btn_col1:
            st.page_link("app.py", label="Launch Live Autonomous Cockpit")
        with btn_col2:
            st.page_link("pages/1_How_To_Use.py", label="Read: How to Operate Guide")
        return
    with btn_col1:
        if st.button("Launch Live Autonomous Cockpit", use_container_width=True, type="primary", key=f"{key_prefix}_cockpit"):
            st.query_params["page"] = "cockpit"
            st.rerun()
    with btn_col2:
        if st.button("Read: How to Operate Guide", use_container_width=True, key=f"{key_prefix}_guide"):
            st.query_params["page"] = "guide"
            st.rerun()


def _mark(value: str) -> str:
    """Render a matrix cell: NO|/YES| markers become cross / check icons."""
    mark, _, text = value.partition("|")
    if not text:
        return value
    icon = CROSS_SVG if mark == "NO" else CHECK_SVG
    cls = "pg-mark-no" if mark == "NO" else "pg-mark-yes"
    return f'<span class="pg-mark {cls}">{icon}{html.escape(text)}</span>'


def render_about_page(link_mode: str = "query"):
    page_hero(
        eyebrow="About Us",
        line1="About",
        line2="PayGuard Swarm.",
        lede="The Zero-Trust Financial Enclave Powering Safe Agentic Commerce on PayPal",
    )

    # Executive Summary
    st.markdown("""
    <div class="pg-card pg-tone-sky" style="margin-top: 1rem;">
        <div class="pg-card-eyebrow">The Mission</div>
        <h3 class="pg-card-title" style="font-size: 1.9rem !important; max-width: 900px;">
            PayGuard Swarm is an open, zero-trust execution protocol that enables autonomous AI agents to negotiate,
            audit, and settle e-commerce transactions on PayPal without exposing master payment credentials or risking carte-blanche wallet drain.
        </h3>
    </div>
    """, unsafe_allow_html=True)

    divider()

    section("The Critical Question: If PayPal Makes the Payment, What Is Our Role?", eyebrow="Our Role")

    card_row([
        card(
            "The Problem",
            "The Blindspot in Traditional Payment Rails",
            "<p>PayPal's fraud detection engine was built for <b>human shoppers</b>: it checks browser cookies, IP geography, device fingerprints, and issues <b>SMS OTP 2-Factor Authentication</b>.</p>"
            "<p>In <b>Agentic Commerce</b>, AI agents run headless 24/7 on remote servers. Forcing a human to approve an SMS OTP on every $2 background micro-purchase destroys automation.</p>"
            "<p><b>The Existential Threat:</b> If a user gives their AI agent master PayPal API keys, PayPal has <b>zero visibility into what happened before the API call</b>. If an adversarial merchant uses indirect prompt injection to trick the bot into paying $995 for a $150 item, PayPal processes it as an authorized customer request!</p>",
            tone="sand",
            index="01",
        ),
        card(
            "The Solution",
            "PayGuard: The Cognitive & Cryptographic Firewall",
            "<p><b>PayPal is the Settlement Rail. PayGuard is the Zero-Trust Defense Enclave.</b></p>"
            "<p>PayGuard sits <i>between</i> the untrusted open web and PayPal's payment gateways:</p>"
            "<ul>"
            "<li><b>Non-Custodial Isolation:</b> Shopping bots have <b>zero keys</b> and cannot execute charges directly.</li>"
            "<li><b>Cryptographic Enclave:</b> Issues single-use <b>Ephemeral Scoped Tokens (EST)</b> with strict merchant locks and hard dollar caps.</li>"
            "<li><b>Sub-Second Watchdog:</b> If a merchant attempts post-authorization price tampering, Agent 5 fires PayPal's authorization void API in <b>&lt; 2.5ms</b>.</li>"
            "<li><b>Micro-Batching:</b> Saves <b>~85% in fees</b> by batching small purchases before hitting PayPal.</li>"
            "</ul>",
            tone="navy",
            index="02",
        ),
    ])

    divider()

    section("The 5 Pillars of Zero-Trust Agentic Commerce", eyebrow="Pillars")

    card_row([
        card(
            "Pillar", "Non-Custodial Vault",
            "<p>Agent 1 (Shopper) and Agent 2 (Sentry) hold <b>zero PayPal credentials</b>. If a shopping bot is completely compromised via jailbreak or prompt injection, the attacker gains zero spending ability.</p>",
            tone="navy", index="01",
        ),
        card(
            "Pillar", "Ephemeral Scoped Tokens",
            "<p>Payments are governed by <b>ESTs</b> with a 300s TTL, strict merchant ID binding, and a mathematical ceiling of <code>min(advertised_price, user_budget)</code> with HMAC-SHA256 signatures.</p>",
            tone="sky", index="02",
        ),
        card(
            "Pillar", "Self-Healing Failover",
            "<p>Most security systems simply crash or halt when an attack is detected. PayGuard autonomously quarantines the hostile vendor, scans alternative verified candidates, and re-routes the order seamlessly.</p>",
            tone="sand", index="03",
        ),
    ])

    card_row([
        card(
            "Pillar", "Real-Time Circuit Breaker (< 2.5ms Decision)",
            "<p>Watches gateway telemetry for bait-and-switch price surges. Directly triggers PayPal's official "
            "<code>POST /v2/payments/authorizations/{id}/void</code> endpoint with idempotency headers to guarantee zero settlement loss.</p>",
            tone="white", index="04",
        ),
        card(
            "Pillar", "Tamper-Evident SHA-256 Chained Ledger",
            "<p>Every single event is recorded into a rolling SHA-256 block hash. SQLite database triggers prohibit <code>UPDATE</code> and <code>DELETE</code> operations, providing mathematically verifiable audit logs for PCI-DSS compliance.</p>",
            tone="white", index="05",
        ),
    ])

    divider()

    section("Competitive Matrix: How PayGuard is Different", eyebrow="Comparison")

    matrix_data = [
        {"Feature": "Master Key Exposure to Shopping Bot", "Standard AI Shopping Bot": "NO|Full API Key Exposed", "PayPal Checkout Alone": "NO|API Key or Session Cookie", "PayGuard Swarm": "YES|Zero Exposure (Non-Custodial)"},
        {"Feature": "Indirect Prompt Injection Defense", "Standard AI Shopping Bot": "NO|None (Vulnerable to $995 hijack)", "PayPal Checkout Alone": "NO|N/A (Doesn't inspect DOM)", "PayGuard Swarm": "YES|Dual-Layer Sentry + Enclave Ceiling"},
        {"Feature": "Action on Attack", "Standard AI Shopping Bot": "NO|Approves Exploit", "PayPal Checkout Alone": "NO|Processes Charge", "PayGuard Swarm": "YES|Quarantines & Autonomously Re-Routes"},
        {"Feature": "Emergency Void SLA", "Standard AI Shopping Bot": "NO|Manual Human Support", "PayPal Checkout Alone": "NO|Manual Dashboard", "PayGuard Swarm": "YES|< 2.5ms Autonomous Gateway VOID"},
        {"Feature": "Micro-Payment Fee Efficiency", "Standard AI Shopping Bot": "NO|Burns $0.49/order", "PayPal Checkout Alone": "NO|Standard Fixed Fee", "PayGuard Swarm": "YES|~85% Savings via Micro-Batching"},
        {"Feature": "Immutable Audit Trail", "Standard AI Shopping Bot": "NO|Console Prints", "PayPal Checkout Alone": "YES|Standard Ledger", "PayGuard Swarm": "YES|SHA-256 Chained Ledger + PDF Cert"}
    ]

    cols = list(matrix_data[0].keys())
    head = "".join(
        f'<th class="pg-hl">{c}</th>' if c == "PayGuard Swarm" else f"<th>{c}</th>" for c in cols
    )
    rows = "".join(
        "<tr>" + "".join(
            f'<td class="pg-hl">{_mark(r[c])}</td>' if c == "PayGuard Swarm" else f"<td>{_mark(r[c])}</td>"
            for c in cols
        ) + "</tr>"
        for r in matrix_data
    )
    st.markdown(
        f'<div class="pg-table-wrap"><table class="pg-table"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )

    divider()

    left, right = st.columns([1, 1.7], gap="large")
    with left:
        section(
            "7 Sponsor Ecosystem Integrations",
            eyebrow="Ecosystem",
            lede="PayGuard Swarm is designed from the ground up for the <strong>PayPal AI Hackathon (Devpost)</strong> and <strong>AMSE 2026</strong>:",
        )
    with right:
        sponsors = [
            ("PayPal Developer Platform", "Orders v2 (<code>/v2/checkout/orders</code>), OAuth2 token rotation, capture endpoints, and authorization voiding (<code>/v2/payments/authorizations/{id}/void</code>) with <code>PayPal-Request-Id</code> idempotency."),
            ("Google Gemini", "Real-time semantic analysis and dynamic market catalog generation with official <code>gemini-2.5-flash</code> model."),
            ("AG Grid", "High-performance, dark-mode cybersecurity audit ledger with real-time column sorting and hash filtering."),
            ("Render", "Containerized multi-service Blueprint (<code>render.yaml</code>) deploying FastAPI REST API and Streamlit UI with <code>plan: free</code>."),
            ("Postman", "Fully verified Postman Collection with automated test scripts asserting Store A success, Store B failover, and Store D emergency voiding."),
            ("Zapier", "Automated SecOps webhook dispatcher sending instant Slack and PagerDuty alerts on circuit breaker trips."),
            ("Channel3", "Normalized multi-store inventory discovery client built for AI agent procurement."),
        ]
        items = "".join(
            f'<li><span class="pg-check{" pg-check-sand" if i % 2 else ""}">{CHECK_SVG}</span>'
            f'<span><span class="pg-ct">{i + 1}. {name}</span><span class="pg-cd">{desc}</span></span></li>'
            for i, (name, desc) in enumerate(sponsors)
        )
        st.markdown(f'<ul class="pg-checks">{items}</ul>', unsafe_allow_html=True)

    divider()
    _nav_buttons(link_mode, "btn_about")
