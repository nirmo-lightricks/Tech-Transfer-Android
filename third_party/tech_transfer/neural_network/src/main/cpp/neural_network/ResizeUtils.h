//
// Created by Gershon Hochman on 09/05/2022.
//

#ifndef FACETUNE_ANDROID_RESIZEUTILS_H
#define FACETUNE_ANDROID_RESIZEUTILS_H

#include <opencv2/core.hpp>

namespace neural_network {
/// Aspect fits size to sizeToFit.
cv::Size2f aspectFit(cv::Size size, cv::Size sizeToFit);

/// Returns the best input size from the list of supportedSizes, such that the content of the
/// sourceSize fits the bigger area without distorting the content aspect ratio.
cv::Size optimalTargetSizeAspectFit(cv::Size sourceSize, const std::vector<cv::Size> &supportedSizes);

/// Returns the best input size from the list of supportedSizes, such that the content of
/// sourceSize fills the whole area with minimal distortion in aspect ratio.
cv::Size optimalTargetSizeAspectFill(cv::Size sourceSize, const std::vector<cv::Size> &supportedSizes);
}

#endif //FACETUNE_ANDROID_RESIZEUTILS_H
