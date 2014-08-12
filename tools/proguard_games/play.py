# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner.

import argparse


def print_range(start, finish):
    current = start
    while current <= finish:
        print unichr(current).encode("utf-8")
        current += 1

def print_chinese():
    print_range(0x5000, 0x62ff)

def print_ethiopic():
    print_range(0x1200, 0x137f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print obfuscation dictionary for ProGuard.")
    args = parser.parse_args()

    print_ethiopic()
