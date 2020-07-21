# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Ehud Plaksin.

import os
import xml.etree.ElementTree as ET
import re
import glob

__doc__ = """
    Script for updating localization in an Android project.
    Copies specified localization strings from directory with new localizations,
    Into the project's localizations.

    @PROJECT_LOCALIZATIONS_DIR resources directory of your project IE parent for where the localization files are kept.
    This should be a facetune android project (!) resources directory.
    @NEW_LOCALIZATIONS_DIR  Directory where the new localizations are stored.
    @NEW_LOCALIZATIONS_KEYS Localization Keys to fetch from the new files into the project files.
    Example usage, comment out with your directories and keys.
"""

STRINGS_XML_FILE_NAME = 'strings.xml'
# NEW_LOCALIZATIONS_KEYS = ['example_subscription_title_1', 'example_subscription_title_2', 'example_subscription_title_3']
# PROJECT_LOCALIZATIONS_DIR = '.../facetune-android/quickshot/src/main/res/'
# NEW_LOCALIZATIONS_DIR = '.../new_localizaitions'


class CommentedTreeBuilder(ET.TreeBuilder):
    """
        Helper class for keeping comments while parsing the XML.
    """

    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)


def get_locale_to_file_dict(directory):
    """
       Generates a dictionary of [locale, file],
       For locale files in @directory.
       Assumes locale files are named @STRINGS_XML_FILE_NAME,
       Assumes each locale file has a <String> element with name attribute 'user_locale'
    """
    locale_to_file_dict = {}
    files = find_localization_files(directory)
    for file in files:
        root = ET.parse(file)
        locale = root.find("string/[@name='user_locale']").text

        if locale is not None:
            locale_to_file_dict[locale] = file

    return locale_to_file_dict


def find_localization_files(directory):
    """
     Returns list of localization files in @directory,
     Assumes localization file name is 'string.xml'
    """
    return glob.glob(os.path.join(directory, '*', STRINGS_XML_FILE_NAME))


def add_localization_to_file(source_file, new_localizations):
    """
        Adds the new localization elements @new_localizations into the source_file tree,
        As Children of its root element.

        @source_file - path to XML file to add new localizations into.
        @new_localizations - list of ElementTree.Element the localization elements to add
    """
    # preserve comments in the source_file
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(source_file, parser=parser)
    root = tree.getroot()

    for localization in new_localizations:
        root.append(localization)

    tree.write(source_file)


def get_new_localizations_from_file(file):
    """
        Reads @file and returns list of elements which match the keys in @NEW_LOCALIZATIONS_KEYS
        @file - path to file where new localizations are stored
        return - list of ElementTree.Element
    """
    root = ET.parse(file)
    new_localizations = []
    for key in NEW_LOCALIZATIONS_KEYS:
        localization = root.find(f"string/[@name='{key}']")
        if localization is not None:
            new_localizations.append(localization)

    return new_localizations


if __name__ == '__main__':
    # verify that the PROJECT_LOCALIZATIONS_DIR is the Android's project resource directory
    if not re.match(r".*\/facetune-android\/.*\/src\/main\/res", PROJECT_LOCALIZATIONS_DIR):
        raise Exception("PROJECT_LOCALIZATIONS_DIR should be an android project res dir")

    project_locale_to_file_dict = get_locale_to_file_dict(PROJECT_LOCALIZATIONS_DIR)
    updates_local_to_file_dict = get_locale_to_file_dict(NEW_LOCALIZATIONS_DIR)

    for lang in project_locale_to_file_dict:
        if lang in updates_local_to_file_dict:
            new_elements = get_new_localizations_from_file(updates_local_to_file_dict[lang])
            add_localization_to_file(project_locale_to_file_dict.get(lang), new_elements)
        else:
            print(f"language : {lang} was not found in updated localizations")
