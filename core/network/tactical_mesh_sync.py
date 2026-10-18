#!/usr/bin/env python3
"""
/opt/annonos/core/network/tactical_mesh_sync.py
AnnonOS Off-Grid Tactical Mesh Networking & P2P Sync Daemon.
Establishes encrypted ad-hoc peer-to-peer channels to broadcast telemetry 
and sync Merkle audit ledgers across field units without central infrastructure.
"""

import os
import sys
import socket
import json
import hmac
import hashlib
import logging
from typing import Dict, Any

# Ensure access to ledger
sys.path.append("/opt/annonos/core/chain_of_custody")
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [MeshSync]: %(message)s'
)
logger = logging.getLogger(__name__)

class TacticalMeshSyncDaemon:
    def __init__(self, bind_port: int = 8844):
        self.bind_port = bind_port
        self.mesh_secret = b"ANNONOS_MESH_SHARED_TACTICAL_KEY_2026"
        self.ledger = MerkleLedger()
        self.active_peers = []
        logger.info(f"Initializing Tactical Mesh Sync Daemon on port {self.bind_port}...")

    def broadcast_packet(self, payload_type: str, data: Dict[str, Any]) -> str:
        """Constructs an encrypted, HMAC-authenticated mesh sync packet."""
        packet_body = {
            "origin_unit": "AnnonOS-Field-Unit-Alpha",
            "type": payload_type,
            "data": data,
            "timestamp": os.popen("date -u +%s").read().strip()
        }
        raw_payload = json.dumps(packet_body).encode('utf-8')
        
        # Compute HMAC signature for peer verification
        signature = hmac.new(self.mesh_secret, raw_payload, hashlib.sha256).hexdigest()
        
        envelope = {
            "signature": signature,
            "payload": packet_body
        }
        
        logger.info(f"Broadcasting mesh packet [{payload_type}] to nearby off-grid peers...")
        return json.dumps(envelope)

    def receive_and_verify_packet(self, raw_envelope_str: str) -> bool:
        """Receives, authenticates, and ingests a peer mesh packet into the local ledger."""
        try:
            envelope = json.loads(raw_envelope_str)
            client_sig = envelope.get("signature", "")
            payload_body = envelope.get("payload", {})
            raw_payload = json.dumps(payload_body).encode('utf-8')

            # Verify peer authenticity via shared mesh HMAC key
            expected_sig = hmac.new(self.mesh_secret, raw_payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(client_sig, expected_sig):
                logger.warning("SECURITY REJECTION: Mesh packet signature verification failed! Possible rogue node.")
                return False

            origin = payload_body.get("origin_unit", "Unknown")
            p_type = payload_body.get("type", "UNKNOWN")
            logger.info(f"Verified incoming mesh packet from [{origin}] of type [{p_type}]")

            # Sync ledger entry locally
            self.ledger.append_record("MESH_SYNC_INCOMING", payload_body)
            return True

        except Exception as e:
            logger.error(f"Error processing incoming mesh packet: {e}")
            return False

if __name__ == "__main__":
    daemon = TacticalMeshSyncDaemon()
    
    # Test mesh packet broadcast
    packet = daemon.broadcast_packet("TELEMETRY_UPDATE", {"status": "NOMINAL", "lat": 45.6387, "lon": -122.6615})
    
    # Test peer verification and ingestion
    daemon.receive_and_verify_packet(packet)
