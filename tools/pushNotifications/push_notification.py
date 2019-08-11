# Copyright (c) 2019 Lightricks. All rights reserved.

"""
Module which makes push notifications.
The project is governed by GOGGLE_APPLICATION_CREDENTIALS environment variable.
This makes the module independent of the project and reusable.
"""
from collections import defaultdict
from typing import Dict, List
import argparse
import csv
import logging

import firebase_admin
from firebase_admin import messaging
from more_itertools import chunked

from model import PushMessage, PushMessageConfiguration

logging.basicConfig(level=logging.INFO)

# Limit of tokens for fcm calls.
TOKENS_PER_FCM_CALL = 100
DEFAULT_TRANSLATION = 'en'
DATA_KEY = 'data'



def _parse_language_file(language_file: str) -> Dict[str, Dict[str, str]]:
    translations: Dict[str, Dict[str, str]] = defaultdict(dict)
    with open(language_file, newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            key = row.pop('key')
            translations[key] = row
    return translations



def _get_translation_with_fallback_to_en(translations: Dict[str, Dict[str, str]], title_key: str,
                                         content_key: str, lang: str) -> List[str]:
    return [
        translations[title_key].get(
            lang) or translations[title_key][DEFAULT_TRANSLATION],
        translations[content_key].get(
            lang) or translations[content_key][DEFAULT_TRANSLATION]
    ]



def _create_push_message(push_message_configuration: PushMessageConfiguration) -> PushMessage:
    language_db = _parse_language_file(push_message_configuration.language_file)
    all_languages = filter(None, language_db[push_message_configuration.title_key].keys())
    translation_dict = {
        language: _get_translation_with_fallback_to_en(
            language_db, push_message_configuration.title_key,
            push_message_configuration.content_key, language)
        for language in all_languages
    }
    return PushMessage(
        translations=translation_dict,
        time=push_message_configuration.time,
        channel=push_message_configuration.channel,
        image_url=push_message_configuration.image_url,
        video_url=push_message_configuration.video_url,
        name=push_message_configuration.name,
        active_feature_id=push_message_configuration.active_feature_id,
        visible_feature_item_id=push_message_configuration.visible_feature_item_id,
        supported_build_version_code=push_message_configuration.supported_build_version_code
    )



def _send_multicast(token_chunk: List[str], data_dict: Dict[str, str]) -> None:
    message = messaging.MulticastMessage(tokens=token_chunk, data=data_dict)
    logging.info(f'Sending message for tokens:{token_chunk}')
    response = messaging.send_multicast(message)
    logging.info(
        f'success count: {response.success_count}, failure count: {response.failure_count}')
    for i, api_response in enumerate(response.responses):
        if api_response.success:
            logging.info(
                f'token: {token_chunk[i]}, message id: {api_response.message_id}, succcess')
        else:
            logging.info(
                f'token: {token_chunk[i]}, message id: {api_response.message_id} failed,  '
                + f'Exception: {api_response.exception}')


def send_push_messages(push_message_configuration: PushMessageConfiguration) -> None:
    """
    main function of the module. Sens push messages according to PushMessageConfiguration
    """
    firebase_admin.initialize_app()
    push_message = _create_push_message(push_message_configuration)
    data_dict = {DATA_KEY: push_message.to_json()}
    with open(push_message_configuration.token_file) as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # skip on the CSV header.

        for token_chunk in chunked((row[0] for row in csv_reader), TOKENS_PER_FCM_CALL):
            if push_message_configuration.dry_run:
                print(data_dict)
                print(token_chunk)
            else:
                try:
                    _send_multicast(token_chunk, data_dict)
                except (messaging.ApiCallError, ValueError) as exception:
                    logging.exception(f'Catched exception:{exception}')


def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('language_file')
    parser.add_argument('token_file')
    parser.add_argument('title_key')
    parser.add_argument('content_key')
    parser.add_argument('channel', help='One of the channels: news, promotions')
    parser.add_argument('name')
    parser.add_argument('image_url')
    parser.add_argument(
        '--time', help="when to run push notification locally. In format hh:mm", default='')
    parser.add_argument('--video_url', default='')
    parser.add_argument('--dry_run', action='store_true', default=False)
    parser.add_argument('--active_feature_id', default='')
    parser.add_argument('--visible_feature_item_id', default='')
    parser.add_argument('--supported_build_version_code', default=186)
    return parser


def _run_program() -> None:
    parser = _create_argument_parser()
    args = parser.parse_args()
    print(args)
    push_message_configuration = PushMessageConfiguration(language_file=args.language_file, token_file=args.token_file,
                                                          channel=args.channel, title_key=args.title_key,
                                                          content_key=args.content_key, image_url=args.image_url,
                                                          time=args.time, video_url=args.video_url,
                                                          dry_run=args.dry_run,
                                                          active_feature_id=args.active_feature_id,
                                                          visible_feature_item_id=args.visible_feature_item_id,
                                                          name=args.name,
                                                          supported_build_version_code=args.supported_build_version_code
                                                          )
    send_push_messages(push_message_configuration)


if __name__ == '__main__':
    _run_program()
