# src/python/api_server.py
import asyncio
import json
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import numpy as np
import sys
sys.path.insert(0, '/Users/yinjili/p10_NeuraHeal_v3/physio-stream-engine/src/python')

from signal_processor import SignalProcessor
from feature_pipeline import FeaturePipeline

app = FastAPI(title="PhysioStream-Engine API")

# Initialize processing pipeline
processor = SignalProcessor(eeg_channels=8, imu_channels=6, sample_rate=250.0)
feature_pipeline = FeaturePipeline(sample_rate=250.0)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/physio_stream")
async def websocket_physio(websocket: WebSocket):
    """
    WebSocket endpoint for real-time physiological signal streaming.

    Expected incoming message format:
    {
        "eeg": [[sample0_ch0, ...], [sample1_ch0, ...], ...],  # 2D array
        "imu": [[sample0_ch0, ...], [sample1_ch0, ...], ...],
        "timestamp": 1234567890.123
    }

    Outgoing message format:
    {
        "quality_score": 0.85,
        "features": {...},
        "state": "relaxed",
        "inference_ms": 12.5
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            eeg = np.array(data['eeg'])
            imu = np.array(data['imu'])

            # Process through pipeline
            import time
            start = time.time()
            features = processor.process(eeg, imu)
            state = feature_pipeline.compute_physio_state(features['eeg_band_powers'])
            inference_ms = (time.time() - start) * 1000

            response = {
                "quality_score": features['eeg_quality_score'],
                "features": {
                    "band_powers": features['eeg_band_powers'],
                    "peak_freq": features['peak_freq'],
                    "imu": features['imu_features']
                },
                "state": state,
                "inference_ms": round(inference_ms, 2)
            }

            # Send back to client
            await websocket.send_json(response)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "pipeline": "physio_stream_engine"}