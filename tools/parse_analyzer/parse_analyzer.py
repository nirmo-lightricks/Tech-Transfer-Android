# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner.

import argparse
import json
import datetime


def analyze(input_file):
    file = open(input_file)

    data = json.load(file)
    file.close()

    i = 1
    for entry in data["results"]:
        if "advertisingId" not in entry:
            created = datetime.datetime.strptime(entry["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
            updated = datetime.datetime.strptime(entry["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if created != updated:
                print i, entry["objectId"], entry["appVersion"]
                i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze parse JSON export and find issues.")
    parser.add_argument('--input', required=True, dest='input', help='input file')
    args = parser.parse_args()

    analyze(args.input)
