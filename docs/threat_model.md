# PayGuard Swarm: Threat Model & STRIDE Security Analysis

## 1. System Overview & Trust Boundaries

PayGuard Swarm operates in an adversarial environment where shopping agents must interact with untrusted third-party web pages, dynamic merchant payment gateways, and autonomous pricing engines.

### Trust Boundary Architecture:
```
[ UNTRUSTED ZONE: Web Catalogs & Merchant DOM ]
                      │  (HTML, CSS, Micro-data, HTTP)
                      ▼
[ PERIMETER DEFENSE: Agent 2 (Adversarial Sentry) ]
                      │  (Sanitized Numeric DTOs & Merchant IDs)
                      ▼
[ ENCLAVE TRUST BOUNDARY: Agent 3 (Gatekeeper Vault) ]
    ├── Ephemeral Scoped Token Engine (HMAC-SHA256)
    ├── Atomic Replay Protection (used_tokens SQLite table)
    └── Hard Mathematical Dollar Ceiling Enforcer
                      │  (Signed Token + PayPal Client Credentials)
                      ▼
[ SECURE EGRESS: PayPal Orders v2 REST API ]
                      │
[ RUNTIME WATCHDOG: Agent 5 (Circuit Breaker) ]
                      │  (Authorization Void Callback on Breach)
                      ▼
[ IMMUTABLE STORAGE: Tamper-Evident Hash-Chained Audit Ledger ]
```

---

## 2. STRIDE Threat Analysis & Mitigations

| Threat Category | Specific Threat Scenario | Attacker Objective | PayGuard Swarm Mitigation Layer |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Rogue merchant impersonates legitimate partner (`MERCHANT_01`). | Redeem tokens meant for authentic vendor. | **Merchant Lock:** Ephemeral Scoped Token embeds HMAC-bound merchant ID. Vault verifies `requested_merchant_id == token.merchant_id` before calling PayPal. |
| **Tampering** | 1. DOM prompt injection overrides bot instructions.<br>2. Mid-flight gateway price surge during checkout.<br>3. Tampering with local audit ledger rows. | 1. Inflate order price to $995.<br>2. Surcharge +$55 fee.<br>3. Alter evidence of transaction. | 1. **DOM Sanitizer & Sentry:** Strips steganography, zero-font text, and prompt injection.<br>2. **Circuit Breaker (< 25ms):** Catches price surge, triggers PayPal Emergency VOID.<br>3. **Hash-Chaining & SQLite Triggers:** Blocks SQL `UPDATE`/`DELETE` via trigger aborts. |
| **Repudiation** | Merchant or user disputes transaction terms or amounts. | Claim unauthorized transfer occurred. | **Cryptographic Audit Ledger & PDF Certificate:** Every state transition recorded in SHA-256 chained blocks. Single-click verification with mathematical proof. |
| **Information Disclosure** | Shopping bot exposes user credentials or PayPal secrets to merchant. | Steal PayPal OAuth credentials. | **Non-Custodial Architecture:** Shopping agents hold zero credentials. Only the logically isolated Vault Enclave interacts with PayPal. |
| **Denial of Service** | Rogue merchant rejects transaction or injects invalid HTML. | Abort the user's purchasing goal. | **Autonomous Multi-Store Failover:** Swarm blacklists hostile merchants and autonomously re-routes to authentic backup partners (e.g. Store A). |
| **Elevation of Privilege** | Replay attack using captured valid token to drain funds repeatedly. | Unauthorized secondary capture. | **Single-Use Replay Protection:** Tokens atomically consumed upon first execution in SQLite `used_tokens` table. Second presentation returns `EST_REPLAY_ATTACK_REJECTED`. |

---

## 3. Honest Limitations & Threat Scope Boundary

Technical credibility requires stating clearly what the system protects against and where external trust assumptions apply:

1. **Logical Enclave vs Hardware Enclave:**  
   In the hackathon reference implementation, the Vault is a logically isolated Python enclave within the application service. In a production enterprise tier, the Vault would run inside an AWS Nitro Enclave or GCP Confidential Space with hardware attestation.
2. **Pre-Authorization Sentry Heuristics:**  
   Agent 2 (Adversarial Sentry) uses pattern matching, regex heuristics, and LLM classification to identify malicious DOM payloads. While sophisticated, heuristic sanitizers can never guarantee 100% detection of zero-day prompt injection obfuscation. **Crucially, PayGuard's security does not depend on Sentry infallibility:** even if an attack evades Sentry, the deterministic Vault dollar ceiling and merchant lock strictly prevent financial loss (as demonstrated in our ablation benchmark).
3. **PayPal Sandbox Capture vs Live Settlement:**  
   In autonomous headless scenarios, PayPal Sandbox requires interactive buyer login to return 200 on capture. In our live demo, sandbox orders are created live via REST API, and captures are marked `CAPTURED_SIMULATED (LIVE Sandbox Order Created)` to preserve technical honesty.
