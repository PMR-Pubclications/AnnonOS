#!/usr/bin/env python3
"""
/opt/annonos/core/navigation/step_gps_navigator.py
AnnonOS Step-Based GPS Navigation Engine.
Translates real-time geospatial coordinates and compass headings into precise 
step-by-step audio instructions (e.g., "Walk forward 45 steps, take a hard left") 
optimized for blind and low-vision field operators via tactical earpieces.
"""

import math
import logging
from typing import Dict, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [StepGPSNavigator]: %(message)s'
)
logger = logging.getLogger(__name__)

class StepGPSNavigator:
    def __init__(self, average_stride_length_meters: float = 0.75):
        # Average human walking stride length (~0.75 meters or ~2.46 feet per step)
        self.stride_length = average_stride_length_meters
        self.current_lat: Optional[float] = None
        self.current_lon: Optional[float] = None
        self.current_heading_deg: float = 0.0  # 0 = North, 90 = East, etc.

    def update_position(self, lat: float, lon: float, heading_deg: float) -> None:
        """Updates real-time GPS position and compass heading from hardware sensors."""
        self.current_lat = lat
        self.current_lon = lon
        self.current_heading_deg = heading_deg

    def _calculate_distance_and_bearing(self, dest_lat: float, dest_lon: float) -> Tuple[float, float]:
        """Calculates distance in meters and bearing angle to destination using Haversine formula."""
        if self.current_lat is None or self.current_lon is None:
            return 0.0, 0.0

        R = 6371e3  # Earth radius in meters
        phi1 = math.radians(self.current_lat)
        phi2 = math.radians(dest_lat)
        dphi = math.radians(dest_lat - self.current_lat)
        dlambda = math.radians(dest_lon - self.current_lon)

        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_meters = R * c

        # Bearing calculation
        y = math.sin(dlambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
        bearing_rad = math.atan2(y, x)
        bearing_deg = (math.degrees(bearing_rad) + 360) % 360

        return distance_meters, bearing_deg

    def get_tactical_step_guidance(self, dest_lat: float, dest_lon: float) -> str:
        """
        Computes distance, converts it into exact steps, evaluates turn angles relative 
        to operator heading, and returns a voice-first directional instruction.
        """
        distance_m, target_bearing = self._calculate_distance_and_bearing(dest_lat, dest_lon)
        
        if distance_m < 2.0:
            return "Destination reached. You have arrived."

        # Convert meters into exact physical steps
        steps = round(distance_m / self.stride_length)

        # Calculate relative turn angle
        angle_diff = (target_bearing - self.current_heading_deg + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360

        # Translate angle difference into natural voice-first turning instructions
        if abs(angle_diff) <= 15:
            turn_instruction = f"Walk forward {steps} steps."
        elif 15 < angle_diff <= 75:
            turn_instruction = f"Take a slight right, then walk {steps} steps."
        elif 75 < angle_diff <= 135:
            turn_instruction = f"Take a right turn, then walk {steps} steps."
        elif angle_diff > 135:
            turn_instruction = f"Turn completely around, then walk {steps} steps."
        elif -75 <= angle_diff < -15:
            turn_instruction = f"Take a slight left, then walk {steps} steps."
        elif -135 <= angle_diff < -75:
            turn_instruction = f"Take a left turn, then walk {steps} steps."
        else:
            turn_instruction = f"Turn around and walk {steps} steps."

        logger.info(f"[Step GPS Guidance]: {turn_instruction} (Distance: {distance_m:.1f}m)")
        return turn_instruction

if __name__ == "__main__":
    navigator = StepGPSNavigator()
    
    # Simulate starting position in Vancouver, WA facing North (0 degrees)
    navigator.update_position(lat=45.6387, lon=-122.6615, heading_deg=0.0)
    
    # Simulate a target waypoint slightly north-east
    instruction = navigator.get_tactical_step_guidance(dest_lat=45.6400, dest_lon=-122.6600)
    print(f"Earpiece Audio Output: {instruction}")
