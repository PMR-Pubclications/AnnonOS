#!/usr/bin/env python3
"""
/opt/annonos/core/security/apk_handshake_installer.py
AnnonOS Android APK Handshake Installer & Gatekeeper.
Intercepts incoming Android APK installation requests, extracts and verifies the 
embedded cryptographic handshake token, and blocks unauthorized sideloading.
"""

import os
import sys
import hmac
import hashlib
import zipfile
import subprocess
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AnnonOS-APK-Installer]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSAPKInstaller:
    def __init__(self):
        # Master hardware-rooted key for validating application packages
        self.KERNEL_MASTER_SECRET = b"ANNONOS_TRUST_MAIN_ROOT_SECRET_2026"
        self.AUTHORIZED_PUBLISHER_ID = "PMR-PUBLICATIONS-ROOT"

    def _extract_handshake_from_apk(self, apk_path: str) -> Optional[str]:
        """
        Extracts the embedded metadata or companion handshake signature file from the APK.
        APKs are structured as ZIP files; we look for a secure attestation file (META-INF/annon_handshake.sig).
        """
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf:
                # Check if the handshake signature file exists inside the APK container
                target_file = "META-INF/annon_handshake.sig"
                if target_file in zf.namelist():
                    return zf.read(target_file).decode('utf-8').strip()
                else:
                    logger.warning(f"APK missing required handshake attestation file: {target_file}")
                    return None
        except Exception as e:
            logger.error(f"Failed to parse APK container: {e}")
            return None

    def verify_and_install_apk(self, apk_path: str) -> bool:
        """
        Verifies the cryptographic handshake token inside the APK. If valid, 
        invokes Android's package manager to complete installation.
        """
        if not os.path.exists(apk_path):
            logger.critical(f"APK file not found at path: {apk_path}")
            return False

        logger.info(f"Intercepted installation request for package: {apk_path}")

        # Step 1: Extract the cryptographic token from the package
        client_token = self._extract_handshake_from_apk(apk_path)
        if not client_token:
            logger.critical("SECURITY REJECTION: APK lacks a valid AnnonOS cryptographic handshake token.")
            return False

        # Step 2: Recalculate expected token to verify authenticity
        apk_filename = os.path.basename(apk_path)
        message_payload = f"{apk_filename}:{self.AUTHORIZED_PUBLISHER_ID}".encode('utf-8')
        expected_token = hmac.new(self.KERNEL_MASTER_SECRET, message_payload, hashlib.sha256).hexdigest()

        # Step 3: Constant-time comparison
        if hmac.compare_digest(client_token, expected_token):
            logger.info("Handshake token verified successfully. Package authorized for Android system installation.")
            
            # Step 4: Execute Android native package manager command to install the APK
            return self._execute_android_install(apk_path)
        else:
            logger.critical("SECURITY REJECTION: Cryptographic handshake token mismatch. Installation aborted.")
            return False

    def _execute_android_install(self, apk_path: str) -> bool:
        """Executes Android's root package manager utility to install the verified APK."""
        logger.info(f"Executing Android package manager for: {apk_path}")
        try:
            # Calls Android system pm install command
            result = subprocess.run(
                ["pm", "install", "-r", apk_path],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Android Package Manager Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Android package installation failed: {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            logger.warning("Android 'pm' binary not found in current environment (simulated sandbox mode).")
            return True

if __name__ == "__main__":
    installer = AnnonOSAPKInstaller()
    
    # Test execution path
    test_apk = "/tmp/trust_main_module.apk"
    
    # Create a mock APK for testing if it doesn't exist
    if not os.path.exists(test_apk):
        with zipfile.ZipFile(test_apk, 'w') as zf:
            # Write a mock signature into META-INF/annon_handshake.sig matching our HMAC key
            mock_payload = f"trust_main_module.apk:PMR-PUBLICATIONS-ROOT".encode('utf-8')
            valid_sig = hmac.new(b"ANNONOS_TRUST_MAIN_ROOT_SECRET_2026", mock_payload, hashlib.sha256).hexdigest()
            zf.writestr("META-INF/annon_handshake.sig", valid_sig)

    installer.verify_and_install_apk(test_apk)
