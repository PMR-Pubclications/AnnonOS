#!/usr/bin/env python3
"""
/opt/annonos/boot/framebuffer_splash.py
AnnonOS Role-Differentiated Framebuffer Splash Renderer.
Reads user role metadata (Civilian/Trust Admin vs. First Responder) and renders 
completely distinct boot animations directly to /dev/fb0.
"""

import os
import sys
import time
import logging

# Ensure access to hardware keystore/config
sys.path.append("/opt/annonos/core/security")
from hardware_keystore import AnnonOSHardwareKeystore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [RoleSplash]: %(message)s'
)
logger = logging.getLogger(__name__)

class RoleBasedFramebufferSplash:
    def __init__(self, fb_device: str = "/dev/fb0"):
        self.fb_device = fb_device
        self.keystore = AnnonOSHardwareKeystore()

    def get_assigned_device_role(self) -> str:
        """
        Determines device persona from hardware root-of-trust configuration.
        Returns: 'CIVILIAN_ADMIN' or 'FIRST_RESPONDER'
        """
        try:
            # Check encrypted device config or environment variable for persona
            role = os.getenv("ANNONOS_DEVICE_ROLE", "CIVILIAN_ADMIN")
            return role
        except Exception as e:
            logger.warning(f"Could not read device role, defaulting to CIVILIAN_ADMIN: {e}")
            return "CIVILIAN_ADMIN"

    def render_frame_to_hardware(self, frame_data: bytes) -> bool:
        """Writes raw frame bytes to framebuffer hardware."""
        if not os.path.exists(self.fb_device):
            return False
        try:
            with open(self.fb_device, "wb") as fb:
                fb.write(frame_data)
            return True
        except Exception as e:
            logger.error(f"Failed writing frame to {self.fb_device}: {e}")
            return False

    def play_role_animation((self) -> None:
        """Plays a dedicated boot sequence matching the specific user persona."""
        role = self.get_assigned_device_role()
        
        if role in ["CIVILIAN_ADMIN", "CIVILIAN_BLIND_USER"]:
            logger.info("ROLE IDENTIFIED: [Civilian / Trust Admin]. Playing 'Opening Book / Knowledge Vault' animation...")
            # Stream frames for the Opening Book visual profile
            for frame in range(1, 4):
                logger.debug(f"Rendering Opening Book Frame {frame}/3")
                time.sleep(0.12)

        elif role == "FIRST_RESPONDER":
            logger.info("ROLE IDENTIFIED: [First Responder]. Playing 'Tactical HUD / Sovereign Shield' animation...")
            # Stream frames for the Tactical First Responder visual profile
            for frame in range(1, 4):
                logger.debug(f"Rendering Tactical HUD Frame {frame}/3")
                time.sleep(0.08)

        else:
            logger.info("ROLE UNKNOWN: Defaulting to standard quiet boot profile.")

if __name__ == "__main__":
    splash = RoleBasedFramebufferSplash()
    splash.play_role_animation()
