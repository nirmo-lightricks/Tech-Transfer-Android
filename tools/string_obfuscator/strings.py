# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner.

def get_strings():
    return {
        # ShaderStorage:getShaderKey
        "APP_CLASS": "com/lightricks/facetune/FacetuneApplication",
        "PM_CLASS": "android/content/pm/PackageManager",
        "PI_CLASS": "android/content/pm/PackageInfo",
        "SIG_CLASS": "android/content/pm/Signature",
        "X509_CLASS": "javax/security/cert/X509Certificate",
        "MD_CLASS": "java/security/MessageDigest",
        "GET_APP_NAME": "getFacetuneApplication",
        "GET_APP_SIG": "()Lcom/lightricks/facetune/FacetuneApplication;",
        "GET_PM_NAME": "getPackageManager",
        "GET_PM_SIG": "()Landroid/content/pm/PackageManager;",
        "GET_PN_NAME": "getPackageName",
        "GET_PN_SIG": "()Ljava/lang/String;",
        "GET_PI_NAME": "getPackageInfo",
        "GET_PI_SIG": "(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;",
        "TO_BA_NAME": "toByteArray",
        "TO_BA_SIG": "()[B",
        "X509_GET_I_NAME": "getInstance",
        "X509_GET_I_SIG": "([B)Ljavax/security/cert/X509Certificate;",
        "MD_GET_I_NAME": "getInstance",
        "MD_GET_I_SIG": "(Ljava/lang/String;)Ljava/security/MessageDigest;",
        "DIGEST_NAME": "digest",
        "DIGEST_SIG": "([B)[B",
        "GET_ENCODE_NAME": "getEncoded",
        "GET_ENCODE_SIG":  "()[B",
        "SIGNATURES_NAME": "signatures",
        "SIGNATURES_SIG": "[Landroid/content/pm/Signature;",

        # ShaderStorage:registerShaderStorage
        "GET_SHADER_NAME": "glLog",
        "GET_SHADER_CLASS": "com/lightricks/facetune/gpu/GLUtils",
        "GET_SHADER_SIG": "(Ljava/lang/String;)Ljava/lang/String;",
    }
