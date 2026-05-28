# tests/test_pipeline_integration.py
import numpy as np
import pytest
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/src/python')

from signal_processor import SignalProcessor
from feature_pipeline import FeaturePipeline

def test_signal_processor_e2e():
    """Test end-to-end pipeline from raw data to features"""
    processor = SignalProcessor(
        eeg_channels=8,
        imu_channels=6,
        sample_rate=250.0
    )

    # Simulate 2 seconds of data (500 samples at 250Hz)
    eeg_data = np.random.randn(500, 8) * 30 + 100  # With DC offset
    imu_data = np.random.randn(500, 6) * 10

    # Process
    features = processor.process(eeg_data, imu_data)

    # Should output valid features
    assert 'eeg_band_powers' in features
    assert 'eeg_quality_score' in features
    assert 'imu_features' in features
    assert 0 <= features['eeg_quality_score'] <= 1

def test_feature_pipeline_produces_downstream_format():
    """Test feature pipeline outputs correct format for ML models"""
    fp = FeaturePipeline(sample_rate=250.0)

    # Generate synthetic time-domain features
    raw_features = {
        'rms': 0.5,
        'mav': 0.4,
        'alpha_power': 100.0,
        'beta_power': 80.0,
        'peak_freq': 10.0
    }

    vector = fp.to_feature_vector(raw_features)
    assert isinstance(vector, np.ndarray)
    assert vector.shape[0] > 0, "Feature vector should not be empty"