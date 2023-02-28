//
// Created by Gershon Hochman on 15/05/2022.
//

#include "ResizeProcessor.h"

#include <opencv2/imgproc.hpp>

#include "ResizeParams.h"

namespace neural_network {
namespace {
cv::InterpolationFlags cvInterpolation(ResizeStrategyInterpolation interpolation) {
    switch (interpolation) {
        case ResizeStrategyInterpolation::bilinear:
            return cv::InterpolationFlags::INTER_LINEAR;
        case ResizeStrategyInterpolation::nearest:
            return cv::InterpolationFlags::INTER_NEAREST;
    }
}

cv::BorderTypes cvAddressMode(ResizeStrategyAddressMode addressMode) {
    switch (addressMode) {
        case ResizeStrategyAddressMode::clampToZero:
            return cv::BorderTypes::BORDER_CONSTANT;
        case ResizeStrategyAddressMode::clampToEdge:
            return cv::BorderTypes::BORDER_REPLICATE;
    }
}

float logarithmOfDestinationToSourceRatio(const cv::Size &source, const cv::Size &destination) {
    return std::log2(std::min((float)destination.width / (float)source.width,
                              (float)destination.height / (float)source.height));
}

std::vector<cv::Size> intermediateSizes(const cv::Size &source, const cv::Size &destination) {
    float logOfRatio = logarithmOfDestinationToSourceRatio(source, destination);

    std::vector<cv::Size> result;
    cv::Size intermediateSize = source;
    if (logOfRatio < -1) {
        for (int i = 1; i < (int)std::ceil(-logOfRatio); ++i) {
            intermediateSize /= 2;
            result.push_back(intermediateSize);
        }
    } else if (logOfRatio > 1) {
        for (int i = 1; i < (int)std::ceil(logOfRatio); ++i) {
            intermediateSize *= 2;
            result.push_back(intermediateSize);
        }
    }

    return result;
}

cv::Mat resizedMat(const cv::Mat &sourceMat, const cv::Size &destinationSize, cv::InterpolationFlags interpolation) {
    auto sourceSize = sourceMat.size();
    cv::Mat destinationMat(destinationSize, sourceMat.type());

    cv::Size trimmedSourceSize = (destinationSize == sourceSize / 2) ? destinationSize * 2 : sourceSize;

    cv::resize(sourceMat(cv::Rect(cv::Point(0, 0), trimmedSourceSize)), destinationMat, destinationSize, 0, 0,
               interpolation);

    return destinationMat;
}

void resizeBySteps(const cv::Mat &sourceMat, const cv::Rect &sourceRect, cv::Mat *destinationMat,
                   const cv::Rect &destinationRect, cv::InterpolationFlags interpolation) {
    auto source = sourceMat(sourceRect);
    auto destination = (*destinationMat)(destinationRect);

    auto intermediateImageSizes = intermediateSizes(sourceRect.size(), destinationRect.size());
    for (auto &size : intermediateImageSizes) {
        source = resizedMat(source, size, interpolation);
    }

    cv::resize(source, destination, destination.size(), 0, 0, interpolation);
}

void resizeAxisAligned(const cv::Mat &input, const ResizeParams &resizeParams, cv::Mat *output) {
    auto inputRect = cv::Rect(std::round(resizeParams.inputRect.center.x - 0.5 * resizeParams.inputRect.size.width),
                              std::round(resizeParams.inputRect.center.y - 0.5 * resizeParams.inputRect.size.height),
                              std::round(resizeParams.inputRect.size.width),
                              std::round(resizeParams.inputRect.size.height));
    auto interpolation = cvInterpolation(resizeParams.interpolation);
    resizeBySteps(input, inputRect, output, resizeParams.outputRect, interpolation);
}

void duplicateRow(cv::Mat *output, int sourceRow, int startDestinationRow, int endDestinationRow) {
    for (int i = startDestinationRow; i < endDestinationRow; ++i) {
        memcpy(output->ptr(i), output->ptr(sourceRow), output->elemSize() * output->cols);
    }
}

void duplicateCol(cv::Mat *output, int sourceCol, int startDestinationCol, int endDestinationCol) {
    if (startDestinationCol >= endDestinationCol) {
        return;
    }
    for (int row = 0; row < output->rows; ++row) {
        for (int col = startDestinationCol; col < endDestinationCol; ++col) {
            memcpy(output->ptr(row, col), output->ptr(row, sourceCol), output->elemSize());
        }
    }
}

void warp(const cv::Mat &input, const ResizeParams &resizeParams, cv::Mat *output) {
    // The points array for storing input rectangle vertices.
    // The order is bottomLeft, topLeft, topRight, bottomRight.
    cv::Point2f inputPoints[4];
    resizeParams.inputRect.points(inputPoints);

    cv::Point2f outputPoints[] = {
        cv::Point2f((float)resizeParams.outputRect.tl().x, (float)resizeParams.outputRect.br().y),
        cv::Point2f((float)resizeParams.outputRect.tl().x, (float)resizeParams.outputRect.tl().y),
        cv::Point2f((float)resizeParams.outputRect.br().x, (float)resizeParams.outputRect.tl().y)
    };

    auto affineTransform = cv::getAffineTransform(inputPoints, outputPoints);

    auto addressMode = cvAddressMode(resizeParams.addressMode);

    cv::InterpolationFlags interpolationFlags = (resizeParams.interpolation == ResizeStrategyInterpolation::nearest) ?
            cv::InterpolationFlags::INTER_NEAREST : cv::InterpolationFlags::INTER_AREA;
    cv::warpAffine(input, *output, affineTransform, output->size(), interpolationFlags, addressMode);
}

void fillMargins(cv::Mat *output, const ResizeParams &resizeParams) {
    if (resizeParams.addressMode == ResizeStrategyAddressMode::clampToZero) {
        output->colRange(0, resizeParams.outputRect.x).setTo(cv::Scalar::all(0));
        output->colRange(resizeParams.outputRect.br().x, output->cols).setTo(cv::Scalar::all(0));
        output->rowRange(0, resizeParams.outputRect.y).setTo(cv::Scalar::all(0));
        output->rowRange(resizeParams.outputRect.br().y, output->rows).setTo(cv::Scalar::all(0));
    } else {
        duplicateRow(output, resizeParams.outputRect.y, 0, resizeParams.outputRect.y);
        duplicateRow(output, resizeParams.outputRect.br().y - 1, resizeParams.outputRect.br().y, output->rows);
        duplicateCol(output, resizeParams.outputRect.x, 0, resizeParams.outputRect.x);
        duplicateCol(output, resizeParams.outputRect.br().x - 1, resizeParams.outputRect.br().x, output->cols);
    }
}
}

cv::Mat resize(const cv::Mat &input, const ResizeParams &resizeParams) {
    cv::Mat output(resizeParams.outputSize, input.type());

    if (std::abs(resizeParams.inputRect.angle) < 1.e-5) {
        resizeAxisAligned(input, resizeParams, &output);
    } else {
        warp(input, resizeParams, &output);
    }

    fillMargins(&output, resizeParams);

    return output;
}
}
