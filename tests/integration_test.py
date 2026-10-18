#!/usr/bin/env python3
"""
/opt/annonos/tests/integration_test.py
AnnonOS End-to-End System Integration Test Suite.
Verifies cross-subsystem communication, cryptographic handshakes, step GPS navigation, 
immutable ledger logging, and secure firmware verification in a unified test run.
"""

import os
import sys
import hmac
import hashlib
import zipfile
import logging

# Add AnnonOS core paths
sys.path.append("/opt/annonos/core/kernel")
sys.path.append("/opt/annonos/core/chain_of_custody")
sys.path.append("/opt/annonos/core/security")
sys.path.append("/opt/annonos/core/ai")
sys.path.append("/opt/annonos/core/navigation")

from merkle_builder import MerkleLedger
from secure_ipc_bridge import AnnonOSSecureIPCBridge
from handshake_receiver import AnnonOSHandshakeReceiver
from step_gps_navigator import StepGPSNavigator
from native_ai_assistant import AnnonOSNativeAI
from ota_firmware_updater import AnnonOSOTAUpdater

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AnnonOS-Test]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSIntegrationTester:
    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 5

    def run_all_tests(self) -> None:
        logger.info("==================================================")
        logger.info("STARTING ANNONOS SYSTEM INTEGRATION TEST SUITE")
        logger.info("==================================================")

        self.test_1_merkle_ledger()
        self.test_2_secure_ipc_handshake()
        self.test_3_step_gps_navigation()
        self.test_4_native_ai_voice_routing()
        self.test_5_ota_firmware_verification()

        logger.info("==================================================")
        logger.info(f"TEST SUITE COMPLETE: {self.passed_tests}/{self.total_tests} TESTS PASSED.")
        logger.info("==================================================")

    def test_1_merkle_ledger(self) -> None:
        """Test 1: Verify immutable Merkle chain audit logging."""
        logger.info("[Test 1/5] Testing Merkle Ledger Chain-of-Custody...")
        try:
            ledger = MerkleLedger()
            ledger.append_record("INTEGRATION_TEST", {"status": "TEST_RUNNING"})
            logger.info("-> Merkle Ledger successfully appended test record.")
            self.passed_tests += 1
        except Exception as e:
            logger.error(f"-> Test 1 Failed: {e}")

    def test_2_secure_ipc_handshake(self) -> None:
        """Test 2: Verify mutual IPC authentication between OS and Trust-Main/Shell."""
        logger.info("[Test 2/5] Testing Secure IPC & Handshake Receiver...")
        try:
            receiver = AnnonOSHandshakeReceiver()
            mock_token = hmac.new(
                b"ANNONOS_TRUST_MAIN_ROOT_SECRET_2026", 
                b"TestModule:PMR-PUBLICATIONS-ROOT", 
                hashlib.sha256
            ).hexdigest()
            
            authorized = receiver.receive_and_verify_handshake(
                module_name="TestModule",
                publisher_id="PMR-PUBLICATIONS-ROOT",
                client_token=mock_token
            )
            assert authorized, "Handshake should have been authorized."
            logger.info("-> Secure IPC handshake verified successfully.")
            self.passed_tests += 1
        except Exception as e:
            logger.error(f"-> Test 2 Failed: {e}")

    def test_3_step_gps_navigation(self) -> None:
        """Test 3: Verify geospatial coordinate to step-count translation."""
        logger.info("[Test 3/5] Testing Step-Based GPS Navigation for Blind Operators...")
        try:
            navigator = StepGPSNavigator(average_stride_length_meters=0.75)
            # Vancouver, WA coordinates simulation
            navigator.update_position(lat=45.6387, lon=-122.6615, heading_deg=0.0)
            instruction = navigator.get_tactical_step_guidance(dest_lat=45.6400, dest_lon=-122.6600)
            
            assert "steps" in instruction.lower(), "Instruction should specify step count."
            logger.info(f"-> GPS Navigation Instruction Generated: '{instruction}'")
            self.passed_tests += 1
        except Exception as e:
            logger.error(f"-> Test 3 Failed: {e}")

    def test_4_native_ai_voice_routing(self) -> None:
        """Test 4: Verify native AI voice command processing."""
        logger.info("[Test 4/5] Testing Native AI Assistant Dialogue Bridge...")
        try:
            ai = AnnonOSNativeAI()
            response = ai.process_voice_command("What is the system status?")
            assert len(response) > 0, "AI assistant must return a verbal response string."
            logger.info(f"-> AI Assistant Response: '{response}'")
            self.passed_tests += 1
        except Exception as e:
            logger.error(f"-> Test 4 Failed: {e}")

    def test_5_ota_firmware_verification(self) -> None:
        """Test 5: Verify cryptographic OTA package signature checking."""
        logger.info("[Test 5/5] Testing Secure OTA Firmware Update Verification...")
        try:
            updater = AnnonOSOTAUpdater()
            test_fw = "/tmp/test_firmware.zip"
            
            # Create valid signed test package
            with zipfile.ZipFile(test_fw, 'w') as zf:
                payload = f"test_firmware.zip:PMR-PUBLICATIONS-ROOT".encode('utf-8')
                sig = hmac.new(b"ANNONOS_TRUST_MAIN_ROOT_SECRET_2026", payload, hashlib.sha256).hexdigest()
                zf.writestr("META-INF/firmware_signature.sig", sig)
            
            success = updater.verify_and_apply_update(test_fw)
            assert success, "OTA update with valid signature should pass."
            logger.info("-> OTA firmware signature verification passed.")
            self.passed_tests += 1
        except Exception as e:
            logger.error(f"-> Test 5 Failed: {e}")

if __name__ == "__main__":
    tester = AnnonOSIntegrationTester()
    tester.run_all_tests()
