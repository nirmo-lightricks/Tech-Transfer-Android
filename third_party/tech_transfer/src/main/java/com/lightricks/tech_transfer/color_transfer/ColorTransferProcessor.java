// Copyright (c) 2020 Lightricks. All rights reserved.
// Created by Nir Moshe.

package com.lightricks.tech_transfer.color_transfer;

import com.google.common.base.Preconditions;

import org.opencv.core.CvType;
import org.opencv.core.Mat;

import androidx.annotation.NonNull;

/**
 * Processor for generating 3D LUT transferring the color distribution of an input to match that of some reference.
 * The algorithm works relatively well on downscaled images. For best results it is recommended to resize both input
 * and reference such that neither has more than 512*512 total pixels.
 *
 * The returned lookup table is a flattened 16x16x16 grid, represented as 16 vertically-stacked slices, each 16x16
 * pixels.
 */
public final class ColorTransferProcessor {
    private ColorTransferProcessor() {}

    /**
     * Generates 3D LUT transferring the color distribution of input to that of reference, using the default parameters.
     * @param input Input image, i.e., image specifying the source color distribution.
     * @param reference Reference image, i.e., image with the desired final color distribution.
     * @return 3D lookup table suitable for converting the given input to match the color distribution of the reference.
     */
    public static Mat generateLUT(@NonNull Mat input, @NonNull Mat reference) {
        return generateLUT(input, reference, 0.5f);
    }

    /**
     * Generates 3D LUT transferring the color distribution of input to that of reference, using the number of
     * iterations and histogram bins.
     * @param input Input image, i.e., image specifying the source color distribution.
     * @param reference Reference image, i.e., image with the desired final color distribution.
     * @param dampingFactor Parameter controlling the strength of each histogram specification step. Larger values yield
     * faster convergence, but may introduce noise. Usually between 0.2-0.5. Must be in range (0, 1].
     * @return 3D lookup table suitable for converting the given input to match the color distribution of the reference.
     */
    public static Mat generateLUT(@NonNull Mat input, @NonNull Mat reference, float dampingFactor) {
        return generateLUT(input, reference, dampingFactor, 10);
    }

    /**
     * Generates 3D LUT transferring the color distribution of input to that of reference, using the number of histogram
     * bins.
     * @param input Input image, i.e., image specifying the source color distribution.
     * @param reference Reference image, i.e., image with the desired final color distribution.
     * @param dampingFactor Parameter controlling the strength of each histogram specification step. Larger values yield
     * faster convergence, but may introduce noise. Usually between 0.2-0.5. Must be in range (0, 1].
     * @param iterations Number of iterations to perform. Must be between 1 and 50. More iterations allow using smaller
     * dampingFactor for a smoother LUT, but require longer processing time.
     * @return 3D lookup table suitable for converting the given input to match the color distribution of the reference.
     */
    public static Mat generateLUT(@NonNull Mat input, @NonNull Mat reference, float dampingFactor, int iterations) {
        return generateLUT(input, reference, dampingFactor, iterations, 32);
    }

    /**
     * Generates 3D LUT transferring the color distribution of input to that of reference.
     * @param input Input image, i.e., image specifying the source color distribution.
     * @param reference Reference image, i.e., image with the desired final color distribution.
     * @param dampingFactor Parameter controlling the strength of each histogram specification step. Larger values yield
     * faster convergence, but may introduce noise. Usually between 0.2-0.5. Must be in range (0, 1].
     * @param iterations Number of iterations to perform. Must be between 1 and 50. More iterations allow using smaller
     * dampingFactor for a smoother LUT, but require longer processing time.
     * @param histogramBins Number of bins in the computed histograms. Must be between 4-256.
     * @return 3D lookup table suitable for converting the given input to match the color distribution of the reference.
     */
    public static Mat generateLUT(@NonNull Mat input, @NonNull Mat reference, float dampingFactor, int iterations,
                                  int histogramBins) {
        Preconditions.checkNotNull(input);
        Preconditions.checkNotNull(reference);
        Preconditions.checkArgument(input.type() == CvType.CV_8UC4, "Input mat must have " +
                "type %s, got %s", CvType.typeToString(CvType.CV_8UC4), CvType.typeToString(input.type()));
        Preconditions.checkArgument(reference.type() == CvType.CV_8UC4, "Reference mat must have " +
                "type %s, got %s", CvType.typeToString(CvType.CV_8UC4), CvType.typeToString(reference.type()));
        Preconditions.checkArgument(dampingFactor > 0 && dampingFactor <= 1, "Damping factor " +
                "must be in range (0, 1], got %s", dampingFactor);
        Preconditions.checkArgument(iterations > 0 && iterations <= 50, "Iterations must be in range " +
                "[1, 50], got %s", iterations);
        Preconditions.checkArgument(histogramBins >= 4 && histogramBins <= 256, "Histogram bins must " +
                "be in range [4, 256], got %s");


        Mat outputMat = new Mat(16*16, 16, CvType.CV_8UC4);
        _generateLUT(input.getNativeObjAddr(), reference.getNativeObjAddr(), dampingFactor, iterations, histogramBins,
                outputMat.getNativeObjAddr());
        return outputMat;
    }

    private static native void _generateLUT(long inputMat, long referenceMat, float dampingFactor, int iterations,
                                            int histogramBins, long outputMat);
}
