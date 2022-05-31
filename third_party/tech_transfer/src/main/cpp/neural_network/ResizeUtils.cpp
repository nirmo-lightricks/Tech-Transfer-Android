//
// Created by Gershon Hochman on 09/05/2022.
//

#include "ResizeUtils.h"

#include <iostream>

namespace {
/// Calculates the measure of correlation between aspect ratios of size1 and size2.
float aspectRatiosCorrelation(cv::Size size1, cv::Size size2) {
    auto aspectRatio1 = (float)size1.width / size1.height;
    auto aspectRatio2 = (float)size2.width / size2.height;
    return std::min(aspectRatio1, aspectRatio2) / std::max(aspectRatio1, aspectRatio2);
}

/// Calculates the absolute difference between areas of size1 and size2.
int areaDiff(cv::Size size1, cv::Size size2) {
    return std::abs(size1.area() - size2.area());
}
}

namespace neural_network {

cv::Size2f aspectFit(cv::Size size, cv::Size sizeToFit) {
    auto widthRatio = (float)sizeToFit.width / size.width;
    auto heightRatio = (float)sizeToFit.height / size.height;

    return cv::Size2f(size) * std::min(widthRatio, heightRatio);
}

cv::Size aspectFitAndRound(cv::Size size, cv::Size sizeToFit) {
    auto floatSize = aspectFit(size, sizeToFit);
    return cv::Size(std::round(floatSize.width), std::round(floatSize.height));
}

cv::Size optimalTargetSizeAspectFit(cv::Size sourceSize, const std::vector<cv::Size> &supportedSizes) {
    if (supportedSizes.empty()) {
        return cv::Size(0, 0);
    }

    // Drop the sizes with area bigger than sourceSize.
    std::vector<cv::Size> validSizes;
    std::copy_if(supportedSizes.begin(), supportedSizes.end(), std::back_inserter(validSizes),
                 [&](const cv::Size &size) {
        return aspectFitAndRound(sourceSize, size).area() < sourceSize.area();
    });

    // If original size is smaller than all supported sizes then return the smallest supported size.
    if (validSizes.empty()) {
        return *std::min_element(supportedSizes.begin(), supportedSizes.end(),
                                 [&](const cv::Size &size1, const cv::Size &size2) {
            return size1.area() < size2.area();
        });
    }

    return *std::min_element(validSizes.begin(), validSizes.end(), [&](const cv::Size &size1, const cv::Size &size2) {
        auto fitSize1 = aspectFitAndRound(sourceSize, size1);
        auto fitSize2 = aspectFitAndRound(sourceSize, size2);

        if (fitSize1.area() != fitSize2.area()) {
            return fitSize1.area() > fitSize2.area();
        }

        // If areas of the rectangles after aspect fit are the same, we want to select the smallest
        // from the two original rects. This is done in order to minimize overall amount of pixels
        // that will be processed.
        return size1.area() < size2.area();
    });
}

cv::Size optimalTargetSizeAspectFill(cv::Size sourceSize, const std::vector<cv::Size> &supportedSizes) {
    if (supportedSizes.empty()) {
        return cv::Size(0, 0);
    }

    // Find the maximal correlation between one of supported sizes and the source size.
    auto supportedSizeWithLargestCorrelation = *std::max_element(supportedSizes.begin(),  supportedSizes.end(),
                                                                 [&](const cv::Size &size1, const cv::Size &size2) {
        return aspectRatiosCorrelation(size1, sourceSize) < aspectRatiosCorrelation(size2, sourceSize);
    });
    auto maxCorrelation = aspectRatiosCorrelation(supportedSizeWithLargestCorrelation, sourceSize);

    // Filter out the sizes with correlation less than 95% of the maximum.
    std::vector<cv::Size> validSizes;
    std::copy_if(supportedSizes.begin(), supportedSizes.end(), std::back_inserter(validSizes),
                 [&](const cv::Size &size) {
        return aspectRatiosCorrelation(size, sourceSize)  >= 0.95 * maxCorrelation;
    });

    // Pick the size with area nearest to the source size.
    return *std::min_element(validSizes.begin(), validSizes.end(), [&](const cv::Size &size1, const cv::Size &size2) {
        return areaDiff(size1, sourceSize) < areaDiff(size2, sourceSize);
    });
}
}
