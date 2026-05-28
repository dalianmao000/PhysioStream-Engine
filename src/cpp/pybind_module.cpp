// src/cpp/pybind_module.cpp
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include "ring_buffer.h"
#include "adaptive_filter.h"
#include "signal_quality.h"
#include "featureExtractor.h"

namespace py = pybind11;

PYBIND11_MODULE(physio_cpp, m) {
    m.doc() = "PhysioStream-Engine: High-performance physiological signal processing";

    // RingBuffer
    py::class_<RingBuffer<8, 1024>>(m, "RingBuffer")
        .def(py::init<double>())
        .def("push", &RingBuffer<8, 1024>::push)
        .def("get_window", &RingBuffer<8, 1024>::get_window)
        .def("size", &RingBuffer<8, 1024>::size);

    // AdaptiveFilter
    py::class_<AdaptiveFilter>(m, "AdaptiveFilter")
        .def(py::init<double, int, double>())
        .def("filter", &AdaptiveFilter::filter)
        .def("reset", &AdaptiveFilter::reset);

    // SignalQuality
    py::class_<SignalQuality>(m, "SignalQuality")
        .def(py::init<double>())
        .def("compute_score", &SignalQuality::compute_score)
        .def("get_metrics", &SignalQuality::get_metrics);

    // FeatureExtractor
    py::class_<FeatureExtractor>(m, "FeatureExtractor")
        .def(py::init<double>())
        .def("extract_time_domain", &FeatureExtractor::extract_time_domain)
        .def("extract_frequency_domain", &FeatureExtractor::extract_frequency_domain)
        .def("extract_nonlinear", &FeatureExtractor::extract_nonlinear);
}