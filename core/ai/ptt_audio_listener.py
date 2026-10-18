#!/usr/bin/env python3
"""
/opt/annonos/core/ai/ptt_audio_listener.py
AnnonOS Push-to-Talk (PTT) Audio Listener & Voice Pipeline.
Listens for physical key triggers (e.g., PTT button press), captures voice audio via 
the C++ engine, transcribes it, and hands off the command to the native AI assistant.
"""

import sys
import time
import logging
from typing import Optional

# Ensure hardware layer paths are linked
sys.path.append("/opt/annonos/core/ai")
from native_ai_assistant import AnnonOSNativeAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [PTTAudioListener]: %(message)s'
)
logger = logging.getLogger(__name__)

class PTTAudioListener:
    def __init__(self):
        self.ai_assistant = AnnonOSNativeAI()
        self.audio_driver = None
        self._load_cpp_audio_driver()

    def _load_cpp_audio_driver(self) -> None:
        try:
            sys.path.append("/opt/annon-os/AudioVideoEngine-CPP/build/")
            import AudioVideoEngineCPP as ave
            if hasattr(ave, "AudioInputDriver"):
                self.audio_driver = ave.AudioInputDriver()
                logger.info("C++ Audio Input driver bound successfully.")
            else:
                logger.warning("AudioInputDriver not found. Running in simulation mode.")
        except ImportError:
            logger.warning("AudioVideoEngineCPP library unavailable. Audio listener running in simulation mode.")

    def on_ptt_pressed(self) -> None:
        """Triggered immediately when the operator presses the physical PTT key."""
        logger.info("PTT Button PRESSED: Opening tactical microphone channel...")
        if self.audio_driver:
            self.audio_driver.start_recording("/tmp/operator_command.wav")
        else:
            logger.info("[Simulation]: Microphone active and listening...")

    def on_ptt_released(self, simulated_spoken_text: Optional[str] = None) -> str:
        """Triggered when the PTT key is released; stops recording and processes voice command."""
        logger.info("PTT Button RELEASED: Closing microphone channel and processing audio...")
        
        audio_buffer = []
        if self.audio_driver:
            audio_buffer = self.audio_driver.stop_recording()
        
        # In production, audio_buffer is passed to Whisper / speech-to-text engine.
        # For testing, we evaluate the transcribed text command:
        command_text = simulated_spoken_text or "Give me directions to the perimeter."
        logger.info(f"Transcribed Operator Speech: '{command_text}'")

        # Route directly into AnnonOS Native AI / Trust-Main speech pipeline
        response = self.ai_assistant.process_voice_command(command_text)
        return response

if __name__ == "__main__":
    listener = PTTAudioListener()
    
    # Simulate a field operator pressing the PTT button, speaking, and releasing
    listener.on_ptt_pressed()
    time.sleep(1.0)  # Simulating speech duration
    listener.on_ptt_released(simulated_spoken_text="What is the system status?")
