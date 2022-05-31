//
// Created by Gershon Hochman on 09/05/2022.
//

#ifndef FACETUNE_ANDROID_RESIZEPARAMS_H
#define FACETUNE_ANDROID_RESIZEPARAMS_H

#include <array>
#include <opencv2/core.hpp>

namespace neural_network {
/// Address mode of the resize's input. Defines how the input is sampled outside of its bounds, if
/// needed.
enum class ResizeStrategyAddressMode {
    /// All the samples outside the input's bounds are clamped to zero.
    clampToZero,
    /// All the samples outside the input's bounds are clamped to the value of closest edge.
    clampToEdge
};

/// Interpolation type to use while sampling resizer input.
enum class ResizeStrategyInterpolation {
    /// Bilinear interpolation.
    bilinear,
    /// Nearest neighbor interpolation.
    nearest
};

class ResizeParams {
public:
    ResizeParams() = delete;

    ResizeParams(cv::RotatedRect inputRect, cv::Size outputSize, cv::Rect outputRect, cv::Rect outputROI,
                 ResizeStrategyAddressMode addressMode, ResizeStrategyInterpolation interpolation);

    /// Input rectangle that should be copied to the output. This can be different from the original
    /// rectangle provided by the caller of resize operation in order to handle padding correctly.
    const cv::RotatedRect inputRect;

    /// Size of the expected output.
    const cv::Size outputSize;

    /// Rectangle in output that will be filled with the content of inputRect. This can be
    /// different from outputROI in order to handle padding correctly.
    const cv::Rect outputRect;

    /// Region in the output that corresponds to the original rectangle provided by the caller of
    /// resize operation.
    const cv::Rect outputROI;

    /// Input address mode type.
    const ResizeStrategyAddressMode addressMode;

    /// Input sampling interpolation type.
    const ResizeStrategyInterpolation interpolation;
};
}

#endif //FACETUNE_ANDROID_RESIZEPARAMS_H
