//
// Created by Gershon Hochman on 10/05/2022.
//

#include "neural_network/InputResizeStrategy.h"

#include <gtest/gtest.h>

namespace {

using ::testing::TestWithParam;
using ::testing::Values;
using namespace neural_network;

struct TestParameters {
    TestParameters(InputResizeStrategy inputResizeStrategy, cv::RotatedRect inputRect,
                   ResizeParams expectedResizeParameters) :
            inputResizeStrategy(inputResizeStrategy), inputRect(inputRect),
            expectedResizeParameters(expectedResizeParameters) {}

    InputResizeStrategy inputResizeStrategy;
    cv::RotatedRect inputRect;
    ResizeParams expectedResizeParameters;
};

typedef TestParameters *CreateTestParameters();

class InputResizeStrategyExamples : public TestWithParam<CreateTestParameters*> {
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

TEST_P(InputResizeStrategyExamples, VerifyResizeParams) {
    auto actualParameters =
            _testParameters->inputResizeStrategy.resizeParameters(_testParameters->inputRect);
    auto expectedParameters = _testParameters->expectedResizeParameters;
    EXPECT_EQ(actualParameters.inputRect.center, expectedParameters.inputRect.center);
    EXPECT_EQ(actualParameters.inputRect.size, expectedParameters.inputRect.size);
    EXPECT_EQ(actualParameters.inputRect.angle, expectedParameters.inputRect.angle);
    EXPECT_EQ(actualParameters.outputSize, expectedParameters.outputSize);
    EXPECT_EQ(actualParameters.outputRect, expectedParameters.outputRect);
    EXPECT_EQ(actualParameters.outputROI, expectedParameters.outputROI);
    EXPECT_EQ(actualParameters.addressMode, expectedParameters.addressMode);
    EXPECT_EQ(actualParameters.interpolation, expectedParameters.interpolation);
}

TestParameters *ResizeStrategyFixed() {
    cv::Size inputSize(512, 512);
    cv::Size targetSize(200, 300);

    InputResizeStrategy inputResizeStrategy(ResizeStrategyAddressMode::clampToEdge,
                                            ResizeStrategyPaddingMode::withZeros,
                                            ResizeStrategyInterpolation::bilinear,
                                            ResizeStrategyScalingMode::aspectFill,
                                            {targetSize});

    cv::RotatedRect inputRect(cv::Point(inputSize / 4), inputSize / 2, 0);
    ResizeParams expectedResizeParameters(inputRect, targetSize, cv::Rect(cv::Point(0, 0), targetSize),
                                          cv::Rect(cv::Point(0, 0), targetSize), ResizeStrategyAddressMode::clampToEdge,
                                          ResizeStrategyInterpolation::bilinear);
    return new TestParameters(inputResizeStrategy, inputRect, expectedResizeParameters);
}

TestParameters *ResizeStrategyCropToFixed() {
    cv::Size inputSize(512, 512);
    cv::Size targetSize(128, 256);

    InputResizeStrategy inputResizeStrategy(ResizeStrategyAddressMode::clampToEdge,
                                            ResizeStrategyPaddingMode::fromSource,
                                            ResizeStrategyInterpolation::bilinear, ResizeStrategyScalingMode::aspectFit,
                                            {targetSize});

    cv::RotatedRect inputRect(cv::Point(inputSize / 2), cv::Size(384, 384), 0);
    cv::Rect outputRect(cv::Point(0, 0), targetSize);
    ResizeParams expectedResizeParameters(cv::RotatedRect(cv::Point(256, 256), cv::Size(384, 768), 0), targetSize,
                                          outputRect, cv::Rect(0, 64, 128, 128), ResizeStrategyAddressMode::clampToEdge,
                                          ResizeStrategyInterpolation::bilinear);
    return new TestParameters(inputResizeStrategy, inputRect, expectedResizeParameters);
}

TestParameters *ResizeStrategyAspectFit() {
    cv::Size inputSize(512, 512);
    cv::Size targetSize(200, 300);

    InputResizeStrategy inputResizeStrategy(ResizeStrategyAddressMode::clampToZero,
                                            ResizeStrategyPaddingMode::withZeros,
                                            ResizeStrategyInterpolation::bilinear, ResizeStrategyScalingMode::aspectFit,
                                            {targetSize});

    cv::RotatedRect inputRect(cv::Point(256, 128), cv::Size(512, 256), 0);
    ResizeParams expectedResizeParameters(inputRect, targetSize, cv::Rect(0, 100, 200, 100), cv::Rect(0, 100, 200, 100),
                                          ResizeStrategyAddressMode::clampToZero,
                                          ResizeStrategyInterpolation::bilinear);
    return new TestParameters(inputResizeStrategy, inputRect, expectedResizeParameters);
}

INSTANTIATE_TEST_SUITE_P(InputResizeStrategy, InputResizeStrategyExamples, Values(
    &ResizeStrategyFixed,
    &ResizeStrategyCropToFixed,
    &ResizeStrategyAspectFit
));

}  // namespace


