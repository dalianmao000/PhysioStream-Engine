# PhysioStream-Engine

> High-performance streaming engine for multi-modal physiological signal processing

[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)]()

## Overview

**PhysioStream-Engine** is a research-grade open-source framework for real-time processing of multi-modal physiological signals (EEG, EMG, ECG, IMU). It provides a hybrid C++/Python architecture optimized for low-latency streaming applications at the edge.

### Core Capabilities

- **Hardware Abstraction**: BrainFlow integration for consumer-grade biosensing devices
- **Adaptive Motion Artifact Removal**: IMU-assisted LMS/RLS filtering
- **Real-time Signal Quality Assessment**: Multi-metric quality scoring with pass/fail thresholds
- **Feature Extraction**: Time-domain, frequency-domain (band powers), and nonlinear features
- **Downstream Task Interface**: Standardized feature vectors for ML classifiers
- **Edge Deployment**: C++ core with Python bindings, Docker-ready

## Architecture

```
[Sensor Devices]
       ↓
[BrainFlow Acquisition]
       ↓
┌─────────────────┐
│  C++ Core Layer │  ← Ring buffer, adaptive filter, SQA, feature extraction
│  (Eigen/FFTW)   │
└────────┬────────┘
         │ pybind11
┌────────▼────────┐
│ Python Business │  ← SignalProcessor, FeaturePipeline, downstream models
│    Layer        │
└────────┬────────┘
         │ gRPC/WebSocket
┌────────▼────────┐
│   API Server    │  ← FastAPI + WebSocket streaming
└─────────────────┘
```

## Quick Start

```bash
# Build C++ extension
bash scripts/build_cpp.sh

# Run with Docker
docker-compose up -d

# Or run locally
pip install -r requirements.txt
uvicorn src.python.api_server:app --reload
```

## Technical Details

### Adaptive Filtering
Uses LMS (Least Mean Squares) adaptive filter with IMU magnitude as reference signal to suppress motion artifacts in EEG/ECG channels. Filter length and learning rate are configurable.

### Signal Quality Assessment
Composite scoring based on: variance, dynamic range, zero-crossing rate, spectral entropy. Threshold-based gating prevents low-quality data from propagating to downstream tasks.

### Feature Extraction
- **Time-domain**: RMS, MAV, zero-crossing rate, variance
- **Frequency-domain**: Band powers (delta/theta/alpha/beta), peak frequency, spectral entropy
- **Nonlinear**: Sample entropy proxy

## Use Cases

This framework is designed for research in:
- Brain-computer interfaces (BCI)
- Physiological computing for human-computer interaction
- Digital health and wellness monitoring
- Motor rehabilitation assistance systems

## Disclaimer

**RESEARCH AND EDUCATIONAL PURPOSES ONLY.** This is not a medical device and is not intended for clinical diagnosis or treatment.