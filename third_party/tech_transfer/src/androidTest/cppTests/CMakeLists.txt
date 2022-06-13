# Build and link tests

# Path to Google Test source dir included into Android NDK.
# Note: Another Google Test implementation can be used.
set(GTEST_DIR ${ANDROID_NDK}/sources/third_party/googletest)

add_library(gtest STATIC ${GTEST_DIR}/src/gtest_main.cc ${GTEST_DIR}/src/gtest-all.cc)
target_include_directories(gtest PRIVATE ${GTEST_DIR})
target_include_directories(gtest PUBLIC ${GTEST_DIR}/include)

set(LT_CPP_TESTS_HOME ${CMAKE_CURRENT_SOURCE_DIR}/../../androidTest/cppTests)
file(GLOB_RECURSE LT_TECH_TRANSFER_TEST_SOURCES "${LT_CPP_TESTS_HOME}/*.cpp")
add_executable(tech_transfer_test
    ${LT_TECH_TRANSFER_TEST_SOURCES}
)

target_link_libraries(tech_transfer_test tech_transfer gtest log jnigraphics z GLESv3 EGL)

set(LT_CPP_TEST_IMAGES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../androidTest/resources/images)

# Push and execute tests as post-build event.
set(TARGET_TEST_DIR /data/local/tmp/tech_transfer_test) # Directory on device to push tests.
set(TARGET_TEST_LIB_DIR ${TARGET_TEST_DIR}/${ANDROID_ABI})
set(TARGET_TEST_IMAGES_DIR ${TARGET_TEST_DIR}/images)

set(STANDARD_LIB_DIR ${ANDROID_NDK}/sources/cxx-stl/llvm-libc++/libs/${ANDROID_ABI})

find_program(ADB NAMES adb PATHS ${ANDROID_SDK_ROOT}/platform-tools)

#Check if the build arch matches the platform arch
execute_process(COMMAND ${ADB} shell getprop ro.product.cpu.abi OUTPUT_VARIABLE PLATFORM_ARCH
        OUTPUT_STRIP_TRAILING_WHITESPACE)

if(PLATFORM_ARCH STREQUAL ANDROID_ABI)
    add_custom_command(TARGET tech_transfer_test POST_BUILD
        # Push libraries
        COMMAND ${ADB} shell mkdir -p ${TARGET_TEST_LIB_DIR}
        COMMAND ${ADB} push $<TARGET_FILE:tech_transfer_test> $<TARGET_FILE:tech_transfer>
            ${LT_OPENCV_LIB_DIR}/libopencv_java4.so ${STANDARD_LIB_DIR}/libc++_shared.so
            ${LT_TFLITE_HOME}/jni/${ANDROID_ABI}/libtensorflowlite_jni.so
            ${LT_TFLITE_HOME}/jni/${ANDROID_ABI}/libtensorflowlite_gpu_jni.so ${TARGET_TEST_LIB_DIR}/

        # Push images
        COMMAND ${ADB} shell mkdir -p ${TARGET_TEST_IMAGES_DIR}
        COMMAND ${ADB} push ${LT_CPP_TEST_IMAGES_DIR}/*.png ${TARGET_TEST_IMAGES_DIR}/

        # Execute tests
        COMMAND ${ADB} shell \"export LD_LIBRARY_PATH=${TARGET_TEST_LIB_DIR}\;
            export TEST_IMAGES_DIR=${TARGET_TEST_IMAGES_DIR}\;
            ${TARGET_TEST_LIB_DIR}/tech_transfer_test\"
    )
endif()
