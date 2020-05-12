# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Nir Moshe.

cmake_minimum_required(VERSION 3.4.1)

# Path to pre-built opencv installation
set(LT_OPENCV_HOME ${CMAKE_CURRENT_SOURCE_DIR}/../../../../opencv-android)
add_library(opencv_java3 SHARED IMPORTED)
set_target_properties(
    opencv_java3
    PROPERTIES
    IMPORTED_LOCATION
    ${LT_OPENCV_HOME}/sdk/native/libs/${ANDROID_ABI}/libopencv_java3.so
)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${LT_OPENCV_HOME}/sdk/native/jni/include
    ${LT_PROTOBUF_HOME}/include
)

add_library(
    tt
    SHARED

    ColorTransferProcessor.cpp
)

target_compile_options(
    tt
    PRIVATE
    -fvisibility=hidden -fvisibility-inlines-hidden -Wall -Wno-unknown-pragmas -std=c++17 -O3
    -Wno-inconsistent-missing-override
)

target_link_libraries(
    tt
    opencv_java3
)
