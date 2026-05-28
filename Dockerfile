# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libfftw3-dev \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and build C++ extension
COPY CMakeLists.txt src/cpp/ ./
COPY src/cpp/*.h src/cpp/*.cpp ./

RUN mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    cd .. && \
    cp build/*.so app/ || true

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source
COPY src/python ./src/python
COPY configs ./configs

# Set environment
ENV PYTHONPATH=/app

CMD ["uvicorn", "src.python.api_server:app", "--host", "0.0.0.0", "--port", "8000"]