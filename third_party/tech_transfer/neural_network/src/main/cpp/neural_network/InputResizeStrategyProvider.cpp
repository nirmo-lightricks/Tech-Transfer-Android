//
// Created by Gershon Hochman on 11/05/2022.
//

#include "InputResizeStrategyProvider.h"

#include "InputResizeStrategy.h"
#include "json.h"
#include "log.h"

namespace neural_network {
namespace {
ResizeStrategyAddressMode addressMode(json::JSON resizeStrategy) {
    auto addressModeString = resizeStrategy["addressMode"].ToString();
    if (addressModeString == "ClampToEdge") {
        return ResizeStrategyAddressMode::clampToEdge;
    } else if (addressModeString == "ClampToZero") {
        return ResizeStrategyAddressMode::clampToZero;
    } else {
        ASSERT(false, "Address mode '%s' is not supported", addressModeString.c_str());
    }
}

ResizeStrategyPaddingMode paddingMode(json::JSON resizeStrategy) {
    auto paddingModeString = resizeStrategy["padding"].ToString();
    if (paddingModeString == "Zero") {
        return ResizeStrategyPaddingMode::withZeros;
    } else if (paddingModeString == "FromSource") {
        return ResizeStrategyPaddingMode::fromSource;
    } else {
        ASSERT(false, "Padding mode '%s' is not supported", paddingModeString.c_str());
    }
}

ResizeStrategyInterpolation interpolation(json::JSON resizeStrategy) {
    auto interpolationString = resizeStrategy["interpolation"].ToString();
    if (interpolationString == "Bilinear") {
        return ResizeStrategyInterpolation::bilinear;
    } else if (interpolationString == "Nearest") {
        return ResizeStrategyInterpolation::nearest;
    } else {
        ASSERT(false, "Interpolation '%s' is not supported", interpolationString.c_str());
    }
}

ResizeStrategyScalingMode scalingMode(json::JSON resizeStrategy) {
    auto scalingModeString = resizeStrategy["mode"].ToString();
    if (scalingModeString == "AspectFill") {
        return ResizeStrategyScalingMode::aspectFill;
    } else if (scalingModeString == "AspectFit") {
        return ResizeStrategyScalingMode::aspectFit;
    } else {
        ASSERT(false, "Scaling mode '%s' is not supported", scalingModeString.c_str());
    }
}

std::vector<cv::Size> supportedSizes(json::JSON supportedSizesMetadata, cv::Size defaultSize) {
    auto supportedSizesRange = supportedSizesMetadata.ArrayRange();

    std::vector<cv::Size> result;
    std::transform(supportedSizesRange.begin(), supportedSizesRange.end(), std::back_inserter(result),
                   [](json::JSON &size) {
        return cv::Size(size[0].ToInt(), size[1].ToInt());
    });

    return result.empty() ? std::vector<cv::Size>({defaultSize}) : result;
}
}

InputResizeStrategy *InputResizeStrategyProvider::strategy(const char *inputName, const char *modelMetadata,
                                                           cv::Size defaultSize) {
    auto json = json::JSON::Load(modelMetadata);
    auto inputMetadata = json["inputs_metadata"][inputName];
    auto resizeStrategy = inputMetadata["resize_strategy"];
    auto supportedSizesMetadata = inputMetadata["input_sizes"];

    return new InputResizeStrategy(addressMode(resizeStrategy), paddingMode(resizeStrategy),
                                   interpolation(resizeStrategy), scalingMode(resizeStrategy),
                                   supportedSizes(supportedSizesMetadata, defaultSize));
}
}
