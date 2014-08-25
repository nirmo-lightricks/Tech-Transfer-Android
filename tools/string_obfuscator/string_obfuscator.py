# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner

from math import ceil
from random import randint
from argparse import ArgumentParser
from datetime import date
from os import path

from strings import get_strings


key = "%s: %02X %02X"
basename = "StringStorage"

header = """// Copyright (c) %s Lightricks. All rights reserved.
// Generated automatically by string_obfuscator.py.
// Do not change manually. Commit to source control.

"""
decoder = """
__attribute__ ((visibility ("hidden"))) char* decode(int startIndex, int endIndex, char* out) {
    int len = endIndex - startIndex;
    int i = 0;
    const char *key = KEY;

    while (i < len) {
        out[i] = stringStorage[startIndex + i] ^ key[i % KEYLEN];
        i++;
    }
    out[i] = 0;

    return out;
}
"""
decoder_fwd = """
char* decode(int startIndex, int endIndex, char* out);

"""

def encrypt(str):
    local_key = key
    if len(local_key) < len(str):
        n = int(ceil(1.0 * len(str) / len(local_key)))
        local_key *= n

    return list(ord(a) ^ ord(b) for a, b in zip(str, local_key))


def write_cpp(file, static, key):
    year = date.today().year
    file.write(header % year)

    file.write(static + "\n")
    file.write('#define KEY "' + key + '"\n')
    file.write("#define KEYLEN " + str(len(key)) + "\n")

    file.write(decoder)


def write_h(file, dictionary):
    year = date.today().year
    file.write(header % year)

    protect = basename.upper() + "_H"
    file.write("#ifndef %s\n" % protect)
    file.write("#define %s\n\n" % protect)

    file.write(dictionary)
    file.write(decoder_fwd)

    file.write("#endif // %s\n" % protect)


def print_obfuscated_code(outdir):
    i = 0
    static = "static const unsigned char stringStorage[] = {\n"
    dictionary = ""
    clear_strings = get_strings()

    for name in clear_strings:
        cipher = encrypt(clear_strings[name])
        static += "    " + ", ".join(str(x) for x in cipher) + ",\n"
        dictionary += "#define " + name + " " + str(i) + ", " + str(i + len(cipher)) + "\n"
        i += len(cipher)
    static += "    " + ", ".join([str(randint(0, 255)) for x in xrange(randint(10, 20))]) + "\n};\n"

    cpp = open(path.join(outdir, basename + ".cpp"), "w")
    write_cpp(cpp, static, key)
    cpp.close()

    h = open(path.join(outdir, basename + ".h"), "w")
    write_h(h, dictionary)
    h.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="Obfuscate strings and print C code to recreate them.")
    parser.add_argument('--outdir', required=True, dest='outdir', help='output directory')
    args = parser.parse_args()

    print_obfuscated_code(args.outdir)
