// src/cpp/adaptive_filter.h
#pragma once
#include <Eigen/Dense>

class AdaptiveFilter {
public:
    AdaptiveFilter(double learning_rate, int filter_order, double leakage);
    Eigen::VectorXd filter(const Eigen::VectorXd& input, const Eigen::VectorXd& reference);
    void reset();

private:
    double learning_rate_;
    int filter_order_;
    double leakage_;
    Eigen::VectorXd weights_;
};