//
// Created by Gershon Hochman on 22/05/2022.
//

#ifndef FACETUNE_ANDROID_LOG_H
#define FACETUNE_ANDROID_LOG_H

#include <android/log.h>

#define  LOG_DEFAULT_TAG    "LTLog"

#define  LogDebug(...)  __android_log_print(ANDROID_LOG_DEBUG, LOG_DEFAULT_TAG, __VA_ARGS__)
#define  LogInfo(...)  __android_log_print(ANDROID_LOG_INFO, LOG_DEFAULT_TAG, __VA_ARGS__)
#define  LogWarning(...)  __android_log_print(ANDROID_LOG_WARN, LOG_DEFAULT_TAG, __VA_ARGS__)
#define  LogError(...)  __android_log_print(ANDROID_LOG_ERROR, LOG_DEFAULT_TAG, __VA_ARGS__)

#define  LogDebugT(tag, ...)  __android_log_print(ANDROID_LOG_DEBUG, tag, __VA_ARGS__)
#define  LogErrorT(tag, ...)  __android_log_print(ANDROID_LOG_ERROR, tag, __VA_ARGS__)
#define  LogWarningT(tag, ...)  __android_log_print(ANDROID_LOG_WARN, tag, __VA_ARGS__)
#define  LogErrorT(tag, ...)  __android_log_print(ANDROID_LOG_ERROR, tag, __VA_ARGS__)

#define ASSERT(condition, ...)                                                            \
  do {                                                                                    \
    if(!(condition))                                                                      \
      __android_log_assert(#condition, LOG_DEFAULT_TAG, __VA_ARGS__);                     \
  } while(0)

#endif //FACETUNE_ANDROID_LOG_H
