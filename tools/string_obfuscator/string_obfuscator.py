# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner

import math
import random
import argparse

from strings import get_strings


key = "%s: %02X %02X"


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
    clear_strings = get_strings()

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
    parser = argparse.ArgumentParser(description="Obfuscate strings and print C code to recreate them.")
    args = parser.parse_args()

    print_obfuscated_code()
