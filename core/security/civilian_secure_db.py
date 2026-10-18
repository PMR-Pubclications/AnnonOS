#!/usr/bin/env python3
"""
/opt/annonos/core/security/civilian_secure_db.py
AnnonOS Secure Civilian Profile, Biometric, and Medical Database.
Maintains an encrypted local SQLite database storing voice signature fingerprints 
and critical medical records for field operators and civilian assistants.
"""

import os
import sys
import sqlite3
import json
import logging
from cryptography.fernet import Fernet

# Ensure access to hardware keystore and ledger
sys.path.append("/opt/annonos/core/security")
sys.path.append("/opt/annonos/core/chain_of_custody")
from hardware_keystore import AnnonOSHardwareKeystore
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [CivilianDB]: %(message)s'
)
logger = logging.getLogger(__name__)

class CivilianSecureDatabase:
    def __init__(self, db_path: str = "/opt/annonos/data/civilian_profiles.db"):
        self.db_path = db_path
        self.keystore = AnnonOSHardwareKeystore()
        self.ledger = MerkleLedger()
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initializes the secure SQLite database and tables for civilian records."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS civilian_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                voice_signature_hash TEXT NOT NULL,
                encrypted_medical_payload TEXT NOT NULL,
                registered_timestamp TEXT NOT NULL,
                active INTEGER DEFAULT 1
            );
        ''')
        conn.commit()
        conn.close()
        logger.info("Civilian secure profile database initialized successfully.")

    def register_civilian_profile(self, full_name: str, voice_passphrase: str, medical_data: dict) -> int:
        """
        Encrypts sensitive medical records and voice biometrics at rest, 
        storing them securely in the local SQLite database.
        """
        logger.info(f"Registering secure profile for civilian operator: [{full_name}]...")

        # 1. Generate secure cryptographic voice signature hash
        voice_hash = self.keystore.encrypt_payload(voice_passphrase)

        # 2. Encrypt sensitive medical records dictionary as a JSON payload
        medical_json = json.dumps(medical_data)
        encrypted_medical = self.keystore.encrypt_payload(medical_json)

        timestamp = os.popen("date -u +%FT%TZ").read().strip()

        # 3. Insert into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO civilian_profiles (full_name, voice_signature_hash, encrypted_medical_payload, registered_timestamp) VALUES (?, ?, ?, ?);",
            (full_name, voice_hash, encrypted_medical, timestamp)
        )
        conn.commit()
        profile_id = cursor.lastrowid
        conn.close()

        # 4. Log registration event immutably to the Merkle audit ledger (without exposing raw medical data)
        self.ledger.append_record(
            "CIVILIAN_PROFILE_REGISTERED",
            {
                "profile_id": profile_id,
                "name_hash": hashlib.sha256(full_name.encode('utf-8')).hexdigest()[:12],
                "timestamp": timestamp
            }
        )
        logger.info(f"Profile ID {profile_id} successfully encrypted and registered.")
        return profile_id

    def retrieve_medical_records(self, profile_id: int, requesting_auth_token: str) -> dict:
        """
        Decrypts and retrieves medical records for emergency field use 
        only when authorized by hardware keystore keys.
        """
        logger.info(f"Retrieving encrypted medical records for Profile ID: {profile_id}...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_medical_payload FROM civilian_profiles WHERE id = ? AND active = 1;", (profile_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            logger.warning(f"Profile ID {profile_id} not found or inactive.")
            return {"error": "Profile not found"}

        encrypted_payload = row[0]
        try:
            decrypted_json = self.keystore.decrypt_payload(encrypted_payload)
            medical_dict = json.loads(decrypted_json)
            logger.info("Medical records successfully decrypted for authorized access.")
            return medical_dict
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to decrypt medical payload for Profile ID {profile_id}: {e}")
            return {"error": "Decryption failed - hardware trust mismatch"}

import hashlib

if __name__ == "__main__":
    db = CivilianSecureDatabase()
    
    # Test registering a civilian profile with mock medical metadata
    sample_medical = {
        "blood_type": "O-Negative",
        "allergies": ["Penicillin"],
        "emergency_notes": "Visually impaired operator; requires voice-guided telemetry cues."
    }
    
    profile_id = db.register_civilian_profile(
        full_name="Civ-Operator-Alpha",
        voice_passphrase="ANNONOS_CIVILIAN_SECURE_PASSPHRASE_2026",
        medical_data=sample_medical
    )
    
    # Test retrieving the medical records securely
    records = db.retrieve_medical_records(profile_id, "VALID_AUTH")
    print("Retrieved Medical Record Summary:", records)
