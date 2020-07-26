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
    'dry_run': False,

    # List of countries or ``None``. Every country is represented according to ISO-3611 (2-characters)
    # for example: ["us", "il"].
    'countries_whitelist': [],

    # If push is sent in order to trigger a push, needs to be set with the promotion name.
    'promotion_name': None,

    # Set to ``True`` if the message is addressed to subscribers as well. Relevant after Pixaloop 1.2.5.
    'should_show_to_subscribers': None,

    # Holds list of offers. for example:
    # [{
    #     "priority": 0,
    #     "configuration": {
    #         "otp": {
    #             "billing_period": "LIFETIME",
    #             "type": "inapp",
    #             "id": "v1_com.lightricks.pixaloop_gp_vip_otp_l_p3_t0_ip0x.0"
    #         },
    #         "monthly": {
    #             "billing_period": "MONTHLY",
    #             "type": "subs",
    #             "id": "v1_com.lightricks.pixaloop_gp_vip_sub_1m_p2_t0_ip0x.0"
    #         },
    #         "yearly": {
    #             "billing_period": "YEARLY",
    #             "type": "subs",
    #             "id": "v1_com.lightricks.pixaloop_gp_vip_sub_1y_p1_t0_ip0x.0"
    #         }
    #     },
    #     "name": "test_offer_2",
    #     "end_date": "2030-02-01"
    # }]
    'offers': None,

    # Use to pick the sku to show for the subscription offer dialog.
    # If null, and the push is a push offer, then Yearly is used by default.
    'push_offer_billing_period': "YEARLY"
}


def send_message(message: dict, topic: str = None, condition: str = None, token: str = None):
    """
    Send FCM message using one of the options. Specifying more than one option is not defined.
    """
    if topic is None and condition is None and token is None:
        raise Exception("Must specify `topic` or `condition` or `token`.")

    data_message = {'data': json.dumps(message)}
    messaging.send(messaging.Message(
        data=data_message,
        topic=topic,
        condition=condition,
        token=token,
        fcm_options=messaging.FCMOptions(analytics_label=message["name"])
    ))


def demo():
    tokens = ["f_XfJWNil2A:APA91bFs8AlXDyvQJ9GHphtLVfV9C0UsGKwgpZda3AvXalIyHB2jNq3SS415sT_Nc251dcZODd05dPIkIuHIgXCQ2HPXiDyRi8s9oGApFGek21ZPJXsH_wKglqU9A_fvK-CgPMJ13VPl"]
    subscribe_to_topic(tokens, "test_topic_1")
    send_message(message=SAMPLE_MESSAGE, topic="test_topic_1")


if __name__ == "__main__":
    demo()
