// Copyright (c) 2020 Lightricks. All rights reserved.
// Created by Nir Moshe.

package com.lightricks.tech_transfer.color_transfer;

import static com.lightricks.common.testutils.MatSubject.assertThat;
import static com.google.common.truth.Truth.assertThat;

import java.io.InputStream;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import org.junit.After;
import org.junit.Test;
import org.opencv.android.Utils;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Scalar;

public class ColorTransferProcessorTest {
    static {
        System.loadLibrary("c++_shared");
        System.loadLibrary("opencv_java4");
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
       if (reference != null) {
           reference.release();
       }
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

    @Test
    public void getMaskedInput() {
        input = new Mat(2, 2, CvType.CV_8UC4);
        input.submat(0, 1, 0,1).setTo(new Scalar(255.0, 0.0, 0.0, 255.0));
        input.submat(1, 2, 0,1).setTo(new Scalar(0.0, 255.0, 0.0, 255.0));
        input.submat(0, 1, 1,2).setTo(new Scalar(0.0, 0.0, 255.0, 255.0));
        input.submat(1, 2, 1,2).setTo(new Scalar(0.0, 255.0, 255.0, 255.0));

        Mat mask = new Mat(input.size(), CvType.CV_8UC1, Scalar.all(0.0));

        mask.submat(0, 1, 0,1).setTo(Scalar.all(255.0));
        mask.submat(1, 2, 1,2).setTo(Scalar.all(255.0));

        Mat expectedMat = new Mat(2,1, input.type());
        expectedMat.submat(0, 1, 0,1).setTo(new Scalar(255.0, 0.0, 0.0, 255.0));
        expectedMat.submat(1, 2, 0,1).setTo(new Scalar(0.0, 255.0, 255.0, 255.0));

        short threshold = 178;
        Mat result = ColorTransferProcessor.getMaskedInput(input, mask, threshold);
        assertThat(result).closeToMatWithin(expectedMat, 1);

        mask.release();
        result.release();
        expectedMat.release();
    }

    @Test
    public void getMaskedInput_withAnEmptyMask_shouldReturnAnEmptyMatWithTheSameTypeAsTheInputMat() {
        input = new Mat(2, 2, CvType.CV_8UC4);
        input.submat(0, 1, 0,1).setTo(new Scalar(255.0, 0.0, 0.0, 255.0));
        input.submat(1, 2, 0,1).setTo(new Scalar(0.0, 255.0, 0.0, 255.0));
        input.submat(0, 1, 1,2).setTo(new Scalar(0.0, 0.0, 255.0, 255.0));
        input.submat(1, 2, 1,2).setTo(new Scalar(0.0, 255.0, 255.0, 255.0));

        Mat mask = new Mat(input.size(), CvType.CV_8UC1, Scalar.all(0.0));

        Mat expectedMat = new Mat(0,0, input.type());

        short threshold = 178;
        Mat result = ColorTransferProcessor.getMaskedInput(input, mask, threshold);
        assertThat(result).closeToMatWithin(expectedMat, 1);
        assertThat(result.type()).isEqualTo(input.type());

        mask.release();
        result.release();
        expectedMat.release();
    }
}
