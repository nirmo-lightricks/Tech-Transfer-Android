//
// Created by Gershon Hochman on 16/05/2022.
//

#include "neural_network/ResizeProcessor.h"

#include <gtest/gtest.h>
#include <opencv2/imgcodecs.hpp>

#include "neural_network/ResizeParams.h"

namespace {

using ::testing::TestWithParam;
using ::testing::Values;
using namespace neural_network;

cv::RotatedRect rotatedRect(const cv::Rect &rect) {
    return cv::RotatedRect(0.5 * (cv::Point2f(rect.tl()) + cv::Point2f(rect.br())), rect.size(), 0);
}

cv::RotatedRect rotatedRect(const cv::Size &size) {
    return cv::RotatedRect(0.5 * cv::Point2f(size), size, 0);
}

cv::Mat loadMat(const char *fileName) {
    auto fullPath = std::string(getenv("TEST_IMAGES_DIR")) + "/" + fileName;
    return cv::imread(fullPath.c_str(), cv::IMREAD_UNCHANGED);
}

struct TestParameters {
    TestParameters(cv::Mat input, ResizeParams resizeParams, const std::string &expectedOutputFileName) :
            input(input), resizeParams(resizeParams), expectedOutputFileName(expectedOutputFileName) {}

    cv::Mat input;
    ResizeParams resizeParams;
    std::string expectedOutputFileName;
};

typedef TestParameters *CreateTestParameters();

class ResizeProcessorExamples : public TestWithParam<CreateTestParameters*> {
public:
    void SetUp() override {
        // The parent's method GetParam() returns pointer to a function from the list defined in
        // INSTANTIATE_TEST_SUITE_P. This function returns a pointer to the TestParameters structure
        // containing the parameter for the current test. SetUp() wraps this pointer with a unique_ptr.
        _testParameters = std::unique_ptr<TestParameters>((*GetParam())());
    }

protected:
    std::unique_ptr<TestParameters> _testParameters;
};

TEST_P(ResizeProcessorExamples, xxx) {
    auto expectedOutput = loadMat(_testParameters->expectedOutputFileName.c_str());
    auto actualOutput = resize(_testParameters->input, _testParameters->resizeParams);
    auto diff = cv::norm(actualOutput, expectedOutput);
    EXPECT_LE(diff, 0.1);
}

TestParameters *ResizeProcessorClampToZero()  {
    cv::Mat1b input = cv::Mat1b(128, 128, 255);

    cv::Size outputSize(64, 96);
    cv::Rect outputROI(0, 16, 64, 64);
    ResizeParams resizeParameters(rotatedRect(input.size()), outputSize, outputROI, outputROI,
                                  ResizeStrategyAddressMode::clampToZero, ResizeStrategyInterpolation::bilinear);

    cv::Mat1b expected = cv::Mat1b::zeros(outputSize);
    expected(outputROI).setTo(cv::Scalar::all(255));

    return new TestParameters(input, resizeParameters, "resize_output_clamp_to_zero.png");
}

TestParameters *ResizeProcessorClampToEdge()  {
    cv::Mat1b input(128, 128);
    input(cv::Rect(0, 0, 128, 64)).setTo(cv::Scalar::all(127));
    input(cv::Rect(0, 64, 128, 64)).setTo(cv::Scalar::all(255));

    cv::Size outputSize(64, 96);
    cv::Rect outputROI(0, 16, 64, 64);
    ResizeParams resizeParameters(rotatedRect(input.size()), outputSize, outputROI, outputROI,
                                  ResizeStrategyAddressMode::clampToEdge, ResizeStrategyInterpolation::bilinear);

    return new TestParameters(input, resizeParameters, "resize_output_clamp_to_edge.png");
}

TestParameters *ResizeProcessorCutResidualMargins()  {
    cv::Size outputSize(12, 12);

    cv::Mat1b input(4 * outputSize.width + 3, 4 * outputSize.height + 1);
    input.forEach([&](uchar &pixel, const int *position) {
        if (position[0] < 4 * outputSize.height && position[1] < 4 * outputSize.width) {
            pixel = 10 * (position[0] / 4 + position[1] / 4);
        } else {
            pixel = 255;
        }
    });

    cv::Rect outputROI(cv::Point(), outputSize);
    ResizeParams resizeParameters(rotatedRect(input.size()), outputSize, outputROI, outputROI,
                                  ResizeStrategyAddressMode::clampToEdge, ResizeStrategyInterpolation::bilinear);

     return new TestParameters(input, resizeParameters, "resize_output_cut_residual_margins.png");
}

TestParameters *ResizeProcessorRotatedSquare()  {
    cv::Mat1b input(24, 24);
    input(cv::Rect(0, 0, 12, 24)).setTo(cv::Scalar::all(0));
    input(cv::Rect(12, 0, 12, 24)).setTo(cv::Scalar::all(255));

    cv::RotatedRect inputRect(cv::Point2f(12, 12), cv::Size(12 * sqrt(2.), 12 * sqrt(2.)), 45);

    cv::Size outputSize(12, 12);
    cv::Rect outputROI(cv::Point(), outputSize);
    ResizeParams resizeParameters(inputRect, outputSize, outputROI, outputROI,
                                  ResizeStrategyAddressMode::clampToZero, ResizeStrategyInterpolation::nearest);

    return new TestParameters(input, resizeParameters, "resize_output_rotated_square.png");
}

INSTANTIATE_TEST_SUITE_P(ResizeProcessor, ResizeProcessorExamples, Values(
    &ResizeProcessorClampToZero ,
    &ResizeProcessorClampToEdge,
    &ResizeProcessorCutResidualMargins,
    &ResizeProcessorRotatedSquare
));

}  // namespace
