#!/usr/bin/env python3
"""
/opt/annonos/core/accessibility/voice_command_registry.py
AnnonOS Voice Command Registry & Audible Help System.
Provides a centralized index of all voice-activated commands for blind operators,
invoked via the 'anon list commands' trigger phrase.
"""

import sys
import logging
from typing import Dict, List

# Ensure access to ledger
sys.path.append("/opt/annonos/core/chain_of_custody")
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [VoiceRegistry]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonVoiceCommandRegistry:
    def __init__(self):
        self.ledger = MerkleLedger()
        self.command_directory = {
            "Navigation & Transit": [
                {"trigger": "anon plan route [destination]", "action": "Calculates walking steps, bus routes, and travel time."},
                {"trigger": "anon next step", "action": "Speaks the next directional instruction and step count."},
                {"trigger": "anon repeat step", "action": "Repeats the current navigation guidance cue."},
                {"trigger": "anon check distance", "action": "Announces remaining distance and estimated time to destination."}
            ],
            "Security & Authentication": [
                {"trigger": "anon verify voice [passphrase]", "action": "Authenticates user identity via secure voice biometrics."},
                {"trigger": "anon request trust-shell override", "action": "Signals the primary operator for remote unlock authorization."},
                {"trigger": "anon check security status", "action": "Reports active cipher suite and encryption envelope status."}
            ],
            "System & Haptic Feedback": [
                {"trigger": "anon battery status", "action": "Announces current battery level and thermal health metrics."},
                {"trigger": "anon test haptics [pattern]", "action": "Plays silent haptic vibration codes (e.g., left, right, hazard)."},
                {"trigger": "anon repeat status", "action": "Reads out system telemetry and active connectivity state."}
            ],
            "Emergency & Crisis": [
                {"trigger": "anon broadcast distress", "action": "Transmits encrypted silent RF or acoustic burst beacon coordinates."},
                {"trigger": "anon emergency wipe", "action": "Triggers hardware key shredding and ledger purge (requires confirmation)."}
            ]
        }

    def list_commands_audible(self, category: str = "all") -> str:
        """
        Compiles and formats a speech-optimized script of available voice commands 
        for text-to-speech (TTS) audio output.
        """
        logger.info(f"Generating audible voice command listing for category: [{category}]...")

        script_lines = ["AnnonOS Voice Command Directory. Here are your available commands:"]

        categories_to_process = self.command_directory.keys() if category == "all" else [category]

        for cat in categories_to_process:
            if cat in self.command_directory:
                script_lines.append(f"Category: {cat}.")
                for cmd in self.command_directory[cat]:
                    script_lines.append(f"Say, '{cmd['trigger']}', to {cmd['action']}")

        full_script = " ".join(script_lines)

        # Log command listing request to Merkle ledger
        self.ledger.append_record(
            "VOICE_COMMANDS_LISTED",
            {"category_queried": category, "status": "SUCCESS"}
        )

        return full_script

    def execute_command_utterance(self, utterance: str) -> str:
        """Parses an incoming voice command utterance and routes it to the correct subsystem."""
        clean_utterance = utterance.strip().lower()

        if "anon list commands" in clean_utterance:
            return self.list_commands_audible("all")
        elif "anon next step" in clean_utterance:
            return "Next navigation waypoint is three hundred meters ahead. Turn left at the intersection."
        elif "anon battery status" in clean_utterance:
            return "System power nominal at eighty-two percent. Thermal levels stable."
        else:
            return "Command not recognized. Say, 'anon list commands', for a complete directory."

if __name__ == "__main__":
    registry = AnnonVoiceCommandRegistry()
    
    # Test invoking 'anon list commands'
    audible_help = registry.execute_command_utterance("anon list commands")
    print("\n--- AUDIBLE COMMAND DIRECTORY ---")
    print(audible_help)
