// src/cpp/featureExtractor.h
#pragma once
#include <Eigen/Dense>

class FeatureExtractor {
public:
    FeatureExtractor(double sample_rate);
    Eigen::VectorXd extract_time_domain(const Eigen::MatrixXd& window);
    Eigen::VectorXd extract_frequency_domain(const Eigen::MatrixXd& window);
    Eigen::VectorXd extract_nonlinear(const Eigen::MatrixXd& window);

private:
    double sample_rate_;
};