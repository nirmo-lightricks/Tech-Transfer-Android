//
// Created by Gershon Hochman on 09/05/2022.
//

#include "InputResizeStrategy.h"

#include "ResizeUtils.h"

namespace {
cv::Point2f center(cv::Rect2f rect) {
    return (rect.tl() + rect.br()) / 2;
}

cv::Rect2f rectFromCenterAndSize(cv::Point2f center, cv::Size2f size) {
    return cv::Rect2f(center - cv::Point2f(size) / 2, center + cv::Point2f(size) / 2);
}
}

namespace neural_network {
InputResizeStrategy::InputResizeStrategy(ResizeStrategyAddressMode addressMode, ResizeStrategyPaddingMode paddingMode,
                                         ResizeStrategyInterpolation interpolation,
                                         ResizeStrategyScalingMode scalingMode, std::vector <cv::Size> supportedSizes) :
        _addressMode(addressMode), _paddingMode(paddingMode), _interpolation(interpolation),
        _scalingMode(scalingMode), _supportedSizes(supportedSizes) {
}

ResizeParams InputResizeStrategy::resizeParameters(cv::RotatedRect inputRect) {
    switch (_scalingMode) {
        case ResizeStrategyScalingMode::aspectFit:
            return aspectFitResizeParameters(inputRect);

        case ResizeStrategyScalingMode::aspectFill:
            return aspectFillResizeParameters(inputRect);
    }
}

ResizeParams InputResizeStrategy::aspectFitResizeParameters(cv::RotatedRect inputRect) {
    auto targetSize = optimalTargetSizeAspectFit(inputRect.size, _supportedSizes);

    auto fitSize = aspectFit(inputRect.size, targetSize);
    auto targetCenter = center(cv::Rect2f(cv::Point2f(0, 0), targetSize));
    auto roiRect = rectFromCenterAndSize(targetCenter, fitSize);

    switch (_paddingMode) {
        case ResizeStrategyPaddingMode::withZeros:
            return ResizeParams(inputRect, targetSize, roiRect, roiRect, _addressMode, _interpolation);

        case ResizeStrategyPaddingMode::fromSource:
            auto fullInputSize = cv::Size2f(inputRect.size.width * targetSize.width / roiRect.width,
                                            inputRect.size.height * targetSize.height / roiRect.height);
            auto fullInputRotatedRect = cv::RotatedRect(inputRect.center, fullInputSize, inputRect.angle);
            return ResizeParams(fullInputRotatedRect, targetSize, cv::Rect(cv::Point(0, 0), targetSize), roiRect,
                                _addressMode, _interpolation);
    }
}

ResizeParams InputResizeStrategy::aspectFillResizeParameters(cv::RotatedRect inputRect) {
    auto targetSize = optimalTargetSizeAspectFill(inputRect.size, _supportedSizes);
    auto targetRect = cv::Rect(cv::Point(0, 0), targetSize);
    return ResizeParams(inputRect, targetSize, targetRect, targetRect, _addressMode, _interpolation);
}
}
