#!/usr/bin/env python3
"""
/opt/annonos/core/zero_smoothing/outlier_detector.py
Zero-Smoothing Outlier Detector for AnnonOS.
Intercepts high-frequency sensor streams and captures transient anomalies (3sigma+ outliers) 
without clipping, low-pass filtering, or destructive smoothing.
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [ZeroSmoothing]: %(message)s'
)
logger = logging.getLogger(__name__)

class ZeroSmoothingDetector:
    def __init__(self, window_size: int = 100, sigma_threshold: float = 3.0):
        self.window_size = window_size
        self.sigma_threshold = sigma_threshold
        self.buffer: List[float] = []

    def ingest_sample(self, sample_value: float) -> Optional[Dict[str, Union[float, bool]]]:
        """
        Ingests a raw telemetry sample, bypassing low-pass filters to evaluate 
        statistical variance and preserve 3sigma+ transient spikes.
        """
        self.buffer.append(sample_value)
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0)

        if len(self.buffer) < 10:
            # Insufficient sample size for rolling baseline
            return {"value": sample_value, "outlier": False}

        # Calculate rolling mean and standard deviation
        arr = np.array(self.buffer)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            z_score = 0.0
        else:
            z_score = abs(sample_value - mean) / std

        is_outlier = z_score >= self.sigma_threshold

        if is_outlier:
            logger.warning(f"CRITICAL TRANSIENT DETECTED (3σ+ Outlier): Value={sample_value:.4f} "
                           f"(Mean={mean:.4f}, Std={std:.4f}, Z-Score={z_score:.2f})")

        return {
            "value": sample_value,
            "mean": float(mean),
            "std": float(std),
            "z_score": float(z_score),
            "outlier": bool(is_outlier)
        }

if __name__ == "__main__":
    detector = ZeroSmoothingDetector()
    # Simulate normal stream followed by a sudden physical anomaly spike
    test_stream = [1.0, 1.02, 0.98, 1.01, 0.99, 1.0, 1.01, 0.99, 1.0, 15.4]
    
    for val in test_stream:
        result = detector.ingest_sample(val)
        if result["outlier"]:
            logger.info(f"Anomaly successfully preserved without clipping: {result}")
