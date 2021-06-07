# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Nir Moshe.

cmake_minimum_required(VERSION 3.4.1)

# Configure CCache if available
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CCACHE_FOUND}")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
endif()

# Path to pre-built opencv installation
set(LT_OPENCV_HOME ${CMAKE_CURRENT_SOURCE_DIR}/../../../../opencv-android)
add_library(opencv_java4 SHARED IMPORTED)
set_target_properties(
    opencv_java4
    PROPERTIES
    IMPORTED_LOCATION
    ${LT_OPENCV_HOME}/sdk/native/libs/${ANDROID_ABI}/libopencv_java4.so
)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${LT_OPENCV_HOME}/sdk/native/jni/include
    ${LT_PROTOBUF_HOME}/include
)

add_library(
    tech_transfer
    SHARED

    ColorTransferProcessor.cpp
    ColorTransfer_jni.cpp
)

target_compile_options(
    tech_transfer
    PRIVATE
    -fvisibility=hidden -fvisibility-inlines-hidden -Wall -Wno-unknown-pragmas -std=c++17 -O3
    -Wno-inconsistent-missing-override
)

target_link_libraries(
    tech_transfer
    opencv_java4
)
