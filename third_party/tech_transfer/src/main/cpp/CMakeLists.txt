# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Nir Moshe.

cmake_minimum_required(VERSION 3.4.1)

# Configure CCache if available
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CCACHE_FOUND}")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
endif()


find_package(opencv_android REQUIRED CONFIG)

set(LT_TFLITE_HOME ${CMAKE_CURRENT_SOURCE_DIR}/../../../../tensorflow-lite)

add_library(tflite_cpp SHARED IMPORTED)
set_target_properties(
    tflite_cpp
    PROPERTIES
    IMPORTED_LOCATION
    ${LT_TFLITE_HOME}/jni/${ANDROID_ABI}/libtensorflowlite_jni.so
)

add_library(tflite_cpp_gpu SHARED IMPORTED)
set_target_properties(
    tflite_cpp_gpu
    PROPERTIES
    IMPORTED_LOCATION
    ${LT_TFLITE_HOME}/jni/${ANDROID_ABI}/libtensorflowlite_gpu_jni.so
)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${LT_TFLITE_HOME}/headers
    ${LT_PROTOBUF_HOME}/include
)

file(GLOB_RECURSE LT_TECH_TRANSFER_CPP_SOURCES "*.cpp")

add_library(
    tech_transfer
    SHARED
    ${LT_TECH_TRANSFER_CPP_SOURCES}
)

if(CMAKE_BUILD_TYPE MATCHES Debug)
    set(CPP_OPTIMIZATION_FLAG "-O0")
else()
    set(CPP_OPTIMIZATION_FLAG "-O3")
endif()

target_compile_options(
    tech_transfer
    PRIVATE
    -fvisibility-inlines-hidden -Wall -Wno-unknown-pragmas -std=c++17 ${CPP_OPTIMIZATION_FLAG}
    -Wno-inconsistent-missing-override
)

target_link_libraries(
    tech_transfer
        opencv_android::opencv_java4
        android
        camera2ndk
        mediandk
        z
    tflite_cpp
    tflite_cpp_gpu
    log
    GLESv2
)

include(../../androidTest/cppTests/CMakeLists.txt)
