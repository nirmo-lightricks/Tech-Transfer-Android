// Copyright (c) 2023 Lightricks. All rights reserved.
// Created by Nir Moshe.

plugins {
    id("com.android.library")
    id("com.lightricks.plugins.publishing-plugin")
}

ltPublishing {
    version = "1.0.0"
    withFlavors = false
    libraryName = "tech-transfer_color-transfer"
}

android {
    namespace = "com.lightricks.tech_transfer.color_transfer"
    compileSdk = 33

    defaultConfig {
        minSdk = 24
        targetSdk = 33

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        externalNativeBuild {
            cmake {
                arguments("-DANDROID_STL=c++_shared",
                          "-DANDROID_ARM_MODE=thumb",
                          "-DANDROID_CPP_FEATURES=rtti exceptions")
            }
        }
    }

    externalNativeBuild {
        cmake {
            path = File(project.projectDir, "src/main/cpp/CMakeLists.txt")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    buildFeatures {
        prefab = true
    }
}

dependencies {
    implementation("com.lightricks:opencv_android:4.5.5")

    // Guava
    implementation("com.google.guava:guava:28.1-android")

    implementation("androidx.appcompat:appcompat:1.0.2")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("com.lightricks:testutils:1.0.0")

    // Truth.
    val truthVersion = "1.1"
    testImplementation("com.google.truth:truth:$truthVersion")
    androidTestImplementation("com.google.truth:truth:$truthVersion")
}
