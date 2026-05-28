# src/python/signal_quality_mock.py
# Pure Python implementation for testing without C++ build
import numpy as np

class SignalQuality:
    """Signal quality assessment using multiple metrics.

    Computes a composite quality score (0-1) based on:
    - Variance (signal power)
    - Peak-to-peak dynamic range
    - Zero crossing rate
    - Spectral entropy
    """

    def __init__(self, sample_rate):
        self.fs = sample_rate
        self.metrics = {}

    def compute_score(self, signal):
        """Compute composite signal quality score.

        Args:
            signal: array-like, 1D signal vector

        Returns:
            float: quality score between 0 and 1
        """
        signal = np.asarray(signal)
        variance = np.var(signal)
        max_val = np.max(signal)
        min_val = np.min(signal)
        peak_to_peak = max_val - min_val

        # Zero-line crossing rate
        crossings = np.sum(np.diff(np.sign(signal)) != 0)
        zcr = crossings / len(signal)

        # Spectral entropy
        entropy = self._compute_spectral_entropy(signal)

        # Composite score: weighted combination
        score = 0.0
        score += 0.3 * min(variance / 1000.0, 1.0)
        score += 0.3 * min(peak_to_peak / 200.0, 1.0)
        score += 0.2 * min(zcr * 2.0, 1.0)
        score += 0.2 * entropy

        self.metrics = {
            'variance': variance,
            'peak_to_peak': peak_to_peak,
            'zcr': zcr,
            'spectral_entropy': entropy
        }

        return max(0.0, min(1.0, score))

    def get_metrics(self):
        """Return current metrics dict for verification."""
        return self.metrics

    def _compute_spectral_entropy(self, signal):
        """Compute normalized spectral entropy via PSD."""
        # Autocorrelation
        n = len(signal)
        acf = np.correlate(signal, signal, mode='full')
        acf = acf[n-1:]  # positive lags
        acf = acf[:n//2]

        # Power spectral density (magnitude squared)
        psd = np.abs(acf) ** 2

        # Normalize to probability
        psd_sum = np.sum(psd)
        if psd_sum < 1e-10:
            return 0.0
        psd_norm = psd / psd_sum

        # Shannon entropy
        entropy = 0.0
        for p in psd_norm:
            if p > 1e-10:
                entropy -= p * np.log2(p)

        # Normalize by max entropy
        n_bins = len(psd_norm)
        if n_bins > 1:
            entropy /= np.log2(n_bins)

        return entropy