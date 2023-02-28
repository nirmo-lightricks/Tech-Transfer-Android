# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Nir Moshe.

cmake_minimum_required(VERSION 3.4.1)

set(MODULE_NAME tech_transfer_neural_network)

# Configure CCache if available
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CCACHE_FOUND}")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
endif()

macro(create_fake_target target_name so_file)
    # Specify the location of the .so file to replace the shared library
    set(FILE_TO_COPY ${so_file})
    add_library(${target_name} SHARED dummy.cpp)

    # Check if the .so file exists
    if(EXISTS ${FILE_TO_COPY})
        message("Using .so file: ${FILE_TO_COPY}")
        add_custom_command(TARGET ${target_name} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy ${FILE_TO_COPY} $<TARGET_FILE:${target_name}>
                )
    else()
        message(FATAL_ERROR "Can't find file ${FILE_TO_COPY}!")
    endif()
endmacro()

find_package(opencv_android REQUIRED CONFIG)

set(LT_TFLITE_HOME ${CMAKE_CURRENT_SOURCE_DIR}/tensorflow-lite)

###################################### tflite_cpp ######################################
set(TENSORFLOW_JNI ${LT_TFLITE_HOME}/jni/${ANDROID_ABI}/libtensorflowlite_jni.so)

add_library(tflite_cpp SHARED IMPORTED)
set_target_properties(
    tflite_cpp
    PROPERTIES
    IMPORTED_LOCATION
    ${TENSORFLOW_JNI}
)

create_fake_target(tensorflowlite_jni ${TENSORFLOW_JNI})

###################################### tflite_cpp_gpu ######################################
set(TENSORFLOW_GPU_JNI ${LT_TFLITE_HOME}/jni/${ANDROID_ABI}/libtensorflowlite_gpu_jni.so)

add_library(tflite_cpp_gpu SHARED IMPORTED)
set_target_properties(
    tflite_cpp_gpu
    PROPERTIES
    IMPORTED_LOCATION
    ${TENSORFLOW_GPU_JNI}
)

create_fake_target(tensorflowlite_gpu_jni ${TENSORFLOW_GPU_JNI})

###################################### tech_transfer ######################################

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${LT_TFLITE_HOME}/headers
)

file(GLOB_RECURSE LT_TECH_TRANSFER_CPP_SOURCES "*.cpp")

add_library(
    ${MODULE_NAME}
    SHARED
    ${LT_TECH_TRANSFER_CPP_SOURCES}
)


target_compile_options(
    ${MODULE_NAME}
    PRIVATE
    -fvisibility-inlines-hidden -Wall -Wno-unknown-pragmas -std=c++17 ${CPP_OPTIMIZATION_FLAG}
    -Wno-inconsistent-missing-override
)

target_link_libraries(
        ${MODULE_NAME}
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
