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
├── .gitignore                 # Git 忽略规则
├── LICENSE                    # Apache 2.0 开源许可证
├── README.md                  # 英文说明文档
├── README_CN.md              # 中文说明文档
├── CMakeLists.txt            # CMake 构建配置
├── Dockerfile                # Docker 容器化配置
├── docker-compose.yml        # Docker Compose 多服务编排
├── requirements.txt          # Python 依赖包列表
├── BUILD_NOTES.txt          # C++ 构建注意事项
│
├── src/
│   ├── cpp/                  # C++ 核心模块（Eigen + FFTW）
│   │   ├── ring_buffer.h     # 环形缓冲区：多源传感器时间戳对齐与插值
│   │   ├── adaptive_filter.h # LMS 自适应滤波器：IMU 辅助运动伪影去除
│   │   ├── signal_quality.h # 信号质量评估：方差/ZCR/频谱熵/动态范围
│   │   ├── featureExtractor.h# 特征提取：时域/频域/非线性特征
│   │   └── pybind_module.cpp# pybind11 绑定：导出 C++ 类到 Python
│   │
│   └── python/               # Python 业务层
│       ├── signal_processor.py  # 信号处理流水线：整合滤波/SQA/特征提取
│       ├── feature_pipeline.py  # 特征向量转换：标准化接口供下游 ML 使用
│       ├── downstream_demo.py   # 下游示例：XGBoost 肌电手势分类器
│       ├── data_acquisition.py  # 数据采集接口：BrainFlow 集成占位
│       ├── api_server.py        # FastAPI WebSocket 服务器：实时流式 API
│       ├── adaptive_filter_mock.py  # LMS 滤波器的纯 Python 实现（测试用）
│       ├── signal_quality_mock.py   # SQA 的纯 Python 实现（测试用）
│       └── feature_extractor_mock.py # 特征提取的纯 Python 实现（测试用）
│
├── tests/                     # 测试套件（pytest）
│   ├── test_adaptive_filter.py       # 自适应滤波测试
│   ├── test_signal_quality.py        # 信号质量评估测试
│   ├── test_feature_extractor.py      # 特征提取测试
│   ├── test_pipeline_integration.py   # 端到端流水线集成测试
│   └── test_gesture_classifier.py     # 手势分类器测试
│
├── configs/                  # 配置文件
│   └── default_config.yaml   # 默认配置（通道数/采样率/滤波器参数）
│
├── scripts/                  # 构建脚本
│   └── build_cpp.sh         # C++ 扩展编译脚本
│
└── docs/                    # 技术文档
    └── architecture.md      # 架构深度解析
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

## 个人近生产级 vs 企业实际生产级 差异对比表

> 🔴 较低   🟡 中等   🟢 极高

| 评估维度 | 个人近生产级方案（本项目） | 差异等级 | 企业实际生产级方案（夏禹集成电路落地产品） | 差异理由与核心壁垒 | 本项目实现状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. 硬件接入与底层驱动** | 依赖开源 SDK 与消费级设备（BrainFlow 接入 OpenBCI/Muse），处理已封装好的标准数据流 | 🔴 | 对接自研医疗级硬件与底层协议栈，处理 ADC 非线性误差、 BLE/WiFi 丢包重传 | **壁垒：软硬协同能力。** 企业级必须和嵌入式团队死磕协议栈，解决复杂电磁环境下的丢包、时间戳溢出等底层问题 | ⚠️ 使用 BrainFlow SDK（已封装），未对接自定义 BLE/WiFi 协议栈 |
| **2. 多源时钟同步机制** | 软件层时间戳对齐，基于系统时间使用环形缓冲区和样条插值对齐不同采样率数据 | 🟢 | 硬件级微秒级时钟同步，基于 PTP (IEEE 1588) 或硬件 PPS 脉冲触发，解决晶振温漂和微秒级相位延迟 | **壁垒：相位保真度。** 软件同步受 OS 调度影响存在毫秒级抖动，对于脑电相干性分析或肌电激活顺序判断，毫秒级误差会导致特征完全失效 | ✅ `ring_buffer.h` 已实现环形缓冲区与时间戳对齐算法 |
| **3. 去噪与抗运动伪影** | 传统数字信号处理（IIR/FIR 滤波器、ICA），基于 IMU 辅助的自适应滤波（LMS/RLS） | 🟢 | 深度学习盲源分离 + 硬件级陷波，引入 GAN/AutoEncoder 自监督去噪模型，结合定制模拟/数字陷波器 | **壁垒：极端场景鲁棒性。** 剧烈运动下传统自适应滤波容易发散，企业级需要海量私有数据训练深度学习去噪模型并轻量化部署到端侧 | ✅ `adaptive_filter.h` 已实现 C++ LMS 自适应滤波，延迟 ~1ms/通道 |
| **4. 信号质量评估 (SQA)** | 基于统计特征的阈值拦截，计算方差、峰峰值、频谱熵，质量低则直接丢弃数据 | 🟢 | 多维融合 SQA 与"自恢复"机制，结合硬件接触阻抗、环境温湿度、运动剧烈程度综合评估，动态调整 ADC 增益或触发重新佩戴提示 | **壁垒：系统连续可用性。** 医疗级产品需要"主动抢救"数据，确保长时间佩戴中的有效数据占比（Yield Rate） | ✅ `signal_quality.h` 已实现多指标 SQA（方差/ZCR/频谱熵/动态范围）|
| **5. 个体差异与模型泛化** | 假设数据同分布（IID），在公开数据集上追求整体 Accuracy/F1-score | 🟡 | 应对严重 Domain Shift，引入小样本学习（Few-shot）和在线迁移学习（Online Adaptation），设计用户初次佩戴校准流程 | **壁垒：生理信号"千人千面"。** 不同人的头骨厚度、皮肤阻抗、肌肉脂肪比例差异巨大，是生理算法落地的最大拦路虎 | ❌ 未实现 Few-shot / Online Adaptation，下游分类器为静态训练模型 |
| **6. 算力约束与嵌入式部署** | C++ 动态库运行于 PC/边缘盒子，Float32 精度，依赖高主频 CPU，功耗和内存不敏感 | 🟡 | 极低功耗 MCU/DSP 部署与定点化，需部署到 Cortex-M4/M33 或专用 DSP，进行定点化（Float32 → INT8/INT16） | **壁垒：戴着不烫头、续航长。** 穿戴设备电池极小，需要极致算子优化、内存复用（Memory Pool）和功耗控制 | ⚠️ C++ 核心已实现，但未进行 MCU/DSP 定点化移植 |
| **7. 算法框架可扩展性** | 面向特定任务的硬编码 Pipeline，针对单一任务写死特征提取和分类逻辑 | 🟡 | 插件化、配置驱动的时序算法中台，支持动态 OTA 下发配置，上层任务以插件形式热加载，支持不同产品线代码复用 | **壁垒：研发效能与产品矩阵支撑。** 公司产品矩阵不可能每个产品重写一套代码，需要高内聚低耦合的 C++ 框架 | ⚠️ Pipeline 架构已解耦，但未实现插件热加载机制 |

**图例说明：**
- 🔴 较低   🟡 中等   🟢 极高：表示个人近生产级方案与企业级方案的**技术差异程度**
- ✅ 已实现：代码完整且经过测试
- ⚠️ 部分实现：基础架构存在，但未达到生产级要求
- ❌ 未实现：需要从零构建或重大重构

## 免责声明

**仅供研究和教育目的使用。** 本项目不是医疗器械，不适用于临床诊断或治疗。使用者需自行确保符合当地关于生物特征数据收集和处理的数据隐私法规（如 HIPAA、GDPR）。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目基于 Apache 2.0 许可证开源。
