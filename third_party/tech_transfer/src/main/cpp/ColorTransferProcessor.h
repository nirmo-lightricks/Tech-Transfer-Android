//
// Created by Itai Shaked on 2020-05-10.
//

#ifndef TT_ANDROID_COLORTRANSFERPROCESSOR_H
#define TT_ANDROID_COLORTRANSFERPROCESSOR_H

#include "opencv2/core/core.hpp"

namespace lit_color_transfer {
    /// Class for performing color-transfer, i.e., given an input image and a reference image, construct a 3D LUT that
    /// can be used to convert the color distribution of the input to match that of the reference.
    class ColorTransferProcessor {
    public:
        ColorTransferProcessor() = delete;

        ColorTransferProcessor(int iterations = 10, int histogramBins = 32) :
            _iterations(iterations), _histogramBins(histogramBins) {}

        /// Generate a lookup table transforming the color distribution of \c input to that of
        /// \c reference, performing the number of iterations set at object initialization. The
        /// \c dampingFactor controls the rate of change at each iteration, with larger values
        /// resulting in larger change, but too large values may introduce some noise.
        void generateLUT(const cv::Mat4b &input, const cv::Mat4b &reference, float dampingFactor,
                         cv::Mat *outputLUT) const;

        /// The size of each dimension of the returned 3D LUT, i.e., the resulting LUT is a cube
        /// kGridSize x kGridSize x kGridSize large.
        static const int kGridSize;

    private:
        static const std::vector<const cv::Mat1f> _rotations;

        int _iterations;
        int _histogramBins;

        /// Returns an initialized identity grid, that is, a flattened 3D grid sized kGridSize x kGridSize x kGridSize
        /// where the value at the normalized coordinate (x, y, z) is (x, y, z). The grid 3D grid is flattened to
        /// kGridSize vertically-stacked slices, each kGridSize x kGridSize, to the returned matrix has
        /// kGridSize x kGridSize rows and kGridSize columns.
        /// This is the starting point of the algorithm, as this grid represents the identity LUT - applying it as is
        /// has no effect.
        cv::Mat3f createIdentityGrid() const;

        /// Converts a 4-channel uint8 matrix to a 3-channel float matrix by discarding the last channel and dividing by
        /// 255. The returned matrix is a single-column matrix.
        cv::Mat3f convertToFloat(const cv::Mat4b &mat) const;

        /// Finds the minimum and maximum for each channel in the input mat.
        /// @param mat Input matrix.
        /// @param minimum Output minimum value per channel.
        /// @param maximum Output maximum value per channel.
        /// @note The input matrix is assumed to be a single-column matrix.
        void findMinMaxPerChannel(const cv::Mat3f &mat, cv::Scalar *minimum, cv::Scalar *maximum) const;

        /// Computes the Cumulative Distribution Function for a given channel.
        /// @param mat Input matrix.
        /// @param channel Channel to process, must in range [0, 2].
        /// @param min Minimum value to consider.
        /// @param max Maximum value to consider.
        /// @param factor Normalization factor for the histogram. Should be one over the total number of input elements.
        /// @param tempHistogram Preallocated matrix to hold the histogram temporarily, passed in order to avoid
        /// reallocations. Must have size <code>_histogramBins x 1</code>.
        /// @param outCDF Preallocated matrix to hold the final CDF. Must be the same size as tempHistogram.
        /// @note The input, temporary histogram and output CDF are all assumed to be single-column matrices.
        void computeCDF(const cv::Mat3f &mat, int channel, float min, float max, float factor,
                        cv::Mat1f *tempHistogram, cv::Mat1f *outCDF) const;

        /// Computes the inverse CDF given a CDF and an expansion factor.
        /// @param cdf Input CDF.
        /// @param binCountFactor Inverse CDF expansion factor. The size of the inverse CDF is the size of the input CDF
        /// multiplied by this factor. This is needed  in order to ensure the inverse CDF quantization doesn't skip over
        /// values in the forward CDF in places where the slope of the forward CDF is low.
        /// @param min Minimum value considered when constructing the CDF.
        /// @param max Maximum value considered when constructing the CDF.
        /// @param outInverseCDF Output inverse CDF.
        /// @note The input CDF and output inverse CDF are assumed to be single-column matrices.
        void computeInverseCDF(const cv::Mat1f &cdf, int binCountFactor, float min, float max,
                               cv::Mat1f *outInverseCDF) const;

        /// Perform histogram specification step on a single channel, see
        /// https://en.wikipedia.org/wiki/Histogram_matching for more details.
        /// @param inputCDF CDF of the input image.
        /// @param inverseCDF Inverse CDF of the reference image.
        /// @param min Minimum value to consider in CDF and inverse CDF.
        /// @param max Maximum value to consider in CDF and inverse CDF.
        /// @param channel Channel to operate on.
        /// @param dampingFactor Mix factor between original value and computed value. The larger it is, the larger the
        /// step towards the reference histogram.
        /// @param mat Values to operate on.
        /// @note The CDF, inverse CDF and target matrix are all assumed to be single-column matrices.
        void specifyHistogram(const cv::Mat1f &inputCDF, const cv::Mat1f &inverseCDF, float min, float max, int channel,
                              float dampingFactor, cv::Mat3f *mat) const;
    };
};

#endif //TT_ANDROID_COLORTRANSFERPROCESSOR_H
