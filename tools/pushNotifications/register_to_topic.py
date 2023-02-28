# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Nir Moshe.

import concurrent.futures
import csv
import logging
import os
import random

from more_itertools import chunked
from firebase_admin import initialize_app, messaging
from retrying import retry

# Max chunk size according to ``messaging.subscribe_to_topic``.
TOKENS_PER_FCM_CALL = 1000

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler(filename="topics_script.log"))
logger.setLevel(logging.INFO)

initialize_app()


########################################################################################################################
# CSV Utils
########################################################################################################################

def split_csv(csv_input, csv_output, csv_output2, shuffle=True):
    """
    Splits a given CSV file into 2 even CSVs.

    :param csv_input: The source csv file name.
    :param csv_output: The destination csv file name.
    :param csv_output2: The destination csv file name.
    :param shuffle:
        If `True` then the function will shuffle all the input file records before splitting it. if `False` then there
        is no shuffling.
    """
    with open(csv_input) as csv_f, open(csv_output, "w") as csv_o, open(csv_output2, "w") as csv_o2:

        reader = csv.reader(csv_f)
        all_tokens = [row for row in reader]

        if shuffle:
            random.shuffle(all_tokens)

        writer = csv.writer(csv_o)
        writer2 = csv.writer(csv_o2)
        for i, row in enumerate(all_tokens):
            if i % 2 == 0:
                writer.writerow(row)
            else:
                writer2.writerow(row)


def subscribe_csv_to_topic(csv_file, topic):
    with open(csv_file) as csv_f:
        reader = csv.reader(csv_f)
        next(reader)  # Ignore the CSV title.
        subscribe_to_topic(tokens=(row[0] for row in reader), topic=topic)

########################################################################################################################
# Topics registration
########################################################################################################################


def subscribe_to_topic(tokens, topic):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_chunk = {
            executor.submit(_subscribe, token_chunk, index, topic):
                (index, token_chunk) for index, token_chunk in enumerate(chunked(tokens, TOKENS_PER_FCM_CALL))
        }
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                future.result()
            except Exception as e:
                logger.exception(e)


@retry(stop_max_attempt_number=5)
def _subscribe(token_chunk, index, topic):
    topic_management_response = messaging.subscribe_to_topic(tokens=token_chunk, topic=topic)
    logger.info({"batch_number": index, "success": topic_management_response.success_count,
                 "failure": topic_management_response.failure_count})
