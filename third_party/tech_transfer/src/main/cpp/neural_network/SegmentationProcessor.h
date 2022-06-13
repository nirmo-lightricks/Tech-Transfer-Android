#include <memory>
#include <opencv2/core.hpp>
#include <tensorflow/lite/c/c_api.h>

#include "ComputeUnit.h"
#include "InputResizeStrategy.h"

void MyGpuDelegateV2Delete(TfLiteDelegate* delegate);

namespace neural_network {
class SegmentationProcessor {
public:
    SegmentationProcessor() = delete;

    /// Creates the processor with the provided model buffer (defined by start pointer and length), metadata
    /// (assumed to be a zero-byte-delimited text string) and the compute unit to run the processor on.
    SegmentationProcessor(void *ptrToModelBuffer, size_t modelBufferSize, void *ptrToMetadataBuffer,
                          ComputeUnit computeUnit);

    /// Returns the size of the output matrix. Vector of 3 inputs is returned; these ints are height, width and channel
    /// count in this order (HWC).
    std::vector<int> outputSizeForInputSize(const cv::Size &inputSize);

    /// Creates the matrix that can be used as an output of the processor when the input has the given size.
    cv::Mat outputMatForInputSize(const cv::Size &inputSize);

    /// Runs segmentation on input and stores it in output.
    void runSegmentation(const cv::Mat4b &input, cv::Mat *output);

    /// Runs segmentation on input and returns the result.
    cv::Mat runSegmentation(const cv::Mat4b &input);
private:
    void setupModel(void *ptrToModelBuffer, size_t modelBufferSize);
    void setupInterpreter(ComputeUnit computeUnit);
    void setupInputResizeStrategy(void *ptrToMetadataBuffer);

    ResizeParams resizeParamsForInputSize(const cv::Size &inputSize);

    void fillInputTensor(const cv::Mat4b &input, const ResizeParams &resizeParams);
    void allocateTensorsIfNeeded(const cv::Size &inputSize);
    void retrieveOutputFromTensor(cv::Mat *output, const ResizeParams &resizeParams);

    std::unique_ptr<TfLiteModel, void (*)(TfLiteModel *)> _model;
    std::unique_ptr<TfLiteInterpreter, void (*)(TfLiteInterpreter *)> _interpreter;
    std::unique_ptr<InputResizeStrategy> _inputResizeStrategy;
    std::unique_ptr<TfLiteDelegate, void (*)(TfLiteDelegate *)> _delegate;
};
}
