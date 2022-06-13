package com.lightricks.tech_transfer.neural_network;

import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;

import android.content.Context;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import com.google.common.truth.Truth;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.opencv.android.Utils;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Size;

import androidx.test.platform.app.InstrumentationRegistry;

public class SegmentationProcessorTest {
    static {
        System.loadLibrary("c++_shared");
        System.loadLibrary("opencv_java4");
        System.loadLibrary("tech_transfer");
    }

    private SegmentationProcessor segmentationProcessor;

    private Mat loadTestMat(final String name) {
        InputStream inputStream = getClass().getClassLoader().getResourceAsStream(name);
        Bitmap bitmap = BitmapFactory.decodeStream(inputStream);

        Mat mat = new Mat(bitmap.getHeight(), bitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(bitmap, mat);
        bitmap.recycle();
        return mat;
    }

    private ByteBuffer loadFile(AssetManager assetManager, String filePath) {
        try (InputStream inputStream = assetManager.open(filePath)) {
            return SegmentationProcessor.loadInputStream(inputStream);
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    @Before
    public void createSegmentationProcessor() throws IOException {
        Context context = InstrumentationRegistry.getInstrumentation().getTargetContext();
        ByteBuffer modelBinaryBuffer = loadFile(context.getAssets(), "schemas/person_segmentation_3.tflite");

        segmentationProcessor = new SegmentationProcessor(modelBinaryBuffer, ComputeUnit.CPU);
    }

    @After
    public void cleanup() {
        segmentationProcessor.recycle();
        segmentationProcessor = null;
    }

    @Test
    public void calculateOutputSize() {
        Size inputSize = new Size(600, 800);

        int outputSize[] = segmentationProcessor.outputSizeForInputSize(inputSize);
        int expectedOutputSize[] = new int[] {512, 384, 1};

        Truth.assertThat(outputSize).isEqualTo(expectedOutputSize);
    }

    @Test
    public void createOutputMat() {
        Size inputSize = new Size(600, 800);
        int expectedOutputSize[] = new int[] {512, 384, 1};

        Mat outputMat = segmentationProcessor.outputMatForInputSize(inputSize);
        int outputRows = outputMat.rows();
        int outputCols = outputMat.cols();
        int outputChannels = outputMat.channels();
        outputMat.release();

        Truth.assertThat(outputRows).isEqualTo(expectedOutputSize[0]);
        Truth.assertThat(outputCols).isEqualTo(expectedOutputSize[1]);
        Truth.assertThat(outputChannels).isEqualTo(expectedOutputSize[2]);
    }

    @Test
    public void runSegmentation() {
        Mat inputMat = loadTestMat("images/person.png");

        Mat expectedMatRGBA = loadTestMat("images/person_segmentation_512_output.png");
        Mat expectedMat = new Mat();
        Core.extractChannel(expectedMatRGBA, expectedMat, 0);

        Mat outputMat = segmentationProcessor.outputMatForInputSize(inputMat.size());
        segmentationProcessor.runSegmentation(inputMat, outputMat);

        double averageDelta = Core.norm(outputMat, expectedMat, Core.NORM_L1) / outputMat.total();
        Truth.assertThat(averageDelta).isAtMost(0.05);

        expectedMatRGBA.release();
        inputMat.release();
        expectedMat.release();
        outputMat.release();
    }

    @Test
    public void runSegmentationAndReturnResult() {
        Mat inputMat = loadTestMat("images/person.png");

        Mat expectedMatRGBA = loadTestMat("images/person_segmentation_512_output.png");
        Mat expectedMat = new Mat();
        Core.extractChannel(expectedMatRGBA, expectedMat, 0);

        Mat outputMat = segmentationProcessor.runSegmentation(inputMat);

        double averageDelta = Core.norm(outputMat, expectedMat, Core.NORM_L1) / outputMat.total();
        Truth.assertThat(averageDelta).isAtMost(0.05);

        expectedMatRGBA.release();
        inputMat.release();
        expectedMat.release();
        outputMat.release();
    }
}
