// src/cpp/adaptive_filter.h
#pragma once
#include <Eigen/Dense>
#include <vector>

class AdaptiveFilter {
public:
    AdaptiveFilter(double sample_rate, int filter_length, double mu)
        : fs_(sample_rate), M_(filter_length), mu_(mu), initialized_(false) {
        w_.setZero(M_);
        x_buffer_.resize(M_, 0.0);
    }

    Eigen::VectorXd filter(const Eigen::VectorXd& primary_input,
                           const Eigen::VectorXd& reference_noise) {
        int N = primary_input.size();
        Eigen::VectorXd output(N);

        for (int i = 0; i < N; ++i) {
            // Update circular buffer
            for (int j = M_ - 1; j > 0; --j) x_buffer_[j] = x_buffer_[j-1];
            x_buffer_[0] = reference_noise(i);

            // LMS update
            double y = w_.dot(Eigen::VectorXd(x_buffer_));
            double e = primary_input(i) - y;
            for (int j = 0; j < M_; ++j) w_(j) += mu_ * e * x_buffer_[j];

            output(i) = e;  // Error signal = denoised primary
        }
        return output;
    }

    void reset() { w_.setZero(); }

private:
    double fs_;
    int M_;
    double mu_;
    Eigen::VectorXd w_;
    std::vector<double> x_buffer_;
    bool initialized_;
};