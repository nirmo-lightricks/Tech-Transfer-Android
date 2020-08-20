//
// Created by Itai Shaked on 2020-05-10.
//

#include "ColorTransferProcessor.h"
#include <opencv2/imgproc.hpp>

namespace lit_color_transfer {

    static inline float interpolate(float value, float scale, float offset, const cv::Mat1f &lut);
    static inline float mix(float x, float y, float a);

    /// Precomputed optimal rotations to apply. See LTColorTransferProcessor+OptimalRotations.h
    static const std::array<float, 50 * 9> kOptimalRotations =
            {{
                     1.000000, 0.000000, 0.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 1.000000,
                     -0.333333, 0.666667, -0.666667, 0.666667, -0.333333, -0.666667, -0.666667, -0.666667, -0.333333,
                     -0.57735, -0.57735, 0.57735, -0.211325, -0.577351, -0.788675, 0.788675, -0.57735, 0.211325,
                     -0.474484, 0.192263, -0.859011, 0.408249, -0.816496, -0.408248, -0.779871, -0.544397, 0.308923,
                     -0.780935, -0.313619, -0.54017, 0.304876, -0.946182, 0.10858, -0.545152, -0.079891, 0.834522,
                     -0.926299, 0.124164, -0.355744, 0.2456, -0.517047, -0.819965, -0.285747, -0.846904, 0.448445,
                     -0.925057, 0.310561, 0.218679, 0.061753, -0.445103, 0.893348, 0.374774, 0.839902, 0.392568,
                     -0.875593, -0.020039, 0.482633, -0.436572, -0.394792, -0.808421, 0.20674, -0.918552, 0.336929,
                     -0.409933, 0.305374, 0.859478, 0.731656, -0.452568, 0.509766, 0.544642, 0.837812, -0.037906,
                     -0.864129, -0.42108, -0.275631, -0.151112, -0.30532, 0.940183, -0.480048, 0.854091, 0.200206,
                     -0.037241, 0.893516, 0.447485, -0.775106, -0.308463, 0.551418, 0.630733, -0.326313, 0.704057,
                     -0.340452, -0.138035, -0.930075, 0.799858, -0.562512, -0.209302, -0.494287, -0.815185, 0.301917,
                     -0.218248, 0.700512, 0.679449, -0.024753, -0.699982, 0.713731, 0.975579, 0.138952, 0.170109,
                     -0.500586, -0.327453, 0.801367, 0.664408, -0.738752, 0.113166, 0.554955, 0.589084, 0.587371,
                     -0.94244, 0.139148, 0.304046, -0.189864, -0.971186, -0.144048, 0.275242, -0.193484, 0.941704,
                     -0.466045, 0.808383, -0.359609, -0.878412, -0.471364, 0.078799, -0.105807, 0.352608, 0.929770,
                     -0.751672, -0.137061, -0.645138, -0.336297, -0.761804, 0.553678, -0.567356, 0.633142, 0.526534,
                     -0.275576, 0.005194, 0.961265, 0.89476, -0.364134, 0.258478, 0.351372, 0.931332, 0.095699,
                     -0.3872, 0.572414, -0.722785, -0.920948, -0.202759, 0.332781, 0.043937, 0.794501, 0.605672,
                     -0.605659, -0.184154, -0.774122, 0.79125, -0.242404, -0.561395, -0.084268, -0.952538, 0.292526,
                     -0.896272, 0.443171, -0.017217, -0.345335, -0.721713, -0.599896, -0.278283, -0.531724, 0.799893,
                     -0.77771, -0.627429, -0.038731, 0.073212, -0.151596, 0.985727, -0.624346, 0.763774, 0.163833,
                     -0.752964, 0.081548, -0.65299, -0.652431, -0.222038, 0.724591, -0.0859, 0.971622, 0.220391,
                     -0.976587, -0.19933, 0.0809, 0.035752, -0.521227, -0.852669, 0.21213, -0.829813, 0.51615,
                     -0.599198, 0.606377, -0.522751, -0.598892, -0.772814, -0.20997, -0.53131, 0.187258, 0.826223,
                     -0.889327, -0.180867, -0.419982, 0.437683, -0.602638, -0.667279, -0.132408, -0.777248, 0.615104,
                     -0.963285, 0.26538, 0.04068, -0.093175, -0.188343, -0.977673, -0.251793, -0.945569, 0.206155,
                     -0.488806, -0.002035, -0.87239, -0.800732, -0.395863, 0.449579, -0.346262, 0.918307, 0.191870,
                     -0.68521, -0.586932, -0.431275, 0.728287, -0.544614, -0.415924, 0.00924, -0.599088, 0.800630,
                     -0.885293, 0.274999, -0.375008, -0.440172, -0.235396, 0.866509, 0.150014, 0.932183, 0.329441,
                     -0.499147, 0.838382, -0.219017, -0.150241, -0.332661, -0.931002, -0.853393, -0.431802, 0.292006,
                     -0.570738, 0.512497, 0.641564, 0.497046, -0.406289, 0.766729, 0.653607, 0.756489, -0.022850,
                     -0.773739, 0.633294, 0.016308, -0.446324, -0.526675, -0.72347, -0.44958, -0.567055, 0.690164,
                     -0.072432, 0.982531, -0.171427, -0.950445, -0.120099, -0.28676, -0.302339, 0.142161, 0.942540,
                     -0.529605, 0.554033, -0.642313, -0.799574, -0.073256, 0.596083, 0.283197, 0.829265, 0.481787,
                     -0.944348, -0.328132, 0.02317, 0.277497, -0.832482, -0.479551, 0.176644, -0.446433, 0.877208,
                     -0.822908, 0.320829, 0.468926, -0.081794, -0.883616, 0.461012, 0.562257, 0.341015, 0.753377,
                     -0.097414, 0.461733, 0.881653, 0.772583, -0.523362, 0.359455, 0.627397, 0.716166, -0.305744,
                     -0.241587, -0.146079, 0.959321, -0.904828, -0.323276, -0.27709, 0.350602, -0.934962, -0.054077,
                     -0.67749, 0.121521, -0.725424, -0.18419, -0.982863, 0.007373, -0.712096, 0.138611, 0.688263,
                     -0.132967, -0.687154, -0.71424, 0.98257, 0.003065, -0.18587, 0.12991, -0.726505, 0.674769,
                     -0.694669, 0.681864, 0.229122, -0.286927, 0.029427, -0.9575, -0.659627, -0.730887, 0.175203,
                     -0.870073, 0.069341, -0.488021, 0.169348, -0.887742, -0.428059, -0.462918, -0.455088, 0.760658,
                     -0.354359, 0.874309, -0.331684, -0.618928, 0.046595, 0.784064, 0.700969, 0.483129, 0.524623,
                     -0.012571, 0.2749, -0.961391, 0.893611, -0.428323, -0.13416, -0.448667, -0.860795, -0.240269,
                     -0.25337, -0.701829, 0.665763, 0.96694, -0.163243, 0.195903, -0.028809, 0.693389, 0.719987,
                     -0.59509, 0.803108, -0.029761, -0.723073, -0.518888, 0.455984, 0.350761, 0.292871, 0.889490,
                     -0.420586, 0.398695, 0.814954, -0.818943, -0.553406, -0.151905, 0.390436, -0.73129, 0.559263,
                     -0.932096, -0.045652, 0.359322, -0.054552, -0.963017, -0.263861, 0.358079, -0.265545, 0.895134,
                     -0.923427, 0.353549, -0.149282, 0.089157, -0.18071, -0.979487, -0.373273, -0.917795, 0.135351
             }};

    class OptimalRotations {
    public:
        std::vector<const cv::Mat1f> rotations;

        OptimalRotations() {
            for (int i = 0; i < 50; ++i) {
                cv::Mat1f rotation(3, 3);
                memcpy(rotation.data, kOptimalRotations.data() + 9 * i, 9 * sizeof(float));
                rotations.push_back(rotation);
            }
        }
    };

    const int ColorTransferProcessor::kGridSize = 16;
    static const OptimalRotations optimalRotations;

    const std::vector<const cv::Mat1f> ColorTransferProcessor::_rotations = optimalRotations.rotations;

    void ColorTransferProcessor::getMaskedInput(const cv::Mat4b &input, const cv::Mat1b &mask, uchar threshold,
                                                cv::Mat *output) {
        for(int row = 0; row < mask.rows; ++row) {
            for (int col = 0; col < mask.cols; ++col) {
                if(mask.at<uchar>(row, col) > threshold) {
                    output -> push_back(input.at<cv::Vec4b>(row, col));
                }
            }
        }
    }

    void ColorTransferProcessor::generateLUT(const cv::Mat4b &input, const cv::Mat4b &reference, float dampingFactor,
                                             cv::Mat *outputLUT) const {
        auto inputNoAlpha = convertToFloat(input);
        auto referenceNoAlpha = convertToFloat(reference);
        cv::Mat3f inputTransformed(inputNoAlpha.size());
        cv::Mat3f referenceTransformed(referenceNoAlpha.size());

        float inputCount = input.total();
        float referenceCount = reference.total();

        auto grid = createIdentityGrid();

        // Scale between number of bins in the inverse CDF and the number of bins in the CDF. This is used to make sure
        // no values in the CDF are skipped when constructing the inverse CDF in cases where the slope of the CDF is
        // low.
        static const int kInverseCDFScale = 20;

        cv::Scalar inputMinValues, referenceMinValues, inputMaxValues, referenceMaxValues;
        cv::Mat1f histogram(_histogramBins, 1);
        cv::Mat1f inputCDF(_histogramBins, 1), referenceCDF(_histogramBins, 1);
        cv::Mat1f inverseCDF(_histogramBins * kInverseCDFScale, 1);

        for (int i = 0; i < _iterations; ++i) {
            auto &transform = _rotations[i];
            cv::transform(inputNoAlpha, inputTransformed, transform);
            cv::transform(referenceNoAlpha, referenceTransformed, transform);
            cv::transform(grid, grid, transform);

            findMinMaxPerChannel(inputTransformed, &inputMinValues, &inputMaxValues);
            findMinMaxPerChannel(referenceTransformed, &referenceMinValues, &referenceMaxValues);

            for (int channel = 0; channel < 3; ++channel) {
                auto channelMin = (float) std::min(inputMinValues[channel], referenceMinValues[channel]);
                auto channelMax = (float) std::max(inputMaxValues[channel], referenceMaxValues[channel]);

                computeCDF(inputTransformed, channel, channelMin, channelMax, 1 / inputCount, &histogram, &inputCDF);
                computeCDF(referenceTransformed, channel, channelMin, channelMax, 1 / referenceCount, &histogram,
                           &referenceCDF);

                computeInverseCDF(referenceCDF, kInverseCDFScale, channelMin, channelMax, &inverseCDF);

                specifyHistogram(inputCDF, inverseCDF, channelMin, channelMax, channel, dampingFactor, &grid);
                specifyHistogram(inputCDF, inverseCDF, channelMin, channelMax, channel, dampingFactor,
                                 &inputTransformed);
            }
            cv::transform(grid, grid, transform.t());
            cv::transform(inputTransformed, inputNoAlpha, transform.t());
        }

        cv::Mat3b result3c;
        grid.convertTo(result3c, CV_8U, 255);
        cv::cvtColor(result3c, *outputLUT, cv::ColorConversionCodes::COLOR_RGB2RGBA);
    }

    cv::Mat3f ColorTransferProcessor::createIdentityGrid() const {
        const int kSizes[3]{kGridSize, kGridSize, kGridSize};
        cv::Mat3f grid(3, kSizes);
        for (int b = 0; b < kGridSize; ++b) {
            for (int g = 0; g < kGridSize; ++g) {
                for (int r = 0; r < kGridSize; ++r) {
                    cv::Vec3f &rgbColor = grid(b, g, r);
                    rgbColor[0] = ((float)r) / (kGridSize - 1);
                    rgbColor[1] = ((float)g) / (kGridSize - 1);
                    rgbColor[2] = ((float)b) / (kGridSize - 1);
                }
            }
        }
        grid = grid.reshape(0, {kGridSize * kGridSize, kGridSize});
        return grid;
    }

    cv::Mat3f ColorTransferProcessor::convertToFloat(const cv::Mat4b &mat) const {
        cv::Mat4f matFloat;
        mat.convertTo(matFloat, CV_32F, 1 / 255.);
        matFloat = matFloat.reshape(0, matFloat.total());
        cv::Mat3f floatNoAlpha(matFloat.size());
        cv::mixChannels(matFloat, floatNoAlpha, {0, 0, 1, 1, 2, 2});
        return floatNoAlpha;
    }

    void ColorTransferProcessor::findMinMaxPerChannel(const cv::Mat3f &mat, cv::Scalar *minimum, cv::Scalar *maximum)
        const {
#if CV_NEON
        // This is faster on devices with Neon support (most ARM processors)
        assert(mat.cols == 1);
        float32x4_t minVec = vmovq_n_f32(std::numeric_limits<float>::max());
        float32x4_t maxVec = vmovq_n_f32(-std::numeric_limits<float>::max());
        for (int i = 0; i < mat.rows; ++i) {
            float32x4_t vec = vld1q_f32((float*)mat.ptr(i));
            minVec  = vminq_f32(vec, minVec);
            maxVec = vmaxq_f32(vec, maxVec);
        }

        float minmaxValues[4];
        vst1q_f32(minmaxValues, minVec);
        (*minimum)[0] = minmaxValues[0];
        (*minimum)[1] = minmaxValues[1];
        (*minimum)[2] = minmaxValues[2];

        vst1q_f32(minmaxValues, maxVec);
        (*maximum)[0] = minmaxValues[0];
        (*maximum)[1] = minmaxValues[1];
        (*maximum)[2] = minmaxValues[2];
#else
        // Non-Neon version for emulator (x86) support
        cv::Mat channelsAsColumns = mat.reshape(1, mat.total());
        for (int i = 0; i < 3; ++i) {
            double min, max;
            cv::minMaxLoc(channelsAsColumns.col(i), &min, &max);
            (*minimum)[i] = min;
            (*maximum)[i] = max;
        }
#endif
    }

    void ColorTransferProcessor::computeCDF(const cv::Mat3f &mat, int channel, float min, float max, float factor,
                                            cv::Mat1f *tempHistogram, cv::Mat1f *outCDF) const {
        // cv::calcHist does not include the maximum range, but we don't want to affect the bin size, so add
        // epsilon to the channel maximum for histogram calculation purposes.
        cv::calcHist(std::vector<cv::Mat>{mat}, {channel}, cv::noArray(), *tempHistogram, {_histogramBins},
                     {min, max + 1e-6f});
        cv::GaussianBlur(*tempHistogram, *tempHistogram, {1, 7}, 0, 1, cv::BorderTypes::BORDER_CONSTANT);

        float sum = 0;
        for (int i = 0; i < tempHistogram->rows; ++i) {
            sum += (*tempHistogram)(i);
            (*outCDF)(i) = sum * factor;
        }
    }

    void ColorTransferProcessor::computeInverseCDF(const cv::Mat1f &cdf, int binCountFactor, float min, float max,
                                                   cv::Mat1f *outInverseCDF) const {
        const float scale = max - min;
        int cdfIndex = 0;
        for (int i = 0; i < cdf.rows * binCountFactor; ++i) {
            float v = i / float(cdf.rows * binCountFactor - 1);
            float minIndex = cdf.rows - 1;
            for (; cdfIndex < cdf.rows; ++cdfIndex) {
                if (cdf(cdfIndex, 0) > v) {
                    if (cdfIndex == 0) {
                        minIndex = cdfIndex;
                    } else {
                        float a = cdf(cdfIndex - 1, 0);
                        float b = cdf(cdfIndex, 0);
                        float alpha = (v - a) / (b - a);
                        minIndex = cdfIndex - 1 + alpha;
                    }
                    break;
                }
            }
            auto index = minIndex / (cdf.rows - 1);
            (*outInverseCDF)(i, 0) = min + index * scale;
        }
    }

    void ColorTransferProcessor::specifyHistogram(const cv::Mat1f &inputCDF, const cv::Mat1f &inverseCDF, float min,
                                                  float max, int channel, float dampingFactor,
                                                  cv::Mat3f *values) const {
        const float scale = max - min;
        const float inputCDFScale = (inputCDF.rows - 1) / scale;
        const float inputCDFOffset = -min * inputCDFScale;
        const float inverseCDFScale = inverseCDF.rows - 1;
        const float inverseCDFOffset = 0;

        values->forEach([dampingFactor, scale, channel, &inputCDF, &inverseCDF, inputCDFScale, inputCDFOffset,
                                inverseCDFScale, inverseCDFOffset](cv::Vec3f &value, const void *){
            float v = value[channel];
            v = interpolate(v, inputCDFScale, inputCDFOffset, inputCDF);
            v = interpolate(v, inverseCDFScale, inverseCDFOffset, inverseCDF);
            value[channel] = mix(value[channel], v, dampingFactor);
        });
    }

    /// Interpolates the given value by applying the scale and offset and interpolating between the respective elements
    /// in the given lut.
    /// @note The lut matrix is assumed to be a single-column matrix.
    static inline float interpolate(float value, float scale, float offset, const cv::Mat1f &lut) {
        float p = scale * value + offset;
        float a = float(p < 0);
        float b = float(p >= 0 && p < lut.rows - 1);
        float c = float(p >= float(lut.rows - 1));

        p = std::clamp(p, 0.f, float(lut.rows - 1));
        float q = std::trunc(p);
        float r = p - q;
        return a * lut(0) + b * mix(lut(int(q)), lut(std::min(int(q) + 1, lut.rows - 1)), r) + c * lut(lut.rows - 1);
    }

    static inline float mix(float x, float y, float a) {
        return x + (y - x) * a;
    }
};
