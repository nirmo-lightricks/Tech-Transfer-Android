#!/usr/bin/env python

# Copyright (c) 2019 Lightricks. All rights reserved.

from __future__ import print_function, division
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import argparse
import binascii

def encrypt(input_file_path, output_file_path, key):
    data = ""
    with open(input_file_path, 'rb') as input_file:
        data = input_file.read()

    cipher = AES.new(key, AES.MODE_SIV)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(output_file_path, 'wb') as output_file:
        output_file.write(tag)
        output_file.write(ciphertext)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    key = binascii.a2b_hex("ea80a0bea95ea33ad91f823d71fbc499c758af91db870dc7a76b5e5dc0d12880")
    encrypt(args.input, args.output, key)

    print(binascii.b2a_hex(key))

if __name__ == "__main__":
    main()

