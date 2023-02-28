//
// Created by Gershon Hochman on 09/05/2022.
//

#ifndef FACETUNE_ANDROID_INPUTRESIZESTRATEGY_H
#define FACETUNE_ANDROID_INPUTRESIZESTRATEGY_H

#include <opencv2/core.hpp>

#include "ResizeParams.h"

namespace neural_network {

/// Padding mode of resize's output. Relevant only if the output is partially filled with the content of the input.
///
/// @note The padding is the operation defined on output, so if the input rectangle is bigger that the actual input size
/// it's content is defined by ResizeStrategyAddressMode, and then padded.
enum class ResizeStrategyPaddingMode {
    /// Destination is padded with zeros if needed.
    withZeros,
    /// Destination is padded with the content of the source if needed.
    fromSource
};

/// Scaling mode of the content while resizing neural network input.
enum class ResizeStrategyScalingMode {
    /// Fits the content of the input in target size without modifying the aspect ratio of the content.
    aspectFit,
    /// Fills the target size with the content of the input by distorting original aspect ratio.
    aspectFill
};

class InputResizeStrategy {
public:
    InputResizeStrategy() = delete;

    InputResizeStrategy(ResizeStrategyAddressMode addressMode, ResizeStrategyPaddingMode paddingMode,
                        ResizeStrategyInterpolation interpolation,  ResizeStrategyScalingMode scalingMode,
                        std::vector<cv::Size> supportedSizes);

    /// Returns parameters describing the size and region of interest of the output of resize process
    /// according to the given inputRect.
    ResizeParams resizeParameters(cv::RotatedRect inputRect);

private:

    /// Returns resize parameters for aspectFit scaling mode.
    ResizeParams aspectFitResizeParameters(cv::RotatedRect inputRect);

    /// Returns resize parameters for aspectFill scaling mode.
    ResizeParams aspectFillResizeParameters(cv::RotatedRect inputRect);

    /// Clamp mode of the resize strategy.
    ResizeStrategyAddressMode _addressMode;

    /// Padding type of the resize strategy.
    ResizeStrategyPaddingMode _paddingMode;

    /// Interpolation type that is used while sampling from source.
    ResizeStrategyInterpolation _interpolation;

    /// Scaling mode.
    ResizeStrategyScalingMode _scalingMode;

    /// List of network's supported input sizes.
    std::vector<cv::Size> _supportedSizes;
};
}
#endif //FACETUNE_ANDROID_INPUTRESIZESTRATEGY_H
