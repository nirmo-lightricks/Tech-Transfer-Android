#!/usr/bin/env python3

# Copyright (c) 2018 Lightricks. All rights reserved.
# Created by Noam Freeman.

from html.parser import HTMLParser
import urllib.request as request
import argparse


class ExifTagExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_span = False
        self.tags = []

    def handle_starttag(self, tag, attr):
        if tag == "a":
            self.in_span = True

    def handle_data(self, data):
        if self.in_span and type(data) == str and data.startswith("TAG_"):
            self.tags.append(data)

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_span = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all the Exif tags available in android.media.ExifInterface.",
                                     epilog="If you get an [SSL: CERTIFICATE_VERIFY_FAILED] URLError, you may need to" \
                                            " run /Applications/Python/Install Certificates.command")
    args = parser.parse_args()

    response = request.urlopen('http://developer.android.com/reference/android/media/ExifInterface')

    the_page = response.read().decode("utf8")
    exif_tag_extractor = ExifTagExtractor()
    exif_tag_extractor.feed(the_page)
    tags = map(lambda x:"ExifInterface."+ x + ",", exif_tag_extractor.tags)
    print("\n".join(tags))
