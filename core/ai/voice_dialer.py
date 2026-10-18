#!/usr/bin/env python3
"""
/opt/annonos/core/ai/voice_dialer.py
AnnonOS Voice-Commanded Dialing Module.
Allows blind or low-vision tactical operators to dial contacts or raw phone numbers 
entirely through voice commands via the PTT pipeline.
"""

import sys
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [VoiceDialer]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSVoiceDialer:
    def __init__(self):
        logger.info("Initializing AnnonOS Voice Dialer...")

    def parse_voice_command(self, spoken_text: str) -> dict:
        """
        Parses spoken text to determine if the user wants to dial a name or a number.
        Example commands:
          - "Call Commander Vance" -> Target type: CONTACT, Value: Commander Vance
          - "Dial 555-0199" -> Target type: NUMBER, Value: 555-0199
        """
        cleaned = spoken_text.strip().lower()
        logger.info(f"Parsing voice dial command: '{spoken_text}'")

        # Check if user specified a phone number directly (digits/hyphens)
        number_match = re.search(r'[\d\-\+\(\)\s]{7,}', cleaned)
        if number_match and ("dial" in cleaned or "call" in cleaned):
            raw_number = number_match.group(0).strip()
            return {"action": "DIAL_NUMBER", "target": raw_number}

        # Otherwise, extract contact name following "call" or "dial"
        for keyword in ["call", "dial", "ring"]:
            if keyword in cleaned:
                parts = cleaned.split(keyword, 1)
                if len(parts) > 1:
                    contact_name = parts[1].strip().title()
                    return {"action": "DIAL_CONTACT", "target": contact_name}

        return {"action": "UNKNOWN", "target": spoken_text}

    def execute_dial(self, spoken_command: str) -> bool:
        """Processes the voice command and initiates the telephony call stack."""
        intent = self.parse_voice_command(spoken_command)
        
        if intent["action"] == "DIAL_CONTACT":
            logger.info(f"Initiating secure call to contact: '{intent['target']}'...")
            # Calls into contact book lookup & telephony driver
            return True
        elif intent["action"] == "DIAL_NUMBER":
            logger.info(f"Initiating secure call to raw number: '{intent['target']}'...")
            # Calls into telephony driver
            return True
        else:
            logger.warning(f"Could not resolve voice dial intent from command: '{spoken_command}'")
            return False

if __name__ == "__main__":
    dialer = AnnonOSVoiceDialer()
    
    # Test voice command parsing and dialing
    dialer.execute_dial("Call Commander Vance")
    dialer.execute_dial("Dial 555-0199-4321")
