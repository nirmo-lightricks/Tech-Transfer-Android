# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner

import math
import random


key = "%s: %02X %02X"

clear_strings = {
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
    "SIGNATURES_SIG": "[Landroid/content/pm/Signature;"
}


def encrypt(str):
    local_key = key
    if len(local_key) < len(str):
        n = int(math.ceil(1.0 * len(str) / len(local_key)))
        local_key *= n

    return list(ord(a) ^ ord(b) for a, b in zip(str, local_key))


def print_obfuscated_code():
    i = 0
    static = "static const unsigned char name[] = {\n"
    dictionary = ""

    for name in clear_strings:
        cipher = encrypt(clear_strings[name])
        static += ", ".join(str(x) for x in cipher) + ",\n"
        dictionary += "#define " + name + " " + str(i) + ", " + str(i + len(cipher)) + "\n"
        i += len(cipher)
    static += ", ".join([str(random.randint(0, 255)) for x in xrange(random.randint(1, 10))]) + "};\n"

    print static
    print dictionary

    print '#define KEY "' + key + '"'
    print "#define KEYLEN " + str(len(key)) + "\n"


if __name__ == "__main__":
    print_obfuscated_code()
