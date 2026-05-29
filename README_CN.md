# PhysioStream-Engine

> 多模态生理信号处理的高性能流式引擎

[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)]()
[![C++](https://img.shields.io/badge/C++-17-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![Eigen](https://img.shields.io/badge/Eigen-3.4-green.svg)]()
[![FFTW](https://img.shields.io/badge/FFTW-3.3-orange.svg)]()
[![pybind11](https://img.shields.io/badge/pybind11-2.11-orange.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)]()
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)]()

**技术栈：** C++17 · Eigen · FFTW · pybind11 · Python 3.10+ · FastAPI · XGBoost · Docker · BrainFlow · scikit-learn

## 概述

**PhysioStream-Engine** 是一个研究级开源框架，用于多模态生理信号（脑电 EEG、肌电 EMG、心电 ECG、惯性测量单元 IMU）的实时处理。采用混合 C++/Python 架构，针对边缘设备上的低延迟流式应用进行了优化。

## 核心功能

- **硬件抽象层**：支持 BrainFlow 集成，可接入消费级生物传感设备
- **自适应运动伪影去除**：基于 IMU 辅助的 LMS/RLS 自适应滤波
- **实时信号质量评估**：多指标质量评分（方差、动态范围、过零率、频谱熵），带阈值门控
- **特征提取**：
  - 时域：RMS、MAV、过零率、方差
  - 频域：δ/θ/α/β 频段功率、峰值频率、频谱熵
  - 非线性：近似熵
- **下游任务接口**：标准化特征向量，支持 XGBoost、scikit-learn、PyTorch 模型
- **边缘部署就绪**：C++ 核心 + pybind11 Python 绑定，Docker 容器化

## 系统架构

```
[传感器设备]
       ↓
[BrainFlow 数据采集]
       ↓
┌─────────────────┐
│  C++ 核心层      │  ← 环形缓冲区、自适应滤波、SQA、特征提取
│  (Eigen/FFTW)   │
└────────┬────────┘
         │ pybind11
┌────────▼────────┐
│  Python 业务层   │  ← SignalProcessor、FeaturePipeline、下游模型
└────────┬────────┘
         │ WebSocket
┌────────▼────────┐
│   API 服务器     │  ← FastAPI + WebSocket 流式传输
└─────────────────┘
```

## 快速开始

### 前置依赖

```bash
# 系统依赖 (macOS)
brew install cmake eigen fftw pybind11

# Python 依赖
pip install -r requirements.txt
```

### 构建 C++ 扩展

```bash
# 克隆项目
git clone https://github.com/your-username/PhysioStream-Engine.git
cd PhysioStream-Engine

# 构建 C++ 扩展
bash scripts/build_cpp.sh
```

### 使用 Docker 运行

```bash
docker-compose up -d
```

### 本地运行

```bash
pip install -r requirements.txt
uvicorn src.python.api_server:app --host 0.0.0.0 --port 8000 --reload
```

### WebSocket 测试

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/physio_stream');

// 发送数据
ws.send(JSON.stringify({
    eeg: [[...], [...]],  // [样本数 x 通道数]
    imu: [[...], [...]],
    timestamp: Date.now()
}));

// 接收处理结果
ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('质量评分:', result.quality_score);
    console.log('生理状态:', result.state);
};
```

## 技术细节

### 自适应滤波

使用 LMS（最小均方）自适应滤波器，以 IMU 幅值作为参考信号，抑制 EEG/ECG 通道中的运动伪影。

```python
from physio_cpp import AdaptiveFilter

adaptive_filter = AdaptiveFilter(sample_rate=250.0, filter_length=64, mu=0.01)
filtered_eeg = adaptive_filter.filter(eeg_signal, imu_magnitude)
```

### 信号质量评估 (SQA)

组合评分权重：
- **方差 (30%)**：信号功率
- **峰峰值 (30%)**：动态范围
- **过零率 (20%)**：信号结构
- **频谱熵 (20%)**：频域规律性

### 特征提取

| 类型 | 特征 |
|------|------|
| 时域 | RMS、MAV、过零率、方差 |
| 频域 | δ/θ/α/β 频段功率、峰值频率、频谱熵 |
| 非线性 | 近似熵 |

## 项目结构

```
physio-stream-engine/
├── src/
│   ├── cpp/                    # C++ 核心模块
│   │   ├── ring_buffer.h      # 多源时间戳对齐
│   │   ├── adaptive_filter.h  # LMS 自适应滤波
│   │   ├── signal_quality.h   # 信号质量评估
│   │   └── featureExtractor.h # 特征提取
│   └── python/                # Python 业务层
│       ├── signal_processor.py # 处理流水线
│       ├── feature_pipeline.py # 特征向量转换
│       ├── downstream_demo.py  # 手势识别示例
│       └── api_server.py      # WebSocket API
├── tests/                     # 测试套件
├── configs/                   # 配置文件
└── docs/                     # 文档
```

## 性能基准

| 模块 | 延迟 | 说明 |
|------|------|------|
| 自适应滤波 | ~1ms/通道 | C++ 实现 |
| 特征提取 | ~5ms | 全特征集 |
| 手势分类推理 | <10ms | XGBoost 单样本 |
| WebSocket 端到端 | <50ms | 含 Python 开销 |

## 下游任务示例：肌电手势识别

```python
from downstream_demo import GestureClassifier

# 初始化分类器（5 种手势）
clf = GestureClassifier(n_classes=5)

# 训练
clf.fit(X_train, y_train)

# 实时推理
prediction = clf.predict(feature_vector)
```

## 应用场景

本框架设计用于以下研究领域：
- 脑机接口（BCI）
- 生理计算与人机交互
- 数字健康与健康监测
- 运动康复辅助系统

## 免责声明

**仅供研究和教育目的使用。** 本项目不是医疗器械，不适用于临床诊断或治疗。使用者需自行确保符合当地关于生物特征数据收集和处理的数据隐私法规（如 HIPAA、GDPR）。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目基于 Apache 2.0 许可证开源。
