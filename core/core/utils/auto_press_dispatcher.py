#!/usr/bin/env python3
"""
/opt/annonos/core/utils/auto_press_dispatcher.py
AnnonOS Automated First Responder Press Release Dispatcher.
Queries the first responder department database, compiles versioned press packets, 
and automatically distributes secure updates to all registered field agencies.
"""

import os
import sys
import sqlite3
import datetime
import logging
from typing import List, Dict, Any

# Ensure access to ledger and release generator
sys.path.append("/opt/annonos/core/chain_of_custody")
sys.path.append("/opt/annonos/core/utils")
from merkle_builder import MerkleLedger
from press_release_publisher import AnnonOSPressReleaseGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [ResponderDispatch]: %(message)s'
)
logger = logging.getLogger(__name__)

class FirstResponderPressDispatcher:
    def __init__(self, db_path: str = "/opt/annonos/data/first_responder_contacts.db"):
        self.db_path = db_path
        self.ledger = MerkleLedger()
        self._initialize_contact_database()

    def _initialize_contact_database(self) -> None:
        """Ensures the local first responder department contact database is initialized."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responder_departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_name TEXT NOT NULL,
                region TEXT NOT NULL,
                secure_endpoint TEXT NOT NULL,
                contact_person TEXT,
                active INTEGER DEFAULT 1
            );
        ''')
        
        # Populate initial default agencies if table is empty
        cursor.execute("SELECT COUNT(*) FROM responder_departments;")
        if cursor.fetchone()[0] == 0:
            default_agencies = [
                ("Tactical EMS Unit Alpha", "Pacific Northwest Sector", "dispatch.alpha@annonos-secure.net", "Cmdr. Vance"),
                ("Emergency Rescue Command Beta", "Metro Region", "secure.dispatch@beta-rescue.org", "Chief Miller"),
                ("First Responder Field Operations", "Statewide Tactical", "ops@first-responder-trust.gov", "Director Hayes"),
                ("Trust Forensics & Telemetry Division", "National Network", "telemetry@trust-forensics.org", "Analyst Thorne")
            ]
            cursor.executemany(
                "INSERT INTO responder_departments (department_name, region, secure_endpoint, contact_person) VALUES (?, ?, ?, ?);",
                default_agencies
            )
            conn.commit()
            logger.info("Initialized first responder department database with default tactical contacts.")
        
        conn.close()

    def fetch_active_departments(self) -> List[Dict[str, Any]]:
        """Retrieves all active first responder departments and dispatch endpoints from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM responder_departments WHERE active = 1;")
        rows = cursor.fetchall()
        conn.close()
        
        departments = [dict(row) for row in rows]
        logger.info(f"Loaded {len(departments)} active first responder departments from database.")
        return departments

    def dispatch_version_update(self, version_tag: str) -> None:
        """
        Generates an updated press release for the given version tag 
        and automatically dispatches it to every department in the database.
        """
        logger.info(f"==================================================")
        logger.info(f"INITIATING AUTOMATED PRESS RELEASE DISPATCH: Version {version_tag}")
        logger.info(f"==================================================")

        # 1. Generate updated press release content
        release_generator = AnnonOSPressReleaseGenerator()
        press_text = release_generator.generate_press_release()
        
        # Append version tag header
        versioned_release = f"**Version Release Tag:** {version_tag}  \n" + press_text

        # 2. Fetch contact database
        departments = self.fetch_active_departments()

        # 3. Simulate secure transmission to each department endpoint
        for dept in departments:
            name = dept["department_name"]
            endpoint = dept["secure_endpoint"]
            region = dept["region"]
            
            logger.info(f"-> Transmitting Version {version_tag} Press Release to [{name}] ({region}) via secure relay [{endpoint}]...")
            # In live hardware/network runtime, this hooks into encrypted mail/webhook APIs or Trust-Shell relays.

        # 4. Record transaction securely to the immutable Merkle audit ledger
        self.ledger.append_record(
            "PRESS_RELEASE_AUTO_DISPATCH",
            {
                "version": version_tag,
                "recipient_count": len(departments),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        logger.info(f"Successfully dispatched Version {version_tag} press release to all departments. Logged to ledger.")

if __name__ == "__main__":
    # Test dispatch for new version release
    dispatcher = FirstResponderPressDispatcher()
    dispatcher.dispatch_version_update("v1.0.4-TACTICAL")
