#!/usr/bin/env python3
"""
/opt/annonos/core/transparency/operator_letter_audible.py
AnnonOS Transparency Letter Audio Service.
Reads the personal letter from the blind lead engineer to the civilian operator 
aloud via the text-to-speech system.
"""

import os
import sys
import logging

sys.path.append("/opt/annonos/core/chain_of_custody")
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [TransparencyLetter]: %(message)s'
)
logger = logging.getLogger(__name__)

class OperatorLetterAnnouncer:
    def __init__(self, letter_path: str = "/opt/annonos/transparency/LETTER_TO_THE_OPERATOR.txt"):
        self.letter_path = letter_path
        self.ledger = MerkleLedger()

    def read_letter_text(self) -> str:
        """Reads the letter from the transparency directory."""
        if os.path.exists(self.letter_path):
            with open(self.letter_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return (
                "AnnonOS Transparency Letter. "
                "This operating system was built and designed with the help of Artificial Intelligence "
                "by a blind engineer who is former law enforcement. Every voice command, step calculator, and security "
                "feature was created to ensure your total independence, privacy, and sovereignty in the field, "
                "providing a better quality of life for the blind and a safer work environment for first responders."
            )

    def generate_audible_script(self) -> str:
        """Formats the text into an audio-optimized speech script."""
        script = (
            "AnnonOS Transparency Message. Letter to the Civilian Operator. "
            "Dear Operator. If you are listening to this message, know that this operating system "
            "was designed and built specifically for you. "
            "AnnonOS is a sovereign, zero-trust system, crafted to guarantee your privacy and independence. "
            "This operating system was engineered and brought to life with the assistance of Artificial Intelligence "
            "by a blind engineer who is former law enforcement. "
            "Because of that shared experience, every feature—from the voice authentication gateway and audible transit "
            "calculator to hands-free navigation—was designed with an exact understanding of what it means to navigate "
            "the world without sight. "
            "You are holding a system that respects your sovereignty, protects your medical privacy behind hardware encryption, "
            "and ensures you always have complete, independent control. "
            "You are never alone, and your tools were built to serve you faithfully. "
            "With the help of an AI, a blind engineer who is former law enforcement built these tools to provide a "
            "better quality of life for the blind and a safer work environment for all who respond to the alarm first. "
            "Thank you and God Bless. "
            "End of message."
        )
        
        # Log readout event to Merkle audit chain
        self.ledger.append_record("TRANSPARENCY_LETTER_READ_ALOUD", {"status": "SUCCESS"})
        return script

if __name__ == "__main__":
    announcer = OperatorLetterAnnouncer()
    speech = announcer.generate_audible_script()
    print("\n--- AUDIBLE LETTER TO THE OPERATOR ---")
    print(speech)
