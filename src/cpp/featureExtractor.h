// src/cpp/featureExtractor.h
#pragma once
#include <Eigen/Dense>
#include <unordered_map>
#include <string>

class FeatureExtractor {
public:
    FeatureExtractor(double sample_rate) : fs_(sample_rate) {}

    std::unordered_map<std::string, double> extract_time_domain(const Eigen::VectorXd& signal) {
        std::unordered_map<std::string, double> features;

        // RMS (Root Mean Square)
        features["rms"] = std::sqrt(signal.array().square().mean());

        // MAV (Mean Absolute Value)
        features["mav"] = signal.array().abs().mean();

        // Zero crossing rate
        int crossings = 0;
        for (int i = 1; i < signal.size(); ++i) {
            if ((signal(i) > 0) != (signal(i-1) > 0)) crossings++;
        }
        features["zero_cross"] = static_cast<double>(crossings) / signal.size();

        // Variance
        features["variance"] = signal.var();

        return features;
    }

    std::unordered_map<std::string, double> extract_frequency_domain(const Eigen::VectorXd& signal) {
        std::unordered_map<std::string, double> features;

        int N = signal.size();
        Eigen::VectorXd psd = compute_psd(signal, N);

        // Band powers: delta(1-4), theta(4-8), alpha(8-13), beta(13-30)
        double delta_power = band_power(psd, 1, 4, fs_, N);
        double theta_power = band_power(psd, 4, 8, fs_, N);
        double alpha_power = band_power(psd, 8, 13, fs_, N);
        double beta_power = band_power(psd, 13, 30, fs_, N);

        features["delta_power"] = delta_power;
        features["theta_power"] = theta_power;
        features["alpha_power"] = alpha_power;
        features["beta_power"] = beta_power;
        features["alpha_theta_ratio"] = alpha_power / (theta_power + 1e-10);

        // Peak frequency
        int peak_idx;
        psd.maxCoeff(&peak_idx);
        features["peak_freq"] = static_cast<double>(peak_idx) * fs_ / N;

        // Spectral entropy
        double sum_psd = psd.sum();
        double entropy = 0.0;
        for (int i = 0; i < psd.size(); ++i) {
            double p = psd(i) / sum_psd;
            if (p > 1e-10) entropy -= p * std::log2(p);
        }
        features["spectral_entropy"] = entropy / std::log2(psd.size());

        return features;
    }

    std::unordered_map<std::string, double> extract_nonlinear(const Eigen::VectorXd& signal) {
        std::unordered_map<std::string, double> features;

        // Approximate entropy (sample entropy proxy)
        int N = signal.size();
        double sum_log = 0.0;
        for (int i = 1; i < N; ++i) {
            sum_log += std::log(signal.segment(i, N-i).array().abs().maxCoeff() + 1e-10);
        }
        features["sample_entropy"] = -sum_log / static_cast<double>(N);

        return features;
    }

private:
    double fs_;

    Eigen::VectorXd compute_psd(const Eigen::VectorXd& signal, int N) {
        // Welch's method simplified: use autocorrelation FFT
        Eigen::VectorXcf fft_result = FFT(signal);
        Eigen::VectorXd psd = fft_result.head(N/2).cwiseAbs2().real();
        return psd;
    }

    double band_power(const Eigen::VectorXd& psd, double low_freq, double high_freq,
                     double fs, int N) {
        int low_bin = static_cast<int>(low_freq * N / fs);
        int high_bin = static_cast<int>(high_freq * N / fs);
        return psd.segment(low_bin, high_bin - low_bin).sum();
    }

    Eigen::VectorXcf FFT(const Eigen::VectorXd& x) {
        int N = x.size();
        Eigen::VectorXcf X(N);
        for (int k = 0; k < N; ++k) {
            std::complex<double> sum(0, 0);
            for (int n = 0; n < N; ++n) {
                double angle = -2.0 * M_PI * k * n / N;
                sum += std::complex<double>(std::cos(angle), std::sin(angle)) * x(n);
            }
            X(k) = sum;
        }
        return X;
    }
};