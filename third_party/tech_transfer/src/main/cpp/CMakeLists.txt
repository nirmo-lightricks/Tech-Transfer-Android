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
set(LT_OPENCV_LIB_DIR ${LT_OPENCV_HOME}/sdk/native/libs/${ANDROID_ABI})
add_library(opencv_java4 SHARED IMPORTED)
set_target_properties(
    opencv_java4
    PROPERTIES
    IMPORTED_LOCATION
    ${LT_OPENCV_LIB_DIR}/libopencv_java4.so
)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${LT_OPENCV_HOME}/sdk/native/jni/include
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
    opencv_java4
)

include(../../androidTest/cppTests/CMakeLists.txt)

