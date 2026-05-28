# tests/test_signal_quality.py
import numpy as np
import pytest
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/build')

def test_clean_signal_high_quality():
    fs = 250.0

    # Try importing - if it fails, that's expected before build
    try:
        from physio_cpp import SignalQuality
        sq = SignalQuality(fs)

        # Clean 10Hz sine wave
        t = np.linspace(0, 2, int(fs * 2))
        clean_signal = np.sin(2 * np.pi * 10 * t)

        score = sq.compute_score(clean_signal)
        assert score > 0.8, f"Clean signal should have high quality, got {score:.3f}"
    except ImportError:
        pytest.skip("C++ extension not built yet")

def test_motion_artifact_lowers_quality():
    fs = 250.0

    try:
        from physio_cpp import SignalQuality
        sq = SignalQuality(fs)

        # Signal with severe motion artifact
        t = np.linspace(0, 2, int(fs * 2))
        clean = np.sin(2 * np.pi * 10 * t)
        motion = 2.0 * np.sin(2 * np.pi * 1 * t)  # Low freq drift
        corrupted = clean + motion

        score = sq.compute_score(corrupted)
        assert score < 0.5, f"Motion artifact should lower quality, got {score:.3f}"
    except ImportError:
        pytest.skip("C++ extension not built yet")

def test_electrode_dislodgement_detected():
    fs = 250.0

    try:
        from physio_cpp import SignalQuality
        sq = SignalQuality(fs)

        # Near-zero signal (electrode detached)
        dead_signal = np.random.randn(int(fs * 2)) * 0.01

        score = sq.compute_score(dead_signal)
        metrics = sq.get_metrics()

        assert metrics['variance'] < 0.1, "Dead signal should have near-zero variance"
    except ImportError:
        pytest.skip("C++ extension not built yet")