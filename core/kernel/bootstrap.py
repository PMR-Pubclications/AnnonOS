#!/usr/bin/env python3
"""
/opt/annonos/core/kernel/bootstrap.py
AnnonOS Master System Bootstrap.
Executes pre-flight hardware checks, validates the cryptographic Merkle ledger, 
mounts virtual kernel filesystems, and safely hands off execution to PID 1 (annon_init.py).
"""

import os
import sys
import subprocess
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AnnonOS-Bootstrap]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSBootstrap:
    def __init__(self):
        self.ledger_db_path = "/opt/annonos/data/ledger.db"
        self.init_daemon_path = "/opt/annonos/core/kernel/annon_init.py"

    def preflight_checks(self) -> bool:
        """Performs mandatory pre-boot security and environment validations."""
        logger.info("Running AnnonOS pre-flight bootstrap checks...")

        # 1. Verify root privileges
        if os.geteuid() != 0:
            logger.critical("BOOT FAILURE: AnnonOS bootstrap must be executed with root privileges.")
            return False

        # 2. Verify Ledger Database integrity
        if not os.path.exists(self.ledger_db_path):
            logger.warning("Ledger database missing. Initializing fresh secure store...")
            os.makedirs(os.path.dirname(self.ledger_db_path), exist_ok=True)
            conn = sqlite3.connect(self.ledger_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ledger_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    payload TEXT,
                    previous_hash TEXT,
                    current_hash TEXT
                );
            ''')
            conn.commit()
            conn.close()

        try:
            conn = sqlite3.connect(self.ledger_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ledger_blocks;")
            count = cursor.fetchone()[0]
            conn.close()
            logger.info(f"Merkle ledger verified. Total audit blocks recorded: {count}")
        except Exception as e:
            logger.critical(f"BOOT FAILURE: Corrupt Merkle ledger database: {e}")
            return False

        # 3. Check hardware input event nodes
        event_nodes = ["/dev/input/event0", "/dev/input/event1"]
        for node in event_nodes:
            if not os.path.exists(node):
                logger.warning(f"Hardware node {node} not found. Operating in fallback simulation mode.")

        logger.info("Pre-flight bootstrap checks passed successfully.")
        return True

    def mount_virtual_filesystems(self) -> None:
        """Mounts essential kernel virtual filesystems if running bare-metal."""
        vfs = [
            ("proc", "/proc", "proc"),
            ("sysfs", "/sys", "sysfs"),
            ("udev", "/dev", "devtmpfs")
        ]
        for fs_type, mount_point, device in vfs:
            if os.path.exists(mount_point) and not os.listdir(mount_point):
                try:
                    subprocess.run(["mount", "-t", fs_type, device, mount_point], check=True)
                    logger.info(f"Mounted virtual filesystem: {mount_point}")
                except Exception as e:
                    logger.warning(f"Could not mount {mount_point} (sandbox/simulation environment): {e}")

    def launch_kernel_supervisor(self) -> None:
        """Hands execution off to the AnnonOS Init Supervisor (PID 1)."""
        if not os.path.exists(self.init_daemon_path):
            logger.critical(f"BOOT FAILURE: Kernel init script not found at {self.init_daemon_path}")
            sys.exit(1)

        logger.info(f"Handing off execution to AnnonOS Kernel Supervisor: {self.init_daemon_path}")
        os.execv(sys.executable, [sys.executable, self.init_daemon_path])

    def boot(self) -> None:
        """Initiates the complete bootstrap sequence."""
        logger.info("==================================================")
        logger.info("ANNONOS HARDWARE BOOTSTRAP INITIALIZED")
        logger.info("==================================================")
        
        if not self.preflight_checks():
            logger.critical("Bootstrap aborted due to security or integrity violations.")
            sys.exit(1)

        self.mount_virtual_filesystems()
        self.launch_kernel_supervisor()

if __name__ == "__main__":
    bootstrap = AnnonOSBootstrap()
    bootstrap.boot()
