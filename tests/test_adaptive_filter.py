# tests/test_adaptive_filter.py
import numpy as np
import pytest

# This test will fail until we build the C++ extension
# For now, we test the Python-side logic only
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/build')

def test_lms_filter_removes_imu_correlated_noise():
    np.random.seed(42)
    fs = 250.0

    # Simulate: EEG with motion artifact correlated with IMU
    t = np.linspace(0, 1, int(fs))
    imu_noise = 0.5 * np.sin(2 * np.pi * 3 * t)  # 3Hz IMU motion component
    eeg_clean = np.sin(2 * np.pi * 10 * t)       # 10Hz clean EEG
    eeg_corrupted = eeg_clean + imu_noise + 0.3 * np.random.randn(len(t))

    # Try importing - if it fails, that's expected before build
    try:
        from physio_cpp import AdaptiveFilter
        adaptive_filter = AdaptiveFilter(fs, filter_length=64, mu=0.01)
        filtered = adaptive_filter.filter(eeg_corrupted, imu_noise)

        # After filtering, correlation with IMU should be reduced by >50%
        corr_before = np.corrcoef(eeg_corrupted, imu_noise)[0, 1]
        corr_after = np.corrcoef(filtered, imu_noise)[0, 1]

        assert abs(corr_after) < abs(corr_before) * 0.5, \
            f"Noise reduction insufficient: corr_before={corr_before:.3f}, corr_after={corr_after:.3f}"
    except ImportError:
        # C++ extension not built yet - skip test
        pytest.skip("C++ extension not built yet")