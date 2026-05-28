# src/python/feature_pipeline.py
import numpy as np
from typing import Dict

class FeaturePipeline:
    """Converts raw features to fixed-size vectors for downstream ML models."""

    def __init__(self, sample_rate: float):
        self.fs = sample_rate

    def to_feature_vector(self, raw_features: Dict) -> np.ndarray:
        """
        Convert feature dict to normalized feature vector.

        Returns:
            np.ndarray of shape [n_features]
        """
        feature_names = ['rms', 'mav', 'alpha_power', 'beta_power',
                        'theta_power', 'delta_power', 'peak_freq',
                        'alpha_theta_ratio']

        vector = []
        for name in feature_names:
            val = raw_features.get(name, 0.0)
            # Log transform for power features (compress dynamic range)
            if 'power' in name:
                val = np.log10(val + 1e-10)
            vector.append(val)

        return np.array(vector)

    def compute_physio_state(self, features: Dict) -> str:
        """
        Rule-based physiological state classification.
        For demonstration only - downstream models replace this.
        """
        alpha = features.get('alpha', 0)
        beta = features.get('beta', 0)
        ratio = alpha / (beta + 1e-10)

        if ratio > 1.5:
            return "relaxed"
        elif ratio < 0.7:
            return "stressed"
        else:
            return "neutral"