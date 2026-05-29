# PhysioStream-Engine

> High-performance streaming engine for multi-modal physiological signal processing

[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)]()
[![C++](https://img.shields.io/badge/C++-17-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![Eigen](https://img.shields.io/badge/Eigen-3.4-green.svg)]()
[![FFTW](https://img.shields.io/badge/FFTW-3.3-orange.svg)]()
[![pybind11](https://img.shields.io/badge/pybind11-2.11-orange.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)]()
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)]()

**Tech Stack:** C++17 · Eigen · FFTW · pybind11 · Python 3.10+ · FastAPI · XGBoost · Docker · BrainFlow · scikit-learn

## Overview

**PhysioStream-Engine** is a research-grade open-source framework for real-time processing of multi-modal physiological signals (EEG, EMG, ECG, IMU). It provides a hybrid C++/Python architecture optimized for low-latency streaming applications at the edge.

## Core Capabilities

- **Hardware Abstraction**: BrainFlow integration for consumer-grade biosensing devices
- **Adaptive Motion Artifact Removal**: IMU-assisted LMS/RLS filtering
- **Real-time Signal Quality Assessment**: Multi-metric quality scoring (variance, dynamic range, ZCR, spectral entropy) with threshold gating
- **Feature Extraction**: Time-domain (RMS, MAV, ZCR, variance), frequency-domain (δ/θ/α/β band powers, peak frequency), and nonlinear features (sample entropy)
- **Downstream Task Interface**: Standardized feature vectors for ML classifiers (XGBoost, scikit-learn, PyTorch)
- **Edge Deployment**: C++ core with pybind11 Python bindings, Docker-ready

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
         │ WebSocket
┌────────▼────────┐
│   API Server    │  ← FastAPI + WebSocket streaming
└─────────────────┘
```

## Quick Start

### Prerequisites

```bash
# System dependencies (macOS)
brew install cmake eigen fftw pybind11

# Python dependencies
pip install -r requirements.txt
```

### Build C++ Extension

```bash
git clone https://github.com/your-username/PhysioStream-Engine.git
cd PhysioStream-Engine
bash scripts/build_cpp.sh
```

### Run with Docker

```bash
docker-compose up -d
```

### Run Locally

```bash
pip install -r requirements.txt
uvicorn src.python.api_server:app --host 0.0.0.0 --port 8000 --reload
```

### WebSocket Testing

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/physio_stream');

// Send data
ws.send(JSON.stringify({
    eeg: [[...], [...]],  // [n_samples x n_channels]
    imu: [[...], [...]],
    timestamp: Date.now()
}));

// Receive processed results
ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Quality:', result.quality_score);
    console.log('State:', result.state);
};
```

## Technical Details

### Adaptive Filtering

LMS (Least Mean Squares) adaptive filter uses IMU magnitude as reference signal to suppress motion artifacts in EEG/ECG channels.

```python
from physio_cpp import AdaptiveFilter

adaptive_filter = AdaptiveFilter(sample_rate=250.0, filter_length=64, mu=0.01)
filtered_eeg = adaptive_filter.filter(eeg_signal, imu_magnitude)
```

### Signal Quality Assessment (SQA)

Composite scoring:
- **Variance (30%)**: Signal power
- **Peak-to-peak (30%)**: Dynamic range
- **Zero-crossing rate (20%)**: Signal structure
- **Spectral entropy (20%)**: Frequency domain regularity

### Feature Extraction

| Type | Features |
|------|----------|
| Time-domain | RMS, MAV, zero-crossing rate, variance |
| Frequency-domain | δ/θ/α/β band powers, peak frequency, spectral entropy |
| Nonlinear | Sample entropy proxy |

## Project Structure

```
physio-stream-engine/
├── src/
│   ├── cpp/                    # C++ core modules
│   │   ├── ring_buffer.h      # Multi-source timestamp alignment
│   │   ├── adaptive_filter.h  # LMS adaptive filtering
│   │   ├── signal_quality.h   # Signal quality assessment
│   │   └── featureExtractor.h # Feature extraction
│   └── python/                # Python business layer
│       ├── signal_processor.py # Processing pipeline
│       ├── feature_pipeline.py # Feature vector conversion
│       ├── downstream_demo.py  # Gesture recognition demo
│       └── api_server.py      # WebSocket API
├── tests/                     # Test suite
├── configs/                   # Configuration files
└── docs/                     # Documentation
```

## Performance Benchmarks

| Module | Latency | Note |
|--------|---------|------|
| Adaptive filter | ~1ms/channel | C++ implementation |
| Feature extraction | ~5ms | Full feature set |
| Gesture classification | <10ms | XGBoost single sample |
| WebSocket E2E | <50ms | Including Python overhead |

## Downstream Demo: sEMG Gesture Recognition

```python
from downstream_demo import GestureClassifier

# Initialize classifier (5 gestures)
clf = GestureClassifier(n_classes=5)

# Train
clf.fit(X_train, y_train)

# Real-time inference
prediction = clf.predict(feature_vector)
```

## Use Cases

This framework is designed for research in:
- Brain-computer interfaces (BCI)
- Physiological computing for human-computer interaction
- Digital health and wellness monitoring
- Motor rehabilitation assistance systems

## Disclaimer

**RESEARCH AND EDUCATIONAL PURPOSES ONLY.** This is not a medical device and is not intended for clinical diagnosis or treatment. Users are responsible for complying with local data privacy regulations (e.g., HIPAA, GDPR) regarding the collection and processing of biometric and physiological data.

## Contributing

Issues and Pull Requests are welcome!

## License

This project is licensed under the Apache 2.0 License.
