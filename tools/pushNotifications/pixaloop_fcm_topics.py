# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Nir Moshe.
__doc__ = """
Simple script to subscribe FCM tokens into Firebase topic. Provide function to send Pixaloop push messages via topics.

Example: 
    >>> tokens = ["fSv1JHI5rRY:APA91bHheNaUfZtEK9WupdleawwRhf8L4Z9NOrfAmIizciI6r_3Cv94y7CtIiHTUWnVfilMTVe7oUXUUm"
                  "ZaaGcqegLJ6cHslh3rBdSs5WdMRQD-YRpOmc-m-IUXoiGpPPZyTJ0pYqt86"]
    >>> subscribe_to_topic(tokens, "test_topic_1")
    >>> send_message_to_topic(topic="test_topic_1")
"""
import concurrent.futures
import json
import logging
import os

from firebase_admin import initialize_app, messaging
from more_itertools import chunked

# Max chunk size according to ``messaging.subscribe_to_topic``.
TOKENS_PER_FCM_CALL = 1000

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler(filename="topics_script.log"))
logger.setLevel(logging.INFO)

initialize_app()


def send_message_to_topic(topic: str):
    z = {'data': json.dumps({
            'translations': {
                'en': ["Don't you want to dazzle?", u'Get on it \U0001f604']
            },
            'time': '',
            'channel': 'news',
            'name': 'gems_15_08_2019',
            'image_url': 'https://assets.pixaloopapp.com/android/production/pn_assets/gems/gems_image.jpg',
            'video_url': 'https://assets.pixaloopapp.com/android/production/pn_assets/gems/gems_video.mp4',
            'active_feature_id': 'element',
            'visible_feature_item_id': 'GM01_BG.mp4',
            'supported_build_version_code': 0
        })
    }
    messaging.send(
        messaging.Message(data=z, topic=topic)
    )


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


def _subscribe(token_chunk, index, topic):
    topic_management_response = messaging.subscribe_to_topic(tokens=token_chunk, topic=topic)
    logger.info(
        f"({index}, {topic_management_response.success_count}, {topic_management_response.failure_count})"
    )


if __name__ == "__main__":
    print(__doc__)
