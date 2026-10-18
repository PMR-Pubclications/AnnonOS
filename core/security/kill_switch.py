#!/usr/bin/env python3
"""
/opt/annonos/core/security/kill_switch.py
AnnonOS Emergency Crypto-Shredder & Kill Switch.
Instantly wipes master encryption keys, erases the audit ledger, and powers down the device.
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [KillSwitch]: %(message)s')
logger = logging.getLogger(__name__)

class AnnonOSKillSwitch:
    def __init__(self, key_path: str = "/opt/annonos/data/.hardware_master.key", ledger_path: str = "/opt/annonos/data/ledger.db"):
        self.key_path = key_path
        self.ledger_path = ledger_path

    def execute_crypto_shred(self) -> None:
        """Executes emergency device sanitization."""
        logger.critical("==================================================")
        logger.critical("EMERGENCY KILL SWITCH TRIGGERED: CRYPTO-SHREDDING ACTIVE")
        logger.critical("==================================================")

        # 1. Overwrite and delete master hardware encryption key
        if os.path.exists(self.key_path):
            try:
                with open(self.key_path, "wb") as f:
                    f.write(os.urandom(4096)) # Random overwrite
                os.remove(self.key_path)
                logger.info("Master hardware keystore successfully shredded.")
            except Exception as e:
                logger.error(f"Error shredding keystore: {e}")

        # 2. Shred immutable audit ledger
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "wb") as f:
                    f.write(os.urandom(8192))
                os.remove(self.ledger_path)
                logger.info("Merkle audit ledger successfully wiped.")
            except Exception as e:
                logger.error(f"Error wiping ledger: {e}")

        logger.critical("Sanitization complete. Forcing hard power shutdown...")
        # In physical bare-metal deployment, this issues a kernel panic or poweroff command
        # os.system("poweroff -f")
        sys.exit(0)

if __name__ == "__main__":
    switch = AnnonOSKillSwitch()
    # switch.execute_crypto_shred()
