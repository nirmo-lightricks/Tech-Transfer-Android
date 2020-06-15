//
// Created by Nir Moshe on 12/05/2020.
//

#include <jni.h>
#include "opencv2/core/core.hpp"

#include "ColorTransferProcessor.h"

using namespace lit_color_transfer;

/**
 * Convert C++ into Java exception and throw it.
 *
 * @param env
 * @param exception
 */
static void throwJavaException(JNIEnv *env, const std::exception& exception) {
    jclass errorClass = env->FindClass("java/lang/RuntimeException");
    env->ThrowNew(errorClass, exception.what());
}

extern "C"
JNIEXPORT void JNICALL
Java_com_lightricks_tech_1transfer_color_1transfer_ColorTransferProcessor__1generateLUT(JNIEnv *env, jclass clazz,
                                                                                     jlong inputMat,
                                                                                     jlong referenceMat,
                                                                                     jfloat dampingFactor,
                                                                                     jint iterations,
                                                                                     jint histogramBins,
                                                                                     jlong outputMat) {
    try
    {
        cv::Mat& input = *reinterpret_cast<cv::Mat*>(inputMat);
        cv::Mat& reference = *reinterpret_cast<cv::Mat*>(referenceMat);
        cv::Mat& output = *reinterpret_cast<cv::Mat*>(outputMat);

        ColorTransferProcessor colorTransferProcessor(iterations, histogramBins);
        colorTransferProcessor.generateLUT(input, reference, dampingFactor, &output);
    }
    catch (std::exception& exception)
    {
        throwJavaException(env, exception);
    }
}
