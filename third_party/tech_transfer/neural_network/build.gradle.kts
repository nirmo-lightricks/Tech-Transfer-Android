plugins {
    id("com.android.library")
    id("com.lightricks.plugins.publishing-plugin")
}

ltPublishing {
    version = "1.0.1"
    withFlavors = false
    libraryName = "tech-transfer_neural-network"
}

android {
    namespace = "com.lightricks.tech_transfer.neural_network"
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
        prefabPublishing = true
    }

    prefab {
        create("tensorflowlite_gpu_jni") {
            headers = "src/main/cpp/tensorflow-lite/headers"
        }

        create("tensorflowlite_jni") {
            headers = "src/main/cpp/tensorflow-lite/headers"
        }
    }

    packagingOptions {
        pickFirst("**/libtensorflowlite_gpu_jni.so")
        pickFirst("**/libtensorflowlite_jni.so")
    }
}

dependencies {
    implementation("com.lightricks:opencv_android:4.5.5")

    implementation("org.tensorflow:tensorflow-lite-metadata:0.1.0")
    implementation("org.tensorflow:tensorflow-lite-gpu:2.6.0")
    implementation("org.tensorflow:tensorflow-lite:2.6.0")

    // Guava
    implementation("com.google.guava:guava:28.1-android")

    // Truth.
    val truthVersion = "1.1"
    testImplementation("com.google.truth:truth:$truthVersion")
    androidTestImplementation("com.google.truth:truth:$truthVersion")

    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.8.0")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}