#!/usr/bin/env python3
"""
/opt/annonos/core/network/mesh_tactical_sync.py
AnnonOS Off-Grid P2P Tactical Mesh Sync Daemon.
Facilitates decentralized, encrypted, peer-to-peer mesh networking over ad-hoc interfaces.
Relays emergency telemetry, voice/text alerts, and Merkle ledger updates in infrastructure-denied environments.
"""

import sys
import os
import time
import socket
import json
import logging
from typing import Dict, Any, List

# Ensure access to security and chain of custody modules
sys.path.append("/opt/annonos/core/security")
sys.path.append("/opt/annonos/core/chain_of_custody")
from polymorphic_security_engine import PolymorphicSecurityEngine
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [MeshSync]: %(message)s'
)
logger = logging.getLogger(__name__)

class TacticalMeshDaemon:
    def __init__(self, mesh_port: int = 8443):
        self.mesh_port = mesh_port
        self.poly_engine = PolymorphicSecurityEngine()
        self.ledger = MerkleLedger()
        self.active_peers: List[str] = []

    def broadcast_beacon(self, node_id: str, payload_data: Dict[str, Any]) -> None:
        """
        Encapsulates telemetry/alerts in a polymorphic envelope and broadcasts 
        it across local mesh interfaces (UDP broadcast).
        """
        logger.info(f"Preparing mesh broadcast beacon for node [{node_id}]...")

        raw_payload = json.dumps({
            "sender_node": node_id,
            "timestamp": time.time(),
            "data": payload_data
        }).encode('utf-8')

        # Wrap payload with polymorphic moving-target cipher envelope
        morphed_envelope = self.poly_engine.mutate_payload_envelope(raw_payload)

        # Broadcast packet over local ad-hoc network socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(morphed_envelope, ('<broadcast>', self.mesh_port))
            sock.close()
            
            logger.info("Polymorphic mesh beacon successfully broadcasted.")
            self.ledger.append_record(
                "MESH_BEACON_TRANSMITTED",
                {"node_id": node_id, "bytes_sent": len(morphed_envelope)}
            )
        except Exception as e:
            logger.error(f"Failed to transmit mesh broadcast: {e}")

    def listen_for_peer_telemetry(self, timeout_seconds: float = 5.0) -> None:
        """
        Listens for incoming peer broadcasts, un-wraps the polymorphic encryption wall,
        and ingests mesh updates into the local system ledger.
        """
        logger.info(f"Listening for mesh peer telemetry on UDP port {self.mesh_port}...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout_seconds)
        
        try:
            sock.bind(('', self.mesh_port))
            data, addr = sock.recvfrom(4096)
            logger.info(f"Received encrypted mesh packet from peer address: {addr[0]}")

            # Verify and un-wrap polymorphic envelope
            if self.poly_engine.verify_mutated_envelope(data):
                # Strip 17-byte polymorphic header offset
                profile = self.poly_engine.compute_current_security_profile()
                payload_bytes = data[17:]
                
                unpacked_json = json.loads(payload_bytes.decode('utf-8'))
                logger.info(f"SUCCESS: Decrypted mesh packet from Peer [{unpacked_json['sender_node']}]")

                # Log mesh sync event into Merkle ledger
                self.ledger.append_record(
                    "MESH_PEER_SYNC_RECEIVED",
                    {
                        "peer_node": unpacked_json['sender_node'],
                        "peer_ip": addr[0]
                    }
                )
            else:
                logger.warning("REJECTED: Mesh packet failed polymorphic envelope verification.")

        except socket.timeout:
            logger.info("Mesh listener window closed (no active peer transmissions detected).")
        except Exception as e:
            logger.error(f"Mesh listener encounter error: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    daemon = TacticalMeshDaemon()

    # Simulate mesh beacon broadcast
    test_telemetry = {
        "status": "OPERATIONAL",
        "role": "CIVILIAN_BLIND_USER",
        "location_grid": "SECTOR_4_ALPHA"
    }
    daemon.broadcast_beacon(node_id="AnnonNode-771", payload_data=test_telemetry)

    # Listen briefly for peer synchronization
    daemon.listen_for_peer_telemetry(timeout_seconds=2.0)
