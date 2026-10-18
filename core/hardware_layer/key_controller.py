#!/usr/bin/env python3
"""
/opt/annonos/core/hardware_layer/key_controller.py
AnnonOS Python Key Press Controller.
Binds to the compiled AudioVideoEngine-CPP key driver to map physical button presses 
to accessibility actions (e.g., repeat GPS step, trigger AI assistant, emergency SOS).
"""

import sys
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [KeyController]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSKeyController:
    def __init__(self, lib_path: str = "/opt/annon-os/AudioVideoEngine-CPP/build/"):
        self.lib_path = lib_path
        self.key_driver = None
        self._load_bindings()

    def _load_bindings(self) -> None:
        try:
            if self.lib_path not in sys.path:
                sys.path.append(self.lib_path)
            import AudioVideoEngineCPP as ave
            
            if hasattr(ave, "KeyPressDriver"):
                self.key_driver = ave.KeyPressDriver("/dev/input/event1")
                self.key_driver.initialize()
                logger.info("C++ Key Press driver bound successfully.")
            else:
                logger.warning("KeyPressDriver class not found in compiled module. Running in simulation mode.")
        except ImportError:
            logger.warning("AudioVideoEngineCPP shared library unavailable. Key controller running in simulation mode.")

    def handle_key_action(self, key_code: int, state: str) -> Optional[str]:
        """
        Maps hardware key codes to tactical OS commands.
        Example mapping:
          - Key 115 (Volume Up / Shortcut A): Trigger Step GPS Navigation repeat
          - Key 114 (Volume Down / Shortcut B): Trigger Native AI Assistant
          - Key 116 (Power / SOS): Emergency broadcast
        """
        logger.info(f"Hardware Key Event -> Code: {key_code}, State: {state}")

        if state == "PRESSED":
            if key_code == 115:  # Shortcut A
                return "REPEAT_LAST_GPS_STEP"
            elif key_code == 114:  # Shortcut B
                return "TRIGGER_NATIVE_AI_LISTENER"
            elif key_code == 116:  # Emergency SOS Key
                return "EMERGENCY_SOS_ACTIVATED"

        return "KEY_EVENT_PROCESSED"

if __name__ == "__main__":
    controller = AnnonOSKeyController()
    
    # Simulate pressing the tactical navigation shortcut key
    action = controller.handle_key_action(key_code=115, state="PRESSED")
    logger.info(f"Resolved Key Action: {action}")
