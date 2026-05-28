# tests/test_feature_extractor.py
import numpy as np
import pytest
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/build')

def test_time_domain_features_extraction():
    fs = 250.0

    try:
        from physio_cpp import FeatureExtractor
        fe = FeatureExtractor(fs)

        # Generate test signal: 10Hz sine with known RMS and MAV
        t = np.linspace(0, 2, int(fs * 2))
        signal = np.sin(2 * np.pi * 10 * t)

        features = fe.extract_time_domain(signal)

        assert 'rms' in features
        assert 'mav' in features
        assert 'zero_cross' in features

        # RMS of sine should be ~0.707 (peak/sqrt(2))
        assert 0.65 < features['rms'] < 0.75, f"RMS out of expected range: {features['rms']}"
    except ImportError:
        pytest.skip("C++ extension not built yet")

def test_frequency_domain_features_extraction():
    fs = 250.0

    try:
        from physio_cpp import FeatureExtractor
        fe = FeatureExtractor(fs)

        # 10Hz dominant signal
        t = np.linspace(0, 2, int(fs * 2))
        signal = np.sin(2 * np.pi * 10 * t) + 0.1 * np.random.randn(len(t))

        features = fe.extract_frequency_domain(signal)

        assert 'peak_freq' in features
        assert 'spectral_entropy' in features
        assert features['peak_freq'] == pytest.approx(10.0, abs=1.0)
    except ImportError:
        pytest.skip("C++ extension not built yet")

def test_band_power_features_for_eeg():
    fs = 250.0

    try:
        from physio_cpp import FeatureExtractor
        fe = FeatureExtractor(fs)

        # EEG-like signal with alpha (10Hz) dominance
        t = np.linspace(0, 2, int(fs * 2))
        signal = (np.sin(2 * np.pi * 10 * t) * 2 +   # Alpha
                  np.sin(2 * np.pi * 4 * t) * 1 +     # Theta
                  np.sin(2 * np.pi * 20 * t) * 0.5 +  # Beta
                  np.random.randn(len(t)) * 0.2)

        features = fe.extract_frequency_domain(signal)

        # Should detect alpha as dominant
        assert features['peak_freq'] == pytest.approx(10.0, abs=2.0)
    except ImportError:
        pytest.skip("C++ extension not built yet")