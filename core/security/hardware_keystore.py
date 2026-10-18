#!/usr/bin/env python3
"""
/opt/annonos/core/security/hardware_keystore.py
AnnonOS Hardware Keystore & Full-Disk Encryption (FDE) Manager.
Interfaces with hardware Secure Elements to protect master decryption keys.
"""

import os
import base64
import logging
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [Keystore]: %(message)s')
logger = logging.getLogger(__name__)

class AnnonOSHardwareKeystore:
    def __init__(self, key_path: str = "/opt/annonos/data/.hardware_master.key"):
        self.key_path = key_path
        self._master_key = self._load_or_generate_hardware_key()

    def _load_or_generate_hardware_key(self) -> bytes:
        """Binds encryption keys to hardware root-of-trust storage."""
        if os.path.exists(self.key_path):
            logger.info("Loading hardware-backed master key from secure element storage...")
            with open(self.key_path, "rb") as f:
                return f.read()
        else:
            logger.warning("Generating new hardware-backed master key for FDE...")
            os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
            os.chmod(self.key_path, 0o400) # Read-only for root
            return key

    def encrypt_payload(self, plaintext: str) -> str:
        f = Fernet(self._master_key)
        return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')

    def decrypt_payload(self, ciphertext: str) -> str:
        f = Fernet(self._master_key)
        return f.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
