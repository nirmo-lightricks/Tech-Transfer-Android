# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Nir Moshe.
__doc__ = """
Simple script to subscribe FCM tokens into Firebase topic. Provide function to send Pixaloop push messages via topics.

Example - send message to topic: 
    >>> tokens = ["fsSAvy9hg58:APA91bGHOG2YMVz8P97g-8XEIPfIqI9IWS7DBTZSMjpgpyc50_wS8AmZZALMZDJHQ7c6pCxf93RY350LvdvzO8E"
                  "NW-mNRSGXd3yCg1EZi2TIZbaAHPs-IOWJc7RwzRfcWo8sGoWKRzrX"]
    >>> subscribe_to_topic(tokens, "test_topic_1")
    >>> send_message(message=SAMPLE_MESSAGE, topic="test_topic_1")
    
    
Example - Send message with condition (topics arithmetic), Send message to all the users in test_topic_1 and not in 
         test_topic_2:
         
    >>> tokens = ["fsSAvy9hg58:APA91bGHOG2YMVz8P97g-8XEIPfIqI9IWS7DBTZSMjpgpyc50_wS8AmZZALMZDJHQ7c6pCxf93RY350LvdvzO8E"
                  "NW-mNRSGXd3yCg1EZi2TIZbaAHPs-IOWJc7RwzRfcWo8sGoWKRzrX"]
    >>> subscribe_to_topic(tokens, "test_topic_1")
    >>> send_message(message=SAMPLE_MESSAGE, condition="'test_topic_1' in topics && !('test_topic_2' in topics)")
"""
import json
import logging
import os

from firebase_admin import initialize_app, messaging

from register_to_topic import subscribe_to_topic

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler(filename="topics_script.log"))
logger.setLevel(logging.INFO)

try:
    initialize_app()
except ValueError:
    pass

SAMPLE_MESSAGE = {
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
    'name': 'tesr',
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
}


def send_message(message: dict, topic: str = None, condition: str = None):
    data_message = {'data': json.dumps(message)}
    if topic:
        messaging.send(messaging.Message(
            data=data_message,
            topic=topic,
            fcm_options=messaging.FCMOptions(analytics_label=message["name"])
        ))
        return

    if condition:
        messaging.send(messaging.Message(
            data=data_message,
            condition=condition,
            fcm_options=messaging.FCMOptions(analytics_label=message["name"])
        ))
        return

    raise Exception("Must specify `topic` or `condition`.")


def demo():
    tokens = ["fTMErE1iuZs:APA91bEC67vU3GpOWPTxq3-jKxycJaO_UWZpyZpbI8IC6ExWH4uX040iiDnP3TBfKuluWhqlaVaVo5fmsdo4viV1ado"
              "8AUn-PGSIqfRN8ILBbQ4-q1J21SBj0VJrMfcrlpR9IEH7Kw8K"]
    subscribe_to_topic(tokens, "test_topic_1")
    send_message(message=SAMPLE_MESSAGE, topic="test_topic_1")


if __name__ == "__main__":
    demo()
