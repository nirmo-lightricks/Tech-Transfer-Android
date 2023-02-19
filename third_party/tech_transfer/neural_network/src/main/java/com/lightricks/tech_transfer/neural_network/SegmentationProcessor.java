// Copyright (c) 2022 Lightricks. All rights reserved.
// Created by Gershon Hochman.

package com.lightricks.tech_transfer.neural_network;

import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

import com.google.common.base.Preconditions;

import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Size;
import org.tensorflow.lite.support.metadata.MetadataExtractor;
import org.tensorflow.lite.gpu.CompatibilityList;

import androidx.annotation.NonNull;
import androidx.annotation.VisibleForTesting;

/**
 * Processor for creating a segmentation mask from the given image according to the given neural network model.
 *
 * This class is not thread safe, you should use separate instance for each thread or serialize calls to its methods.
 *
 * Given model should contain an associated file called "metadata.json" describing its resize strategy and supported
 * input sizes.
 */
public final class SegmentationProcessor {
    private long _nativeSegmentationProcessor;

    /**
     * Creates a segmentation processor object from a {@code ByteBuffer} containing the TFLite model.
     * Caller retains ownership of the {@code ByteBuffer} and should keep it alive until the
     * {@code SegmentationProcessor} is destroyed.
     *
     *  The processor will run on the hardware defined by {@code ComputeUnit}.
     */
    public SegmentationProcessor(@NonNull ByteBuffer modelBinary, @NonNull ComputeUnit computeUnit) throws IOException {
        ByteBuffer metadata = extractMetadata(modelBinary);
        _nativeSegmentationProcessor = _createNativeSegmentationProcessor(modelBinary, metadata,
                availableComputeUnit(computeUnit).ordinal());
    }

    private ComputeUnit availableComputeUnit(ComputeUnit computeUnit) {
        if (computeUnit == ComputeUnit.CPU) {
            return computeUnit;
        }

        CompatibilityList gpuCompatibilityList = new CompatibilityList();
        return gpuCompatibilityList.isDelegateSupportedOnThisDevice() ? computeUnit : ComputeUnit.CPU;
    }

    /**
     * Returns the size of output image for the given size of the input image. The size is a 3-element array in HWC
     * (height, width, channel count) order.
     */
    public int[] outputSizeForInputSize(@NonNull Size inputSize) {
        return _nativeOutputSizeForInputSize(_nativeSegmentationProcessor, inputSize);
    }

    /**
     * Returns an empty output image for the given size of the input image.
     */
    public Mat outputMatForInputSize(@NonNull Size inputSize) {
        return _nativeOutputMatForInputSize(_nativeSegmentationProcessor, inputSize);
    }

    /**
     * Performs segmentation of {@code input} and returns the result.
     */
    public Mat runSegmentation(@NonNull Mat input) {
        Preconditions.checkNotNull(input);
        Preconditions.checkArgument(input.type() == CvType.CV_8UC4, "Input mat must have " +
                "type %s, got %s", CvType.typeToString(CvType.CV_8UC4), CvType.typeToString(input.type()));

        return _nativeRunSegmentationAndReturnResult(_nativeSegmentationProcessor, input.getNativeObjAddr());
    }

    /**
     * Performs segmentation of {@code input} and saves the result in {@code output}.
     */
    public void runSegmentation(@NonNull Mat input, @NonNull Mat output) {
        Preconditions.checkNotNull(input);
        Preconditions.checkNotNull(output);
        Preconditions.checkArgument(input.type() == CvType.CV_8UC4, "Input mat must have " +
                "type %s, got %s", CvType.typeToString(CvType.CV_8UC4), CvType.typeToString(input.type()));
        Preconditions.checkArgument(output.depth() == CvType.CV_8U, "Output mat must have " +
                "depth CV_8U(%d), got %d", CvType.CV_8U, output.depth());

        _runNativeSegmentation(_nativeSegmentationProcessor, input.getNativeObjAddr(), output.getNativeObjAddr());
    }

    public void recycle() {
        if (_nativeSegmentationProcessor == 0) {
            return;
        }
        _deleteNativeSegmentationProcessor(_nativeSegmentationProcessor);
        _nativeSegmentationProcessor = 0;
    }

    @VisibleForTesting
    public static ByteBuffer loadInputStream(InputStream inputStream) throws IOException {
        int size = inputStream.available();

        ByteBuffer byteBuffer = ByteBuffer.allocateDirect(size);
        if (inputStream.read(byteBuffer.array(), byteBuffer.arrayOffset(), size) != size) {
            throw new IOException("Could not read the full size of the input stream");
        }
        byteBuffer.order(ByteOrder.nativeOrder());
        byteBuffer.rewind();

        return byteBuffer;
    }

    private static ByteBuffer extractMetadata(ByteBuffer modelBinaryBuffer) throws IOException {
        MetadataExtractor metadataExtractor = new MetadataExtractor(modelBinaryBuffer);

        try (InputStream metadataStream = metadataExtractor.getAssociatedFile("metadata.json")) {
            return loadInputStream(metadataStream);
        }
    }

    private static native long _createNativeSegmentationProcessor(ByteBuffer modelBinary, ByteBuffer metadata,
                                                                  int computeUnit);
    private static native void _deleteNativeSegmentationProcessor(long nativeSegmentationProcessor);

    private static native int[] _nativeOutputSizeForInputSize(long nativeSegmentationProcessor, Size inputSize);

    private static native Mat _nativeOutputMatForInputSize(long nativeSegmentationProcessor, Size inputSize);

    private static native Mat _nativeRunSegmentationAndReturnResult(long nativeSegmentationProcessor, long inputMat);

    private static native void _runNativeSegmentation(long nativeSegmentationProcessor, long input, long output);
}
