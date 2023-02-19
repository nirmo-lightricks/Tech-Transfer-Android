//
// Created by Gershon Hochman on 09/05/2022.
//

#include "ResizeParams.h"

namespace neural_network {

ResizeParams::ResizeParams(cv::RotatedRect inputRect, cv::Size outputSize, cv::Rect outputRect, cv::Rect outputROI,
                           ResizeStrategyAddressMode addressMode, ResizeStrategyInterpolation interpolation) :
        inputRect(inputRect), outputSize(outputSize), outputRect(outputRect), outputROI(outputROI),
        addressMode(addressMode), interpolation(interpolation) {
}

}