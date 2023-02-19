//
// Created by Gershon Hochman on 10/05/2022.
//

#include "neural_network/ResizeUtils.h"

#include <gtest/gtest.h>

namespace {

using ::testing::TestWithParam;
using ::testing::Values;
using namespace neural_network;

struct TestParameters {
    TestParameters(std::vector<cv::Size> supportedSizes, cv::Size sourceSize, cv::Size expectedFitSize,
                   cv::Size expectedFillSize) : supportedSizes(supportedSizes), sourceSize(sourceSize),
                   expectedFitSize(expectedFitSize), expectedFillSize(expectedFillSize) {}

    std::vector<cv::Size> supportedSizes;
    cv::Size sourceSize;
    cv::Size expectedFitSize;
    cv::Size expectedFillSize;
};

typedef TestParameters *CreateTestParameters();

class ResizeUtilsExamples : public TestWithParam<CreateTestParameters*> {
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

TEST_P(ResizeUtilsExamples, ShouldCalculateOptimalSizeForFit) {
    auto actualFitSize = neural_network::optimalTargetSizeAspectFit(_testParameters->sourceSize,
                                                                    _testParameters->supportedSizes);
    EXPECT_EQ(actualFitSize, _testParameters->expectedFitSize);
}

TEST_P(ResizeUtilsExamples, ShouldCalculateOptimalSizeForFill) {
    auto actualFillSize = neural_network::optimalTargetSizeAspectFill(_testParameters->sourceSize,
                                                                      _testParameters->supportedSizes);
    EXPECT_EQ(actualFillSize, _testParameters->expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForWideInput() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(1022, 10);
    cv::Size expectedFitSize(512, 128);
    cv::Size expectedFillSize(512, 128);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForLongInput() {
    std::vector<cv::Size> supportedSizes = {{128, 512}, {256, 512}, {512, 512}};
    cv::Size sourceSize(10, 1022);
    cv::Size expectedFitSize(128, 512);
    cv::Size expectedFillSize(128, 512);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForSmallInput() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(257, 129);
    cv::Size expectedFitSize(512, 128);
    cv::Size expectedFillSize(512, 256);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForLongInputWithFlippedAspectRatio() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(10, 1022);
    cv::Size expectedFitSize(512, 512);
    cv::Size expectedFillSize(512, 512);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForBigInput() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(1022, 500);
    cv::Size expectedFitSize(512, 256);
    cv::Size expectedFillSize(512, 256);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForInputSmallerThanAllOfTheSupportedSizes() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(20, 10);
    cv::Size expectedFitSize(512, 128);
    cv::Size expectedFillSize(512, 256);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForSquareInputSmallerThanAllOfTheSupportedSizes() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(10, 10);
    cv::Size expectedFitSize(512, 128);
    cv::Size expectedFillSize(512, 512);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForInputCloseToSupportedSizeAndFlippedAspectRatio() {
    std::vector<cv::Size> supportedSizes = {{128, 512}, {256, 512}, {512, 512}};
    cv::Size sourceSize(553, 500);
    cv::Size expectedFitSize(512, 512);
    cv::Size expectedFillSize(512, 512);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeForInputCloseToSupportedSize() {
    std::vector<cv::Size> supportedSizes = {{512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(553, 500);
    cv::Size expectedFitSize(512, 512);
    cv::Size expectedFillSize(512, 512);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeWenSupportedSizesContainsTwoSetsOfSizes() {
    std::vector<cv::Size> supportedSizes = {{256, 64}, {256, 128}, {256, 256}, {512, 128}, {512, 256}, {512, 512}};
    cv::Size sourceSize(257, 129);
    cv::Size expectedFitSize(256, 256);
    cv::Size expectedFillSize(256, 128);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

TestParameters *ShouldReturnOptimalSizeClosestToInput() {
    std::vector<cv::Size> supportedSizes = {{256, 256}, {512, 512}};
    cv::Size sourceSize(257, 257);
    cv::Size expectedFitSize(256, 256);
    cv::Size expectedFillSize(256, 256);

    return new TestParameters(supportedSizes, sourceSize, expectedFitSize, expectedFillSize);
}

INSTANTIATE_TEST_SUITE_P(InputResizeStrategy, ResizeUtilsExamples, Values(
    &ShouldReturnOptimalSizeForWideInput,
    &ShouldReturnOptimalSizeForLongInput,
    &ShouldReturnOptimalSizeForSmallInput,
    &ShouldReturnOptimalSizeForLongInputWithFlippedAspectRatio,
    &ShouldReturnOptimalSizeForBigInput,
    &ShouldReturnOptimalSizeForInputSmallerThanAllOfTheSupportedSizes,
    &ShouldReturnOptimalSizeForSquareInputSmallerThanAllOfTheSupportedSizes,
    &ShouldReturnOptimalSizeForInputCloseToSupportedSizeAndFlippedAspectRatio,
    &ShouldReturnOptimalSizeForInputCloseToSupportedSize,
    &ShouldReturnOptimalSizeWenSupportedSizesContainsTwoSetsOfSizes,
    &ShouldReturnOptimalSizeClosestToInput
));

}  // namespace
