# src/python/feature_extractor_mock.py
"""Pure Python mock for FeatureExtractor — used when C++ extension unavailable."""
import numpy as np


class FeatureExtractor:
    def __init__(self, sample_rate):
        self.fs = sample_rate

    def extract_time_domain(self, signal):
        signal = np.asarray(signal)
        return {
            'rms': float(np.sqrt(np.mean(signal ** 2))),
            'mav': float(np.mean(np.abs(signal))),
            'zero_cross': float(np.sum(np.diff(np.sign(signal)) != 0) / len(signal)),
            'variance': float(np.var(signal)),
        }

    def extract_frequency_domain(self, signal):
        signal = np.asarray(signal)
        N = len(signal)
        freqs = np.fft.rfftfreq(N, 1.0 / self.fs)
        psd = np.abs(np.fft.rfft(signal)) ** 2

        bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
        }
        features = {}
        for band, (low, high) in bands.items():
            idx = (freqs >= low) & (freqs < high)
            features[f'{band}_power'] = float(np.sum(psd[idx])) if np.any(idx) else 0.0

        alpha_power = features['alpha_power']
        theta_power = features['theta_power']
        features['alpha_theta_ratio'] = alpha_power / (theta_power + 1e-10)

        peak_idx = int(np.argmax(psd))
        features['peak_freq'] = float(freqs[peak_idx])

        psd_norm = psd / (psd.sum() + 1e-10)
        features['spectral_entropy'] = float(-np.sum(psd_norm * np.log2(psd_norm + 1e-10)) / np.log2(len(psd)))

        return features

    def extract_nonlinear(self, signal):
        signal = np.asarray(signal)
        N = len(signal)
        segs = [np.max(np.abs(signal[i:])) for i in range(1, N)]
        return {
            'sample_entropy': float(-np.mean(np.log(np.array(segs) + 1e-10))),
        }