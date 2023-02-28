//
// Created by Gershon Hochman on 08/06/2022.
//

#ifndef FACETUNE_ANDROID_COMPUTEUNIT_H
#define FACETUNE_ANDROID_COMPUTEUNIT_H

/// Enumeration of compute units used for NN inference. This C++ enum class must exactly match the Java enum class found
/// in ComputeUnit.java.
enum class ComputeUnit {
    CPU,
    GPU,
    DO_NOT_CARE
};

#endif //FACETUNE_ANDROID_COMPUTEUNIT_H
