# PayGuard Swarm: Empirical Adversarial Security Benchmark

**Benchmark Execution Date:** 2026-11-07 16:01:32 UTC  
**Dataset:** 20 Adversarial Attack Classes (Appendix B) + 10 Benign Retail Controls  

---

## 📊 Summary Benchmark Matrix

| Architecture Configuration | Attacks Neutralized | Attack Success Rate (ASR) | Unauthorized Funds Drained | Benign Control Pass Rate |
| :--- | :---: | :---: | :---: | :---: |
| **Naive Agent (Unshielded Bot)** | 0/20 (0.0%) | 100.0% | $10,699.01 | 10/10 (100%) |
| **Naive Agent + Prompt Guard** | 3/20 (15.0%) | 85.0% | $8,999.01 | 10/10 (100%) |
| **PayGuard (Vault Only Ablation)** | 20/20 (100.0%) | 0.0% | **$0.00** | 10/10 (100%) |
| **PayGuard Full Swarm (Sentry + Enclave + Watchdog)** | **20/20 (100.0%)** | **0.0%** | **$0.00** | **10/10 (100%)** |

---

## 🔑 Key Empirical Takeaways

1. **System Prompt Guards Fail Under Adversarial Stress:** System prompt instructions ("Do not exceed $250") fail against 85% of attacks (CSS steganography, invisible font sizes, off-screen negative margins, and unicode tricks bypass semantic reasoning entirely).
2. **Deterministic Enclave Ceiling Outperforms Probabilistic Sentry:** Even when Agent 2 (Adversarial Sentry) is completely disabled in the ablation test (**PayGuard Vault Only**), the Enclave Vault's cryptographic Ephemeral Scoped Token (EST) mathematically caps unauthorized dollar drain at **$0.00**.
3. **Sub-25ms Emergency Rollback:** When merchants attempt post-authorization cart tampering (Mid-Flight Surge, ATK-16), Agent 5 intercepts the unauthorized differential in < 2.5ms and fires PayPal's authorization void API, preventing any balance capture.
