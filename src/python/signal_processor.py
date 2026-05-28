# src/python/signal_processor.py
import numpy as np
from typing import Dict
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/build')

# Try to import C++ modules, fall back to mocks
try:
    from physio_cpp import AdaptiveFilter, SignalQuality, FeatureExtractor
except ImportError:
    from adaptive_filter_mock import AdaptiveFilter
    from signal_quality_mock import SignalQuality
    from feature_extractor_mock import FeatureExtractor

class SignalProcessor:
    """High-level signal processing pipeline orchestrating C++ core modules."""

    def __init__(self, eeg_channels: int, imu_channels: int, sample_rate: float):
        self.eeg_channels = eeg_channels
        self.imu_channels = imu_channels
        self.fs = sample_rate

        # Initialize C++ processing cores
        self.adaptive_filters = [
            AdaptiveFilter(sample_rate, filter_length=64, mu=0.01)
            for _ in range(eeg_channels)
        ]
        self.sqa = SignalQuality(sample_rate)
        self.feature_extractor = FeatureExtractor(sample_rate)

        self.buffer_len = int(sample_rate * 2)  # 2-second window
        self.buffer = np.zeros((self.buffer_len, eeg_channels))

    def process(self, eeg_data: np.ndarray, imu_data: np.ndarray) -> Dict:
        """
        Process raw EEG and IMU data through the full pipeline.

        Args:
            eeg_data: [n_samples x n_eeg_channels]
            imu_data: [n_samples x n_imu_channels]

        Returns:
            Dict with 'eeg_band_powers', 'eeg_quality_score', 'imu_features'
        """
        # 1. Adaptive filtering using IMU as reference noise
        eeg_filtered = np.zeros_like(eeg_data)
        for ch in range(self.eeg_channels):
            # IMU magnitude as reference noise signal
            imu_magnitude = np.linalg.norm(imu_data, axis=1)
            if hasattr(self.adaptive_filters[ch], 'filter'):
                filtered = self.adaptive_filters[ch].filter(
                    eeg_data[:, ch], imu_magnitude
                )
            else:
                filtered = eeg_data[:, ch]  # Fallback
            eeg_filtered[:, ch] = filtered

        # 2. Signal Quality Assessment
        # Average across channels for overall quality
        avg_signal = eeg_filtered.mean(axis=1)
        quality_score = self.sqa.compute_score(avg_signal)

        # 3. Feature extraction from best-quality window
        if quality_score > 0.6:
            features = self.feature_extractor.extract_frequency_domain(avg_signal)
            time_features = self.feature_extractor.extract_time_domain(avg_signal)
            features.update(time_features)
        else:
            features = {}

        # 4. IMU features
        imu_features = self._extract_imu_features(imu_data)

        return {
            'eeg_band_powers': {
                'alpha': features.get('alpha_power', 0),
                'beta': features.get('beta_power', 0),
                'theta': features.get('theta_power', 0),
                'delta': features.get('delta_power', 0)
            },
            'eeg_quality_score': quality_score,
            'imu_features': imu_features,
            'peak_freq': features.get('peak_freq', 0)
        }

    def _extract_imu_features(self, imu_data: np.ndarray) -> Dict:
        """Extract features from IMU data (acceleration, gyroscope)."""
        return {
            'acc_magnitude_mean': np.linalg.norm(imu_data[:, :3], axis=1).mean(),
            'acc_magnitude_std': np.linalg.norm(imu_data[:, :3], axis=1).std(),
            'gyro_magnitude_mean': np.linalg.norm(imu_data[:, 3:], axis=1).mean(),
            'movement_intensity': np.linalg.norm(imu_data[:, :3], axis=1).std()
        }