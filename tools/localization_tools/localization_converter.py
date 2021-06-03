# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Lea Cohen Tannoudji.

"""
This Converts iOS .strings files to Android .xml files.

Example:
    python localization_converter.py my_iphone_localizations.strings
In order to drop empty lines:
    python localization_converter.py my_iphone_localizations.strings drop

With any question, you can come to Lea@lightricks.com
"""

import sys
IOS_FILE_SUFFIX = ".strings"
WRONG_SUFFIX_MESSAGE = " is not a .strings file. Are you sure it's the right one? \nStopping...."
USAGE_MESSAGE = "Wrong number of arguments. \nUsage: script_name input_filepath "
SUCCESS_MESSAGE = "Success! The file was created, and is in "

android_special_chars_dict = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "\&quot;", "\'": "\&apos;"}


def parse_file(input_file_path, include_empty_lines):
    with open(input_file_path, "r") as input_file:
        original_filename = input_file.name
        if IOS_FILE_SUFFIX not in original_filename:
            print(original_filename + WRONG_SUFFIX_MESSAGE)
            return

        android_filename = original_filename.replace(IOS_FILE_SUFFIX, "") + ".xml"
        with open(android_filename, "w") as android_file:
            android_file.write("<resources>\n")
            for line in input_file:
                # Does this a line contain something?
                if is_empty_line(line):
                    if include_empty_lines:
                        android_file.write(line)
                    continue

                if is_comment(line):
                    line = replace_comment(line)
                    android_file.write(line)
                    continue
                while ";" not in line:
                    next_line = next(input_file)
                    line = line + next_line

                key, value = parse_line(line)
                key = convert_key(key)
                value = replace_special_chars(value)
                android_line = plugin_html(key, value)

                android_file.write(android_line)

            android_file.write("</resources>\n")

        print SUCCESS_MESSAGE + android_filename


def replace_special_chars(value):
    new_value = value
    for special_char, special_char_translation in android_special_chars_dict.iteritems():
        new_value = value.replace(special_char, special_char_translation)

    return new_value


def is_empty_line(line):
    return line.isspace()


"""
iOS.Key. -> ios_key_
"""
def convert_key(key):
    key = key.strip()
    key = key.lower()
    key = key.replace(".", "_")
    return key.replace(" ", "")


def plugin_html(key, value):
    return "<string name=\"" + key + "\">" + value + "</string>\n"


def is_comment(line):
    return "/*" in line or "*/" in line or "// " in line


def parse_line(line):
    line = line.replace("\"", "")
    line = line.replace(";", "")
    key, value = line.split("=")

    return key.strip(), value.strip()


def replace_comment(line):
        line = line.replace("/*", "<!--")
        return line.replace("*/", "-->")


# Usage: script_name input_filename
if __name__ == '__main__':
    args = sys.argv
    print("example usage:")
    print("python localization_converter.py my_iphone_localizations.strings [optional:drop]")
    if len(args) < 2:
        print(USAGE_MESSAGE)
    input_file_path = args[1]
    include_empty_lines = False if len(args) > 2 else True
    parse_file(input_file_path, include_empty_lines)
