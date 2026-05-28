# Architecture Deep Dive

## C++ Core Design Principles

1. **Deterministic Memory**: No heap allocations in real-time processing path. Pre-allocated buffers.
2. **SIMD-friendly**: Eigen library provides vectorized operations.
3. **Lock-free where possible**: Real-time threads avoid mutex contention.

## Python Bindings (pybind11)

All C++ classes are exposed to Python via pybind11 with numpy array conversion.
Eigen::VectorXd ↔ np.ndarray (zero-copy view where possible).

## Processing Pipeline

```
Raw Samples → Ring Buffer → Adaptive Filter → SQA Gate → Feature Extractor → Feature Vector
                                      ↓
                              Quality < 0.6?
                                  ↓ yes
                           Drop / Flag segment
```

## Downstream Integration

Feature vectors are fixed-size arrays designed to plug into scikit-learn, XGBoost, or PyTorch models.