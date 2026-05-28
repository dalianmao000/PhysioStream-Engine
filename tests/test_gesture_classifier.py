import numpy as np
import pytest
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/src/python')

from downstream_demo import GestureClassifier

def test_gesture_classifier_training():
    """Test that classifier can learn to distinguish 2 gestures from synthetic data"""
    np.random.seed(42)

    clf = GestureClassifier(n_classes=2)

    # Generate synthetic sEMG patterns for 2 gestures
    n_samples = 100
    X = np.vstack([
        np.random.randn(n_samples, 8) * 20 + np.array([50, 40, 30, 20, 10, 5, 2, 1]),
        np.random.randn(n_samples, 8) * 20 + np.array([1, 2, 5, 10, 20, 30, 40, 50])
    ])
    y = np.array([0] * n_samples + [1] * n_samples)

    # Train
    clf.fit(X, y, epochs=50, verbose=False)

    # Evaluate
    acc = clf.evaluate(X, y)
    assert acc > 0.7, f"Classifier should learn synthetic patterns, got accuracy {acc:.3f}"

def test_gesture_classifier_inference_latency():
    """Test that inference is fast enough for real-time applications"""
    import time
    clf = GestureClassifier(n_classes=5)
    clf.fit(np.random.randn(200, 8), np.random.randint(0, 5, 200), epochs=10)

    single_sample = np.random.randn(8).reshape(1, -1)

    start = time.time()
    for _ in range(100):
        pred = clf.predict(single_sample)
    latency = (time.time() - start) / 100 * 1000  # ms

    assert latency < 10, f"Inference latency {latency:.2f}ms too high for real-time"