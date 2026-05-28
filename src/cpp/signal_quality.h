// src/cpp/signal_quality.h
#pragma once
#include <Eigen/Dense>
#include <cmath>
#include <unordered_map>
#include <string>

class SignalQuality {
public:
    SignalQuality(double sample_rate) : fs_(sample_rate) {}

    double compute_score(const Eigen::VectorXd& signal) {
        double variance = signal.var();
        double max_val = signal.maxCoeff();
        double min_val = signal.minCoeff();
        double peak_to_peak = max_val - min_val;

        // Zero-line crossing rate
        int crossings = 0;
        for (int i = 1; i < signal.size(); ++i) {
            if ((signal(i) > 0) != (signal(i-1) > 0)) crossings++;
        }
        double zcr = static_cast<double>(crossings) / signal.size();

        // Spectral entropy (proxy for signal structure)
        double entropy = compute_spectral_entropy(signal);

        // Composite score: weighted combination
        double score = 0.0;
        score += 0.3 * std::min(variance / 1000.0, 1.0);   // Variance (not too low, not too high)
        score += 0.3 * std::min(peak_to_peak / 200.0, 1.0); // Dynamic range
        score += 0.2 * std::min(zcr * 2.0, 1.0);            // Some crossing rate is good
        score += 0.2 * entropy;                              // Spectral structure

        metrics_["variance"] = variance;
        metrics_["peak_to_peak"] = peak_to_peak;
        metrics_["zcr"] = zcr;
        metrics_["spectral_entropy"] = entropy;

        return std::clamp(score, 0.0, 1.0);
    }

    Eigen::VectorXd get_metrics() {
        Eigen::VectorXd result(4);
        result << metrics_["variance"], metrics_["peak_to_peak"],
                  metrics_["zcr"], metrics_["spectral_entropy"];
        return result;
    }

private:
    double fs_;
    std::unordered_map<std::string, double> metrics_;

    double compute_spectral_entropy(const Eigen::VectorXd& signal) {
        // Compute PSD via autocorrelation
        Eigen::VectorXd acf = signal.array().autocorr();
        Eigen::VectorXd psd = acf.head(signal.size() / 2).cwiseAbs2();

        // Normalize to probability
        double sum = psd.sum();
        if (sum < 1e-10) return 0.0;
        psd /= sum;

        // Shannon entropy
        double entropy = 0.0;
        for (int i = 0; i < psd.size(); ++i) {
            if (psd(i) > 1e-10) entropy -= psd(i) * std::log2(psd(i));
        }
        return entropy / std::log2(psd.size());  // Normalized
    }
};