#!/usr/bin/env python3
"""
/opt/annonos/core/chain_of_custody/merkle_builder.py
Merkle-Tree Local Ledger & Chain-of-Custody Engine for AnnonOS.
Cryptographically hashes and appends forensic evidence, sensor streams, 
and motor telemetry data into an immutable, tamper-evident hash chain.
"""

import os
import hashlib
import json
import logging
import sqlite3
import time
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [MerkleLedger]: %(message)s'
)
logger = logging.getLogger(__name__)

class MerkleLedger:
    def __init__(self, db_path: str = "/opt/annonos/data/ledger.db"):
        self.db_path = db_path
        self._ensure_storage_directory()
        self._init_db()

    def _ensure_storage_directory(self) -> None:
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _init_db(self) -> None:
        """Initializes the append-only cryptographic SQLite ledger."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledger_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                payload TEXT,
                previous_hash TEXT,
                current_hash TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _get_latest_hash(self) -> str:
        """Retrieves the hash of the most recent block to maintain the chain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT current_hash FROM ledger_blocks ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "0" * 64  # Genesis hash

    def append_record(self, record_type: str, data: Dict[str, Any]) -> str:
        """
        Appends a new record (including motor telemetry, sensor anomalies, or forensic logs)
        into the Merkle hash chain.
        """
        timestamp = time.time()
        previous_hash = self._get_latest_hash()

        payload = {
            "timestamp": timestamp,
            "type": record_type,
            "data": data
        }
        payload_str = json.dumps(payload, sort_keys=True)

        # Compute cryptographic hash linking previous block with current payload
        hasher = hashlib.sha256()
        hasher.update((previous_hash + payload_str).encode('utf-8'))
        current_hash = hasher.hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ledger_blocks (timestamp, payload, previous_hash, current_hash)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, payload_str, previous_hash, current_hash))
        conn.commit()
        conn.close()

        logger.info(f"Immutable Record Appended [{record_type}] -> Hash: {current_hash[:16]}...")
        return current_hash

    def verify_chain_integrity(self) -> bool:
        """Audits the entire local ledger to ensure zero tampering or corruption."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, timestamp, payload, previous_hash, current_hash FROM ledger_blocks ORDER BY id ASC')
        rows = cursor.fetchall()
        conn.close()

        expected_previous_hash = "0" * 64
        for row in rows:
            block_id, timestamp, payload_str, prev_hash, curr_hash = row
            
            if prev_hash != expected_previous_hash:
                logger.critical(f"FATAL: Chain-of-custody broken at block {block_id} (Previous hash mismatch)!")
                return False

            hasher = hashlib.sha256()
            hasher.update((prev_hash + payload_str).encode('utf-8'))
            recalculated_hash = hasher.hexdigest()

            if recalculated_hash != curr_hash:
                logger.critical(f"FATAL: Data corruption or tampering detected at block {block_id}!")
                return False

            expected_previous_hash = curr_hash

        logger.info("Chain-of-custody audit complete. Ledger integrity is 100% verified.")
        return True

if __name__ == "__main__":
    ledger = MerkleLedger()
    
    # Example: Appending motor telemetry and actuator data into the ledger
    motor_telemetry = {
        "motor_id": "ACTUATOR_DRIVE_01",
        "rpm": 3450.2,
        "torque_nm": 42.5,
        "temperature_celsius": 68.4,
        "status": "OPTIMAL"
    }
    
    ledger.append_record("MOTOR_TELEMETRY", motor_telemetry)
    ledger.verify_chain_integrity()
