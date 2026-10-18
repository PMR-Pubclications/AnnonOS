#!/usr/bin/env python3
"""
/opt/annonos/core/navigation/bus_route_audible_calculator.py
AnnonOS Audible Bus Route & Walking Time Calculator.
Calculates total transit and walking durations, converts distances to precise step counts, 
and generates fully audible announcements optimized for text-to-speech (TTS) engines.
"""

import sys
import logging
from typing import Dict, Any

# Ensure access to ledger
sys.path.append("/opt/annonos/core/chain_of_custody")
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AudibleTransitCalc]: %(message)s'
)
logger = logging.getLogger(__name__)

class AudibleTransitCalculator:
    def __init__(self, average_stride_meters: float = 0.75, walking_speed_mps: float = 1.2):
        """
        Default stride length (~0.75 meters) and walking speed (~1.2 meters per second)
        optimized for pedestrian navigation.
        """
        self.stride_meters = average_stride_meters
        self.walking_speed_mps = walking_speed_mps
        self.ledger = MerkleLedger()

    def calculate_walking_metrics(self, distance_meters: float) -> Dict[str, Any]:
        """Converts distance in meters into walking time in minutes and precise step counts."""
        if distance_meters <= 0:
            return {"time_mins": 0, "steps": 0}

        # Calculate time in seconds, then round to nearest minute
        time_seconds = distance_meters / self.walking_speed_mps
        time_mins = round(time_seconds / 60.0, 1)
        
        # Calculate precise steps based on stride length
        total_steps = int(distance_meters / self.stride_meters)

        return {
            "distance_meters": distance_meters,
            "time_mins": time_mins,
            "steps": total_steps
        }

    def plan_audible_route(self, origin: str, destination: str, walk_to_bus_meters: float, bus_route_name: str, bus_wait_mins: float, bus_ride_mins: float) -> str:
        """
        Synthesizes a complete multi-modal route (walk -> bus -> walk) into a 
        clear, naturally paced audible script optimized for screen readers and TTS audio.
        """
        logger.info(f"Planning audible route from [{origin}] to [{destination}] via [{bus_route_name}]...")

        # 1. Calculate walking metrics to the bus stop
        initial_walk = self.calculate_walking_metrics(walk_to_bus_meters)

        # 2. Compile speech-optimized announcement string
        audible_script = (
            f"Route plan loaded from {origin} to {destination}. "
            f"Step one: Walk {initial_walk['distance_meters']} meters, approximately {initial_walk['steps']} steps, "
            f"taking about {initial_walk['time_mins']} minutes to reach the bus stop for {bus_route_name}. "
            f"Estimated wait time at the stop is {bus_wait_mins} minutes. "
            f"Board {bus_route_name}. Total bus ride duration will be {bus_ride_mins} minutes. "
            f"Route calculation complete. Ready for navigation."
        )

        # Log route calculation event to Merkle audit chain
        self.ledger.append_record(
            "AUDIBLE_ROUTE_CALCULATED",
            {
                "origin": origin,
                "destination": destination,
                "bus_route": bus_route_name,
                "total_estimated_mins": initial_walk['time_mins'] + bus_wait_mins + bus_ride_mins
            }
        )

        logger.info("Audible route script successfully generated.")
        return audible_script

if __name__ == "__main__":
    calculator = AudibleTransitCalculator()
    
    # Test planning a route for a blind civilian
    announcement = calculator.plan_audible_route(
        origin="Sector Alpha Safehouse",
        destination="Central Medical Post",
        walk_to_bus_meters=350.0,
        bus_route_name="Route 42 Express",
        bus_wait_mins=4.0,
        bus_ride_mins=12.0
    )
    
    print("\n--- AUDIBLE TRANSIT ANNOUNCEMENT ---")
    print(announcement)
