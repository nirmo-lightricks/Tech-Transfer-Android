#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner

import localizable
import argparse
from lxml import etree as ET
import os

from key_dict import get_key_dict


def adapt_string_android(str):
    str = str.encode("utf-8")
    str = str.replace("'", "\\'")
    str = str.replace("...", "…")
    str = str.replace("\n", "\\n")
    str = str.decode("utf-8")
    return str


def adapt_string_ios(str):
    str = str.replace("\\n", "\n")
    return str


def import_strings(input, base, output, empty_if_missing):
    input_dict = dict()
    key_dict = get_key_dict()

    strings = localizable.parse_strings(filename=input)
    for entry in strings:
        input_dict[adapt_string_ios(entry["key"])] = entry["value"]

    tree = ET.parse(base)
    root = tree.getroot()
    for child in root:
        if type(child) == ET._Comment:
            continue

        android_string_name = child.attrib["name"]
        ios_string_key = key_dict[android_string_name]
        if input_dict.has_key(ios_string_key):
            child.text = adapt_string_android(input_dict[ios_string_key])
        elif empty_if_missing:
            child.text = ""

    tree.write(output, xml_declaration=True, encoding='utf-8', method='html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import localized strings from iOS to Android.")
    parser.add_argument('--ios', required=True, dest='input', help='input file, iOS formatted')
    parser.add_argument('--format', required=True, dest='base', help='file to copy formatting from')
    parser.add_argument('--android', required=True, dest='output', help='output file, Android formatted')

    args = parser.parse_args()

    if os.path.isfile(args.input):
        import_strings(args.input, args.base, args.output, True)
    else:
        for root, dirs, files in os.walk(args.input):
            first = True
            for file in files:
                filename = os.path.join(root, file)
                if first:
                    import_strings(filename, args.base, args.output, True)
                    first = False
                else:
                    import_strings(filename, args.output, args.output, False)
