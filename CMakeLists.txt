cmake_minimum_required(VERSION 3.15)
project(physio_stream_engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(Eigen3 REQUIRED)
find_package(FFTW REQUIRED)
find_package(pybind11 REQUIRED)

# Source files
set(SOURCES
    src/cpp/ring_buffer.h
    src/cpp/adaptive_filter.h
    src/cpp/signal_quality.h
    src/cpp/featureExtractor.h
    src/cpp/pybind_module.cpp
)

# Build shared library
pybind11_add_module(physio_cpp src/cpp/pybind_module.cpp)
target_include_directories(physio_cpp PRIVATE ${EIGEN3_INCLUDE_DIR} ${FFTW_INCLUDE_DIRS})
target_link_libraries(physio_cpp Eigen3::Eigen ${FFTW_LIBRARIES})

# Install targets
install(TARGETS physio_cpp LIBRARY DESTINATION lib)