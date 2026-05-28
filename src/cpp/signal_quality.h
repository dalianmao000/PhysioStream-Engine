// src/cpp/signal_quality.h
#pragma once
#include <Eigen/Dense>

class SignalQuality {
public:
    SignalQuality(double sample_rate);
    double compute_score(const Eigen::MatrixXd& data);
    Eigen::VectorXd get_metrics() const;

private:
    double sample_rate_;
    double snr_;
    double correlation_;
};