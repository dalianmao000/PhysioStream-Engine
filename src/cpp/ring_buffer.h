// src/cpp/ring_buffer.h
#pragma once
#include <vector>
#include <array>
#include <cmath>
#include <Eigen/Dense>

template<size_t NumChannels, size_t BufferSize = 1024>
class RingBuffer {
public:
    RingBuffer(double sample_rate) : sample_rate_(sample_rate) {
        buffer_.setZero();
        timestamps_.setZero();
        write_idx_ = 0;
    }

    void push(const Eigen::VectorXd& data, double timestamp) {
        buffer_.row(write_idx_) = data;
        timestamps_(write_idx_) = timestamp;
        write_idx_ = (write_idx_ + 1) % BufferSize;
    }

    Eigen::MatrixXd get_window(double start_time, double end_time) {
        int start_idx = static_cast<int>((start_time - timestamps_(0)) * sample_rate_);
        int end_idx = static_cast<int>((end_time - timestamps_(0)) * sample_rate_);
        // Return interpolated window using spline
        return interpolate_window(start_idx, end_idx);
    }

    size_t size() const { return BufferSize; }

private:
    Eigen::MatrixXd buffer_;          // [NumChannels x BufferSize]
    Eigen::VectorXd timestamps_;      // [BufferSize]
    size_t write_idx_;
    double sample_rate_;

    Eigen::MatrixXd interpolate_window(int start, int end);
};

template<size_t NumChannels, size_t BufferSize>
Eigen::MatrixXd RingBuffer<NumChannels, BufferSize>::interpolate_window(int start, int end) {
    size_t len = std::min(end - start, static_cast<int>(BufferSize));
    Eigen::MatrixXd result(NumChannels, len);
    for (size_t i = 0; i < len; ++i) {
        float alpha = static_cast<float>(i) / len;
        int idx0 = (start + i) % BufferSize;
        int idx1 = (start + i + 1) % BufferSize;
        result.col(i) = buffer_.col(idx0) * (1 - alpha) + buffer_.col(idx1) * alpha;
    }
    return result;
}