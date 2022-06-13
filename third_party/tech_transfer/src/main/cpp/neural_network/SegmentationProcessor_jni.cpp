#include <exception>
#include <jni.h>

#include "SegmentationProcessor.h"

static void throwJavaException(JNIEnv *env, const std::exception& exception) {
    jclass errorClass = env->FindClass("java/lang/RuntimeException");
    env->ThrowNew(errorClass, exception.what());
}

static cv::Size cppSizeFromJavaSize(JNIEnv *env, jobject javaSize) {
    jclass sizeClass = env->GetObjectClass(javaSize);

    jfieldID widthId = env->GetFieldID(sizeClass, "width", "D");
    jdouble inputWidth  = env->GetDoubleField(javaSize, widthId);

    jfieldID heightId = env->GetFieldID(sizeClass, "height", "D");
    jdouble inputHeight  = env->GetDoubleField(javaSize, heightId);

    return cv::Size((int)std::lround(inputWidth), (int)std::lround(inputHeight));
}

static jintArray javaArrayFromCppVector(JNIEnv *env, const std::vector<int> &cppVector) {
    jintArray javaArray = env->NewIntArray(cppVector.size());

    jint* javaArrayAsCppArray = env->GetIntArrayElements(javaArray, NULL);
    for (size_t i = 0; i < cppVector.size(); ++i) {
        javaArrayAsCppArray[i] = cppVector[i];
    }
    env->ReleaseIntArrayElements(javaArray, javaArrayAsCppArray, 0);

    return javaArray;
}

static jobject javaMatFromCppMat(JNIEnv *env, const cv::Mat *cppMat) {
    jclass matClass = env->FindClass("org/opencv/core/Mat");
    jmethodID constructor = env->GetMethodID(matClass, "<init>", "(J)V");
    return env->NewObject(matClass, constructor, (long)cppMat);
}

extern "C" JNIEXPORT jlong JNICALL
Java_com_lightricks_tech_1transfer_neural_1network_SegmentationProcessor__1createNativeSegmentationProcessor(
        JNIEnv *env, jclass clazz, jobject model_binary, jobject metadata, jint computeUnit) {
    try {
      auto ptrToModelBuffer = env->GetDirectBufferAddress(model_binary);
      auto modelBufferCapacity = env->GetDirectBufferCapacity(model_binary);
      auto ptrToMetadataBuffer = env->GetDirectBufferAddress(metadata);
      auto cppComputeUnit = (ComputeUnit)computeUnit;

      return (jlong)(new neural_network::SegmentationProcessor(ptrToModelBuffer, modelBufferCapacity,
                                                               ptrToMetadataBuffer, cppComputeUnit));
    } catch (std::exception& exception) {
        throwJavaException(env, exception);
    }
}

extern "C"
JNIEXPORT void JNICALL
Java_com_lightricks_tech_1transfer_neural_1network_SegmentationProcessor__1deleteNativeSegmentationProcessor(
        JNIEnv *env, jclass clazz, jlong native_segmentation_processor) {
    delete (neural_network::SegmentationProcessor *)native_segmentation_processor;
}

extern "C"
JNIEXPORT void JNICALL
Java_com_lightricks_tech_1transfer_neural_1network_SegmentationProcessor__1runNativeSegmentation(
    JNIEnv *env, jclass clazz, jlong native_segmentation_processor, jlong inputMat, jlong outputMat) {
    try {
      auto segmentationProcessor =
          reinterpret_cast<neural_network::SegmentationProcessor *>(native_segmentation_processor);
      auto &input = *reinterpret_cast<cv::Mat4b *>(inputMat);
      auto &output = *reinterpret_cast<cv::Mat *>(outputMat);

      segmentationProcessor->runSegmentation(input, &output);
    } catch (std::exception& exception) {
        throwJavaException(env, exception);
    }
}
extern "C"
JNIEXPORT jintArray JNICALL
Java_com_lightricks_tech_1transfer_neural_1network_SegmentationProcessor__1nativeOutputSizeForInputSize(
        JNIEnv *env, jclass clazz, jlong native_segmentation_processor, jobject input_size) {
    try {
        auto segmentationProcessor =
                reinterpret_cast<neural_network::SegmentationProcessor *>(native_segmentation_processor);

        auto cppInputSize = cppSizeFromJavaSize(env, input_size);

        auto cppOutputSize = segmentationProcessor->outputSizeForInputSize(cppInputSize);

        return javaArrayFromCppVector(env, cppOutputSize);
    } catch (std::exception& exception) {
        throwJavaException(env, exception);
    }
}
extern "C"
JNIEXPORT jobject JNICALL
Java_com_lightricks_tech_1transfer_neural_1network_SegmentationProcessor__1nativeOutputMatForInputSize(
        JNIEnv *env, jclass clazz, jlong native_segmentation_processor, jobject input_size) {
    try {
        auto segmentationProcessor =
                reinterpret_cast<neural_network::SegmentationProcessor *>(native_segmentation_processor);

        auto cppInputSize = cppSizeFromJavaSize(env, input_size);

        auto cppOutputMat = new cv::Mat(segmentationProcessor->outputMatForInputSize(cppInputSize));

        return javaMatFromCppMat(env, cppOutputMat);
    } catch (std::exception& exception) {
        throwJavaException(env, exception);
    }
}

extern "C"
JNIEXPORT jobject JNICALL
Java_com_lightricks_tech_1transfer_neural_1network_SegmentationProcessor__1nativeRunSegmentationAndReturnResult(
        JNIEnv *env, jclass clazz, jlong native_segmentation_processor, jlong inputMat) {
    try {
        auto segmentationProcessor =
                reinterpret_cast<neural_network::SegmentationProcessor *>(native_segmentation_processor);
        auto &cppInputMat = *reinterpret_cast<cv::Mat4b *>(inputMat);

        auto cppOutputMat = new cv::Mat(segmentationProcessor->runSegmentation(cppInputMat));
        return javaMatFromCppMat(env, cppOutputMat);
    } catch (std::exception& exception) {
        throwJavaException(env, exception);
    }
}
