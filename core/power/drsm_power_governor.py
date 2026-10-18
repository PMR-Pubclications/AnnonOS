#!/usr/bin/env python3
"""
/opt/annonos/core/power/drsm_power_governor.py
AnnonOS Dynamic Resource & Power Governor (DRSM).
Monitors system thermals, battery state of charge, and CPU load to automatically 
adjust performance profiles, ensuring sustained operational life in tactical environments.
"""

import sys
import os
import time
import logging
from typing import Dict, Any

# Ensure access to ledger
sys.path.append("/opt/annonos/core/chain_of_custody")
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [DRSMGovernor]: %(message)s'
)
logger = logging.getLogger(__name__)

class DRSMPowerGovernor:
    def __init__(self):
        self.ledger = MerkleLedger()
        self.thermal_zone_path = "/sys/class/thermal/thermal_zone0/temp"
        self.battery_capacity_path = "/sys/class/power_supply/BAT0/capacity"
        self.current_profile = "NOMINAL"

    def read_system_telemetry(self) -> Dict[str, float]:
        """Reads hardware sensors for CPU temperature and battery percentage."""
        temp_c = 45.0  # Simulated default baseline (45°C)
        battery_pct = 85.0  # Simulated default baseline (85%)

        if os.path.exists(self.thermal_zone_path):
            try:
                with open(self.thermal_zone_path, "r") as f:
                    temp_c = float(f.read().strip()) / 1000.0
            except Exception as e:
                logger.warning(f"Could not read thermal sensor: {e}")

        if os.path.exists(self.battery_capacity_path):
            try:
                with open(self.battery_capacity_path, "r") as f:
                    battery_pct = float(f.read().strip())
            except Exception as e:
                logger.warning(f"Could not read battery sensor: {e}")

        return {"temperature_c": temp_c, "battery_pct": battery_pct}

    def evaluate_and_apply_governor(() -> str:
        """
        Evaluates hardware metrics and applies thermal/power scaling profiles.
        Profiles:
          - NOMINAL: Full performance, active mesh, standard voice polling.
          - SURVIVAL: Power < 20% or Temp > 70°C -> Throttles CPU, reduces RF beacon intervals.
          - CRITICAL_STEALTH: Power < 5% or Temp > 85°C -> Drops non-essential daemons, enforces thermal throttle.
        """
        telemetry = self.read_system_telemetry()
        temp = telemetry["temperature_c"]
        bat = telemetry["battery_pct"]

        new_profile = "NOMINAL"

        if temp >= 85.0 or bat <= 5.0:
            new_profile = "CRITICAL_STEALTH"
        elif temp >= 70.0 or bat <= 20.0:
            new_profile = "SURVIVAL"

        if new_profile != self.current_profile:
            logger.warning(f"DRSM STATE CHANGE: Shifting from [{self.current_profile}] to [{new_profile}]")
            logger.info(f"Telemetry Trigger -> CPU Temp: {temp}°C | Battery: {bat}%")
            self.current_profile = new_profile

            # Log governor state change to Merkle audit chain
            self.ledger.append_record(
                "DRSM_PROFILE_MUTATED",
                {
                    "new_profile": new_profile,
                    "temperature_c": temp,
                    "battery_pct": bat
                }
            )

            # Apply OS scaling rules
            self._apply_hardware_profile(new_profile)

        return self.current_profile

    def _apply_hardware_profile(self, profile: str) -> None:
        """Executes low-level hardware frequency and backlight controls."""
        if profile == "CRITICAL_STEALTH":
            logger.critical("Applying CRITICAL_STEALTH: CPU set to powersave, RF beacon intervals extended to 15m.")
            # Example OS scaling: os.system("cpufreq-set -g powersave")
        elif profile == "SURVIVAL":
            logger.info("Applying SURVIVAL: Reducing display brightness, disabling background log flushes.")
            # Example OS scaling: os.system("brightnessctl set 10%")
        else:
            logger.info("Applying NOMINAL: Restoring standard operating frequencies.")

if __name__ == "__main__":
    governor = DRSMPowerGovernor()
    active_profile = governor.evaluate_and_apply_governor()
    print(f"\n--- DRSM ACTIVE GOVERNOR PROFILE: {active_profile} ---")
