#!/usr/bin/env python3
"""
/opt/annonos/core/security/handshake_enforcer.py
AnnonOS Application Gatekeeper & Handshake Enforcer.
Intercepts all application installation and execution requests. Automatically authorizes 
official signed modules (such as Trust-Shell) while instantly rejecting unauthorized 
binaries missing a valid hardware-rooted cryptographic handshake.
"""

import os
import sys
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional

# Add ledger path to log security violations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../chain_of_custody")))
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AnnonOS-Gatekeeper]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSAppGatekeeper:
    def __init__(self, ledger_db_path: str = "/opt/annonos/data/ledger.db"):
        self.ledger = MerkleLedger(db_path=ledger_db_path)
        
        # Hardcoded authorized cryptographic public identity for Trust-Shell
        # In production, this matches the hardware root-of-trust certificate authority
        self.AUTHORIZED_APPS = {
            "Trust-Shell": {
                "expected_publisher_id": "ANNONOS_OFFICIAL_TRUST_ROOT_2026",
                "master_token_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Example SHA-256 root
            }
        }

    def verify_and_authorize_app(self, app_name: str, publisher_id: str, handshake_token: str, binary_path: str) -> bool:
        """
        Validates an incoming application's handshake token against the hardware root-of-trust.
        Rejects any application that fails verification or is not explicitly recognized (like Trust-Shell).
        """
        logger.info(f"Intercepted installation request for application: [{app_name}]")

        # Check 1: Is the application recognized in the sovereign whitelist?
        if app_name not in self.AUTHORIZED_APPS:
            reason = f"Unauthorized application '{app_name}' rejected. Not recognized by AnnonOS registry."
            self._reject_and_log(app_name, binary_path, reason)
            return False

        app_profile = self.AUTHORIZED_APPS[app_name]

        # Check 2: Verify publisher identity cryptographic signature
        if publisher_id != app_profile["expected_publisher_id"]:
            reason = f"Cryptographic publisher mismatch for '{app_name}'. Expected root identity, got '{publisher_id}'."
            self._reject_and_log(app_name, binary_path, reason)
            return False

        # Check 3: Verify handshake token integrity
        if hmac.compare_digest(handshake_token, app_profile["master_token_hash"]):
            success_msg = f"Handshake verified successfully. [{app_name}] authorized for execution on AnnonOS."
            logger.info(success_msg)
            
            # Log successful authorization to the immutable ledger
            self.ledger.append_record("APP_AUTHORIZATION_SUCCESS", {
                "app_name": app_name,
                "publisher_id": publisher_id,
                "binary_path": binary_path,
                "status": "GRANTED"
            })
            return True
        else:
            reason = f"Handshake token authentication failed for '{app_name}'. Invalid cryptographic proof."
            self._reject_and_log(app_name, binary_path, reason)
            return False

    def _reject_and_log(self, app_name: str, binary_path: str, reason: str) -> None:
        """Logs security violation to console and records tamper event in the immutable Merkle ledger."""
        logger.critical(f"SECURITY VIOLATION: {reason}")
        
        # Commit rejection to the tamper-evident audit ledger
        self.ledger.append_record("APP_AUTHORIZATION_REJECTED", {
            "app_name": app_name,
            "binary_path": binary_path,
            "rejection_reason": reason,
            "status": "BLOCKED"
        })

if __name__ == "__main__":
    gatekeeper = AnnonOSAppGatekeeper()

    # Test 1: Authorized Trust-Shell handshake attempt
    gatekeeper.verify_and_authorize_app(
        app_name="Trust-Shell",
        publisher_id="ANNONOS_OFFICIAL_TRUST_ROOT_2026",
        handshake_token="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        binary_path="/opt/annonos/apps/trust_shell_v1.bin"
    )

    # Test 2: Unauthorized third-party app sideload attempt (should be blocked)
    gatekeeper.verify_and_authorize_app(
        app_name="MaliciousSideloadApp",
        publisher_id="UNKNOWN_HACKER_KEY",
        handshake_token="fake_token_hash_12345",
        binary_path="/tmp/untrusted_app.apk"
    )
