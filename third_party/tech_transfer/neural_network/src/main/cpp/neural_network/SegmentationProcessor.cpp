#include "SegmentationProcessor.h"

#include <bits/sysconf.h>
#include <cstdio>
#include "log.h"
#include <opencv2/imgproc/imgproc.hpp>
#include <string>
#include <tensorflow/lite/delegates/gpu/delegate.h>
#include <tensorflow/lite/delegates/xnnpack/xnnpack_delegate.h>

#include "InputResizeStrategyProvider.h"
#include "ResizeProcessor.h"

static void TFLInterpreterErrorReporter(__unused void *user_data, const char *format, va_list args) {
    fprintf(stderr, format, args);
}

namespace neural_network {
SegmentationProcessor::SegmentationProcessor(void *ptrToModelBuffer, size_t modelBufferSize, void *ptrToMetadataBuffer,
                                             ComputeUnit computeUnit) :
        _model(nullptr, nullptr), _interpreter(nullptr, nullptr), _delegate(nullptr, nullptr) {
    setupModel(ptrToModelBuffer, modelBufferSize);
    setupInterpreter(computeUnit);
    setupInputResizeStrategy(ptrToMetadataBuffer);
}

void SegmentationProcessor::setupModel(void *ptrToModelBuffer, size_t modelBufferSize) {
    _model = {TfLiteModelCreate(ptrToModelBuffer, modelBufferSize), &TfLiteModelDelete};
    ASSERT(_model != nullptr, "Failed to create TFLite model");
}

void SegmentationProcessor::setupInterpreter(ComputeUnit computeUnit) {
    auto options = TfLiteInterpreterOptionsCreate();
    ASSERT(options != nullptr, "Failed to create interpreter options structure");

    // Set the interpreter's thread number to the number of active cores.
    auto coreCount = sysconf(_SC_NPROCESSORS_ONLN);
    TfLiteInterpreterOptionsSetNumThreads(options, coreCount);

    TfLiteInterpreterOptionsSetErrorReporter(options, TFLInterpreterErrorReporter, nullptr);

    switch (computeUnit) {
        case ComputeUnit::GPU: {
            auto gpuDelegateOptions = TfLiteGpuDelegateOptionsV2Default();
            _delegate = {TfLiteGpuDelegateV2Create(&gpuDelegateOptions), &TfLiteGpuDelegateV2Delete};
            break;
        }
        case ComputeUnit::CPU:
        case ComputeUnit::DO_NOT_CARE: {
            auto xnnPackDelegateOptions = TfLiteXNNPackDelegateOptionsDefault();
            xnnPackDelegateOptions.num_threads = coreCount;
            _delegate = {TfLiteXNNPackDelegateCreate(&xnnPackDelegateOptions), &TfLiteXNNPackDelegateDelete};
            break;
        }
    }

    ASSERT(_delegate, "Failed to create delegate");
    TfLiteInterpreterOptionsAddDelegate(options, _delegate.get());

    _interpreter = {TfLiteInterpreterCreate(_model.get(), options), &TfLiteInterpreterDelete};
    ASSERT(_interpreter != nullptr, "Failed to initialize TFLite interpreter: return code");
    TfLiteInterpreterOptionsDelete(options);

    // Allocate tensors to sizes defined by the default input size.
    TfLiteInterpreterAllocateTensors(_interpreter.get());
}

void SegmentationProcessor::setupInputResizeStrategy(void *ptrToMetadataBuffer) {
    auto inputTensor = TfLiteInterpreterGetInputTensor(_interpreter.get(), 0);
    auto inputName = TfLiteTensorName(inputTensor);
    auto inputDefaultSize = cv::Size(TfLiteTensorDim(inputTensor, 2), TfLiteTensorDim(inputTensor, 1));

    _inputResizeStrategy = std::unique_ptr<InputResizeStrategy>(InputResizeStrategyProvider::strategy(
            inputName, (const char *)ptrToMetadataBuffer, inputDefaultSize));
}

std::vector<int> SegmentationProcessor::outputSizeForInputSize(const cv::Size &inputSize) {
    auto resizeParams = resizeParamsForInputSize(inputSize);

    int height = resizeParams.outputROI.height;
    int width = resizeParams.outputROI.width;

    auto outputTensor = TfLiteInterpreterGetOutputTensor(_interpreter.get(), 0);
    auto channelCount = TfLiteTensorDim(outputTensor, 3);

    return {height, width, channelCount};
}

ResizeParams SegmentationProcessor::resizeParamsForInputSize(const cv::Size &inputSize) {
    cv::RotatedRect inputRect(cv::Point2f(inputSize) / 2, inputSize, 0);
    return _inputResizeStrategy->resizeParameters(inputRect);
}

cv::Mat SegmentationProcessor::outputMatForInputSize(const cv::Size &inputSize) {
    auto outputSize = outputSizeForInputSize(inputSize);
    return cv::Mat(outputSize[0], outputSize[1], CV_8UC(outputSize[2]));
}

void SegmentationProcessor::runSegmentation(const cv::Mat4b &input, cv::Mat *output) {
    auto expectedOutputSize = outputSizeForInputSize(input.size());

    ASSERT(output->rows == expectedOutputSize[0], "Expected output matrix with %d rows but got %d",
           expectedOutputSize[0], output->rows);
    ASSERT(output->cols == expectedOutputSize[1], "Expected output matrix with %d columns but got %d",
           expectedOutputSize[1], output->cols);
    ASSERT(output->channels() == expectedOutputSize[2], "Expected output matrix with %d channels but got %d",
           expectedOutputSize[2], output->channels());
    ASSERT(output->depth() == CV_8U, "Expected output matrix of depth CV_8U(%d) but got %d", CV_8U, output->depth());

    auto resizeParams = resizeParamsForInputSize(input.size());
    fillInputTensor(input, resizeParams);

    auto returnCode = TfLiteInterpreterInvoke(_interpreter.get());
    ASSERT(returnCode == kTfLiteOk, "Failed to invoke TFLite interpreter: return code %d", returnCode);

    retrieveOutputFromTensor(output, resizeParams);
}

void SegmentationProcessor::fillInputTensor(const cv::Mat4b &input, const ResizeParams &resizeParams) {
    allocateTensorsIfNeeded(resizeParams.outputSize);

    auto inputRGBA = resize(input, resizeParams);

    cv::Mat3b inputRGB;
    cv::cvtColor(inputRGBA, inputRGB, cv::COLOR_RGBA2RGB);

    auto inputTensor = TfLiteInterpreterGetInputTensor(_interpreter.get(), 0);
    auto inputTensorDataPtr = (float *)TfLiteTensorData(inputTensor);

    cv::Mat3f inputFloat(inputRGB.rows, inputRGB.cols, (cv::Vec3f *)inputTensorDataPtr);
    inputRGB.convertTo(inputFloat, CV_32F, 1. / 255.);
}

void SegmentationProcessor::allocateTensorsIfNeeded(const cv::Size &inputSize) {
    auto inputTensor = TfLiteInterpreterGetInputTensor(_interpreter.get(), 0);
    if (cv::Size(TfLiteTensorDim(inputTensor, 2), TfLiteTensorDim(inputTensor, 1)) == inputSize) {
        return;
    }

    std::vector<int> newInputDimensions = {
        TfLiteTensorDim(inputTensor, 0),
        inputSize.height,
        inputSize.width,
        TfLiteTensorDim(inputTensor, 3)
    };

    TfLiteInterpreterResizeInputTensor(_interpreter.get(), 0, newInputDimensions.data(),
                                       (int)newInputDimensions.size());
    TfLiteInterpreterAllocateTensors(_interpreter.get());
}

void SegmentationProcessor::retrieveOutputFromTensor(cv::Mat *output, const ResizeParams &resizeParams) {
    auto outputTensor = TfLiteInterpreterGetOutputTensor(_interpreter.get(), 0);

    cv::Mat outputFloat(TfLiteTensorDim(outputTensor, 1), TfLiteTensorDim(outputTensor, 2),
                        CV_32FC(TfLiteTensorDim(outputTensor, 3)), TfLiteTensorData(outputTensor));

    outputFloat(resizeParams.outputROI).convertTo(*output, CV_8U, 255);
}

cv::Mat SegmentationProcessor::runSegmentation(const cv::Mat4b &input) {
    cv::Mat output = outputMatForInputSize(input.size());
    runSegmentation(input, &output);
    return output;
}
}
