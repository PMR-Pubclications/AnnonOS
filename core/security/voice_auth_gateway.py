#!/usr/bin/env python3
"""
/opt/annonos/core/security/voice_auth_gateway.py
AnnonOS Voice-Activated Accessibility Authentication & Trust-Shell Override Gateway.
Provides hands-free voice passphrase verification for blind users, coupled with 
instant hardware-rooted remote override capabilities from the primary Trust-Shell node.
"""

import sys
import hmac
import hashlib
import time
import logging
from typing import Optional

# Ensure access to ledger
sys.path.append("/opt/annonos/core/chain_of_custody")
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [VoiceAuthGateway]: %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceAuthGateway:
    def __init__(self):
        self.ledger = MerkleLedger()
        # Authorized voice biometric hash signature (stubbed for secure vector matching)
        self.authorized_voice_hash = hashlib.sha256(b"ANNONOS_CIVILIAN_SECURE_PASSPHRASE_2026").hexdigest()
        self.trust_shell_override_active = False

    def check_trust_shell_remote_override(self) -> bool:
        """
        Polls the secure Trust-Shell interface to check if the primary tactical operator 
        has issued a remote unlock override for the user.
        """
        # In live deployment, this checks an encrypted IPC socket or hardware-backed flag from Trust-Shell
        # For simulation, we check our internal state register
        return self.trust_shell_override_active

    def trigger_remote_override_from_trust_shell(self, authorization_token: str) -> bool:
        """Allows the Trust-Shell owner to instantly grant access, bypassing civilian input."""
        expected_token = hmac.new(
            b"TRUST_SHELL_MASTER_KEY_2026", 
            b"REMOTE_OVERRIDE_AUTHORIZE", 
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(authorization_token, expected_token):
            self.trust_shell_override_active = True
            logger.info("TRUST-SHELL OVERRIDE ENGAGED: Remote operator has authorized operating system access.")
            self.ledger.append_record("TRUST_SHELL_REMOTE_UNLOCK", {"status": "AUTHORIZED_BY_OPERATOR"})
            return True
        else:
            logger.warning("Invalid Trust-Shell override token rejected.")
            return False

    def authenticate_via_voice(self, spoken_passphrase: str) -> bool:
        """
        Processes voice-to-text input from a blind user, verifying the secure passphrase 
        or checking for an active Trust-Shell override.
        """
        logger.info("Processing voice-activated authentication request...")

        # 1. Check if Trust-Shell operator has already overridden the lock
        if self.check_trust_shell_remote_override():
            logger.info("ACCESS GRANTED: Trust-Shell remote override active.")
            return True

        # 2. Verify spoken passphrase cryptographically
        spoken_hash = hashlib.sha256(spoken_passphrase.strip().encode('utf-8')).hexdigest()

        if hmac.compare_digest(spoken_hash, self.authorized_voice_hash):
            logger.info("ACCESS GRANTED: Civilian voice passphrase verified successfully.")
            self.ledger.append_record("VOICE_AUTH_SUCCESS", {"method": "PASSPHRASE_MATCH"})
            return True
        else:
            logger.critical("ACCESS DENIED: Voice passphrase mismatch or unauthorized voice signature.")
            self.ledger.append_record("VOICE_AUTH_FAILURE", {"method": "UNAUTHORIZED"})
            return False

if __name__ == "__main__":
    gateway = VoiceAuthGateway()
    
    # Test 1: Failed civilian voice attempt without override
    gateway.authenticate_via_voice("incorrect password phrase")
    
    # Test 2: Successful civilian voice passphrase
    gateway.authenticate_via_voice("ANNONOS_CIVILIAN_SECURE_PASSPHRASE_2026")
    
    # Test 3: Trust-Shell Operator Remote Override
    valid_token = hmac.new(b"TRUST_SHELL_MASTER_KEY_2026", b"REMOTE_OVERRIDE_AUTHORIZE", hashlib.sha256).hexdigest()
    gateway.trigger_remote_override_from_trust_shell(valid_token)
    gateway.authenticate_via_voice("any phrase now works due to override")
