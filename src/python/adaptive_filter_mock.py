# src/python/adaptive_filter_mock.py
"""
Pure Python LMS adaptive filter implementation for testing.
This mock mimics the C++ AdaptiveFilter class interface.
"""
import numpy as np


class AdaptiveFilter:
    """
    LMS (Least Mean Squares) adaptive filter for IMU-assisted motion artifact removal.

    Args:
        sample_rate: Sampling rate in Hz
        filter_length: Number of filter coefficients (M)
        mu: Step size (learning rate) for LMS adaptation
    """

    def __init__(self, sample_rate, filter_length=64, mu=0.01):
        self.fs = sample_rate
        self.M = filter_length
        self.mu = mu
        self.w = np.zeros(filter_length)
        self.x_buffer = np.zeros(filter_length)
        self.initialized = False

    def filter(self, primary_input, reference_noise):
        """
        Apply LMS adaptive filtering to remove reference noise from primary input.

        Args:
            primary_input: Vector of corrupted signal (e.g., EEG with motion artifacts)
            reference_noise: Vector of reference noise (e.g., IMU signal)

        Returns:
            Filtered output (error signal = denoised primary)
        """
        primary_input = np.asarray(primary_input)
        reference_noise = np.asarray(reference_noise)
        N = primary_input.shape[0]
        output = np.zeros(N)

        for i in range(N):
            # Update circular buffer
            for j in range(self.M - 1, 0, -1):
                self.x_buffer[j] = self.x_buffer[j - 1]
            self.x_buffer[0] = reference_noise[i]

            # LMS update with weight clamping to prevent overflow
            y = np.dot(self.w, self.x_buffer)
            e = primary_input[i] - y
            for j in range(self.M):
                self.w[j] += self.mu * e * self.x_buffer[j]
            # Clamp weights to prevent overflow
            self.w = np.clip(self.w, -100, 100)

            output[i] = e  # Error signal = denoised primary

        return output

    def reset(self):
        """Reset filter weights to zero."""
        self.w.fill(0.0)