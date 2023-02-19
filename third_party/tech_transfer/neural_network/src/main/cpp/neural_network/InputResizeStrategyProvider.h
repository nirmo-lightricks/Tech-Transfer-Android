//
// Created by Gershon Hochman on 11/05/2022.
//

#ifndef FACETUNE_ANDROID_INPUTRESIZESTRATEGYPROVIDER_H
#define FACETUNE_ANDROID_INPUTRESIZESTRATEGYPROVIDER_H

#include <opencv2/core.hpp>

namespace neural_network {

class InputResizeStrategy;

class InputResizeStrategyProvider {
public:
    /// Returns pointer to input resize strategy. It is responsibility of the caller to free this pointer.
    static InputResizeStrategy *strategy(const char *inputName, const char *modelMetadata, cv::Size defaultSize);
};
}

#endif //FACETUNE_ANDROID_INPUTRESIZESTRATEGYPROVIDER_H
