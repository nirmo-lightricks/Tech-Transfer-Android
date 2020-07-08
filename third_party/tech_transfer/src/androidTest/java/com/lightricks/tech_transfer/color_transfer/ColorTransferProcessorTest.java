// Copyright (c) 2020 Lightricks. All rights reserved.
// Created by Nir Moshe.

package com.lightricks.tech_transfer.color_transfer;

import static com.lightricks.common.testutils.MatSubject.assertThat;

import java.io.InputStream;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import org.junit.After;
import org.junit.Test;
import org.opencv.android.Utils;
import org.opencv.core.CvType;
import org.opencv.core.Mat;

public class ColorTransferProcessorTest {
    static {
        System.loadLibrary("c++_shared");
        System.loadLibrary("opencv_java3");
        System.loadLibrary("tech_transfer");
    }

    private Mat input;
    private  Mat reference;
    private  Mat result;

    private Bitmap loadTestImage(final String name) {
        InputStream inputStream = getClass().getClassLoader().getResourceAsStream(name);
        return BitmapFactory.decodeStream(inputStream);
    }

    @After
    public void releaseMats() throws Exception {
       input.release();
       reference.release();
       if (result != null) {
           result.release();
       }
    }

    @Test
    public void generateLUT_lowDampingFactor() {
        Bitmap inputBitmap = loadTestImage("images/LTColorTransferInput.png");
        Bitmap referenceBitmap = loadTestImage("images/LTColorTransferReference.png");

        input = new Mat(inputBitmap.getHeight(), inputBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(inputBitmap, input);
        reference = new Mat(referenceBitmap.getHeight(), referenceBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(referenceBitmap, reference);

        result = ColorTransferProcessor.generateLUT(input, reference, 0.2f);

        Bitmap expectedLUTBitmap = loadTestImage("images/expected_lut_0.2.png");
        Mat expectedLUT = new Mat(expectedLUTBitmap.getHeight(), expectedLUTBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(expectedLUTBitmap, expectedLUT);


        assertThat(result).closeToMatWithin(expectedLUT, 3);
        expectedLUT.release();
        inputBitmap.recycle();
        referenceBitmap.recycle();
        expectedLUTBitmap.recycle();
    }

    @Test
    public void generateLUT_highDampingFactor() {
        Bitmap inputBitmap = loadTestImage("images/LTColorTransferInput.png");
        Bitmap referenceBitmap = loadTestImage("images/LTColorTransferReference.png");

        input = new Mat(inputBitmap.getHeight(), inputBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(inputBitmap, input);
        reference = new Mat(referenceBitmap.getHeight(), referenceBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(referenceBitmap, reference);

        result = ColorTransferProcessor.generateLUT(input, reference, 0.5f);

        Bitmap expectedLUTBitmap = loadTestImage("images/expected_lut_0.5.png");
        Mat expectedLUT = new Mat(expectedLUTBitmap.getHeight(), expectedLUTBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(expectedLUTBitmap, expectedLUT);

        assertThat(result).closeToMatWithin(expectedLUT, 3);
        expectedLUT.release();
        inputBitmap.recycle();
        referenceBitmap.recycle();
        expectedLUTBitmap.recycle();
    }

    @Test
    public void generateLUT_20Iterations() {
        Bitmap inputBitmap = loadTestImage("images/LTColorTransferInput.png");
        Bitmap referenceBitmap = loadTestImage("images/LTColorTransferReference.png");

        input = new Mat(inputBitmap.getHeight(), inputBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(inputBitmap, input);
        reference = new Mat(referenceBitmap.getHeight(), referenceBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(referenceBitmap, reference);

        result = ColorTransferProcessor.generateLUT(input, reference, 0.3f, 20);

        Bitmap expectedLUTBitmap = loadTestImage("images/expected_lut_20iterations.png");
        Mat expectedLUT = new Mat(expectedLUTBitmap.getHeight(), expectedLUTBitmap.getWidth(), CvType.CV_8UC4);
        Utils.bitmapToMat(expectedLUTBitmap, expectedLUT);

        assertThat(result).closeToMatWithin(expectedLUT, 3);
        expectedLUT.release();
        inputBitmap.recycle();
        referenceBitmap.recycle();
        expectedLUTBitmap.recycle();
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyInputType() {
        input = new Mat(1, 1, CvType.CV_8UC1);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyReferenceType() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_32FC4);
        ColorTransferProcessor.generateLUT(input, reference);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyDampingFactorUnder1() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference, 1.2f);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyDampingFactorOver0() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference, 0.f);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyIterationsOver1() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference, 0.5f, 0);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyIterationsUnder50() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference, 0.5f, 51);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyHistogramBinsOver4() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference, 0.5f, 10, 3);
    }

    @Test(expected = IllegalArgumentException.class)
    public void genreateLUT_verifyHistogramBinsUnder256() {
        input = new Mat(1, 1, CvType.CV_8UC4);
        reference = new Mat(1, 1, CvType.CV_8UC4);
        ColorTransferProcessor.generateLUT(input, reference, 0.5f, 10, 257);
    }
}
