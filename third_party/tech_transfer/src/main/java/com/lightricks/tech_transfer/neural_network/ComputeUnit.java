package com.lightricks.tech_transfer.neural_network;

/**
 * Enumeration of compute units used for NN inference. This Java enum class must exactly match the C++ enum class found
 * in ComputeUnit.h.
 */
public enum ComputeUnit {
    CPU,
    GPU,
    DO_NOT_CARE
}
