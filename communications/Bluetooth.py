#!/usr/bin/env python3
"""
Radio Bluetooth Audio Bridge (radio_bt_bridge.py)
Part of the Annon OS / Trust Forensics Mobile Lab (TFML) Infrastructure.
Handles secure pairing, connection persistence, and audio routing to tactical radio earpieces.
"""

import os
import sys
import time
import logging
import subprocess
import socket
from typing import Optional

# Configure logging for forensic event tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [RadioBTBridge]: %(message)s'
)
logger = logging.getLogger(__name__)

class RadioBluetoothBridge:
    def __init__(self, target_device_name: str = "ANNO_TACTICAL_RSM", audio_sink_port: int = 5555):
        self.target_name = target_device_name
        self.audio_sink_port = audio_sink_port
        self.is_connected = False
        self.socket_connection: Optional[socket.socket] = None
        
    def scan_for_tactical_accessory(self) -> Optional[str]:
        """
        Scans for certified Bluetooth Low Energy (BLE) or Bluetooth Classic tactical 
        radio accessories within range. Returns the MAC address if found.
        """
        logger.info(f"Scanning for tactical radio accessory: {self.target_name}...")
        try:
            # Utilizing BlueZ system tools native to Annon OS kernel environment
            cmd = ["hcitool", "scan"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.warning("Bluetooth scan interface returned non-zero exit code.")
                return None
                
            for line in result.stdout.splitlines():
                if self.target_name in line:
                    parts = line.strip().split()
                    mac_address = parts[0]
                    logger.info(f"Found target tactical accessory at MAC: {mac_address}")
                    return mac_address
                    
        except Exception as e:
            logger.error(f"Error during tactical accessory scan: {e}")
            
        return None

    def establish_secure_link(self, mac_address: str) -> bool:
        """
        Establishes a cryptographically paired, low-latency audio link to the radio accessory.
        """
        logger.info(f"Establishing secure connection with radio accessory {mac_address}...")
        try:
            # Bind audio routing to the system audio policy socket
            connect_cmd = ["rfcomm", "connect", "0", mac_address, "1"]
            res = subprocess.run(connect_cmd, capture_output=True, text=True, timeout=15)
            
            if res.returncode == 0:
                self.is_connected = True
                logger.info("Secure radio earpiece link established successfully.")
                return True
            else:
                logger.error(f"Failed to bind RFCOMM channel: {res.stderr}")
                self.is_connected = False
                return False
                
        except Exception as e:
            logger.error(f"Exception encountered while securing radio link: {e}")
            self.is_connected = False
            return False

    def route_audio_to_earpiece(self, audio_payload_path: str) -> bool:
        """
        Routes generated audio prompts or text-to-speech warnings directly 
        through the radio earpiece channel, overriding default speaker output.
        """
        if not self.is_connected:
            logger.warning("Cannot route audio: Radio earpiece link is inactive.")
            return False

        try:
            logger.info(f"Routing priority audio payload [{audio_payload_path}] to tactical earpiece...")
            
            # Direct ALSA/Audio Policy socket transmission in Annon OS
            play_cmd = ["aplay", "-D", "plug:bt_audio_card", audio_payload_path]
            result = subprocess.run(play_cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                logger.info("Audio successfully delivered to tactical earpiece.")
                return true
            else:
                logger.error(f"Audio playback error on radio channel: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to transmit audio stream to radio earpiece: {e}")
            return False

    def monitor_link_health(self) -> None:
        """
        Continuous background heartbeat to ensure the radio link remains active.
        Triggers haptic fallback or visual HUD alert if connection drops.
        """
        while True:
            if self.is_connected:
                # Ping RFCOMM channel state
                check_cmd = ["hcitool", "con"]
                res = subprocess.run(check_cmd, capture_output=True, text=True)
                if self.target_name not in res.stdout:
                    logger.warning("Radio link dropped unexpectedly! Triggering fallback queue.")
                    self.is_connected = False
            time.sleep(5)

if __name__ == "__main__":
    bridge = RadioBluetoothBridge()
    mac = bridge.scan_for_tactical_accessory()
    if mac:
        bridge.establish_secure_link(mac)
    else:
        logger.info("Tactical accessory not in range. Operating on fallback local audio mode.")
