# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Aviel Benya.
import json
import logging
import os
import pathlib
import re
import ast

from datetime import datetime


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

DICTIONARY_REGEX = r'(\{[^{}]+\})'


def gat_tokens_registration_stats(log_file_name):
    folder_path = pathlib.Path(__file__).parent
    file_path = os.path.join(folder_path, log_file_name)
    successes = []
    failures = []
    with open(file_path, 'r') as log_file:
        for line in log_file:
            try:
                current_line = line[:-1]
                matches = re.findall(DICTIONARY_REGEX, current_line)
                for match in matches:
                    stats_dic = ast.literal_eval(match)
                    successes.append(stats_dic["success"])
                    failures.append(stats_dic["failure"])
            except Exception:
                logger.info(f"current line is: [{current_line}] and could not be parsed")

    return {"successes": sum(successes), "failures": sum(failures)}


def write_results_to_file(output_file):
    with open(output_file, 'w') as outfile:
        json.dump(stats, outfile)


if __name__ == "__main__":
    stats = gat_tokens_registration_stats("topics_script.log")
    file_name = "tokens_stats_" + datetime.now().strftime("%d_%m_%Y_%H%M")+".json"
    write_results_to_file(file_name)
