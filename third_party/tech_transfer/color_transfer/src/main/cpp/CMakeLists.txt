# Copyright (c) 2023 Lightricks. All rights reserved.
# Created by Nir Moshe.

cmake_minimum_required(VERSION 3.4.1)

set(MODULE_NAME tech_transfer_color_transfer)

# Configure CCache if available
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CCACHE_FOUND}")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
endif()

find_package(opencv_android REQUIRED CONFIG)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_library(${MODULE_NAME}
        SHARED
        color_transfer/ColorTransfer_jni.cpp
        color_transfer/ColorTransferProcessor.cpp
)

target_compile_options(${MODULE_NAME}
    PRIVATE
    -fvisibility-inlines-hidden -Wall -Wno-unknown-pragmas -std=c++17 -Wno-inconsistent-missing-override
)

target_link_libraries(${MODULE_NAME}
    opencv_android::opencv_java4
    android
    camera2ndk
    mediandk
    z
    log
)
