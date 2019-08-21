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

z = {'data': json.dumps({
    # pos 0 = push title, pos 1 = push subtitle. Whats new dialog title and subtitle are identical to push titles.
    # Set position 2 and 3 in order to set separated text for whats new dialog. Do not set position 2 and 3 if the
    # text of the whats new dialog is identical to the push text since it will increase the payload size for no
    # reason.
    'translations': {
        'en': ["Don't you want to dazzle?", 'Get on it, New Gems pack out now!']
    },
    # Time fo push to be displayed. Format hh::mm. Empty means immediately.
    'time': '',
    # Mandatory filed. Defines the channel for the push.
    'channel': 'news',
    #  Mandatory filed. Used for analytics as a push identifier.
    'name': 'gems_15_08_2019',
    # Image for whats new dialog, mandatory if display_whats_new_dialog is set to True. If video_url is set than the
    # image should be set to be as the first frame of the video.
    'image_url': 'https://assets.pixaloopapp.com/android/production/pn_assets/gems/gems_image.jpg',
    # Optional field. Video for whats new dialog.
    'video_url': 'https://assets.pixaloopapp.com/android/production/pn_assets/gems/gems_video.mp4',
    # Optional field. Image for rich push.
    'push_image_url': 'https://assets.pixaloopapp.com/android/production/pn_assets/gems/gems_image.jpg',
    # Optional field. For deep linking, Defines the visible feature in the toolbar.
    'active_feature_id': 'element',
    # For deep linking, Defines the scroll portion in the toolbar.
    'visible_feature_item_id': 'GM01_BG.mp4',
    # If set to True than image_url must point to a valid url.
    'display_whats_new_dialog': True,
    # Use to filter out devices with old versions that we don't want them to see the push. For example if we publish
    # a push describing a new feature we don't want to show it to devices thatn don't have that feature yet.
    'supported_build_version_code': 0,
    # Set to true of push text contains an emoji. Used for analytics.
    'with_emoji': True,
    # Push will travel all the way up to the stage where it is ready to display but won't be display. Use for sending
    # push to control group for analytics purposes.
    'dry_run': False
    })
}


def send_message_to_topic(topic: str):
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


def demo():
    tokens = [
        "fsSAvy9hg58:APA91bGHOG2YMVz8P97g-8XEIPfIqI9IWS7DBTZSMjpgpyc50_wS8AmZZALMZDJHQ7c6pCxf93RY350LvdvzO8ENW-mNRSGXd3yCg1EZi2TIZbaAHPs-IOWJc7RwzRfcWo8sGoWKRzrX"]
    subscribe_to_topic(tokens, "test_topic_2")
    send_message_to_topic(topic="test_topic_2")


if __name__ == "__main__":
    demo()
