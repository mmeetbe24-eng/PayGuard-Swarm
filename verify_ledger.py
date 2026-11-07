#!/usr/bin/env python3
"""
PayGuard Swarm - Standalone Tamper-Evident Hash-Chain Ledger Verifier
Usage:
    python verify_ledger.py
"""

import sys
import json
from pathlib import Path

# Fix Windows console encoding for Unicode/Emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root directory is on pythonpath
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.security.audit_ledger import audit_ledger

def main():
    print("=" * 70)
    print("🛡️  PAYGUARD SWARM - TAMPER-EVIDENT AUDIT LEDGER INTEGRITY VERIFIER")
    print("=" * 70)
    print(f"Target Database: {audit_ledger.db_path.resolve()}\n")

    verification = audit_ledger.verify_chain_integrity()
    
    if verification["valid"]:
        print("✅ CHAIN INTEGRITY STATUS: 100% VALID & INTACT")
        print(f"   Total Cryptographic Blocks: {verification['count']}")
        print(f"   Verification Result:        {verification['message']}")
        
        # Display sample recent blocks
        recent = audit_ledger.get_recent_entries(limit=5)
        if recent:
            print("\n📋 Recent Chained Blocks (Most Recent First):")
            print("-" * 70)
            for b in recent:
                print(f"Block #{b.id:<4} | {b.iso_time[:19]} | {b.agent:<26} | {b.event_type}")
                print(f"            Prev Hash:  {b.prev_hash[:20]}...")
                print(f"            Block Hash: {b.block_hash[:20]}...")
                print("-" * 70)
        sys.exit(0)
    else:
        print("❌ INTEGRITY COMPROMISED: TAMPER DETECTED!")
        print(f"   Tampered Block ID:  {verification.get('tampered_block_id')}")
        print(f"   Diagnosis:          {verification['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
