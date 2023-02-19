//
// Created by Gershon Hochman on 15/05/2022.
//

#ifndef FACETUNE_ANDROID_RESIZEPROCESSOR_H
#define FACETUNE_ANDROID_RESIZEPROCESSOR_H

#include <opencv2/core.hpp>

namespace neural_network {

class ResizeParams;

cv::Mat resize(const cv::Mat &input, const ResizeParams &resizeParams);

}

#endif //FACETUNE_ANDROID_RESIZEPROCESSOR_H
